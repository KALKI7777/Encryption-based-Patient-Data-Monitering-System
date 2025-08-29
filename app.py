import streamlit as st
import sqlite3
from typing import Tuple
from cryptography.fernet import Fernet

DB_NAME = "hospital.db"

# ------------------------------
# Encryption / Decryption (Fernet)
# ------------------------------
with open("secret.key", "rb") as f:
    _KEY = f.read()
fernet = Fernet(_KEY)

def encrypt_data(problem: str, treatment: str) -> str:
    data = f"Problem: {problem}||Treatment: {treatment}"
    return fernet.encrypt(data.encode()).decode()

def decrypt_data(enc_data: str) -> str:
    try:
        return fernet.decrypt(enc_data.encode()).decode()
    except Exception:
        return "❌ Error decrypting data"

def extract_problem_treatment(enc_data: str) -> Tuple[str, str]:
    raw = decrypt_data(enc_data).strip()
    problem, treatment = "", ""

    if "||" in raw:  # New format
        parts = {}
        for item in raw.split("||"):
            if ": " in item:
                k, v = item.split(": ", 1)
                parts[k.strip()] = v.strip()
        problem = parts.get("Problem", "")
        treatment = parts.get("Treatment", "")
    else:  # Legacy fallback
        for s in raw.split(","):
            s = s.strip()
            if s.lower().startswith("problem:"):
                problem = s.split(":", 1)[1].strip()
            elif s.lower().startswith("treatment:"):
                treatment = s.split(":", 1)[1].strip()

    return problem, treatment

# ------------------------------
# Database helpers
# ------------------------------
def get_connection():
    return sqlite3.connect(DB_NAME)

