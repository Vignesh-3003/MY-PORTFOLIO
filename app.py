import hmac
import os
import re
import sqlite3

from flask import Flask, abort, g, jsonify, request, send_from_directory

app = Flask(__name__)
BASE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE, "portfolio.db")
ADMIN_KEY = os.environ.get("ADMIN_KEY", "change-me")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def init_db():
    with sqlite3.connect(DB) as c:
        c.executescript(
            """
            CREATE TABLE IF NOT EXISTS visits (id INTEGER PRIMARY KEY, n INTEGER NOT NULL);
            INSERT OR IGNORE INTO visits (id, n) VALUES (1, 0);
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL, email TEXT NOT NULL, message TEXT NOT NULL,
                created TEXT DEFAULT CURRENT_TIMESTAMP
            );
            """
        )


def db():
    if "db" not in g:
        g.db = sqlite3.connect(DB)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_):
    conn = g.pop("db", None)
    if conn:
        conn.close()


@app.route("/")
def home():
    return send_from_directory(BASE, "index.html")


@app.get("/<name>.jpg")
def photo(name):
    if name not in ("vignesh", "avatar"):
        abort(404)
    return send_from_directory(BASE, name + ".jpg")


@app.get("/api/visit")
def visit():
    conn = db()
    is_new = request.cookies.get("seen") is None  # count each browser once a day
    if is_new:
        conn.execute("UPDATE visits SET n = n + 1 WHERE id = 1")
        conn.commit()
    total = conn.execute("SELECT n FROM visits WHERE id = 1").fetchone()["n"]
    resp = jsonify(visits=total)
    if is_new:
        resp.set_cookie("seen", "1", max_age=86400, samesite="Lax")
    return resp


@app.post("/api/contact")
def contact():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip()
    message = str(data.get("message", "")).strip()
    errors = {}
    if not 2 <= len(name) <= 80:
        errors["name"] = "Enter your name (2 to 80 characters)."
    if not EMAIL_RE.match(email) or len(email) > 120:
        errors["email"] = "Enter a valid email address."
    if not 10 <= len(message) <= 1000:
        errors["message"] = "Write a message of 10 to 1000 characters."
    if errors:
        return jsonify(ok=False, errors=errors), 400
    conn = db()
    conn.execute(
        "INSERT INTO messages (name, email, message) VALUES (?, ?, ?)",
        (name, email, message),
    )
    conn.commit()
    return jsonify(ok=True)


@app.get("/admin/messages")
def admin_messages():
    key = request.args.get("key", "")
    if not hmac.compare_digest(key, ADMIN_KEY):
        return jsonify(error="Not allowed"), 403
    rows = db().execute("SELECT * FROM messages ORDER BY id DESC").fetchall()
    return jsonify([dict(r) for r in rows])


init_db()

if __name__ == "__main__":
    app.run(debug=True)
