import os
import sys
import sqlite3
import json
import traceback
from datetime import datetime
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_cors import CORS
from functools import wraps
from config import Config
from services.lang import detect_lang
from services.emotion import detect_emotion
from services.safety import is_crisis, crisis_message, is_physical_symptom, physical_symptom_message
from services.groq_llm import GroqChatModel
from services.stt_whisper import transcribe_audio
import uuid
import hashlib

app = Flask(__name__)
app.config["SECRET_KEY"] = Config.SECRET_KEY
CORS(app)

# Initialize Groq model
print("Initializing Groq Chat Model...")
chat_model = GroqChatModel(Config.GROQ_API_KEY)

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    """Initialize database with complete schema including user authentication"""
    conn = sqlite3.connect(Config.DATABASE_PATH)
    c = conn.cursor()
    
    # Create users table with authentication
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  email TEXT UNIQUE NOT NULL,
                  password_hash TEXT NOT NULL,
                  full_name TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  last_login TIMESTAMP)''')
    
    # Create conversations table with all columns
    c.execute('''CREATE TABLE IF NOT EXISTS conversations
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER NOT NULL,
                  user_message TEXT NOT NULL,
                  bot_message TEXT NOT NULL,
                  language TEXT DEFAULT 'en',
                  emotion TEXT DEFAULT 'neutral',
                  recommendations TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES users(id))''')
    
    # Create feedback table
    c.execute('''CREATE TABLE IF NOT EXISTS feedback
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER NOT NULL,
                  convo_id INTEGER,
                  recommendation_type TEXT,
                  rating INTEGER DEFAULT 0,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES users(id))''')
    
    # Create user_preferences table
    c.execute('''CREATE TABLE IF NOT EXISTS user_preferences
                 (user_id INTEGER PRIMARY KEY,
                  preferred_language TEXT DEFAULT 'auto',
                  enable_voice BOOLEAN DEFAULT 1,
                  FOREIGN KEY (user_id) REFERENCES users(id))''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized with user authentication")

# Initialize database
try:
    init_db()
except Exception as e:
    print(f"⚠️ Database init warning: {e}")

def get_db():
    return sqlite3.connect(Config.DATABASE_PATH)

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def register_user(username, email, password, full_name=""):
    """Register a new user"""
    try:
        conn = get_db()
        c = conn.cursor()
        
        # Check if username exists
        c.execute("SELECT id FROM users WHERE username = ?", (username,))
        if c.fetchone():
            conn.close()
            return False, "Username already exists"
        
        # Check if email exists
        c.execute("SELECT id FROM users WHERE email = ?", (email,))
        if c.fetchone():
            conn.close()
            return False, "Email already exists"
        
        password_hash = hash_password(password)
        
        c.execute('''INSERT INTO users (username, email, password_hash, full_name)
                     VALUES (?, ?, ?, ?)''', (username, email, password_hash, full_name))
        
        user_id = c.lastrowid
        
        # Create default preferences
        c.execute('''INSERT INTO user_preferences (user_id, preferred_language, enable_voice)
                     VALUES (?, ?, ?)''', (user_id, 'auto', 1))
        
        conn.commit()
        conn.close()
        return True, user_id
    except Exception as e:
        return False, str(e)

def login_user(username, password):
    """Authenticate user login"""
    try:
        conn = get_db()
        c = conn.cursor()
        
        password_hash = hash_password(password)
        
        c.execute('''SELECT id, username, email, full_name 
                     FROM users 
                     WHERE username = ? AND password_hash = ?''', (username, password_hash))
        
        user = c.fetchone()
        
        if user:
            # Update last login time
            c.execute('''UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?''', (user[0],))
            conn.commit()
            conn.close()
            return True, {'id': user[0], 'username': user[1], 'email': user[2], 'full_name': user[3]}
        else:
            conn.close()
            return False, "Invalid username or password"
    except Exception as e:
        return False, str(e)

