from app.models import Weights
from app.pipeline import brief, ranking


def _data(store, cid="CL-BR-0001"):
    scored, contexts = ranking.rank(store, Weights())
    s = next(x for x in scored if x.cluster_id == cid)
    return brief.build_input(s, contexts[cid], store, ranking.scope_label(store, None, None, None), len(scored))


def test_template_brief_is_fully_grounded_and_cites_sources(store):
    for cid in ("CL-BR-0001", "CL-AP-0001", "CL-MH-0001", "CL-BR-0002"):
        data = _data(store, cid)
        b, prov = brief.generate(data)
        g = brief.check_grounding(b, data)
        assert g["ok"], (cid, g)
        assert prov.mode == "demo" and prov.prompt_version == "evidence_brief_v1"
        assert all(d.source and d.year for d in b.data_evidence)
        assert b.uncertainties and b.next_step


def test_grounding_flags_invented_numbers(store):
    data = _data(store)
    b, _ = brief.generate(data)
    b.demand_evidence.append("Roughly 98,765 people would benefit.")
    g = brief.check_grounding(b, data)
    assert not g["ok"] and "98,765" in g["ungrounded_numbers"]


def test_brief_keeps_rank_and_score_from_deterministic_model(store):
    data = _data(store)
    b, _ = brief.generate(data)
    assert f"{data['ranking']['priority_score']} / 100" in b.summary
    assert f"rank {data['ranking']['rank']} of" in b.summary
