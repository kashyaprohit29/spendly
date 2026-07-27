# Implementation Plan: Backend Route for Profile Page

## Context
This step replaces hardcoded data in the `/profile` route with live database queries to display real user data. Currently, the profile page shows static data matching the seed database. This implementation will make the profile page dynamic, showing each user's actual expenses, statistics, and profile information.

## Implementation Approach
Based on codebase analysis, I will:
1. Create a new `database/queries.py` module for pure query functions
2. Implement four query helper functions following existing patterns in `database/db.py`
3. Modify the `/profile` route in `app.py` to use these query functions
4. Update `templates/profile.html` to display Indian Rupee (₹) symbol instead of $
5. Handle edge cases like users with no expenses

## Files to Modify/Create
1. **Create**: `database/queries.py` - New module for query helper functions
2. **Modify**: `app.py` - Update `/profile` route to use database queries
3. **Modify**: `templates/profile.html` - Change currency symbol from $ to ₹

## Implementation Details

### 1. Create database/queries.py
This module will contain pure query functions with no Flask dependencies:
- `get_user_by_id(user_id)`: Get user profile data with formatted member_since
- `get_summary_stats(user_id)`: Calculate total spent, transaction count, top category
- `get_recent_transactions(user_id, limit=10)`: Get recent expenses ordered by date DESC
- `get_category_breakdown(user_id)`: Get category totals with percentages summing to 100

Each function will:
- Use `get_db()` for connection
- Use parameterized queries with `?` placeholders
- Handle connection properly with try/finally
- Return data in format expected by existing template
- Handle edge cases gracefully (empty results)

### 2. Update app.py profile route
Replace hardcoded data (lines 127-160) with calls to query functions:
- Keep authentication check: `if not session.get("user_id"): return redirect(url_for("login"))`
- Replace user dict with: `user = get_user_by_id(session["user_id"])`
- Replace stats dict with: `stats = get_summary_stats(session["user_id"])`
- Replace transactions list with: `recent_transactions = get_recent_transactions(session["user_id"])`
- Replace category_totals dict with: `category_totals = get_category_breakdown(session["user_id"])`
- Handle potential None returns gracefully

### 3. Update templates/profile.html
Change currency symbol from $ to ₹:
- Update total spent: `₹{{ "%.2f"|format(stats.total_spent) }}`
- Update transaction amounts: `₹{{ "%.2f"|format(tx.amount) }}`
- Update category amounts: `₹{{ "%.2f"|format(total) }}`

## Implementation Order
1. Create database/queries.py with all four functions
2. Update templates/profile.html for currency symbol
3. Modify app.py profile route to use query functions
4. Verify implementation follows all rules from CLAUDE.md

## Rules Compliance
- ✅ No SQLAlchemy/ORM - using raw sqlite3 via get_db()
- ✅ Parameterized queries only - no string formatting in SQL
- ✅ Foreign keys PRAGMA enabled via get_db()
- ✅ CSS variables only - no hex values in template (already compliant)
- ✅ All templates extend base.html (already compliant)
- ✅ Authentication guard maintained
- ✅ Handle edge cases (no expenses)

## Definition of Done
- [ ] Logged-in seed user shows actual name/email from database
- [ ] Total spent equals ₹346.24 (sum of seed expenses)
- [ ] Transaction count shows 8
- [ ] Top category shows "Bills" (highest category total)
- [ ] Transaction list shows 8 rows ordered newest first
- [ ] Category breakdown shows 7 categories with percentages summing to 100%
- [ ] All amounts display ₹ symbol
- [ ] New users see ₹0.00, 0 transactions, empty breakdown without errors
- [ ] All database queries use parameterized statements
- [ ] No hardcoded data remains in profile route

## Detailed Function Specifications

### get_user_by_id(user_id)
- **Input**: user_id (integer)
- **Returns**: dict with keys: id, name, email, member_since (formatted as "Month YYYY") or None if not found
- **Logic**: 
  1. Query users table for the given user_id
  2. Format the created_at timestamp to "Month YYYY" format
  3. Return dict with user data

### get_summary_stats(user_id)
- **Input**: user_id (integer)
- **Returns**: dict with keys: total_spent (float), transaction_count (int), top_category (string or "—" if no expenses)
- **Logic**:
  1. Calculate SUM(amount) and COUNT(*) from expenses for user_id
  2. Find category with highest SUM(amount) for top_category
  3. Return zeros and "—" for top_category if no expenses exist

### get_recent_transactions(user_id, limit=10)
- **Input**: user_id (integer), limit (integer, default 10)
- **Returns**: list of dicts, each with date, description, category, amount, ordered by date DESC
- **Logic**:
  1. Query expenses table for user_id ordered by date DESC with LIMIT
  2. Return list of dicts, empty list if no expenses

### get_category_breakdown(user_id)
- **Input**: user_id (integer)
- **Returns**: list of dicts, each with name (category), amount (float), pct (int percentage)
- **Logic**:
  1. Get total spent per category for user_id
  2. Calculate overall total spent
  3. For each category, calculate percentage = (category_total / overall_total) * 100
  4. Round percentages to integers and adjust largest category to ensure sum = 100
  5. Return list ordered by amount descending, empty list if no expenses