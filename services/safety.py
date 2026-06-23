import re

# --- Crisis detection ---
CRISIS_PATTERNS = [
    r"\bkill myself\b",
    r"\bsuicide\b",
    r"\bend my life\b",
    r"\bself[- ]harm\b",
    r"\bcut myself\b",
    r"\bwant to die\b",
    # Tamil (basic)
    r"தற்கொலை",
    r"சாகணும்",
    r"என்னை கொல்ல",
    r"என் வாழ்க்கை முடிக்க",
    # Hindi (basic)
    r"आत्महत्या",
    r"मरना चाहता",
    r"खुद को मार",
]

def is_crisis(text: str) -> bool:
    t = (text or "").lower()
    for pat in CRISIS_PATTERNS:
        if re.search(pat, t, re.IGNORECASE):
            return True
    return False

def crisis_message(lang: str) -> str:
    if lang == "ta":
        return (
            "நீங்க இப்படி feel பண்ணுறது ரொம்ப கஷ்டம். ஆனால் நான் அவசர உதவியை மாற்ற முடியாது.\n\n"
            "👉 இப்போது உடனடி உதவி:\n"
            "• Emergency number-க்கு call பண்ணுங்க (India: 112)\n"
            "• நம்பிக்கை உள்ள ஒருவரை இப்போதே தொடர்பு கொள்ளுங்க\n"
            "• அருகிலுள்ள hospital/helpline-க்கு செல்லுங்க\n\n"
            "நீங்க பாதுகாப்பாக இருக்கணும். நீங்கள் இப்போ தனியாக இருக்கிறீர்களா?"
        )
    if lang == "hi":
        return (
            "मुझे दुख है कि आप ऐसा महसूस कर रहे हैं, लेकिन मैं आपातकालीन मदद का विकल्प नहीं हूँ।\n\n"
            "तुरंत मदद के लिए:\n"
            "• इमरजेंसी नंबर पर कॉल करें (India: 112)\n"
            "• किसी भरोसेमंद व्यक्ति को अभी संपर्क करें\n"
            "• नज़दीकी अस्पताल/हेल्पलाइन पर जाएँ\n\n"
            "आप अकेले तो नहीं हैं अभी?"
        )
    return (
        "I’m really sorry you’re feeling this way, but I can’t provide emergency help.\n\n"
        "Please seek immediate support:\n"
        "• Call your local emergency number (India: 112)\n"
        "• Reach out to someone you trust right now\n"
        "• Go to the nearest hospital/helpline\n\n"
        "You matter. Are you alone right now?"
    )

# --- Physical symptom handling (safe) ---
SYMPTOM_PATTERNS = [
    r"\bstomach pain\b", r"\bbelly pain\b", r"\babdominal pain\b",
    r"\bheadache\b", r"\bhead pain\b",
    r"\bfever\b", r"\bnausea\b", r"\bvomit\b",
    r"\bdizzy\b", r"\bchest pain\b", r"\bbreathing problem\b",
    # Tamil common words (basic)
    r"வயிறு வலி", r"தலைவலி", r"காய்ச்சல்", r"மயக்கம்", r"மார்வலி",
    # Hindi (basic)
    r"पेट दर्द", r"सिरदर्द", r"बुखार", r"चक्कर", r"सीने में दर्द",
]

def is_physical_symptom(text: str) -> bool:
    t = (text or "").lower()
    return any(re.search(p, t, re.IGNORECASE) for p in SYMPTOM_PATTERNS)

def physical_symptom_message(lang: str) -> str:
    if lang == "ta":
        return (
            "உங்களுக்கு உடல் வலி/அசௌகரியம் இருக்கிறது போல.\n"
            "நான் மருத்துவர் அல்ல; diagnosis சொல்ல முடியாது.\n"
            "வலி அதிகமாக இருந்தால் அல்லது தொடர்ந்து இருந்தால் மருத்துவரை அணுகுங்கள்.\n"
            "இப்போ உடனடி உதவி: தண்ணீர் குடிங்க, ஓய்வு எடுக்கவும், மெதுவா 2 நிமிடம் மூச்சுப்பயிற்சி.\n"
            "இந்த வலி எத்தனை நேரமா இருக்கிறது? தீவிரம் (1–10) எத்தனை?"
        )
    if lang == "hi":
        return (
            "लगता है आपको शारीरिक दर्द/असहजता है।\n"
            "मैं डॉक्टर नहीं हूँ, इसलिए निदान नहीं कर सकता।\n"
            "अगर दर्द तेज है या लगातार है, तो कृपया डॉक्टर से संपर्क करें।\n"
            "अभी: थोड़ा पानी पिएँ, आराम करें, और 2 मिनट धीमी साँस लें.\n"
            "यह कितनी देर से हो रहा है और दर्द 1–10 में कितना है?"
        )
    return (
        "It sounds like you’re having a physical symptom (pain/discomfort).\n"
        "I’m not a doctor, so I can’t diagnose. If the pain is severe or persistent, please seek medical help.\n"
        "Right now: sip water, rest, and try slow breathing for 2 minutes.\n"
        "How long has it been happening, and how intense is it (1–10)?"
    )
