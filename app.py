import os
import re
import shutil
import sqlite3
import time

from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.exceptions import BadRequest, NotFound, RequestEntityTooLarge


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_DIR = os.path.join(BASE_DIR, "databases")
MEDICAL_DB_PATH = os.path.join(DATABASE_DIR, "medical.db")
SANDBOX_DIR = os.path.join(DATABASE_DIR, "sandbox")

DATABASE_NAME_RE = re.compile(r"^[A-Za-z0-9_-]+$")
TABLE_NAME_RE = re.compile(r"^[A-Za-z0-9_]+$")

DEFAULT_LIMIT = 50
MAX_LIMIT = 500
MAX_UPLOAD_BYTES = 5 * 1024 * 1024
SQLITE_HEADER = b"SQLite format 3\x00"

# Safety guards applied to every SQLite connection we open.
QUERY_TIMEOUT_SECONDS = 5
PROGRESS_HANDLER_OPS = 10000
SQLITE_ATTACH = getattr(sqlite3, "SQLITE_ATTACH", 24)
SQLITE_DETACH = getattr(sqlite3, "SQLITE_DETACH", 25)
SQLITE_DENY = getattr(sqlite3, "SQLITE_DENY", 1)
SQLITE_OK = getattr(sqlite3, "SQLITE_OK", 0)


def _block_attach_authorizer(action, *_args):
    """Deny ATTACH/DETACH so a single query can never reach a file outside its
    own database (otherwise a sandbox query could create arbitrary files or
    inject fake databases into the shared gallery)."""
    if action in (SQLITE_ATTACH, SQLITE_DETACH):
        return SQLITE_DENY
    return SQLITE_OK


def harden_connection(conn, timeout_seconds=None):
    """Apply the safety guards shared by every connection: forbid ATTACH/DETACH
    and abort any statement that runs past a wall-clock deadline (stops runaway
    recursive CTEs from pinning the single server worker)."""
    if timeout_seconds is None:
        timeout_seconds = QUERY_TIMEOUT_SECONDS
    conn.set_authorizer(_block_attach_authorizer)
    deadline = time.monotonic() + timeout_seconds
    conn.set_progress_handler(
        lambda: 1 if time.monotonic() > deadline else 0, PROGRESS_HANDLER_OPS
    )
    return conn


app = Flask(__name__, static_folder="static")
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_BYTES
CORS(app)


def query_db(db_path, sql, args=()):
    """Run a read-only SQLite query and return rows as plain dictionaries."""
    conn = None
    try:
        conn = sqlite3.connect("file:%s?mode=ro" % db_path, uri=True)
        harden_connection(conn)
        conn.row_factory = sqlite3.Row
        rows = conn.execute(sql, args).fetchall()
        return [dict(row) for row in rows]
    finally:
        if conn is not None:
            conn.close()


def table_names_for(db_path):
    """Return user-visible table names for one SQLite database."""
    rows = query_db(
        db_path,
        "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name",
    )
    return [row["name"] for row in rows]


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


def list_database_filenames(directory):
    """Return safe .db filenames directly inside a directory."""
    try:
        filenames = os.listdir(directory)
    except FileNotFoundError:
        return []

    safe_filenames = []
    for filename in filenames:
        if filename != filename.lower() or not filename.endswith(".db"):
            continue
        full_path = os.path.join(directory, filename)
        if not os.path.isfile(full_path):
            continue
        try:
            query_database_paths_for(filename)
        except BadRequest:
            continue
        safe_filenames.append(filename)
    return sorted(safe_filenames)


def database_item_for(filename, db_path):
    """Build the JSON shape used for gallery and sandbox database lists."""
    tables = table_names_for(db_path)
    return {
        "database": filename,
        "name": filename[:-3],
        "tables": tables,
        "table_count": len(tables),
    }


def normalise_upload_filename(raw_name):
    """Validate an uploaded database name and return a lowercase .db filename."""
    if not isinstance(raw_name, str) or not raw_name.strip():
        raise BadRequest("database name is required.")

    stem = raw_name.strip().lower()
    if stem.endswith(".db"):
        stem = stem[:-3]
    if not DATABASE_NAME_RE.match(stem):
        raise BadRequest("Invalid database name.")

    return stem + ".db"


def normalise_route_filename(raw_name):
    """Validate a route database name, accepting either name or name.db."""
    if not isinstance(raw_name, str):
        raise BadRequest("Invalid database name.")

    stem = raw_name.lower()
    if stem.endswith(".db"):
        stem = stem[:-3]
    if not DATABASE_NAME_RE.match(stem):
        raise BadRequest("Invalid database name.")

    return stem + ".db"


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


