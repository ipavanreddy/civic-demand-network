import json

from app.pipeline import understanding


def test_system_status_reports_demo_mode(client):
    st = client.get("/api/system/status").json()
    assert st["demo_mode"] is True and st["sample_data"] is True
    assert st["integrations"]["gemini"]["mode"] == "demo"
    assert st["synthetic_requests"] > 1000
    assert client.get("/health").json()["demo_mode"] is True


def test_states_and_interop(client):
    states = client.get("/api/states").json()
    assert {s["state_code"] for s in states} == {"BR", "AP", "MH"}
    ap = client.get("/api/states/AP").json()
    assert ap["default_language"] == "te" and ap["adapter"]["units"]["format"] == "json"
    io = client.get("/api/states/AP/interop").json()
    assert io["raw_unit_record"]["habitation"]["code"] == io["canonical_unit"]["lgd_code"]
    assert client.get("/api/states/ZZ").status_code == 404
    ind = client.get("/api/districts/BR.GAY/indicators").json()
    assert any(r["indicator_name"] == "aspirational_district" for r in ind["indicators"])


def test_analytics_and_hotspots(client):
    a = client.get("/api/analytics").json()
    assert a["requests"] > 1000 and a["clusters"] == 19 and a["top_categories"]
    assert a["freshness"]["citizen_requests_last_received"]
    br = client.get("/api/states/BR/analytics").json()
    assert br["scope"]["label"] == "Bihar" and br["requests"] < a["requests"]
    hs = client.get("/api/hotspots", params={"state": "AP", "category": "drinking_water"}).json()
    assert hs["cells"] and all(c["top_category"] == "drinking_water" for c in hs["cells"])
    assert len(hs["cells"][0]["boundary"]) == 6


def test_clusters_and_recommendations(client):
    clusters = client.get("/api/clusters", params={"state": "BR"}).json()
    assert clusters[0]["state"] == "BR" and clusters[0]["rank"] == 1
    detail = client.get("/api/clusters/CL-AP-0001").json()
    assert detail["request_count"] >= 118 and detail["places"]
    recs = client.get("/api/recommendations").json()
    assert recs["items"][0]["priority_score"] >= recs["items"][-1]["priority_score"]
    rec = client.get("/api/recommendations/REC-CL-MH-0001", params={"state": "MH"}).json()
    assert rec["scope"]["label"] == "Maharashtra" and rec["indicators"] and rec["investments"]
    assert client.get("/api/recommendations/REC-NOPE").status_code == 404


def test_weight_change_reranks_and_is_logged(client):
    before = client.get("/api/recommendations").json()["items"]
    body = {"weights": {"demand": 5, "infra_gap": 10, "vulnerability": 70, "trend": 5, "investment": 10},
            "officer": "test-officer", "reason": "equity lens"}
    after = client.post("/api/recommendations/score", json=body).json()["items"]
    assert [i["cluster_id"] for i in before] != [i["cluster_id"] for i in after]
    assert any(i["rank"] != i["default_rank"] for i in after)
    log = client.get("/api/recommendations/weights-log").json()
    assert log[0]["officer"] == "test-officer" and log[0]["to"]["vulnerability"] == 70


def test_brief_and_human_decision(client):
    b = client.post("/api/recommendations/REC-CL-BR-0002/brief", json={"state": "BR"}).json()
    assert b["grounding"]["ok"] and b["model_name"] == "demo-template" and b["prompt_version"] == "evidence_brief_v1"
    assert b["evidence_brief"]["investment_context"][0].startswith("BR-PMGSY-2025-117")
    d = client.post("/api/recommendations/REC-CL-BR-0002/decision",
                    json={"decision": "approve_for_field_verification", "officer": "o1", "note": "check"}).json()
    assert d["cluster_status"] == "Recommended"
    rec = client.get("/api/recommendations/REC-CL-BR-0002").json()
    assert rec["decision"]["officer"] == "o1" and rec["brief"]["grounding"]["ok"]
    bad = client.post("/api/recommendations/REC-CL-BR-0002/decision", json={"decision": "auto_fund"})
    assert bad.status_code == 422


def test_language_endpoints_demo(client):
    fx = next(f for f in understanding.fixtures() if f["language"] == "hi")
    assert client.post("/api/translate", json={"text": fx["text_original"], "language": "hi"}).json()["text_en"] == fx["text_en"]
    tts = client.post("/api/text-to-speech", json={"text": "नमस्ते", "language": "hi"}).json()
    assert tts["mode"] == "demo" and tts["audio_base64"] is None
    stt = client.post("/api/speech-to-text", files={"audio": ("v.webm", b"\x1a\x45", "audio/webm")},
                      data={"language": "te", "state": "AP"}).json()
    assert stt["mode"] == "demo" and stt["language"] == "te"


def test_request_validation_and_404(client):
    assert client.post("/api/requests", json={"text": "", "language": "hi"}).status_code == 422
    assert client.post("/api/requests", json={"text": "hello there", "language": "fr"}).status_code == 422
    assert client.get("/api/requests/REQ-NOPE").status_code == 404
    r = client.post("/api/requests", json={"text": "Sonbarsa needs a bridge", "language": "en", "state": "BR"}).json()
    bad = client.post(f"/api/requests/{r['request']['request_id']}/confirm", json={"category": "space_program"})
    assert bad.status_code == 400


def test_telegram_webhook_demo_mode(client, store):
    fx = next(f for f in understanding.fixtures() if f["language"] == "te" and f["state"] == "AP")
    upd = {"update_id": 1, "message": {"message_id": 1, "chat": {"id": 42}, "text": fx["text_original"]}}
    res = client.post("/api/webhooks/messaging", json=upd).json()
    assert res["mode"] == "demo" and res["delivered"] is False
    assert res["result"]["cluster"]["cluster_id"] == "CL-AP-0001"  # auto-confirmed into the Kalyandurg cluster
    assert res["result"]["request"]["channel"] == "telegram"
    status = client.post("/api/webhooks/messaging", json={"message": {"chat": {"id": 42}, "text": "/status"}}).json()
    assert res["result"]["request"]["request_id"] in json.dumps(status["result"])
    # clarification loop over the bot
    amb = next(f for f in understanding.fixtures() if f["id"] == "scenario_d_bihar_ambiguous_hi")
    r1 = client.post("/api/webhooks/messaging", json={"message": {"chat": {"id": 7}, "text": amb["text_original"]}}).json()
    assert r1["result"]["needs_clarification"]
    r2 = client.post("/api/webhooks/messaging", json={"message": {"chat": {"id": 7}, "text": "Rampur, Imamganj"}}).json()
    assert r2["result"]["cluster"]["cluster_id"] == "CL-BR-0003"


def test_demo_scenarios_endpoint(client):
    sc = client.get("/api/demo/scenarios").json()
    assert {s["state"] for s in sc} == {"BR", "AP", "MH"}
    assert all(s["text_original"] for s in sc)
