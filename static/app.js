const chat = document.getElementById("chat");
const recsDiv = document.getElementById("recs");
const msg = document.getElementById("msg");
const sendBtn = document.getElementById("sendBtn");
const micBtn = document.getElementById("micBtn");
const clearBtn = document.getElementById("clearBtn");
const refreshRecs = document.getElementById("refreshRecs");
const currentEmotionEl = document.getElementById("currentEmotion");
const logoutBtn = document.getElementById("logoutBtn");
const userNameDisplay = document.getElementById("userNameDisplay");

let lastConversationId = null;
let mediaRecorder = null;
let chunks = [];

// Get username from session (passed from Flask)
const currentUsername = window.currentUser ? window.currentUser.username : "guest";
const currentFullName = window.currentUser ? window.currentUser.fullName : "Guest";

// Update username display
if (userNameDisplay) {
    userNameDisplay.textContent = currentFullName || currentUsername;
}

// Emotion emoji mapping
const emotionEmojis = {
    "anxiety": "😰",
    "stress": "😫",
    "sadness": "😔",
    "anger": "😠",
    "happiness": "😊",
    "neutral": "😐",
    "physical": "🤒",
    "crisis": "🚨"
};

// Daily tips array
const dailyTips = [
    "Take 3 deep breaths. You're doing great! 💚",
    "It's okay to not be okay. You're not alone.",
    "One small step at a time. Progress, not perfection.",
    "Be kind to yourself today. You deserve it.",
    "Take a 5-minute break. Stretch and breathe.",
    "Write down 3 things you're grateful for.",
    "Remember: This feeling will pass.",
    "You are stronger than you think! 💪"
];

function addMessage(text, who, emotion = null, language = null) {
    const messageDiv = document.createElement("div");
    messageDiv.className = `message ${who}`;
    
    const content = document.createElement("div");
    content.className = "message-content";
    content.textContent = text;
    
    if (emotion || language) {
        const meta = document.createElement("div");
        meta.className = "message-meta";
        if (emotion) meta.innerHTML += `${emotionEmojis[emotion] || "💬"} ${emotion}`;
        if (language) meta.innerHTML += ` • ${language.toUpperCase()}`;
        content.appendChild(meta);
    }
    
    messageDiv.appendChild(content);
    chat.appendChild(messageDiv);
    chat.scrollTop = chat.scrollHeight;
}

function showTypingIndicator() {
    const typingDiv = document.createElement("div");
    typingDiv.className = "message bot";
    typingDiv.id = "typingIndicator";
    typingDiv.innerHTML = `
        <div class="message-content">
            <div class="typing-indicator">
                <span></span><span></span><span></span>
            </div>
        </div>
    `;
    chat.appendChild(typingDiv);
    chat.scrollTop = chat.scrollHeight;
}

function hideTypingIndicator() {
    const indicator = document.getElementById("typingIndicator");
    if (indicator) indicator.remove();
}

function updateDailyTip() {
    const tipElement = document.getElementById("dailyTip");
    if (tipElement) {
        const randomTip = dailyTips[Math.floor(Math.random() * dailyTips.length)];
        tipElement.textContent = randomTip;
    }
}

// Update emotion display with color coding
function updateEmotionDisplay(emotion) {
    if (currentEmotionEl) {
        const emoji = emotionEmojis[emotion] || "💬";
        currentEmotionEl.innerHTML = `${emoji} ${emotion.toUpperCase()}`;
        currentEmotionEl.className = `emotion-badge ${emotion}`;
    }
}

