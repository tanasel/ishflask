"""
Small client-side example for students.

Run the Flask app locally first, then run:

    python client_example.py

This file uses the third-party requests package. Install it with
``pip install requests`` if your Python environment does not have it yet.
"""

import requests


# Swap this for the live URL when deployed, for example:
# BASE_URL = "https://api.ishweb.nl"
BASE_URL = "http://127.0.0.1:5000"


def get_json(path):
    response = requests.get(BASE_URL + path, timeout=10)
    response.raise_for_status()
    return response.json()


def print_rows(title, rows):
    print("\n" + title)
    print("-" * len(title))
    for row in rows:
        print(row)


def main():
    patients = get_json("/patients")
    print_rows("All patients", patients)

    appointments = get_json("/appointments/D1")
    print_rows("Appointments for doctor D1", appointments)

    search_results = get_json("/patients/search?name=Anika")
    print_rows("Patients matching Anika", search_results)


if __name__ == "__main__":
    main()
