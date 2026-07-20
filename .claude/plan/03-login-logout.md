# Implementation Plan: Login and Logout

## Overview
This plan outlines the steps to implement user login and logout functionality for the Spendly expense tracker, building upon the existing user registration system.

## Steps

### 1. Update database/db.py
   - Add a new function `get_user_by_email(email)` that:
     - Uses `get_db()` to get a database connection
     - Executes a parameterized query: `SELECT id, name, email, password_hash, created_at FROM users WHERE email = ?`
     - Returns the user as a dictionary if found, or None if not found
     - Ensures the connection is closed in a finally block

### 2. Update app.py
   - Implement the POST /login route:
     - Define `@app.route("/login", methods=["POST"])`
     - Extract email and password from form data
     - Validate that both fields are present and non-empty
     - Call `get_user_by_email(email)` to retrieve user record
     - If user exists:
         - Use `werkzeug.security.check_password_hash(user['password_hash'], password)` to verify password
         - If password is correct:
             * Set `session['user_id'] = user['id']`
             * Set `session['user_name'] = user['name']`
             * Redirect to `url_for('profile')`
         - If password is incorrect:
             * Set error message: "Invalid email or password"
     - If user does not exist:
         * Set error message: "Invalid email or password" (same message for security)
     - If validation fails or authentication fails:
         * Render `login.html` with the error message and HTTP 400 status
   - Implement the GET /logout route:
     - Define `@app.route("/logout")`
     - Remove user data from session: `session.pop('user_id', None)` and `session.pop('user_name', None)`
     - Redirect to `url_for('landing')`

### 3. Update templates/login.html
   - The template already includes an error display block:
     ```html
     {% if error %}
     <div class="auth-error">{{ error }}</div>
     {% endif %}
     ```
   - No changes needed to the template structure, but ensure the view passes an `error` variable when authentication fails.

### 4. Verify Implementation
   - Ensure all database queries use parameterized queries (? placeholders)
   - Confirm password verification uses `check_password_hash` from werkzeug.security
   - Validate that session is properly set on login and cleared on logout
   - Check that redirects go to the correct pages (login → profile on success, logout → landing)
   - Confirm error messages are displayed without exposing system details

## Rules Adherence
- No SQLAlchemy or ORMs: Using raw SQLite with parameterized queries
- Parameterised queries only: All SQL queries use ? placeholders
- Passwords hashed with werkzeug: Using `check_password_hash` for verification
- Use CSS variables: Leveraging existing CSS classes in style.css (auth-error)
- All templates extend base.html: login.html already extends base.html
- Session management: Using Flask session to store user_id and user_name
- Input validation: Checking for empty email and password before processing
- Error handling: Providing user-friendly error messages for invalid credentials
- Security: Parameterized queries prevent SQL injection; generic error messages avoid user enumeration
- Redirect after login: Redirecting to profile page on successful login
- Redirect after logout: Redirecting to landing page after logout

## Files to Modify
- database/db.py: Add get_user_by_email function
- app.py: Add POST /login and GET /logout route implementations
- templates/login.html: No structural changes needed (already has error display)

## Dependencies
- No new dependencies required (uses existing werkzeug.security and Flask session)
