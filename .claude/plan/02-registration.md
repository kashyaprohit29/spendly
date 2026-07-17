# Implementation Plan: Registration Feature (Step 2)

## Overview
This plan outlines the implementation of user registration functionality for Spendly, building upon the completed database setup (Step 1). The implementation will add POST /register route handling, user creation logic, and automatic login after registration.

## Prerequisites
- Step 1 (Database setup) is complete and functional
- Current branch: feature/registration
- Working directory is clean

## Implementation Steps

### 1. Update Database Helper Functions
**File**: `database/db.py`
**Task**: Add `create_user()` function to handle user registration with proper validation and error handling
- Create function that takes name, email, password
- Hash password using werkzeug.security.generate_password_hash
- Insert new user into users table using parameterized query
- Handle duplicate email constraint violations
- Return user data or appropriate error

### 2. Implement Registration Route Handler
**File**: `app.py`
**Task**: Add POST /register route to process form submission
- Import necessary modules (request, redirect, url_for, session if needed)
- Add @app.route("/register", methods=["POST"]) function
- Extract form data (name, email, password)
- Validate input (non-empty fields, email format, password length)
- Call create_user() function from db.py
- Handle success case: log in user, redirect to profile page
- Handle error case: display validation errors in form
- Ensure all database operations use parameterized queries

### 3. Enhance Registration Template
**File**: `templates/register.html`
**Task**: Modify to display server-side validation errors
- Add conditional display for error messages (similar to existing error handling)
- Ensure error messages are styled appropriately using existing CSS classes
- Maintain existing form structure and styling
- Keep all existing HTML structure and classes intact

### 4. Implement User Session Management
**File**: `app.py` (potentially)
**Task**: Add login functionality after successful registration
- Set user session data upon successful registration
- Implement session management for tracking logged-in users
- Ensure session data includes user ID and other relevant information
- Redirect to profile page after login

### 5. Test Implementation
**Task**: Verify all functionality works correctly
- Test registration with valid data
- Test registration with duplicate email
- Test registration with invalid/missing data
- Verify password is properly hashed in database
- Verify automatic login and redirect to profile
- Verify error messages display correctly
- Test that existing functionality remains unaffected

## Detailed Implementation Notes

### Database Changes (database/db.py)
Add the following function:
```python
def create_user(name, email, password):
    """Create a new user with the given credentials."""
    conn = get_db()
    try:
        # Check if email already exists
        existing = conn.execute(
            'SELECT id FROM users WHERE email = ?', (email,)
        ).fetchone()
        
        if existing:
            return None, "Email already registered"
        
        # Hash the password
        password_hash = generate_password_hash(password)
        
        # Insert new user
        cursor = conn.execute(
            '''INSERT INTO users (name, email, password_hash) 
               VALUES (?, ?, ?)''',
            (name, email, password_hash)
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
```

### Route Handler (app.py)
Add the POST route:
```python
@app.route("/register", methods=["POST"])
def register_post():
    """Handle registration form submission."""
    # Get form data
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')
    
    # Validate input
    errors = []
    
    if not name:
        errors.append("Name is required")
    
    if not email:
        errors.append("Email is required")
    elif '@' not in email:  # Basic email validation
        errors.append("Please enter a valid email address")
    
    if not password:
        errors.append("Password is required")
    elif len(password) < 6:
        errors.append("Password must be at least 6 characters long")
    
    # If there are validation errors, show form again
    if errors:
        return render_template("register.html", errors=errors), 400
    
    # Attempt to create user
    from database.db import create_user
    user, error = create_user(name, email, password)
    
    if error:
        if "Email already registered" in error:
            errors.append("An account with this email already exists")
        else:
            errors.append("Registration failed. Please try again.")
        return render_template("register.html", errors=errors), 400
    
    # Log in the user (set session)
    session['user_id'] = user['id']
    session['user_name'] = user['name']
    
    # Redirect to profile page
    return redirect(url_for('profile'))
```

### Template Updates (templates/register.html)
Add error display section:
```html
{% if errors %}
<div class="alert errors">
    {% for error in errors %}
    <p>{{ error }}</p>
    {% endfor %}
</div>
{% endif %}
```

Place this above the form in the auth-card section.

## Dependencies
- No new dependencies required
- Uses existing Flask and Werkzeug packages
- Uses existing session management (will need to import session from flask)

## Verification Checklist
- [ ] Registration form loads correctly (GET /register)
- [ ] Form submission works with valid data (POST /register)
- [ ] New user created in database with hashed password
- [ ] Duplicate email prevented with appropriate error message
- [ ] User automatically logged in after registration
- [ ] Redirected to profile page after successful registration
- [ ] Validation errors displayed for missing/invalid data
- [ ] Password properly hashed using werkzeug
- [ ] All database queries use parameterized statements
- [ ] No hardcoded CSS values (uses existing CSS variables)
- [ ] Template extends base.html correctly
- [ ] Existing routes and functionality remain unaffected

## Estimated Time
- Database function implementation: 30 minutes
- Route handler implementation: 45 minutes  
- Template updates: 15 minutes
- Testing and verification: 30 minutes
- Total: ~2 hours

## Risks and Mitigations
- **Risk**: Password hashing not working correctly
  **Mitigation**: Test with known values and verify hash format
  
- **Risk**: Session management not properly implemented
  **Mitigation**: Ensure session is imported and used correctly
  
- **Risk**: Database connection issues
  **Mitigation**: Use existing get_db() function which is proven to work
  
- **Risk**: Validation gaps
  **Mitigation**: Implement comprehensive validation before database operations

## Completion Criteria
All items in the Definition of Done from the specification must be verified:
- GET /register renders registration form
- POST /register processes form submission correctly
- New user created with hashed password
- Duplicate email prevention works
- User automatically logged in and redirected to profile
- Validation errors displayed in form
- All database queries use parameterized statements
- No hardcoded hex values in CSS
- Registration form works with existing base.html template
- Manual testing confirms end-to-end functionality