def fetch_history(user_id: int, limit: int = 6):
    conn = get_db()
    c = conn.cursor()
    try:
        c.execute("""SELECT user_message, bot_message
                     FROM conversations
                     WHERE user_id = ?
                     ORDER BY id DESC
                     LIMIT ?""", (user_id, limit))
        rows = c.fetchall()
        return [{"u": r[0], "b": r[1]} for r in reversed(rows)]
    except Exception as e:
        print(f"Error fetching history: {e}")
        return []
    finally:
        conn.close()

def get_user_preferences(user_id):
    """Get user preferences"""
    try:
        conn = get_db()
        c = conn.cursor()
        c.execute('''SELECT preferred_language, enable_voice 
                     FROM user_preferences 
                     WHERE user_id = ?''', (user_id,))
        prefs = c.fetchone()
        conn.close()
        if prefs:
            return {'preferred_language': prefs[0], 'enable_voice': bool(prefs[1])}
        return {'preferred_language': 'auto', 'enable_voice': True}
    except Exception as e:
        print(f"Error getting preferences: {e}")
        return {'preferred_language': 'auto', 'enable_voice': True}

# ==================== ROUTES ====================

@app.route("/")
def home():
    """Home page - redirect to login or index"""
    if 'user_id' in session:
        return redirect(url_for('index'))
    return redirect(url_for('login'))

@app.route("/index")
@login_required
def index():
    """Main chat interface - using index.html"""
    return render_template("index.html", 
                         username=session.get('username'),
                         full_name=session.get('full_name'))

@app.route("/register", methods=['GET', 'POST'])
def register():
    """User registration page"""
    if request.method == 'GET':
        return render_template("register.html")
    
    # POST request - handle registration
    try:
        data = request.get_json() if request.is_json else request.form
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        full_name = data.get('full_name', '').strip()
        
        # Validation
        if not username or not email or not password:
            return jsonify({"success": False, "error": "All fields are required"}), 400
        
        if len(password) < 6:
            return jsonify({"success": False, "error": "Password must be at least 6 characters"}), 400
        
        success, result = register_user(username, email, password, full_name)
        
        if success:
            return jsonify({"success": True, "message": "Registration successful! Please login."})
        else:
            return jsonify({"success": False, "error": result}), 400
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/login", methods=['GET', 'POST'])
def login():
    """User login page"""
    if request.method == 'GET':
        # If already logged in, redirect to index
        if 'user_id' in session:
            return redirect(url_for('index'))
        return render_template("login.html")
    
    # POST request - handle login
    try:
        data = request.get_json() if request.is_json else request.form
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({"success": False, "error": "Username and password required"}), 400
        
        success, result = login_user(username, password)
        
        if success:
            session['user_id'] = result['id']
            session['username'] = result['username']
            session['email'] = result['email']
            session['full_name'] = result['full_name']
            return jsonify({"success": True, "message": "Login successful!", "redirect": "/index"})
        else:
            return jsonify({"success": False, "error": result}), 401
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/logout")
def logout():
    """Logout user"""
    session.clear()
    return redirect(url_for('login'))

@app.route("/api/status", methods=["GET"])
def api_status():
    """Health check endpoint"""
    return jsonify({
        "status": "running",
        "groq_available": chat_model.use_api,
        "database": os.path.exists(Config.DATABASE_PATH),
        "authenticated": 'user_id' in session
    })

