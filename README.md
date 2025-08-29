# 🏥 Hospital Management System (Streamlit + SQLite)

This is a simple hospital management system built with **Streamlit** for the web interface and **SQLite** as the database.  
It supports **doctor login**, **receptionist login**, patient records, and **encrypted health data** using the `cryptography` library.

---

## 🚀 Features
- Receptionist can register and manage patients.
- Doctors can view only their department’s patients.
- Patient health records are stored in **encrypted form**.
- Role-based access (Doctor / Receptionist).
- Simple, clean UI with Streamlit.

---

## 📦 Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/KALKI7777/Encryption-based-Patient-Data-Monitering-System.git
cd hospital-management
```

### 2. Create Virtual Environment (Recommended)
Create and activate a Python virtual environment:

**Windows (PowerShell):**
```bash
python -m venv env
.\env\Scripts\activate
```

**Linux / MacOS:**
```bash
python3 -m venv env
source env/bin/activate
```

---

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

---

### 4. Setup the Database
Run the setup script once to initialize the database:

```bash
python setup_db.py
```

This will create a fresh **hospital.db** with:
- 3 doctors  
- 1 receptionist  
- 3 sample patients  

---

### 5. Setup the secret key
Run the setup script once to initialize the secret.key file:

```bash
python secret.py
```

### 6. Run the Application
```bash
streamlit run app.py
```

---

## 🔑 Default Login Credentials

| Role         | Username | Password | Department   |
|--------------|----------|----------|--------------|
| Doctor       | smith    | 1234     | Cardiology   |
| Doctor       | brown    | 1234     | Neurology    |
| Doctor       | john     | 1234     | Orthopedic   |
| Receptionist | recep    | 1234     | Reception    |

---

## 📂 Project Structure
```
📁 hospital-management
 ┣ 📄 app.py          # Main Streamlit app
 ┣ 📄 setup_db.py     # Script to create and seed database
 ┣ 📄 requirements.txt # Dependencies
 ┣ 📄 hospital.db      # SQLite database (created after setup)
 ┣ 📄 secret.py       # Script to create secret.key file
 ┗ 📄 README.txt      # Project instructions
```

---

## 🛡️ Notes
- All patient health data is encrypted using **Fernet (AES-128)** before saving into the database.  
- Passwords for doctors/receptionist are currently stored as plain text for simplicity (can be upgraded to hashed).  
- Only install dependencies inside a **virtual environment** to avoid conflicts.

---


