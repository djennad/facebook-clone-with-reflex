"""Database models for sudfa+."""

import os
from datetime import datetime, timezone

import sqlmodel
from sqlmodel import Field, SQLModel, Session, create_engine

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///facebook.db")
# Some hosts hand out "postgres://" URLs, which SQLAlchemy doesn't accept.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = "postgresql://" + DATABASE_URL.removeprefix("postgres://")
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    pool_pre_ping=True,
)


def get_session() -> Session:
    return Session(engine)


def create_db() -> None:
    SQLModel.metadata.create_all(engine)


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(SQLModel, table=True):
    """A registered user."""

    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    password_hash: str
    first_name: str
    last_name: str
    bio: str = ""
    avatar_url: str = ""
    cover_url: str = ""
    city: str = ""
    created_at: datetime = Field(default_factory=utcnow)

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()


class AuthSession(SQLModel, table=True):
    """A login session; the token is kept in the browser's local storage."""

    id: int | None = Field(default=None, primary_key=True)
    token: str = Field(unique=True, index=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    created_at: datetime = Field(default_factory=utcnow)


class Post(SQLModel, table=True):
    """A status update on the news feed."""

    id: int | None = Field(default=None, primary_key=True)
    author_id: int = Field(foreign_key="user.id", index=True)
    content: str = ""
    image_url: str = ""
    created_at: datetime = Field(default_factory=utcnow, index=True)


class Comment(SQLModel, table=True):
    """A comment on a post."""

    id: int | None = Field(default=None, primary_key=True)
    post_id: int = Field(foreign_key="post.id", index=True)
    author_id: int = Field(foreign_key="user.id")
    content: str
    created_at: datetime = Field(default_factory=utcnow)


class Like(SQLModel, table=True):
    """A like on a post (one per user per post)."""

    __table_args__ = (sqlmodel.UniqueConstraint("post_id", "user_id"),)

    id: int | None = Field(default=None, primary_key=True)
    post_id: int = Field(foreign_key="post.id", index=True)
    user_id: int = Field(foreign_key="user.id")


class Friendship(SQLModel, table=True):
    """A friend request; status is "pending" or "accepted"."""

    __table_args__ = (sqlmodel.UniqueConstraint("requester_id", "addressee_id"),)

    id: int | None = Field(default=None, primary_key=True)
    requester_id: int = Field(foreign_key="user.id", index=True)
    addressee_id: int = Field(foreign_key="user.id", index=True)
    status: str = "pending"
    created_at: datetime = Field(default_factory=utcnow)
