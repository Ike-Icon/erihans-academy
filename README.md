# Erihans Wealth & Wellness Academy — website

A landing page and mission/vision page for the academy, plus a FastAPI
backend for the enrollment form and newsletter signup. The backend also
serves the frontend files, so the whole site is one app, one deploy,
one URL.

```
erihans-website/
  frontend/
    index.html
    mission-vision.html
    styles.css
    script.js
  backend/
    main.py
    requirements.txt
  render.yaml
```

## Run it locally

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Open `http://127.0.0.1:8000` — that's the whole site, frontend and API
together. It creates `erihans.db` (SQLite) on first run, no separate
database setup needed for local development.

Endpoints:
- `GET  /api/health` — health check
- `GET  /api/programs` — the five program listings
- `POST /api/enroll` — enrollment / callback request form
- `POST /api/newsletter` — newsletter signup
- `GET  /api/admin/enrollments` — lists submitted enrollments (add auth before using this outside local dev)

Interactive API docs: `http://127.0.0.1:8000/docs`

## Deploy to Render (recommended)

Render will host the API, serve the frontend, and give you a free
managed Postgres database, so your leads survive redeploys.

1. **Push this folder to a GitHub repo.** Render deploys from a repo,
   not a local folder.
2. **Go to [render.com](https://render.com) → New → Blueprint.**
   Point it at your repo. Render reads `render.yaml` at the repo root
   and sets up both the web service and the database automatically —
   you shouldn't need to fill in build/start commands by hand.
3. **Click Apply.** First deploy takes a few minutes. Render installs
   `backend/requirements.txt`, starts Uvicorn, and wires the
   `DATABASE_URL` environment variable to the new Postgres database
   for you.
4. **Open the URL Render gives you** (something like
   `https://erihans-academy.onrender.com`). That's your live site —
   frontend and API both, same domain.
5. **Submit a test enrollment** through the live form, then check it
   landed in the database: visit `/api/admin/enrollments` on your live
   URL. Once you confirm this endpoint works, restrict it (see below)
   so it isn't public.

**Free tier note:** the free web service sleeps after 15 minutes of no
traffic and takes a few seconds to wake on the next visit. That's fine
for a course-enrollment site with steady but not constant traffic. If
that wake-up delay bothers you, Render's paid tier ($7/month) keeps it
always on. The free Postgres database doesn't sleep, but Render does
delete unused free databases after 90 days of inactivity, so if the
site goes quiet for that long, revisit it.

**Custom domain:** once deployed, Render → your service → Settings →
Custom Domains lets you point `erihansacademy.com` at it with a CNAME
record. Render issues the SSL certificate automatically.

### Railway, as an alternative

Same idea, different dashboard: New Project → Deploy from GitHub →
Railway auto-detects the FastAPI app. Add a Postgres plugin from their
marketplace, and it sets `DATABASE_URL` for you the same way Render
does. Slightly less generous free tier, but the workflow is nearly
identical.

## If you'd rather split frontend and backend across two hosts

You don't need this for a site this size, but if you later hand the
frontend to a separate team or a no-code page builder:

- Deploy `backend/` to Render or Railway as above.
- Deploy `frontend/` to Netlify or Vercel (drag-and-drop the folder,
  or connect the repo).
- In `frontend/script.js`, set `API_BASE` to your backend's real URL,
  e.g. `"https://erihans-api.onrender.com"`.
- In `backend/main.py`, replace the wildcard in `allow_origins` with
  your actual Netlify/Vercel domain.

## Before going to production

- **Set a real admin password.** `/api/admin/enrollments` is now
  protected with a username and password (the browser will prompt for
  them — no extra frontend page needed). Locally it defaults to
  `admin` / `change-me-before-deploying` so it still works out of the
  box, but on Render, `render.yaml` generates a random password for
  you automatically as the `ADMIN_PASSWORD` environment variable — go
  to your service → Environment in the Render dashboard to see it (or
  set your own). Change `ADMIN_USERNAME` there too if you don't want
  it to stay as `admin`.
- Add real photography to `frontend/styles.css` in place of the
  gradient placeholders (`.hero-photo`, `.approach-img--*`).
- Wire up an email service (e.g. SES, Postmark) so enrollment and
  newsletter submissions trigger a confirmation email.
- If you split frontend/backend (above), tighten `allow_origins` in
  `main.py` to your real domain instead of the wildcard `*`.

