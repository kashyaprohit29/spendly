from flask import Flask, render_template, request, redirect, url_for, session , flash, abort
from database.db import get_db, init_db, seed_db, create_user, get_user_by_email, check_password_hash
from database.queries import (
    get_user_by_id, get_summary_stats, get_recent_transactions, get_category_breakdown,
    get_expense_by_id, update_expense, delete_expense as delete_expense_row
)
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'dev-secret-key-change-in-production'  # In production, use environment variable

CATEGORIES = ["Food", "Transport", "Bills", "Health", "Entertainment", "Shopping", "Other"]

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

    # Get date filter parameters from query string
    date_from = request.args.get('date_from', '').strip()
    date_to = request.args.get('date_to', '').strip()

    # Validate date format (YYYY-MM-DD)
    def is_valid_date(date_str):
        try:
            if date_str:
                datetime.strptime(date_str, '%Y-%m-%d')
                return True
            return False
        except ValueError:
            return False

    # Validate dates
    valid_date_from = date_from if is_valid_date(date_from) else None
    valid_date_to = date_to if is_valid_date(date_to) else None

    # If only one date is provided, ignore both (require both or neither)
    if (valid_date_from and not valid_date_to) or (not valid_date_from and valid_date_to):
        valid_date_from = None
        valid_date_to = None
    # If both dates are provided but invalid range, ignore both
    elif valid_date_from and valid_date_to and valid_date_from > valid_date_to:
        flash("Start date must be before end date.", "warning")
        valid_date_from = None
        valid_date_to = None

    # Calculate preset date ranges for the filter UI
    today = datetime.now().date()

    # This month: first day of current month to today
    this_month_start = today.replace(day=1)

    # Last 3 months: first day of 3 months ago to today
    if today.month <= 3:
        three_months_month = today.month + 12 - 3
        three_months_year = today.year - 1
    else:
        three_months_month = today.month - 3
        three_months_year = today.year
    three_months_start = today.replace(year=three_months_year, month=three_months_month, day=1)

    # Last 6 months: first day of 6 months ago to today
    if today.month <= 6:
        six_months_month = today.month + 12 - 6
        six_months_year = today.year - 1
    else:
        six_months_month = today.month - 6
        six_months_year = today.year
    six_months_start = today.replace(year=six_months_year, month=six_months_month, day=1)

    # Get statistics from database with date filtering
    stats = get_summary_stats(user_id, valid_date_from, valid_date_to)

    # Get recent transactions from database with date filtering
    recent_transactions = get_recent_transactions(user_id, 10, valid_date_from, valid_date_to)

    # Get category breakdown from dictionary expected by template with date filtering
    category_totals = get_category_breakdown(user_id, valid_date_from, valid_date_to)

    return render_template("profile.html",
                         user=user,
                         stats=stats,
                         recent_transactions=recent_transactions,
                         category_totals=category_totals,
                         date_from=valid_date_from,
                         date_to=valid_date_to,
                         today=today,
                         this_month_start=this_month_start,
                         three_months_start=three_months_start,
                         six_months_start=six_months_start)


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    if not session.get("user_id"):
        return redirect(url_for("login"))

    expense = get_expense_by_id(id, session["user_id"])
    if not expense:
        abort(404)

    return render_template("edit_expense.html", expense=expense, categories=CATEGORIES)


@app.route("/expenses/<int:id>/edit", methods=["POST"])
def edit_expense_post(id):
    if not session.get("user_id"):
        return redirect(url_for("login"))

    expense = get_expense_by_id(id, session["user_id"])
    if not expense:
        abort(404)

    # Get form data
    amount_raw = request.form.get('amount', '').strip()
    category = request.form.get('category', '').strip()
    date = request.form.get('date', '').strip()
    description = request.form.get('description', '').strip()

    # Validate input
    errors = []

    amount = None
    if not amount_raw:
        errors.append("Amount is required")
    else:
        try:
            amount = float(amount_raw)
            if amount <= 0:
                errors.append("Amount must be greater than 0")
        except ValueError:
            errors.append("Amount must be a valid number")

    if not category:
        errors.append("Category is required")
    elif category not in CATEGORIES:
        errors.append("Please select a valid category")

    if not date:
        errors.append("Date is required")
    else:
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            errors.append("Please enter a valid date")

    if not description:
        description = None

    # If there are validation errors, show form again with submitted values
    if errors:
        submitted = {
            'id': expense['id'],
            'amount': amount_raw,
            'category': category,
            'date': date,
            'description': description,
        }
        return render_template("edit_expense.html", expense=submitted,
                               categories=CATEGORIES, errors=errors), 400

    update_expense(id, session["user_id"], amount, category, date, description)

    return redirect(url_for("profile"))


@app.route("/expenses/<int:id>/delete", methods=["POST"])
def delete_expense(id):
    if not session.get("user_id"):
        return redirect(url_for("login"))

    expense = get_expense_by_id(id, session["user_id"])
    if not expense:
        abort(404)

    delete_expense_row(id, session["user_id"])

    return redirect(url_for("profile"))


@app.route("/analytics")
def analytics():
    if not session.get("user_id"):
        return redirect(url_for("login"))
    return render_template("analytics.html")


@app.route("/Term")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


if __name__ == "__main__":
    app.run(debug=True, port=5001)