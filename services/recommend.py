from typing import Dict, List

# Music recommendations based on emotion
MUSIC_RECOMMENDATIONS = {
    "anxiety": [
        {"name": "Weightless by Marconi Union", "type": "scientific", "link": "https://youtu.be/UfcAVejslrU"},
        {"name": "Meditation Music - Tibetan Bowls", "type": "meditation", "link": "https://youtu.be/9PZp0SfEYcY"},
        {"name": "Binaural Beats - Alpha Waves", "type": "focus", "link": "https://youtu.be/UdKKBqDET7k"},
        {"name": "Calm Piano Collection", "type": "relaxation", "link": "https://youtu.be/2wjJqTcJ2Qw"}
    ],
    "stress": [
        {"name": "Stress Relief - Nature Sounds", "type": "nature", "link": "https://youtu.be/eKFTSSKC9WA"},
        {"name": "LoFi Study Beats", "type": "chill", "link": "https://youtu.be/jfKfPfyJRdk"},
        {"name": "Classical Music for Stress", "type": "classical", "link": "https://youtu.be/X5h55wCOT1s"},
        {"name": "Ambient Relaxation", "type": "ambient", "link": "https://youtu.be/1tO5WpzMRDE"}
    ],
    "sadness": [
        {"name": "Upbeat Positive Energy", "type": "motivational", "link": "https://youtu.be/9g6LrOifN1c"},
        {"name": "Happy Morning Music", "type": "uplifting", "link": "https://youtu.be/WfVrFw2dYkI"},
        {"name": "Feel Good Vibes Playlist", "type": "pop", "link": "https://youtu.be/YRSeY-FJXmY"},
        {"name": "Gratitude Meditation Music", "type": "meditation", "link": "https://youtu.be/2j6rPQCUw98"}
    ],
    "anger": [
        {"name": "Calming Ocean Waves", "type": "nature", "link": "https://youtu.be/F0e6FjHnvtY"},
        {"name": "Deep Breathing Music", "type": "meditation", "link": "https://youtu.be/xUvR6I5Xh4A"},
        {"name": "Soothing Piano", "type": "relaxation", "link": "https://youtu.be/5qap5aO4i9A"},
        {"name": "Letting Go Meditation", "type": "guided", "link": "https://youtu.be/l4zwCj5Gjvs"}
    ],
    "happiness": [
        {"name": "Dance Energy Mix", "type": "energetic", "link": "https://youtu.be/GjGJHoVr5Dc"},
        {"name": "Celebration Playlist", "type": "party", "link": "https://youtu.be/K4DyBUG242c"},
        {"name": "Morning Motivation", "type": "inspirational", "link": "https://youtu.be/nkLX2CQgQDo"},
        {"name": "Feel Good 2024 Hits", "type": "pop", "link": "https://youtu.be/9PZp0SfEYcY"}
    ],
    "neutral": [
        {"name": "Focus Flow", "type": "productivity", "link": "https://youtu.be/5qap5aO4i9A"},
        {"name": "Peaceful Meditation", "type": "mindfulness", "link": "https://youtu.be/inpok4MKVLM"},
        {"name": "Ambient Study Music", "type": "study", "link": "https://youtu.be/jfKfPfyJRdk"},
        {"name": "Nature Relaxation", "type": "calm", "link": "https://youtu.be/eKFTSSKC9WA"}
    ]
}

