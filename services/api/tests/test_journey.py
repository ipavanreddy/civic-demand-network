"""PRD §44 demo journey end to end through the API, in demo mode (no keys)."""
from app.pipeline import understanding


def test_demo_journey_voice_to_decision(client):
    # 0:30 Hindi voice request (demo transcript because Speech-to-Text is not configured)
    res = client.post("/api/requests/voice", files={"audio": ("note.webm", b"\x1a\x45\xdf\xa3fake", "audio/webm")},
                      data={"language": "hi", "state": "BR", "district": "BR.GAY", "citizen_ref": "parent-gaya"})
    assert res.status_code == 200, res.text
    v = res.json()
    assert v["speech"]["mode"] == "demo" and v["request"]["channel"] == "voice"
    assert v["request"]["audio_url"].startswith("local://")
    # Gemini-style extraction (fixture), provenance stored on the record
    assert v["request"]["category"] == "roads_bridges" and v["request"]["urgency"] == "high"
    assert v["request"]["model_name"] == "demo-fixture" and v["request"]["prompt_version"] == "extract_v1"
    assert v["location"]["lgd_unit"] == "BR.GAY.TEK.SNB" and v["location"]["h3_cell"]
    assert "सोनबरसा" in v["message"]["text"]  # confirmation in Hindi
    assert v["demo_mode"] is True
    rid = v["request"]["request_id"]

    before = client.get("/api/recommendations/REC-CL-BR-0001").json()

    # 1:10 confirm -> joins the existing Sonbarsa bridge cluster
    c = client.post(f"/api/requests/{rid}/confirm").json()
    assert c["cluster"]["cluster_id"] == "CL-BR-0001" and c["cluster"]["joined_existing"]
    assert c["cluster"]["request_count"] == before["request_count"] + 1
    assert c["cluster"]["representative_quotes"]

    # 1:50 fusion + priority score with factor breakdown; weights re-rank
    recs = client.get("/api/recommendations", params={"state": "BR"}).json()
    top = recs["items"][0]
    assert top["cluster_id"] == "CL-BR-0001" and len(top["breakdown"]) == 5
    rescored = client.post("/api/recommendations/score", json={
        "state": "BR", "weights": {"demand": 0, "infra_gap": 10, "vulnerability": 80, "trend": 10, "investment": 10}}).json()
    assert rescored["items"][0]["cluster_id"] != "CL-BR-0001" or rescored["items"][0]["priority_score"] != top["priority_score"]
    client.post("/api/recommendations/score", json={"state": "BR", "weights": {}})  # back to PRD defaults

    # 2:30 evidence brief: grounded numbers, sources, uncertainties, provenance
    b = client.post("/api/recommendations/REC-CL-BR-0001/brief", json={"state": "BR"}).json()
    assert b["grounding"]["ok"], b["grounding"]
    assert b["evidence_brief"]["uncertainties"] and b["evidence_brief"]["data_evidence"]
    assert {"model_name", "model_version", "prompt_version"} <= set(b)

    # 3:10 hotspot map
    hs = client.get("/api/hotspots", params={"state": "BR"}).json()
    assert any("CL-BR-0001" in cell["cluster_ids"] for cell in hs["cells"])

    # human decision closes the loop to the citizen
    client.post("/api/recommendations/REC-CL-BR-0001/decision", json={"decision": "approve_for_field_verification"})
    status = client.get(f"/api/requests/{rid}").json()
    assert status["status"] == "Recommended" and status["status_label"] == "अनुशंसित"

    # 3:40 interoperability: same pipeline for AP / Telugu / drinking water
    fx = next(f for f in understanding.fixtures() if f["state"] == "AP")
    ap = client.post("/api/requests", json={"text": fx["text_original"], "language": "te", "state": "AP"}).json()
    ap = client.post(f"/api/requests/{ap['request']['request_id']}/confirm").json()
    assert ap["cluster"]["cluster_id"] == "CL-AP-0001" and ap["request"]["state"] == "AP"
    assert set(ap["request"]) == set(c["request"])  # identical canonical record shape


def test_new_need_starts_new_cluster_and_ambiguity_is_clarified(client):
    r = client.post("/api/requests", json={"text": "Kothrud needs a public toilet near the bus depot, the drain smells",
                                           "language": "en", "state": "MH"}).json()
    assert r["request"]["category"] == "sanitation" and r["location"]["lgd_unit"] == "PMC-W31"
    c = client.post(f"/api/requests/{r['request']['request_id']}/confirm").json()
    assert c["cluster"]["joined_existing"] is False and c["cluster"]["cluster_id"].startswith("CL-MH-")
    amb = next(f for f in understanding.fixtures() if f["id"] == "scenario_d_bihar_ambiguous_hi")
    a = client.post("/api/requests", json={"text": amb["text_original"], "language": "hi", "state": "BR"}).json()
    assert a["needs_clarification"] and len(a["location"]["candidates"]) == 2
    code = next(x["lgd_code"] for x in a["location"]["candidates"] if "Imamganj" in x["label"])
    done = client.post(f"/api/requests/{a['request']['request_id']}/confirm", json={"lgd_code": code}).json()
    assert done["location"]["method"] == "clarified" and done["cluster"]["cluster_id"] == "CL-BR-0003"
