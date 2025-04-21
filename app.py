import os
import sqlite3
from functools import wraps

from flask import Flask, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.secret_key = "super_insecure_secret_key"
app.debug = True
os.environ["WERKZEUG_DEBUG_PIN"] = "off"


def get_db_connection():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    return conn


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)

    return decorated_function


@app.route("/")
@login_required
def index():
    return redirect(url_for("dashboard"))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        user = conn.execute(query).fetchone()
        conn.close()

        if user:
            session["logged_in"] = True
            session["username"] = user["username"]
            return redirect(url_for("dashboard"))

        error = "Invalid credentials"

    return render_template("login.html", error=error)


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", username=session.get("username"))


@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    session.pop("username", None)
    return redirect(url_for("login"))


@app.route("/users")
@app.route("/analytics")
@app.route("/settings")
@app.route("/profile")
@login_required
def under_construction():
    raise Exception("[ERROR]: Feature not completed")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
