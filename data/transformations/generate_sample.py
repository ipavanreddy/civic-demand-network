"""Deterministic generator for JanVaani SYNTHETIC sample data.

Run from the repo root:  python3 data/transformations/generate_sample.py

Standard library only, fixed seed, fixed reference date -> byte-identical output on every run.
No AI model is called. Everything written here is SYNTHETIC / SAMPLE data:
- administrative codes are "LGD-style" sample codes (NOT official LGD codes);
- populations and indicators are illustrative values in the style of Census 2011 / state MIS tables;
- citizen requests are template-generated text in Hindi, Telugu and English.

Outputs (raw files deliberately use *different, state-specific* formats so the state adapters in
`data/adapters/*.json` + `services/api/app/interop/adapters.py` have something real to map):
  data/sample/manifest.json
  data/sample/states/BR/bihar_village_indicators.csv   (Hindi-transliterated column names)
  data/sample/states/BR/bihar_yojana_suchi.csv          (scheme list, Hindi status/category labels)
  data/sample/states/AP/ap_habitation_indicators.json   (nested JSON, SC and ST split)
  data/sample/states/AP/ap_jjm_works.csv                (households, cost in crore)
  data/sample/states/MH/pune_ward_stats.csv             (urban wards, slum share)
  data/sample/states/MH/pune_capex_projects.csv         (department-based, INR)
  data/sample/requests_synthetic.jsonl                  (canonical, already-processed history)
  data/sample/clusters_synthetic.json                   (seed demand clusters)
"""
from __future__ import annotations

import csv
import hashlib
import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "sample"
SEED = 20260928
DATASET_VERSION = "sample-v1"
IST = timezone(timedelta(hours=5, minutes=30))
AS_OF = datetime(2026, 9, 28, 12, 0, tzinfo=IST)  # fixed reference date for the synthetic history
GENERATOR = "data/transformations/generate_sample.py"

# --------------------------------------------------------------------------------------------
# Geography (sample LGD-style codes). Coordinates are approximate real locations.
# --------------------------------------------------------------------------------------------
BR_UNITS = [
    # district, dcode, block, bcode, village, village_hi, code, lat, lng, pop, scst, lit, road, naljal, elec, phc_km, school5km
    ("Gaya", "BR.GAY", "Tekari", "BR.GAY.TEK", "Sonbarsa", "सोनबरसा", "BR.GAY.TEK.SNB", 24.952, 84.823, 3120, 34, 52, "nahi", 41, 88, 14, "nahi"),
    ("Gaya", "BR.GAY", "Tekari", "BR.GAY.TEK", "Kurmawan", "कुरमावां", "BR.GAY.TEK.KRM", 24.931, 84.801, 2890, 29, 55, "nahi", 45, 90, 16, "nahi"),
    ("Gaya", "BR.GAY", "Tekari", "BR.GAY.TEK", "Belhari", "बेलहरी", "BR.GAY.TEK.BLH", 24.968, 84.858, 2410, 38, 49, "nahi", 38, 85, 18, "nahi"),
    ("Gaya", "BR.GAY", "Sherghati", "BR.GAY.SHG", "Dumri", "डुमरी", "BR.GAY.SHG.DMR", 24.548, 84.781, 4200, 31, 58, "nahi", 55, 92, 9, "haan"),
    ("Gaya", "BR.GAY", "Sherghati", "BR.GAY.SHG", "Rampur", "रामपुर", "BR.GAY.SHG.RMP", 24.571, 84.812, 3600, 22, 61, "haan", 62, 94, 6, "haan"),
    ("Gaya", "BR.GAY", "Imamganj", "BR.GAY.IMG", "Kothi", "कोठी", "BR.GAY.IMG.KTH", 24.412, 84.571, 3900, 45, 47, "haan", 22, 80, 11, "haan"),
    ("Gaya", "BR.GAY", "Imamganj", "BR.GAY.IMG", "Rampur", "रामपुर", "BR.GAY.IMG.RMP", 24.389, 84.603, 2750, 48, 44, "nahi", 18, 78, 13, "nahi"),
    ("Gaya", "BR.GAY", "Bodhgaya", "BR.GAY.BDG", "Bakraur", "बकरौर", "BR.GAY.BDG.BKR", 24.699, 85.003, 5100, 36, 57, "haan", 60, 95, 12, "haan"),
    ("Gaya", "BR.GAY", "Bodhgaya", "BR.GAY.BDG", "Mastipur", "मस्तीपुर", "BR.GAY.BDG.MST", 24.681, 84.972, 2300, 33, 55, "haan", 58, 93, 10, "haan"),
    ("Gaya", "BR.GAY", "Wazirganj", "BR.GAY.WZG", "Fatehpur", "फतेहपुर", "BR.GAY.WZG.FTP", 24.831, 85.221, 6100, 27, 60, "haan", 50, 91, 7, "nahi"),
    ("Aurangabad", "BR.AUR", "Obra", "BR.AUR.OBR", "Khaira", "खैरा", "BR.AUR.OBR.KHR", 24.851, 84.402, 3300, 30, 59, "nahi", 48, 89, 10, "haan"),
    ("Aurangabad", "BR.AUR", "Deo", "BR.AUR.DEO", "Deo", "देव", "BR.AUR.DEO.DEO", 24.659, 84.434, 9800, 24, 66, "haan", 64, 82, 4, "haan"),
]
BR_ASPIRATIONAL = {"BR.GAY": 1, "BR.AUR": 1}

