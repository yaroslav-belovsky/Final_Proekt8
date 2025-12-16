from flask import Flask, render_template, request, redirect, session
from users import get_db
app = Flask(__name__)
app.secret_key = "123"
@app.route("/", methods=["GET", "POST"])
def login_page():
    error = ""
    if request.method == "POST":
        conn, cursor = get_db()
        login = request.form["login"]
        password = request.form["password"]
        cursor.execute("SELECT * FROM users WHERE Login=? AND password=?", (login, password))
        user = cursor.fetchone()
        if user:
            session["user_id"] = user["id"]
            session["login"] = user["Login"]
            return redirect("/questions_page")
        else:
            error = "Невірний логін або пароль"
    return render_template("login.html", error=error)
@app.route("/register", methods=["GET", "POST"])
def register_page():
    error = ""
    if request.method == "POST":
        conn, cursor = get_db()
        try:
            cursor.execute("INSERT INTO users (Login, password) VALUES (?, ?)", (request.form["login"], request.form["password"]))
            conn.commit()
            return redirect("/")
        except:
            error = "Логін вже існує"
    return render_template("register.html", error=error)
@app.route("/questions_page")
def questions_page():
    if "user_id" not in session:
        return redirect("/")
    conn, cursor = get_db()
    cursor.execute("""
        select q.*, u.Login as q_user
        from questions q
        left join users u on u.id = q.user_id
    """)
    questions = cursor.fetchall()
    return render_template("questions.html", questions=questions, user=session["login"])
@app.route("/questions_add", methods=["POST"])
def questions_add():
    if "user_id" not in session:
        return redirect("/")
    conn, cursor = get_db()
    cursor.execute("INSERT INTO questions (user_id, question) VALUES (?, ?)", (session["user_id"], request.form["question"]))
    conn.commit()
    return redirect("/questions_page")
@app.route("/questions_page/<int:id>")
def question_page(id):
    conn, cursor = get_db()
    cursor.execute("""
        select 
            q.question,
            u.Login as q_user,
            a.answer,
            au.Login as a_user
        from questions q
        left join users u on u.id = q.user_id
        left join answers a on a.question_id = q.id
        left join users au on au.id = a.user_id
        where q.id=?
    """, (id,))
    rows = cursor.fetchall()
    return render_template("question.html", rows=rows, qid=id)
@app.route("/answers_add", methods=["POST"])
def answers_add():
    if "user_id" not in session:
        return redirect("/")
    conn, cursor = get_db()
    cursor.execute("INSERT INTO answers (question_id, user_id, answer) VALUES (?, ?, ?)",
                   (request.form["qid"], session["user_id"], request.form["answer"]))
    conn.commit()
    return redirect(f"/questions_page/{request.form['qid']}")
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")
if __name__ == "__main__":
    app.run(debug=True)
