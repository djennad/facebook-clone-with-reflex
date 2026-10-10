# sudfa+

**sudfa+** is a small social network written entirely in Python with [Reflex](https://reflex.dev) and SQLModel (SQLite by default).

## Features

- **Accounts**: sign up, log in and log out. Passwords are hashed with PBKDF2, and the session token is kept in local storage.
- **News feed**: shows posts from you and your friends. You can create posts with text and a photo (upload a file or paste a URL), like, comment, and delete your own posts and comments.
- **Profiles**: cover photo, avatar, intro (bio, city, join date), a friends grid and the user's posts. You can edit your own profile.
- **Friends**: send, accept, decline and cancel friend requests, unfriend, and see "People you may know" with mutual-friend counts.
- **Search**: find people by name or email from the navbar.
- A responsive layout that works on phones.

## Run it

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
reflex run
```

Open http://localhost:3000. On first start the database is created and seeded with demo users.

**Demo login:** `amina@example.com` / `password` (every seeded user has the password `password`).

To wipe the database and re-seed it:

```bash
python -m facebook_clone.seed --reset
```

Set `DATABASE_URL` to use another database, for example Postgres.

## Deploy to Render

The repo includes a `Dockerfile` and a `render.yaml` Blueprint that creates the web service and a free Postgres database.

1. In the [Render dashboard](https://dashboard.render.com), choose **New → Blueprint** and select this repository.
2. Click **Apply**. The first deploy takes a few minutes; the app is then live at `https://<service-name>.onrender.com`.

The app reads `RENDER_EXTERNAL_URL`, which Render sets automatically, so the browser connects to the right address. On any other host, set `API_URL` to the site's public URL.

Notes:
- Free web services sleep after 15 minutes without traffic, so the next visit takes about a minute to wake up.
- Render deletes free Postgres databases 30 days after creation unless you upgrade them.
- Uploaded photos are stored on the service's disk, which is wiped on every deploy or restart. Attach a Render disk at `/app/uploaded_files` (paid plans) to keep them.

## Project layout

```
rxconfig.py                  Reflex config (app name, theme, public URL)
Dockerfile, render.yaml      Production container and Render Blueprint
facebook_clone/
  facebook_clone.py          App and page routes
  models.py                  SQLModel tables + engine
  state.py                   Auth, feed, profile, friends and search state
  seed.py                    Demo data
  components/                Navbar, layout, post card/composer, shared UI
  pages/                     login, home, profile, friends, search
assets/seed/                 Local SVG images used by the demo data
```
