---
# Spec: Login and Logout

## Overview
This feature implements user authentication login and logout functionality for the Spendly expense tracker. Users can securely log in with their email and password, and log out to end their session. This builds upon the existing user registration system to provide complete authentication flow.

## Dependencies
This feature depends on Step 2 (registration) being complete, as it requires the existing users table, password hashing infrastructure, and session management foundations established during registration.

## Routes
- `POST /login` — Process login form submission, validate credentials, establish user session — access level: public (allows unauthenticated access to log in)
- `GET /logout` — Clear user session and redirect to landing page — access level: logged-in (requires authenticated user)

## Database Changes
No database changes required. The existing users table schema (id, name, email, password_hash, created_at) is sufficient for login functionality.

## Templates
- **Create:** None
- **Modify:** 
  - `templates/login.html` — Already includes error handling for invalid credentials (no changes needed)

## Files to Change
- `app.py` — Add POST /login route and implement GET /logout route
- `database/db.py` — Add get_user_by_email function to retrieve user by email

## New Dependencies
No new dependencies required. Uses existing werkzeug.security for password hash checking (already imported in db.py).

## Implementation Rules
- No SQLAlchemy or ORMs — continue using raw SQLite parameterized queries
- Parameterised queries only — use ? placeholders for all SQL queries
- Passwords hashed with werkzeug — use check_password_hash() to verify passwords against stored hashes
- Use CSS variables — never hardcode hex values (rely on existing CSS in style.css)
- All templates extend base.html — login.html already extends base.html
- Session management — use Flask session to store user_id and user_name on login, clear session on logout
- Input validation — validate email and password inputs before processing
- Error handling — provide user-friendly error messages for invalid credentials (same message for security to prevent user enumeration)
- Redirect after login — redirect to landing page upon successful login (changed from profile to landing per updated requirements)
- Redirect after logout — redirect to landing page after logout

## Definition of Done
- User can successfully log in with valid email and password (demo@spendly.com/demo123)
- Invalid login attempts show appropriate error messages
- Upon successful login, user is redirected to landing page and session is established
- Logging out clears the session and redirects to landing page
- Protected routes (like /profile) require authentication (to be implemented in later steps)
- Password verification uses secure check (hash is not reversible)
- All database queries use parameterized statements
- Error messages are displayed in login template without exposing system details
- Session cookies are properly managed (set on login, cleared on logout)