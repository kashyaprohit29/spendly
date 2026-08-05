# Spec: Delete Expense

## Overview
This feature lets a logged-in user permanently remove one of their own expenses from Spendly. It replaces the `GET /expenses/<id>/delete` stub with a real, ownership-checked delete action, adds a `delete_expense` query helper alongside the existing `get_expense_by_id`/`update_expense` helpers in `database/queries.py`, and adds a **Delete** action next to the existing **Edit** link on each transaction row in `profile.html`. Because deletion is destructive and irreversible, the delete action must be a POST-only route guarded by a client-side confirmation prompt — never a bare `GET` link a crawler or prefetch could trigger.

## Depends on
- Step 1: Database setup — `expenses` table and `get_db()` with `PRAGMA foreign_keys = ON`.
- Step 3: Login / Logout — `session['user_id']` established on login, cleared on logout.
- Step 8: Edit Expense — establishes the ownership-check pattern (`get_expense_by_id(id, user_id)` scoping, 404 on not-found/not-owned) that this feature reuses for the delete path, and adds the transaction `id` to `get_recent_transactions` rows that `profile.html` already relies on for the Edit link.

## Routes
- `POST /expenses/<id>/delete` — deletes the expense if it belongs to the logged-in user, then redirects to `/profile` — logged-in only

