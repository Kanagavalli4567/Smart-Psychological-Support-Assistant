import requests
import json
import random
import time
from typing import Dict, Optional, List
import pyttsx3  # Changed from gTTS to pyttsx3
import threading
import queue

class GroqChatModel:
    def __init__(self, api_key):
        self.api_key = api_key
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama-3.1-8b-instant"
        self.use_api = bool(api_key and api_key != "" and api_key != "your-api-key-here")
        self.max_retries = 2
        self.retry_delay = 2  # seconds
        
        # Initialize TTS engine with male voice only
        self.tts_engine = None
        self._init_tts_engine()
        
    def _init_tts_engine(self):
        """Initialize TTS engine with male voice only"""
        try:
            self.tts_engine = pyttsx3.init()
            
            # Get available voices
            voices = self.tts_engine.getProperty('voices')
            
            # Select male voice (try different indices based on system)
            male_voice_found = False
            
            for voice in voices:
                # Check for male voice indicators
                voice_name = voice.name.lower()
                if 'male' in voice_name or 'david' in voice_name or 'mark' in voice_name:
                    self.tts_engine.setProperty('voice', voice.id)
                    male_voice_found = True
                    print(f"✅ Selected male voice: {voice.name}")
                    break
            
            # If no male voice found, try specific indices (0 is often male on some systems)
            if not male_voice_found and len(voices) > 1:
                # On Windows, voice 1 is often male (Microsoft David)
                if len(voices) >= 2:
                    self.tts_engine.setProperty('voice', voices[1].id)
                    print(f"✅ Using alternative voice: {voices[1].name}")
                else:
                    self.tts_engine.setProperty('voice', voices[0].id)
                    print(f"⚠️ Using default voice: {voices[0].name}")
            
            # Set speech properties for male voice characteristics
            self.tts_engine.setProperty('rate', 150)    # Speed (words per minute)
            self.tts_engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)
            
            print("✅ TTS engine initialized with male voice preference")
            
        except Exception as e:
            print(f"⚠️ Could not initialize pyttsx3: {str(e)}")
            print("Installing pyttsx3: pip install pyttsx3")
            self.tts_engine = None
    
    def detect_language_from_text(self, text: str) -> str:
        """Detect language from text content"""
        tamil_chars = set('கஙசஞடணதநபமயரலவழளறனஂஃஅஆஇஈஉஊஎஏஐஒஓஔ')
        hindi_chars = set('कखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसहअआइईउऊऋएऐओऔंः')
        
        tamil_count = sum(1 for char in text if char in tamil_chars)
        hindi_count = sum(1 for char in text if char in hindi_chars)
        
        if tamil_count > hindi_count and tamil_count > 5:
            return 'ta'
        elif hindi_count > tamil_count and hindi_count > 5:
            return 'hi'
        else:
            return 'en'
    
    def text_to_speech(self, text: str, lang: str = None) -> bool:
        """Convert text to speech with MALE VOICE ONLY"""
        if self.tts_engine is None:
            print("⚠️ TTS engine not available")
            return False
        
        try:
            print(f"🔊 Speaking in {lang.upper()} language with MALE voice...")
            
            # Use a queue to signal when speech is done
            speech_queue = queue.Queue()
            
            def speak():
                try:
                    self.tts_engine.say(text)
                    self.tts_engine.runAndWait()
                    speech_queue.put(True)
                except Exception as e:
                    print(f"⚠️ Speech error: {str(e)}")
                    speech_queue.put(False)
            
            # Run speech in a separate thread
            speech_thread = threading.Thread(target=speak)
            speech_thread.start()
            
            # Wait for speech to complete
            speech_thread.join(timeout=60)  # 60 second timeout
            
            return True
            
        except Exception as e:
            print(f"⚠️ Text-to-speech error: {str(e)}")
            return False
    
    def test_connection(self) -> bool:
        """Test if Groq API is reachable with valid key"""
        if not self.use_api:
            return False
            
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            test_payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": "Say OK"}],
                "max_tokens": 5,
                "temperature": 0
            }
            
            print(f"Testing Groq API with model: {self.model}")
            response = requests.post(
                self.api_url, 
                headers=headers, 
                json=test_payload, 
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ Groq API connection successful")
                return True
            else:
                print(f"❌ Groq API test failed: {response.status_code}")
                if response.status_code == 400:
                    print("Trying alternative model: mixtral-8x7b-32768")
                    test_payload["model"] = "mixtral-8x7b-32768"
                    response2 = requests.post(
                        self.api_url, 
                        headers=headers, 
                        json=test_payload, 
                        timeout=10
                    )
                    if response2.status_code == 200:
                        self.model = "mixtral-8x7b-32768"
                        print("✅ Success with mixtral model")
                        return True
                return False
                
        except Exception as e:
            print(f"❌ Cannot connect to Groq API: {str(e)}")
            return False
    
    def generate(self, user_text: str, lang: str, emotion: str, history: list, enable_voice: bool = True) -> dict:
        """Generate both chat response and recommendations in user's language"""
        
        # Auto-detect language if set to 'auto'
        if lang == 'auto':
            lang = self.detect_language_from_text(user_text)
            print(f"🌐 Auto-detected language: {lang.upper()}")
        
        # Force language based on user input
        if self.detect_language_from_text(user_text) == 'hi':
            lang = 'hi'
            print(f"🎯 Hindi detected - forcing Hindi mode")
        elif self.detect_language_from_text(user_text) == 'ta':
            lang = 'ta'
            print(f"🎯 Tamil detected - forcing Tamil mode")
        
        if not self.use_api:
            print("⚠️ No valid API key provided, using fallback mode")
            return self.get_fallback_response(emotion, lang, user_text, enable_voice)
        
        # Test connection first
        if not self.test_connection():
            print("⚠️ API connection failed, using fallback mode")
            return self.get_fallback_response(emotion, lang, user_text, enable_voice)
        
        # Language-specific system prompts
        language_prompts = {
            'ta': """நீங்கள் MindMate, ஒரு அன்பான, கவனிப்பு மனநல துணை.

முக்கியமான விதிகள்:
- நீங்கள் முற்றிலும் தமிழில் மட்டுமே பதிலளிக்க வேண்டும்
- ஒரு ஆங்கில வார்த்தை கூட பயன்படுத்த வேண்டாம்
- இயற்கையான, சூடான தமிழில் பேசுங்கள்

உங்கள் பதில்கள்:
1. உண்மையான பச்சாதாபத்துடன் தொடங்குங்கள்
2. அவர்களின் உணர்வை ஏற்றுக்கொள்ளுங்கள்
3. 3-6 வரிகளில், சூடான மற்றும் உரையாடல் நடையில் இருக்க வேண்டும்

முக்கியம்: தமிழ் மட்டுமே! ஆங்கிலம் கூடாது!""",
            
            'hi': """आप MindMate हैं, एक गर्मजोशी से भरपूर, देखभाल करने वाले मानसिक स्वास्थ्य साथी।

महत्वपूर्ण नियम:
- आपको केवल हिंदी में जवाब देना है
- एक भी अंग्रेजी शब्द का प्रयोग न करें
- प्राकृतिक, गर्म हिंदी में बोलें

आपके जवाब:
1. वास्तविक सहानुभूति के साथ शुरू करें
2. उनकी भावना को स्वीकार करें
3. 3-6 पंक्तियों में, गर्म और संवादी होना चाहिए

महत्वपूर्ण: केवल हिंदी! अंग्रेजी नहीं!""",
            
            'en': """You are MindMate, a warm, caring mental health companion.

Your responses should:
1. Start with genuine empathy
2. Validate their feeling
3. Be 3-6 lines, warm and conversational"""
        }
        
        system_prompt = language_prompts.get(lang, language_prompts['en'])
        
        # Build messages
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history
        for turn in history[-4:]:
            messages.append({"role": "user", "content": turn['u']})
            messages.append({"role": "assistant", "content": turn['b']})
        
        # Add current message with emotion context
        if lang == 'ta':
            current_message = f"""பயனரின் தற்போதைய உணர்வு: {emotion}
பயனரின் செய்தி: {user_text}

தயவுசெய்து உண்மையான அக்கறை மற்றும் பச்சாதாபத்துடன் தமிழில் மட்டும் பதிலளிக்கவும்:"""
        elif lang == 'hi':
            current_message = f"""उपयोगकर्ता की वर्तमान भावना: {emotion}
उपयोगकर्ता का संदेश: {user_text}

कृपया वास्तविक देखभाल और सहानुभूति के साथ केवल हिंदी में जवाब दें:"""
        else:
            current_message = f"The user is feeling: {emotion}\nUser's message: {user_text}\n\nPlease respond with genuine care and empathy in English:"
        
        messages.append({"role": "user", "content": current_message})
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.8,
            "max_tokens": 300
        }
        
        # Retry logic for chat response
        for attempt in range(self.max_retries):
            try:
                print(f"📡 Calling Groq API for {lang} chat response (attempt {attempt + 1}/{self.max_retries})...")
                response = requests.post(
                    self.api_url, 
                    headers=headers, 
                    json=payload, 
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    chat_response = data['choices'][0]['message']['content'].strip()
                    print(f"✅ {lang} chat response received successfully")
                    print(f"💬 Response: {chat_response[:100]}...")
                    
                    # Convert to speech with MALE VOICE ONLY
                    if enable_voice:
                        self.text_to_speech(chat_response, lang)
                    
                    # Generate recommendations in the same language
                    recommendations = self.generate_recommendations(emotion, user_text, lang)
                    
                    return {
                        "reply": chat_response,
                        "recommendations": recommendations,
                        "language": lang
                    }
                else:
                    print(f"⚠️ API Error {response.status_code}: {response.text[:200]}")
                    
                    if response.status_code in [401, 403]:
                        print("❌ Invalid API key")
                        self.use_api = False
                        return self.get_fallback_response(emotion, lang, user_text, enable_voice)
                    
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay)
                        continue
                    else:
                        return self.get_fallback_response(emotion, lang, user_text, enable_voice)
                    
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                else:
                    return self.get_fallback_response(emotion, lang, user_text, enable_voice)
        
        return self.get_fallback_response(emotion, lang, user_text, enable_voice)
    
    def generate_recommendations(self, emotion: str, user_text: str, lang: str) -> dict:
        """Generate personalized recommendations in user's language"""
        
        if not self.use_api:
            return self.get_fallback_recommendations(emotion, lang)
        
        # Language-specific recommendation prompts
        if lang == 'ta':
            rec_prompt = f"""பயனரின் உணர்வு: "{emotion}"
பயனரின் செய்தி: "{user_text[:500]}"

முக்கியமான விதிகள்:
- இசை பரிந்துரைகள் தமிழ் பாடல்கள் மட்டுமே
- உடற்பயிற்சிகள் மற்றும் குறிப்புகள் தமிழில் மட்டுமே

JSON வடிவத்தில் மட்டும் பதிலளிக்கவும்:

{{
    "music": [
        {{"name": "தமிழ் பாடல் பெயர்", "reason": "இது ஏன் உதவுகிறது", "mood": "மனநிலை", "language": "ta"}}
    ],
    "exercises": [
        {{"name": "உடற்பயிற்சி பெயர்", "duration": "கால அளவு", "instructions": "எப்படி செய்வது", "benefit": "நன்மை"}}
    ],
    "tips": [
        {{"tip": "ஆலோசனை", "why_it_helps": "ஏன் உதவுகிறது"}}
    ],
    "affirmation": "தனிப்பயனாக்கப்பட்ட உறுதிமொழி"
}}"""
            
        elif lang == 'hi':
            rec_prompt = f"""उपयोगकर्ता की भावना: "{emotion}"
उपयोगकर्ता का संदेश: "{user_text[:500]}"

महत्वपूर्ण नियम:
- संगीत अनुशंसाएँ केवल हिंदी गाने
- व्यायाम और सुझाव केवल हिंदी में

केवल JSON प्रारूप में जवाब दें:

{{
    "music": [
        {{"name": "हिंदी गाने का नाम", "reason": "यह क्यों मदद करता है", "mood": "मूड", "language": "hi"}}
    ],
    "exercises": [
        {{"name": "व्यायाम का नाम", "duration": "समय", "instructions": "कैसे करें", "benefit": "लाभ"}}
    ],
    "tips": [
        {{"tip": "सलाह", "why_it_helps": "क्यों मदद करता है"}}
    ],
    "affirmation": "व्यक्तिगत पुष्टि"
}}"""
            
        else:
            rec_prompt = f"""Based on the user's emotion "{emotion}" and their message: "{user_text[:500]}"

Generate personalized recommendations in JSON format:

{{
    "music": [
        {{"name": "song name", "reason": "why this helps", "mood": "matching mood", "language": "en"}}
    ],
    "exercises": [
        {{"name": "exercise name", "duration": "time", "instructions": "how to do it", "benefit": "what it helps with"}}
    ],
    "tips": [
        {{"tip": "practical advice", "why_it_helps": "explanation"}}
    ],
    "affirmation": "A warm, personalized affirmation"
}}

Return ONLY valid JSON, no other text."""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": rec_prompt}],
            "temperature": 0.7,
            "max_tokens": 800
        }
        
        for attempt in range(self.max_retries):
            try:
                print(f"📡 Calling Groq API for {lang} recommendations...")
                response = requests.post(
                    self.api_url, 
                    headers=headers, 
                    json=payload, 
                    timeout=30
                )
                
                if response.status_code == 200:
                    data = response.json()
                    rec_text = data['choices'][0]['message']['content'].strip()
                    rec_text = rec_text.replace('```json', '').replace('```', '').strip()
                    recommendations = json.loads(rec_text)
                    
                    if 'music' in recommendations:
                        for music in recommendations['music']:
                            music['language'] = lang
                    
                    return recommendations
                else:
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay)
                        continue
                    else:
                        return self.get_fallback_recommendations(emotion, lang)
                        
            except Exception as e:
                print(f"⚠️ Recommendation error: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                else:
                    return self.get_fallback_recommendations(emotion, lang)
        
        return self.get_fallback_recommendations(emotion, lang)
    
    def get_fallback_response(self, emotion: str, lang: str, user_text: str, enable_voice: bool = True) -> dict:
        """Fallback responses when API fails"""
        
        if lang == 'ta':
            caring_responses = {
                "sadness": ["💕 நீங்கள் வருத்தமாக உணர்கிறீர்கள் என்பதை நான் கேட்கிறேன். நீங்கள் தனியாக இல்லை. உங்கள் மனதில் என்ன இருக்கிறது? நான் கேட்க இங்கே இருக்கிறேன்."],
                "anxiety": ["💙 நீங்கள் பதட்டமாக உணர்கிறீர்கள். ஒரு கணம் மூச்சு விடுவோம். நீங்கள் பாதுகாப்பாக இருக்கிறீர்கள்."],
                "default": ["💚 உங்களைப் பகிர்ந்துகொண்டதற்கு நன்றி. நான் எப்படி உங்களை ஆதரிக்க முடியும்?"]
            }
        elif lang == 'hi':
            caring_responses = {
                "sadness": ["💕 मैं सुन सकता हूँ कि आप उदास हैं। आप अकेले नहीं हैं। क्या आप बता सकते हैं कि आपके मन में क्या है?"],
                "anxiety": ["💙 मैं महसूस कर सकता हूँ कि आप चिंतित हैं। एक सांस लें। आप सुरक्षित हैं।"],
                "default": ["💚 साझा करने के लिए धन्यवाद। मैं आपकी कैसे मदद कर सकता हूँ?"]
            }
        else:
            caring_responses = {
                "sadness": ["💕 I hear that you're feeling sad. You're not alone. Can you tell me what's on your mind?"],
                "anxiety": ["💙 I can feel your anxiety. Take a breath. You're safe right now."],
                "default": ["💚 Thank you for sharing. How can I support you?"]
            }
        
        response_text = caring_responses.get(emotion, caring_responses['default'])[0]
        
        if enable_voice:
            self.text_to_speech(response_text, lang)
        
        return {
            "reply": response_text,
            "recommendations": self.get_fallback_recommendations(emotion, lang),
            "language": lang
        }
    
    def get_fallback_recommendations(self, emotion: str, lang: str) -> dict:
        """Fallback recommendations with language-specific music"""
        
        # Hindi songs only
        if lang == 'hi':
            recommendations = {
                "sadness": {
                    "music": [
                        {"name": "Kal Ho Naa Ho - Har Ghadi", "reason": "आपकी भावनाओं को समझता है", "mood": "भावुक", "language": "hi"},
                        {"name": "Rock On - Tum Ho Toh", "reason": "आशा प्रदान करता है", "mood": "आशावान", "language": "hi"},
                        {"name": "Jab We Met - Ye Ishq Hai", "reason": "मन को शांत करता है", "mood": "शांत", "language": "hi"}
                    ],
                    "exercises": [
                        {"name": "हल्का स्ट्रेचिंग", "duration": "5 मिनट", "instructions": "धीरे-धीरे स्ट्रेच करें", "benefit": "तनाव दूर करता है"}
                    ],
                    "tips": [
                        {"tip": "किसी से बात करें", "why_it_helps": "अकेलापन कम करता है"}
                    ],
                    "affirmation": "आप मजबूत हैं, यह भावना बीत जाएगी। 💕"
                },
                "anxiety": {
                    "music": [
                        {"name": "Rang De Basanti - Luka Chuppi", "reason": "चिंता कम करता है", "mood": "शांत", "language": "hi"},
                        {"name": "Taare Zameen Par", "reason": "गहरा आराम देता है", "mood": "शांतिपूर्ण", "language": "hi"},
                        {"name": "Barfi - Phir Le Aaya Dil", "reason": "मन को शांत करता है", "mood": "प्रसन्न", "language": "hi"}
                    ],
                    "exercises": [
                        {"name": "4-7-8 सांस लेना", "duration": "2 मिनट", "instructions": "4 सेकंड लें, 7 रोकें, 8 छोड़ें", "benefit": "तंत्रिका तंत्र शांत करता है"}
                    ],
                    "tips": [
                        {"tip": "ठंडे पानी से चेहरा धोएं", "why_it_helps": "चिंता कम करता है"}
                    ],
                    "affirmation": "आप सुरक्षित हैं। मेरे साथ सांस लें। 💙"
                }
            }
        # Tamil songs only
        elif lang == 'ta':
            recommendations = {
                "sadness": {
                    "music": [
                        {"name": "Oru Naal - Na Muthukumar", "reason": "உணர்வுகளை ஏற்க உதவுகிறது", "mood": "உணர்ச்சி", "language": "ta"},
                        {"name": "Michael - AR Rahman", "reason": "நம்பிக்கை தருகிறது", "mood": "நம்பிக்கை", "language": "ta"},
                        {"name": "Ninaithale - Ilaiyaraaja", "reason": "மனதை அமைதிப்படுத்துகிறது", "mood": "அமைதி", "language": "ta"}
                    ],
                    "exercises": [
                        {"name": "மெதுவான நீட்சி", "duration": "5 நிமிடங்கள்", "instructions": "மெதுவாக நீட்டவும்", "benefit": "பதற்றத்தை விடுவிக்கிறது"}
                    ],
                    "tips": [
                        {"tip": "ஒருவரை தொடர்பு கொள்ளுங்கள்", "why_it_helps": "தனிமை குறைகிறது"}
                    ],
                    "affirmation": "நீங்கள் வலிமையானவர். இந்த உணர்வு கடந்து போகும். 💕"
                },
                "anxiety": {
                    "music": [
                        {"name": "Vennila - AR Rahman", "reason": "மன அழுத்தத்தை குறைக்கும்", "mood": "அமைதி", "language": "ta"},
                        {"name": "Thendrale - Ilaiyaraaja", "reason": "ஆழ்ந்த தளர்வு தருகிறது", "mood": "சாந்தம்", "language": "ta"},
                        {"name": "Mellisai - Harris Jayaraj", "reason": "மனதை அமைதிப்படுத்துகிறது", "mood": "அமைதி", "language": "ta"}
                    ],
                    "exercises": [
                        {"name": "4-7-8 மூச்சு", "duration": "2 நிமிடங்கள்", "instructions": "4 உள்ளிழு, 7 நிறுத்து, 8 வெளிவிடு", "benefit": "நரம்பு மண்டலத்தை அமைதிப்படுத்துகிறது"}
                    ],
                    "tips": [
                        {"tip": "குளிர்ந்த நீர் தெளிக்கவும்", "why_it_helps": "பதட்டத்தை குறைக்கிறது"}
                    ],
                    "affirmation": "நீங்கள் பாதுகாப்பாக இருக்கிறீர்கள். என்னுடன் மூச்சு விடுங்கள். 💙"
                }
            }
        else:
            recommendations = {
                "sadness": {
                    "music": [
                        {"name": "Someone Like You - Adele", "reason": "Validates feelings", "mood": "Emotional", "language": "en"},
                        {"name": "Fix You - Coldplay", "reason": "Offers hope", "mood": "Hopeful", "language": "en"}
                    ],
                    "exercises": [
                        {"name": "Gentle Stretching", "duration": "5 minutes", "instructions": "Stretch slowly", "benefit": "Releases tension"}
                    ],
                    "tips": [
                        {"tip": "Reach out to someone", "why_it_helps": "Reduces isolation"}
                    ],
                    "affirmation": "You are stronger than you know. 💕"
                },
                "anxiety": {
                    "music": [
                        {"name": "Weightless - Marconi Union", "reason": "Reduces anxiety", "mood": "Calming", "language": "en"},
                        {"name": "Clair de Lune - Debussy", "reason": "Calms the mind", "mood": "Serene", "language": "en"}
                    ],
                    "exercises": [
                        {"name": "4-7-8 Breathing", "duration": "2 minutes", "instructions": "Inhale 4, hold 7, exhale 8", "benefit": "Calms nervous system"}
                    ],
                    "tips": [
                        {"tip": "Splash cold water on face", "why_it_helps": "Triggers calm reflex"}
                    ],
                    "affirmation": "You are safe. Breathe with me. 💙"
                }
            }
        
        return recommendations.get(emotion, recommendations.get("sadness", {}))
    
    def cleanup(self):
        """Clean up TTS engine"""
        if self.tts_engine:
            self.tts_engine.stop()


# Example usage:
if __name__ == "__main__":
    # Install required package first:
    # pip install pyttsx3
    
    # Initialize with your API key
    chat = GroqChatModel("your-groq-api-key-here")
    
    print("\n" + "="*50)
    print("TESTING HINDI INPUT WITH MALE VOICE")
    print("="*50)
    
    response = chat.generate(
        user_text="आज मुझे बहुत उदास महसूस हो रहा है, कोई मेरी बात नहीं सुनता",
        lang='auto',
        emotion='sadness',
        history=[],
        enable_voice=True
    )
    
    print(f"\n🤖 AI Response ({response['language'].upper()}):")
    print(response['reply'])
    print(f"\n📝 Recommendations:")
    if 'music' in response['recommendations']:
        print(f"   🎵 Music: {[m['name'] for m in response['recommendations']['music']]}")
    
    # Cleanup
    chat.cleanup()