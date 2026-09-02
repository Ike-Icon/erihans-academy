# Erihans Wealth & Wellness Academy

The official website: a landing page, a mission & vision page, and a FastAPI
backend that captures enrollment inquiries and newsletter signups. One app,
one deploy, one URL — the backend serves the frontend itself, so there's no
separate hosting to juggle.

```
Learn · Earn · Save · Invest · Live Well
```

---

## What's in here

| Piece                            | What it does                                                          |
| -------------------------------- | --------------------------------------------------------------------- |
| `frontend/index.html`          | The homepage — hero, five programs, gallery, values, enrollment form |
| `frontend/mission-vision.html` | Vision, mission and commitment statement                              |
| `frontend/styles.css`          | The full navy-and-gold design system, one file                        |
| `frontend/script.js`           | Mobile nav toggle + form submissions to the API                       |
| `backend/main.py`              | FastAPI app: serves the frontend and handles form data                |
| `backend/requirements.txt`     | Python dependencies                                                   |
| `render.yaml`                  | One-click deploy blueprint for Render                                 |

---

## Quick start (2 minutes)

You need Python 3.10+ installed. That's the only prerequisite.

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Open **http://127.0.0.1:8000** — that's the whole site, frontend and API
together, running from one process. A SQLite file (`erihans.db`) is created
automatically on first run, so there's nothing else to set up.

Try the interactive API docs at **http://127.0.0.1:8000/docs** — you can
fire test requests at every endpoint straight from the browser.

---

## How it fits together

The backend does double duty. `main.py` defines the `/api/*` routes first,
then mounts the `frontend/` folder to serve everything else:

```python
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
```

That mount has to stay **last** in the file. Routes are matched top to
bottom, and this one matches almost anything, so anything registered after
it would never be reached.

Because of this, file paths matter. If `styles.css` lives at
`frontend/styles.css` on disk, the browser fetches it from `/styles.css` —
**not** `/frontend/styles.css`. The `frontend/` folder becomes your site
root once it's mounted; don't reference it by name inside your own HTML.
(See **Troubleshooting** below — this is the single most common way people
get a working site locally and a blank, unstyled page after deploying.)

### API endpoints

| Method   | Path                       | Purpose                                                              |
| -------- | -------------------------- | -------------------------------------------------------------------- |
| `GET`  | `/api/health`            | Health check                                                         |
| `GET`  | `/api/programs`          | The five program listings, as JSON                                   |
| `POST` | `/api/enroll`            | Enrollment / callback request form                                   |
| `POST` | `/api/newsletter`        | Newsletter signup                                                    |
| `GET`  | `/api/admin/enrollments` | Every submitted enrollment —**password protected**, see below |

---

## Deploy it (Render, ~10 minutes)

Render hosts the app, serves the frontend, and gives you a free managed
Postgres database, so enrollment data survives redeploys instead of living
in a SQLite file that resets.

1. **Push this repo to GitHub.** Render deploys from a repo, not a local
   folder — commit everything, including `frontend/`.
2. Go to **[render.com](https://render.com) → New → Blueprint** and point it
   at your repo. Render reads `render.yaml` and provisions the web service
   *and* the database together — no manual build/start command entry.
3. Click **Apply**. First deploy takes a few minutes.
4. Open the URL Render gives you (something like
   `https://erihans-academy.onrender.com`). That's your live site.
5. Submit a test enrollment through the live form, then confirm it saved —
   see **Checking submissions** below.

**Free tier note:** the web service sleeps after 15 minutes idle and takes
a few seconds to wake on the next visit. Fine for steady-but-not-constant
traffic; upgrade to the $7/month tier if that wake delay is a problem. The
free Postgres database stays awake but gets deleted after 90 days of
total inactivity — worth remembering if the site goes quiet for a season.

**Custom domain:** Render → your service → Settings → Custom Domains. Point
a CNAME at it; Render issues the SSL certificate automatically, no extra
steps.

---

## Checking submissions

Enrollment inquiries land in the database, viewable at:

```
https://erihans-academy.onrender.com/index.html#enroll
```

This is protected with a username and password — your browser will prompt
for them. Locally, the defaults are `admin` / `change-me-before-deploying`.
On Render, `render.yaml` generates a strong random password for you
automatically; find it under your service's **Environment** tab as
`ADMIN_PASSWORD`. Change either value there whenever you like.

---