AP_UNITS = [
    # district, dcode, mandal, mcode, habitation, hab_te, code, lat, lng, pop, sc, st, lit, fhtc, irrig, phc_km
    ("Anantapur", "AP.ATP", "Kalyandurg", "AP.ATP.KDG", "Mudigal", "ముదిగల్", "AP.ATP.KDG.MDG", 14.601, 77.083, 4600, 18, 6, 54, 28, 22, 8),
    ("Anantapur", "AP.ATP", "Kalyandurg", "AP.ATP.KDG", "Varli", "వర్లి", "AP.ATP.KDG.VRL", 14.522, 77.151, 2100, 22, 9, 50, 21, 18, 12),
    ("Anantapur", "AP.ATP", "Dharmavaram", "AP.ATP.DMV", "Chigicherla", "చిగిచెర్ల", "AP.ATP.DMV.CGC", 14.452, 77.701, 3800, 20, 4, 58, 35, 30, 7),
    ("Anantapur", "AP.ATP", "Dharmavaram", "AP.ATP.DMV", "Pothukunta", "పోతుకుంట", "AP.ATP.DMV.PTK", 14.398, 77.752, 1900, 25, 5, 55, 30, 26, 9),
    ("Anantapur", "AP.ATP", "Rayadurg", "AP.ATP.RYD", "Kanekal", "కణేకల్", "AP.ATP.RYD.KNK", 14.871, 76.931, 7200, 17, 3, 57, 62, 24, 5),
    ("Anantapur", "AP.ATP", "Gooty", "AP.ATP.GTY", "Gooty", "గుత్తి", "AP.ATP.GTY.GTY", 15.121, 77.631, 48000, 15, 3, 70, 71, 35, 2),
    ("Kurnool", "AP.KNL", "Pattikonda", "AP.KNL.PTK", "Hosur", "హోసూరు", "AP.KNL.PTK.HSR", 15.421, 77.502, 3500, 21, 2, 49, 25, 20, 10),
    ("Kurnool", "AP.KNL", "Adoni", "AP.KNL.ADN", "Pedda Harivanam", "పెద్ద హరివాణం", "AP.KNL.ADN.PHV", 15.591, 77.201, 8900, 19, 1, 46, 58, 28, 6),
]

MH_UNITS = [
    # ward_no, ward, ward_mr, corp, corp_code, lat, lng, pop, slum, lit, bus500, sewer, piped_pct, water_hrs
    ("PMC-W04", "Kharadi", "खराडी", "Pune Municipal Corporation", "MH.PUN.PMC", 18.551, 73.941, 72000, 12, 89, 38, 70, 88, 4),
    ("PMC-W22", "Hadapsar", "हडपसर", "Pune Municipal Corporation", "MH.PUN.PMC", 18.502, 73.927, 145000, 22, 86, 61, 74, 90, 3),
    ("PMC-W03", "Wagholi", "वाघोली", "Pune Municipal Corporation", "MH.PUN.PMC", 18.580, 73.983, 65000, 18, 84, 22, 45, 62, 2),
    ("PMC-W26", "Kondhwa", "कोंढवा", "Pune Municipal Corporation", "MH.PUN.PMC", 18.470, 73.890, 110000, 26, 83, 55, 52, 81, 3),
    ("PMC-W06", "Yerawada", "येरवडा", "Pune Municipal Corporation", "MH.PUN.PMC", 18.553, 73.887, 98000, 41, 78, 70, 60, 85, 4),
    ("PMC-W31", "Kothrud", "कोथरूड", "Pune Municipal Corporation", "MH.PUN.PMC", 18.507, 73.807, 120000, 6, 94, 82, 90, 97, 5),
    ("PCMC-W02", "Moshi", "मोशी", "Pimpri-Chinchwad Municipal Corporation", "MH.PUN.PCMC", 18.671, 73.851, 58000, 15, 85, 30, 50, 70, 2),
    ("PCMC-W01", "Chikhli", "चिखली", "Pimpri-Chinchwad Municipal Corporation", "MH.PUN.PCMC", 18.681, 73.811, 76000, 24, 82, 44, 48, 66, 1),
]

