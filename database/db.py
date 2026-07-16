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