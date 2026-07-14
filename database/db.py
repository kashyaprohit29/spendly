import sqlite3
import os
from werkzeug.security import generate_password_hash
from datetime import date, timedelta

def get_db():
    """Return a SQLite connection with row_factory and foreign keys enabled."""
    # Database file in project root
    db_path = os.path.join(os.path.dirname(__file__), '..', 'expense-tracker.db')
    # Ensure directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    # Enable foreign key constraints
    conn.execute('PRAGMA foreign_keys = ON')
    return conn


def init_db():
    """Create database tables if they don't exist."""
    db = get_db()
    # Schema matching the spec exactly
    schema = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        category TEXT NOT NULL,
        date TEXT NOT NULL,  -- YYYY-MM-DD format
        description TEXT,
        created_at TEXT DEFAULT (datetime('now')),
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    );
    """
    db.executescript(schema)
    db.commit()


def seed_db():
    """Insert sample data for development."""
    db = get_db()
    # Check if we already have data
    cursor = db.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] > 0:
        return  # Already seeded

    # Create demo user
    demo_hash = generate_password_hash("demo123")
    cursor = db.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Demo User", "demo@spendly.com", demo_hash)
    )
    user_id = cursor.lastrowid

    # Generate dates spread across current month
    today = date.today()
    # Create dates spread across the month (early, middle, late)
    dates = [
        today.replace(day=min(28, today.day)),  # Today or latest possible
        today.replace(day=max(1, today.day - 5)),  # 5 days ago or 1st
        today.replace(day=max(1, today.day - 10)),  # 10 days ago or 1st
        today.replace(day=max(1, today.day - 15)),  # 15 days ago or 1st
        today.replace(day=max(1, today.day - 20)),  # 20 days ago or 1st
        today.replace(day=max(1, today.day - 25)),  # 25 days ago or 1st
        today.replace(day=max(1, today.day - 30)),  # 30 days ago or 1st
    ]

    # Sample expenses data - 8 expenses covering all 7 categories
    # One category will have 2 expenses to make 8 total
    expenses = [
        # Food
        (user_id, 12.50, "Food", dates[0].isoformat(), "Groceries at FreshMart"),
        # Transport
        (user_id, 45.00, "Transport", dates[1].isoformat(), "Monthly bus pass"),
        # Bills
        (user_id, 85.00, "Bills", dates[2].isoformat(), "Electricity bill"),
        # Health
        (user_id, 30.00, "Health", dates[3].isoformat(), "Pharmacy purchase"),
        # Entertainment
        (user_id, 20.00, "Entertainment", dates[4].isoformat(), "Movie tickets"),
        # Shopping
        (user_id, 35.50, "Shopping", dates[5].isoformat(), "New shirt"),
        # Other
        (user_id, 22.00, "Other", dates[6].isoformat(), "Gift for friend"),
        # Second Food expense (to make 8 total)
        (user_id, 15.75, "Food", dates[1].isoformat(), "Lunch at restaurant"),
    ]

    db.executemany(
        "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
        expenses
    )
    db.commit()