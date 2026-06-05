import os
import sqlite3

import pytest

import app as app_module


@pytest.fixture
def client():
    app_module.app.config.update(TESTING=True)
    with app_module.app.test_client() as test_client:
        yield test_client


def test_root_serves_landing_page(client):
    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.content_type
    assert b"IB CS Medical API" in response.data


def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_api_index(client):
    response = client.get("/api")
    data = response.get_json()

    assert response.status_code == 200
    assert "medical" in data["databases"]
    assert any(item["path"] == "/patients" for item in data["example_endpoints"])
    assert any(item["path"] == "/db/medical/Patients?limit=10" for item in data["generic_explorer"])


def test_patients_route_returns_all_patients(client):
    response = client.get("/patients")
    data = response.get_json()

    assert response.status_code == 200
    assert len(data) == 25
    assert {"PatientID": "P1", "Patient": "Anika", "DOB": 1988} in data


def test_appointments_route_returns_doctor_rows(client):
    response = client.get("/appointments/D1")
    data = response.get_json()

    assert response.status_code == 200
    assert len(data) == 16
    assert data
    assert all(row["Doctor"] == "Dr. Hare" for row in data)


def test_patient_search_route_uses_query_parameter(client):
    response = client.get("/patients/search?name=Anika")
    data = response.get_json()

    assert response.status_code == 200
    assert data == [{"PatientID": "P1", "Patient": "Anika", "DOB": 1988}]


def test_db_route_lists_databases(client):
    response = client.get("/db")

    assert response.status_code == 200
    assert "medical" in response.get_json()


def test_tables_route_lists_tables(client):
    response = client.get("/db/medical/tables")
    data = response.get_json()

    assert response.status_code == 200
    assert "Patients" in data
    assert "Appointments" in data


def test_generic_table_route_returns_limited_rows(client):
    response = client.get("/db/medical/Patients?limit=2")
    data = response.get_json()

    assert response.status_code == 200
    assert len(data) == 2
    assert set(data[0]) == {"PatientID", "Patient", "DOB"}


def test_unknown_db_returns_json_404(client):
    response = client.get("/db/not_here/tables")

    assert response.status_code == 404
    assert "error" in response.get_json()


def test_unknown_table_returns_json_404(client):
    response = client.get("/db/medical/NotATable")

    assert response.status_code == 404
    assert "error" in response.get_json()


def test_unknown_route_returns_json_404(client):
    response = client.get("/not-a-route")

    assert response.status_code == 404
    assert "error" in response.get_json()


def test_bad_db_identifier_is_rejected(client):
    response = client.get("/db/bad.name/tables")

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_path_traversal_db_identifier_is_rejected(client):
    response = client.get("/db/%2e%2e/tables")

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_bad_table_identifier_is_rejected(client):
    response = client.get("/db/medical/Bad-Name")

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_table_name_injection_attempt_is_rejected(client):
    response = client.get("/db/medical/Patients%3BDROP%20TABLE%20Patients")

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_non_integer_limit_returns_400(client):
    response = client.get("/db/medical/Patients?limit=lots")

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_limit_is_clamped_to_one(client):
    response = client.get("/db/medical/Patients?limit=0")

    assert response.status_code == 200
    assert len(response.get_json()) == 1


def test_limit_is_clamped_to_500(tmp_path, monkeypatch, client):
    db_dir = tmp_path / "databases"
    db_dir.mkdir()
    db_path = db_dir / "large.db"

    conn = sqlite3.connect(str(db_path))
    conn.execute("CREATE TABLE Numbers (NumberID INTEGER PRIMARY KEY, Label TEXT NOT NULL)")
    conn.executemany(
        "INSERT INTO Numbers (Label) VALUES (?)",
        [("row-%03d" % number,) for number in range(600)],
    )
    conn.commit()
    conn.close()

    monkeypatch.setattr(app_module, "DATABASE_DIR", str(db_dir))

    response = client.get("/db/large/Numbers?limit=9999")

    assert response.status_code == 200
    assert len(response.get_json()) == 500


def test_query_db_opens_connections_read_only():
    with pytest.raises(sqlite3.OperationalError) as exc_info:
        app_module.query_db(
            app_module.MEDICAL_DB_PATH,
            "INSERT INTO Patients (PatientID, Patient, DOB) VALUES (?, ?, ?)",
            ("PX", "Test", 2000),
        )

    assert "readonly" in str(exc_info.value).lower() or "read-only" in str(exc_info.value).lower()


