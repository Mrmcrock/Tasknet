import os
import re
import secrets
import sqlite3
from pathlib import Path

from flask import Flask, abort, redirect, request, send_from_directory, session, url_for, render_template_string
from markupsafe import escape
from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "tasknet.db"

app = Flask(__name__, static_folder="styles", static_url_path="/styles")
app.secret_key = os.environ.get("TASKNET_SECRET_KEY") or secrets.token_hex(32)
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("TASKNET_HTTPS", "0") == "1",
)

PAGES = {
    "index.html", "hire.html", "about.html", "services.html",
    "login.html", "signup.html", "contact.html", "faq.html", "payments.html",
}



# Payment configuration is deliberately environment-based. Never put API keys in HTML or Git.
TASK_CATALOG = {
    "car-wash-1h": {"name": "Car washing — 1 hour", "amount_pence": 500},
    "pet-care-1h": {"name": "Pet care — 1 hour", "amount_pence": 600},
    "garden-help-1h": {"name": "Garden help — 1 hour", "amount_pence": 700},
}



WORKERS_PAGE = """<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="theme-color" content="#10233f">
    <title>Find a Worker | TaskNet</title>

    <style>
        :root {
            --navy: #10233f;
            --blue: #2563eb;
            --blue-dark: #1d4ed8;
            --muted: #64748b;
            --border: #e2e8f0;
            --background: #f5f7fb;
            --white: #ffffff;
            --green: #15803d;
        }

        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            background: var(--background);
            color: var(--navy);
            font-family: Arial, Helvetica, sans-serif;
            line-height: 1.6;
        }

        a {
            color: inherit;
        }

        .topbar {
            background: var(--navy);
            color: white;
            padding: 17px 24px;
        }

        .topbar-inner {
            max-width: 1120px;
            margin: auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 18px;
        }

        .brand {
            font-size: 25px;
            font-weight: 800;
            letter-spacing: -1px;
            text-decoration: none;
        }

        .brand span {
            color: #60a5fa;
        }

        .top-link {
            color: #e2e8f0;
            text-decoration: none;
            font-size: 14px;
            font-weight: 700;
        }

        .top-link:hover {
            color: white;
            text-decoration: underline;
        }

        .container {
            max-width: 1120px;
            margin: 0 auto;
            padding: 34px 22px 60px;
        }

        .intro {
            margin-bottom: 27px;
        }

        .eyebrow {
            display: inline-block;
            color: var(--blue);
            background: #dbeafe;
            border-radius: 50px;
            padding: 5px 11px;
            font-size: 12px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.7px;
        }

        h1 {
            margin: 13px 0 8px;
            font-size: clamp(30px, 5vw, 43px);
            line-height: 1.15;
            letter-spacing: -1.3px;
        }

        .intro p {
            color: var(--muted);
            max-width: 650px;
            margin: 0;
        }

        .search-panel {
            background: var(--white);
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: 23px;
            margin-bottom: 34px;
            box-shadow: 0 8px 25px rgba(16, 35, 63, 0.04);
        }

        .search-heading {
            margin: 0 0 17px;
            font-size: 18px;
        }

        .filters {
            display: grid;
            grid-template-columns: minmax(180px, 1.2fr) minmax(180px, 1fr) auto auto;
            align-items: end;
            gap: 13px;
        }

        .field {
            display: grid;
            gap: 7px;
            min-width: 0;
        }

        .field label {
            font-size: 13px;
            font-weight: 700;
        }

        input,
        select {
            width: 100%;
            min-width: 0;
            padding: 12px;
            border: 1px solid #cbd5e1;
            border-radius: 9px;
            background: white;
            color: var(--navy);
            font: inherit;
            font-size: 14px;
        }

        input:focus,
        select:focus {
            outline: 3px solid #bfdbfe;
            border-color: var(--blue);
        }

        .btn {
            display: inline-flex;
            justify-content: center;
            align-items: center;
            gap: 7px;
            min-height: 44px;
            padding: 11px 16px;
            border: 1px solid transparent;
            border-radius: 9px;
            background: var(--blue);
            color: white;
            text-decoration: none;
            text-align: center;
            font: inherit;
            font-size: 14px;
            font-weight: 700;
            cursor: pointer;
            transition: background 0.15s ease;
            white-space: nowrap;
        }

        .btn:hover {
            background: var(--blue-dark);
        }

        .btn-secondary {
            background: white;
            color: var(--navy);
            border-color: var(--border);
        }

        .btn-secondary:hover {
            background: #f1f5f9;
        }

        .results-heading {
            display: flex;
            justify-content: space-between;
            align-items: end;
            gap: 14px;
            flex-wrap: wrap;
            margin-bottom: 17px;
        }

        .results-heading h2 {
            margin: 0;
            font-size: 23px;
            letter-spacing: -0.5px;
        }

        .results-count {
            color: var(--muted);
            font-size: 13px;
        }

        .worker-list {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 18px;
        }

        .worker-card {
            min-width: 0;
            background: white;
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 22px;
            box-shadow: 0 5px 18px rgba(16, 35, 63, 0.035);
            display: flex;
            flex-direction: column;
            gap: 17px;
        }

        .worker-top {
            display: flex;
            align-items: flex-start;
            gap: 13px;
        }

        .avatar {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 49px;
            height: 49px;
            flex: 0 0 49px;
            border-radius: 14px;
            background: #dbeafe;
            color: #1d4ed8;
            font-size: 21px;
            font-weight: 800;
            text-transform: uppercase;
        }

        .worker-heading {
            flex: 1;
            min-width: 0;
        }

        .worker-heading h3 {
            margin: 1px 0 4px;
            font-size: 19px;
            line-height: 1.3;
            overflow-wrap: anywhere;
        }

        .service-tag {
            display: inline-block;
            background: #eff6ff;
            color: #1d4ed8;
            border-radius: 6px;
            padding: 3px 8px;
            font-size: 12px;
            font-weight: 700;
        }

        .worker-bio {
            margin: 0;
            color: #526178;
            font-size: 14px;
            overflow-wrap: anywhere;
            white-space: pre-line;
        }

        .worker-location {
            margin: 0;
            display: flex;
            align-items: flex-start;
            gap: 7px;
            color: #475569;
            font-size: 13px;
            overflow-wrap: anywhere;
        }

        .worker-bottom {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            padding-top: 16px;
            border-top: 1px solid #edf1f6;
            margin-top: auto;
        }

        .rate-label {
            color: var(--muted);
            font-size: 12px;
        }

        .rate {
            color: var(--navy);
            font-size: 24px;
            line-height: 1.3;
            font-weight: 800;
            letter-spacing: -0.6px;
        }

        .rate small {
            color: var(--muted);
            font-size: 12px;
            font-weight: 500;
            letter-spacing: 0;
        }

        .notice {
            color: var(--muted);
            background: #eef2f7;
            border-radius: 9px;
            padding: 12px 14px;
            margin-top: 22px;
            font-size: 12px;
        }

        .empty-state {
            grid-column: 1 / -1;
            background: white;
            border: 1px dashed #cbd5e1;
            border-radius: 16px;
            padding: 44px 22px;
            text-align: center;
        }

        .empty-icon {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 58px;
            height: 58px;
            border-radius: 18px;
            background: #eff6ff;
            color: var(--blue);
            font-size: 27px;
        }

        .empty-state h3 {
            margin: 15px 0 6px;
            font-size: 21px;
        }

        .empty-state p {
            color: var(--muted);
            max-width: 420px;
            margin: 0 auto 20px;
            font-size: 14px;
        }

        .footer {
            border-top: 1px solid var(--border);
            background: white;
            padding: 20px;
            text-align: center;
            color: var(--muted);
            font-size: 12px;
        }

        @media (max-width: 900px) {
            .filters {
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }

            .worker-list {
                grid-template-columns: 1fr;
            }
        }

        @media (max-width: 520px) {
            .topbar {
                padding: 15px 18px;
            }

            .brand {
                font-size: 22px;
            }

            .container {
                padding: 26px 15px 42px;
            }

            .search-panel {
                padding: 17px;
            }

            .filters {
                grid-template-columns: 1fr;
            }

            .filters .btn {
                width: 100%;
            }

            .worker-card {
                padding: 18px;
            }

            .worker-bottom {
                align-items: flex-start;
                flex-direction: column;
            }

            .worker-bottom .btn {
                width: 100%;
            }
        }

        @media (prefers-reduced-motion: reduce) {
            *,
            *::before,
            *::after {
                transition: none !important;
            }
        }
    </style>
</head>

<body>
    <header class="topbar">
        <div class="topbar-inner">
            <a class="brand" href="/">Task<span>Net</span></a>
            <a class="top-link" href="/hire.html">← Back to services</a>
        </div>
    </header>

    <main class="container">
        <section class="intro">
            <span class="eyebrow">Local help, made easier</span>
            <h1>Find your next worker.</h1>
            <p>
                Explore TaskNet worker profiles, compare hourly rates,
                and find someone offering the service you need.
            </p>
        </section>

        <section class="search-panel" aria-labelledby="search-title">
            <h2 class="search-heading" id="search-title">Search worker profiles</h2>

            <form method="get" action="/workers" class="filters">
                <div class="field">
                    <label for="area">Area or postcode</label>
                    <input
                        id="area"
                        type="text"
                        name="area"
                        value="{{ area }}"
                        maxlength="100"
                        placeholder="e.g. Edinburgh"
                    >
                </div>

                <div class="field">
                    <label for="service">Service</label>
                    <select id="service" name="service">
                        <option value="">All services</option>
                        {% for option in services %}
                        <option value="{{ option }}" {% if service == option %}selected{% endif %}>{{ option }}</option>
                        {% endfor %}
                    </select>
                </div>

                <button class="btn" type="submit">Search workers</button>
                <a class="btn btn-secondary" href="/worker/profile">+ Create profile</a>
            </form>
        </section>

        <section aria-labelledby="results-title">
            <div class="results-heading">
                <h2 id="results-title">Available profiles</h2>
                <span class="results-count">
                    {{ workers|length }} profile{% if workers|length != 1 %}s{% endif %} found
                </span>
            </div>

            <div class="worker-list">
                {% if workers %}
                    {% for w in workers %}
                    <article class="worker-card">
                        <div class="worker-top">
                            <div class="avatar" aria-hidden="true">{{ w['name'][0]|upper }}</div>

                            <div class="worker-heading">
                                <h3>{{ w['name'] }}</h3>
                                <span class="service-tag">{{ w['service'] }}</span>
                            </div>
                        </div>

                        <p class="worker-bio">{{ w['bio'] }}</p>

                        <p class="worker-location">
                            <span aria-hidden="true">📍</span>
                            <span>Service area: <strong>{{ w['area'] }}</strong></span>
                        </p>

                        <div class="worker-bottom">
                            <div>
                                <div class="rate-label">Hourly rate</div>
                                <div class="rate">£{{ '%.2f'|format(w['rate']) }}<small> / hour</small></div>
                            </div>
                            <a class="btn btn-secondary" href="/worker/profile">Worker profiles</a>
                        </div>
                    </article>
                    {% endfor %}
                {% else %}
                    <div class="empty-state">
                        <div class="empty-icon" aria-hidden="true">⌕</div>
                        <h3>No matching workers yet</h3>
                        <p>
                            {% if service or area %}
                            Try changing your service or area filters. You can also create a worker profile.
                            {% else %}
                            There aren't any worker profiles yet. Be among the first to create one on TaskNet.
                            {% endif %}
                        </p>
                        <a class="btn" href="/worker/profile">Create a worker profile</a>
                        {% if service or area %}
                        <a class="btn btn-secondary" href="/workers">Clear filters</a>
                        {% endif %}
                    </div>
                {% endif %}
            </div>
        </section>

        <p class="notice">
            Worker profiles are submitted by registered users. Listings do not
            guarantee availability, verified qualifications, or confirmed bookings.
            Contact and booking features can be added in a later update.
        </p>
    </main>

    <footer class="footer">
        TaskNet · Helping people find local services
    </footer>
</body>
</html>"""