def query_database_paths_for(filename):
    """Validate a .db filename and return shared and sandbox candidate paths.

    The name is lower-cased so it maps to the same file on every operating
    system (some filesystems are case-insensitive). This keeps each student's
    sandbox isolated and reserves shared names like medical.db no matter how
    they are typed (e.g. MEDICAL.db cannot become a separate writable file).
    """
    if not isinstance(filename, str):
        raise BadRequest("Invalid database name.")

    filename = filename.lower()
    if not filename.endswith(".db"):
        raise BadRequest("Invalid database name.")

    db_name = filename[:-3]
    if not DATABASE_NAME_RE.match(db_name):
        raise BadRequest("Invalid database name.")

    databases_root = os.path.realpath(DATABASE_DIR)
    shared_candidate = os.path.realpath(os.path.join(databases_root, filename))
    if os.path.commonpath([databases_root, shared_candidate]) != databases_root:
        raise BadRequest("Invalid database path.")

    sandbox_root = os.path.realpath(SANDBOX_DIR)
    sandbox_candidate = os.path.realpath(os.path.join(sandbox_root, filename))
    if os.path.commonpath([sandbox_root, sandbox_candidate]) != sandbox_root:
        raise BadRequest("Invalid database path.")

    return shared_candidate, sandbox_candidate


def request_json_object():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise BadRequest("JSON body must be an object.")
    return data


def is_select_sql(sql):
    stripped = sql.lstrip()
    while stripped.startswith("("):
        stripped = stripped[1:].lstrip()
    return stripped.upper().startswith(("SELECT", "WITH"))


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


@app.errorhandler(RequestEntityTooLarge)
def handle_request_entity_too_large(error):
    return jsonify({"error": "Uploaded file is too large. Maximum size is 5 MB."}), 413


@app.errorhandler(500)
def handle_server_error(error):
    return jsonify({"error": "Internal server error."}), 500


@app.get("/")
def index():
    return app.send_static_file("index.html")


@app.get("/host")
def host():
    return app.send_static_file("host.html")


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
            "write_practice": [
                {
                    "method": "POST",
                    "path": "/query",
                    "description": "Run SELECT on shared databases or read/write SQL on your own sandbox database.",
                },
                {
                    "method": "POST",
                    "path": "/reseed",
                    "description": "Copy fresh medical sample data into your own sandbox database.",
                },
            ],
            "upload_and_host": [
                {
                    "method": "POST",
                    "path": "/upload",
                    "description": "Upload a real SQLite .db file into your own sandbox.",
                },
                {
                    "method": "GET",
                    "path": "/gallery",
                    "description": "List shared read-only gallery databases.",
                },
                {
                    "method": "GET",
                    "path": "/mydbs",
                    "description": "List your uploaded and editable sandbox databases.",
                },
                {
                    "method": "DELETE",
                    "path": "/mydbs/<name>",
                    "description": "Delete one sandbox database.",
                },
                {
                    "method": "POST",
                    "path": "/queryx",
                    "description": "Compatibility alias for /query; accepts database or db_name.",
                },
            ],
            "safety": "Shared class databases are read-only; sandbox databases are per-student read-write files.",
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
    return jsonify(table_names_for(db_path))


@app.get("/db/<db_name>/<table>")
def table_rows(db_name, table):
    db_path = database_path_for(db_name)
    ensure_table_exists(db_path, table)
    limit = parse_limit()
    rows = query_db(db_path, 'SELECT * FROM "%s" LIMIT ?' % table, (limit,))
    return jsonify(rows)


@app.get("/gallery")
def gallery():
    items = []
    for filename in list_database_filenames(DATABASE_DIR):
        shared_path, _ = query_database_paths_for(filename)
        items.append(database_item_for(filename, shared_path))
    return jsonify(items)


@app.get("/mydbs")
def mydbs():
    items = []
    for filename in list_database_filenames(SANDBOX_DIR):
        shared_path, sandbox_path = query_database_paths_for(filename)
        if os.path.isfile(shared_path):
            continue
        items.append(database_item_for(filename, sandbox_path))
    return jsonify(items)


@app.delete("/mydbs/<name>")
def delete_mydb(name):
    filename = normalise_route_filename(name)
    shared_path, sandbox_path = query_database_paths_for(filename)
    if os.path.isfile(shared_path):
        return jsonify({"error": f"{filename} is a shared, read-only class database."}), 403
    if not os.path.isfile(sandbox_path):
        raise NotFound("Database not found.")

    os.remove(sandbox_path)
    return jsonify({"message": f"Deleted '{filename}'."})


