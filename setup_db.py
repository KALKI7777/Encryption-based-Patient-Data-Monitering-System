import sqlite3, base64

# -----------------------------
# Helper function for encryption
# -----------------------------
def encrypt(data: str) -> str:
    return base64.b64encode(data.encode()).decode()

# -----------------------------
# Connect & reset DB
# -----------------------------
conn = sqlite3.connect("hospital.db")
cur = conn.cursor()

# Drop old tables
cur.execute("DROP TABLE IF EXISTS doctors")
cur.execute("DROP TABLE IF EXISTS patients")

# -----------------------------
# Create doctors table
# -----------------------------
cur.execute("""
CREATE TABLE doctors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    department TEXT,
    name TEXT,
    role TEXT
)
""")

# -----------------------------
# Create patients table
# -----------------------------
cur.execute("""
CREATE TABLE patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age INTEGER,
    department TEXT,
    encrypted_data TEXT,
    notes TEXT DEFAULT '',
    status TEXT DEFAULT 'Under Treatment'
)
""")

# -----------------------------
# Insert doctors & receptionist
# -----------------------------
doctors = [
    ("smith", "1234", "Cardiology", "Dr. Smith", "doctor"),
    ("brown", "1234", "Neurology", "Dr. Brown", "doctor"),
    ("john", "1234", "Orthopedic", "Dr. John", "doctor"),
    ("recep", "1234", "Reception", "Alice", "receptionist")
]

cur.executemany(
    "INSERT INTO doctors (username, password, department, name, role) VALUES (?, ?, ?, ?, ?)",
    doctors
)

# -----------------------------
# Insert sample patients
# -----------------------------
patients = [
    ("Michael", 50, "Cardiology", encrypt("Problem: chest pain, Treatment: BP tablets"), "", "Under Treatment"),
    ("Sophia", 28, "Neurology", encrypt("Problem: frequent headaches, Treatment: MRI + medication"), "", "Under Treatment"),
    ("David", 40, "Orthopedic", encrypt("Problem: broken leg, Treatment: plaster cast"), "", "Discharged"),
]

cur.executemany(
    "INSERT INTO patients (name, age, department, encrypted_data, notes, status) VALUES (?, ?, ?, ?, ?, ?)",
    patients
)

# -----------------------------
# Save & Close
# -----------------------------
conn.commit()
conn.close()

print("✅ New hospital.db created successfully with sample data!")