PAYMENT_PAGE = """<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>TaskNet payments</title><style>body{font-family:Arial,sans-serif;background:#f4f7fb;color:#17233c;margin:0;padding:28px}.wrap{max-width:760px;margin:auto;background:white;padding:28px;border-radius:16px;box-shadow:0 8px 28px #182b4a12}h1{margin-top:0}.task{border:1px solid #dce5f1;border-radius:12px;padding:16px;margin:12px 0;display:flex;gap:12px;align-items:center;justify-content:space-between;flex-wrap:wrap}.muted{color:#5b6780;line-height:1.55}.btn{border:0;border-radius:8px;background:#1769e0;color:#fff;padding:11px 16px;font-weight:700;cursor:pointer}.pill{display:inline-block;background:#fff4d9;color:#775400;padding:5px 9px;border-radius:99px;font-size:12px;font-weight:bold}.back{color:#1769e0}</style></head><body><main class='wrap'><a class='back' href='/hire.html'>← Back to Hire</a><h1>TaskNet secure payments</h1><p class='muted'>Choose a sample task to see the checkout flow. Prices are server-defined and TaskNet's commission is calculated on the server.</p><p class='pill'>Payments stay in test mode until you configure provider accounts</p>{% for key,task in tasks.items() %}<section class='task'><div><strong>{{task.name}}</strong><p class='muted'>Total: £{{'%.2f' % (task.amount_pence/100)}} · TaskNet commission (10%): £{{'%.2f' % (task.amount_pence/1000)}} · Worker share (90%): £{{'%.2f' % (task.amount_pence*0.9/100)}}</p></div><form method='post' action='/payments/stripe/checkout'><input type='hidden' name='task_id' value='{{key}}'><input type='hidden' name='csrf_token' value='{{csrf}}'><button class='btn' type='submit'>Pay by card (Stripe)</button></form></section>{% endfor %}<h2>PayPal</h2><p class='muted'>PayPal marketplace payments are not enabled in this build. TaskNet must be approved for PayPal's platform/partner solution before live marketplace split-fees and seller payouts can be enabled. Do not accept real payments through a placeholder button.</p><p class='muted'>The Stripe route requires a Stripe Connect account, a connected worker account ID, and API keys in environment variables. Use test credentials first.</p></main></body></html>"""


