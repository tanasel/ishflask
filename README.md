# ishflask

ishflask is a small Flask and SQLite JSON API for two jobs: a live client-server teaching demo for the IB Computer Science Databases unit, and a clean template students can copy for an Internal Assessment project that needs a read-only database behind an API.

## Run Locally

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python seed_medical.py
flask --app app run
```

You can also run `python app.py` for local development. Open `http://127.0.0.1:5000` in a browser.

## Deploy On ICDSoft (api.ishweb.nl)

In the ICDSoft panel, go to WebApps -> Create:

- Engine: `Custom`
- Subdomain: `api.ishweb.nl`
- Deployment directory: `/home/ishweb/private/ishflask`
- Start command: `sh run.sh`

Then use SSH from the Web SSH Terminal:

```sh
sureapp project shell ishflask
cd /home/ishweb/private/ishflask
python3 -m venv .
source bin/activate
pip install -r requirements.txt
python seed_medical.py
sureapp service manage --enable
sureapp service manage --start
sureapp project modify ishflask --subdomain api
curl -s http://localhost:$PORT/health
```

This venv-in-place method follows ICDSoft FAQ article-2014 for the Custom engine, not Node.js.

## How Students Use It

Browser URLs:

- `http://127.0.0.1:5000/patients`
- `http://127.0.0.1:5000/appointments/D1`
- `http://127.0.0.1:5000/patients/search?name=Anika`
- `http://127.0.0.1:5000/db`
- `http://127.0.0.1:5000/db/medical/tables`
- `http://127.0.0.1:5000/db/medical/Patients?limit=10`

The `client_example.py` file shows the same requests from Python with `requests`. Change `BASE_URL` from `http://127.0.0.1:5000` to the deployed URL when the API is live.

## Copy This For Your IA

To reuse this template, add your own `.db` file to `databases/`, edit the fixed example routes in `app.py`, and keep the generic database explorer read-only. Keep using `?` placeholders for values and validate database and table names before building SQL around identifiers.

## Data Warning

This project uses sample fictional data only. It is read-only and must never contain real personal data.
