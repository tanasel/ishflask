"""
seed_medical.py
================
Builds the sample ``databases/medical.db`` SQLite database used by the
ishflask teaching API.

Run it once after cloning:

    python3 seed_medical.py

It is safe to run again — the database file is deleted and rebuilt from
scratch every time, so you always get a clean, known data set.

The data is fictional (made-up patients and doctors) and exists only to
demonstrate relational queries. Never put real personal data in here.
"""

import os
import sqlite3

# ---------------------------------------------------------------------------
# Where the database file lives: <this folder>/databases/medical.db
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_DIR = os.path.join(BASE_DIR, "databases")
DB_PATH = os.path.join(DB_DIR, "medical.db")

# ---------------------------------------------------------------------------
# Sample data (fictional)
# ---------------------------------------------------------------------------
DEPARTMENTS = [
    ("Dept1", "Heart Unit"),
    ("Dept2", "Child Unit"),
    ("Dept3", "Bone Unit"),
]

DOCTORS = [
    ("D1", "Dr. Hare",      "Cardiology",          "Dept1"),
    ("D2", "Dr. Tanasel",   "Paediatrics",         "Dept2"),
    ("D3", "Dr. Lira",      "Orthopaedics",        "Dept3"),
    ("D4", "Dr. Okonkwo",   "Cardiac Surgery",     "Dept1"),
    ("D5", "Dr. Fernández", "Neonatal Care",       "Dept2"),
    ("D6", "Dr. Patel",     "Interventional Card", "Dept1"),
    ("D7", "Dr. Nguyen",    "Paediatric Surgery",  "Dept2"),
    ("D8", "Dr. Schmidt",   "Sports Medicine",     "Dept3"),
]

PATIENTS = [
    ("P1",  "Anika",    1988), ("P2",  "Boris",    1972), ("P3",  "Chiamaka", 2015),
    ("P4",  "Delli",    1965), ("P5",  "Bruce",    1990), ("P6",  "Sofia",    1983),
    ("P7",  "Marcus",   2001), ("P8",  "Yuki",     1978), ("P9",  "Fatima",   2010),
    ("P10", "Luca",     1995), ("P11", "Priya",    1969), ("P12", "Kwame",    2018),
    ("P13", "Elena",    1987), ("P14", "Tariq",    1955), ("P15", "Ingrid",   2003),
    ("P16", "Ravi",     1992), ("P17", "Amara",    2012), ("P18", "Jonas",    1948),
    ("P19", "Mei",      1976), ("P20", "Tobias",   2008), ("P21", "Leila",    1999),
    ("P22", "Dimitri",  1961), ("P23", "Nadia",    2016), ("P24", "Samuel",   1984),
    ("P25", "Hana",     1970),
]

TREATMENTS = [
    ("ECG",        50),
    ("Blood Test", 30),
    ("Vaccine",    25),
    ("X-Ray",      80),
    ("Physio",     60),
]