def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_db() as connection:
        connection.execute(
            """CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE COLLATE NOCASE,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )"""
        )
        connection.execute("""CREATE TABLE IF NOT EXISTS worker_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE,
            service TEXT NOT NULL,
            rate REAL NOT NULL,
            area TEXT NOT NULL,
            bio TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )""")


def csrf_token():
    token = session.get("csrf_token")
    if not token:
        token = secrets.token_urlsafe(32)
        session["csrf_token"] = token
    return token


def check_csrf():
    submitted = request.form.get("csrf_token", "")
    stored = session.get("csrf_token", "")
    if not submitted or not stored or not secrets.compare_digest(submitted, stored):
        abort(400, description="Your form expired. Please refresh the page and try again.")


def account_badge():
    user_id = session.get("user_id")
    if not user_id:
        return ""
    with get_db() as connection:
        user = connection.execute("SELECT name FROM users WHERE id = ?", (user_id,)).fetchone()
    if not user:
        session.clear()
        return ""
    name = str(escape(user["name"]))
    return ('<a class="tasknet-account-badge" href="/profile.html" aria-label="Open profile">'
            '<span class="tasknet-account-avatar">' + name[:1].upper() + '</span>'
            '<span class="tasknet-account-copy"><strong>' + name + '</strong>'
            '<span class="tasknet-account-rating">☆☆☆☆☆ <small>Not rated yet</small></span>'
            '</span></a>')


