"""A Facebook clone built with Reflex."""

import reflex as rx

from .pages.friends import friends_page
from .pages.home import home_page
from .pages.login import login_page
from .pages.profile import profile_page
from .pages.search import search_page
from .seed import init_db
from .state import AuthState, FriendsState, HomeState, ProfileState, SearchState

init_db()

app = rx.App(
    style={"font_family": "Helvetica, Arial, sans-serif"},
)

app.add_page(home_page, route="/", title="Facebook", on_load=HomeState.load_home)
app.add_page(login_page, route="/login", title="Facebook – log in or sign up", on_load=AuthState.redirect_if_logged_in)
app.add_page(profile_page, route="/profile/[uid]", title="Profile | Facebook", on_load=ProfileState.load_profile)
app.add_page(friends_page, route="/friends", title="Friends | Facebook", on_load=FriendsState.load_friends)
app.add_page(search_page, route="/search", title="Search | Facebook", on_load=SearchState.load_search)
