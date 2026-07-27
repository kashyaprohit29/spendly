from flask import Flask, render_template, request, redirect, url_for, session , flash
from database.db import get_db, init_db, seed_db, create_user, get_user_by_email, check_password_hash
from database.queries import get_user_by_id, get_summary_stats, get_recent_transactions, get_category_breakdown

app = Flask(__name__)
app.secret_key = 'dev-secret-key-change-in-production'  # In production, use environment variable

# Initialize database on startup
with app.app_context():
    init_db()
    seed_db()


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #


@app.route("/")
def landing():
    # If user is logged in, redirect to profile
    if session.get("user_id"):
        return redirect(url_for("profile"))
    return render_template("landing.html")


@app.route("/register")
def register():
    return render_template("register.html")


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
    elif '@' not in email:
        errors.append("Please enter a valid email address")

    if not password:
        errors.append("Password is required")
    elif len(password) < 6:
        errors.append("Password must be at least 6 characters long")

    # If there are validation errors, show form again
    if errors:
        return render_template("register.html", errors=errors), 400

    # Attempt to create user
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
    flash("Account created successfully! Welcome to your profile.", "success")
    return redirect(url_for("profile"))

@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login_post():
    """Handle login form submission."""
    # Get form data
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')

    # Validate input
    if not email:
        return render_template("login.html", error="Email address is required"), 400

    if not password:
        return render_template("login.html", error="Password is required"), 400

    # Get user by email
    user = get_user_by_email(email)

    if user and check_password_hash(user['password_hash'], password):
        # Login successful - set session
        session['user_id'] = user['id']
        session['user_name'] = user['name']
        return redirect(url_for('profile'))
    else:
        # Login failed - show generic error to prevent user enumeration
        return render_template("login.html", error="Invalid email or password"), 400


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #


@app.route("/logout")
def logout():
    # Clear user session
    session.pop('user_id', None)
    session.pop('user_name', None)
    return redirect(url_for('landing'))


@app.route("/profile")
def profile():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    user_id = session["user_id"]

    # Get user data from database
    user = get_user_by_id(user_id)
    if not user:
        # If user not found, redirect to login
        session.clear()
        return redirect(url_for("login"))

    # Get statistics from database
    stats = get_summary_stats(user_id)

    # Get recent transactions from database
    recent_transactions = get_recent_transactions(user_id)

    # Get category breakdown from dictionary expected by template
    category_totals = get_category_breakdown(user_id)

    return render_template("profile.html",
                         user=user,
                         stats=stats,
                         recent_transactions=recent_transactions,
                         category_totals=category_totals)


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


@app.route("/Term")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


if __name__ == "__main__":
    app.run(debug=True, port=5001)