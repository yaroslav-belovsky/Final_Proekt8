import json
import sqlite3
from sqlite3 import IntegrityError
from flask import Flask, request

app = Flask(__name__)


def get_db():
    # Підключення до бази даних
    conn = sqlite3.connect('Users.db')
    conn.row_factory = sqlite3.Row
    # Створення курсора
    cursor = conn.cursor()

    # Створення таблиці (якщо її ще немає)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        Login  TEXT UNIQUE,
        password TEXT
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        question text
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS answers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question_id INTEGER,
        user_id INTEGER,
        answer text
    );
    """)

    return conn, cursor

@app.post("/reg")
def reg():
    conn, cursor = get_db()
    with conn:
        try:
            login = request.form.get('login')
            password = request.form.get('password')
            cursor.execute("INSERT INTO users (Login, password) VALUES (?, ?)", (login, password))
            conn.commit()
            return json.dumps({
            'success': True,
            'message': ''
            })
        except IntegrityError as e:
            return json.dumps({
                'success': False,
                'message': "Користувач з таким логіном вже існує"
            })
        except Exception:
            return json.dumps({
                'success': False,
                'message': 'Internal server error'
            })


@app.post("/login")
def login():
    conn, cursor = get_db()
    with conn:
        try:
            login = request.form.get('login')
            password = request.form.get('password')
            cursor.execute("SELECT * FROM users WHERE Login = ? and password = ?", (login, password))
            user = cursor.fetchone()
            if not user:
                return json.dumps({
                    'success': False,
                    'message': "Користувача з таким логіном не знайдено"
                })
            else:
                return json.dumps({
                    'success': True,
                    'message': '',
                    'user_id': user['id']
                })
        except Exception:
            return json.dumps({
                'success': False,
                'message': 'Internal server error'
            })

@app.post("/questions")
def questions_add():
    conn, cursor = get_db()
    with conn:
        try:
            user_id = request.form.get('user_id')
            question = request.form.get('question')
            cursor.execute("INSERT INTO questions (user_id, question) VALUES (?, ?)", (user_id, question))
            conn.commit()
            return json.dumps({
            'success': True,
            'message': ''
            })
        except Exception:
            return json.dumps({
                'success': False,
                'message': 'Internal server error'
            })

@app.get("/questions")
def questions_list():
    conn, cursor = get_db()
    with conn:
        try:
            cursor.execute("""
                select 
                    q.*,
                    qu.login as question_user 
                from questions q
                left join users qu on qu.id = q.user_id
                """)
            return json.dumps({
            'success': True,
            'message': '',
            'items': [dict(row) for row in cursor.fetchall()]
            })
        except Exception as e:
            return json.dumps({
                'success': False,
                'message': 'Internal server error'
            })


@app.get('/questions/<int:id>')
def question(id):
    conn, cursor = get_db()
    with conn:
        try:
            cursor.execute("""
                select 
                    q.*,
                    qu.login as question_user,
                    au.login as answer_user,
                    a.id answer_id,
                    a.user_id answer_user_id,
                    a.answer
                from questions q
                left join users qu on qu.id = q.user_id
                left join answers a on a.question_id = q.id
                left join users au on au.id = a.user_id
                where q.id = ?
            """, (id,))
            return json.dumps({
                'success': True,
                'message': '',
                'items':  [dict(row) for row in cursor.fetchall()]
            })
        except Exception as e:
            return json.dumps({
                'success': False,
                'message': 'Internal server error'
            })

@app.post("/answers")
def answers_add():
    conn, cursor = get_db()
    with conn:
        try:
            question_id = request.form.get('question_id')
            user_id = request.form.get('user_id')
            answer = request.form.get('answer')
            cursor.execute("INSERT INTO answers (question_id, user_id, answer) VALUES (?, ?, ?)", (question_id, user_id, answer))
            conn.commit()
            return json.dumps({
            'success': True,
            'message': ''
            })
        except Exception as e:
            return json.dumps({
                'success': False,
                # 'message': 'Internal server error'
                'message': str(e)
            })


# Закриття з'єднання
# conn.close()
if __name__ == "__main__":

    app.run(debug=True)