BADGE_CSS = """<style>
.tasknet-account-badge{display:inline-flex;align-items:center;gap:9px;margin-left:12px;padding:7px 11px;border:1px solid #dbe5f4;border-radius:12px;background:#fff;color:#17233c;text-decoration:none;white-space:nowrap;box-shadow:0 3px 12px rgba(25,45,90,.08);font:inherit;line-height:1.2}
.tasknet-account-badge:hover{border-color:#1769e0}.tasknet-account-avatar{display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;flex:0 0 32px;border-radius:50%;background:#1769e0;color:#fff;font-weight:800;text-transform:uppercase}.tasknet-account-copy{display:flex;flex-direction:column;gap:4px;min-width:0}.tasknet-account-copy strong{max-width:150px;overflow:hidden;text-overflow:ellipsis;font-size:13px}.tasknet-account-rating{font-size:12px;color:#e6a817;letter-spacing:1px}.tasknet-account-rating small{font-size:10px;letter-spacing:0;color:#66738c}@media(max-width:850px){.tasknet-account-badge{margin:8px 0 0}}
</style>"""


def render_page(filename):
    html = (BASE_DIR / filename).read_text(encoding="utf-8")
    if filename in {"login.html", "signup.html"}:
        html = html.replace("__TASKNET_CSRF_TOKEN__", str(escape(csrf_token())))
    badge = account_badge()
    if badge:
        # Hide the logged-out Login / Sign Up navigation links for authenticated users.
        auth_nav_css = """<style>
        a[href$="login.html"], a[href$="signup.html"] { display: none !important; }
        .nav-actions:has(a[href$="login.html"]),
        .nav-actions:has(a[href$="signup.html"]),
        .header-signup:has(a[href$="signup.html"]) { display: none !important; }
        </style>"""
        html = html.replace("</head>", BADGE_CSS + auth_nav_css + "\n</head>", 1)
        match = re.search(r"</nav>", html, re.IGNORECASE)
        if match:
            html = html[:match.end()] + "\n" + badge + html[match.end():]
        else:
            match = re.search(r"</header>", html, re.IGNORECASE)
            if match:
                html = html[:match.start()] + badge + html[match.start():]
    html = html.replace("</head>", '<style id="tasknet-age-gate-css">\n#tasknet-age-gate{position:fixed;inset:0;z-index:2147483647;display:flex;align-items:center;justify-content:center;padding:20px;background:rgba(12,20,35,.82);font-family:inherit;overflow:auto}\n#tasknet-age-gate .age-card{box-sizing:border-box;width:min(100%,440px);padding:30px;border-radius:18px;background:#fff;color:#17233c;text-align:center;box-shadow:0 20px 70px rgba(0,0,0,.3)}\n#tasknet-age-gate h2{margin:0 0 12px;font-size:25px}#tasknet-age-gate p{margin:0 0 22px;line-height:1.5}\n#tasknet-age-gate .age-actions{display:flex;flex-direction:column;gap:10px}#tasknet-age-gate button{padding:13px 16px;border:0;border-radius:9px;background:#1769e0;color:#fff;font:inherit;font-weight:700;cursor:pointer}#tasknet-age-gate .age-no{background:#e9edf4;color:#17233c}#tasknet-age-gate .age-error{margin-top:16px;padding:12px;border-radius:8px;background:#fff0f0;color:#a11;font-weight:700}\n</style>\n<script id="tasknet-age-gate-script">(function(){\'use strict\';var K=\'tasknet_age_13_or_over\';try{if(sessionStorage.getItem(K)===\'yes\')return;}catch(e){}function show(){if(document.getElementById(\'tasknet-age-gate\'))return;var o=document.createElement(\'div\');o.id=\'tasknet-age-gate\';o.setAttribute(\'role\',\'dialog\');o.setAttribute(\'aria-modal\',\'true\');o.innerHTML=\'<div class="age-card"><h2>Before you continue</h2><p>Are you 13 years old or above?</p><div class="age-actions"><button type="button" class="age-yes">Yes, I’m 13 or above</button><button type="button" class="age-no">No, I’m under 13</button></div><div class="age-error" hidden>You have to be 13 or above to use this website.</div></div>\';document.body.appendChild(o);document.documentElement.style.overflow=\'hidden\';o.querySelector(\'.age-yes\').onclick=function(){try{sessionStorage.setItem(K,\'yes\')}catch(e){}o.remove();document.documentElement.style.overflow=\'\'};o.querySelector(\'.age-no\').onclick=function(){o.querySelector(\'.age-error\').hidden=false;o.querySelector(\'.age-actions\').hidden=true};}if(document.readyState===\'loading\')document.addEventListener(\'DOMContentLoaded\',show,{once:true});else show();})();</script>' + "\n</head>", 1)
    return app.response_class(html, mimetype="text/html")


