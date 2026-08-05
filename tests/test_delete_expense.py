import uuid

import pytest
from app import app as flask_app
from database.db import get_db, init_db, create_user


@pytest.fixture
def app():
    flask_app.config.update({
        'TESTING': True,
        'DATABASE': ':memory:',
        'SECRET_KEY': 'test-secret',
        'WTF_CSRF_ENABLED': False,
    })
    with flask_app.app_context():
        init_db()
        yield flask_app


@pytest.fixture
def client(app):
    return flask_app.test_client()


def _insert_expense(user_id, amount=25.0, category='Food', date='2026-01-15', description='Lunch'):
    conn = get_db()
    try:
        cursor = conn.execute(
            'INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)',
            (user_id, amount, category, date, description)
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def _get_expense_row(expense_id):
    conn = get_db()
    try:
        row = conn.execute('SELECT * FROM expenses WHERE id = ?', (expense_id,)).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def _delete_user(user_id):
    conn = get_db()
    try:
        conn.execute('DELETE FROM expenses WHERE user_id = ?', (user_id,))
        conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
        conn.commit()
    finally:
        conn.close()


@pytest.fixture
def auth_client(client):
    """Create a user, log in, and give them one expense. Cleans up after itself
    since get_db() always points at the real spendly.db, not an isolated DB."""
    email = f'test-{uuid.uuid4().hex}@example.com'
    user, err = create_user('Test User', email, 'testpass')
    assert err is None
    assert user is not None
    user_id = user['id']

    expense_id = _insert_expense(user_id)

    client.post('/login', data={'email': email, 'password': 'testpass'})
    yield client, expense_id

    _delete_user(user_id)


@pytest.fixture
def other_user_expense(client):
    """Create a second user with their own expense, owned by neither auth_client user."""
    email = f'other-{uuid.uuid4().hex}@example.com'
    user, err = create_user('Other User', email, 'otherpass')
    assert err is None
    expense_id = _insert_expense(user['id'], amount=99.0, category='Bills', date='2026-02-01', description='Rent')

    yield expense_id

    _delete_user(user['id'])


# -- Auth guard ------------------------------------------------------- #

def test_post_delete_requires_login(client):
    email = f'noauth-{uuid.uuid4().hex}@example.com'
    user, err = create_user('No Auth User', email, 'testpass')
    assert err is None
    expense_id = _insert_expense(user['id'])

    resp = client.post(f'/expenses/{expense_id}/delete', follow_redirects=False)
    assert resp.status_code == 302
    assert '/login' in resp.location
    assert _get_expense_row(expense_id) is not None

    _delete_user(user['id'])


# -- Ownership / not found --------------------------------------------- #

def test_post_delete_other_users_expense_returns_404(auth_client, other_user_expense):
    client, _ = auth_client
    resp = client.post(f'/expenses/{other_user_expense}/delete')
    assert resp.status_code == 404

    row = _get_expense_row(other_user_expense)
    assert row is not None
    assert row['amount'] == 99.0
    assert row['category'] == 'Bills'


def test_post_delete_nonexistent_id_returns_404(auth_client):
    client, _ = auth_client
    resp = client.post('/expenses/999999/delete')
    assert resp.status_code == 404


# -- Successful delete -------------------------------------------------- #

def test_post_delete_own_expense_removes_and_redirects(auth_client):
    client, expense_id = auth_client
    assert _get_expense_row(expense_id) is not None

    resp = client.post(f'/expenses/{expense_id}/delete', follow_redirects=False)

    assert resp.status_code == 302
    assert '/profile' in resp.location
    assert _get_expense_row(expense_id) is None


# -- Method guard --------------------------------------------------------- #

def test_get_delete_not_allowed(auth_client):
    client, expense_id = auth_client
    resp = client.get(f'/expenses/{expense_id}/delete')
    assert resp.status_code == 405
    assert _get_expense_row(expense_id) is not None