@app.route("/api/chat", methods=["POST"])
@login_required
def api_chat():
    """Main chat endpoint with authentication"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400
            
        user_text = (data.get("message") or "").strip()
        
        if not user_text:
            return jsonify({"error": "Empty message"}), 400
        
        user_id = session['user_id']
        prefs = get_user_preferences(user_id)
        
        print(f"📝 Chat request from {session['username']}: {user_text[:50]}...")
        
        lang = detect_lang(user_text)
        emotion = detect_emotion(user_text, lang=lang)
        
        # Override language if user has preference
        if prefs['preferred_language'] != 'auto':
            lang = prefs['preferred_language']
        
        # Crisis check
        if Config.ENABLE_CRISIS_CHECK and is_crisis(user_text):
            print("🚨 Crisis detected")
            bot = crisis_message(lang)
            recommendations = {
                "music": [],
                "exercises": [],
                "tips": [{"tip": crisis_message(lang), "why_it_helps": "Professional help is available"}],
                "affirmation": "You matter. Please reach out for help immediately."
            }
            
            # Store in database
            conn = get_db()
            c = conn.cursor()
            c.execute("""INSERT INTO conversations
                         (user_id, user_message, bot_message, language, emotion, recommendations)
                         VALUES (?, ?, ?, ?, ?, ?)""",
                      (user_id, user_text, bot, lang, "crisis", json.dumps(recommendations)))
            conn.commit()
            conn.close()
            
            return jsonify({
                "reply": bot,
                "language": lang,
                "emotion": "crisis",
                "recommendations": recommendations
            })
        
        # Get conversation history
        history = fetch_history(user_id, limit=6)
        
        # Generate response
        print("🤖 Generating response...")
        result = chat_model.generate(user_text, lang=lang, emotion=emotion, history=history, 
                                    enable_voice=prefs['enable_voice'])
        
        # Store conversation
        conn = get_db()
        c = conn.cursor()
        c.execute("""INSERT INTO conversations
                     (user_id, user_message, bot_message, language, emotion, recommendations)
                     VALUES (?, ?, ?, ?, ?, ?)""",
                  (user_id, user_text, result['reply'], lang, emotion, json.dumps(result['recommendations'])))
        convo_id = c.lastrowid
        conn.commit()
        conn.close()
        
        print("✅ Response sent successfully")
        
        return jsonify({
            "reply": result['reply'],
            "language": lang,
            "emotion": emotion,
            "conversation_id": convo_id,
            "recommendations": result['recommendations']
        })
        
    except Exception as e:
        print(f"❌ Error in api_chat: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            "error": "Internal server error",
            "details": str(e) if app.debug else "Please try again"
        }), 500

@app.route("/api/feedback", methods=["POST"])
@login_required
def api_feedback():
    try:
        data = request.get_json()
        convo_id = data.get("conversation_id")
        rec_type = data.get("recommendation_type")
        rating = int(data.get("rating", 0))
        
        user_id = session['user_id']
        
        conn = get_db()
        c = conn.cursor()
        c.execute("""INSERT INTO feedback (user_id, convo_id, recommendation_type, rating)
                     VALUES (?, ?, ?, ?)""",
                  (user_id, convo_id, rec_type, rating))
        conn.commit()
        conn.close()
        
        return jsonify({"status": "ok"})
    except Exception as e:
        print(f"Error in feedback: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/history", methods=["GET"])
@login_required
def api_history():
    """Get user's chat history"""
    try:
        user_id = session['user_id']
        limit = request.args.get('limit', 50, type=int)
        
        conn = get_db()
        c = conn.cursor()
        c.execute("""SELECT user_message, bot_message, emotion, language, created_at
                     FROM conversations
                     WHERE user_id = ?
                     ORDER BY created_at DESC
                     LIMIT ?""", (user_id, limit))
        
        history = []
        for row in c.fetchall():
            history.append({
                'user_message': row[0],
                'bot_message': row[1],
                'emotion': row[2],
                'language': row[3],
                'created_at': row[4]
            })
        
        conn.close()
        return jsonify({"success": True, "history": history})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/preferences", methods=["GET", "POST"])