# --------------------------------------------------------------------------------------------
# Demand "needs" -> seed clusters with request templates (language, original, English)
# --------------------------------------------------------------------------------------------
NEEDS = [
    dict(cluster_id="CL-BR-0001", state="BR", units=["BR.GAY.TEK.SNB", "BR.GAY.TEK.KRM", "BR.GAY.TEK.BLH"],
         category="roads_bridges", sub="bridge", n=146, span=60, recent=0.55, urgency="high",
         vulnerable=["children"], season="monsoon", status="Under Review",
         summary="No bridge over the river near Sonbarsa, Kurmawan and Belhari; villages are cut off and children miss school every monsoon.",
         templates=[
             ("hi", "सोनबरसा गाँव में नदी पर पुल नहीं है। बरसात में बच्चे तीन महीने स्कूल नहीं जा पाते।", "There is no bridge over the river in Sonbarsa village. Children cannot go to school for three months during the monsoon."),
             ("hi", "कुरमावां से टेकारी जाने के लिए नदी पार करनी पड़ती है, बारिश में रास्ता बंद हो जाता है। पुल चाहिए।", "To go from Kurmawan to Tekari we have to cross the river; the route closes in the rains. We need a bridge."),
             ("hi", "बेलहरी के लोग बरसात में अस्पताल नहीं पहुँच पाते, नदी पर पुल बनवाइए।", "People of Belhari cannot reach the hospital in the monsoon; please build a bridge over the river."),
             ("hi", "हर साल बाढ़ में सोनबरसा का संपर्क टूट जाता है, बच्चों की पढ़ाई छूट जाती है।", "Every year in the floods Sonbarsa gets cut off and the children's studies stop."),
             ("en", "Sonbarsa needs a bridge. Kids wade across the river to reach school in the monsoon.", "Sonbarsa needs a bridge. Kids wade across the river to reach school in the monsoon."),
         ]),
    dict(cluster_id="CL-BR-0002", state="BR", units=["BR.GAY.SHG.DMR"], category="roads_bridges", sub="rural_road",
         n=58, span=90, recent=0.3, urgency="medium", vulnerable=["elderly", "pregnant women"], season="monsoon",
         status="Under Review",
         summary="Kutcha road from Dumri to Sherghati becomes impassable in the rains; ambulances cannot reach the village.",
         templates=[
             ("hi", "डुमरी गाँव की कच्ची सड़क बरसात में कीचड़ बन जाती है, एम्बुलेंस नहीं आ पाती।", "The kutcha road of Dumri village turns to mud in the rains; ambulances cannot come."),
             ("hi", "डुमरी से शेरघाटी तक पक्की सड़क चाहिए।", "We need a paved road from Dumri to Sherghati."),
         ]),
    dict(cluster_id="CL-BR-0003", state="BR", units=["BR.GAY.IMG.KTH", "BR.GAY.IMG.RMP"], category="drinking_water",
         sub="handpump_repair", n=72, span=45, recent=0.7, urgency="high", vulnerable=["women", "children"],
         season="summer", status="Clustered",
         summary="Handpumps broken and Nal Jal taps dry in Kothi and Rampur (Imamganj); women walk long distances for water.",
         templates=[
             ("hi", "कोठी में सारे हैंडपंप खराब हैं, औरतों को दो किलोमीटर दूर से पानी लाना पड़ता है।", "All the handpumps in Kothi are broken; women have to fetch water from two kilometres away."),
             ("hi", "इमामगंज के रामपुर में नल जल योजना का पानी नहीं आता।", "Water from the Nal Jal scheme does not come in Rampur, Imamganj."),
         ]),
    dict(cluster_id="CL-BR-0004", state="BR", units=["BR.GAY.BDG.BKR", "BR.GAY.BDG.MST"], category="health_facility",
         sub="phc", n=40, span=120, recent=0.25, urgency="medium", vulnerable=["pregnant women"], season=None,
         status="Clustered",
         summary="No functional health centre in Bakraur and Mastipur; deliveries require travel to Gaya city.",
         templates=[
             ("hi", "बकरौर में स्वास्थ्य केंद्र नहीं है, प्रसव के लिए गया शहर जाना पड़ता है।", "There is no health centre in Bakraur; for deliveries we have to go to Gaya city."),
             ("hi", "मस्तीपुर में डॉक्टर हफ्ते में एक दिन भी नहीं आते।", "In Mastipur the doctor does not come even one day a week."),
         ]),
    dict(cluster_id="CL-BR-0005", state="BR", units=["BR.GAY.WZG.FTP"], category="school_education", sub="secondary_school",
         n=30, span=90, recent=0.4, urgency="medium", vulnerable=["girls"], season=None, status="Clustered",
         summary="No high school in Fatehpur; girls drop out after class eight.",
         templates=[
             ("hi", "फतेहपुर में हाई स्कूल नहीं है, लड़कियाँ आठवीं के बाद पढ़ाई छोड़ देती हैं।", "There is no high school in Fatehpur; girls drop out after class eight."),
         ]),
    dict(cluster_id="CL-BR-0006", state="BR", units=["BR.AUR.OBR.KHR"], category="roads_bridges", sub="bridge",
         n=38, span=60, recent=0.5, urgency="high", vulnerable=["children"], season="monsoon", status="Clustered",
         summary="No bridge on the Punpun river near Khaira; the village is cut off in the monsoon.",
         templates=[
             ("hi", "खैरा के पास पुनपुन नदी पर पुल नहीं है, बरसात में गाँव कट जाता है।", "There is no bridge on the Punpun river near Khaira; the village is cut off in the monsoon."),
         ]),
    dict(cluster_id="CL-BR-0007", state="BR", units=["BR.AUR.DEO.DEO"], category="electricity", sub="transformer",
         n=25, span=30, recent=0.8, urgency="medium", vulnerable=[], season=None, status="Clustered",
         summary="Burnt-out transformer in Deo; no electricity for days.",
         templates=[
             ("hi", "देव में ट्रांसफार्मर जल गया है, दस दिन से बिजली नहीं है।", "The transformer in Deo has burnt out; there has been no electricity for ten days."),
         ]),
    dict(cluster_id="CL-AP-0001", state="AP", units=["AP.ATP.KDG.MDG", "AP.ATP.KDG.VRL"], category="drinking_water",
         sub="piped_supply", n=118, span=60, recent=0.6, urgency="high", vulnerable=["women", "elderly"],
         season="summer", status="Under Review",
         summary="No reliable drinking water in Mudigal and Varli (Kalyandurg); tanker once a week, borewells dry.",
         templates=[
             ("te", "మా ఊరు ముదిగల్ లో తాగునీరు లేదు. వారానికి ఒక్కసారే ట్యాంకర్ వస్తుంది.", "Our village Mudigal has no drinking water. The tanker comes only once a week."),
             ("te", "వర్లి గ్రామంలో బోరు ఎండిపోయింది, మహిళలు దూరం నుండి నీళ్ళు తెస్తున్నారు.", "The borewell in Varli village has dried up; women are bringing water from far away."),
             ("te", "ముదిగల్ లో కుళాయి కనెక్షన్ ఇచ్చారు కానీ నీళ్ళు రావడం లేదు.", "Tap connections were given in Mudigal but no water comes."),
         ]),
    dict(cluster_id="CL-AP-0002", state="AP", units=["AP.ATP.DMV.CGC", "AP.ATP.DMV.PTK"], category="drinking_water",
         sub="fluoride_free_water", n=64, span=90, recent=0.35, urgency="high", vulnerable=["children", "elderly"],
         season=None, status="Clustered",
         summary="High-fluoride groundwater in Chigicherla and Pothukunta (Dharmavaram); safe drinking water needed.",
         templates=[
             ("te", "చిగిచెర్ల లో నీటిలో ఫ్లోరైడ్ ఎక్కువ, పిల్లల పళ్ళు పాడవుతున్నాయి.", "The water in Chigicherla has high fluoride; children's teeth are getting damaged."),
             ("te", "పోతుకుంట లో సురక్షితమైన తాగునీరు కావాలి.", "Pothukunta needs safe drinking water."),
         ]),
    dict(cluster_id="CL-AP-0003", state="AP", units=["AP.ATP.RYD.KNK"], category="irrigation", sub="check_dam",
         n=35, span=120, recent=0.2, urgency="medium", vulnerable=["farmers"], season="kharif", status="Clustered",
         summary="Canal water not reaching the Kanekal tank; crops drying.",
         templates=[
             ("te", "కణేకల్ చెరువుకు కాలువ నీరు రావడం లేదు, పంటలు ఎండిపోతున్నాయి.", "Canal water is not reaching the Kanekal tank; crops are drying up."),
         ]),
    dict(cluster_id="CL-AP-0004", state="AP", units=["AP.ATP.GTY.GTY"], category="health_facility", sub="ambulance",
         n=22, span=60, recent=0.5, urgency="medium", vulnerable=[], season=None, status="Clustered",
         summary="No ambulance available at night in Gooty.",
         templates=[
             ("te", "గుత్తి లో రాత్రి అంబులెన్స్ దొరకడం లేదు.", "No ambulance is available at night in Gooty."),
         ]),
    dict(cluster_id="CL-AP-0005", state="AP", units=["AP.KNL.PTK.HSR"], category="drinking_water", sub="tanker_supply",
         n=44, span=45, recent=0.75, urgency="high", vulnerable=["women"], season="summer", status="Clustered",
         summary="Water tanker reaches Hosur (Pattikonda) only once every ten days.",
         templates=[
             ("te", "హోసూరు లో నీటి ట్యాంకర్ పది రోజులకు ఒకసారి వస్తుంది.", "In Hosur the water tanker comes once every ten days."),
         ]),
    dict(cluster_id="CL-AP-0006", state="AP", units=["AP.KNL.ADN.PHV"], category="school_education", sub="classrooms",
         n=20, span=90, recent=0.3, urgency="medium", vulnerable=["children"], season=None, status="Clustered",
         summary="Not enough classrooms in the Pedda Harivanam school.",
         templates=[
             ("te", "పెద్ద హరివాణం బడిలో తరగతి గదులు సరిపోవడం లేదు.", "The school in Pedda Harivanam does not have enough classrooms."),
         ]),
    dict(cluster_id="CL-MH-0001", state="MH", units=["PMC-W04", "PMC-W22"], category="public_transport", sub="bus_route",
         n=96, span=60, recent=0.6, urgency="medium", vulnerable=["students", "women commuters"], season=None,
         status="Under Review",
         summary="Too few morning buses between Kharadi and Hadapsar; long waits at the EON IT Park stop.",
         templates=[
             ("en", "No direct PMPML bus from Kharadi to Hadapsar in the morning; we wait 40 minutes at EON IT Park.", "No direct PMPML bus from Kharadi to Hadapsar in the morning; we wait 40 minutes at EON IT Park."),
             ("en", "Please start a feeder bus between Kharadi and Hadapsar railway station.", "Please start a feeder bus between Kharadi and Hadapsar railway station."),
             ("hi", "खराडी से हडपसर के लिए सुबह बस बहुत कम है।", "There are very few morning buses from Kharadi to Hadapsar."),
         ]),
    dict(cluster_id="CL-MH-0002", state="MH", units=["PMC-W03"], category="public_transport", sub="last_mile",
         n=70, span=45, recent=0.7, urgency="medium", vulnerable=["elderly"], season=None, status="Clustered",
         summary="No bus stop within walking distance of new housing societies in Wagholi.",
         templates=[
             ("en", "Wagholi has no bus stop within walking distance of the new housing societies.", "Wagholi has no bus stop within walking distance of the new housing societies."),
             ("en", "Elderly residents in Wagholi cannot reach the main road bus stop. Need a feeder bus.", "Elderly residents in Wagholi cannot reach the main road bus stop. Need a feeder bus."),
         ]),
    dict(cluster_id="CL-MH-0003", state="MH", units=["PCMC-W02"], category="public_transport", sub="bus_route",
         n=34, span=60, recent=0.45, urgency="medium", vulnerable=[], season=None, status="Clustered",
         summary="Moshi needs a bus connection to Bhosari MIDC.",
         templates=[
             ("en", "Moshi needs a direct bus connection to Bhosari MIDC for factory workers.", "Moshi needs a direct bus connection to Bhosari MIDC for factory workers."),
         ]),
    dict(cluster_id="CL-MH-0004", state="MH", units=["PMC-W26"], category="sanitation", sub="drainage",
         n=52, span=30, recent=0.9, urgency="high", vulnerable=["children"], season="monsoon", status="Clustered",
         summary="Open drains overflow in Kondhwa whenever it rains.",
         templates=[
             ("en", "Open drains overflow in Kondhwa every time it rains; dengue cases are rising.", "Open drains overflow in Kondhwa every time it rains; dengue cases are rising."),
             ("hi", "कोंढवा में बारिश में नाली का पानी घरों में घुस जाता है।", "In Kondhwa drain water enters homes when it rains."),
         ]),
    dict(cluster_id="CL-MH-0005", state="MH", units=["PCMC-W01"], category="drinking_water", sub="piped_supply",
         n=41, span=60, recent=0.5, urgency="medium", vulnerable=[], season="summer", status="Clustered",
         summary="Chikhli gets piped water only one hour on alternate days.",
         templates=[
             ("en", "Chikhli gets piped water only one hour on alternate days.", "Chikhli gets piped water only one hour on alternate days."),
         ]),
    dict(cluster_id="CL-MH-0006", state="MH", units=["PMC-W06"], category="electricity", sub="streetlights",
         n=18, span=30, recent=0.6, urgency="medium", vulnerable=["women"], season=None, status="Clustered",
         summary="Streetlights not working on lanes in Yerawada; unsafe for women at night.",
         templates=[
             ("en", "Streetlights are not working in the Yerawada lanes; it is unsafe for women at night.", "Streetlights are not working in the Yerawada lanes; it is unsafe for women at night."),
         ]),
]