The existing stub is currently `GET`-only with no auth check; it is replaced entirely (no `GET` variant is kept — a `GET` request to this path now returns 405, Flask's default behavior for an unmatched method on a defined path).

## Database changes
No schema changes. Uses the existing `expenses` table (`database/db.py`, `init_db()`):
```sql
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    category TEXT NOT NULL,
    date TEXT NOT NULL,
    description TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users (id)
)
```
No `ON DELETE CASCADE` exists on the FK and none is needed — this feature only deletes rows *from* `expenses`, it never deletes a `users` row.

## Templates
- **Create:** none.
- **Modify:** `templates/profile.html` — in the transaction row loop (currently lines 69-79), add a delete control next to the existing Edit link in the Actions cell:
  ```html
  <td>
      <a href="{{ url_for('edit_expense', id=tx.id) }}">Edit</a>
      <form method="POST" action="{{ url_for('delete_expense', id=tx.id) }}" class="delete-form">
          <button type="submit" class="btn-delete-link" onclick="return confirm('Delete this expense? This cannot be undone.');">Delete</button>
      </form>
  </td>
  ```
  The `<button class="btn-delete-link">` must be styled to read as an inline text link (matching the existing `<a>Edit</a>`), not as a default `<button>` — add the `.btn-delete-link` rule to `static/css/style.css` (global, since `profile.html` uses `css/profile.css` for page styles but the Actions-cell control pairs with the existing Edit link styling, which is not page-specific). Do not add a new CSS file for a one-rule change.

## Files to change
- `app.py`:
  - Import `delete_expense` from `database.queries` alongside the existing `get_expense_by_id, update_expense` import.
  - Replace the stub at the current `/expenses/<id>/delete` route with:
    ```python
    @app.route("/expenses/<int:id>/delete", methods=["POST"])
    def delete_expense(id):
        if not session.get("user_id"):
            return redirect(url_for("login"))

        expense = get_expense_by_id(id, session["user_id"])
        if not expense:
            abort(404)

        delete_expense(id, session["user_id"])

        return redirect(url_for("profile"))
    ```
    Note the naming collision: the imported query function and the route view function cannot both be named `delete_expense` in the same module. Import the query helper under an alias — `from database.queries import delete_expense as delete_expense_row` — and call `delete_expense_row(id, session["user_id"])` inside the view. Keep the view function itself named `delete_expense` so `url_for('delete_expense', id=...)` in templates continues to work unchanged.
- `database/queries.py`:
  - Add `delete_expense(expense_id, user_id)`, following the same shape as `update_expense`: `DELETE FROM expenses WHERE id = ? AND user_id = ?`, commit, no return value. The `user_id` clause is the ownership guard — identical double-guard pattern to step 8 (the route already calls `get_expense_by_id` first to 404 on not-found/not-owned; the `WHERE user_id = ?` in the delete statement itself is the second guard, matching how `update_expense` is written).
- `templates/profile.html`: add the delete form/button described above.
- `static/css/style.css`: add a `.btn-delete-link` rule that resets button chrome (border/background/padding/font) so it renders inline like the adjacent `<a>Edit</a>` text link, using existing CSS variables for color — no new hex values.

## Files to create
None.

## New dependencies
No new dependencies.

## Rules for implementation
- No SQLAlchemy or ORMs — raw `sqlite3` only via `get_db()`.
- Parameterised queries only — never string-format values into SQL.
- Foreign keys PRAGMA must be enabled on every connection (already done in `get_db()`).
- `/expenses/<id>/delete` must be POST-only — no GET handler, so it cannot be triggered by a plain link, browser prefetch, or crawler.
- Unauthenticated access to `POST /expenses/<id>/delete` must redirect to `/login`.
- `get_expense_by_id` (already scoped to `id = ? AND user_id = ?`) must be called first to verify ownership; if the expense does not exist or belongs to another user, return a 404 via `abort(404)` — do not call the delete query at all in that case.
- The new `delete_expense` query function must independently scope its `DELETE` statement to `WHERE id = ? AND user_id = ?` as a second ownership guard, even though the route already checked ownership — same double-guard pattern as `update_expense`.
- After a successful delete, redirect to `url_for("profile")` — do not render any intermediate template.
- The delete control in `profile.html` must require a client-side `confirm()` before submitting — no silent/instant deletes.
- Use CSS variables — never hardcode hex values.
- All templates extend `base.html` (no new templates are added by this feature, but the modified `profile.html` continues to do so).
- No inline `<style>` tags — the new button rule goes in `static/css/style.css`.
- Currency must always display as ₹ — not applicable to this feature directly (no amount is rendered in new markup), but do not regress the existing ₹ formatting already in the transaction row.

## Tests to write
Test file: `tests/test_delete_expense.py`, following the same fixture pattern as `tests/test_edit_expense.py` (`app`, `client`, `_insert_expense`, `_get_expense_row`, `auth_client` returning `(client, expense_id)`, and an `other_user_expense` fixture for the cross-user case).

### Unit tests
| Function | Input | Expected output |
|---|---|---|
| `delete_expense` | Existing `expense_id` owned by `user_id` | Row removed from `expenses`; `_get_expense_row(expense_id)` returns `None` after |
| `delete_expense` | `expense_id` that exists but belongs to a different `user_id` | No row removed; the other user's expense row is unchanged |
| `delete_expense` | Nonexistent `expense_id` | No error raised; no rows affected |

### Route tests
- `POST /expenses/<id>/delete` — unauthenticated:
  - Redirects to `/login` (302)
  - The expense row still exists in the database afterward
- `POST /expenses/<id>/delete` — authenticated, owns the expense:
  - Returns a redirect (302) to `/profile`
  - The expense row no longer exists in the database afterward (`_get_expense_row` returns `None`)
- `POST /expenses/<id>/delete` — authenticated, expense belongs to another user (`other_user_expense`):
  - Returns 404
  - The other user's expense row still exists in the database afterward, unchanged
- `POST /expenses/<id>/delete` — authenticated, nonexistent expense id (e.g. `99999`):
  - Returns 404
- `GET /expenses/<id>/delete` — authenticated, owns the expense:
  - Returns 405 (method not allowed) — confirms the route is POST-only
  - The expense row still exists in the database afterward

## Definition of done
- [ ] Logging in, then clicking **Delete** next to any transaction on the profile page prompts a browser confirmation dialog before submitting.
- [ ] Confirming the dialog removes the expense from the transaction list and returns the user to `/profile`.
- [ ] Dismissing the confirmation dialog leaves the expense untouched and the page unchanged.
- [ ] After deleting an expense, the summary stats (total spent, transaction count, top category) and category breakdown on `/profile` reflect the removal on next load.
- [ ] Visiting `POST /expenses/<id>/delete` for an expense owned by another user returns a 404 and does not delete that user's data.
- [ ] Visiting `POST /expenses/<id>/delete` while logged out redirects to `/login` and does not delete anything.
- [ ] Sending a `GET` request to `/expenses/<id>/delete` returns 405 — there is no way to delete an expense via a plain link or GET request.
- [ ] All new/changed code uses parameterized SQL queries — no f-strings or string concatenation in any SQL statement.
- [ ] `pytest tests/test_delete_expense.py` passes.
