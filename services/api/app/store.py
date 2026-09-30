"""In-memory repository seeded from the state adapters + synthetic sample data.

Demo mode: runtime changes (new requests/clusters, decisions, weight log, briefs) are persisted to a
local JSON file (`settings.local_state_path`). Real mode additionally streams rows to BigQuery
through `integrations.bigquery_sink` (the in-memory store stays the serving layer for the MVP).
"""
from __future__ import annotations

import json
import logging
import threading
from datetime import UTC, datetime
from pathlib import Path

from app.config import settings
from app.integrations import bigquery_sink
from app.interop.adapters import StateData, load_all_states
from app.models import (
    AdminUnit,
    CitizenRequest,
    DemandCluster,
    Indicator,
    Investment,
    Weights,
)

log = logging.getLogger(__name__)


class Store:
    def __init__(self, data_dir: Path, state_path: str = "") -> None:
        self.data_dir = data_dir
        self.state_path = Path(state_path) if state_path else None
        self.lock = threading.RLock()
        self.reset()

    # ------------------------------------------------------------------ loading
    def reset(self, load_runtime: bool = True) -> None:
        self.states: dict[str, StateData] = load_all_states(self.data_dir)
        self.units: dict[str, AdminUnit] = {}
        self.indicators: dict[str, list[Indicator]] = {}
        self.investments: list[Investment] = []
        for sd in self.states.values():
            for u in sd.units:
                self.units[u.lgd_code] = u
            for ind in sd.indicators:
                self.indicators.setdefault(ind.lgd_code, []).append(ind)
            self.investments.extend(sd.investments)
        sample = self.data_dir / "sample"
        self.manifest = json.loads((sample / "manifest.json").read_text(encoding="utf-8"))
        self.requests: dict[str, CitizenRequest] = {}
        self.clusters: dict[str, DemandCluster] = {}
        self.members: dict[str, list[str]] = {}
        self.weight_log: list[dict] = []
        self.decisions: dict[str, dict] = {}
        self.briefs: dict[str, dict] = {}
        self.weights = Weights()
        self.telegram_chats: dict[str, dict] = {}
        # per-request pipeline details (extraction, provenance, translation, location, clustering)
        self.extras: dict[str, dict] = {}
        for c in json.loads((sample / "clusters_synthetic.json").read_text(encoding="utf-8"))["clusters"]:
            self.clusters[c["cluster_id"]] = DemandCluster(**c)
            self.members[c["cluster_id"]] = []
        with (sample / "requests_synthetic.jsonl").open(encoding="utf-8") as f:
            for line in f:
                r = CitizenRequest(**json.loads(line))
                r.h3_cell = self.units[r.lgd_unit].h3_cell if r.lgd_unit in self.units else None
                self.requests[r.request_id] = r
                self.members[r.cluster_id].append(r.request_id)
        if load_runtime and self.state_path and self.state_path.exists():
            self._load_runtime()
        for cid in self.clusters:
            self.refresh_cluster(cid)

    def _load_runtime(self) -> None:
        try:
            doc = json.loads(self.state_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            log.warning("ignoring unreadable runtime state: %s", exc)
            return
        for c in doc.get("clusters", []):
            self.clusters[c["cluster_id"]] = DemandCluster(**c)
            self.members.setdefault(c["cluster_id"], [])
        for r in doc.get("requests", []):
            req = CitizenRequest(**r)
            self.requests[req.request_id] = req
            if req.cluster_id:
                self.members.setdefault(req.cluster_id, []).append(req.request_id)
        for cid, status in doc.get("cluster_status", {}).items():
            if cid in self.clusters:
                self.clusters[cid].status = status
        self.weight_log = doc.get("weight_log", [])
        self.decisions = doc.get("decisions", {})
        self.briefs = doc.get("briefs", {})
        self.extras = doc.get("extras", {})
        if doc.get("weights"):
            self.weights = Weights(**doc["weights"])

    def save(self) -> None:
        if not self.state_path:
            return
        with self.lock:
            doc = {
                "requests": [r.model_dump(mode="json") for r in self.requests.values() if not r.is_synthetic],
                "clusters": [c.model_dump(mode="json") for c in self.clusters.values() if not c.is_synthetic],
                "cluster_status": {c.cluster_id: c.status for c in self.clusters.values()},
                "weight_log": self.weight_log,
                "decisions": self.decisions,
                "briefs": self.briefs,
                "extras": self.extras,
                "weights": self.weights.model_dump(),
            }
            self.state_path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.state_path.with_suffix(".tmp")
            tmp.write_text(json.dumps(doc, ensure_ascii=False, default=str), encoding="utf-8")
            tmp.replace(self.state_path)

    # ------------------------------------------------------------------ mutations
    def add_request(self, req: CitizenRequest) -> None:
        with self.lock:
            self.requests[req.request_id] = req
        bigquery_sink.insert("requests", [req.model_dump(mode="json")])
        self.save()

    def assign(self, req: CitizenRequest, cluster_id: str) -> None:
        with self.lock:
            req.cluster_id = cluster_id
            req.status = "Clustered"
            self.members.setdefault(cluster_id, []).append(req.request_id)
            self.refresh_cluster(cluster_id)
        bigquery_sink.insert("request_cluster_assignments", [{
            "request_id": req.request_id, "cluster_id": cluster_id, "assigned_at": datetime.now(UTC).isoformat()}])
        self.save()

    def new_cluster_id(self, state: str) -> str:
        n = sum(1 for c in self.clusters if c.startswith(f"CL-{state}-")) + 1
        return f"CL-{state}-{n:04d}"

    def refresh_cluster(self, cluster_id: str) -> None:
        c = self.clusters[cluster_id]
        reqs = [self.requests[i] for i in self.members.get(cluster_id, [])]
        c.request_count = len(reqs)
        c.unique_citizens = len({r.citizen_id for r in reqs})
        if reqs:
            c.first_seen = min(r.created_at for r in reqs)
            c.last_seen = max(r.created_at for r in reqs)
        units = list(dict.fromkeys([*c.lgd_units, *[r.lgd_unit for r in reqs if r.lgd_unit]]))
        c.lgd_units = units
        c.h3_cells = sorted({self.units[u].h3_cell for u in units if u in self.units})

    # ------------------------------------------------------------------ queries
    def cluster_requests(self, cluster_id: str) -> list[CitizenRequest]:
        return [self.requests[i] for i in self.members.get(cluster_id, [])]

    def unit_indicators(self, code: str) -> list[Indicator]:
        return self.indicators.get(code, [])

    def filter_clusters(self, state: str | None = None, district: str | None = None,
                        category: str | None = None) -> list[DemandCluster]:
        out = []
        for c in self.clusters.values():
            if c.request_count == 0:
                continue
            if state and c.state != state:
                continue
            if district and c.lgd_district != district:
                continue
            if category and c.category != category:
                continue
            out.append(c)
        return out


_store: Store | None = None


def get_store() -> Store:
    global _store
    if _store is None:
        _store = Store(Path(settings.data_dir), settings.local_state_path)
    return _store


def set_store(store: Store) -> None:
    global _store
    _store = store