function renderRecommendations(recs) {
    if (!recs) return;
    
    let html = '';
    
    // Display affirmation first
    if (recs.affirmation) {
        html += `
            <div class="recs-section affirmation-box">
                <h4>💖 A message for you</h4>
                <p style="background: linear-gradient(135deg, #667eea15, #764ba215); padding: 15px; border-radius: 12px; font-style: italic; font-size: 14px; line-height: 1.5;">
                    "${escapeHtml(recs.affirmation)}"
                </p>
            </div>
        `;
    }
    
    // Music Recommendations
    if (recs.music && recs.music.length > 0) {
        html += `
            <div class="recs-section">
                <h4>🎵 Music Therapy</h4>
                <ul class="recs-list">
                    ${recs.music.map(music => `
                        <li class="music-item" onclick="playMusic('${escapeHtml(music.name)}')">
                            <div class="music-info">
                                <div class="music-name">${escapeHtml(music.name)}</div>
                                <div class="music-reason">🎯 ${escapeHtml(music.reason)}</div>
                                <small>😌 Mood: ${escapeHtml(music.mood)}</small>
                            </div>
                            <button class="music-play-btn">▶️ Play</button>
                        </li>
                    `).join('')}
                </ul>
                <div class="feedback-buttons">
                    <button class="feedback-btn" onclick="sendFeedback('music', 1)">👍 Helpful</button>
                    <button class="feedback-btn" onclick="sendFeedback('music', -1)">👎 Not Helpful</button>
                </div>
            </div>
        `;
    }
    
    // Exercises
    if (recs.exercises && recs.exercises.length > 0) {
        html += `
            <div class="recs-section">
                <h4>🧘 Mindful Exercises</h4>
                <ul class="recs-list">
                    ${recs.exercises.map(ex => `
                        <li class="exercise-item">
                            <div>
                                <strong>${escapeHtml(ex.name)}</strong><br>
                                <small>⏱️ ${escapeHtml(ex.duration)}</small><br>
                                <small>📝 ${escapeHtml(ex.instructions)}</small><br>
                                <small>💪 Benefit: ${escapeHtml(ex.benefit)}</small>
                            </div>
                        </li>
                    `).join('')}
                </ul>
                <div class="feedback-buttons">
                    <button class="feedback-btn" onclick="sendFeedback('exercises', 1)">👍 Helpful</button>
                    <button class="feedback-btn" onclick="sendFeedback('exercises', -1)">👎 Not Helpful</button>
                </div>
            </div>
        `;
    }
    
    // Tips
    if (recs.tips && recs.tips.length > 0) {
        html += `
            <div class="recs-section">
                <h4>💡 Wellness Tips</h4>
                <ul class="recs-list">
                    ${recs.tips.map(tip => `
                        <li>
                            <strong>✨ ${escapeHtml(tip.tip)}</strong><br>
                            <small>💭 ${escapeHtml(tip.why_it_helps)}</small>
                        </li>
                    `).join('')}
                </ul>
                <div class="feedback-buttons">
                    <button class="feedback-btn" onclick="sendFeedback('tips', 1)">👍 Helpful</button>
                    <button class="feedback-btn" onclick="sendFeedback('tips', -1)">👎 Not Helpful</button>
                </div>
            </div>
        `;
    }
    
    recsDiv.innerHTML = html || "<p>✨ I'm generating personalized recommendations for you. Keep chatting! 💚</p>";
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function playMusic(songName) {
    const searchQuery = encodeURIComponent(songName + " official audio");
    window.open(`https://www.youtube.com/results?search_query=${searchQuery}`, '_blank');
}

async function sendFeedback(type, rating) {
    try {
        const response = await fetch("/api/feedback", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                conversation_id: lastConversationId,
                recommendation_type: type,
                rating: rating
            })
        });
        
        const data = await response.json();
        
        // Show temporary feedback
        const btn = event.target;
        const originalText = btn.textContent;
        if (rating === 1) {
            btn.textContent = "✅ Thanks!";
            btn.classList.add('liked');
        } else {
            btn.textContent = "📝 Noted";
            btn.classList.add('disliked');
        }
        
        setTimeout(() => {
            btn.textContent = originalText;
            btn.classList.remove('liked', 'disliked');
        }, 2000);
    } catch (error) {
        console.error("Feedback error:", error);
    }
}

async function sendText() {
    const text = msg.value.trim();
    if (!text) return;
    
    addMessage(text, "user");
    msg.value = "";
    showTypingIndicator();
    
    try {
        const res = await fetch("/api/chat", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                message: text
            })
        });
        
        const data = await res.json();
        hideTypingIndicator();
        
        if (data.error) {
            addMessage("Sorry, I encountered an error. Please try again.", "bot");
            return;
        }
        
        lastConversationId = data.conversation_id;
        addMessage(data.reply, "bot", data.emotion, data.language);
        
        // Update emotion display
        if (data.emotion) {
            updateEmotionDisplay(data.emotion);
        }
        
        // Speak the response
        speak(data.reply, data.language);
        
        // Render recommendations
        if (data.recommendations) {
            renderRecommendations(data.recommendations);
        }
    } catch (error) {
        hideTypingIndicator();
        addMessage("Network error. Please check your connection.", "bot");
        console.error("Chat error:", error);
    }
}

function speak(text, lang) {
    if (!window.speechSynthesis) return;
    
    try {
        // Cancel any ongoing speech
        window.speechSynthesis.cancel();
        
        const utterance = new SpeechSynthesisUtterance(text);
        
        // Set language for voice
        if (lang === "ta") utterance.lang = "ta-IN";
        else if (lang === "hi") utterance.lang = "hi-IN";
        else utterance.lang = "en-US";
        
        utterance.rate = 0.9;
        utterance.pitch = 1.0;
        
        // Try to select male voice
        const voices = window.speechSynthesis.getVoices();
        const maleVoice = voices.find(voice => 
            voice.name.includes('Google UK English Male') ||
            voice.name.includes('Microsoft David') ||
            (voice.name.includes('Male') && voice.lang.startsWith('en'))
        );
        
        if (maleVoice) utterance.voice = maleVoice;
        
        window.speechSynthesis.speak(utterance);
    } catch (error) {
        console.error("Speech error:", error);
    }
}

