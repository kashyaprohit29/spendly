from flask import Flask, render_template, redirect, url_for, flash, request, session
from database.db import get_db, init_db, seed_db

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'


@app.before_request
def require_login():
    # Allow access to login and register routes without login
    if request.endpoint in ['login', 'register']:
        return
    if 'user_id' not in session:
        flash('Please log in to access this page.', 'warning')
        return redirect(url_for('login'))


@app.route('/')
def landing():
    return render_template('landing.html')


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('landing'))


@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    return render_template('profile.html', user=user)


@app.route('/expenses/add')
def add_expense():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('add_expense.html')


@app.route('/expenses/<int:id>/edit')
def edit_expense(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    db = get_db()
    expense = db.execute('SELECT * FROM expenses WHERE id = ?', (id,)).fetchone()
    return render_template('edit_expense.html', expense=expense)


@app.route('/expenses/<int:id>/delete')
def delete_expense(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    db = get_db()
    db.execute('DELETE FROM expenses WHERE id = ?', (id,))
    db.commit()
    flash('Expense deleted successfully.', 'success')
    return redirect(url_for('index'))


@app.route('/Term')
def terms():
    return render_template('terms.html')


@app.route('/privacy')
def privacy():
    return render_template('privacy.html')


if __name__ == '__main__':
    with app.app_context():
        init_db()
        seed_db()
    app.run(debug=True, port=5001)