# ishflask — ready-to-paste additions for the teaching doc + slides

These are drafted for **Robin to paste into his own Google Doc / Slides** (his materials —
not edited directly). All `api.ishweb.nl` URLs go live **once the app is deployed**
(deploy currently blocked by an ICDSoft disk-space error — see project notes).

---

## A) For the Python/SQLite doc — turn the abstract "Option 2" into a real example

> **Try it live** (real, clickable once the API is deployed):
> - All patients (JSON): `https://api.ishweb.nl/patients`
> - One doctor's appointments — a JOIN over HTTP: `https://api.ishweb.nl/appointments/D1`
> - Search patients by name: `https://api.ishweb.nl/patients/search?name=Anika`
> - Friendly page (click buttons, see a table): `https://api.ishweb.nl/`
> - Any table of any uploaded database: `https://api.ishweb.nl/db/medical/Patients?limit=10`

**Call it from Python (the client side):**

```python
import requests

# all patients
print(requests.get("https://api.ishweb.nl/patients").json())

# Dr. Hare's appointments (the server does the JOIN for you)
print(requests.get("https://api.ishweb.nl/appointments/D1").json())

# search by name
print(requests.get("https://api.ishweb.nl/patients/search",
                   params={"name": "Anika"}).json())
```

Notice: you never download `medical.db`. You ask the server a question over HTTP and it
sends back **only the rows you asked for**, as JSON. That is "Option 2 — Python on the server".

**How it works:**

```
Browser / Python          Flask app on the server          SQLite (medical.db)
   (the client)
       |   --- HTTP request:  GET /appointments/D1 --->         |
       |                          | --- SQL: SELECT ... JOIN --->|
       |                          | <--------- rows ------------ |
       |   <--- JSON response ----                               |
```

---

## B) New section — "Want a database in YOUR IA?"

> The class API is also a **template you can copy** for your Internal Assessment:
> 1. Get the project: `github.com/tanasel/ishflask` (or ask your teacher for the folder).
> 2. Replace `databases/medical.db` with **your own** `.db`.
> 3. In `app.py`, write your **own** routes (your own SQL queries) — *this* is the part that
>    counts as your IA work. The template just gives you a safe, working starting point.
> 4. Run it locally for your video (`flask --app app run`), or deploy your own copy.
>
> ⚠️ The example is **read-only** and uses **made-up data**. Never put real personal data in a
> database you publish online — anyone could read it.

---

## C) New slide for the "Host X online — for free" deck

Matches the existing slides ("Host your HTML / file / image online — for free").

> ### Host your DATABASE online — a live API! For free
>
> - Your `.db` stays on the server. People send a request and get back **just the data** they
>   asked for — not the whole file.
> - Example: `api.ishweb.nl/db/<yourname>/<table>` → rows as JSON.
> - **For the unit:** your teacher adds your practice `.db` to the class API.
> - **For your IA:** copy the template (`github.com/tanasel/ishflask`), add your own `.db` and
>   your own code.
> - This is **"Option 2 — Python on the server"** made real (vs. Option 1 = download the `.db`).

---

## Optional: a client → server → database diagram for the slide
Three boxes left-to-right: **Client** (browser / Python `requests`) → **Server** (Flask `app.py`)
→ **Database** (`medical.db`). Arrows: request goes right ("GET /appointments/D1"),
data comes back left ("JSON rows"). Caption: *the database never leaves the server.*
