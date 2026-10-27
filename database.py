"""database.py - everything that talks to the SQLite database."""
import os
import sys
import sqlite3
import hashlib

if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_NAME = os.path.join(BASE_DIR, "expense.db")


def get_connection():
    return sqlite3.connect(DB_NAME)


def query(sql, params=(), write=False):
    """Run one SQL command. Returns rows for SELECT, nothing for INSERT/UPDATE/DELETE."""
    conn = get_connection()
    try:
        cur = conn.execute(sql, params)
        if write:
            conn.commit()
            return None
        return cur.fetchall()
    finally:
        conn.close()


def create_tables():
    query("""CREATE TABLE IF NOT EXISTS users(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL)""", write=True)
    query("""CREATE TABLE IF NOT EXISTS expenses(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                date TEXT,
                category TEXT,
                amount REAL,
                description TEXT)""", write=True)
    query("""CREATE TABLE IF NOT EXISTS settings(
                key TEXT PRIMARY KEY,
                value TEXT)""", write=True)


# ---------------- USER LOGIN ----------------
def hash_password(password, salt=None):
    """Store 'salt$hash' - the random salt makes every hash different."""
    salt = salt or os.urandom(8).hex()
    return salt + "$" + hashlib.sha256((salt + password).encode()).hexdigest()


def register_user(username, password):
    """Returns True if created, False if the username already exists."""
    try:
        query("INSERT INTO users(username, password) VALUES(?, ?)",
              (username, hash_password(password)), write=True)
        return True
    except sqlite3.IntegrityError:
        return False


def check_login(username, password):
    rows = query("SELECT password FROM users WHERE username=?", (username,))
    if not rows:
        return False
    stored = rows[0][0]
    salt = stored.split("$")[0]
    return hash_password(password, salt) == stored


# ---------------- CRUD ON EXPENSES (each user sees only his own) ----------------
def add_expense(user, date, category, amount, description):          # Create
    query("INSERT INTO expenses(username, date, category, amount, description) "
          "VALUES(?,?,?,?,?)", (user, date, category, amount, description), write=True)


def get_all_expenses(user):                                          # Read
    return query("SELECT id, date, category, amount, description FROM expenses "
                 "WHERE username=? ORDER BY date DESC, id DESC", (user,))


def update_expense(exp_id, date, category, amount, description):     # Update
    query("UPDATE expenses SET date=?, category=?, amount=?, description=? WHERE id=?",
          (date, category, amount, description, exp_id), write=True)


def delete_expense(exp_id):                                          # Delete
    query("DELETE FROM expenses WHERE id=?", (exp_id,), write=True)


# ---------------- BUDGET (one per user) ----------------
def set_budget(user, amount):
    query("INSERT OR REPLACE INTO settings(key, value) VALUES(?, ?)",
          (f"budget_{user}", str(amount)), write=True)


def get_budget(user):
    rows = query("SELECT value FROM settings WHERE key=?", (f"budget_{user}",))
    return float(rows[0][0]) if rows else None