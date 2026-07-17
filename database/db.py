import sqlite3
from werkzeug.security import generate_password_hash
import os

def get_db():
    """Create and return a SQLite connection with row factory and foreign keys enabled."""
    # Get the absolute path to the database file in the project root
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'spendly.db')
    conn = sqlite3.connect(db_path)
    # Enable foreign key constraints
    conn.execute('PRAGMA foreign_keys = ON')
    # Return rows as dictionary-like objects
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database by creating tables if they don't exist."""
    conn = get_db()
    try:
        # Create users table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now'))
            )
        ''')

        # Create expenses table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                description TEXT,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        conn.commit()
    finally:
        conn.close()

def seed_db():
    """Seed the database with initial demo data if it doesn't already exist."""
    conn = get_db()
    try:
        # Check if we already have users
        cursor = conn.execute('SELECT COUNT(*) FROM users')
        user_count = cursor.fetchone()[0]

        # If we already have users, don't seed again
        if user_count > 0:
            return

        # Create demo user
        demo_password_hash = generate_password_hash('demo123')
        cursor = conn.execute(
            'INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)',
            ('Demo User', 'demo@spendly.com', demo_password_hash)
        )
        user_id = cursor.lastrowid

        # Insert 8 sample expenses covering all categories
        expenses_data = [
            # Food (2 entries)
            (user_id, 12.5, 'Food', '2026-07-01', 'Lunch at cafe'),
            (user_id, 25.0, 'Food', '2026-07-05', 'Groceries'),

            # Transport
            (user_id, 15.0, 'Transport', '2026-07-02', 'Gas refill'),

            # Bills
            (user_id, 75.0, 'Bills', '2026-07-03', 'Electricity bill'),

            # Health
            (user_id, 20.0, 'Health', '2026-07-04', 'Pharmacy'),

            # Entertainment
            (user_id, 30.0, 'Entertainment', '2026-07-06', 'Movie tickets'),

            # Shopping
            (user_id, 45.0, 'Shopping', '2026-07-07', 'New clothes'),

            # Other
            (user_id, 10.0, 'Other', '2026-07-08', 'Gift for friend')
        ]

        conn.executemany(
            'INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)',
            expenses_data
        )

        conn.commit()
    finally:
        conn.close()


def create_user(name, email, password):
    """Create a new user with the given credentials."""
    conn = get_db()
    try:
        # Validate input
        if not name or not name.strip():
            return None, "Name is required"

        if not email or not email.strip():
            return None, "Email is required"

        if not password:
            return None, "Password is required"

        if len(password) < 6:
            return None, "Password must be at least 6 characters long"

        # Check if email already exists
        existing = conn.execute(
            'SELECT id FROM users WHERE email = ?', (email.strip(),)
        ).fetchone()

        if existing:
            return None, "Email already registered"

        # Hash the password
        password_hash = generate_password_hash(password)

        # Insert new user
        cursor = conn.execute(
            '''INSERT INTO users (name, email, password_hash)
               VALUES (?, ?, ?)''',
            (name.strip(), email.strip(), password_hash)
        )
        conn.commit()

        # Get the newly created user
        user_id = cursor.lastrowid
        user = conn.execute(
            'SELECT id, name, email, created_at FROM users WHERE id = ?',
            (user_id,)
        ).fetchone()

        return dict(user), None
    except Exception as e:
        return None, str(e)
    finally:
        conn.close()