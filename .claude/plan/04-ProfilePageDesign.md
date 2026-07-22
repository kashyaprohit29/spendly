# Implementation Plan: Profile Page (Step 4)

## Context
The Spendly expense tracker currently has a stub `/profile` route that returns placeholder text. This step implements the full profile page UI using hardcoded data, establishing the visual layout before connecting to actual database queries in Step 5. The profile page will display user information, summary statistics, transaction history, and category breakdowns.

## Recommended Approach
1. **Update app.py**: Replace the `/profile` stub with a proper view function that:
   - Checks for user authentication via `session.get("user_id")`
   - Redirects to `/login` if not authenticated
   - Passes hardcoded user data, statistics, transactions, and category breakdowns to the template
2. **Create template**: Build `templates/profile.html` extending `base.html` with four sections:
   - User info card (name, email, member-since)
   - Summary stats row (total spent, transaction count, top category)
   - Transaction history table (date, description, category badge, amount)
   - Category breakdown list (category names with totals)
3. **Adhere to constraints**: 
   - No database queries in this step (hardcoded data only)
   - Use CSS variables, no inline styles or hex colors
   - All templates extend `base.html`
   - Authentication guard using session check
   - Parameterized queries if any DB interaction were added (though none in this step)

## Files to Modify
- `app.py`: Replace the `/profile` route stub

## Files to Create
- `templates/profile.html` (new file)

## Implementation Details

### app.py changes
Replace the current stub:
```python
@app.route("/profile")
def profile():
    return "Profile page — coming in Step 4"
```

With a view function that:
- Checks authentication via session
- Redirects unauthenticated users to login
- Passes hardcoded data matching the seed data from database/db.py:
  - User info (name, email, member since date)
  - Summary statistics (total spent, transaction count, top category)
  - Recent transactions list (date, description, category, amount)
  - Category totals breakdown

### templates/profile.html structure
Create a template that extends `base.html` with:
- User info card showing avatar initials, name, email, and member-since date
- Summary stats row with three stat cards (total spent, transactions, top category)
- Transaction history table with columns for date, description, category (with badge), and amount
- Category breakdown section showing each category with its total and a progress bar visualization

## Verification Steps
1. Start the application: `python app.py`
2. Navigate to `/profile` without logging in → should redirect to `/login`
3. Log in with demo credentials (demo@spendly.com / demo123)
4. Verify `/profile` returns HTTP 200
5. Check that page displays:
   - User info card with name and email
   - Summary stats with at least three values (total spent, transaction count, top category)
   - Transaction history table with at least three hardcoded rows
   - Category breakdown section with at least three categories
   - Navbar shows logged-in state (username + logout link)
   - No hex color values in profile.html (only CSS variables)


## Dependencies
- Completion of Steps 1-3 (database, registration, login/logout)
- Existing `base.html` template
- Existing CSS variables in stylesheet