import streamlit as st
import sqlite3
import hashlib
import json
import csv
import io
import math
import random
import copy
from datetime import datetime, date
from contextlib import contextmanager
from collections import defaultdict

DB_PATH = "bgris.db"

UI_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Barlow:wght@300;400;500;600;700&display=swap');

:root {
    --bg-primary: #141414;
    --bg-secondary: #1f1f1f;
    --bg-card: #2a2a2a;
    --bg-card-hover: #333333;
    --accent: #e50914;
    --accent-hover: #f40612;
    --accent-dim: #b20710;
    --text-primary: #ffffff;
    --text-secondary: #b3b3b3;
    --text-muted: #6d6d6e;
    --border: #333333;
    --success: #2ecc71;
    --warning: #f39c12;
    --danger: #e74c3c;
    --info: #3498db;
    --low-risk: #27ae60;
    --medium-risk: #e67e22;
    --high-risk: #c0392b;
}

html, body, [class*="css"] {
    background-color: var(--bg-primary) !important;
    color: var(--text-primary) !important;
    font-family: 'Barlow', sans-serif !important;
}

.stApp {
    background-color: var(--bg-primary) !important;
}

[data-testid="stSidebar"] {
    display: none !important;
}

.stTextInput input, .stTextArea textarea, .stSelectbox select {
    background-color: #333 !important;
    color: #fff !important;
    border: 1px solid #555 !important;
    border-radius: 4px !important;
}

.stButton > button {
    background-color: var(--accent) !important;
    color: white !important;
    border: none !important;
    border-radius: 4px !important;
    font-weight: 700 !important;
    font-family: 'Barlow', sans-serif !important;
    letter-spacing: 1px !important;
    transition: all 0.2s !important;
    padding: 8px 20px !important;
}

.stButton > button:hover {
    background-color: var(--accent-hover) !important;
    transform: scale(1.03) !important;
}

.stSlider > div > div > div {
    background-color: var(--accent) !important;
}

div[data-testid="metric-container"] {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    padding: 16px !important;
}

.stTabs [data-baseweb="tab"] {
    background-color: transparent !important;
    color: var(--text-secondary) !important;
    border-bottom: 2px solid transparent !important;
    font-weight: 600 !important;
}

.stTabs [aria-selected="true"] {
    color: var(--text-primary) !important;
    border-bottom: 2px solid var(--accent) !important;
}

.stExpander {
    background-color: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
}

.stExpander > div > div {
    background-color: var(--bg-card) !important;
}

.stForm {
    background-color: var(--bg-card) !important;
    border-radius: 8px !important;
    padding: 16px !important;
}

label, .stMarkdown p, .stText {
    color: var(--text-secondary) !important;
}

h1, h2, h3 {
    color: var(--text-primary) !important;
    font-family: 'Bebas Neue', sans-serif !important;
    letter-spacing: 2px !important;
}

hr {
    border-color: var(--border) !important;
}

.stDownloadButton > button {
    background-color: #333 !important;
    border: 1px solid var(--accent) !important;
    color: var(--accent) !important;
}

div[data-testid="stDataFrame"] {
    background-color: var(--bg-card) !important;
}

.stRadio > div {
    background-color: transparent !important;
}

.stCheckbox > label {
    color: var(--text-secondary) !important;
}

div[data-baseweb="select"] > div {
    background-color: #333 !important;
    border-color: #555 !important;
    color: #fff !important;
}

[data-testid="stNumberInput"] input {
    background-color: #333 !important;
    color: #fff !important;
    border-color: #555 !important;
}

.stProgress > div > div {
    background-color: var(--accent) !important;
}

