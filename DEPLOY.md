# Deploy ishflask on ICDSoft SureServer

**Status: ✅ DEPLOYED & VERIFIED LIVE at https://api.ishweb.nl (5 Jun 2026).**
These are the exact steps used, with the real values for the ISH account.

This runbook deploys the shared class API once. Students can then upload `.db` files into `databases/` and query them from a browser, Python `requests`, or static pages hosted at `http://students.ishweb.nl/projects/<folder>`.

The shared student FTP account serves static files only — it cannot run Python by itself. Do not reuse or overwrite the existing `hootish` Node.js WebApp.

This follows the ICDSoft FAQ article-2014 pattern: create a **Custom** WebApp, build a Python virtual environment in its deployment directory, and let `run.sh` run Flask on ICDSoft's assigned `$PORT`.

## Confirmed values (ISH account)

| Item | Real value |
| --- | --- |
| Server | `s951.sureserver.com` (panel: https://panel.s951.sureserver.com) |
| Account (`whoami`) | `ishweb` |
| Deployment directory | `/home/ishweb/private/ishflask` |
| Domain / Subdomain | `ishweb.nl` / `api` → `api.ishweb.nl` |
| App name / Engine | `ishflask` / `Custom` |
| Assigned port | automatic (was `27855`) |

## 1. Clone the code (Web SSH Terminal)

SSH and build tools are already enabled on this account. In the Web SSH Terminal:

```sh
git clone https://github.com/tanasel/ishflask.git ~/private/ishflask
```

## 2. Build the Python environment

```sh
cd ~/private/ishflask
python3 -m venv .
. bin/activate
python -m pip install --no-cache-dir -r requirements.txt
python seed_medical.py
```

`--no-cache-dir` is good practice on quota-limited shared hosting.

## 3. Create the subdomain + Custom WebApp (panel)

**Subdomains → Create →** `api` (creates `api.ishweb.nl`).

**WebApps → Create:**

| Field | Value |
| --- | --- |
| Engine | `Custom`  (NOT Node.js) |
| Name | `ishflask` |
| Domain / Subdomain | `ishweb.nl` / `api` |
| Web access path | `/` |
| Deployment directory | `/private/ishflask` — **use the folder browser**; the field ignores typed paths and only accepts existing folders (that is why you clone first) |
| Start command | `sh run.sh` |

WebApps get an auto-assigned `$PORT`; never set `PORT` yourself.

## 4. Start and bind (Web SSH Terminal)

```sh
sureapp project shell ishflask
sureapp service manage --enable
sureapp service manage --start
sureapp service status            # shows the listening port
```

Selecting `api` in the Create form already binds the subdomain. If the public URL ever shows the static `www/api` folder instead of the app, bind it explicitly:

```sh
sureapp project modify ishflask --subdomain api
```

There is no `sureapp service manage --restart` — use `--stop` then `--start`.

## 5. Verify

```sh
curl -s http://localhost:$PORT/health        # {"status":"ok"}
curl -s https://api.ishweb.nl/health         # {"status":"ok"}  (also confirms HTTPS)
curl -s https://api.ishweb.nl/appointments/D1
```

## How the teacher adds a student database

Copy or FTP the student's `.db` into `/home/ishweb/private/ishflask/databases/`. **No restart needed** — the API reads database files at request time. Verified live example:

```text
# library.db dropped into databases/  ->  instantly live:
#   https://api.ishweb.nl/db/library/tables          -> ["Books"]
#   https://api.ishweb.nl/db/library/Books?limit=5   -> JSON rows
```

## Updating the deployed app

```sh
sureapp project shell ishflask
cd ~/private/ishflask && git pull
. bin/activate && python -m pip install --no-cache-dir -r requirements.txt
sureapp service manage --stop && sureapp service manage --start
```

## Troubleshooting

| Problem | Likely cause | Fix |
| --- | --- | --- |
| "Not enough disk space" but the panel/`df` shows space free | Known ICDSoft **false-positive** (the ISH account had ~24 GB free). It did **not** recur on a fresh Custom WebApp. | Retry on a NEW Custom WebApp (do not reuse the Node app). If it persists, open an ICDSoft support ticket quoting the free space — it is server-side, not your usage. |
| Browser shows `No site configured` on the API subdomain | Subdomain still points at the static folder. | `sureapp project modify ishflask --subdomain api`. |
| Deployment-directory field won't keep a typed path | It only accepts existing folders via the folder browser. | Clone the code first, then pick `/private/ishflask` with the "Select folder" button. |
| `MODULE_NOT_FOUND` / app won't start | Created as Node.js, or wrong deployment dir / start command. | Engine `Custom`, dir `/home/ishweb/private/ishflask`, start `sh run.sh`. |
| `curl localhost:$PORT/health` fails | Not running, or the venv was not built in the deployment dir. | `sureapp project shell ishflask`, `. bin/activate`, reinstall `--no-cache-dir`, `--stop` then `--start`. |
