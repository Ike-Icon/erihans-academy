# Erihans Wealth & Wellness Academy

The full site: 12 pages, one FastAPI app, one deploy. Shared header, nav
and footer live in a single template, so editing them once updates every
page.

```
Learn · Earn · Save · Invest · Live Well
```

---

## Pages

| Page                 | URL                                |
| -------------------- | ---------------------------------- |
| Home                 | `/`                              |
| About Us             | `/about`                         |
| Financial Education  | `/programs/financial-education`  |
| Money Management     | `/programs/money-management`     |
| Investment Education | `/programs/investment-education` |
| Entrepreneurship     | `/programs/entrepreneurship`     |
| Wealth Creation      | `/programs/wealth-creation`      |
| Wellness             | `/programs/wellness`             |
| Courses              | `/courses`                       |
| Events               | `/events`                        |
| Contact Us           | `/contact`                       |
| Student Registration | `/register`                      |

---

## What's in here

```
erihans-website/
  backend/
    main.py                     ← routes + the three form endpoints
    requirements.txt
    templates/
      base.html                 ← shared header, nav, footer — edit once
      pages/
        home.html
        about.html
        courses.html
        events.html
        contact.html
        register.html
        programs/
          financial-education.html
          money-management.html
          investment-education.html
          entrepreneurship.html
          wealth-creation.html
          wellness.html
    static/
      css/styles.css             ← the whole design system, one file
      js/script.js
      assets/                    ← drop real photos here (see below)
  render.yaml                    ← one-click Render deploy
```

Every page extends `base.html` and only fills in its own `{% block content %}`.
Change the nav, the footer contact details, or the "Student Registration"
button once in `base.html`, and it updates on all 12 pages.

---

## Quick start (2 minutes)

You need Python 3.10+. That's the only prerequisite.

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Open **http://127.0.0.1:8000** — that's the whole site. A SQLite file
(`erihans.db`) is created automatically on first run.

Interactive API docs: **http://127.0.0.1:8000/docs**

---

## Placeholder content — two pages need your real numbers

You asked to get the structure built now and fill in specifics later.
Two pages are marked clearly so nothing gets missed:

**Courses** (`templates/pages/courses.html`) — six cards, one per
program, with `[Course name]`, `[X weeks]`, `[GHS ___]` and
`[date]` placeholders. Each card also carries a small red
"Add real details" badge so it's obvious at a glance in the browser.

**Events** (`templates/pages/events.html`) — two example event cards
showing the layout. Replace the bracketed text, and copy the whole
`<article class="event-card">` block to add more events.

**Student Registration** (`templates/pages/register.html`) also has a
placeholder fee table — the form itself is fully working, only the
`[GHS ___]` prices need filling in.

Every placeholder uses square brackets, so you can search the codebase
for `[` to find everything still waiting on real content.

---

## How the forms work

Three forms, three endpoints, all storing to the same database:

| Form                 | Page               | Endpoint                 |
| -------------------- | ------------------ | ------------------------ |
| Student registration | `/register`      | `POST /api/enroll`     |
| Contact message      | `/contact`       | `POST /api/contact`    |
| Newsletter signup    | footer, every page | `POST /api/newsletter` |

**One nice touch:** every "Register for this program" button on a
program page links to `/register?program=financial_education` (etc.).
`script.js` reads that query parameter on load and pre-selects the
matching option in the registration form's dropdown, so someone
coming from the Wellness page doesn't have to re-select "Wellness"
themselves.

### Checking submissions

```
https://your-site.onrender.com/api/admin/enrollments
https://your-site.onrender.com/api/admin/messages
```

Both are protected with HTTP Basic Auth — your browser will prompt for
a username and password. Locally, the defaults are `admin` /
`change-me-before-deploying`. On Render, `render.yaml` generates a
strong random password automatically; find it under your service's
**Environment** tab as `ADMIN_PASSWORD`.

---

## Deploy it (Render, ~10 minutes)

1. **Push this repo to GitHub**, including `templates/` and `static/`.
2. Go to **[render.com](https://render.com) → New → Blueprint** and
   point it at your repo. Render reads `render.yaml` and provisions the
   web service and a free Postgres database together.
3. Click **Apply**. First deploy takes a few minutes.
4. Open the URL Render gives you. That's your live site, all 12 pages.

**Free tier note:** the web service sleeps after 15 minutes idle and
takes a few seconds to wake on the next visit. The free Postgres
database stays awake but gets deleted after 90 days of total
inactivity.

**Custom domain:** Render → your service → Settings → Custom Domains.

---

## Adding real photos

`static/css/styles.css` references image files that don't exist yet —
until you add them, each section falls back to a gradient, so nothing
looks broken in the meantime. Drop files into `static/assets/` with
these exact names:

```
hero-photo.jpg    education.jpg    money.jpg
invest.jpg        business.jpg     wealth.jpg
wellness.jpg
```

Free, commercially-licensed sources: unsplash.com, pexels.com,
pixabay.com — no attribution required on any of them.

---

## Troubleshooting

**A page shows a 500 error.** Almost always a typo in a Jinja template
(a `{% block %}` not closed, or a mismatched `{% endblock %}`). Check
the terminal running `uvicorn` — it prints the exact template and line.

**CSS or JS isn't loading.** Check that the reference in `base.html`
still points at `{{ url_for('static', path='css/styles.css') }}` —
don't hardcode `/static/css/styles.css` directly, `url_for` keeps it
correct if the mount path ever changes.

**New page not showing up.** Two things have to exist: the template
file under `templates/pages/`, and a matching `@app.get(...)` route in
`main.py` that renders it. Adding one without the other is the most
common mistake when copying an existing page to make a new one.

---

## Adding a 13th page later

1. Copy an existing simple page (e.g. `pages/contact.html`) to a new
   filename under `templates/pages/`.
2. Add a route in `main.py`:
   ```python
   @app.get("/new-page")
   def page_new(request: Request):
       return templates.TemplateResponse(request, "pages/new-page.html", {"active": "new_page"})
   ```
3. Add a link to it in `templates/base.html`'s nav and/or footer.

---

## Before you make it public

- [ ] Fill in the Courses and Events placeholder content (see above)
- [ ] Confirm `ADMIN_PASSWORD` on Render (see "Checking submissions")
- [ ] Add real photography to `static/assets/`
- [ ] Connect an email service so form submissions trigger a
  confirmation email
- [ ] Point your custom domain at the Render service

---

**Stack:** FastAPI · Jinja2 · SQLModel · SQLite (dev) / Postgres
(production) · plain CSS and JS — no build step, no framework, nothing
to compile.
