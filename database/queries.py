"""
Query helper functions for the profile page.
These functions encapsulate database queries for user profile data.
"""

import sqlite3
from datetime import datetime
from .db import get_db


def get_user_by_id(user_id):
    """
    Get user profile information by user ID.

    Args:
        user_id (int): The user's ID

    Returns:
        dict: User data with keys id, name, email, member_since
              or None if user not found
    """
    conn = get_db()
    try:
        user = conn.execute(
            'SELECT id, name, email, created_at FROM users WHERE id = ?',
            (user_id,)
        ).fetchone()

        if user:
            user_dict = dict(user)
            # Format created_at to "Month YYYY" (e.g., "January 2024")
            try:
                dt = datetime.strptime(user_dict['created_at'], '%Y-%m-%d %H:%M:%S')
                user_dict['member_since'] = dt.strftime('%B %Y')
            except ValueError:
                # Fallback if date format is different
                user_dict['member_since'] = user_dict['createdat'][:7]  # YYYY-MM
            return user_dict
        return None
    finally:
        conn.close()


def get_summary_stats(user_id, date_from=None, date_to=None):
    """
    Get summary statistics for a user's expenses.

    Args:
        user_id (int): The user's ID
        date_from (str, optional): Start date in YYYY-MM-DD format (inclusive)
        date_to (str, optional): End date in YYYY-MM-DD format (inclusive)

    Returns:
        dict: Statistics with keys total_spent, transaction_count, top_category
    """
    conn = get_db()
    try:
        # Build query with optional date filtering
        query = '''
            SELECT
                COALESCE(SUM(amount), 0) as total_spent,
                COUNT(*) as transaction_count
            FROM expenses
            WHERE user_id = ?
        '''
        params = [user_id]

        if date_from and date_to:
            query += ' AND date BETWEEN ? AND ?'
            params.extend([date_from, date_to])

        stats_row = conn.execute(query, params).fetchone()

        total_spent = float(stats_row['total_spent']) if stats_row['total_spent'] is not None else 0.0
        transaction_count = stats_row['transaction_count'] if stats_row['transaction_count'] is not None else 0

        # Get top category (category with highest total spending)
        if transaction_count > 0:
            category_query = '''
                SELECT category, SUM(amount) as total
                FROM expenses
                WHERE user_id = ?
            '''
            category_params = [user_id]

            if date_from and date_to:
                category_query += ' AND date BETWEEN ? AND ?'
                category_params.extend([date_from, date_to])

            category_query += '''
                GROUP BY category
                ORDER BY total DESC
                LIMIT 1
            '''

            category_row = conn.execute(category_query, category_params).fetchone()
            top_category = category_row['category'] if category_row else "—"
        else:
            top_category = "—"

        return {
            'total_spent': total_spent,
            'transaction_count': transaction_count,
            'top_category': top_category
        }
    finally:
        conn.close()


def get_recent_transactions(user_id, limit=10, date_from=None, date_to=None):
    """
    Get recent transactions for a user.

    Args:
        user_id (int): The user's ID
        limit (int): Maximum number of transactions to return
        date_from (str, optional): Start date in YYYY-MM-DD format (inclusive)
        date_to (str, optional): End date in YYYY-MM-DD format (inclusive)

    Returns:
        list: List of transaction dicts with keys id, date, description, category, amount
    """
    conn = get_db()
    try:
        # Build query with optional date filtering
        query = '''
            SELECT id, date, description, category, amount
            FROM expenses
            WHERE user_id = ?
        '''
        params = [user_id]

        if date_from and date_to:
            query += ' AND date BETWEEN ? AND ?'
            params.extend([date_from, date_to])

        query += '''
            ORDER BY date DESC, created_at DESC
            LIMIT ?
        '''
        params.append(limit)

        transactions = conn.execute(query, params).fetchall()

        return [dict(tx) for tx in transactions]
    finally:
        conn.close()


def get_expense_by_id(expense_id, user_id):
    """
    Get a single expense by ID, scoped to the owning user.

    Args:
        expense_id (int): The expense's ID
        user_id (int): The ID of the user who must own the expense

    Returns:
        dict: Expense data with keys id, user_id, amount, category, date, description
              or None if not found or not owned by this user
    """
    conn = get_db()
    try:
        expense = conn.execute(
            '''SELECT id, user_id, amount, category, date, description
               FROM expenses WHERE id = ? AND user_id = ?''',
            (expense_id, user_id)
        ).fetchone()

        return dict(expense) if expense else None
    finally:
        conn.close()


def update_expense(expense_id, user_id, amount, category, date, description):
    """
    Update an existing expense, scoped to the owning user.

    Args:
        expense_id (int): The expense's ID
        user_id (int): The ID of the user who must own the expense
        amount (float): The updated amount
        category (str): The updated category
        date (str): The updated date in YYYY-MM-DD format
        description (str or None): The updated description

    Returns:
        None
    """
    conn = get_db()
    try:
        conn.execute(
            '''UPDATE expenses
               SET amount = ?, category = ?, date = ?, description = ?
               WHERE id = ? AND user_id = ?''',
            (amount, category, date, description, expense_id, user_id)
        )
        conn.commit()
    finally:
        conn.close()


def delete_expense(expense_id, user_id):
    """
    Delete an expense, scoped to the owning user.

    Args:
        expense_id (int): The expense's ID
        user_id (int): The ID of the user who must own the expense

    Returns:
        None
    """
    conn = get_db()
    try:
        conn.execute(
            'DELETE FROM expenses WHERE id = ? AND user_id = ?',
            (expense_id, user_id)
        )
        conn.commit()
    finally:
        conn.close()


def get_category_breakdown(user_id, date_from=None, date_to=None):
    """
    Get spending breakdown by category for a user.

    Args:
        user_id (int): The user's ID
        date_from (str, optional): Start date in YYYY-MM-DD format (inclusive)
        date_to (str, optional): End date in YYYY-MM-DD format (inclusive)

    Returns:
        dict: Dictionary mapping category names to total amounts
    """
    conn = get_db()
    try:
        # Get total spent per category with optional date filtering
        query = '''
            SELECT category, SUM(amount) as total
            FROM expenses
            WHERE user_id = ?
        '''
        params = [user_id]

        if date_from and date_to:
            query += ' AND date BETWEEN ? AND ?'
            params.extend([date_from, date_to])

        query += '''
            GROUP BY category
        '''

        category_rows = conn.execute(query, params).fetchall()

        # Convert to dictionary format: {category: amount}
        category_totals = {}
        for row in category_rows:
            category = row['category']
            amount = float(row['total']) if row['total'] is not None else 0.0
            category_totals[category] = amount

        return category_totals
    finally:
        conn.close()