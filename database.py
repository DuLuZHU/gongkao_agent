import sqlite3
import os
from datetime import datetime

def init_database(db_path):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            content TEXT NOT NULL,
            type TEXT,
            tags TEXT,
            analysis TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS wrong_answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            question_id INTEGER,
            user_answer TEXT,
            correct_answer TEXT,
            review_count INTEGER DEFAULT 0,
            last_review TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (question_id) REFERENCES questions(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            content TEXT NOT NULL,
            tags TEXT,
            category TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shenlun_submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            requirements TEXT,
            answer TEXT,
            material TEXT,
            critique TEXT,
            score INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS battle_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            question_id INTEGER,
            is_correct BOOLEAN,
            time_spent REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (question_id) REFERENCES questions(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS review_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            question_id INTEGER,
            due_date TIMESTAMP,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (question_id) REFERENCES questions(id)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_connection(db_path):
    return sqlite3.connect(db_path)

def add_user(db_path, username, password):
    conn = get_connection(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user(db_path, username, password):
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

def add_question(db_path, user_id, content, type=None, tags=None, analysis=None):
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO questions (user_id, content, type, tags, analysis) VALUES (?, ?, ?, ?, ?)',
        (user_id, content, type, tags, analysis)
    )
    conn.commit()
    question_id = cursor.lastrowid
    conn.close()
    return question_id

def add_wrong_answer(db_path, user_id, question_id, user_answer, correct_answer):
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO wrong_answers (user_id, question_id, user_answer, correct_answer) VALUES (?, ?, ?, ?)',
        (user_id, question_id, user_answer, correct_answer)
    )
    conn.commit()
    conn.close()

def get_wrong_answers(db_path, user_id):
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT wa.*, q.content FROM wrong_answers wa
        JOIN questions q ON wa.question_id = q.id
        WHERE wa.user_id = ?
        ORDER BY wa.created_at DESC
    ''', (user_id,))
    results = cursor.fetchall()
    conn.close()
    return results

def add_note(db_path, user_id, content, tags=None, category=None):
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO notes (user_id, content, tags, category) VALUES (?, ?, ?, ?)',
        (user_id, content, tags, category)
    )
    conn.commit()
    conn.close()

def search_notes(db_path, user_id, keyword):
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(
        'SELECT * FROM notes WHERE user_id = ? AND (content LIKE ? OR tags LIKE ?)',
        (user_id, f'%{keyword}%', f'%{keyword}%')
    )
    results = cursor.fetchall()
    conn.close()
    return results

def add_review_task(db_path, user_id, question_id, due_date):
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO review_tasks (user_id, question_id, due_date) VALUES (?, ?, ?)',
        (user_id, question_id, due_date)
    )
    conn.commit()
    conn.close()

def get_pending_reviews(db_path, user_id):
    conn = get_connection(db_path)
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute('''
        SELECT rt.*, q.content FROM review_tasks rt
        JOIN questions q ON rt.question_id = q.id
        WHERE rt.user_id = ? AND rt.status = 'pending' AND rt.due_date <= ?
        ORDER BY rt.due_date ASC
    ''', (user_id, now))
    results = cursor.fetchall()
    conn.close()
    return results

def update_review_status(db_path, task_id, status):
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute('UPDATE review_tasks SET status = ? WHERE id = ?', (status, task_id))
    conn.commit()
    conn.close()

def add_shenlun_submission(db_path, user_id, requirements, answer, material, critique, score):
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO shenlun_submissions (user_id, requirements, answer, material, critique, score) VALUES (?, ?, ?, ?, ?, ?)',
        (user_id, requirements, answer, material, critique, score)
    )
    conn.commit()
    conn.close()

def get_shenlun_submissions(db_path, user_id):
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(
        'SELECT * FROM shenlun_submissions WHERE user_id = ? ORDER BY created_at DESC',
        (user_id,)
    )
    results = cursor.fetchall()
    conn.close()
    return results

def add_battle_record(db_path, user_id, question_id, is_correct, time_spent):
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO battle_records (user_id, question_id, is_correct, time_spent) VALUES (?, ?, ?, ?)',
        (user_id, question_id, is_correct, time_spent)
    )
    conn.commit()
    conn.close()

def get_battle_stats(db_path, user_id):
    conn = get_connection(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM battle_records WHERE user_id = ?', (user_id,))
    total = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM battle_records WHERE user_id = ? AND is_correct = 1', (user_id,))
    correct = cursor.fetchone()[0]
    cursor.execute('SELECT AVG(time_spent) FROM battle_records WHERE user_id = ?', (user_id,))
    avg_time = cursor.fetchone()[0]
    conn.close()
    return {'total': total, 'correct': correct, 'avg_time': avg_time}

init_database(os.path.join(os.path.dirname(__file__), "data", "gongkao.db"))
