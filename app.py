from flask import Flask, render_template, request, redirect, url_for, session
app = Flask(__name__)
app.secret_key = "letmein"

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/fake-login", methods=["POST"])
def fake_login():
    session["honeypot"] = True
    return redirect(url_for("wrong_dashboard"))

@app.route("/wrongdashboard")
def wrong_dashboard():
    if not session.get("honeypot"):
        return redirect(url_for("home"))
    return render_template("wrongdashboard.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("uname")
        password = request.form.get("psw")
        if username == "admin" and password == "password123":
            session["authenticated"] = True
            return redirect(url_for("dashboard"))
        error = "Invalid credentials"
    return render_template("login.html", error=error)

@app.route("/dashboard")
def dashboard():
    if not session.get("authenticated"):
        return redirect(url_for("login"))
    return render_template("dashboard.html")

@app.route("/admin-panel")
def admin_panel():
    if not session.get("superadmin"):
        return "Access denied", 403
    return render_template("admin_panel.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

CORRECT_ANSWERS = {
    "q1": "hydra",
    "q2": "burp",
    "q3": "cookie",
    "q4": "flask-unsign"
}

@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    if not session.get("superadmin"):
        return redirect(url_for("login"))
    error = None
    if request.method == "POST":
        answers = {
            "q1": request.form.get("q1", "").strip().lower(),
            "q2": request.form.get("q2", "").strip().lower(),
            "q3": request.form.get("q3", "").strip().lower(),
            "q4": request.form.get("q4", "").strip().lower(),
        }
        if answers == CORRECT_ANSWERS:
            session["quiz_passed"] = True
            return redirect(url_for("vault"))
        error = "Not quite — review and try again."
    return render_template("quiz.html", error=error)

@app.route("/vault")
def vault():
    if not session.get("quiz_passed"):
        return redirect(url_for("quiz"))
    return render_template("vault.html")

if __name__ == "__main__":
    app.run(debug=False)