// Voice recording
micBtn.onclick = async () => {
    if (mediaRecorder && mediaRecorder.state === "recording") {
        mediaRecorder.stop();
        micBtn.classList.remove("recording");
        micBtn.textContent = "🎙️";
        return;
    }
    
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        chunks = [];
        
        mediaRecorder.ondataavailable = (e) => chunks.push(e.data);
        mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(chunks, { type: "audio/webm" });
            addMessage("🎤 Voice message sent...", "user");
            showTypingIndicator();
            
            const formData = new FormData();
            formData.append("audio", audioBlob);
            
            try {
                const res = await fetch("/api/voice", {
                    method: "POST",
                    body: formData
                });
                
                const data = await res.json();
                hideTypingIndicator();
                
                if (data.error) {
                    addMessage(`Voice recognition error: ${data.error}`, "bot");
                    return;
                }
                
                if (data.transcript) {
                    addMessage(`📝 Transcript: "${data.transcript}"`, "user");
                }
                addMessage(data.reply, "bot", data.emotion, data.language);
                
                if (data.emotion) {
                    updateEmotionDisplay(data.emotion);
                }
                
                speak(data.reply, data.language);
                if (data.recommendations) {
                    renderRecommendations(data.recommendations);
                }
            } catch (error) {
                hideTypingIndicator();
                addMessage("Voice processing error. Please try again.", "bot");
                console.error("Voice error:", error);
            }
            
            // Clean up
            stream.getTracks().forEach(track => track.stop());
        };
        
        mediaRecorder.start();
        micBtn.classList.add("recording");
        micBtn.textContent = "⏹️";
    } catch (error) {
        alert("Microphone access denied. Please allow microphone access.");
        console.error("Microphone error:", error);
    }
};

// Refresh recommendations
refreshRecs.onclick = async () => {
    refreshRecs.style.transform = 'rotate(180deg)';
    
    // Get last user message to regenerate recommendations
    const lastUserMsg = document.querySelector('.message.user .message-content');
    if (lastUserMsg) {
        const lastMessage = lastUserMsg.textContent.split('\n')[0];
        msg.value = lastMessage;
        await sendText();
        msg.value = '';
    }
    
    setTimeout(() => {
        refreshRecs.style.transform = 'rotate(0deg)';
    }, 300);
};

// Clear chat
clearBtn.onclick = () => {
    if (confirm('Are you sure you want to clear the chat history?')) {
        chat.innerHTML = "";
        recsDiv.innerHTML = "";
        lastConversationId = null;
        updateEmotionDisplay('neutral');
        addMessage("✨ Chat cleared! How are you feeling today? 💚", "bot");
    }
};

// Logout function
logoutBtn.onclick = () => {
    if (confirm('Are you sure you want to logout?')) {
        window.location.href = '/logout';
    }
};

// Send on Enter
msg.addEventListener("keypress", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendText();
    }
});

// Load chat history from server
async function loadChatHistory() {
    try {
        const response = await fetch('/api/history?limit=20');
        const data = await response.json();
        
        if (data.success && data.history.length > 0) {
            // Clear any existing messages
            chat.innerHTML = '';
            // Load history in reverse order (oldest first)
            data.history.reverse().forEach(conv => {
                addMessage(conv.user_message, 'user');
                addMessage(conv.bot_message, 'bot', conv.emotion, conv.language);
            });
        } else {
            // Welcome message
            addMessage("👋 Hello " + (currentFullName || currentUsername) + "! I'm your AI mental health assistant. I'm here to listen and support you. How are you feeling today? 💚", "bot");
        }
    } catch (error) {
        console.error('Error loading history:', error);
        addMessage("👋 Hello! I'm your AI mental health assistant. I'm here to listen and support you. How are you feeling today? 💚", "bot");
    }
}

// Load user preferences
async function loadUserPreferences() {
    try {
        const response = await fetch('/api/preferences');
        const data = await response.json();
        
        if (data.success && data.preferences) {
            // Apply preferences
            if (data.preferences.enable_voice === false) {
                // Voice disabled by default
                console.log('Voice responses disabled in preferences');
            }
        }
    } catch (error) {
        console.error('Error loading preferences:', error);
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    loadChatHistory();
    loadUserPreferences();
    updateDailyTip();
    
    // Update daily tip every 30 seconds
    setInterval(updateDailyTip, 30000);
});

// Load voices when available
window.speechSynthesis.onvoiceschanged = () => {
    window.speechSynthesis.getVoices();
};