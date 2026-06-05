# ishflask

ishflask is a small Flask and SQLite JSON API for two jobs: a live client-server teaching demo for the IB Computer Science Databases unit, and a clean template students can copy for an Internal Assessment project that needs a read-only database behind an API.

**Live:** https://api.ishweb.nl  (deployed on ICDSoft SureServer, 5 Jun 2026)

## Run Locally

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python seed_medical.py
flask --app app run
```

You can also run `python app.py` for local development. Open `http://127.0.0.1:5000` in a browser.

## Deploy On ICDSoft (api.ishweb.nl) — LIVE

See [DEPLOY.md](DEPLOY.md) for the full, verified ICDSoft runbook. The live deployment uses account `ishweb` and subdomain `api.ishweb.nl` on server `s951`.

In the ICDSoft panel, go to WebApps -> Create:

- Engine: `Custom`  (NOT Node.js)
- Subdomain: `api.ishweb.nl`
- Deployment directory: `/home/ishweb/private/ishflask`
- Start command: `sh run.sh`

Then use SSH from the Web SSH Terminal:

```sh
git clone https://github.com/tanasel/ishflask.git ~/private/ishflask
sureapp project shell ishflask
cd /home/ishweb/private/ishflask
python3 -m venv .
source bin/activate
pip install --no-cache-dir -r requirements.txt
python seed_medical.py
sureapp service manage --enable
sureapp service manage --start
sureapp project modify ishflask --subdomain api
curl -s http://localhost:$PORT/health
```

This venv-in-place method follows ICDSoft FAQ article-2014 for the Custom engine, not Node.js.

## How Students Use It

Live API (open these in a browser):

- https://api.ishweb.nl/patients
- https://api.ishweb.nl/appointments/D1
- https://api.ishweb.nl/patients/search?name=Anika
- https://api.ishweb.nl/db
- https://api.ishweb.nl/db/medical/tables
- https://api.ishweb.nl/db/medical/Patients?limit=10

The `client_example.py` file shows the same requests from Python with `requests`; set `BASE_URL = "https://api.ishweb.nl"`.

## Add A Student Database (shared class API)

Drop any `.db` file into `databases/` on the server (via FTP or git/SSH). It is queryable immediately — no restart needed. Example added live:

- https://api.ishweb.nl/db/library/tables
- https://api.ishweb.nl/db/library/Books?limit=5

## Copy This For Your IA

To reuse this template, add your own `.db` file to `databases/`, edit the fixed example routes in `app.py`, and keep the generic database explorer read-only. Keep using `?` placeholders for values and validate database and table names before building SQL around identifiers.

## Data Warning

This project uses sample fictional data only. It is read-only and must never contain real personal data.
