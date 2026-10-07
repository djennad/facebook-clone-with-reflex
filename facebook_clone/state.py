"""Application state: authentication, feed, profiles, friends and search."""

import dataclasses
import hashlib
import hmac
import re
import secrets
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

import reflex as rx
from sqlmodel import Session, col, delete, func, or_, select

from .models import (
    AuthSession,
    Comment,
    Friendship,
    Like,
    Post,
    User,
    get_session,
    utcnow,
)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
ALLOWED_IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".gif", ".webp"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 200_000)
    return f"{salt}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt, digest = stored.split("$", 1)
    except ValueError:
        return False
    candidate = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt.encode(), 200_000
    )
    return hmac.compare_digest(candidate.hex(), digest)


def time_ago(when: datetime) -> str:
    seconds = int((utcnow() - when).total_seconds())
    if seconds < 60:
        return "Just now"
    if seconds < 3600:
        return f"{seconds // 60}m"
    if seconds < 86400:
        return f"{seconds // 3600}h"
    if seconds < 7 * 86400:
        return f"{seconds // 86400}d"
    return when.strftime("%b %d, %Y")


def initials(user: User) -> str:
    return (user.first_name[:1] + user.last_name[:1]).upper() or "?"


def friend_ids(session: Session, user_id: int) -> list[int]:
    rows = session.exec(
        select(Friendship).where(
            Friendship.status == "accepted",
            or_(Friendship.requester_id == user_id, Friendship.addressee_id == user_id),
        )
    ).all()
    return [r.addressee_id if r.requester_id == user_id else r.requester_id for r in rows]


def friendship_between(session: Session, a: int, b: int) -> Friendship | None:
    return session.exec(
        select(Friendship).where(
            or_(
                (Friendship.requester_id == a) & (Friendship.addressee_id == b),
                (Friendship.requester_id == b) & (Friendship.addressee_id == a),
            )
        )
    ).first()


def friend_status(session: Session, me: int, other: int) -> str:
    """One of: self, friends, sent, received, none."""
    if me == other:
        return "self"
    f = friendship_between(session, me, other)
    if f is None:
        return "none"
    if f.status == "accepted":
        return "friends"
    return "sent" if f.requester_id == me else "received"


# ---------------------------------------------------------------------------
# View models sent to the frontend
# ---------------------------------------------------------------------------


@dataclasses.dataclass
class UserCard:
    id: int = 0
    name: str = ""
    avatar: str = ""
    initials: str = ""
    subtitle: str = ""


@dataclasses.dataclass
class CommentView:
    id: int = 0
    author_id: int = 0
    author_name: str = ""
    author_avatar: str = ""
    author_initials: str = ""
    content: str = ""
    time_ago: str = ""
    can_delete: bool = False


@dataclasses.dataclass
class PostView:
    id: int = 0
    author_id: int = 0
    author_name: str = ""
    author_avatar: str = ""
    author_initials: str = ""
    content: str = ""
    image_url: str = ""
    image_is_upload: bool = False
    time_ago: str = ""
    like_count: int = 0
    liked: bool = False
    comment_count: int = 0
    comments: list[CommentView] = dataclasses.field(default_factory=list)
    can_delete: bool = False


def user_card(user: User, subtitle: str = "") -> UserCard:
    return UserCard(
        id=user.id or 0,
        name=user.full_name,
        avatar=user.avatar_url,
        initials=initials(user),
        subtitle=subtitle,
    )