def get_user_id(email):
    with get_db() as connection:
        row = connection.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
    return row["id"] if row else None


@app.route("/")
def home():
    if session.get("user_id"):
        return redirect(url_for("profile"))
    return render_page("index.html")


@app.route("/signup.html", methods=["GET", "POST"])
def signup():
    if session.get("user_id"):
        return redirect(url_for("profile"))
    if request.method == "GET":
        return render_page("signup.html")

    check_csrf()
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    confirm_password = request.form.get("confirm_password", "")

    if len(name) < 2 or len(name) > 80:
        return redirect(url_for("signup", error="name"))
    if len(email) > 254 or "@" not in email:
        return redirect(url_for("signup", error="email"))
    if len(password) < 12:
        return redirect(url_for("signup", error="password"))
    if password != confirm_password:
        return redirect(url_for("signup", error="match"))

    try:
        with get_db() as connection:
            connection.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                (name, email, generate_password_hash(password)),
            )
    except sqlite3.IntegrityError:
        return redirect(url_for("signup", error="exists"))

    session.clear()
    session["user_id"] = get_user_id(email)
    session["csrf_token"] = secrets.token_urlsafe(32)
    return redirect(url_for("profile"))


@app.route("/login.html", methods=["GET", "POST"])
def login():
    if session.get("user_id"):
        return redirect(url_for("profile"))
    if request.method == "GET":
        return render_page("login.html")

    check_csrf()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    with get_db() as connection:
        user = connection.execute(
            "SELECT id, password_hash FROM users WHERE email = ?", (email,)
        ).fetchone()

    if not user or not check_password_hash(user["password_hash"], password):
        return redirect(url_for("login", error="invalid"))

    session.clear()
    session["user_id"] = user["id"]
    session["csrf_token"] = secrets.token_urlsafe(32)
    return redirect(url_for("profile"))