.stAlert {
    border-radius: 6px !important;
}
</style>
"""

CARD_CSS = """
<style>
.bgris-hero {
    background: linear-gradient(135deg, #0a0a0a 0%, #1a0000 50%, #0a0a0a 100%);
    padding: 60px 40px;
    text-align: center;
    border-bottom: 2px solid #e50914;
    margin-bottom: 30px;
    position: relative;
    overflow: hidden;
}
.bgris-hero::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle at 60% 40%, rgba(229,9,20,0.08) 0%, transparent 60%);
    pointer-events: none;
}
.hero-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 72px;
    letter-spacing: 8px;
    color: #ffffff;
    margin: 0;
    text-shadow: 0 0 40px rgba(229,9,20,0.4);
    line-height: 1;
}
.hero-subtitle {
    font-family: 'Barlow', sans-serif;
    font-size: 16px;
    letter-spacing: 4px;
    color: #b3b3b3;
    text-transform: uppercase;
    margin-top: 10px;
}
.hero-accent {
    color: #e50914;
}
.stat-card {
    background: linear-gradient(145deg, #2a2a2a, #1f1f1f);
    border: 1px solid #333;
    border-radius: 10px;
    padding: 24px 20px;
    text-align: center;
    margin: 6px 0;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}
.stat-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: #e50914;
}
.stat-card:hover {
    border-color: #e50914;
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(229,9,20,0.2);
}
.stat-value {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 52px;
    color: #ffffff;
    line-height: 1;
    margin: 0;
}
.stat-label {
    font-family: 'Barlow', sans-serif;
    font-size: 11px;
    color: #b3b3b3;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-top: 6px;
}
.stat-delta {
    font-size: 13px;
    margin-top: 8px;
    font-weight: 600;
}
.barcode-card {
    background: linear-gradient(145deg, #2a2a2a, #1e1e1e);
    border: 1px solid #333;
    border-radius: 10px;
    padding: 20px;
    margin: 10px 0;
    transition: all 0.3s;
    cursor: pointer;
}
.barcode-card:hover {
    border-color: #e50914;
    box-shadow: 0 4px 20px rgba(229,9,20,0.15);
    transform: scale(1.01);
}
.barcode-value {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 22px;
    letter-spacing: 3px;
    color: #e50914;
}
.badge {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
}
.badge-compliant { background: rgba(46,204,113,0.15); color: #2ecc71; border: 1px solid #2ecc71; }
.badge-violation { background: rgba(231,76,60,0.15); color: #e74c3c; border: 1px solid #e74c3c; }
.badge-reconstructed { background: rgba(52,152,219,0.15); color: #3498db; border: 1px solid #3498db; }
.badge-unreadable { background: rgba(108,117,125,0.2); color: #aaa; border: 1px solid #555; }
.badge-high { background: rgba(192,57,43,0.2); color: #e74c3c; border: 1px solid #c0392b; }
.badge-medium { background: rgba(230,126,34,0.2); color: #e67e22; border: 1px solid #e67e22; }
.badge-low { background: rgba(39,174,96,0.2); color: #2ecc71; border: 1px solid #27ae60; }
.risk-bar-wrap {
    background: #1a1a1a;
    border-radius: 20px;
    overflow: hidden;
    height: 8px;
    margin-top: 6px;
}
.risk-bar-fill {
    height: 100%;
    border-radius: 20px;
    transition: width 0.6s ease;
}
.section-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 28px;
    letter-spacing: 3px;
    color: #ffffff;
    border-left: 4px solid #e50914;
    padding-left: 14px;
    margin: 24px 0 16px 0;
}
.nav-bar {
    background: rgba(20,20,20,0.97);
    border-bottom: 1px solid #333;
    padding: 12px 30px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: sticky;
    top: 0;
    z-index: 100;
    backdrop-filter: blur(10px);
}
.nav-brand {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 28px;
    color: #e50914;
    letter-spacing: 4px;
}
.nav-user {
    font-family: 'Barlow', sans-serif;
    font-size: 13px;
    color: #b3b3b3;
    background: #2a2a2a;
    border: 1px solid #444;
    padding: 4px 14px;
    border-radius: 4px;
}
.nav-role-badge {
    display: inline-block;
    background: rgba(229,9,20,0.15);
    border: 1px solid #e50914;
    color: #e50914;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    padding: 2px 8px;
    border-radius: 3px;
    margin-left: 8px;
}
.login-container {
    min-height: 100vh;
    background: linear-gradient(160deg, #0a0a0a 0%, #1a0000 40%, #0d0d0d 100%);
    display: flex;
    align-items: center;
    justify-content: center;
}
.login-card {
    background: rgba(30,30,30,0.97);
    border: 1px solid #333;
    border-radius: 12px;
    padding: 48px 44px;
    width: 100%;
    max-width: 460px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.7), 0 0 0 1px rgba(229,9,20,0.1);
}
.rule-card {
    background: linear-gradient(145deg, #252525, #1e1e1e);
    border: 1px solid #333;
    border-radius: 8px;
    padding: 16px 20px;
    margin: 8px 0;
    transition: all 0.2s;
}
.rule-card:hover {
    border-color: #555;
    background: #2a2a2a;
}
.rule-active { border-left: 3px solid #2ecc71; }
.rule-inactive { border-left: 3px solid #555; }
.chart-container {
    background: linear-gradient(145deg, #242424, #1c1c1c);
    border: 1px solid #333;
    border-radius: 10px;
    padding: 24px;
    margin: 10px 0;
}
.audit-row {
    background: #222;
    border: 1px solid #2e2e2e;
    border-radius: 6px;
    padding: 12px 16px;
    margin: 6px 0;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.audit-action {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 14px;
    letter-spacing: 1px;
    color: #e50914;
}
.audit-meta {
    font-size: 11px;
    color: #777;
}
.progress-ring {
    width: 80px;
    height: 80px;
}
.confidence-chip {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #1e1e1e;
    border: 1px solid #3a3a3a;
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 12px;
    color: #b3b3b3;
}
</style>
"""

def inject_css():
    st.markdown(UI_CSS, unsafe_allow_html=True)
    st.markdown(CARD_CSS, unsafe_allow_html=True)

@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def init_db():
    with get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                full_name TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS batches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                created_by INTEGER,
                status TEXT DEFAULT 'Processing',
                batch_limit INTEGER DEFAULT 100,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                batch_id INTEGER,
                filename TEXT NOT NULL,
                file_size INTEGER DEFAULT 0,
                status TEXT DEFAULT 'Uploaded',
                preprocessed INTEGER DEFAULT 0,
                preprocessing_options TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(batch_id) REFERENCES batches(id)
            );
            CREATE TABLE IF NOT EXISTS barcodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image_id INTEGER,
                barcode_value TEXT,
                barcode_type TEXT DEFAULT 'EAN-13',
                confidence_score REAL DEFAULT 1.0,
                is_reconstructed INTEGER DEFAULT 0,
                is_unreadable INTEGER DEFAULT 0,
                status TEXT DEFAULT 'Decoded',
                compliance_status TEXT DEFAULT 'Pending',
                risk_score REAL DEFAULT 0.0,
                risk_level TEXT DEFAULT 'Low',
                decision TEXT DEFAULT 'Pending',
                decision_rationale TEXT,
                review_notes TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(image_id) REFERENCES images(id)
            );
            CREATE TABLE IF NOT EXISTS compliance_rules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rule_id TEXT UNIQUE NOT NULL,
                rule_name TEXT NOT NULL,
                description TEXT,
                category TEXT DEFAULT 'General',
                severity_weight REAL DEFAULT 0.5,
                is_active INTEGER DEFAULT 1,
                rule_order INTEGER DEFAULT 1,
                rule_logic TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS compliance_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                barcode_id INTEGER,
                rule_id INTEGER,
                passed INTEGER DEFAULT 1,
                violation_detail TEXT,
                evaluated_at TEXT NOT NULL,
                FOREIGN KEY(barcode_id) REFERENCES barcodes(id),
                FOREIGN KEY(rule_id) REFERENCES compliance_rules(id)
            );
            CREATE TABLE IF NOT EXISTS risk_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                param_name TEXT UNIQUE NOT NULL,
                param_value REAL NOT NULL,
                description TEXT,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                action TEXT NOT NULL,
                entity_type TEXT,
                entity_id INTEGER,
                details TEXT,
                logged_at TEXT NOT NULL
            );
        """)
        if not conn.execute("SELECT id FROM users WHERE username='admin'").fetchone():
            now = datetime.now().isoformat()
            conn.execute("INSERT INTO users(username,password_hash,role,full_name,is_active,created_at) VALUES(?,?,?,?,1,?)",
                ("admin", hash_pw("admin@bgris"), "System Administrator", "System Admin", now))
        if not conn.execute("SELECT id FROM compliance_rules LIMIT 1").fetchone():
            now = datetime.now().isoformat()
            rules = [
                ("R001","Expiration Date Check","Validates product expiration date encoded in barcode","Expiration",0.9,1,1,"expiry_check"),
                ("R002","Recall Status Check","Checks if barcode matches recall registry","Safety",1.0,1,2,"recall_check"),
                ("R003","Regional Restriction","Validates regional compliance codes","Regional",0.7,1,3,"region_check"),
                ("R004","Barcode Format Integrity","Validates barcode structure and checksum","Format",0.6,1,4,"format_check"),
                ("R005","Label Placement Rule","Checks correct label positioning metadata","Placement",0.5,1,5,"placement_check"),
                ("R006","Minimum Confidence Threshold","Ensures reconstruction confidence meets threshold","Quality",0.8,1,6,"confidence_check"),
            ]
            for r in rules:
                conn.execute("INSERT INTO compliance_rules(rule_id,rule_name,description,category,severity_weight,is_active,rule_order,rule_logic,created_at,updated_at) VALUES(?,?,?,?,?,?,?,?,?,?)",
                    (r[0],r[1],r[2],r[3],r[4],r[5],r[6],r[7],now,now))
        if not conn.execute("SELECT id FROM risk_config LIMIT 1").fetchone():
            now = datetime.now().isoformat()
            params = [
                ("violation_weight", 0.6, "Weight assigned to rule violations"),
                ("confidence_weight", 0.4, "Weight assigned to reconstruction confidence"),
                ("high_risk_threshold", 0.7, "Score above which risk is High"),
                ("medium_risk_threshold", 0.4, "Score above which risk is Medium"),
                ("reconstruction_penalty", 0.2, "Extra risk added for reconstructed barcodes"),
            ]
            for p in params:
                conn.execute("INSERT INTO risk_config(param_name,param_value,description,updated_at) VALUES(?,?,?,?)",
                    (p[0],p[1],p[2],now))

def log_audit(conn, user_id, username, action, entity_type=None, entity_id=None, details=None):
    conn.execute("INSERT INTO audit_logs(user_id,username,action,entity_type,entity_id,details,logged_at) VALUES(?,?,?,?,?,?,?)",
        (user_id, username, action, entity_type, entity_id, details, datetime.now().isoformat()))

def get_risk_params(conn):
    rows = conn.execute("SELECT param_name, param_value FROM risk_config").fetchall()
    return {r["param_name"]: r["param_value"] for r in rows}

def compute_risk_score(conn, barcode_id):
    params = get_risk_params(conn)
    results = conn.execute("SELECT passed, r.severity_weight FROM compliance_results cr JOIN compliance_rules r ON cr.rule_id=r.id WHERE cr.barcode_id=?", (barcode_id,)).fetchall()
    bc = conn.execute("SELECT confidence_score, is_reconstructed FROM barcodes WHERE id=?", (barcode_id,)).fetchone()
    if not bc:
        return 0.0, "Low"
    violation_score = 0.0
    total_weight = 0.0
    for r in results:
        total_weight += r["severity_weight"]
        if not r["passed"]:
            violation_score += r["severity_weight"]
    vw = params.get("violation_weight", 0.6)
    cw = params.get("confidence_weight", 0.4)
    conf_penalty = (1.0 - bc["confidence_score"]) if bc["confidence_score"] else 0.5
    recon_penalty = params.get("reconstruction_penalty", 0.2) if bc["is_reconstructed"] else 0.0
    v_component = (violation_score / max(total_weight, 1.0)) * vw if results else 0.0
    c_component = conf_penalty * cw
    score = min(v_component + c_component + recon_penalty, 1.0)
    high_t = params.get("high_risk_threshold", 0.7)
    med_t = params.get("medium_risk_threshold", 0.4)
    level = "High" if score >= high_t else ("Medium" if score >= med_t else "Low")
    return round(score, 3), level

def evaluate_compliance_rules(conn, barcode_id, user_id, username):
    bc = conn.execute("SELECT * FROM barcodes WHERE id=?", (barcode_id,)).fetchone()
    if not bc:
        return
    rules = conn.execute("SELECT * FROM compliance_rules WHERE is_active=1 ORDER BY rule_order").fetchall()
    conn.execute("DELETE FROM compliance_results WHERE barcode_id=?", (barcode_id,))
    now = datetime.now().isoformat()
    value = bc["barcode_value"] or ""
    for rule in rules:
        logic = rule["rule_logic"]
        passed = 1
        detail = None
        if logic == "expiry_check":
            passed = 1 if len(value) >= 8 else 0
            detail = None if passed else "Barcode too short to contain expiry data"
        elif logic == "recall_check":
            recall_prefix = ["999", "000", "BAD"]
            passed = 0 if any(value.startswith(p) for p in recall_prefix) else 1
            detail = "Barcode matches recall registry prefix" if not passed else None
        elif logic == "region_check":
            passed = 1 if value and value[0].isdigit() else 0
            detail = None if passed else "Regional code mismatch"
        elif logic == "format_check":
            passed = 1 if value and value.isalnum() and len(value) >= 6 else 0
            detail = None if passed else "Invalid barcode format or too short"
        elif logic == "placement_check":
            passed = 1 if len(value) <= 20 else 0
            detail = "Barcode exceeds placement length limit" if not passed else None
        elif logic == "confidence_check":
            threshold = 0.6
            passed = 1 if bc["confidence_score"] >= threshold else 0
            detail = f"Confidence {bc['confidence_score']:.2f} below threshold {threshold}" if not passed else None
        conn.execute("INSERT INTO compliance_results(barcode_id,rule_id,passed,violation_detail,evaluated_at) VALUES(?,?,?,?,?)",
            (barcode_id, rule["id"], passed, detail, now))
    score, level = compute_risk_score(conn, barcode_id)
    violations = conn.execute("SELECT COUNT(*) as c FROM compliance_results WHERE barcode_id=? AND passed=0", (barcode_id,)).fetchone()["c"]
    comp_status = "Compliant" if violations == 0 else "Violation"
    conn.execute("UPDATE barcodes SET compliance_status=?,risk_score=?,risk_level=? WHERE id=?",
        (comp_status, score, level, barcode_id))
    log_audit(conn, user_id, username, "COMPLIANCE_EVALUATED", "Barcode", barcode_id, f"Status:{comp_status} Risk:{score}")

def generate_barcode_value(barcode_type="EAN-13"):
    if barcode_type == "EAN-13":
        digits = [str(random.randint(0,9)) for _ in range(12)]
        total = sum(int(d) * (1 if i%2==0 else 3) for i, d in enumerate(digits))
        check = (10 - (total % 10)) % 10
        return "".join(digits) + str(check)
    elif barcode_type == "QR":
        chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        return "QR-" + "".join(random.choices(chars, k=10))
    elif barcode_type == "CODE128":
        chars = "0123456789ABCDEF"
        return "C128-" + "".join(random.choices(chars, k=12))
    elif barcode_type == "UPC-A":
        digits = [str(random.randint(0,9)) for _ in range(11)]
        total = sum(int(d) * (3 if i%2==0 else 1) for i, d in enumerate(digits))
        check = (10 - (total % 10)) % 10
        return "".join(digits) + str(check)
    return "BC" + str(random.randint(100000, 999999))

def login_register_page():
    inject_css()
    st.markdown("""
    <div style="min-height:100vh;background:linear-gradient(160deg,#0a0a0a 0%,#1a0000 45%,#0d0d0d 100%);display:flex;flex-direction:column;align-items:center;justify-content:center;padding:40px 20px;">
        <div style="text-align:center;margin-bottom:40px;">
            <div style="font-family:'Bebas Neue',sans-serif;font-size:80px;letter-spacing:10px;color:#e50914;text-shadow:0 0 50px rgba(229,9,20,0.5);line-height:1;">BGRIS</div>
            <div style="font-family:'Barlow',sans-serif;font-size:13px;letter-spacing:6px;color:#777;text-transform:uppercase;margin-top:4px;">Barcode Governance &amp; Risk Intelligence System</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_l, col_c, col_r = st.columns([1, 1.2, 1])
    with col_c:
        st.markdown("""
        <div style="background:rgba(28,28,28,0.97);border:1px solid #333;border-radius:12px;padding:40px;box-shadow:0 20px 60px rgba(0,0,0,0.8);">
        </div>
        """, unsafe_allow_html=True)
        mode = st.radio("", ["Sign In", "Register"], horizontal=True, label_visibility="collapsed")
        st.markdown("---")
        if mode == "Sign In":
            with st.form("login_form"):
                st.markdown("<div style='font-family:Bebas Neue;font-size:24px;letter-spacing:3px;color:#fff;margin-bottom:16px;'>SIGN IN</div>", unsafe_allow_html=True)
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("SIGN IN", use_container_width=True)
            if submitted:
                if not username or not password:
                    st.error("Enter username and password.")
                    return
                with get_conn() as conn:
                    user = conn.execute("SELECT * FROM users WHERE username=? AND password_hash=?",
                        (username, hash_pw(password))).fetchone()
                    if not user:
                        st.error("Invalid credentials.")
                        return
                    if not user["is_active"]:
                        st.error("Account is deactivated.")
                        return
                    st.session_state["user"] = dict(user)
                    log_audit(conn, user["id"], user["username"], "LOGIN")
                st.success("Signed in.")
                st.rerun()
        else:
            with st.form("reg_form"):
                st.markdown("<div style='font-family:Bebas Neue;font-size:24px;letter-spacing:3px;color:#fff;margin-bottom:16px;'>CREATE ACCOUNT</div>", unsafe_allow_html=True)
                full_name = st.text_input("Full Name")
                reg_username = st.text_input("Username")
                role = st.selectbox("Role", ["Warehouse Operator", "Compliance Analyst", "Operations Manager"])
                reg_password = st.text_input("Password", type="password")
                confirm_pw = st.text_input("Confirm Password", type="password")
                submitted_r = st.form_submit_button("CREATE ACCOUNT", use_container_width=True)
            if submitted_r:
                if not all([full_name, reg_username, reg_password, confirm_pw]):
                    st.error("All fields are required.")
                    return
                if reg_password != confirm_pw:
                    st.error("Passwords do not match.")
                    return
                if len(reg_password) < 6:
                    st.error("Password must be at least 6 characters.")
                    return
                try:
                    with get_conn() as conn:
                        conn.execute("INSERT INTO users(username,password_hash,role,full_name,is_active,created_at) VALUES(?,?,?,?,1,?)",
                            (reg_username, hash_pw(reg_password), role, full_name, datetime.now().isoformat()))
                        log_audit(conn, None, reg_username, "REGISTER")
                    st.success(f"Account created for {full_name}. Please sign in.")
                except sqlite3.IntegrityError:
                    st.error("Username already exists.")

def top_navbar():
    user = st.session_state.get("user", {})
    col1, col2, col3 = st.columns([1, 4, 2])
    with col1:
        st.markdown("<div style='font-family:Bebas Neue;font-size:32px;color:#e50914;letter-spacing:5px;padding-top:6px;'>BGRIS</div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div style='text-align:right;padding-top:4px;'>
            <span style='font-family:Barlow;font-size:13px;color:#b3b3b3;'>{user.get('full_name','User')}</span>
            <span style='display:inline-block;background:rgba(229,9,20,0.15);border:1px solid #e50914;color:#e50914;font-size:10px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;padding:2px 8px;border-radius:3px;margin-left:8px;'>{user.get('role','')}</span>
        </div>
        """, unsafe_allow_html=True)

def page_selector():
    user = st.session_state.get("user", {})
    role = user.get("role", "")
    all_pages = ["Dashboard", "Image Processing", "Compliance & Risk", "Batch Management", "Reports", "Admin Panel", "Profile"]
    if role == "Warehouse Operator":
        pages = ["Dashboard", "Image Processing", "Batch Management", "Profile"]
    elif role == "Compliance Analyst":
        pages = ["Dashboard", "Compliance & Risk", "Batch Management", "Reports", "Profile"]
    elif role == "Operations Manager":
        pages = ["Dashboard", "Batch Management", "Reports", "Compliance & Risk", "Profile"]
    elif role == "System Administrator":
        pages = all_pages
    else:
        pages = all_pages

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    cols = st.columns(len(pages) + 1)
    active = st.session_state.get("active_page", "Dashboard")
    for i, pg in enumerate(pages):
        with cols[i]:
            style = "background:#e50914;color:#fff;border:none;" if pg == active else "background:#1f1f1f;color:#b3b3b3;border:1px solid #333;"
            if st.button(pg, key=f"nav_{pg}", use_container_width=True):
                st.session_state["active_page"] = pg
                st.rerun()
    with cols[-1]:
        if st.button("Sign Out", use_container_width=True):
            st.session_state.clear()
            st.rerun()
    st.markdown("<div style='border-bottom:1px solid #333;margin:10px 0 20px 0;'></div>", unsafe_allow_html=True)
    return st.session_state.get("active_page", "Dashboard")

def dashboard_page():
    user = st.session_state["user"]
    st.markdown("""
    <div class='bgris-hero'>
        <div class='hero-title'>BARCODE <span class='hero-accent'>INTELLIGENCE</span> COMMAND</div>
        <div class='hero-subtitle'>Governance &bull; Risk Scoring &bull; Compliance Analytics</div>
    </div>
    """, unsafe_allow_html=True)

    with get_conn() as conn:
        total_images = conn.execute("SELECT COUNT(*) as c FROM images").fetchone()["c"]
        total_barcodes = conn.execute("SELECT COUNT(*) as c FROM barcodes").fetchone()["c"]
        compliant = conn.execute("SELECT COUNT(*) as c FROM barcodes WHERE compliance_status='Compliant'").fetchone()["c"]
        violations = conn.execute("SELECT COUNT(*) as c FROM barcodes WHERE compliance_status='Violation'").fetchone()["c"]
        high_risk = conn.execute("SELECT COUNT(*) as c FROM barcodes WHERE risk_level='High'").fetchone()["c"]
        reconstructed = conn.execute("SELECT COUNT(*) as c FROM barcodes WHERE is_reconstructed=1").fetchone()["c"]
        total_batches = conn.execute("SELECT COUNT(*) as c FROM batches").fetchone()["c"]
        active_rules = conn.execute("SELECT COUNT(*) as c FROM compliance_rules WHERE is_active=1").fetchone()["c"]
        avg_risk = conn.execute("SELECT AVG(risk_score) as a FROM barcodes WHERE compliance_status != 'Pending'").fetchone()["a"]
        avg_risk = round(avg_risk or 0, 3)
        recent_barcodes = conn.execute(
            "SELECT b.*, i.filename FROM barcodes b LEFT JOIN images i ON b.image_id=i.id ORDER BY b.created_at DESC LIMIT 6"
        ).fetchall()
        risk_dist = conn.execute("SELECT risk_level, COUNT(*) as c FROM barcodes WHERE risk_level IS NOT NULL GROUP BY risk_level").fetchall()
        comp_dist = conn.execute("SELECT compliance_status, COUNT(*) as c FROM barcodes GROUP BY compliance_status").fetchall()

    c1, c2, c3, c4 = st.columns(4)
    metrics = [
        (c1, total_barcodes, "BARCODES ANALYZED", "#e50914"),
        (c2, compliant, "COMPLIANT", "#2ecc71"),
        (c3, violations, "VIOLATIONS", "#e74c3c"),
        (c4, high_risk, "HIGH RISK", "#e67e22"),
    ]
    for col, val, label, color in metrics:
        with col:
            st.markdown(f"""
            <div class='stat-card' style='border-top-color:{color};'>
                <div class='stat-value' style='color:{color};'>{val}</div>
                <div class='stat-label'>{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    c5, c6, c7, c8 = st.columns(4)
    sub_metrics = [
        (c5, total_images, "IMAGES PROCESSED", "#3498db"),
        (c6, reconstructed, "RECONSTRUCTED", "#9b59b6"),
        (c7, total_batches, "BATCHES", "#1abc9c"),
        (c8, active_rules, "ACTIVE RULES", "#f39c12"),
    ]
    for col, val, label, color in sub_metrics:
        with col:
            st.markdown(f"""
            <div class='stat-card' style='border-top-color:{color};'>
                <div class='stat-value' style='color:{color};'>{val}</div>
                <div class='stat-label'>{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.markdown("<div class='section-title'>RISK DISTRIBUTION ANALYTICS</div>", unsafe_allow_html=True)
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        risk_map = {r["risk_level"]: r["c"] for r in risk_dist}
        low_c = risk_map.get("Low", 0)
        med_c = risk_map.get("Medium", 0)
        high_c = risk_map.get("High", 0)
        total_r = max(low_c + med_c + high_c, 1)
        for level, count, color in [("LOW RISK", low_c, "#27ae60"), ("MEDIUM RISK", med_c, "#e67e22"), ("HIGH RISK", high_c, "#c0392b")]:
            pct = round(count / total_r * 100, 1)
            st.markdown(f"""
            <div style='margin:12px 0;'>
                <div style='display:flex;justify-content:space-between;margin-bottom:6px;'>
                    <span style='font-family:Barlow;font-size:12px;color:#b3b3b3;letter-spacing:1px;'>{level}</span>
                    <span style='font-family:Bebas Neue;font-size:16px;color:{color};'>{count} &nbsp; ({pct}%)</span>
                </div>
                <div class='risk-bar-wrap'>
                    <div class='risk-bar-fill' style='width:{pct}%;background:{color};'></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div class='section-title'>COMPLIANCE STATUS BREAKDOWN</div>", unsafe_allow_html=True)
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        comp_map = {c["compliance_status"]: c["c"] for c in comp_dist}
        for status, color in [("Compliant", "#2ecc71"), ("Violation", "#e74c3c"), ("Pending", "#777")]:
            cnt = comp_map.get(status, 0)
            pct = round(cnt / max(total_barcodes, 1) * 100, 1)
            st.markdown(f"""
            <div style='margin:10px 0;'>
                <div style='display:flex;justify-content:space-between;margin-bottom:5px;'>
                    <span style='font-family:Barlow;font-size:12px;color:#b3b3b3;'>{status.upper()}</span>
                    <span style='font-family:Bebas Neue;font-size:16px;color:{color};'>{cnt}</span>
                </div>
                <div class='risk-bar-wrap'>
                    <div class='risk-bar-fill' style='width:{pct}%;background:{color};'></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown("<div class='section-title'>AVERAGE RISK SCORE</div>", unsafe_allow_html=True)
        risk_pct = int(avg_risk * 100)
        risk_color = "#c0392b" if avg_risk >= 0.7 else ("#e67e22" if avg_risk >= 0.4 else "#27ae60")
        circumference = 2 * math.pi * 35
        offset = circumference * (1 - avg_risk)
        st.markdown(f"""
        <div class='chart-container' style='text-align:center;'>
            <svg width='140' height='140' viewBox='0 0 100 100'>
                <circle cx='50' cy='50' r='35' fill='none' stroke='#333' stroke-width='8'/>
                <circle cx='50' cy='50' r='35' fill='none' stroke='{risk_color}' stroke-width='8'
                    stroke-dasharray='{circumference:.1f}' stroke-dashoffset='{offset:.1f}'
                    stroke-linecap='round' transform='rotate(-90 50 50)'/>
                <text x='50' y='46' text-anchor='middle' font-family='Bebas Neue' font-size='18' fill='white'>{risk_pct}%</text>
                <text x='50' y='60' text-anchor='middle' font-family='Barlow' font-size='7' fill='#777'>AVG RISK</text>
            </svg>
            <div style='font-family:Barlow;font-size:11px;color:#777;letter-spacing:2px;margin-top:8px;'>OVERALL RISK INDEX</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div class='section-title'>QUICK SUMMARY</div>", unsafe_allow_html=True)
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)

        with get_conn() as conn:
            total_users = conn.execute("SELECT COUNT(*) as c FROM users WHERE is_active=1").fetchone()["c"]
            avg_conf = conn.execute("SELECT AVG(confidence_score) as a FROM barcodes").fetchone()["a"] or 0
            unreadable = conn.execute("SELECT COUNT(*) as c FROM barcodes WHERE is_unreadable=1").fetchone()["c"]

        for label, val, color in [
            ("Active Users", str(total_users), "#e50914"),
            ("Avg Confidence", f"{avg_conf:.0%}", "#3498db"),
            ("Unreadable", str(unreadable), "#e74c3c")
        ]:
            st.markdown(f"""
            <div style='display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid #2a2a2a;'>
                <span style='font-size:12px;color:#777;font-family:Barlow;'>{label}</span>
                <span style='font-family:Bebas Neue;font-size:18px;color:{color};'>{val}</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    if recent_barcodes:
        st.markdown("<div class='section-title'>RECENTLY ANALYZED BARCODES</div>", unsafe_allow_html=True)
        cols = st.columns(3)
        for i, bc in enumerate(recent_barcodes):
            with cols[i % 3]:
                risk_color_map = {"High": "#e74c3c", "Medium": "#e67e22", "Low": "#2ecc71"}
                rc = risk_color_map.get(bc["risk_level"], "#777")
                comp_badge = "badge-compliant" if bc["compliance_status"] == "Compliant" else ("badge-violation" if bc["compliance_status"] == "Violation" else "badge-unreadable")
                st.markdown(f"""
                <div class='barcode-card'>
                    <div class='barcode-value'>{(bc['barcode_value'] or 'N/A')[:16]}</div>
                    <div style='margin:8px 0;'>
                        <span class='badge {comp_badge}'>{bc['compliance_status']}</span>
                        &nbsp;<span class='badge badge-{"high" if bc["risk_level"]=="High" else ("medium" if bc["risk_level"]=="Medium" else "low")}'>{bc['risk_level']} RISK</span>
                    </div>
                    <div style='display:flex;justify-content:space-between;align-items:center;margin-top:10px;'>
                        <div class='risk-bar-wrap' style='width:70%;'>
                            <div class='risk-bar-fill' style='width:{int(bc["risk_score"]*100)}%;background:{rc};'></div>
                        </div>
                        <span style='font-family:Bebas Neue;font-size:16px;color:{rc};'>{bc["risk_score"]:.2f}</span>
                    </div>
                    <div style='font-size:10px;color:#555;margin-top:6px;'>{bc['filename'] or 'N/A'}</div>
                </div>
                """, unsafe_allow_html=True)

def image_processing_page():
    user = st.session_state["user"]
    st.markdown("<div class='section-title'>IMAGE PROCESSING CENTER</div>", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["Upload & Process", "Barcode Results", "Reconstruction"])

    with tab1:
        col_form, col_info = st.columns([2, 1])
        with col_form:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            with st.form("upload_form"):
                st.markdown("<div style='font-family:Bebas Neue;font-size:20px;letter-spacing:2px;color:#fff;'>UPLOAD PRODUCT IMAGES</div>", unsafe_allow_html=True)
                batch_name = st.text_input("Batch Name (optional)", placeholder="e.g. Warehouse Batch A - May 2026")
                filenames_raw = st.text_area("Image Filenames (one per line)", placeholder="product_001.jpg\nproduct_002.png\n...")
                barcode_type = st.selectbox("Expected Barcode Type", ["EAN-13", "QR", "CODE128", "UPC-A", "Mixed"])
                preprocessing_opts = st.multiselect("Preprocessing Options", ["Rotation Correction", "Noise Reduction", "Contrast Enhancement", "Grayscale Conversion"])
                submit_upload = st.form_submit_button("PROCESS IMAGES", use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_info:
            st.markdown("""
            <div class='chart-container'>
                <div style='font-family:Bebas Neue;font-size:16px;letter-spacing:2px;color:#e50914;margin-bottom:12px;'>SUPPORTED FORMATS</div>
                <div style='font-size:12px;color:#b3b3b3;line-height:2;'>
                    JPG / JPEG<br>PNG<br>BMP<br>TIFF<br>WEBP
                </div>
                <div style='margin-top:16px;font-family:Bebas Neue;font-size:16px;letter-spacing:2px;color:#e50914;'>BARCODE TYPES</div>
                <div style='font-size:12px;color:#b3b3b3;line-height:2;'>
                    EAN-13 &bull; UPC-A<br>QR Code &bull; CODE128<br>Code 39 &bull; DataMatrix
                </div>
            </div>
            """, unsafe_allow_html=True)

        if submit_upload:
            filenames = [f.strip() for f in filenames_raw.strip().split("\n") if f.strip()]
            if not filenames:
                st.error("Enter at least one filename.")
            else:
                with get_conn() as conn:
                    batch_id = None
                    if batch_name or len(filenames) > 1:
                        cur = conn.execute("INSERT INTO batches(name,created_by,status,created_at) VALUES(?,?,?,?)",
                            (batch_name or f"Batch_{datetime.now().strftime('%Y%m%d_%H%M')}", user["id"], "Processing", datetime.now().isoformat()))
                        batch_id = cur.lastrowid
                        log_audit(conn, user["id"], user["username"], "BATCH_CREATED", "Batch", batch_id)
                    now = datetime.now().isoformat()
                    created_images = []
                    for fname in filenames:
                        is_valid = any(fname.lower().endswith(ext) for ext in [".jpg",".jpeg",".png",".bmp",".tiff",".webp"])
                        if not is_valid:
                            st.warning(f"Skipped {fname}: unsupported format.")
                            continue
                        cur2 = conn.execute("INSERT INTO images(batch_id,filename,status,preprocessed,preprocessing_options,created_at) VALUES(?,?,?,?,?,?)",
                            (batch_id, fname, "Preprocessed" if preprocessing_opts else "Uploaded", 1 if preprocessing_opts else 0, json.dumps(preprocessing_opts), now))
                        img_id = cur2.lastrowid
                        created_images.append(img_id)
                        log_audit(conn, user["id"], user["username"], "IMAGE_UPLOADED", "Image", img_id, fname)
                    for img_id in created_images:
                        btype = barcode_type if barcode_type != "Mixed" else random.choice(["EAN-13","QR","CODE128","UPC-A"])
                        conf = round(random.uniform(0.55, 1.0), 3)
                        is_recon = 1 if conf < 0.75 else 0
                        is_unread = 1 if conf < 0.6 else 0
                        bval = generate_barcode_value(btype)
                        if is_unread:
                            bval = bval[:int(len(bval)*0.6)] + "X" * (len(bval) - int(len(bval)*0.6))
                        conn.execute("INSERT INTO barcodes(image_id,barcode_value,barcode_type,confidence_score,is_reconstructed,is_unreadable,status,created_at) VALUES(?,?,?,?,?,?,?,?)",
                            (img_id, bval, btype, conf, is_recon, is_unread, "Reconstructed" if is_recon else "Decoded", now))
                    if batch_id:
                        conn.execute("UPDATE batches SET status='Processed' WHERE id=?", (batch_id,))
                prog = st.progress(0)
                for i in range(100):
                    prog.progress(i+1)
                st.success(f"Processed {len(created_images)} image(s) successfully.")

    with tab2:
        st.markdown("<div class='section-title'>BARCODE DETECTION RESULTS</div>", unsafe_allow_html=True)
        filter_col1, filter_col2 = st.columns(2)
        filt_status = filter_col1.selectbox("Filter by Status", ["All", "Decoded", "Reconstructed", "Unreadable"])
        filt_type = filter_col2.selectbox("Filter by Type", ["All", "EAN-13", "QR", "CODE128", "UPC-A"])
        q = "SELECT b.*, i.filename FROM barcodes b LEFT JOIN images i ON b.image_id=i.id WHERE 1=1"
        params = []
        if filt_status != "All":
            if filt_status == "Unreadable":
                q += " AND b.is_unreadable=1"
            else:
                q += " AND b.status=?"
                params.append(filt_status)
        if filt_type != "All":
            q += " AND b.barcode_type=?"
            params.append(filt_type)
        q += " ORDER BY b.created_at DESC LIMIT 50"
        with get_conn() as conn:
            barcodes = conn.execute(q, params).fetchall()
        if not barcodes:
            st.info("No barcode results found.")
        else:
            for bc in barcodes:
                conf_pct = int(bc["confidence_score"] * 100)
                conf_color = "#27ae60" if conf_pct >= 80 else ("#e67e22" if conf_pct >= 60 else "#e74c3c")
                with st.expander(f"{bc['barcode_value'] or 'UNREADABLE'}  |  {bc['barcode_type']}  |  {bc['status']}"):
                    c1, c2, c3 = st.columns(3)
                    c1.markdown(f"""
                    <div style='font-family:Bebas Neue;font-size:13px;color:#777;letter-spacing:1px;'>BARCODE VALUE</div>
                    <div style='font-family:Bebas Neue;font-size:20px;color:#e50914;letter-spacing:2px;'>{bc['barcode_value'] or 'N/A'}</div>
                    <div style='font-size:11px;color:#555;margin-top:4px;'>Type: {bc['barcode_type']}</div>
                    """, unsafe_allow_html=True)
                    c2.markdown(f"""
                    <div style='font-family:Bebas Neue;font-size:13px;color:#777;letter-spacing:1px;'>CONFIDENCE SCORE</div>
                    <div style='font-family:Bebas Neue;font-size:32px;color:{conf_color};'>{conf_pct}%</div>
                    <div class='risk-bar-wrap'><div class='risk-bar-fill' style='width:{conf_pct}%;background:{conf_color};'></div></div>
                    """, unsafe_allow_html=True)
                    c3.markdown(f"""
                    <div style='font-family:Bebas Neue;font-size:13px;color:#777;letter-spacing:1px;'>FLAGS</div>
                    <div>{'<span class="badge badge-reconstructed">RECONSTRUCTED</span>' if bc["is_reconstructed"] else ''}</div>
                    <div style='margin-top:4px;'>{'<span class="badge badge-unreadable">UNREADABLE</span>' if bc["is_unreadable"] else ''}</div>
                    <div style='font-size:11px;color:#555;margin-top:6px;'>Source: {bc['filename'] or 'N/A'}</div>
                    """, unsafe_allow_html=True)
                    if bc["is_unreadable"] or bc["confidence_score"] < 0.75:
                        if st.button("Flag as Unreadable", key=f"flag_{bc['id']}"):
                            with get_conn() as conn:
                                conn.execute("UPDATE barcodes SET is_unreadable=1,status='Unreadable' WHERE id=?", (bc["id"],))
                                log_audit(conn, user["id"], user["username"], "FLAG_UNREADABLE", "Barcode", bc["id"])
                            st.success("Flagged.")
                            st.rerun()

    with tab3:
        st.markdown("<div class='section-title'>DAMAGED BARCODE RECONSTRUCTION</div>", unsafe_allow_html=True)
        with get_conn() as conn:
            damaged = conn.execute("SELECT b.*, i.filename FROM barcodes b LEFT JOIN images i ON b.image_id=i.id WHERE b.is_reconstructed=1 OR b.is_unreadable=1 ORDER BY b.created_at DESC LIMIT 30").fetchall()
        if not damaged:
            st.info("No damaged barcodes requiring reconstruction.")
        else:
            st.markdown(f"<div style='font-family:Barlow;font-size:13px;color:#b3b3b3;margin-bottom:16px;'>{len(damaged)} barcode(s) eligible for reconstruction</div>", unsafe_allow_html=True)
            for bc in damaged:
                with st.expander(f"{'[UNREADABLE]' if bc['is_unreadable'] else '[RECONSTRUCTED]'}  {bc['barcode_value'] or 'N/A'}  |  Conf: {bc['confidence_score']:.0%}"):
                    c1, c2 = st.columns(2)
                    c1.markdown(f"<div style='font-size:12px;color:#777;'>Original Value: <span style='color:#e50914;font-family:Bebas Neue;'>{bc['barcode_value'] or 'Unknown'}</span></div>", unsafe_allow_html=True)
                    c1.markdown(f"<div style='font-size:12px;color:#777;margin-top:4px;'>Confidence: <span style='color:#3498db;'>{bc['confidence_score']:.0%}</span></div>", unsafe_allow_html=True)
                    if c2.button("Reconstruct", key=f"recon_{bc['id']}"):
                        new_val = generate_barcode_value(bc["barcode_type"])
                        new_conf = round(min(bc["confidence_score"] + random.uniform(0.1, 0.25), 1.0), 3)
                        with get_conn() as conn:
                            conn.execute("UPDATE barcodes SET barcode_value=?,confidence_score=?,is_reconstructed=1,is_unreadable=0,status='Reconstructed',updated_at=? WHERE id=?",
                                (new_val, new_conf, datetime.now().isoformat(), bc["id"]))
                            log_audit(conn, user["id"], user["username"], "RECONSTRUCT", "Barcode", bc["id"], f"NewConf:{new_conf}")
                        st.success(f"Reconstructed: {new_val} (Confidence: {new_conf:.0%})")
                        st.rerun()
                    if bc["confidence_score"] < 0.6:
                        st.markdown("<div style='background:rgba(231,76,60,0.1);border:1px solid #c0392b;border-radius:6px;padding:8px 12px;font-size:12px;color:#e74c3c;margin-top:8px;'>Confidence below acceptable threshold. Manual review recommended.</div>", unsafe_allow_html=True)

def compliance_risk_page():
    user = st.session_state["user"]
    st.markdown("<div class='section-title'>COMPLIANCE AND RISK INTELLIGENCE</div>", unsafe_allow_html=True)
    tab1, tab2, tab3, tab4 = st.tabs(["Evaluate Compliance", "Risk Details", "Decision Paths", "Annotations"])

    with tab1:
        with get_conn() as conn:
            pending = conn.execute("SELECT b.*, i.filename FROM barcodes b LEFT JOIN images i ON b.image_id=i.id WHERE b.compliance_status='Pending' ORDER BY b.created_at DESC LIMIT 30").fetchall()
            evaluated = conn.execute("SELECT b.*, i.filename FROM barcodes b LEFT JOIN images i ON b.image_id=i.id WHERE b.compliance_status!='Pending' ORDER BY b.created_at DESC LIMIT 20").fetchall()

        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown(f"""
            <div class='chart-container'>
                <div style='font-family:Bebas Neue;font-size:18px;color:#fff;letter-spacing:2px;'>PENDING EVALUATION</div>
                <div style='font-family:Bebas Neue;font-size:52px;color:#e50914;'>{len(pending)}</div>
                <div style='font-size:11px;color:#777;letter-spacing:2px;'>BARCODES AWAITING COMPLIANCE CHECK</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("EVALUATE ALL PENDING", use_container_width=True):
                with get_conn() as conn:
                    for bc in pending:
                        evaluate_compliance_rules(conn, bc["id"], user["id"], user["username"])
                st.success(f"Evaluated {len(pending)} barcodes.")
                st.rerun()

        with col2:
            if pending:
                bc_options = {f"{bc['barcode_value'] or 'N/A'} ({bc['filename'] or 'N/A'})": bc["id"] for bc in pending}
                sel = st.selectbox("Select barcode to evaluate individually", list(bc_options.keys()))
                if st.button("Evaluate Selected"):
                    with get_conn() as conn:
                        evaluate_compliance_rules(conn, bc_options[sel], user["id"], user["username"])
                    st.success("Evaluated.")
                    st.rerun()

        st.markdown("<div class='section-title'>RECENTLY EVALUATED</div>", unsafe_allow_html=True)
        for bc in evaluated[:10]:
            risk_color = {"High": "#e74c3c", "Medium": "#e67e22", "Low": "#2ecc71"}.get(bc["risk_level"], "#777")
            with st.expander(f"{bc['barcode_value'] or 'N/A'}  |  {bc['compliance_status']}  |  Risk: {bc['risk_level']}"):
                c1, c2, c3 = st.columns(3)
                c1.markdown(f"<div style='font-size:12px;color:#777;'>Compliance</div><div style='font-family:Bebas Neue;font-size:22px;color:{'#2ecc71' if bc['compliance_status']=='Compliant' else '#e74c3c'};'>{bc['compliance_status']}</div>", unsafe_allow_html=True)
                c2.markdown(f"<div style='font-size:12px;color:#777;'>Risk Score</div><div style='font-family:Bebas Neue;font-size:22px;color:{risk_color};'>{bc['risk_score']:.3f}</div>", unsafe_allow_html=True)
                c3.markdown(f"<div style='font-size:12px;color:#777;'>Confidence</div><div style='font-family:Bebas Neue;font-size:22px;color:#3498db;'>{bc['confidence_score']:.0%}</div>", unsafe_allow_html=True)
                with get_conn() as conn:
                    results = conn.execute("SELECT cr.*, r.rule_name, r.category, r.severity_weight FROM compliance_results cr JOIN compliance_rules r ON cr.rule_id=r.id WHERE cr.barcode_id=?", (bc["id"],)).fetchall()
                for res in results:
                    icon = "PASS" if res["passed"] else "FAIL"
                    color = "#2ecc71" if res["passed"] else "#e74c3c"
                    st.markdown(f"""
                    <div style='background:#1e1e1e;border:1px solid {"#2a3a2a" if res["passed"] else "#3a2a2a"};border-radius:6px;padding:8px 14px;margin:4px 0;display:flex;justify-content:space-between;align-items:center;'>
                        <div>
                            <span style='font-family:Bebas Neue;font-size:13px;color:{color};letter-spacing:1px;'>{icon}</span>
                            <span style='font-size:12px;color:#b3b3b3;margin-left:10px;'>{res['rule_name']}</span>
                            <span style='font-size:10px;color:#555;margin-left:8px;'>[{res['category']}]</span>
                        </div>
                        <span style='font-size:11px;color:#555;'>Weight: {res['severity_weight']}</span>
                    </div>
                    {"<div style='font-size:11px;color:#e74c3c;padding:4px 14px;'>" + res['violation_detail'] + "</div>" if res['violation_detail'] else ""}
                    """, unsafe_allow_html=True)

    with tab2:
        st.markdown("<div class='section-title'>RISK SCORE DETAILS</div>", unsafe_allow_html=True)
        flt = st.selectbox("Filter by Risk Level", ["All", "High", "Medium", "Low"], key="risk_flt")
        q2 = "SELECT b.*, i.filename FROM barcodes b LEFT JOIN images i ON b.image_id=i.id WHERE b.compliance_status != 'Pending'"
        p2 = []
        if flt != "All":
            q2 += " AND b.risk_level=?"
            p2.append(flt)
        q2 += " ORDER BY b.risk_score DESC LIMIT 40"
        with get_conn() as conn:
            risk_list = conn.execute(q2, p2).fetchall()
        for bc in risk_list:
            rc = {"High": "#e74c3c", "Medium": "#e67e22", "Low": "#2ecc71"}.get(bc["risk_level"], "#777")
            st.markdown(f"""
            <div class='barcode-card'>
                <div style='display:flex;justify-content:space-between;align-items:flex-start;'>
                    <div>
                        <div class='barcode-value'>{(bc['barcode_value'] or 'N/A')[:20]}</div>
                        <div style='font-size:11px;color:#555;margin-top:2px;'>{bc['filename'] or 'N/A'} &bull; {bc['barcode_type']}</div>
                    </div>
                    <div style='text-align:right;'>
                        <div style='font-family:Bebas Neue;font-size:28px;color:{rc};'>{bc['risk_score']:.3f}</div>
                        <span class='badge badge-{"high" if bc["risk_level"]=="High" else ("medium" if bc["risk_level"]=="Medium" else "low")}'>{bc["risk_level"]} RISK</span>
                    </div>
                </div>
                <div style='margin-top:10px;'>
                    <div class='risk-bar-wrap'>
                        <div class='risk-bar-fill' style='width:{int(bc["risk_score"]*100)}%;background:{rc};'></div>
                    </div>
                </div>
                <div style='display:flex;gap:8px;margin-top:8px;'>
                    <span class='badge {"badge-compliant" if bc["compliance_status"]=="Compliant" else "badge-violation"}'>{bc['compliance_status']}</span>
                    {'<span class="badge badge-reconstructed">RECONSTRUCTED</span>' if bc['is_reconstructed'] else ''}
                </div>
            </div>
            """, unsafe_allow_html=True)

    with tab3:
        st.markdown("<div class='section-title'>DECISION PATH TRACE</div>", unsafe_allow_html=True)
        with get_conn() as conn:
            all_barcodes = conn.execute("SELECT id, barcode_value FROM barcodes WHERE compliance_status != 'Pending' ORDER BY created_at DESC LIMIT 50").fetchall()
        if all_barcodes:
            opts = {f"[{bc['id']}] {bc['barcode_value'] or 'N/A'}": bc["id"] for bc in all_barcodes}
            sel_bc = st.selectbox("Select Barcode to Trace", list(opts.keys()))
            sel_id = opts[sel_bc]
            with get_conn() as conn:
                bc_data = conn.execute("SELECT * FROM barcodes WHERE id=?", (sel_id,)).fetchone()
                rule_results = conn.execute("SELECT cr.*, r.rule_name, r.category, r.severity_weight, r.rule_logic, r.rule_order FROM compliance_results cr JOIN compliance_rules r ON cr.rule_id=r.id WHERE cr.barcode_id=? ORDER BY r.rule_order", (sel_id,)).fetchall()
            st.markdown(f"""
            <div class='chart-container'>
                <div style='font-family:Bebas Neue;font-size:18px;color:#fff;letter-spacing:2px;margin-bottom:16px;'>TRACE: {bc_data['barcode_value'] or 'N/A'}</div>
            """, unsafe_allow_html=True)
            for i, res in enumerate(rule_results):
                color = "#2ecc71" if res["passed"] else "#e74c3c"
                label = "PASSED" if res["passed"] else "FAILED"
                st.markdown(f"""
                <div style='display:flex;align-items:flex-start;gap:12px;margin:8px 0;'>
                    <div style='display:flex;flex-direction:column;align-items:center;'>
                        <div style='width:32px;height:32px;border-radius:50%;background:{color};display:flex;align-items:center;justify-content:center;font-family:Bebas Neue;font-size:13px;color:white;flex-shrink:0;'>{i+1}</div>
                        {"<div style='width:2px;flex:1;background:#333;margin:4px 0;height:20px;'></div>" if i < len(rule_results)-1 else ""}
                    </div>
                    <div style='background:#1e1e1e;border:1px solid #2e2e2e;border-radius:8px;padding:10px 14px;flex:1;'>
                        <div style='display:flex;justify-content:space-between;align-items:center;'>
                            <span style='font-family:Bebas Neue;font-size:15px;color:#fff;letter-spacing:1px;'>{res['rule_name']}</span>
                            <span style='font-family:Bebas Neue;font-size:13px;color:{color};'>{label}</span>
                        </div>
                        <div style='font-size:11px;color:#555;margin-top:2px;'>Category: {res['category']} &bull; Weight: {res['severity_weight']}</div>
                        {f"<div style='font-size:11px;color:#e74c3c;margin-top:4px;'>{res['violation_detail']}</div>" if res['violation_detail'] else ""}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown(f"""
                <div style='margin-top:16px;padding-top:16px;border-top:1px solid #333;display:flex;justify-content:space-between;'>
                    <div style='font-family:Bebas Neue;font-size:16px;color:#777;'>FINAL OUTCOME</div>
                    <div>
                        <span style='font-family:Bebas Neue;font-size:18px;color:{"#2ecc71" if bc_data["compliance_status"]=="Compliant" else "#e74c3c"};'>{bc_data['compliance_status']}</span>
                        <span style='font-family:Bebas Neue;font-size:18px;color:#777;margin:0 8px;'>|</span>
                        <span style='font-family:Bebas Neue;font-size:18px;color:#e50914;'>RISK SCORE: {bc_data['risk_score']:.3f}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with tab4:
        st.markdown("<div class='section-title'>ANNOTATE COMPLIANCE DECISIONS</div>", unsafe_allow_html=True)
        with get_conn() as conn:
            bc_list = conn.execute("SELECT id, barcode_value FROM barcodes WHERE compliance_status != 'Pending' ORDER BY created_at DESC LIMIT 50").fetchall()
        if bc_list:
            opts2 = {f"[{b['id']}] {b['barcode_value'] or 'N/A'}": b["id"] for b in bc_list}
            sel_ann = st.selectbox("Select Barcode to Annotate", list(opts2.keys()))
            sel_ann_id = opts2[sel_ann]
            with st.form("annotation_form"):
                note = st.text_area("Review Note / Annotation")
                submit_ann = st.form_submit_button("SAVE ANNOTATION")
            if submit_ann:
                if note:
                    with get_conn() as conn:
                        conn.execute("UPDATE barcodes SET review_notes=? WHERE id=?", (note, sel_ann_id))
                        log_audit(conn, user["id"], user["username"], "ANNOTATE", "Barcode", sel_ann_id)
                    st.success("Annotation saved.")
                else:
                    st.error("Note cannot be empty.")

def batch_management_page():
    user = st.session_state["user"]
    st.markdown("<div class='section-title'>BATCH MANAGEMENT CENTER</div>", unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["Batch Overview", "Approve / Reject Actions", "Damage Trends"])

    with tab1:
        with get_conn() as conn:
            batches = conn.execute("SELECT bt.*, u.full_name as created_by_name, (SELECT COUNT(*) FROM images WHERE batch_id=bt.id) as img_count FROM batches bt LEFT JOIN users u ON bt.created_by=u.id ORDER BY bt.created_at DESC").fetchall()
        if not batches:
            st.info("No batches found.")
        else:
            filt_status = st.selectbox("Filter by Status", ["All", "Processing", "Processed", "Archived"])
            for bt in batches:
                if filt_status != "All" and bt["status"] != filt_status:
                    continue
                with st.expander(f"BATCH: {bt['name']}  |  {bt['img_count']} images  |  {bt['status']}"):
                    c1, c2, c3 = st.columns(3)
                    c1.markdown(f"<div style='font-size:11px;color:#777;'>CREATED BY</div><div style='font-family:Bebas Neue;font-size:18px;'>{bt['created_by_name'] or 'N/A'}</div>", unsafe_allow_html=True)
                    c2.markdown(f"<div style='font-size:11px;color:#777;'>IMAGES</div><div style='font-family:Bebas Neue;font-size:18px;color:#3498db;'>{bt['img_count']}</div>", unsafe_allow_html=True)
                    c3.markdown(f"<div style='font-size:11px;color:#777;'>CREATED</div><div style='font-size:12px;color:#b3b3b3;'>{bt['created_at'][:16]}</div>", unsafe_allow_html=True)
                    with get_conn() as conn:
                        bc_stats = conn.execute("""
                            SELECT COUNT(*) as total,
                            SUM(CASE WHEN b.compliance_status='Compliant' THEN 1 ELSE 0 END) as comp,
                            SUM(CASE WHEN b.compliance_status='Violation' THEN 1 ELSE 0 END) as viol,
                            SUM(CASE WHEN b.risk_level='High' THEN 1 ELSE 0 END) as high_r,
                            AVG(b.risk_score) as avg_r
                            FROM barcodes b JOIN images i ON b.image_id=i.id WHERE i.batch_id=?
                        """, (bt["id"],)).fetchone()
                    st.markdown(f"""
                    <div style='display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin-top:12px;'>
                        <div class='stat-card' style='padding:12px;'><div class='stat-value' style='font-size:28px;'>{bc_stats['total']}</div><div class='stat-label'>BARCODES</div></div>
                        <div class='stat-card' style='padding:12px;border-top-color:#2ecc71;'><div class='stat-value' style='font-size:28px;color:#2ecc71;'>{bc_stats['comp'] or 0}</div><div class='stat-label'>COMPLIANT</div></div>
                        <div class='stat-card' style='padding:12px;border-top-color:#e74c3c;'><div class='stat-value' style='font-size:28px;color:#e74c3c;'>{bc_stats['viol'] or 0}</div><div class='stat-label'>VIOLATIONS</div></div>
                        <div class='stat-card' style='padding:12px;border-top-color:#e67e22;'><div class='stat-value' style='font-size:28px;color:#e67e22;'>{bc_stats['high_r'] or 0}</div><div class='stat-label'>HIGH RISK</div></div>
                        <div class='stat-card' style='padding:12px;border-top-color:#9b59b6;'><div class='stat-value' style='font-size:28px;color:#9b59b6;'>{(bc_stats['avg_r'] or 0):.2f}</div><div class='stat-label'>AVG RISK</div></div>
                    </div>
                    """, unsafe_allow_html=True)
                    if bt["status"] != "Archived":
                        if st.button("Archive Batch", key=f"arch_{bt['id']}"):
                            with get_conn() as conn:
                                conn.execute("UPDATE batches SET status='Archived' WHERE id=?", (bt["id"],))
                                log_audit(conn, user["id"], user["username"], "ARCHIVE_BATCH", "Batch", bt["id"])
                            st.success("Archived.")
                            st.rerun()

    with tab2:
        st.markdown("<div class='section-title'>APPROVE / REJECT OPERATIONAL ACTIONS</div>", unsafe_allow_html=True)
        with get_conn() as conn:
            pending_decisions = conn.execute("SELECT b.*, i.filename FROM barcodes b LEFT JOIN images i ON b.image_id=i.id WHERE b.decision='Pending' AND b.compliance_status != 'Pending' ORDER BY b.risk_score DESC LIMIT 30").fetchall()
        if not pending_decisions:
            st.info("No pending operational decisions.")
        else:
            st.markdown(f"<div style='font-family:Barlow;font-size:13px;color:#b3b3b3;margin-bottom:16px;'>{len(pending_decisions)} item(s) awaiting decision</div>", unsafe_allow_html=True)
            for bc in pending_decisions:
                rc = {"High": "#e74c3c", "Medium": "#e67e22", "Low": "#2ecc71"}.get(bc["risk_level"], "#777")
                with st.expander(f"{bc['barcode_value'] or 'N/A'}  |  {bc['compliance_status']}  |  Risk: {bc['risk_level']}  |  Score: {bc['risk_score']:.3f}"):
                    c1, c2 = st.columns([3, 1])
                    c1.markdown(f"""
                    <div style='font-size:12px;color:#777;'>Barcode Value: <span style='color:#e50914;font-family:Bebas Neue;font-size:16px;'>{bc['barcode_value'] or 'N/A'}</span></div>
                    <div style='font-size:12px;color:#777;margin-top:4px;'>Risk Score: <span style='color:{rc};font-weight:700;'>{bc['risk_score']:.3f}</span>  &bull;  Source: {bc['filename'] or 'N/A'}</div>
                    """, unsafe_allow_html=True)
                    with st.form(f"decision_form_{bc['id']}"):
                        rationale = st.text_input("Decision Rationale", key=f"rat_{bc['id']}")
                        dc1, dc2 = st.columns(2)
                        approve = dc1.form_submit_button("APPROVE", use_container_width=True)
                        reject = dc2.form_submit_button("REJECT", use_container_width=True)
                    if approve:
                        with get_conn() as conn:
                            conn.execute("UPDATE barcodes SET decision='Approved',decision_rationale=? WHERE id=?", (rationale, bc["id"]))
                            log_audit(conn, user["id"], user["username"], "APPROVE", "Barcode", bc["id"], rationale)
                        st.success("Approved.")
                        st.rerun()
                    if reject:
                        with get_conn() as conn:
                            conn.execute("UPDATE barcodes SET decision='Rejected',decision_rationale=? WHERE id=?", (rationale, bc["id"]))
                            log_audit(conn, user["id"], user["username"], "REJECT", "Barcode", bc["id"], rationale)
                        st.error("Rejected.")
                        st.rerun()

    with tab3:
        st.markdown("<div class='section-title'>BARCODE DAMAGE AND RECONSTRUCTION TRENDS</div>", unsafe_allow_html=True)
        with get_conn() as conn:
            total_bc = conn.execute("SELECT COUNT(*) as c FROM barcodes").fetchone()["c"]
            recon_bc = conn.execute("SELECT COUNT(*) as c FROM barcodes WHERE is_reconstructed=1").fetchone()["c"]
            unread_bc = conn.execute("SELECT COUNT(*) as c FROM barcodes WHERE is_unreadable=1").fetchone()["c"]
            avg_conf = conn.execute("SELECT AVG(confidence_score) as a FROM barcodes").fetchone()["a"] or 0
            recon_success = conn.execute("SELECT COUNT(*) as c FROM barcodes WHERE is_reconstructed=1 AND is_unreadable=0").fetchone()["c"]
        c1, c2, c3, c4 = st.columns(4)
        for col, val, label, color in [(c1, total_bc, "TOTAL BARCODES", "#fff"), (c2, recon_bc, "RECONSTRUCTED", "#3498db"), (c3, unread_bc, "UNREADABLE", "#e74c3c"), (c4, recon_success, "RECON SUCCESS", "#2ecc71")]:
            with col:
                st.markdown(f"<div class='stat-card' style='border-top-color:{color};'><div class='stat-value' style='color:{color};'>{val}</div><div class='stat-label'>{label}</div></div>", unsafe_allow_html=True)

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.markdown("<div style='font-family:Bebas Neue;font-size:16px;letter-spacing:2px;color:#fff;margin-bottom:14px;'>RECONSTRUCTION SUCCESS RATE</div>", unsafe_allow_html=True)
        success_rate = round(recon_success / max(recon_bc, 1) * 100, 1)
        damage_rate = round(recon_bc / max(total_bc, 1) * 100, 1)
        avg_conf_pct = round(avg_conf * 100, 1)
        for label, val, color in [("Damage Rate", damage_rate, "#e67e22"), ("Reconstruction Success", success_rate, "#2ecc71"), ("Average Confidence", avg_conf_pct, "#3498db")]:
            st.markdown(f"""
            <div style='margin:10px 0;'>
                <div style='display:flex;justify-content:space-between;margin-bottom:5px;'>
                    <span style='font-size:12px;color:#b3b3b3;font-family:Barlow;'>{label}</span>
                    <span style='font-family:Bebas Neue;font-size:16px;color:{color};'>{val}%</span>
                </div>
                <div class='risk-bar-wrap'>
                    <div class='risk-bar-fill' style='width:{val}%;background:{color};'></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

def reports_page():
    user = st.session_state["user"]
    st.markdown("<div class='section-title'>REPORTS AND EXPORT CENTER</div>", unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["Compliance Report", "Risk Report", "Audit Trail"])

    with tab1:
        st.markdown("<div class='section-title'>COMPLIANCE EXPORT</div>", unsafe_allow_html=True)
        with get_conn() as conn:
            data = conn.execute("""
                SELECT b.id, b.barcode_value, b.barcode_type, b.confidence_score,
                       b.is_reconstructed, b.compliance_status, b.risk_score, b.risk_level,
                       b.decision, b.review_notes, b.created_at, i.filename
                FROM barcodes b LEFT JOIN images i ON b.image_id=i.id
                ORDER BY b.created_at DESC
            """).fetchall()

        col1, col2 = st.columns(2)
        comp_count = sum(1 for d in data if d["compliance_status"] == "Compliant")
        viol_count = sum(1 for d in data if d["compliance_status"] == "Violation")
        col1.markdown(f"<div class='chart-container'><div class='stat-value' style='color:#2ecc71;'>{comp_count}</div><div class='stat-label'>COMPLIANT</div></div>", unsafe_allow_html=True)
        col2.markdown(f"<div class='chart-container'><div class='stat-value' style='color:#e74c3c;'>{viol_count}</div><div class='stat-label'>VIOLATIONS</div></div>", unsafe_allow_html=True)

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "Barcode Value", "Type", "Confidence", "Reconstructed", "Compliance Status", "Risk Score", "Risk Level", "Decision", "Notes", "Filename", "Created At"])
        for d in data:
            writer.writerow([d["id"], d["barcode_value"], d["barcode_type"], d["confidence_score"],
                             "Yes" if d["is_reconstructed"] else "No", d["compliance_status"],
                             d["risk_score"], d["risk_level"], d["decision"], d["review_notes"] or "", d["filename"] or "", d["created_at"]])
        st.download_button("EXPORT COMPLIANCE CSV", output.getvalue(), file_name=f"compliance_report_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv", use_container_width=True)

        json_data = [dict(d) for d in data]
        st.download_button("EXPORT COMPLIANCE JSON", json.dumps(json_data, indent=2, default=str), file_name=f"compliance_report_{datetime.now().strftime('%Y%m%d')}.json", mime="application/json", use_container_width=True)

        st.markdown("<div class='section-title'>COMPLIANCE DATA PREVIEW</div>", unsafe_allow_html=True)
        for d in data[:15]:
            rc = {"High": "#e74c3c", "Medium": "#e67e22", "Low": "#2ecc71"}.get(d["risk_level"], "#777")
            cs_color = "#2ecc71" if d["compliance_status"] == "Compliant" else "#e74c3c"
            st.markdown(f"""
            <div class='audit-row'>
                <div>
                    <div style='font-family:Bebas Neue;font-size:15px;color:#e50914;letter-spacing:1px;'>{(d['barcode_value'] or 'N/A')[:20]}</div>
                    <div style='font-size:11px;color:#555;'>{d['filename'] or 'N/A'} &bull; {d['barcode_type']}</div>
                </div>
                <div style='text-align:center;'>
                    <span style='font-family:Bebas Neue;font-size:14px;color:{cs_color};'>{d['compliance_status']}</span>
                </div>
                <div style='text-align:right;'>
                    <div style='font-family:Bebas Neue;font-size:18px;color:{rc};'>{d['risk_score']:.3f}</div>
                    <div style='font-size:10px;color:#555;'>{d['risk_level']} RISK</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    with tab2:
        st.markdown("<div class='section-title'>RISK INTELLIGENCE REPORT</div>", unsafe_allow_html=True)
        with get_conn() as conn:
            risk_data = conn.execute("SELECT b.*, i.filename FROM barcodes b LEFT JOIN images i ON b.image_id=i.id WHERE b.compliance_status != 'Pending' ORDER BY b.risk_score DESC").fetchall()
            batch_runs = conn.execute("SELECT bt.id, bt.name, COUNT(b.id) as total, AVG(b.risk_score) as avg_risk, SUM(CASE WHEN b.risk_level='High' THEN 1 ELSE 0 END) as high_r FROM batches bt LEFT JOIN images i ON i.batch_id=bt.id LEFT JOIN barcodes b ON b.image_id=i.id GROUP BY bt.id ORDER BY bt.created_at DESC LIMIT 10").fetchall()

        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.markdown("<div style='font-family:Bebas Neue;font-size:16px;letter-spacing:2px;color:#fff;margin-bottom:14px;'>BATCH RISK COMPARISON</div>", unsafe_allow_html=True)
        for bt in batch_runs:
            avg_r = bt["avg_risk"] or 0
            rc = "#e74c3c" if avg_r >= 0.7 else ("#e67e22" if avg_r >= 0.4 else "#2ecc71")
            st.markdown(f"""
            <div style='margin:10px 0;'>
                <div style='display:flex;justify-content:space-between;margin-bottom:5px;'>
                    <span style='font-size:12px;color:#b3b3b3;'>{bt['name'][:40]}</span>
                    <span style='font-family:Bebas Neue;font-size:15px;color:{rc};'>{avg_r:.3f} AVG &bull; {bt['high_r'] or 0} HIGH</span>
                </div>
                <div class='risk-bar-wrap'>
                    <div class='risk-bar-fill' style='width:{min(int(avg_r*100),100)}%;background:{rc};'></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        out2 = io.StringIO()
        w2 = csv.writer(out2)
        w2.writerow(["Batch", "Total Barcodes", "Avg Risk", "High Risk Count"])
        for bt in batch_runs:
            w2.writerow([bt["name"], bt["total"] or 0, round(bt["avg_risk"] or 0, 3), bt["high_r"] or 0])
        st.download_button("EXPORT BATCH RISK REPORT", out2.getvalue(), file_name=f"batch_risk_report_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv", use_container_width=True)

    with tab3:
        st.markdown("<div class='section-title'>AUDIT TRAIL</div>", unsafe_allow_html=True)
        with get_conn() as conn:
            logs = conn.execute("SELECT * FROM audit_logs ORDER BY logged_at DESC LIMIT 100").fetchall()
        if not logs:
            st.info("No audit logs.")
        else:
            action_filter = st.selectbox("Filter by Action", ["All"] + list(set(l["action"] for l in logs)))
            for log in logs:
                if action_filter != "All" and log["action"] != action_filter:
                    continue
                action_color_map = {"LOGIN": "#3498db", "COMPLIANCE_EVALUATED": "#2ecc71", "APPROVE": "#27ae60", "REJECT": "#e74c3c", "RECONSTRUCT": "#9b59b6", "ARCHIVE_BATCH": "#e67e22"}
                ac = action_color_map.get(log["action"], "#e50914")
                st.markdown(f"""
                <div class='audit-row'>
                    <div>
                        <div class='audit-action' style='color:{ac};'>{log['action']}</div>
                        <div class='audit-meta'>{log['username'] or 'System'} &bull; {log['entity_type'] or ''} {log['entity_id'] or ''}</div>
                        {f"<div style='font-size:10px;color:#444;margin-top:2px;'>{log['details']}</div>" if log['details'] else ""}
                    </div>
                    <div style='font-size:11px;color:#444;'>{log['logged_at'][:16]}</div>
                </div>
                """, unsafe_allow_html=True)

def admin_panel_page():
    user = st.session_state["user"]
    if user["role"] != "System Administrator":
        st.error("Access restricted to System Administrators.")
        return
    st.markdown("<div class='section-title'>ADMINISTRATION PANEL</div>", unsafe_allow_html=True)
    tab1, tab2, tab3, tab4 = st.tabs(["Compliance Rules", "Risk Parameters", "User Management", "System Config"])

    with tab1:
        st.markdown("<div class='section-title'>COMPLIANCE RULE CONFIGURATION</div>", unsafe_allow_html=True)
        with get_conn() as conn:
            rules = conn.execute("SELECT * FROM compliance_rules ORDER BY rule_order").fetchall()
        for rule in rules:
            status_color = "#2ecc71" if rule["is_active"] else "#555"
            with st.expander(f"{rule['rule_id']} | {rule['rule_name']} | {'ACTIVE' if rule['is_active'] else 'INACTIVE'}"):
                c1, c2, c3 = st.columns(3)
                c1.markdown(f"<div style='font-size:11px;color:#777;'>CATEGORY</div><div style='font-family:Bebas Neue;font-size:16px;color:#e50914;'>{rule['category']}</div>", unsafe_allow_html=True)
                c2.markdown(f"<div style='font-size:11px;color:#777;'>SEVERITY WEIGHT</div><div style='font-family:Bebas Neue;font-size:16px;color:#e67e22;'>{rule['severity_weight']}</div>", unsafe_allow_html=True)
                c3.markdown(f"<div style='font-size:11px;color:#777;'>EXECUTION ORDER</div><div style='font-family:Bebas Neue;font-size:16px;'>{rule['rule_order']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='font-size:12px;color:#777;margin-top:8px;'>{rule['description']}</div>", unsafe_allow_html=True)
                with st.form(f"edit_rule_{rule['id']}"):
                    new_name = st.text_input("Rule Name", value=rule["rule_name"])
                    new_desc = st.text_area("Description", value=rule["description"] or "")
                    new_cat = st.selectbox("Category", ["General", "Expiration", "Safety", "Regional", "Format", "Placement", "Quality"], index=["General", "Expiration", "Safety", "Regional", "Format", "Placement", "Quality"].index(rule["category"]) if rule["category"] in ["General", "Expiration", "Safety", "Regional", "Format", "Placement", "Quality"] else 0)
                    new_weight = st.slider("Severity Weight", 0.1, 1.0, float(rule["severity_weight"]), 0.05)
                    new_order = st.number_input("Rule Order", min_value=1, max_value=20, value=int(rule["rule_order"]))
                    new_active = st.checkbox("Active", value=bool(rule["is_active"]))
                    save_rule = st.form_submit_button("UPDATE RULE")
                if save_rule:
                    with get_conn() as conn:
                        conn.execute("UPDATE compliance_rules SET rule_name=?,description=?,category=?,severity_weight=?,rule_order=?,is_active=?,updated_at=? WHERE id=?",
                            (new_name, new_desc, new_cat, new_weight, new_order, 1 if new_active else 0, datetime.now().isoformat(), rule["id"]))
                        log_audit(conn, user["id"], user["username"], "UPDATE_RULE", "Rule", rule["id"])
                    st.success("Rule updated.")
                    st.rerun()

    with tab2:
        st.markdown("<div class='section-title'>RISK SCORING PARAMETERS</div>", unsafe_allow_html=True)
        with get_conn() as conn:
            params = conn.execute("SELECT * FROM risk_config ORDER BY param_name").fetchall()
        for param in params:
            with st.expander(f"{param['param_name'].replace('_',' ').upper()}  |  Current: {param['param_value']}"):
                st.markdown(f"<div style='font-size:12px;color:#777;margin-bottom:10px;'>{param['description']}</div>", unsafe_allow_html=True)
                with st.form(f"param_form_{param['id']}"):
                    new_val = st.slider("Value", 0.0, 2.0, float(param["param_value"]), 0.05)
                    save_param = st.form_submit_button("UPDATE PARAMETER")
                if save_param:
                    with get_conn() as conn:
                        conn.execute("UPDATE risk_config SET param_value=?,updated_at=? WHERE id=?", (new_val, datetime.now().isoformat(), param["id"]))
                        log_audit(conn, user["id"], user["username"], "UPDATE_RISK_PARAM", "RiskConfig", param["id"])
                    st.success("Parameter updated.")
                    st.rerun()

    with tab3:
        st.markdown("<div class='section-title'>USER ACCOUNT MANAGEMENT</div>", unsafe_allow_html=True)
        tab_ua, tab_uc = st.tabs(["All Users", "Create User"])
        with tab_ua:
            with get_conn() as conn:
                users = conn.execute("SELECT * FROM users ORDER BY created_at DESC").fetchall()
            for u in users:
                with st.expander(f"{u['full_name'] or u['username']}  |  {u['role']}  |  {'ACTIVE' if u['is_active'] else 'INACTIVE'}"):
                    c1, c2 = st.columns(2)
                    c1.markdown(f"<div style='font-size:11px;color:#777;'>USERNAME</div><div style='font-family:Bebas Neue;font-size:16px;color:#e50914;'>{u['username']}</div>", unsafe_allow_html=True)
                    c2.markdown(f"<div style='font-size:11px;color:#777;'>CREATED</div><div style='font-size:12px;color:#b3b3b3;'>{u['created_at'][:10]}</div>", unsafe_allow_html=True)
                    if u["id"] != user["id"]:
                        if u["is_active"]:
                            if st.button("DISABLE ACCOUNT", key=f"dis_{u['id']}"):
                                with get_conn() as conn:
                                    conn.execute("UPDATE users SET is_active=0 WHERE id=?", (u["id"],))
                                    log_audit(conn, user["id"], user["username"], "DISABLE_USER", "User", u["id"])
                                st.success("Account disabled.")
                                st.rerun()
                        else:
                            if st.button("ENABLE ACCOUNT", key=f"en_{u['id']}"):
                                with get_conn() as conn:
                                    conn.execute("UPDATE users SET is_active=1 WHERE id=?", (u["id"],))
                                    log_audit(conn, user["id"], user["username"], "ENABLE_USER", "User", u["id"])
                                st.success("Account enabled.")
                                st.rerun()
        with tab_uc:
            with st.form("create_user_form"):
                new_full = st.text_input("Full Name")
                new_uname = st.text_input("Username")
                new_role = st.selectbox("Role", ["Warehouse Operator", "Compliance Analyst", "Operations Manager", "System Administrator"])
                new_pw = st.text_input("Password", type="password")
                create_submit = st.form_submit_button("CREATE USER")
            if create_submit:
                if not all([new_full, new_uname, new_pw]):
                    st.error("All fields required.")
                else:
                    try:
                        with get_conn() as conn:
                            conn.execute("INSERT INTO users(username,password_hash,role,full_name,is_active,created_at) VALUES(?,?,?,?,1,?)",
                                (new_uname, hash_pw(new_pw), new_role, new_full, datetime.now().isoformat()))
                            log_audit(conn, user["id"], user["username"], "CREATE_USER", "User", None, new_uname)
                        st.success(f"User '{new_uname}' created.")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("Username already exists.")

    with tab4:
        st.markdown("<div class='section-title'>SYSTEM CONFIGURATION</div>", unsafe_allow_html=True)
        with get_conn() as conn:
            batches = conn.execute("SELECT id, name, status FROM batches").fetchall()
        st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
        st.markdown("<div style='font-family:Bebas Neue;font-size:18px;letter-spacing:2px;color:#fff;margin-bottom:12px;'>BATCH PROCESSING LIMITS</div>", unsafe_allow_html=True)
        with st.form("batch_limit_form"):
            default_limit = st.number_input("Default Batch Limit (images per batch)", min_value=10, max_value=10000, value=100)
            save_limits = st.form_submit_button("SAVE CONFIGURATION")
        if save_limits:
            with get_conn() as conn:
                conn.execute("UPDATE batches SET batch_limit=?", (default_limit,))
                log_audit(conn, user["id"], user["username"], "UPDATE_BATCH_LIMIT", "Config", None, str(default_limit))
            st.success("Configuration saved.")
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div class='chart-container' style='margin-top:16px;'>", unsafe_allow_html=True)
        st.markdown("<div style='font-family:Bebas Neue;font-size:18px;letter-spacing:2px;color:#fff;margin-bottom:12px;'>ARCHIVE RECORDS</div>", unsafe_allow_html=True)
        non_archived = [b for b in batches if b["status"] != "Archived"]
        if non_archived:
            batch_opts = {b["name"]: b["id"] for b in non_archived}
            sel_arch = st.selectbox("Select Batch to Archive", list(batch_opts.keys()))
            if st.button("ARCHIVE SELECTED BATCH"):
                with get_conn() as conn:
                    conn.execute("UPDATE batches SET status='Archived' WHERE id=?", (batch_opts[sel_arch],))
                    log_audit(conn, user["id"], user["username"], "ARCHIVE_BATCH", "Batch", batch_opts[sel_arch])
                st.success("Batch archived.")
                st.rerun()
        else:
            st.info("No active batches to archive.")
        st.markdown("</div>", unsafe_allow_html=True)

def profile_page():
    user = st.session_state["user"]
    st.markdown("<div class='section-title'>MY PROFILE</div>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 2])
    with col1:
        initials = "".join(w[0].upper() for w in (user.get("full_name") or user["username"]).split()[:2])
        st.markdown(f"""
        <div class='chart-container' style='text-align:center;'>
            <div style='width:80px;height:80px;border-radius:50%;background:linear-gradient(135deg,#e50914,#7b0000);display:flex;align-items:center;justify-content:center;font-family:Bebas Neue;font-size:32px;color:white;margin:0 auto 16px;'>{initials}</div>
            <div style='font-family:Bebas Neue;font-size:22px;color:#fff;letter-spacing:2px;'>{user.get('full_name') or user['username']}</div>
            <div style='font-size:12px;color:#777;margin-top:4px;'>@{user['username']}</div>
            <div style='display:inline-block;background:rgba(229,9,20,0.15);border:1px solid #e50914;color:#e50914;font-size:10px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;padding:3px 10px;border-radius:3px;margin-top:10px;'>{user['role']}</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        with st.form("change_pw_form"):
            st.markdown("<div style='font-family:Bebas Neue;font-size:20px;letter-spacing:2px;color:#fff;margin-bottom:12px;'>CHANGE PASSWORD</div>", unsafe_allow_html=True)
            curr_pw = st.text_input("Current Password", type="password")
            new_pw = st.text_input("New Password", type="password")
            conf_pw = st.text_input("Confirm New Password", type="password")
            save_pw = st.form_submit_button("UPDATE PASSWORD")
        if save_pw:
            if not all([curr_pw, new_pw, conf_pw]):
                st.error("All fields required.")
            elif new_pw != conf_pw:
                st.error("New passwords do not match.")
            elif len(new_pw) < 6:
                st.error("Password must be at least 6 characters.")
            else:
                with get_conn() as conn:
                    row = conn.execute("SELECT id FROM users WHERE id=? AND password_hash=?", (user["id"], hash_pw(curr_pw))).fetchone()
                    if not row:
                        st.error("Current password is incorrect.")
                    else:
                        conn.execute("UPDATE users SET password_hash=? WHERE id=?", (hash_pw(new_pw), user["id"]))
                        log_audit(conn, user["id"], user["username"], "CHANGE_PASSWORD")
                        st.success("Password updated.")

def main():
    st.set_page_config(page_title="BGRIS", layout="wide", initial_sidebar_state="collapsed")
    init_db()
    inject_css()
    if "user" not in st.session_state:
        login_register_page()
        return
    if "active_page" not in st.session_state:
        st.session_state["active_page"] = "Dashboard"
    top_navbar()
    page = page_selector()
    if page == "Dashboard":
        dashboard_page()
    elif page == "Image Processing":
        image_processing_page()
    elif page == "Compliance & Risk":
        compliance_risk_page()
    elif page == "Batch Management":
        batch_management_page()
    elif page == "Reports":
        reports_page()
    elif page == "Admin Panel":
        admin_panel_page()
    elif page == "Profile":
        profile_page()

if __name__ == "__main__":
    main()