"""Demo data so the app isn't empty on first run.

Run `python -m facebook_clone.seed --reset` to wipe and re-seed the database.
"""

import sys
from datetime import timedelta

from sqlalchemy.exc import IntegrityError, ProgrammingError
from sqlmodel import SQLModel, select

from .models import Comment, Friendship, Like, Post, User, create_db, engine, get_session, utcnow
from .state import hash_password

DEMO_PASSWORD = "password"

USERS = [
    ("Mark", "Zuckerberg", "mark@example.com", "Menlo Park", "Building things. Connecting people."),
    ("Priscilla", "Chan", "priscilla@example.com", "Palo Alto", "Pediatrician & philanthropist."),
    ("Sheryl", "Sandberg", "sheryl@example.com", "Menlo Park", "Lean in."),
    ("Eduardo", "Saverin", "eduardo@example.com", "Singapore", "Investor. Co-founder."),
    ("Dustin", "Moskovitz", "dustin@example.com", "San Francisco", "Asana. Good Ventures."),
    ("Chris", "Hughes", "chris@example.com", "New York", "Writer and economist."),
    ("Ada", "Lovelace", "ada@example.com", "London", "First programmer. Big fan of engines."),
    ("Alan", "Turing", "alan@example.com", "Manchester", "Can machines think?"),
]

# (author index, content, image, hours ago)
POSTS = [
    (0, "Welcome to sudfa+! Built entirely in Python with Reflex. 🚀", "", 1),
    (1, "Beautiful morning hike with the family 🌄", "/seed/hike.svg", 3),
    (6, "Reminder: the Analytical Engine might act upon other things besides number. 🤔", "", 5),
    (2, "Proud of the team today. Keep leaning in!", "/seed/team.svg", 9),
    (7, "Proposed a little game today — let's call it the imitation game.", "", 20),
    (4, "Working from a coffee shop with a view ☕", "/seed/coffee.svg", 30),
    (3, "Throwback to the dorm room days.", "/seed/dorm.svg", 52),
    (5, "New essay out this week — would love your thoughts.", "", 75),
]

# Pairs of user indexes that are friends.
FRIENDS = [(0, 1), (0, 2), (0, 3), (0, 4), (0, 6), (1, 2), (4, 5), (6, 7), (2, 5)]
# Pending requests (requester, addressee).
PENDING = [(5, 0), (7, 0)]

COMMENTS = [
    (0, 1, "So proud of you! ❤️"),
    (0, 4, "Nice — does it scale?"),
    (1, 0, "Gorgeous view!"),
    (2, 7, "Agreed. Machines that can follow any rule, in principle."),
    (4, 6, "I'd like to play."),
]

LIKES = [(0, 1), (0, 2), (0, 3), (0, 4), (1, 0), (1, 2), (2, 7), (3, 0), (4, 6), (5, 0)]


def seed() -> None:
    now = utcnow()
    with get_session() as session:
        users = []
        for i, (first, last, email, city, bio) in enumerate(USERS):
            user = User(
                email=email,
                password_hash=hash_password(DEMO_PASSWORD),
                first_name=first,
                last_name=last,
                city=city,
                bio=bio,
                cover_url=f"/seed/cover{i}.svg",
                created_at=now - timedelta(days=400 - i * 30),
            )
            session.add(user)
            users.append(user)
        session.commit()
        for u in users:
            session.refresh(u)

        for a, b in FRIENDS:
            session.add(Friendship(requester_id=users[a].id, addressee_id=users[b].id, status="accepted"))
        for a, b in PENDING:
            session.add(Friendship(requester_id=users[a].id, addressee_id=users[b].id))

        posts = []
        for author, content, image, hours in POSTS:
            post = Post(
                author_id=users[author].id,
                content=content,
                image_url=image,
                created_at=now - timedelta(hours=hours),
            )
            session.add(post)
            posts.append(post)
        session.commit()
        for p in posts:
            session.refresh(p)

        for post_i, user_i, text in COMMENTS:
            session.add(
                Comment(
                    post_id=posts[post_i].id,
                    author_id=users[user_i].id,
                    content=text,
                    created_at=posts[post_i].created_at + timedelta(minutes=20),
                )
            )
        for post_i, user_i in LIKES:
            session.add(Like(post_id=posts[post_i].id, user_id=users[user_i].id))
        session.commit()


def init_db() -> None:
    """Create tables and seed demo data if the database is empty."""
    try:
        create_db()
        with get_session() as session:
            if session.exec(select(User)).first() is None:
                seed()
    except (IntegrityError, ProgrammingError):
        # Several server workers start at once; another one got here first.
        pass


if __name__ == "__main__":
    if "--reset" in sys.argv:
        SQLModel.metadata.drop_all(engine)
    init_db()
    print("Database ready. Demo login: mark@example.com / password")
