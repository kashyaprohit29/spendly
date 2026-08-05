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


@pytest.fixture
def auth_client(client):
    """Create a user, log in, and give them one expense."""
    user, err = create_user('Test User', 'test@example.com', 'testpass')
    assert err is None
    assert user is not None
    user_id = user['id']

    expense_id = _insert_expense(user_id)

    client.post('/login', data={'email': 'test@example.com', 'password': 'testpass'})
    return client, expense_id


@pytest.fixture
def other_user_expense(client):
    """Create a second user with their own expense, owned by neither auth_client user."""
    user, err = create_user('Other User', 'other@example.com', 'otherpass')
    assert err is None
    return _insert_expense(user['id'], amount=99.0, category='Bills', date='2026-02-01', description='Rent')


# -- Auth guard ------------------------------------------------------- #

def test_get_edit_requires_login(client):
    resp = client.get('/expenses/1/edit', follow_redirects=False)
    assert resp.status_code == 302
    assert '/login' in resp.location


def test_post_edit_requires_login(client):
    resp = client.post('/expenses/1/edit', data={}, follow_redirects=False)
    assert resp.status_code == 302
    assert '/login' in resp.location


# -- Ownership / not found --------------------------------------------- #

def test_get_edit_nonexistent_id_returns_404(auth_client):
    client, _ = auth_client
    resp = client.get('/expenses/999999/edit')
    assert resp.status_code == 404


def test_get_edit_other_users_expense_returns_404(auth_client, other_user_expense):
    client, _ = auth_client
    resp = client.get(f'/expenses/{other_user_expense}/edit')
    assert resp.status_code == 404


def test_post_edit_other_users_expense_returns_404(auth_client, other_user_expense):
    client, _ = auth_client
    resp = client.post(f'/expenses/{other_user_expense}/edit', data={
        'amount': '50.00', 'category': 'Food', 'date': '2026-03-01', 'description': 'Hack'
    })
    assert resp.status_code == 404
    # Other user's row must be untouched
    row = _get_expense_row(other_user_expense)
    assert row['amount'] == 99.0
    assert row['category'] == 'Bills'


# -- GET renders pre-filled form ---------------------------------------- #

def test_get_edit_own_expense_prefills_form(auth_client):
    client, expense_id = auth_client
    resp = client.get(f'/expenses/{expense_id}/edit')
    assert resp.status_code == 200
    assert b'25.0' in resp.data
    assert b'2026-01-15' in resp.data
    assert b'Lunch' in resp.data
    assert b'selected' in resp.data


# -- Successful update -------------------------------------------------- #

def test_post_edit_valid_data_updates_and_redirects(auth_client):
    client, expense_id = auth_client
    before = _get_expense_row(expense_id)

    resp = client.post(f'/expenses/{expense_id}/edit', data={
        'amount': '42.50',
        'category': 'Transport',
        'date': '2026-04-10',
        'description': 'Taxi',
    }, follow_redirects=False)

    assert resp.status_code == 302
    assert '/profile' in resp.location

    after = _get_expense_row(expense_id)
    assert after['amount'] == 42.50
    assert after['category'] == 'Transport'
    assert after['date'] == '2026-04-10'
    assert after['description'] == 'Taxi'

    # id, user_id, created_at must be unchanged
    assert after['id'] == before['id']
    assert after['user_id'] == before['user_id']
    assert after['created_at'] == before['created_at']


def test_post_edit_blank_description_saved_as_null(auth_client):
    client, expense_id = auth_client
    resp = client.post(f'/expenses/{expense_id}/edit', data={
        'amount': '10.00',
        'category': 'Other',
        'date': '2026-05-01',
        'description': '',
    }, follow_redirects=False)
    assert resp.status_code == 302

    after = _get_expense_row(expense_id)
    assert after['description'] is None


# -- Validation errors ---------------------------------------------------- #

def test_post_edit_missing_amount_rerenders_with_error(auth_client):
    client, expense_id = auth_client
    before = _get_expense_row(expense_id)

    resp = client.post(f'/expenses/{expense_id}/edit', data={
        'amount': '',
        'category': 'Food',
        'date': '2026-01-15',
        'description': 'Lunch',
    })
    assert resp.status_code == 400
    assert b'Amount is required' in resp.data
    assert _get_expense_row(expense_id) == before


def test_post_edit_zero_amount_rerenders_with_error(auth_client):
    client, expense_id = auth_client
    resp = client.post(f'/expenses/{expense_id}/edit', data={
        'amount': '0',
        'category': 'Food',
        'date': '2026-01-15',
        'description': 'Lunch',
    })
    assert resp.status_code == 400
    assert b'greater than 0' in resp.data


def test_post_edit_non_numeric_amount_rerenders_with_error(auth_client):
    client, expense_id = auth_client
    resp = client.post(f'/expenses/{expense_id}/edit', data={
        'amount': 'abc',
        'category': 'Food',
        'date': '2026-01-15',
        'description': 'Lunch',
    })
    assert resp.status_code == 400
    assert b'valid number' in resp.data


def test_post_edit_invalid_category_rerenders_with_error(auth_client):
    client, expense_id = auth_client
    resp = client.post(f'/expenses/{expense_id}/edit', data={
        'amount': '25.00',
        'category': 'NotACategory',
        'date': '2026-01-15',
        'description': 'Lunch',
    })
    assert resp.status_code == 400
    assert b'valid category' in resp.data


def test_post_edit_invalid_date_rerenders_with_error(auth_client):
    client, expense_id = auth_client
    resp = client.post(f'/expenses/{expense_id}/edit', data={
        'amount': '25.00',
        'category': 'Food',
        'date': 'not-a-date',
        'description': 'Lunch',
    })
    assert resp.status_code == 400
    assert b'valid date' in resp.data


def test_post_edit_invalid_data_does_not_write_to_db(auth_client):
    client, expense_id = auth_client
    before = _get_expense_row(expense_id)

    client.post(f'/expenses/{expense_id}/edit', data={
        'amount': '-5',
        'category': 'Food',
        'date': '2026-01-15',
        'description': 'Lunch',
    })

    after = _get_expense_row(expense_id)
    assert after == before