@login_required
def api_preferences():
    """Get or update user preferences"""
    user_id = session['user_id']
    
    if request.method == "GET":
        prefs = get_user_preferences(user_id)
        return jsonify({"success": True, "preferences": prefs})
    
    # POST - update preferences
    try:
        data = request.get_json()
        conn = get_db()
        c = conn.cursor()
        
        if 'preferred_language' in data:
            c.execute("""UPDATE user_preferences 
                         SET preferred_language = ? 
                         WHERE user_id = ?""", 
                      (data['preferred_language'], user_id))
        
        if 'enable_voice' in data:
            c.execute("""UPDATE user_preferences 
                         SET enable_voice = ? 
                         WHERE user_id = ?""", 
                      (data['enable_voice'], user_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({"success": True, "message": "Preferences updated"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/voice", methods=["POST"])
@login_required
def api_voice():
    try:
        if "audio" not in request.files:
            return jsonify({"error": "No audio uploaded"}), 400
        
        audio_file = request.files["audio"]
        temp_dir = os.path.join(os.getcwd(), "temp_audio")
        os.makedirs(temp_dir, exist_ok=True)
        
        filename = f"{uuid.uuid4().hex}.webm"
        filepath = os.path.join(temp_dir, filename)
        audio_file.save(filepath)
        
        try:
            text_msg = transcribe_audio(filepath, model_size=Config.WHISPER_MODEL)
            print(f"🎤 Transcribed: {text_msg[:50]}...")
        except Exception as e:
            print(f"STT failed: {e}")
            return jsonify({"error": "STT failed", "details": str(e)}), 500
        finally:
            if os.path.exists(filepath):
                os.remove(filepath)
        
        # Process the transcribed text
        user_id = session['user_id']
        prefs = get_user_preferences(user_id)
        
        lang = detect_lang(text_msg)
        emotion = detect_emotion(text_msg, lang=lang)
        
        if prefs['preferred_language'] != 'auto':
            lang = prefs['preferred_language']
        
        # Crisis check
        if Config.ENABLE_CRISIS_CHECK and is_crisis(text_msg):
            bot = crisis_message(lang)
            recommendations = {
                "music": [], "exercises": [], 
                "tips": [{"tip": bot, "why_it_helps": "Professional help"}],
                "affirmation": "Please reach out for help immediately"
            }
            
            conn = get_db()
            c = conn.cursor()
            c.execute("""INSERT INTO conversations
                         (user_id, user_message, bot_message, language, emotion, recommendations)
                         VALUES (?, ?, ?, ?, ?, ?)""",
                      (user_id, text_msg, bot, lang, "crisis", json.dumps(recommendations)))
            conn.commit()
            conn.close()
            
            return jsonify({
                "transcript": text_msg,
                "reply": bot,
                "language": lang,
                "emotion": "crisis",
                "recommendations": recommendations
            })
        
        history = fetch_history(user_id, limit=6)
        result = chat_model.generate(text_msg, lang=lang, emotion=emotion, history=history,
                                    enable_voice=prefs['enable_voice'])
        
        conn = get_db()
        c = conn.cursor()
        c.execute("""INSERT INTO conversations
                     (user_id, user_message, bot_message, language, emotion, recommendations)
                     VALUES (?, ?, ?, ?, ?, ?)""",
                  (user_id, text_msg, result['reply'], lang, emotion, json.dumps(result['recommendations'])))
        convo_id = c.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            "transcript": text_msg,
            "reply": result['reply'],
            "language": lang,
            "emotion": emotion,
            "conversation_id": convo_id,
            "recommendations": result['recommendations']
        })
        
    except Exception as e:
        print(f"Error in voice endpoint: {e}")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n🚀 Starting MindMate server on http://localhost:{port}")
    print(f"📊 Status endpoint: http://localhost:{port}/api/status")
    print(f"💬 Chat endpoint: http://localhost:{port}/api/chat")
    print(f"🔐 Register: http://localhost:{port}/register")
    print(f"🔑 Login: http://localhost:{port}/login")
    print(f"💬 Main Chat: http://localhost:{port}/index")
    print("\nPress Ctrl+C to stop\n")
    
    app.run(debug=True, host="0.0.0.0", port=port)