APPOINTMENTS = [
    ("A1", "P1", "D1"),   ("A2", "P2", "D1"),   ("A3", "P3", "D2"),
    ("A4", "P4", "D3"),   ("A5", "P5", "D3"),   ("A6", "P6", "D1"),
    ("A7", "P7", "D2"),   ("A8", "P8", "D4"),   ("A9", "P9", "D5"),
    ("A10", "P10", "D3"), ("A11", "P11", "D1"), ("A12", "P12", "D2"),
    ("A13", "P13", "D6"), ("A14", "P14", "D4"), ("A15", "P15", "D7"),
    ("A16", "P16", "D8"), ("A17", "P17", "D5"), ("A18", "P18", "D1"),
    ("A19", "P19", "D3"), ("A20", "P20", "D2"), ("A21", "P21", "D6"),
    ("A22", "P22", "D4"), ("A23", "P23", "D7"), ("A24", "P24", "D8"),
    ("A25", "P25", "D1"), ("A26", "P1", "D4"),  ("A27", "P2", "D6"),
    ("A28", "P3", "D5"),  ("A29", "P4", "D8"),  ("A30", "P5", "D2"),
    ("A31", "P6", "D7"),  ("A32", "P7", "D3"),  ("A33", "P8", "D1"),
    ("A34", "P9", "D2"),  ("A35", "P10", "D5"), ("A36", "P11", "D8"),
    ("A37", "P12", "D4"), ("A38", "P13", "D3"), ("A39", "P14", "D7"),
    ("A40", "P15", "D1"), ("A41", "P16", "D2"), ("A42", "P17", "D6"),
    ("A43", "P18", "D3"), ("A44", "P19", "D4"), ("A45", "P20", "D5"),
    ("A46", "P21", "D8"), ("A47", "P22", "D1"), ("A48", "P23", "D2"),
    ("A49", "P24", "D3"), ("A50", "P25", "D6"), ("A51", "P1", "D7"),
    ("A52", "P2", "D8"),  ("A53", "P3", "D1"),  ("A54", "P4", "D4"),
    ("A55", "P5", "D6"),  ("A56", "P6", "D3"),  ("A57", "P7", "D8"),
    ("A58", "P8", "D5"),  ("A59", "P9", "D7"),  ("A60", "P10", "D1"),
    ("A61", "P11", "D4"), ("A62", "P12", "D6"), ("A63", "P13", "D2"),
    ("A64", "P14", "D8"), ("A65", "P15", "D3"), ("A66", "P16", "D5"),
    ("A67", "P17", "D1"), ("A68", "P18", "D7"), ("A69", "P19", "D2"),
    ("A70", "P20", "D4"), ("A71", "P21", "D3"), ("A72", "P22", "D6"),
    ("A73", "P23", "D8"), ("A74", "P24", "D1"), ("A75", "P25", "D5"),
    ("A76", "P1", "D2"),  ("A77", "P2", "D3"),  ("A78", "P3", "D7"),
    ("A79", "P4", "D6"),  ("A80", "P5", "D4"),  ("A81", "P6", "D8"),
    ("A82", "P7", "D1"),  ("A83", "P8", "D6"),  ("A84", "P9", "D3"),
    ("A85", "P10", "D7"), ("A86", "P11", "D2"), ("A87", "P12", "D5"),
    ("A88", "P13", "D4"), ("A89", "P14", "D1"), ("A90", "P15", "D6"),
    ("A91", "P16", "D3"), ("A92", "P17", "D8"), ("A93", "P18", "D4"),
    ("A94", "P19", "D5"), ("A95", "P20", "D7"), ("A96", "P21", "D1"),
    ("A97", "P22", "D2"), ("A98", "P23", "D5"), ("A99", "P24", "D6"),
    ("A100", "P25", "D4"),
]

APPOINTMENT_TREATMENTS = [
    ("A1", "ECG"),   ("A1", "Blood Test"), ("A2", "ECG"),
    ("A3", "Blood Test"), ("A3", "Vaccine"), ("A4", "X-Ray"),
    ("A4", "Physio"), ("A5", "Physio"), ("A6", "ECG"),
    ("A6", "Blood Test"), ("A7", "Vaccine"), ("A8", "ECG"),
    ("A8", "Blood Test"), ("A9", "Vaccine"), ("A9", "Blood Test"),
    ("A10", "X-Ray"), ("A11", "ECG"), ("A12", "Vaccine"),
    ("A12", "Blood Test"), ("A13", "ECG"), ("A13", "Physio"),
    ("A14", "Blood Test"), ("A15", "Vaccine"), ("A16", "X-Ray"),
    ("A16", "Physio"), ("A17", "Vaccine"), ("A18", "ECG"),
    ("A18", "Blood Test"), ("A19", "X-Ray"), ("A20", "Vaccine"),
    ("A21", "ECG"), ("A22", "Blood Test"), ("A22", "ECG"),
    ("A23", "Vaccine"), ("A24", "Physio"), ("A24", "X-Ray"),
    ("A25", "ECG"), ("A26", "Blood Test"), ("A26", "ECG"),
    ("A27", "ECG"), ("A28", "Vaccine"), ("A28", "Blood Test"),
    ("A29", "Physio"), ("A30", "Vaccine"), ("A31", "X-Ray"),
    ("A31", "Physio"), ("A32", "X-Ray"), ("A33", "ECG"),
    ("A34", "Blood Test"), ("A35", "Vaccine"), ("A35", "Blood Test"),
    ("A36", "Physio"), ("A37", "Blood Test"), ("A37", "ECG"),
    ("A38", "X-Ray"), ("A39", "Vaccine"), ("A40", "ECG"),
    ("A40", "Blood Test"), ("A41", "Vaccine"), ("A42", "ECG"),
    ("A43", "X-Ray"), ("A43", "Physio"), ("A44", "Blood Test"),
    ("A45", "Vaccine"), ("A45", "Blood Test"), ("A46", "Physio"),
    ("A47", "ECG"), ("A48", "Vaccine"), ("A49", "X-Ray"),
    ("A50", "ECG"), ("A50", "Blood Test"), ("A51", "Vaccine"),
    ("A52", "Physio"), ("A52", "X-Ray"), ("A53", "ECG"),
    ("A54", "Blood Test"), ("A54", "ECG"), ("A55", "ECG"),
    ("A56", "X-Ray"), ("A57", "Physio"), ("A58", "Vaccine"),
    ("A58", "Blood Test"), ("A59", "Vaccine"), ("A60", "ECG"),
    ("A60", "Blood Test"), ("A61", "Blood Test"), ("A62", "ECG"),
    ("A63", "Vaccine"), ("A63", "Blood Test"), ("A64", "Physio"),
    ("A65", "X-Ray"), ("A65", "Physio"), ("A66", "Vaccine"),
    ("A67", "ECG"), ("A68", "Vaccine"), ("A68", "Blood Test"),
    ("A69", "Blood Test"), ("A70", "ECG"), ("A70", "X-Ray"),
    ("A71", "X-Ray"), ("A72", "ECG"), ("A73", "Physio"),
    ("A74", "Blood Test"), ("A74", "ECG"), ("A75", "Vaccine"),
    ("A76", "Blood Test"), ("A77", "X-Ray"), ("A77", "Physio"),
    ("A78", "Vaccine"), ("A79", "ECG"), ("A80", "Blood Test"),
    ("A80", "ECG"), ("A81", "Physio"), ("A82", "ECG"),
    ("A82", "Blood Test"), ("A83", "ECG"), ("A84", "X-Ray"),
    ("A85", "Vaccine"), ("A85", "Blood Test"), ("A86", "ECG"),
    ("A87", "Vaccine"), ("A88", "Blood Test"), ("A88", "X-Ray"),
    ("A89", "ECG"), ("A90", "ECG"), ("A90", "Physio"),
    ("A91", "X-Ray"), ("A92", "Physio"), ("A93", "Blood Test"),
    ("A93", "ECG"), ("A94", "Vaccine"), ("A95", "Vaccine"),
    ("A95", "Blood Test"), ("A96", "ECG"), ("A97", "Blood Test"),
    ("A98", "Vaccine"), ("A98", "Blood Test"), ("A99", "ECG"),
    ("A100", "X-Ray"), ("A100", "Physio"),
]


