from flask import Flask, request, render_template_string
import sqlite3
import os
import subprocess
import pickle

app = Flask(__name__)

# Hardcoded secret (Bad practice)
app.secret_key = "hardcoded-secret-key"

DATABASE = "test.db"

def get_db():
    conn = sqlite3.connect(DATABASE)
    return conn

@app.route("/")
def index():
    return "Welcome to the vulnerable Flask app"

# 1. SQL Injection vulnerability
@app.route("/user")
def get_user():
    username = request.args.get("username")
    conn = get_db()
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)
    result = cursor.fetchall()
    return str(result)

# 2. XSS vulnerability
@app.route("/greet")
def greet():
    name = request.args.get("name", "")
    return render_template_string("<h1>Hello, {{ name }}</h1>", name=name)

# 3. Command Injection
@app.route("/ping")
def ping():
    host = request.args.get("host", "")
    # Allowlist of valid hosts
    ALLOWED_HOSTS = {"127.0.0.1", "localhost", "example.com"}
    if host not in ALLOWED_HOSTS:
        return "Invalid host", 400
    # Use subprocess.run for safer command execution
    result = subprocess.run(["ping", "-c", "1", host], capture_output=True, text=True)
    if result.returncode == 0:
        return f"Pinged {host}: {result.stdout}"
    else:
        return f"Failed to ping {host}: {result.stderr}", 500

# 4. Insecure deserialization
@app.route("/load_pickle", methods=["POST"])
def load_pickle():
    data = request.data
    obj = pickle.loads(data)  # Insecure deserialization
    return f"Loaded object: {obj}"

# 5. Information leakage (debug mode)
if __name__ == "__main__":
    app.run(debug=True)
