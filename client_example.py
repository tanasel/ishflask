"""
Beginner client for the ishflask teaching API.

Install requests first if needed:

    pip install requests

Then run:

    python client_example.py
"""

import requests


SERVER = "https://api.ishweb.nl"
MY_DATABASE = "yourname.db"


def post_json(path, payload):
    """Send JSON to the API and print the JSON response."""
    response = requests.post(SERVER + path, json=payload, timeout=10)
    data = response.json()
    print("\nPOST", path)
    print("Status:", response.status_code)
    print(data)
    response.raise_for_status()
    return data


def run_sql(database, sql):
    """Run one SQL statement through POST /query."""
    return post_json("/query", {"database": database, "sql": sql})


def reseed(database):
    """Copy fresh medical data into your own sandbox database."""
    return post_json("/reseed", {"database": database})


def main():
    # Shared class databases are read-only. SELECT is allowed.
    run_sql(
        "medical.db",
        "SELECT PatientID, Patient, DOB FROM Patients WHERE PatientID = 'P1'",
    )

    # JOIN queries are also allowed on shared databases.
    run_sql(
        "medical.db",
        """
        SELECT p.Patient, d.Doctor, d.Specialisation
        FROM Appointments a
        JOIN Patients p ON a.PatientID = p.PatientID
        JOIN Doctors d ON a.DoctorID = d.DoctorID
        WHERE p.PatientID = 'P1'
        """,
    )

    # Reseed your own sandbox before write practice.
    reseed(MY_DATABASE)

    # Sandbox databases allow INSERT, UPDATE, DELETE, and other write queries.
    run_sql(
        MY_DATABASE,
        """
        INSERT INTO Patients (PatientID, Patient, DOB)
        VALUES ('P99', 'Your Name', 2008)
        """,
    )

    # Read back the row you inserted.
    run_sql(
        MY_DATABASE,
        "SELECT PatientID, Patient, DOB FROM Patients WHERE PatientID = 'P99'",
    )


if __name__ == "__main__":
    main()