# Exercise recommendations based on emotion
EXERCISE_RECOMMENDATIONS = {
    "anxiety": [
        {"name": "Deep Breathing (4-7-8 Method)", "duration": "3 minutes", "difficulty": "Easy"},
        {"name": "Progressive Muscle Relaxation", "duration": "10 minutes", "difficulty": "Easy"},
        {"name": "Gentle Yoga Stretches", "duration": "15 minutes", "difficulty": "Beginner"},
        {"name": "Mindful Walking", "duration": "10 minutes", "difficulty": "Easy"}
    ],
    "stress": [
        {"name": "Box Breathing Technique", "duration": "5 minutes", "difficulty": "Easy"},
        {"name": "Desk Stretches", "duration": "5 minutes", "difficulty": "Easy"},
        {"name": "Treadmill Walking", "duration": "20 minutes", "difficulty": "Moderate"},
        {"name": "Tai Chi Basic Moves", "duration": "15 minutes", "difficulty": "Beginner"}
    ],
    "sadness": [
        {"name": "Morning Sunlight Walk", "duration": "15 minutes", "difficulty": "Easy"},
        {"name": "Dance to Favorite Song", "duration": "5 minutes", "difficulty": "Fun"},
        {"name": "Beginner Yoga Flow", "duration": "20 minutes", "difficulty": "Beginner"},
        {"name": "Jumping Jacks (Endorphin Boost)", "duration": "2 minutes", "difficulty": "Moderate"}
    ],
    "anger": [
        {"name": "High-Intensity Interval Training", "duration": "10 minutes", "difficulty": "Intense"},
        {"name": "Punching Bag (Safe Outlet)", "duration": "5 minutes", "difficulty": "Intense"},
        {"name": "Running/Sprinting", "duration": "15 minutes", "difficulty": "Moderate"},
        {"name": "Cool Down Stretches", "duration": "10 minutes", "difficulty": "Easy"}
    ],
    "happiness": [
        {"name": "Celebration Dance", "duration": "5 minutes", "difficulty": "Fun"},
        {"name": "Outdoor Cycling", "duration": "30 minutes", "difficulty": "Moderate"},
        {"name": "Group Exercise Class", "duration": "45 minutes", "difficulty": "Any"},
        {"name": "Power Walk with Music", "duration": "20 minutes", "difficulty": "Easy"}
    ],
    "neutral": [
        {"name": "Daily Stretch Routine", "duration": "10 minutes", "difficulty": "Easy"},
        {"name": "Core Strengthening", "duration": "15 minutes", "difficulty": "Moderate"},
        {"name": "Balance Exercises", "duration": "10 minutes", "difficulty": "Beginner"},
        {"name": "Posture Correction", "duration": "5 minutes", "difficulty": "Easy"}
    ]
}

def get_music_recommendations(emotion: str) -> List[Dict]:
    return MUSIC_RECOMMENDATIONS.get(emotion, MUSIC_RECOMMENDATIONS["neutral"])

def get_exercise_recommendations(emotion: str) -> List[Dict]:
    return EXERCISE_RECOMMENDATIONS.get(emotion, EXERCISE_RECOMMENDATIONS["neutral"])

