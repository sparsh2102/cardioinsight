import sqlite3, os
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

DB_PATH = 'cardioinsight.db'

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        name       TEXT NOT NULL,
        email      TEXT UNIQUE NOT NULL,
        password   TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS assessments (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id     INTEGER,
        name        TEXT,
        age         INTEGER,
        sex         INTEGER,
        cholesterol INTEGER,
        bp          INTEGER,
        heart_rate  INTEGER,
        smoking     INTEGER,
        exercise    INTEGER,
        exang       INTEGER,
        ca          INTEGER,
        risk_score  REAL,
        risk_label  TEXT,
        created_at  TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')

    conn.commit()
    conn.close()

# ── User functions ─────────────────────────────────────────────
def register_user(name, email, password):
    try:
        conn = get_db()
        pw_hash = generate_password_hash(password)
        conn.execute('INSERT INTO users (name,email,password) VALUES (?,?,?)',
                     (name, email, pw_hash))
        conn.commit()
        conn.close()
        return True, "Registration successful"
    except sqlite3.IntegrityError:
        return False, "Email already registered"

def login_user(email, password):
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE email=?', (email,)).fetchone()
    conn.close()
    if user and check_password_hash(user['password'], password):
        return True, dict(user)
    return False, "Invalid email or password"

def get_user_by_id(user_id):
    conn = get_db()
    user = conn.execute('SELECT * FROM users WHERE id=?', (user_id,)).fetchone()
    conn.close()
    return dict(user) if user else None

# ── Assessment functions ────────────────────────────────────────
def save_assessment(user_id, name, age, sex, chol, bp, hr, smoking, exercise, exang, ca, risk, label):
    conn = get_db()
    conn.execute('''INSERT INTO assessments
        (user_id,name,age,sex,cholesterol,bp,heart_rate,smoking,exercise,exang,ca,risk_score,risk_label)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)''',
        (user_id, name, age, sex, chol, bp, hr, smoking, exercise, exang, ca, risk, label))
    conn.commit()
    conn.close()

def get_user_assessments(user_id):
    conn = get_db()
    rows = conn.execute(
        'SELECT * FROM assessments WHERE user_id=? ORDER BY created_at DESC',
        (user_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_stats():
    conn = get_db()
    total = conn.execute('SELECT COUNT(*) FROM assessments').fetchone()[0]
    high  = conn.execute("SELECT COUNT(*) FROM assessments WHERE risk_label='High Risk'").fetchone()[0]
    avg   = conn.execute('SELECT AVG(risk_score) FROM assessments').fetchone()[0]
    conn.close()
    return {'total': total, 'high_risk': high, 'avg_risk': round(avg or 0, 1)}

def update_user_name(user_id, new_name):
    conn = get_db()
    conn.execute('UPDATE users SET name=? WHERE id=?', (new_name, user_id))
    conn.commit()
    conn.close()

def update_user_password(user_id, new_password):
    conn = get_db()
    pw_hash = generate_password_hash(new_password)
    conn.execute('UPDATE users SET password=? WHERE id=?', (pw_hash, user_id))
    conn.commit()
    conn.close()

def clear_user_history(user_id):
    conn = get_db()
    conn.execute('DELETE FROM assessments WHERE user_id=?', (user_id,))
    conn.commit()
    conn.close()

def get_user_risk_stats(user_id):
    conn = get_db()
    total = conn.execute('SELECT COUNT(*) FROM assessments WHERE user_id=?', (user_id,)).fetchone()[0]
    avg   = conn.execute('SELECT AVG(risk_score) FROM assessments WHERE user_id=?', (user_id,)).fetchone()[0]
    conn.close()
    return {'total': total, 'avg_risk': round(avg or 0, 1) if avg else None}

def get_admin_stats():
    conn = get_db()
    total_users = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    total_ass   = conn.execute('SELECT COUNT(*) FROM assessments').fetchone()[0]
    high  = conn.execute("SELECT COUNT(*) FROM assessments WHERE risk_label='High Risk'").fetchone()[0]
    mod   = conn.execute("SELECT COUNT(*) FROM assessments WHERE risk_label='Moderate Risk'").fetchone()[0]
    low   = conn.execute("SELECT COUNT(*) FROM assessments WHERE risk_label='Low Risk'").fetchone()[0]
    avg   = conn.execute('SELECT AVG(risk_score) FROM assessments').fetchone()[0]
    conn.close()
    return {
        'total_users': total_users, 'total_assessments': total_ass,
        'high_risk_count': high, 'mod_risk_count': mod,
        'low_risk_count': low, 'avg_risk': round(avg or 0, 1)
    }

def get_all_assessments(limit=50):
    conn = get_db()
    rows = conn.execute(
        'SELECT * FROM assessments ORDER BY created_at DESC LIMIT ?', (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_users():
    conn = get_db()
    rows = conn.execute('SELECT id, name, email, created_at FROM users ORDER BY id').fetchall()
    conn.close()
    return [dict(r) for r in rows]