SENTIMENT = {"critical": -0.8, "high": -0.6, "medium": -0.4, "low": -0.2}
CHANNELS = [("web", 0.4), ("telegram", 0.4), ("voice", 0.2)]
PREFIX = {
    "hi": ["", "", "कृपया ध्यान दें। ", "सर, "],
    "te": ["", "", "దయచేసి సహాయం చేయండి. ", "అయ్యా, "],
    "en": ["", "", "Please help. ", "Sir, "],
}


def _meta(source: str, ref: str, scope: str) -> dict:
    return {
        "source": source,
        "reference_timestamp": ref,
        "dataset_version": DATASET_VERSION,
        "geographic_scope": scope,
        "is_sample": True,
        "is_synthetic": True,
        "generated_by": GENERATOR,
    }


def write_csv(path: Path, header: list[str], rows: list[list]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)


def write_states() -> None:
    write_csv(
        OUT / "states/BR/bihar_village_indicators.csv",
        ["jila_naam", "jila_code", "prakhand_naam", "prakhand_code", "gram_naam", "gram_naam_hindi", "gram_code",
         "akshansh", "deshantar", "jansankhya_2011", "anusuchit_jati_janjati_pratishat", "saksharta_dar",
         "barahmasi_sadak", "nal_jal_pratishat", "vidyut_parivar_pratishat", "phc_doori_km",
         "madhyamik_vidyalay_5km", "aakankshi_jila", "sandarbh_varsh"],
        [[*u[:13], u[13], u[14], u[15], u[16], BR_ASPIRATIONAL[u[1]], 2024] for u in BR_UNITS],
    )
    write_csv(
        OUT / "states/BR/bihar_yojana_suchi.csv",
        ["yojana_id", "yojana_naam", "shreni", "prakhand_code", "gram_codes", "sthiti", "rashi_lakh",
         "aarambh_tithi", "labharthi_jansankhya"],
        [
            ["BR-PMGSY-2025-117", "PMGSY: Dumri-Sherghati all-weather road", "सड़क", "BR.GAY.SHG", "BR.GAY.SHG.DMR", "स्वीकृत", 185, "2025-11-10", 4200],
            ["BR-HGNJ-2024-044", "Har Ghar Nal Jal: Kothi", "पेयजल", "BR.GAY.IMG", "BR.GAY.IMG.KTH", "चालू", 62, "2024-06-01", 1500],
            ["BR-MMGSY-2022-009", "Mukhyamantri Gram Sampark: Fatehpur culvert", "पुल", "BR.GAY.WZG", "BR.GAY.WZG.FTP", "पूर्ण", 240, "2022-02-14", 6100],
            ["BR-HSC-2025-003", "Health sub-centre: Bakraur", "स्वास्थ्य", "BR.GAY.BDG", "BR.GAY.BDG.BKR", "स्वीकृत", 95, "2025-09-01", 2600],
        ],
    )
    ap = []
    for u in AP_UNITS:
        ap.append({
            "district": {"name": u[0], "code": u[1]},
            "mandal": {"name": u[2], "code": u[3]},
            "habitation": {"name": u[4], "name_te": u[5], "code": u[6]},
            "location": {"lat": u[7], "lon": u[8]},
            "census_2011_population": u[9],
            "sc_pct": u[10], "st_pct": u[11], "literacy_pct": u[12],
            "fhtc_coverage_pct": u[13], "irrigated_area_pct": u[14], "phc_distance_km": u[15],
            "ref_year": 2025,
        })
    p = OUT / "states/AP/ap_habitation_indicators.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"_meta": _meta("Synthetic sample in the style of AP RWS&S habitation MIS", "2025-03-31", "Andhra Pradesh: Anantapur, Kurnool"),
                             "habitations": ap}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    write_csv(
        OUT / "states/AP/ap_jjm_works.csv",
        ["work_id", "scheme", "component", "mandal_code", "habitation_codes", "work_status", "est_cost_crore",
         "sanction_date", "households_covered"],
        [
            ["AP-JJM-KDG-0231", "Jal Jeevan Mission", "Retrofitting of piped water supply", "AP.ATP.KDG", "AP.ATP.KDG.MDG", "Grounded", 3.4, "2025-08-20", 520],
            ["AP-JJM-PTK-0045", "Jal Jeevan Mission", "New single-village scheme", "AP.KNL.PTK", "AP.KNL.PTK.HSR", "Not Started", 1.1, "2026-03-01", 300],
            ["AP-SS-ADN-0012", "Samagra Shiksha", "Additional classrooms", "AP.KNL.ADN", "AP.KNL.ADN.PHV", "Completed", 0.6, "2024-07-01", 900],
        ],
    )
    write_csv(
        OUT / "states/MH/pune_ward_stats.csv",
        ["ward_no", "ward_name", "ward_name_mr", "corporation", "corporation_code", "district", "district_code",
         "lat", "lng", "population_2011", "slum_population_pct", "literacy_pct", "pop_within_500m_bus_stop_pct",
         "sewer_connection_pct", "households_piped_water_pct", "water_supply_hours", "data_year"],
        [[u[0], u[1], u[2], u[3], u[4], "Pune", "MH.PUN", *u[5:], 2024] for u in MH_UNITS],
    )
    write_csv(
        OUT / "states/MH/pune_capex_projects.csv",
        ["project_code", "project_title", "department", "ward_nos", "status", "budget_inr", "start", "beneficiary_pop"],
        [
            ["PMC-PMPML-2026-07", "New PMPML feeder routes Kharadi-Hadapsar", "PMPML", "PMC-W04|PMC-W22", "Tendered", 42000000, "2026-06-15", 60000],
            ["PMC-SWD-2025-31", "Storm water drain upgrade, Kondhwa", "Storm Water Drainage", "PMC-W26", "Work in progress", 120000000, "2025-12-01", 40000],
            ["PCMC-WS-2024-12", "24x7 water supply, Chikhli", "Water Supply", "PCMC-W01", "Work in progress", 380000000, "2024-10-01", 76000],
        ],
    )


