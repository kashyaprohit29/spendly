---
# Spec: Registration

## Overview
This feature implements the user registration functionality for Spendly. Users can create an account by providing their name, email, and password. Upon successful registration show a successful message, they are automatically logged in and redirected to their profile page. This step builds upon the completed database setup (Step 1) and enables user authentication for subsequent features like profile management and expense tracking.

## Depends on
- Step 1: Database setup (users table with proper schema, get_db/init_db/seed_db functions)

## Routes
- `GET /register` — Renders registration form (already implemented) — public
- `POST /register` — Processes registration form submission, creates user account, logs user in — public

## Database changes
No database changes required. The users table was already created in Step 1.

## Templates
- **Create:** None (register.html already exists)
- **Modify:** 
  - `register.html` - Add server-side validation error display and modify form to include CSRF protection considerations (though we'll keep it simple for now per project constraints)

## Files to change
- `app.py` - Add POST handler for /register route, implement user creation logic, add login functionality after registration
- `database/db.py` - Add `create_user()` function to handle user registration with password hashing
- `templates/register.html` - Modify to display server-side validation errors

## Files to create
- None

## New dependencies
- No new dependencies (uses existing flask and werkzeug)

## Rules for implementation
- No SQLAlchemy or ORMs - use parameterized queries only
- Passwords hashed with werkzeug.security.generate_password_hash
- Use CSS variables from existing style.css - never hardcode hex values
- All templates extend base.html (register.html already does)
- Use parameterized queries for all database operations
- Implement proper error handling (duplicate email, validation errors)
- After successful registration, automatically log in the user and redirect to profile page
- Validate input data (name, email format, password strength)

## Definition of done
- [ ] GET /register renders registration form (already implemented)
- [ ] POST /register processes form submission correctly
- [ ] New user is created in database with hashed password
- [ ] Duplicate email prevention works correctly
- [ ] After successful registration, user is logged in and redirected to profile page
- [ ] Validation errors are displayed in the form
- [ ] Password is hashed using werkzeug.security.generate_password_hash
- [ ] All database queries use parameterized statements
- [ ] No hardcoded hex values in CSS (use CSS variables)
- [ ] Registration form works with existing base.html template
- [ ] Manual testing confirms registration flow works end-to-end