def ensure_schema():
    conn = get_connection()
    cur = conn.cursor()

    # Patients
    cur.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER,
            department TEXT,
            encrypted_data TEXT,
            notes TEXT DEFAULT '',
            status TEXT DEFAULT 'Under Treatment'
        )
    """)

    # Doctors
    cur.execute("""
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            department TEXT,
            name TEXT,
            role TEXT
        )
    """)

    conn.commit()
    conn.close()

# ------------------------------
# Auth
# ------------------------------
def get_user(username, password):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM doctors WHERE username=? AND password=?", (username, password))
    user = cur.fetchone()
    conn.close()
    return user

# ------------------------------
# Patient CRUD
# ------------------------------
def add_patient(name, age, department, problem, treatment):
    conn = get_connection()
    cur = conn.cursor()
    encrypted = encrypt_data(problem, treatment)
    cur.execute(
        "INSERT INTO patients (name, age, department, encrypted_data, notes, status) VALUES (?, ?, ?, ?, ?, ?)",
        (name, age, department, encrypted, "", "Under Treatment")
    )
    conn.commit()
    conn.close()

def get_patients():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name, age, department, encrypted_data, notes, status FROM patients")
    patients = cur.fetchall()
    conn.close()
    return patients

def update_patient(pid, name, age, problem, treatment):
    department = detect_department(problem)
    encrypted = encrypt_data(problem, treatment)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE patients SET name=?, age=?, department=?, encrypted_data=?, status=? WHERE id=?",
        (name, age, department, encrypted, "Under Treatment", pid)
    )
    conn.commit()
    conn.close()
    return department

def delete_patient(pid):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM patients WHERE id=?", (pid,))
    conn.commit()
    conn.close()

def add_doctor_note(pid, note):
    if not note.strip():
        return
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT notes FROM patients WHERE id=?", (pid,))
    row = cur.fetchone()
    existing = (row[0] if row and row[0] else "").strip()
    updated_notes = (existing + ("\n" if existing else "") + f"[{timestamp}] {note}").strip()
    cur.execute("UPDATE patients SET notes=? WHERE id=?", (updated_notes, pid))
    conn.commit()
    conn.close()

def set_discharge(pid):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE patients SET status='Discharged' WHERE id=?", (pid,))
    conn.commit()
    conn.close()

# ------------------------------
# Auto department detection
# ------------------------------
def detect_department(problem: str) -> str:
    problem = (problem or "").lower()
    if any(word in problem for word in ["chest", "heart", "bp", "pressure"]):
        return "Cardiology"
    elif any(word in problem for word in ["head", "seizure", "brain", "memory", "stroke"]):
        return "Neurology"
    elif any(word in problem for word in ["fracture", "bone", "knee", "joint", "orthopedic"]):
        return "Orthopedic"
    else:
        return "General"

# ------------------------------
# Session state init
# ------------------------------
if "user" not in st.session_state:
    st.session_state["user"] = None
if "role" not in st.session_state:
    st.session_state["role"] = None

# ------------------------------
# Login page
# ------------------------------
def login():
    st.title("🏥 Hospital Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = get_user(username, password)

        if user:
            st.session_state["user"] = user
            st.session_state["role"] = user[5]  # role column
            st.success("✅ Login successful!")
            st.rerun()
        else:
            st.error("❌ Invalid credentials")

# ------------------------------
# Dashboard for doctors
# ------------------------------
def doctor_dashboard():
    st.title(f"👨‍⚕️ Welcome Dr. {st.session_state['user'][4]}")  # name
    department = st.session_state["user"][3]  # department

    st.subheader(f"📋 Patients in {department} Department")
    colf1, colf2 = st.columns([2, 1])
    with colf1:
        search = st.text_input("🔍 Search patients (by name)")
    with colf2:
        show_discharged = st.checkbox("Show discharged", value=False)

    patients = get_patients()

    filtered = []
    for pid, name, age, dept, enc_data, notes, status in patients:
        if dept != department:
            continue
        if search and search.lower() not in name.lower():
            continue
        if not show_discharged and status == "Discharged":
            continue
        filtered.append((pid, name, age, dept, enc_data, notes, status))

    if not filtered:
        st.info("No patients match your filters.")
        return

    for pid, name, age, dept, enc_data, notes, status in filtered:
        problem, treatment = extract_problem_treatment(enc_data)
        header = f"🧑 {name} • Age: {age} • Status: {status}"
        with st.expander(header):
            st.write(f"**Department:** {dept}")
            st.info(f"**Problem:** {problem}\n\n**Treatment:** {treatment}")
            if notes:
                st.write("**Existing Notes:**")
                st.code(notes)

            note = st.text_area(f"💊 Add Notes/Prescription for {name}", key=f"note_{pid}")
            cols = st.columns([1, 1, 1])
            if cols[0].button("Save Note", key=f"savenote_{pid}"):
                add_doctor_note(pid, note)
                st.success("✅ Note saved!")
                st.rerun()

            disabled = (status == "Discharged")
            if cols[1].button("🏥 Discharge", key=f"discharge_{pid}", disabled=disabled):
                set_discharge(pid)
                st.success(f"✅ {name} marked as Discharged.")
                st.rerun()

# ------------------------------
# Dashboard for receptionist
# ------------------------------
def receptionist_dashboard():
    st.title("👩‍💼 Receptionist Dashboard")

    # Add Patient
    st.subheader("➕ Add New Patient")
    with st.form("add_patient_form", clear_on_submit=True):
        name = st.text_input("Name")
        age = st.number_input("Age", 0, 120)
        problem = st.text_input("Problem")
        treatment = st.text_input("Treatment")
        submitted = st.form_submit_button("Save Patient")
        if submitted:
            auto_department = detect_department(problem)
            add_patient(name, age, auto_department, problem, treatment)
            st.success(f"✅ Patient added and routed to **{auto_department}** department!")

    # Search & Manage Patients
    st.subheader("🔧 Manage Patients")
    col1, col2 = st.columns([2, 1])
    with col1:
        search = st.text_input("Search patients (by name)")
    with col2:
        status_filter = st.selectbox("Status", ["All", "Under Treatment", "Discharged"], index=0)

    patients = get_patients()

    def status_matches(s: str) -> bool:
        if status_filter == "All":
            return True
        return s == status_filter

    for pid, name, age, dept, enc_data, notes, status in patients:
        if search and search.lower() not in name.lower():
            continue
        if not status_matches(status):
            continue

        problem, treatment = extract_problem_treatment(enc_data)
        with st.expander(f"🧑 {name} • Age: {age} • Dept: {dept} • Status: {status}"):
            st.write("**Current Details**")
            st.info(f"**Problem:** {problem}\n\n**Treatment:** {treatment}")
            if notes:
                st.write("**Doctor Notes (read-only):**")
                st.code(notes)

            st.markdown("---")
            st.write("### ✏️ Update Patient (auto re-routes department)")
            new_name = st.text_input("Name", value=name, key=f"n_{pid}")
            new_age = st.number_input("Age", 0, 120, value=age, key=f"a_{pid}")
            new_problem = st.text_input("Problem", value=problem, key=f"p_{pid}")
            new_treatment = st.text_input("Treatment", value=treatment, key=f"t_{pid}")

            ucol1, ucol2, ucol3 = st.columns([1, 1, 1])
            if ucol1.button("Update", key=f"u_{pid}"):
                new_dept = update_patient(pid, new_name, new_age, new_problem, new_treatment)
                st.success(f"✅ Patient updated and moved to **{new_dept}** department!")
                st.rerun()

            if ucol2.button("Delete", key=f"d_{pid}"):
                delete_patient(pid)
                st.warning("🗑️ Patient deleted!")
                st.rerun()

# ------------------------------
# Main App
# ------------------------------
def main():
    ensure_schema()

    if st.session_state["user"] is None:
        login()
    else:
        role = st.session_state["role"]
        if role == "doctor":
            doctor_dashboard()
        elif role == "receptionist":
            receptionist_dashboard()
        else:
            st.error("❌ Unknown role")

        if st.button("Logout"):
            st.session_state["user"] = None
            st.session_state["role"] = None
            st.rerun()

if __name__ == "__main__":
    main()
