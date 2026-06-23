def detect_emotion(text: str, lang: str = "en") -> str:
    t = text.lower()

    # Simple keyword rules (extend as you like)
    anxiety = ["anxious", "panic", "worried", "nervous", "overthinking", "fear", "scared", "presentation", "presentations"]
    stress  = ["stress", "stressed", "pressure", "burnout", "tired", "overwhelmed", "deadline", "project", "assignment", "workload", "presentation"]
    sad     = ["sad", "depressed", "hopeless", "cry", "lonely", "empty", "down"]
    angry   = ["angry", "furious", "irritated", "mad", "annoyed"]
    happy   = ["happy", "good", "great", "relieved", "excited", "glad"]

    ta_anxiety = ["பயம்", "பதட்ட", "கவலை", "நர்வஸ்", "அதிகமாக யோசிக்க", "அஞ்ச", "டென்ஷன்"]
    ta_stress  = ["ஸ்ட்ரெஸ்", "அழுத்த", "சோர்வ", "முடங்கி", "ஓவர்வெல்ம்", "தளர்ச்சி", "மனம் களைப்பு"]
    ta_sad     = ["சோகம்", "துக்க", "மனச்சோர்வ", "தனிம", "கண்ணீர்", "நம்பிக்கையில்லை", "மனசு கஷ்டம்"]
    ta_angry   = ["கோப", "எரிச்ச", "சினம்", "கடுப்ப", "மூட் ஆஃப்"]
    ta_happy   = ["சந்தோஷ", "மகிழ்ச்ச", "நன்றாக", "ரிலாக்ஸ்", "உற்சாக", "சூப்பர்"]


    def contains(words):
        return any(w in t for w in words)

    if lang == "ta":
        if contains(ta_anxiety): return "anxiety"
        if contains(ta_stress):  return "stress"
        if contains(ta_sad):     return "sadness"
        if contains(ta_angry):   return "anger"
        if contains(ta_happy):   return "happiness"
        return "neutral"

    if contains(anxiety): return "anxiety"
    if contains(stress):  return "stress"
    if contains(sad):     return "sadness"
    if contains(angry):   return "anger"
    if contains(happy):   return "happiness"
    return "neutral"