def unit_index() -> dict[str, dict]:
    idx = {}
    for u in BR_UNITS:
        idx[u[6]] = {"state": "BR", "district": u[0], "district_code": u[1], "block": u[2], "block_code": u[3], "name": u[4]}
    for u in AP_UNITS:
        idx[u[6]] = {"state": "AP", "district": u[0], "district_code": u[1], "block": u[2], "block_code": u[3], "name": u[4]}
    for u in MH_UNITS:
        idx[u[0]] = {"state": "MH", "district": "Pune", "district_code": "MH.PUN", "block": u[3], "block_code": u[4], "name": u[1]}
    return idx


def write_requests() -> None:
    rng = random.Random(SEED)
    units = unit_index()
    requests, clusters = [], []
    seq = 0
    for need in NEEDS:
        citizens: list[str] = []
        created = []
        for i in range(need["n"]):
            recent = rng.random() < need["recent"]
            if recent or need["span"] <= 30:
                age = rng.uniform(0, min(30, need["span"]))
            else:
                age = rng.uniform(30, need["span"])
            ts = AS_OF - timedelta(days=age, minutes=rng.randint(0, 600))
            # ~7% repeat submissions from a citizen already in this cluster (must not inflate demand)
            if citizens and rng.random() < 0.07:
                cit = rng.choice(citizens)
            else:
                cit = "CIT-" + hashlib.sha256(f"{need['cluster_id']}-{i}".encode()).hexdigest()[:10]
                citizens.append(cit)
            lang, original, english = rng.choice(need["templates"])
            unit_code = rng.choice(need["units"])
            u = units[unit_code]
            ch = rng.choices([c for c, _ in CHANNELS], weights=[w for _, w in CHANNELS])[0]
            seq += 1
            created.append(ts)
            requests.append({
                "request_id": f"SYN-{seq:05d}",
                "citizen_id": cit,
                "channel": ch,
                "language": lang,
                "text_original": rng.choice(PREFIX[lang]) + original,
                "text_en": english,
                "category": need["category"],
                "sub_category": need["sub"],
                "summary_en": english,
                "urgency": need["urgency"],
                "urgency_reason": None,
                "est_beneficiaries": None,
                "vulnerable_groups": need["vulnerable"],
                "seasonality": need["season"],
                "sentiment": SENTIMENT[need["urgency"]],
                "confidence": round(rng.uniform(0.72, 0.95), 2),
                "state": u["state"],
                "lgd_district": u["district_code"],
                "lgd_block": u["block_code"],
                "lgd_unit": unit_code,
                "resolution_method": "exact_match",
                "resolution_confidence": 0.9,
                "cluster_id": need["cluster_id"],
                "status": "Clustered",
                "created_at": ts.isoformat(),
                "model_name": "synthetic-generator",
                "model_version": DATASET_VERSION,
                "prompt_version": "n/a",
                "is_synthetic": True,
            })
        u0 = units[need["units"][0]]
        clusters.append({
            "cluster_id": need["cluster_id"],
            "state": need["state"],
            "category": need["category"],
            "sub_category": need["sub"],
            "lgd_district": u0["district_code"],
            "lgd_block": u0["block_code"],
            "lgd_units": need["units"],
            "summary": need["summary"],
            "status": need["status"],
            "is_synthetic": True,
        })
    requests.sort(key=lambda r: r["created_at"])
    with (OUT / "requests_synthetic.jsonl").open("w", encoding="utf-8") as f:
        for r in requests:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    (OUT / "clusters_synthetic.json").write_text(
        json.dumps({"_meta": _meta("Synthetic seed demand clusters", AS_OF.isoformat(), "BR, AP, MH sample areas"),
                    "clusters": clusters}, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"requests: {len(requests)}  clusters: {len(clusters)}")


def write_manifest() -> None:
    manifest = {
        "dataset_version": DATASET_VERSION,
        "generated_by": GENERATOR,
        "seed": SEED,
        "as_of": AS_OF.isoformat(),
        "notice": "ALL FILES ARE SYNTHETIC SAMPLE DATA for the hackathon demo. Codes are LGD-style sample codes, not official LGD codes. Values are illustrative, not real statistics.",
        "datasets": [
            {"path": "states/BR/bihar_village_indicators.csv", **_meta("Synthetic sample in the style of Census 2011 PCA + Bihar rural MIS", "2024", "Bihar: Gaya, Aurangabad (villages)")},
            {"path": "states/BR/bihar_yojana_suchi.csv", **_meta("Synthetic sample scheme list (PMGSY / Har Ghar Nal Jal style)", "2025", "Bihar: Gaya (blocks)")},
            {"path": "states/AP/ap_habitation_indicators.json", **_meta("Synthetic sample in the style of AP RWS&S habitation MIS", "2025", "Andhra Pradesh: Anantapur, Kurnool (habitations)")},
            {"path": "states/AP/ap_jjm_works.csv", **_meta("Synthetic sample JJM works list", "2026", "Andhra Pradesh (mandals)")},
            {"path": "states/MH/pune_ward_stats.csv", **_meta("Synthetic sample ward statistics (PMC / PCMC style)", "2024", "Maharashtra: Pune urban wards")},
            {"path": "states/MH/pune_capex_projects.csv", **_meta("Synthetic sample municipal capital-works list", "2026", "Maharashtra: Pune urban wards")},
            {"path": "requests_synthetic.jsonl", **_meta("Template-generated multilingual citizen requests (no AI used)", AS_OF.isoformat(), "BR, AP, MH sample areas")},
            {"path": "clusters_synthetic.json", **_meta("Seed demand clusters for the synthetic requests", AS_OF.isoformat(), "BR, AP, MH sample areas")},
        ],
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    write_states()
    write_requests()
    write_manifest()
