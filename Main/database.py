import sqlite3
from sqlite3 import Error

def init_db():
    """Initialize SQLite database"""
    conn = None
    try:
        conn = sqlite3.connect('pipeline_monitoring.db')
        cur = conn.cursor()
        
        # Create users table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                email TEXT
            )
        """)
        
        # Insert default users if empty
        cur.execute("SELECT COUNT(*) FROM users")
        if cur.fetchone()[0] == 0:
            default_users = [
                ("admin", "admin123", "admin", "admin@example.com"),
                ("engineer", "engineer123", "engineer", "engineer@example.com"),
                ("technician", "tech123", "technician", "tech@example.com"),
                ("manager", "manager123", "manager", "manager@example.com")
            ]
            cur.executemany(
                "INSERT INTO users (username, password, role, email) VALUES (?, ?, ?, ?)",
                default_users
            )
        
        conn.commit()
    except Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

def authenticate(username, password):
    """Authenticate user"""
    try:
        conn = sqlite3.connect('pipeline_monitoring.db')
        cur = conn.cursor()
        cur.execute(
            "SELECT role FROM users WHERE username = ? AND password = ?",
            (username, password)
        )
        result = cur.fetchone()
        return result[0] if result else None
    except Error as e:
        print(f"Authentication error: {e}")
        return None
    finally:
        if conn:
            conn.close()