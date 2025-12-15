import json
import sqlite3
from sqlite3 import IntegrityError

from flask import Flask, request
app = Flask(__name__)


def get_db():
    # Підключення до бази даних
    conn = sqlite3.connect('Users.db')

    # Створення курсора
    cursor = conn.cursor()

    # Створення таблиці (якщо її ще немає)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (

    id INTEGER PRIMARY KEY AUTOINCREMENT,
    Login  TEXT UNIQUE,
    password TEXT

    )
    """)

    return conn, cursor

@app.post("/reg")
def reg():
    conn, cursor = get_db()
    with conn:
        try:
            login = request.form.get('login')
            password = request.form.get('password')
            print(login, password)
            cursor.execute("INSERT INTO users (Login, password) VALUES (?, ?)", (login, password))
            conn.commit()
            return json.dumps({
            'success': True,
            'message': ''
            })
        except IntegrityError as e:
            print(e, type(e))
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
            print(login, password)
            cursor.execute("SELECT * FROM users WHERE Login = ? and password = ?", (login, password))
            user = cursor.fetchone()
            print(user)
            if not user:
                return json.dumps({
                    'success': False,
                    'message': "Користувача з таким логіном не знайдено"
                })
            else:
                return json.dumps({
            'success': True,
            'message': ''
            })
        except Exception:
            return json.dumps({
                'success': False,
                'message': 'Internal server error'
            })



# # Перевірка результату (вибірка всіх записів)
# cursor.execute("SELECT * FROM users")
# data = cursor.fetchall()
# for date in data:
#     print(date)  # Вивести всі записи з таблиці


# Закриття з'єднання
# conn.close()
if __name__ == "__main__":

    app.run(debug=True)