def test_api_index_lists_write_practice_endpoints(client):
    response = client.get("/api")
    data = response.get_json()

    assert response.status_code == 200
    assert any(item["path"] == "/query" for item in data["write_practice"])
    assert any(item["path"] == "/reseed" for item in data["write_practice"])


def test_query_select_on_shared_medical_returns_row(client):
    response = client.post(
        "/query",
        json={
            "database": "medical.db",
            "sql": "SELECT * FROM Patients WHERE PatientID = 'P1'",
        },
    )
    data = response.get_json()

    assert response.status_code == 200
    assert data["count"] == 1
    assert data["results"] == [{"PatientID": "P1", "Patient": "Anika", "DOB": 1988}]


def test_query_write_on_shared_medical_is_forbidden_and_unchanged(client):
    response = client.post(
        "/query",
        json={
            "database": "medical.db",
            "sql": "DELETE FROM Patients",
        },
    )
    patients_after = client.get("/patients").get_json()

    assert response.status_code == 403
    assert "shared, read-only class database" in response.get_json()["error"]
    assert len(patients_after) == 25


def test_query_sandbox_create_insert_select(tmp_path, monkeypatch, client):
    monkeypatch.setattr(app_module, "SANDBOX_DIR", str(tmp_path / "sandbox"))

    create_response = client.post(
        "/query",
        json={
            "database": "student.db",
            "sql": "CREATE TABLE Notes (NoteID INTEGER PRIMARY KEY, Body TEXT NOT NULL)",
        },
    )
    insert_response = client.post(
        "/query",
        json={
            "database": "student.db",
            "sql": "INSERT INTO Notes (Body) VALUES ('First note')",
        },
    )
    select_response = client.post(
        "/query",
        json={
            "database": "student.db",
            "sql": "SELECT NoteID, Body FROM Notes ORDER BY NoteID",
        },
    )

    assert create_response.status_code == 200
    assert create_response.get_json()["message"] == "Query executed"
    assert insert_response.status_code == 200
    assert insert_response.get_json()["rows_affected"] == 1
    assert select_response.status_code == 200
    assert select_response.get_json() == {
        "results": [{"NoteID": 1, "Body": "First note"}],
        "count": 1,
    }


def test_reseed_sandbox_then_insert_patient(tmp_path, monkeypatch, client):
    monkeypatch.setattr(app_module, "SANDBOX_DIR", str(tmp_path / "sandbox"))

    reseed_response = client.post("/reseed", json={"database": "yourname.db"})
    insert_response = client.post(
        "/query",
        json={
            "database": "yourname.db",
            "sql": (
                "INSERT INTO Patients (PatientID, Patient, DOB) "
                "VALUES ('PX', 'Practice Patient', 2010)"
            ),
        },
    )
    select_response = client.post(
        "/query",
        json={
            "database": "yourname.db",
            "sql": "SELECT * FROM Patients WHERE PatientID = 'PX'",
        },
    )

    assert reseed_response.status_code == 200
    assert reseed_response.get_json() == {
        "message": "Reseeded 'yourname.db' with a fresh copy of the medical data."
    }
    assert insert_response.status_code == 200
    assert insert_response.get_json()["rows_affected"] == 1
    assert select_response.status_code == 200
    assert select_response.get_json() == {
        "results": [{"PatientID": "PX", "Patient": "Practice Patient", "DOB": 2010}],
        "count": 1,
    }


def test_reseed_shared_database_is_forbidden(client):
    response = client.post("/reseed", json={"database": "medical.db"})

    assert response.status_code == 403
    assert "shared, read-only class database" in response.get_json()["error"]


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"database": "medical.db"},
        {"sql": "SELECT 1"},
        {"database": "medical.db", "sql": ""},
        {"database": "medical.db", "sql": "   "},
        {"database": "medical.db", "sql": 123},
    ],
)
def test_query_missing_fields_or_bad_sql_returns_400(client, payload):
    response = client.post("/query", json=payload)

    assert response.status_code == 400
    assert "error" in response.get_json()


@pytest.mark.parametrize(
    "database",
    ["medical", "bad.name.db", "../medical.db", "sandbox/other.db"],
)
def test_query_bad_or_traversal_database_name_returns_400(client, database):
    response = client.post(
        "/query",
        json={"database": database, "sql": "SELECT 1"},
    )

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_query_sql_error_on_sandbox_returns_400(tmp_path, monkeypatch, client):
    monkeypatch.setattr(app_module, "SANDBOX_DIR", str(tmp_path / "sandbox"))

    response = client.post(
        "/query",
        json={"database": "broken.db", "sql": "SELECT * FROM MissingTable"},
    )

    assert response.status_code == 400
    assert "no such table" in response.get_json()["error"]
