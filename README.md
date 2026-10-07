# Facebook clone with Reflex

A Facebook-style social network written entirely in Python with [Reflex](https://reflex.dev) and SQLModel (SQLite by default).

## Features

- **Accounts**: sign up, log in and log out. Passwords are hashed with PBKDF2, and the session token is kept in local storage.
- **News feed**: shows posts from you and your friends. You can create posts with text and a photo (upload a file or paste a URL), like, comment, and delete your own posts and comments.
- **Profiles**: cover photo, avatar, intro (bio, city, join date), a friends grid and the user's posts. You can edit your own profile.
- **Friends**: send, accept, decline and cancel friend requests, unfriend, and see "People you may know" with mutual-friend counts.
- **Search**: find people by name or email from the navbar.
- A responsive layout styled like Facebook.

## Run it

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
reflex run
```

Open http://localhost:3000. On first start the database is created and seeded with demo users.

**Demo login:** `mark@example.com` / `password` (every seeded user has the password `password`).

To wipe the database and re-seed it:

```bash
python -m facebook_clone.seed --reset
```

Set `DATABASE_URL` to use another database, for example Postgres.

## Project layout

```
rxconfig.py                  Reflex config (app name, theme)
facebook_clone/
  facebook_clone.py          App and page routes
  models.py                  SQLModel tables + engine
  state.py                   Auth, feed, profile, friends and search state
  seed.py                    Demo data
  components/                Navbar, layout, post card/composer, shared UI
  pages/                     login, home, profile, friends, search
assets/seed/                 Local SVG images used by the demo data
```
