# ishflask — ready-to-paste additions for the teaching doc + slides

These are drafted for **Robin to paste into his own Google Doc / Slides** (his materials —
not edited directly). ✅ **The API is LIVE at https://api.ishweb.nl** (deployed 5 Jun 2026) —
every `api.ishweb.nl` URL below is real and clickable. The earlier ICDSoft "disk-space"
error was a false alarm and did not recur.

---

## A) For the Python/SQLite doc — turn the abstract "Option 2" into a real example

> **Try it live** — real, clickable URLs (the API is live now):
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

## B) New section — "Build your own database for your IA"

*Paste the block below into the doc after Option 2. (The same content is also a standalone, print-ready student handout: `handouts/ishflask_Student_IA_Handout.docx`.)*

> ### Build your own database app for your IA
>
> The class API ("ishflask") is also a **template you can copy** for your Internal Assessment. It is a safe, working starting point — your job is to make it your own.
>
> **Do you even need this?**  If your IA is a simple tool, plain Python + `sqlite3` (no web app) is a perfectly good IA and is simpler. Use this template only if you want a **web app / API** — a program that answers requests with data.
>
> **⚠️ What counts as YOUR work:**  your IA must be your own programming. The template is just a skeleton — you must supply your own database, your own routes, and your own SQL. **Do not submit the medical example.**
>
> **Step 1 — Design your database.**  In DB Browser for SQLite, create your own tables, fields and relationships for your topic (a gym, a library, a booking system…). Save it as `mydata.db`.
>
> **Step 2 — Get the template.**
> ```
> git clone https://github.com/tanasel/ishflask.git my-ia
> cd my-ia
> ```
> Then copy your `mydata.db` into the `databases/` folder.
>
> **Step 3 — Write your own routes** (this is your IA work). In `app.py`, delete the medical examples and write routes for your own tables:
> ```python
> @app.get("/members")
> def members():
>     return jsonify(query_db("databases/mydata.db",
>                             "SELECT * FROM Members"))
> ```
> Add the searches, filters and JOINs your project needs.
>
> **Step 4 — Let your app add and change data.**  The template only *reads* (it is read-only, for safety). A real app adds, edits and deletes records — this is where you show INSERT / UPDATE / DELETE (syllabus A3.3.3):
> ```python
> import sqlite3
>
> def write_db(sql, args=()):
>     conn = sqlite3.connect("databases/mydata.db")  # not read-only
>     conn.execute(sql, args)
>     conn.commit(); conn.close()
>
> @app.post("/members")
> def add_member():
>     d = request.get_json()
>     write_db("INSERT INTO Members (Name, Email) VALUES (?, ?)",
>              (d["name"], d["email"]))
>     return jsonify({"status": "added"})
> ```
> Always use `?` placeholders for values — never paste user input straight into an SQL string (that is how SQL injection happens).
>
> **Step 5 — Run it for your video.**
> ```
> python3 -m venv .venv
> source .venv/bin/activate        # Windows: .venv\Scripts\activate
> pip install -r requirements.txt
> flask --app app run              # open http://127.0.0.1:5000
> ```
> You do not need to host it online — running on your own laptop is fine for the 5-minute video.
>
> **Your checklist — "is this really mine?"**
> - ☐ My own database design (tables, fields, relationships)
> - ☐ My own routes in `app.py`
> - ☐ My own SQL queries, including at least one JOIN
> - ☐ Add / edit / delete works — not just read
> - ☐ I removed the medical example
>
> **Safety:** use made-up / sample data only. Never put real personal data in a database you publish online — anyone could read it.

*Teacher note (do not paste): a student who only swaps the `.db` and changes nothing else has not demonstrated the programming — the routes and the read + write logic must be their own.*

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
