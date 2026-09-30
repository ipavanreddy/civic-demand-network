"""Citizen-facing message templates in English, Hindi and Telugu (PRD §10, §19).

Analysis always runs on canonical English; only presentation is localised. Adding a language =
adding a column here + a BCP-47 code in integrations/google_speech.py.
"""
from __future__ import annotations

from app.pipeline import taxonomy

TEMPLATES = {
    "confirm": {
        "en": "Thank you. We understood your request as: {category} in {place}. Request ID: {id}. Please confirm or correct.",
        "hi": "धन्यवाद। हमने आपका अनुरोध समझा: {place} में {category}। अनुरोध संख्या: {id}। कृपया पुष्टि करें या सुधारें।",
        "te": "ధన్యవాదాలు. మీ అభ్యర్థనను ఇలా అర్థం చేసుకున్నాం: {place} లో {category}. అభ్యర్థన సంఖ్య: {id}. దయచేసి నిర్ధారించండి లేదా సరిచేయండి.",
    },
    "ambiguous": {
        "en": "There is more than one place called {name}. Which block is it in? {options}",
        "hi": "{name} नाम की एक से अधिक जगहें हैं। यह किस प्रखंड में है? {options}",
        "te": "{name} పేరుతో ఒకటి కంటే ఎక్కువ ప్రదేశాలు ఉన్నాయి. ఇది ఏ మండలంలో ఉంది? {options}",
    },
    "unresolved": {
        "en": "Which village or ward is this request about?",
        "hi": "यह अनुरोध किस गाँव या वार्ड के बारे में है?",
        "te": "ఈ అభ్యర్థన ఏ గ్రామం లేదా వార్డు గురించి?",
    },
    "low_confidence": {
        "en": "We are not sure we understood. Could you describe the problem and the place again?",
        "hi": "हमें पूरा यकीन नहीं है कि हमने सही समझा। क्या आप समस्या और जगह फिर से बता सकते हैं?",
        "te": "మేము సరిగ్గా అర్థం చేసుకున్నామో లేదో ఖచ్చితంగా తెలియదు. సమస్య మరియు ప్రదేశాన్ని మళ్ళీ చెప్పగలరా?",
    },
    "clustered": {
        "en": "Your request {id} has joined {n} similar requests from {unique} citizens in your area. Status: {status}.",
        "hi": "आपका अनुरोध {id} आपके क्षेत्र के {unique} नागरिकों के {n} समान अनुरोधों के साथ जुड़ गया है। स्थिति: {status}।",
        "te": "మీ అభ్యర్థన {id} మీ ప్రాంతంలోని {unique} పౌరుల {n} ఇలాంటి అభ్యర్థనలతో కలిసింది. స్థితి: {status}.",
    },
    "new_cluster": {
        "en": "Your request {id} is the first of its kind in your area and has started a new demand group. Status: {status}.",
        "hi": "आपका अनुरोध {id} आपके क्षेत्र में इस तरह का पहला अनुरोध है और एक नया मांग समूह शुरू हुआ है। स्थिति: {status}।",
        "te": "మీ అభ్యర్థన {id} మీ ప్రాంతంలో ఈ రకమైన మొదటిది, కొత్త డిమాండ్ సమూహం ప్రారంభమైంది. స్థితి: {status}.",
    },
}

STATUS = {
    "Received": {"hi": "प्राप्त", "te": "స్వీకరించబడింది"},
    "Understood": {"hi": "समझा गया", "te": "అర్థం చేసుకోబడింది"},
    "Needs Clarification": {"hi": "स्पष्टीकरण आवश्यक", "te": "స్పష్టత అవసరం"},
    "Clustered": {"hi": "समूहित", "te": "సమూహం చేయబడింది"},
    "Under Review": {"hi": "समीक्षाधीन", "te": "సమీక్షలో ఉంది"},
    "Recommended": {"hi": "अनुशंसित", "te": "సిఫార్సు చేయబడింది"},
    "Sanctioned": {"hi": "स्वीकृत", "te": "మంజూరు చేయబడింది"},
    "Completed": {"hi": "पूर्ण", "te": "పూర్తయింది"},
}


def status_label(status: str, language: str) -> str:
    return STATUS.get(status, {}).get(language, status)


def render(key: str, language: str, **values) -> str:
    table = TEMPLATES[key]
    text = table.get(language) or table["en"]
    if "category" in values:
        values["category"] = taxonomy.label(values["category"], language)
    if "status" in values:
        values["status"] = status_label(values["status"], language)
    return text.format(**values)