@app.post("/upload")
def upload():
    if "file" not in request.files:
        raise BadRequest("file is required.")

    uploaded_file = request.files["file"]
    payload = uploaded_file.read()
    if not payload:
        raise BadRequest("file must be non-empty.")
    if len(payload) > MAX_UPLOAD_BYTES:
        raise BadRequest("file must be 5 MB or smaller.")
    if payload[:16] != SQLITE_HEADER:
        raise BadRequest("file must be a SQLite .db file.")

    raw_name = request.form.get("name") or uploaded_file.filename
    filename = normalise_upload_filename(raw_name)
    shared_path, sandbox_path = query_database_paths_for(filename)
    if os.path.isfile(shared_path):
        raise BadRequest("Cannot overwrite a shared gallery database.")

    os.makedirs(os.path.dirname(sandbox_path), exist_ok=True)
    with open(sandbox_path, "wb") as db_file:
        db_file.write(payload)

    try:
        tables = table_names_for(sandbox_path)
    except sqlite3.Error:
        try:
            os.remove(sandbox_path)
        except FileNotFoundError:
            pass
        raise BadRequest("Uploaded file is not a valid SQLite database.")

    return jsonify(
        {
            "message": f"Uploaded '{filename}' to your sandbox.",
            "database": filename,
            "tables": tables,
        }
    )


def run_query(database, sql):
    if not isinstance(sql, str) or not sql.strip():
        raise BadRequest("sql must be a non-empty string.")

    shared_path, sandbox_path = query_database_paths_for(database)
    select_query = is_select_sql(sql)
    is_shared = os.path.isfile(shared_path)

    if is_shared and not select_query:
        return (
            jsonify(
                {
                    "error": (
                        f"{database} is a shared, read-only class database. "
                        "To practise INSERT/UPDATE/DELETE, use your own database, "
                        'e.g. {"database": "yourname.db", "sql": "..."} '
                        "(POST /reseed first to get your own copy of the data)."
                    )
                }
            ),
            403,
        )

    try:
        if is_shared:
            rows = query_db(shared_path, sql)
            return jsonify({"results": rows, "count": len(rows)})

        os.makedirs(os.path.dirname(sandbox_path), exist_ok=True)
        conn = None
        try:
            conn = sqlite3.connect(sandbox_path)
            harden_connection(conn)
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(sql)
            if select_query:
                rows = [dict(row) for row in cursor.fetchall()]
                return jsonify({"results": rows, "count": len(rows)})

            conn.commit()
            return jsonify({"message": "Query executed", "rows_affected": cursor.rowcount})
        finally:
            if conn is not None:
                conn.close()
    except (sqlite3.Error, sqlite3.Warning) as exc:
        # sqlite3.Warning (e.g. "only execute one statement at a time") is NOT a
        # subclass of sqlite3.Error, so it must be caught explicitly or it would
        # surface as an uncaught 500.
        message = str(exc)
        lowered = message.lower()
        if "interrupt" in lowered:
            message = (
                "Query took too long and was stopped "
                "(limit: %d seconds)." % QUERY_TIMEOUT_SECONDS
            )
        elif "not authorized" in lowered:
            message = "That statement is not allowed here (ATTACH/DETACH are disabled)."
        return jsonify({"error": message}), 400


@app.post("/query")
def query():
    data = request_json_object()
    if "database" not in data or "sql" not in data:
        raise BadRequest("database and sql are required.")

    return run_query(data["database"], data["sql"])


@app.post("/queryx")
def queryx():
    data = request_json_object()
    if ("database" not in data and "db_name" not in data) or "sql" not in data:
        raise BadRequest("database and sql are required.")

    database = data["database"] if "database" in data else data["db_name"]
    return run_query(database, data["sql"])


@app.post("/reseed")
def reseed():
    data = request_json_object()
    if "database" not in data:
        raise BadRequest("database is required.")

    database = data["database"]
    shared_path, sandbox_path = query_database_paths_for(database)
    if os.path.isfile(shared_path):
        return jsonify({"error": f"{database} is a shared, read-only class database."}), 403

    source_database = data.get("from", "medical.db")
    source_shared_path, _ = query_database_paths_for(source_database)
    if not os.path.isfile(source_shared_path):
        raise NotFound("Source gallery database not found.")

    os.makedirs(os.path.dirname(sandbox_path), exist_ok=True)
    shutil.copyfile(source_shared_path, sandbox_path)

    if "from" not in data:
        return jsonify({"message": f"Reseeded '{database}' with a fresh copy of the medical data."})
    return jsonify({"message": f"Reseeded '{database}' with a fresh copy of '{source_database}'."})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
