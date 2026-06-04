import os
import re
import sqlite3

from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.exceptions import BadRequest, NotFound


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_DIR = os.path.join(BASE_DIR, "databases")
MEDICAL_DB_PATH = os.path.join(DATABASE_DIR, "medical.db")

DATABASE_NAME_RE = re.compile(r"^[A-Za-z0-9_-]+$")
TABLE_NAME_RE = re.compile(r"^[A-Za-z0-9_]+$")

DEFAULT_LIMIT = 50
MAX_LIMIT = 500


app = Flask(__name__, static_folder="static")
CORS(app)


def query_db(db_path, sql, args=()):
    """Run a read-only SQLite query and return rows as plain dictionaries."""
    conn = None
    try:
        conn = sqlite3.connect("file:%s?mode=ro" % db_path, uri=True)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(sql, args).fetchall()
        return [dict(row) for row in rows]
    finally:
        if conn is not None:
            conn.close()


def list_database_names():
    """Return database names without the .db suffix."""
    try:
        filenames = os.listdir(DATABASE_DIR)
    except FileNotFoundError:
        return []

    names = []
    for filename in filenames:
        full_path = os.path.join(DATABASE_DIR, filename)
        if filename.endswith(".db") and os.path.isfile(full_path):
            names.append(filename[:-3])
    return sorted(names)


def database_path_for(db_name):
    """Validate a database name and return its real path inside databases/."""
    if not DATABASE_NAME_RE.match(db_name):
        raise BadRequest("Invalid database name.")

    databases_root = os.path.realpath(DATABASE_DIR)
    candidate = os.path.realpath(os.path.join(databases_root, db_name + ".db"))

    if os.path.commonpath([databases_root, candidate]) != databases_root:
        raise BadRequest("Invalid database path.")
    if not os.path.isfile(candidate):
        raise NotFound("Database not found.")

    return candidate


def ensure_table_exists(db_path, table):
    """Validate that a table name is safe and present in sqlite_master."""
    if not TABLE_NAME_RE.match(table):
        raise BadRequest("Invalid table name.")

    rows = query_db(
        db_path,
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name = ?",
        (table,),
    )
    if not rows:
        raise NotFound("Table not found.")


def parse_limit():
    raw_limit = request.args.get("limit", str(DEFAULT_LIMIT))
    try:
        limit = int(raw_limit)
    except ValueError:
        raise BadRequest("limit must be an integer.")

    return max(1, min(limit, MAX_LIMIT))


@app.errorhandler(400)
def handle_bad_request(error):
    return jsonify({"error": getattr(error, "description", "Bad request.")}), 400


@app.errorhandler(404)
def handle_not_found(error):
    return jsonify({"error": getattr(error, "description", "Not found.")}), 404


@app.errorhandler(500)
def handle_server_error(error):
    return jsonify({"error": "Internal server error."}), 500


@app.get("/")
def index():
    return app.send_static_file("index.html")


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/api")
def api_index():
    return jsonify(
        {
            "databases": list_database_names(),
            "example_endpoints": [
                {
                    "method": "GET",
                    "path": "/patients",
                    "description": "List every sample patient.",
                },
                {
                    "method": "GET",
                    "path": "/appointments/D1",
                    "description": "List appointments for one doctor.",
                },
                {
                    "method": "GET",
                    "path": "/patients/search?name=Anika",
                    "description": "Search patients by name.",
                },
            ],
            "generic_explorer": [
                {
                    "method": "GET",
                    "path": "/db",
                    "description": "List available .db files.",
                },
                {
                    "method": "GET",
                    "path": "/db/medical/tables",
                    "description": "List tables in one database.",
                },
                {
                    "method": "GET",
                    "path": "/db/medical/Patients?limit=10",
                    "description": "Read rows from a validated table.",
                },
            ],
            "safety": "All SQLite connections are opened read-only.",
        }
    )


@app.get("/patients")
def patients():
    rows = query_db(MEDICAL_DB_PATH, "SELECT * FROM Patients ORDER BY PatientID")
    return jsonify(rows)


@app.get("/appointments/<doctor_id>")
def appointments_for_doctor(doctor_id):
    rows = query_db(
        MEDICAL_DB_PATH,
        """
        SELECT p.Patient, p.DOB, d.Doctor, d.Specialisation
        FROM Appointments a
        JOIN Patients p ON a.PatientID = p.PatientID
        JOIN Doctors d ON a.DoctorID = d.DoctorID
        WHERE a.DoctorID = ?
        """,
        (doctor_id,),
    )
    return jsonify(rows)


@app.get("/patients/search")
def search_patients():
    name = request.args.get("name", "")
    rows = query_db(
        MEDICAL_DB_PATH,
        "SELECT * FROM Patients WHERE Patient LIKE ? ORDER BY PatientID",
        ("%" + name + "%",),
    )
    return jsonify(rows)


@app.get("/db")
def databases():
    return jsonify(list_database_names())


@app.get("/db/<db_name>/tables")
def tables(db_name):
    db_path = database_path_for(db_name)
    rows = query_db(
        db_path,
        "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name",
    )
    return jsonify([row["name"] for row in rows])


@app.get("/db/<db_name>/<table>")
def table_rows(db_name, table):
    db_path = database_path_for(db_name)
    ensure_table_exists(db_path, table)
    limit = parse_limit()
    rows = query_db(db_path, 'SELECT * FROM "%s" LIMIT ?' % table, (limit,))
    return jsonify(rows)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
