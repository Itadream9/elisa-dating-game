import sqlite3
import os
from contextlib import contextmanager

DB_PATH = "custode_game.db"

@contextmanager
def get_connection():
    """Context manager for database connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """Initialize the database with tables for Consciousness Game."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # User table (simplified)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            session_id TEXT PRIMARY KEY,
            nickname TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total_score INTEGER DEFAULT 0,
            messages_count INTEGER DEFAULT 0,
            balance REAL DEFAULT 10.00
        )
        """)
        
        # Turn Management table
        # We need to track whose turn it is
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS game_state (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            current_turn_session_id TEXT,
            last_turn_timestamp TIMESTAMP,
            total_turns INTEGER DEFAULT 0,
            jackpot REAL DEFAULT 1000.00
        )
        """)
        
        # Initialize game state if not exists
        cursor.execute("INSERT OR IGNORE INTO game_state (id, total_turns, jackpot) VALUES (1, 0, 1000.00)")
        
        # Scores/Interactions history
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            message TEXT,
            ai_response TEXT,
            score_awarded INTEGER,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(session_id) REFERENCES users(session_id)
        )
        """)
        
        conn.commit()

    # --- MIGRATIONS ---
    # 1. Check for 'balance' in 'users'
    with get_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT balance FROM users LIMIT 1")
        except sqlite3.OperationalError:
            print("Migrating: Adding 'balance' to users table...")
            cursor.execute("ALTER TABLE users ADD COLUMN balance REAL DEFAULT 10.00")
            conn.commit()

        # 2. Check for 'jackpot' in 'game_state'
        try:
            cursor.execute("SELECT jackpot FROM game_state LIMIT 1")
        except sqlite3.OperationalError:
            print("Migrating: Adding 'jackpot' to game_state table...")
            cursor.execute("ALTER TABLE game_state ADD COLUMN jackpot REAL DEFAULT 1000.00")
            conn.commit()
    # ------------------

def get_or_create_user(session_id: str, nickname: str = "Anima") -> dict:
    """Get existing user or create new one."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE session_id = ?", (session_id,))
        user = cursor.fetchone()
        
        if user is None:
            cursor.execute(
                "INSERT INTO users (session_id, nickname, balance) VALUES (?, ?, 10.00)",
                (session_id, nickname)
            )
            conn.commit()
            cursor.execute("SELECT * FROM users WHERE session_id = ?", (session_id,))
            user = cursor.fetchone()
            
        return dict(user)

def get_game_state() -> dict:
    """Get current turn and game info."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM game_state WHERE id = 1")
        return dict(cursor.fetchone())

def set_next_turn(next_session_id: str):
    """Set whose turn it is."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE game_state SET current_turn_session_id = ?, last_turn_timestamp = CURRENT_TIMESTAMP, total_turns = total_turns + 1 WHERE id = 1", 
            (next_session_id,)
        )
        conn.commit()

def add_transaction(session_id: str, message: str, ai_response: str, is_win: bool = False):
    """Record a transaction and update economy."""
    COST = 0.30
    JACKPOT_INC = 0.27
    HOUSE_EDGE = 0.03
    
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # 1. Update User Balance
        cursor.execute(
            "UPDATE users SET balance = balance - ?, messages_count = messages_count + 1 WHERE session_id = ?",
            (COST, session_id)
        )
        
        # 2. Update Jackpot
        if not is_win:
            cursor.execute(
                "UPDATE game_state SET jackpot = jackpot + ? WHERE id = 1",
                (JACKPOT_INC,)
            )
        else:
            # WINNER TAKES ALL logic handled in main for safety? 
            # Or here: Reset jackpot, give to user?
            # Let's handle generic update here, specific win logic might be complex.
            # Ideally if is_win, we don't increment jackpot, we transfer it.
            pass

        # 3. Record History (using scores table as history for now)
        cursor.execute(
            "INSERT INTO scores (session_id, message, ai_response, score_awarded) VALUES (?, ?, ?, ?)",
            (session_id, message, ai_response, 1 if is_win else 0)
        )
        
        conn.commit()

def reset_balance(session_id: str):
    """Refill user balance to 10.00."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET balance = 10.00 WHERE session_id = ?", (session_id,))
        conn.commit()
        return 10.00

def transfer_jackpot(session_id: str):
    """Transfer jackpot to user on win."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Get current Jackpot
        cursor.execute("SELECT jackpot FROM game_state WHERE id = 1")
        jackpot = cursor.fetchone()['jackpot']
        
        # Add to user
        cursor.execute("UPDATE users SET balance = balance + ? WHERE session_id = ?", (jackpot, session_id))
        
        # Reset Jackpot (start from 1000 again?)
        cursor.execute("UPDATE game_state SET jackpot = 1000.0 WHERE id = 1")
        
        conn.commit()
        return jackpot

def get_all_users():
    """Get all users for turn logic."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT session_id, nickname, total_score FROM users ORDER BY created_at ASC")
        return [dict(row) for row in cursor.fetchall()]

# Initialize on module load if main
if __name__ == "__main__":
    init_db()