BASE_RECS: Dict[str, Dict[str, List[str]]] = {
    "anxiety": {
        "exercises": [
            "🧘‍♀️ 4-7-8 Breathing: Inhale 4 sec, hold 7 sec, exhale 8 sec - repeat 4 times",
            "🌿 5-4-3-2-1 Grounding: Name 5 things you see, 4 you touch, 3 you hear, 2 you smell, 1 you taste",
            "📝 Worry Journal: Write down your anxious thoughts for 5 minutes, then close the book",
            "🧊 Cold Water Reset: Splash cold water on your face or hold an ice cube",
            "🎯 Progressive Muscle Relaxation: Tense and relax each muscle group from toes to head"
        ],
        "tips": [
            "💧 Stay hydrated - dehydration can worsen anxiety",
            "☕ Reduce caffeine intake today",
            "📱 Take a 10-minute social media break",
            "🎯 Break tasks into smaller, manageable steps",
            "💭 Practice thought labeling: 'I notice I'm having anxious thoughts'"
        ]
    },
    "stress": {
        "exercises": [
            "📦 Box Breathing: Inhale 4-hold 4-exhale 4-hold 4",
            "🧘‍♀️ 2-Minute Meditation: Focus only on your breath",
            "🚶‍♀️ Walking Meditation: Walk slowly and notice each step",
            "💪 Shoulder Rolls: Roll shoulders backward 10 times slowly",
            "🗓️ Time Blocking: Plan your next 2 hours in 30-min blocks"
        ],
        "tips": [
            "🎯 Prioritize: Do the hardest task first for 25 minutes",
            "🚫 Learn to say 'no' to non-essential commitments",
            "🌙 Establish a consistent sleep schedule",
            "📵 Create 'no-phone' zones during work/study",
            "🎨 Schedule 15 minutes of hobby time today"
        ]
    },
    "sadness": {
        "exercises": [
            "🌞 Morning Light Exposure: Spend 10 minutes in sunlight",
            "📝 Gratitude List: Write 3 things you're grateful for",
            "🎵 Dance Break: Put on an uplifting song and move",
            "🤝 Reach Out: Send a text to one friend",
            "✨ Small Win: Complete one tiny task (make bed, shower)"
        ],
        "tips": [
            "🌟 Behavioral Activation: Do one activity you used to enjoy",
            "💬 Talk to someone you trust today",
            "🏃‍♀️ Exercise releases endorphins - try 10 minutes of movement",
            "🎯 Set one small, achievable goal for today",
            "📖 Read something inspiring for 5 minutes"
        ]
    },
    "anger": {
        "exercises": [
            "⏸️ 60-Second Pause: Step away before responding",
            "💪 Physical Release: 20 jumping jacks or push-ups",
            "📝 Write a Letter: Express anger, then tear it up",
            "🎧 Listen to Calm Music for 5 minutes",
            "🧊 Cold Water on Wrists: Helps cool down quickly"
        ],
        "tips": [
            "🗣️ Use 'I feel' statements instead of blaming",
            "⏰ Wait 24 hours before sending angry messages",
            "🧘‍♀️ Practice deep breathing when you feel triggered",
            "🎯 Identify the real need behind the anger",
            "🚶‍♀️ Take a 10-minute walk to cool down"
        ]
    },
    "happiness": {
        "exercises": [
            "📝 Savoring Journal: Write what went well today",
            "🤝 Share Joy: Tell someone about your good news",
            "🎯 Set a Fun Goal for tomorrow",
            "💃 Dance to Your Favorite Song",
            "🌟 Help Someone: Small act of kindness"
        ],
        "tips": [
            "🎨 Amplify: What made you happy? Do more of it!",
            "📸 Capture the moment with a photo",
            "💪 Use this energy for a productive task",
            "🌱 Plan another enjoyable activity this week",
            "🤗 Express appreciation to someone"
        ]
    },
    "neutral": {
        "exercises": [
            "🧘‍♀️ 2-Minute Mindful Breathing",
            "🚶‍♀️ 10-Minute Walk Outside",
            "📝 Quick Mood Check-in: Rate 1-10",
            "💧 Drink a Glass of Water Mindfully",
            "🎯 Set One Intention for Today"
        ],
        "tips": [
            "🌱 Build a small daily routine",
            "📊 Track your mood patterns",
            "💤 Prioritize sleep hygiene",
            "🥗 Eat a balanced meal",
            "🤝 Connect with someone briefly"
        ]
    },
    "physical": {
        "exercises": [
            "🧘 Gentle Stretching (if comfortable)",
            "💆‍♀️ Self-Massage: Neck and shoulders",
            "🛌 Rest with Deep Breathing",
            "💧 Hydrate Slowly",
            "🩹 Apply Heat/Cold as appropriate"
        ],
        "tips": [
            "🏥 Seek medical help if severe or persistent",
            "📝 Track symptoms: duration, intensity, triggers",
            "🛌 Get adequate rest",
            "🥣 Eat light, easily digestible food",
            "💊 Only take medications as prescribed"
        ]
    }
}

def personalize(recs: Dict[str, List[str]], user_preference: Dict) -> Dict:
    order = sorted(["exercises", "tips"], key=lambda k: -user_preference.get(k, 0))
    return {"order": order, **recs}

def build_recommendations(emotion: str, user_preference: Dict) -> Dict:
    key = emotion if emotion in BASE_RECS else "neutral"
    base = BASE_RECS.get(key, BASE_RECS["neutral"])
    return personalize(base, user_preference)