def build_post_views(session: Session, posts: list[Post], viewer_id: int) -> list[PostView]:
    if not posts:
        return []
    post_ids = [p.id for p in posts]
    comments = session.exec(
        select(Comment)
        .where(col(Comment.post_id).in_(post_ids))
        .order_by(col(Comment.created_at))
    ).all()
    likes = session.exec(select(Like).where(col(Like.post_id).in_(post_ids))).all()
    user_ids = {p.author_id for p in posts} | {c.author_id for c in comments}
    users = {
        u.id: u for u in session.exec(select(User).where(col(User.id).in_(user_ids))).all()
    }

    views = []
    for p in posts:
        author = users[p.author_id]
        post_likes = [lk for lk in likes if lk.post_id == p.id]
        post_comments = [
            CommentView(
                id=c.id or 0,
                author_id=c.author_id,
                author_name=users[c.author_id].full_name,
                author_avatar=users[c.author_id].avatar_url,
                author_initials=initials(users[c.author_id]),
                content=c.content,
                time_ago=time_ago(c.created_at),
                can_delete=viewer_id in (c.author_id, p.author_id),
            )
            for c in comments
            if c.post_id == p.id
        ]
        views.append(
            PostView(
                id=p.id or 0,
                author_id=p.author_id,
                author_name=author.full_name,
                author_avatar=author.avatar_url,
                author_initials=initials(author),
                content=p.content,
                image_url=p.image_url,
                image_is_upload=bool(p.image_url) and not p.image_url.startswith(("http", "/")),
                time_ago=time_ago(p.created_at),
                like_count=len(post_likes),
                liked=any(lk.user_id == viewer_id for lk in post_likes),
                comment_count=len(post_comments),
                comments=post_comments,
                can_delete=p.author_id == viewer_id,
            )
        )
    return views


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------


