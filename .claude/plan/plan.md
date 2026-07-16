# Implementation Plan for Database Setup (Step 1)

## Context
This plan implements the database layer for the Spendly expense tracker application. The database layer is the foundation for all future features including authentication, user profiles, and expense tracking. Currently, the database/db.py file contains only placeholder comments, and no database functionality exists.

## Implementation Approach

### 1. Database Module (`database/db.py`)
Implement three core functions:

#### A. `get_db()`
- Create connection to `spendly.db` in project root
- Set `row_factory = sqlite3.Row` for dictionary-like access
- Enable foreign key constraints with `PRAGMA foreign_keys = ON`
- Return the connection object

#### B. `init_db()`
- Use `get_db()` to obtain connection
- Create `users` table with schema:
  - id INTEGER PRIMARY KEY AUTOINCREMENT
  - name TEXT NOT NULL
  - email TEXT UNIQUE NOT NULL
  - password_hash TEXT NOT NULL
  - created_at TEXT DEFAULT (datetime('now'))
- Create `expenses` table with schema:
  - id INTEGER PRIMARY KEY AUTOINCREMENT
  - user_id INTEGER NOT NULL (FOREIGN KEY referencing users.id)
  - amount REAL NOT NULL
  - category TEXT NOT NULL
  - date TEXT NOT NULL (YYYY-MM-DD format)
  - description TEXT NULLABLE
  - created_at TEXT DEFAULT (datetime('now'))
- Use `CREATE TABLE IF NOT EXISTS` for idempotent operation
- Commit changes and close connection

#### C. `seed_db()`
- Use `get_db()` to obtain connection
- Check if users table already has data (COUNT(*) > 0)
- If data exists, return early to prevent duplication
- Import `generate_password_hash` from `werkzeug.security`
- Create demo user:
  - name: "Demo User"
  - email: "demo@spendly.com"
  - password_hash: hash of "demo123"
- Insert 8 sample expenses covering all categories:
  - Food, Transport, Bills, Health, Entertainment, Shopping, Other (with one duplicated)
  - All linked to demo user via user_id
  - Dates spread across current month (YYYY-MM-DD format)
  - At least one expense per category
- Commit changes and close connection

### 2. Application Integration (`app.py`)
- Import `get_db`, `init_db`, `seed_db` from `database.db`
- Within application factory/context, call `init_db()` and `seed_db()` on startup
- Ensure database initialization happens before any routes are accessed

### 3. Implementation Details
- Use only `sqlite3` (standard library) and `werkzeug.security` (already installed)
- All SQL queries must use parameterized queries (`?` placeholders)
- No string formatting in SQL queries
- Dates must be stored in YYYY-MM-DD format
- Follow existing code style: snake_case, PEP 8 compliance

### 4. Verification
- Verify database file is created on app startup
- Confirm both tables exist with correct schema and constraints
- Verify demo user exists with hashed password
- Confirm 8 sample expenses exist across categories
- Ensure no duplicate seed data on repeated runs
- Confirm app starts without errors
- Validate foreign key enforcement works
- Ensure all queries use parameterized SQL

## Files to Modify
1. `database/db.py` - Implement all three functions
2. `app.py` - Add imports and startup calls

## Dependencies
- No new pip packages required
- Use existing Flask and Werkzeug installations