def build():
    os.makedirs(DB_DIR, exist_ok=True)
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")

    cursor.execute("""
        CREATE TABLE Departments (
            DeptID     TEXT PRIMARY KEY,
            Department TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE Doctors (
            DoctorID       TEXT PRIMARY KEY,
            Doctor         TEXT NOT NULL,
            Specialisation TEXT NOT NULL,
            DeptID         TEXT NOT NULL,
            FOREIGN KEY (DeptID) REFERENCES Departments(DeptID)
        )
    """)
    cursor.execute("""
        CREATE TABLE Patients (
            PatientID TEXT PRIMARY KEY,
            Patient   TEXT NOT NULL,
            DOB       INTEGER NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE Treatments (
            Treatment     TEXT PRIMARY KEY,
            TreatmentCost INTEGER NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE Appointments (
            ApptID    TEXT PRIMARY KEY,
            PatientID TEXT NOT NULL,
            DoctorID  TEXT NOT NULL,
            FOREIGN KEY (PatientID) REFERENCES Patients(PatientID),
            FOREIGN KEY (DoctorID)  REFERENCES Doctors(DoctorID)
        )
    """)
    cursor.execute("""
        CREATE TABLE AppointmentTreatments (
            ApptID    TEXT NOT NULL,
            Treatment TEXT NOT NULL,
            PRIMARY KEY (ApptID, Treatment),
            FOREIGN KEY (ApptID)    REFERENCES Appointments(ApptID),
            FOREIGN KEY (Treatment) REFERENCES Treatments(Treatment)
        )
    """)

    cursor.executemany("INSERT INTO Departments VALUES (?, ?)", DEPARTMENTS)
    cursor.executemany("INSERT INTO Doctors VALUES (?, ?, ?, ?)", DOCTORS)
    cursor.executemany("INSERT INTO Patients VALUES (?, ?, ?)", PATIENTS)
    cursor.executemany("INSERT INTO Treatments VALUES (?, ?)", TREATMENTS)
    cursor.executemany("INSERT INTO Appointments VALUES (?, ?, ?)", APPOINTMENTS)
    cursor.executemany("INSERT INTO AppointmentTreatments VALUES (?, ?)", APPOINTMENT_TREATMENTS)

    conn.commit()

    # Quick verification so a wrong count is obvious immediately.
    for table in ("Departments", "Doctors", "Patients", "Treatments",
                  "Appointments", "AppointmentTreatments"):
        count = cursor.execute("SELECT COUNT(*) FROM %s" % table).fetchone()[0]
        print("%-22s %4d rows" % (table, count))

    conn.close()
    print("\nDone. Database written to:", DB_PATH)


if __name__ == "__main__":
    build()