class AuthState(rx.State):
    """Tracks the logged-in user. Every other state inherits from this one."""

    auth_token: str = rx.LocalStorage(name="fb_auth_token")
    user_id: int = 0
    first_name: str = ""
    last_name: str = ""
    email: str = ""
    avatar: str = ""
    auth_error: str = ""

    @rx.var
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    @rx.var
    def user_initials(self) -> str:
        return (self.first_name[:1] + self.last_name[:1]).upper()

    @rx.var
    def is_logged_in(self) -> bool:
        return self.user_id > 0

    def _set_user(self, user: User | None):
        self.user_id = user.id if user else 0
        self.first_name = user.first_name if user else ""
        self.last_name = user.last_name if user else ""
        self.email = user.email if user else ""
        self.avatar = user.avatar_url if user else ""

    def _load_user(self) -> bool:
        if not self.auth_token:
            self._set_user(None)
            return False
        with get_session() as session:
            auth = session.exec(
                select(AuthSession).where(AuthSession.token == self.auth_token)
            ).first()
            user = session.get(User, auth.user_id) if auth else None
            self._set_user(user)
        return user is not None

    def _start_session(self, user: User, session: Session):
        token = secrets.token_urlsafe(32)
        session.add(AuthSession(token=token, user_id=user.id))
        session.commit()
        self.auth_token = token
        self._set_user(user)

    @rx.event
    def require_login(self):
        """on_load guard for pages that need a logged-in user."""
        if not self._load_user():
            return rx.redirect("/login")

    @rx.event
    def redirect_if_logged_in(self):
        self.auth_error = ""
        if self._load_user():
            return rx.redirect("/")

    @rx.event
    def login(self, form_data: dict):
        email = form_data.get("email", "").strip().lower()
        password = form_data.get("password", "")
        with get_session() as session:
            user = session.exec(select(User).where(User.email == email)).first()
            if user is None or not verify_password(password, user.password_hash):
                self.auth_error = "The email or password you entered is incorrect."
                return
            self._start_session(user, session)
        self.auth_error = ""
        return rx.redirect("/")

    @rx.event
    def signup(self, form_data: dict):
        first = form_data.get("first_name", "").strip()
        last = form_data.get("last_name", "").strip()
        email = form_data.get("email", "").strip().lower()
        password = form_data.get("password", "")
        if not first or not last:
            self.auth_error = "What's your name?"
            return
        if not EMAIL_RE.match(email):
            self.auth_error = "Please enter a valid email address."
            return
        if len(password) < 6:
            self.auth_error = "Your password must be at least 6 characters."
            return
        with get_session() as session:
            if session.exec(select(User).where(User.email == email)).first():
                self.auth_error = "An account with this email already exists."
                return
            user = User(
                email=email,
                password_hash=hash_password(password),
                first_name=first,
                last_name=last,
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            self._start_session(user, session)
        self.auth_error = ""
        return rx.redirect("/")

    @rx.event
    def logout(self):
        if self.auth_token:
            with get_session() as session:
                session.exec(delete(AuthSession).where(AuthSession.token == self.auth_token))
                session.commit()
        self.auth_token = ""
        self._set_user(None)
        return rx.redirect("/login")


# ---------------------------------------------------------------------------
# Posts (shared by the news feed and profile pages)
# ---------------------------------------------------------------------------


class PostsState(AuthState):
    """A list of posts. `scope_user_id == 0` means the news feed."""

    posts: list[PostView] = []
    scope_user_id: int = 0
    new_post_text: str = ""
    new_post_image: str = ""
    composer_open: bool = False

    @rx.event
    def set_new_post_text(self, value: str):
        self.new_post_text = value

    @rx.event
    def set_new_post_image(self, value: str):
        self.new_post_image = value

    @rx.event
    def set_composer_open(self, value: bool):
        self.composer_open = value
        if not value:
            self.new_post_text = ""
            self.new_post_image = ""

    def _reload_posts(self):
        with get_session() as session:
            if self.scope_user_id:
                author_ids = [self.scope_user_id]
            else:
                author_ids = [self.user_id, *friend_ids(session, self.user_id)]
            posts = session.exec(
                select(Post)
                .where(col(Post.author_id).in_(author_ids))
                .order_by(col(Post.created_at).desc())
                .limit(50)
            ).all()
            self.posts = build_post_views(session, list(posts), self.user_id)

    @rx.event
    async def handle_image_upload(self, files: list[rx.UploadFile]):
        for file in files[:1]:
            suffix = Path(file.name or "").suffix.lower()
            if suffix not in ALLOWED_IMAGE_SUFFIXES:
                return rx.toast.error("Please choose an image file.")
            data = await file.read()
            name = f"{secrets.token_hex(8)}{suffix}"
            upload_dir = rx.get_upload_dir()
            upload_dir.mkdir(parents=True, exist_ok=True)
            (upload_dir / name).write_bytes(data)
            self.new_post_image = name

    @rx.event
    def create_post(self):
        text = self.new_post_text.strip()
        image = self.new_post_image.strip()
        if not text and not image:
            return
        with get_session() as session:
            session.add(Post(author_id=self.user_id, content=text, image_url=image))
            session.commit()
        self.new_post_text = ""
        self.new_post_image = ""
        self.composer_open = False
        self._reload_posts()

    @rx.event
    def toggle_like(self, post_id: int):
        with get_session() as session:
            existing = session.exec(
                select(Like).where(Like.post_id == post_id, Like.user_id == self.user_id)
            ).first()
            if existing:
                session.delete(existing)
            else:
                session.add(Like(post_id=post_id, user_id=self.user_id))
            session.commit()
        self._reload_posts()

    @rx.event
    def add_comment(self, form_data: dict):
        text = form_data.get("comment", "").strip()
        post_id = str(form_data.get("post_id", ""))
        if not text or not post_id.isdigit():
            return
        post_id = int(post_id)
        with get_session() as session:
            if session.get(Post, post_id) is None:
                return
            session.add(Comment(post_id=post_id, author_id=self.user_id, content=text))
            session.commit()
        self._reload_posts()

    @rx.event
    def delete_comment(self, comment_id: int):
        with get_session() as session:
            comment = session.get(Comment, comment_id)
            if comment is None:
                return
            post = session.get(Post, comment.post_id)
            if self.user_id not in (comment.author_id, post.author_id if post else 0):
                return
            session.delete(comment)
            session.commit()
        self._reload_posts()

    @rx.event
    def delete_post(self, post_id: int):
        with get_session() as session:
            post = session.get(Post, post_id)
            if post is None or post.author_id != self.user_id:
                return
            session.exec(delete(Comment).where(Comment.post_id == post_id))
            session.exec(delete(Like).where(Like.post_id == post_id))
            session.delete(post)
            session.commit()
        self._reload_posts()
        return rx.toast("Post deleted")


class HomeState(PostsState):
    """News feed page with contacts and friend suggestions."""

    contacts: list[UserCard] = []
    suggestions: list[UserCard] = []
    request_count: int = 0

    @rx.event
    def load_home(self):
        if not self._load_user():
            return rx.redirect("/login")
        self.scope_user_id = 0
        self._reload_posts()
        with get_session() as session:
            ids = friend_ids(session, self.user_id)
            friends = session.exec(select(User).where(col(User.id).in_(ids))).all()
            self.contacts = [user_card(u) for u in friends]
            self.suggestions = suggest_people(session, self.user_id, limit=4)
            self.request_count = pending_request_count(session, self.user_id)


def suggest_people(session: Session, user_id: int, limit: int = 10) -> list[UserCard]:
    related = session.exec(
        select(Friendship).where(
            or_(Friendship.requester_id == user_id, Friendship.addressee_id == user_id)
        )
    ).all()
    excluded = {user_id} | {r.requester_id for r in related} | {r.addressee_id for r in related}
    my_friends = set(friend_ids(session, user_id))
    candidates = session.exec(
        select(User).where(col(User.id).not_in(excluded)).order_by(col(User.created_at).desc())
    ).all()
    cards = []
    for u in candidates:
        mutual = len(my_friends & set(friend_ids(session, u.id)))
        cards.append((mutual, user_card(u, f"{mutual} mutual friends" if mutual else "")))
    cards.sort(key=lambda pair: -pair[0])
    return [card for _, card in cards[:limit]]


def pending_request_count(session: Session, user_id: int) -> int:
    return session.exec(
        select(func.count())
        .select_from(Friendship)
        .where(Friendship.addressee_id == user_id, Friendship.status == "pending")
    ).one()


# ---------------------------------------------------------------------------
# Friend actions (used by profile, friends and search pages)
# ---------------------------------------------------------------------------


def send_friend_request(me: int, other: int):
    with get_session() as session:
        if me == other or session.get(User, other) is None:
            return
        if friendship_between(session, me, other) is None:
            session.add(Friendship(requester_id=me, addressee_id=other))
            session.commit()


def accept_friend_request(me: int, other: int):
    with get_session() as session:
        f = friendship_between(session, me, other)
        if f and f.status == "pending" and f.addressee_id == me:
            f.status = "accepted"
            session.add(f)
            session.commit()


def remove_friendship(me: int, other: int):
    """Unfriend, cancel a sent request, or decline a received one."""
    with get_session() as session:
        f = friendship_between(session, me, other)
        if f:
            session.delete(f)
            session.commit()


class ProfileState(PostsState):
    """A user's profile page."""

    profile: UserCard = UserCard()
    profile_bio: str = ""
    profile_city: str = ""
    profile_cover: str = ""
    profile_joined: str = ""
    profile_friend_status: str = "none"
    profile_friends: list[UserCard] = []
    profile_friend_count: int = 0
    profile_not_found: bool = False
    edit_open: bool = False

    @rx.var
    def is_own_profile(self) -> bool:
        return self.profile_friend_status == "self"

    def _profile_id_from_url(self) -> int:
        last = self.router.url.path.rstrip("/").rsplit("/", 1)[-1]
        return int(last) if last.isdigit() else 0

    def _reload_profile(self):
        with get_session() as session:
            user = session.get(User, self.scope_user_id) if self.scope_user_id else None
            self.profile_not_found = user is None
            if user is None:
                self.posts = []
                return
            self.profile = user_card(user)
            self.profile_bio = user.bio
            self.profile_city = user.city
            self.profile_cover = user.cover_url
            self.profile_joined = user.created_at.strftime("%B %Y")
            self.profile_friend_status = friend_status(session, self.user_id, user.id)
            ids = friend_ids(session, user.id)
            self.profile_friend_count = len(ids)
            friends = session.exec(select(User).where(col(User.id).in_(ids)).limit(9)).all()
            self.profile_friends = [user_card(u) for u in friends]
        self._reload_posts()

    @rx.event
    def load_profile(self):
        if not self._load_user():
            return rx.redirect("/login")
        self.scope_user_id = self._profile_id_from_url() or self.user_id
        self.edit_open = False
        self._reload_profile()

    @rx.event
    def add_friend(self):
        send_friend_request(self.user_id, self.scope_user_id)
        self._reload_profile()

    @rx.event
    def accept_friend(self):
        accept_friend_request(self.user_id, self.scope_user_id)
        self._reload_profile()

    @rx.event
    def remove_friend(self):
        remove_friendship(self.user_id, self.scope_user_id)
        self._reload_profile()

    @rx.event
    def set_edit_open(self, value: bool):
        self.edit_open = value

    @rx.event
    def save_profile(self, form_data: dict):
        with get_session() as session:
            user = session.get(User, self.user_id)
            if user is None:
                return
            user.first_name = form_data.get("first_name", "").strip() or user.first_name
            user.last_name = form_data.get("last_name", "").strip() or user.last_name
            user.bio = form_data.get("bio", "").strip()[:300]
            user.city = form_data.get("city", "").strip()[:100]
            user.avatar_url = form_data.get("avatar_url", "").strip()
            user.cover_url = form_data.get("cover_url", "").strip()
            session.add(user)
            session.commit()
            self._set_user(user)
        self.edit_open = False
        self._reload_profile()
        return rx.toast.success("Profile updated")


# ---------------------------------------------------------------------------
# Friends page
# ---------------------------------------------------------------------------


class FriendsState(AuthState):
    requests: list[UserCard] = []
    sent: list[UserCard] = []
    friends: list[UserCard] = []
    suggestions: list[UserCard] = []

    def _reload(self):
        with get_session() as session:
            incoming = session.exec(
                select(Friendship).where(
                    Friendship.addressee_id == self.user_id, Friendship.status == "pending"
                )
            ).all()
            outgoing = session.exec(
                select(Friendship).where(
                    Friendship.requester_id == self.user_id, Friendship.status == "pending"
                )
            ).all()

            def cards(ids: list[int]) -> list[UserCard]:
                users = session.exec(select(User).where(col(User.id).in_(ids))).all()
                return [user_card(u) for u in users]

            self.requests = cards([f.requester_id for f in incoming])
            self.sent = cards([f.addressee_id for f in outgoing])
            self.friends = cards(friend_ids(session, self.user_id))
            self.suggestions = suggest_people(session, self.user_id, limit=12)

    @rx.event
    def load_friends(self):
        if not self._load_user():
            return rx.redirect("/login")
        self._reload()

    @rx.event
    def add_friend(self, other: int):
        send_friend_request(self.user_id, other)
        self._reload()
        return rx.toast("Friend request sent")

    @rx.event
    def accept(self, other: int):
        accept_friend_request(self.user_id, other)
        self._reload()

    @rx.event
    def remove(self, other: int):
        remove_friendship(self.user_id, other)
        self._reload()


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------


@dataclasses.dataclass
class SearchResult:
    user: UserCard = dataclasses.field(default_factory=UserCard)
    status: str = "none"


class SearchState(AuthState):
    query: str = ""
    results: list[SearchResult] = []

    @rx.event
    def submit_search(self, form_data: dict):
        q = form_data.get("q", "").strip()
        if q:
            return rx.redirect(f"/search?q={quote(q)}")

    def _reload(self):
        terms = self.query.split()
        if not terms:
            self.results = []
            return
        with get_session() as session:
            stmt = select(User)
            for term in terms:
                like = f"%{term}%"
                stmt = stmt.where(
                    or_(
                        col(User.first_name).ilike(like),
                        col(User.last_name).ilike(like),
                        col(User.email).ilike(like),
                    )
                )
            users = session.exec(stmt.limit(30)).all()
            self.results = [
                SearchResult(
                    user=user_card(u, u.city and f"Lives in {u.city}"),
                    status=friend_status(session, self.user_id, u.id),
                )
                for u in users
            ]

    @rx.event
    def load_search(self):
        if not self._load_user():
            return rx.redirect("/login")
        self.query = self.router.url.query_parameters.get("q", "")
        self._reload()

    @rx.event
    def add_friend(self, other: int):
        send_friend_request(self.user_id, other)
        self._reload()

    @rx.event
    def accept(self, other: int):
        accept_friend_request(self.user_id, other)
        self._reload()