@app.route("/profile.html")
def profile():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login"))

    with get_db() as connection:
        user = connection.execute(
            "SELECT name, email, created_at FROM users WHERE id = ?", (user_id,)
        ).fetchone()

    if not user:
        session.clear()
        return redirect(url_for("login"))

    html = (BASE_DIR / "profile.html").read_text(encoding="utf-8")
    html = html.replace("__TASKNET_USER_NAME__", str(escape(user["name"])))
    html = html.replace("__TASKNET_USER_EMAIL__", str(escape(user["email"])))
    html = html.replace("__TASKNET_MEMBER_SINCE__", str(escape(user["created_at"])))
    html = html.replace("__TASKNET_CSRF_TOKEN__", str(escape(csrf_token())))
    badge = account_badge()
    if badge:
        html = html.replace("</head>", BADGE_CSS + "\n</head>", 1)
        match = re.search(r"</nav>", html, re.IGNORECASE)
        if match:
            html = html[:match.end()] + "\n" + badge + html[match.end():]
    html = html.replace("</head>", '<style id="tasknet-age-gate-css">\n#tasknet-age-gate{position:fixed;inset:0;z-index:2147483647;display:flex;align-items:center;justify-content:center;padding:20px;background:rgba(12,20,35,.82);font-family:inherit;overflow:auto}\n#tasknet-age-gate .age-card{box-sizing:border-box;width:min(100%,440px);padding:30px;border-radius:18px;background:#fff;color:#17233c;text-align:center;box-shadow:0 20px 70px rgba(0,0,0,.3)}\n#tasknet-age-gate h2{margin:0 0 12px;font-size:25px}#tasknet-age-gate p{margin:0 0 22px;line-height:1.5}\n#tasknet-age-gate .age-actions{display:flex;flex-direction:column;gap:10px}#tasknet-age-gate button{padding:13px 16px;border:0;border-radius:9px;background:#1769e0;color:#fff;font:inherit;font-weight:700;cursor:pointer}#tasknet-age-gate .age-no{background:#e9edf4;color:#17233c}#tasknet-age-gate .age-error{margin-top:16px;padding:12px;border-radius:8px;background:#fff0f0;color:#a11;font-weight:700}\n</style>\n<script id="tasknet-age-gate-script">(function(){\'use strict\';var K=\'tasknet_age_13_or_over\';try{if(sessionStorage.getItem(K)===\'yes\')return;}catch(e){}function show(){if(document.getElementById(\'tasknet-age-gate\'))return;var o=document.createElement(\'div\');o.id=\'tasknet-age-gate\';o.setAttribute(\'role\',\'dialog\');o.setAttribute(\'aria-modal\',\'true\');o.innerHTML=\'<div class="age-card"><h2>Before you continue</h2><p>Are you 13 years old or above?</p><div class="age-actions"><button type="button" class="age-yes">Yes, I’m 13 or above</button><button type="button" class="age-no">No, I’m under 13</button></div><div class="age-error" hidden>You have to be 13 or above to use this website.</div></div>\';document.body.appendChild(o);document.documentElement.style.overflow=\'hidden\';o.querySelector(\'.age-yes\').onclick=function(){try{sessionStorage.setItem(K,\'yes\')}catch(e){}o.remove();document.documentElement.style.overflow=\'\'};o.querySelector(\'.age-no\').onclick=function(){o.querySelector(\'.age-error\').hidden=false;o.querySelector(\'.age-actions\').hidden=true};}if(document.readyState===\'loading\')document.addEventListener(\'DOMContentLoaded\',show,{once:true});else show();})();</script>' + "\n</head>", 1)
    return app.response_class(html, mimetype="text/html")



