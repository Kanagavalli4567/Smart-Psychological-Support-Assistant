import sqlite3
import os

def view_all_users():
    """View all registered users in the database"""
    
    db_path = 'mindmate.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Database {db_path} not found!")
        return
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    print("\n" + "="*60)
    print("📊 MINDMATE DATABASE - USER LIST")
    print("="*60)
    
    # Get all users
    c.execute("""
        SELECT id, username, email, full_name, created_at, last_login 
        FROM users 
        ORDER BY id
    """)
    
    users = c.fetchall()
    
    if not users:
        print("\n❌ No users found in database!")
        print("Please register first at http://localhost:5000/register")
    else:
        print(f"\n✅ Found {len(users)} user(s) in database:\n")
        
        for user in users:
            print(f"📌 User ID: {user[0]}")
            print(f"   Username: {user[1]}")
            print(f"   Email: {user[2]}")
            print(f"   Full Name: {user[3] if user[3] else 'Not provided'}")
            print(f"   Registered: {user[4]}")
            print(f"   Last Login: {user[5] if user[5] else 'Never'}")
            print("-" * 40)
    
    # Get user preferences
    print("\n🎯 USER PREFERENCES:")
    print("="*60)
    
    c.execute("""
        SELECT u.username, up.preferred_language, up.enable_voice
        FROM user_preferences up
        JOIN users u ON u.id = up.user_id
    """)
    
    prefs = c.fetchall()
    
    if prefs:
        for pref in prefs:
            print(f"   {pref[0]}: Language={pref[1]}, Voice={pref[2]}")
    else:
        print("   No preferences found")
    
    # Get conversation count per user
    print("\n💬 CONVERSATION COUNTS:")
    print("="*60)
    
    c.execute("""
        SELECT u.username, COUNT(c.id) as chat_count
        FROM users u
        LEFT JOIN conversations c ON u.id = c.user_id
        GROUP BY u.id
    """)
    
    conv_counts = c.fetchall()
    
    for count in conv_counts:
        print(f"   {count[0]}: {count[1]} conversations")
    
    conn.close()
    
    print("\n" + "="*60)
    print("📝 To add a test user, run: python add_test_user.py")
    print("="*60)

def view_specific_user(username):
    """View details of a specific user"""
    
    db_path = 'mindmate.db'
    
    if not os.path.exists(db_path):
        print(f"❌ Database {db_path} not found!")
        return
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    c.execute("""
        SELECT id, username, email, full_name, created_at, last_login 
        FROM users 
        WHERE username = ?
    """, (username,))
    
    user = c.fetchone()
    
    if user:
        print(f"\n✅ User '{username}' found:")
        print(f"   ID: {user[0]}")
        print(f"   Username: {user[1]}")
        print(f"   Email: {user[2]}")
        print(f"   Full Name: {user[3] if user[3] else 'Not provided'}")
        print(f"   Registered: {user[4]}")
        print(f"   Last Login: {user[5] if user[5] else 'Never'}")
        
        # Get user's chat history
        c.execute("""
            SELECT COUNT(*), MIN(created_at), MAX(created_at)
            FROM conversations
            WHERE user_id = ?
        """, (user[0],))
        
        chat_stats = c.fetchone()
        if chat_stats[0] > 0:
            print(f"\n   Chat Statistics:")
            print(f"   - Total messages: {chat_stats[0]}")
            print(f"   - First chat: {chat_stats[1]}")
            print(f"   - Last chat: {chat_stats[2]}")
    else:
        print(f"\n❌ User '{username}' not found!")
    
    conn.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # View specific user
        view_specific_user(sys.argv[1])
    else:
        # View all users
        view_all_users()