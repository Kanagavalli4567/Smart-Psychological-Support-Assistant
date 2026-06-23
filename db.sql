CREATE DATABASE IF NOT EXISTS mental_chatbot
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE mental_chatbot;

CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(80) UNIQUE NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS conversations (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  user_message TEXT NOT NULL,
  bot_message TEXT NOT NULL,
  language VARCHAR(16) DEFAULT 'en',
  emotion VARCHAR(32) DEFAULT 'neutral',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS moods (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  mood_score INT DEFAULT 0,
  emotion VARCHAR(32) DEFAULT 'neutral',
  notes TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS feedback (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  convo_id INT,
  recommendation_type VARCHAR(32),
  rating INT DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (convo_id) REFERENCES conversations(id) ON DELETE SET NULL
);
-- Drop and recreate database for MySQL Workbench
DROP DATABASE IF EXISTS mental_chatbot;
CREATE DATABASE mental_chatbot
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE mental_chatbot;

-- Users table with more profile info
CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(80) UNIQUE NOT NULL,
  email VARCHAR(120),
  age INT,
  preferred_language VARCHAR(10) DEFAULT 'en',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Conversations table
CREATE TABLE IF NOT EXISTS conversations (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  user_message TEXT NOT NULL,
  bot_message TEXT NOT NULL,
  language VARCHAR(16) DEFAULT 'en',
  emotion VARCHAR(32) DEFAULT 'neutral',
  sentiment_score FLOAT DEFAULT 0,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  INDEX idx_user_created (user_id, created_at)
);

-- Mood tracking with more details
CREATE TABLE IF NOT EXISTS moods (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  mood_score INT DEFAULT 0 COMMENT '1-10 scale',
  emotion VARCHAR(32) DEFAULT 'neutral',
  energy_level INT DEFAULT 5 COMMENT '1-10 scale',
  sleep_hours FLOAT,
  stress_level INT DEFAULT 5 COMMENT '1-10 scale',
  notes TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  INDEX idx_user_mood_date (user_id, created_at)
);

-- Feedback for recommendations
CREATE TABLE IF NOT EXISTS feedback (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  convo_id INT,
  recommendation_type VARCHAR(32),
  rating INT DEFAULT 0 COMMENT '-1, 0, 1',
  helpful BOOLEAN DEFAULT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (convo_id) REFERENCES conversations(id) ON DELETE SET NULL,
  INDEX idx_user_feedback (user_id, recommendation_type)
);

-- User goals and achievements
CREATE TABLE IF NOT EXISTS goals (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  goal_text TEXT NOT NULL,
  goal_type VARCHAR(50) COMMENT 'daily, weekly, monthly',
  target_date DATE,
  completed BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  completed_at TIMESTAMP NULL,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Daily check-ins for consistency
CREATE TABLE IF NOT EXISTS daily_checkins (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  checkin_date DATE NOT NULL,
  mood_score INT,
  gratitude_text TEXT,
  affirmation_used VARCHAR(255),
  UNIQUE KEY unique_daily_checkin (user_id, checkin_date),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Resources library
CREATE TABLE IF NOT EXISTS resources (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  content TEXT,
  category VARCHAR(50),
  language VARCHAR(10),
  url VARCHAR(500),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample resources
INSERT INTO resources (title, content, category, language) VALUES
('Understanding Anxiety', 'Anxiety is your body''s natural response to stress...', 'education', 'en'),
('5 Minute Breathing Exercise', 'Take a deep breath in for 4 seconds...', 'exercise', 'en'),
('Coping with Stress', 'Here are 10 proven ways to manage daily stress...', 'tips', 'en'),
('மன அழுத்தத்தை குறைக்கும் வழிகள்', 'தினமும் 10 நிமிடம் தியானம் செய்யுங்கள்...', 'tips', 'ta');