@app.route("/workers")
def workers_page():
    service = request.args.get("service", "").strip()
    area = request.args.get("area", "").strip()
    services = ["Car washing", "Pet care", "Gardening", "Cleaning", "Errands", "Other tasks"]
    sql = "SELECT wp.*, u.name FROM worker_profiles wp JOIN users u ON u.id=wp.user_id WHERE 1=1"
    params = []
    if service:
        sql += " AND wp.service = ?"
        params.append(service)
    if area:
        sql += " AND lower(wp.area) LIKE ?"
        params.append("%" + area.lower() + "%")
    sql += " ORDER BY wp.created_at DESC"
    with get_db() as connection:
        matches = connection.execute(sql, params).fetchall()
    return render_template_string(WORKERS_PAGE, workers=matches, service=service, area=area, services=services)

@app.route("/worker/profile", methods=["GET", "POST"])
def worker_profile():
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("login", next="/worker/profile"))
    services = ["Car washing", "Pet care", "Gardening", "Cleaning", "Errands", "Other tasks"]
    if request.method == "POST":
        check_csrf()
        service = request.form.get("service", "").strip()
        area = request.form.get("area", "").strip()
        bio = request.form.get("bio", "").strip()
        try:
            rate = float(request.form.get("rate", ""))
        except ValueError:
            abort(400, "Enter a valid hourly rate")
        if service not in services or not (1 <= rate <= 200) or not area or len(area) > 100 or not bio or len(bio) > 500:
            abort(400, "Please check the profile fields and try again")
        with get_db() as connection:
            connection.execute("""INSERT INTO worker_profiles (user_id, service, rate, area, bio)
                VALUES (?, ?, ?, ?, ?) ON CONFLICT(user_id) DO UPDATE SET
                service=excluded.service, rate=excluded.rate, area=excluded.area, bio=excluded.bio""",
                (user_id, service, rate, area, bio))
        return redirect(url_for("workers_page"), code=303)
    return render_template_string(WORKER_PROFILE_PAGE, services=services, csrf=csrf_token())

@app.route("/hire/continue", methods=["POST"])
def hire_continue():
    check_csrf()
    abort(503, "Booking and live availability are not enabled yet. No payment was taken.")

@app.route("/payments.html")
def payments_page():
    return render_template_string(PAYMENT_PAGE, tasks=TASK_CATALOG, csrf=csrf_token())


@app.route("/payments/stripe/checkout", methods=["POST"])
def stripe_checkout():
    if not session.get("user_id"):
        return redirect(url_for("login"))
    check_csrf_if_present()
    task = TASK_CATALOG.get(request.form.get("task_id", ""))
    if not task:
        abort(400, "Unknown task")
    secret = os.environ.get("STRIPE_SECRET_KEY", "")
    connected_account = os.environ.get("STRIPE_CONNECTED_ACCOUNT_ID", "")
    if not secret or not connected_account:
        return ("Stripe is not configured yet. Set STRIPE_SECRET_KEY (test key) and "
                "STRIPE_CONNECTED_ACCOUNT_ID for the worker's connected account, then restart TaskNet. "
                "No payment was taken.", 503, {"Content-Type": "text/plain; charset=utf-8"})
    try:
        import stripe
    except ImportError:
        return ("Stripe SDK is missing. Run: py -m pip install stripe", 503)
    stripe.api_key = secret
    amount = int(task["amount_pence"])
    fee = amount // 10  # 10% platform commission, in pence; rounded down to a whole penny.
    base_url = request.url_root.rstrip("/")
    try:
        checkout = stripe.checkout.Session.create(
            mode="payment",
            line_items=[{"price_data": {"currency": "gbp", "product_data": {"name": task["name"]}, "unit_amount": amount}, "quantity": 1}],
            payment_intent_data={"application_fee_amount": fee, "transfer_data": {"destination": connected_account}},
            success_url=base_url + "/payments/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=base_url + "/payments/cancel",
            metadata={"task_id": request.form.get("task_id"), "platform_fee_pence": str(fee)},
        )
    except Exception:
        app.logger.exception("Stripe Checkout session creation failed")
        return ("Checkout could not be started. Check your Stripe test configuration. No payment was taken.", 502)
    return redirect(checkout.url, code=303)


def check_csrf_if_present():
    # Payment forms should carry CSRF tokens in production; reject requests without a session token.
    token = request.form.get("csrf_token", "")
    expected = session.get("csrf_token", "")
    if not token or not expected or not secrets.compare_digest(token, expected):
        abort(400, "Invalid or missing CSRF token. Refresh the page and try again.")


@app.route("/payments/success")
def payment_success():
    return "Payment provider returned success. Confirm the payment server-side using Stripe webhooks before marking a task paid.", 200


@app.route("/payments/cancel")
def payment_cancel():
    return "Checkout was cancelled. No completed payment was recorded.", 200


@app.route("/logout", methods=["POST"])
def logout():
    check_csrf()
    session.clear()
    return redirect(url_for("home"))


@app.route("/<path:page>")
def serve_page(page):
    if page in PAGES and page not in {"login.html", "signup.html"}:
        return render_page(page)
    return "Page not found", 404


init_db()

if __name__ == "__main__":
    app.run(debug=True)

import sqlite3
from getpass import getpass
from pathlib import Path
from werkzeug.security import generate_password_hash

DATABASE = Path(__file__).resolve().parent / "tasknet.db"


def main():
    if not DATABASE.exists():
        print("TaskNet database was not found. Check this file is beside app.py.")
        return

    email = input("Enter your TaskNet account email: ").strip().lower()

    if not email or "@" not in email:
        print("Please enter a valid email address.")
        return

    with sqlite3.connect(DATABASE) as db:
        user = db.execute(
            "SELECT id, name FROM users WHERE email = ? COLLATE NOCASE",
            (email,)
        ).fetchone()

        if user is None:
            print("No TaskNet account was found with that email.")
            return

        print(f"Account found for: {user[1]}")

        password = getpass("Enter your new password (minimum 12 characters): ")
        confirmation = getpass("Confirm your new password: ")

        if len(password) < 12:
            print("Password must be at least 12 characters.")
            return

        if password != confirmation:
            print("The passwords do not match.")
            return

        password_hash = generate_password_hash(password)

        db.execute(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (password_hash, user[0])
        )

    print("Password updated successfully! You can now log in to TaskNet.")


if __name__ == "__main__":
    main()
