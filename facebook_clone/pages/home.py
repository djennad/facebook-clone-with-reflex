"""News feed (home) page."""

import reflex as rx

from ..components.common import TEXT_MUTED, profile_link, sidebar_item, user_avatar
from ..components.layout import app_layout
from ..components.post import composer, post_list
from ..state import AuthState, FriendsState, HomeState, UserCard


def left_sidebar() -> rx.Component:
    return rx.vstack(
        profile_link(
            AuthState.user_id,
            rx.hstack(
                user_avatar(AuthState.avatar, AuthState.user_initials, size="2"),
                rx.text(AuthState.full_name, weight="medium", size="2"),
                align="center",
                spacing="3",
            ),
            padding="8px",
            border_radius="8px",
            width="100%",
            _hover={"background": "#E4E6E9"},
        ),
        sidebar_item(
            "users",
            rx.cond(
                HomeState.request_count > 0,
                f"Friends ({HomeState.request_count})",
                "Friends",
            ),
            "/friends",
        ),
        sidebar_item("newspaper", "Feed", "/"),
        sidebar_item("search", "Find people", "/search"),
        sidebar_item("circle-user-round", "Your profile", f"/profile/{AuthState.user_id}"),
        rx.separator(margin_y="8px"),
        rx.text(
            "Privacy · Terms · Advertising · Cookies · Meta © 2026 (just a clone!)",
            size="1",
            color=TEXT_MUTED,
            padding_x="8px",
        ),
        position="sticky",
        top="72px",
        width="280px",
        spacing="1",
        display=["none", "none", "none", "flex"],
    )


def contact_item(user: UserCard) -> rx.Component:
    return profile_link(
        user.id,
        rx.hstack(
            rx.box(
                user_avatar(user.avatar, user.initials, size="2"),
                rx.box(
                    width="10px",
                    height="10px",
                    background="#31A24C",
                    border="2px solid #F0F2F5",
                    border_radius="50%",
                    position="absolute",
                    bottom="0",
                    right="0",
                ),
                position="relative",
            ),
            rx.text(user.name, size="2", weight="medium"),
            align="center",
            spacing="3",
        ),
        padding="8px",
        border_radius="8px",
        width="100%",
        _hover={"background": "#E4E6E9"},
    )


def suggestion_item(user: UserCard) -> rx.Component:
    return rx.hstack(
        profile_link(user.id, user_avatar(user.avatar, user.initials, size="3")),
        rx.vstack(
            profile_link(user.id, rx.text(user.name, size="2", weight="medium")),
            rx.cond(user.subtitle != "", rx.text(user.subtitle, size="1", color=TEXT_MUTED)),
            spacing="0",
            flex="1",
        ),
        rx.icon_button(
            rx.icon("user-plus", size=16),
            on_click=[FriendsState.add_friend(user.id), HomeState.load_home],
            variant="soft",
            size="2",
        ),
        align="center",
        width="100%",
        padding="4px 8px",
    )


def right_sidebar() -> rx.Component:
    return rx.vstack(
        rx.cond(
            HomeState.suggestions.length() > 0,
            rx.vstack(
                rx.hstack(
                    rx.text("People you may know", weight="bold", color=TEXT_MUTED, size="3"),
                    rx.spacer(),
                    rx.link("See all", href="/friends", size="2"),
                    width="100%",
                    padding_x="8px",
                ),
                rx.foreach(HomeState.suggestions, suggestion_item),
                rx.separator(margin_y="8px"),
                width="100%",
                spacing="1",
            ),
        ),
        rx.text("Contacts", weight="bold", color=TEXT_MUTED, size="3", padding_x="8px"),
        rx.cond(
            HomeState.contacts.length() > 0,
            rx.foreach(HomeState.contacts, contact_item),
            rx.text("No friends yet. Send some requests!", size="2", color=TEXT_MUTED, padding_x="8px"),
        ),
        position="sticky",
        top="72px",
        width="280px",
        spacing="1",
        display=["none", "none", "flex"],
    )


def home_page() -> rx.Component:
    return app_layout(
        rx.hstack(
            left_sidebar(),
            rx.vstack(
                composer(),
                post_list(),
                width="100%",
                max_width="590px",
                spacing="4",
                padding_bottom="32px",
                margin_x="auto",
            ),
            right_sidebar(),
            justify="between",
            align="start",
            padding_x="16px",
            padding_top="16px",
            spacing="6",
            max_width="1280px",
            margin="0 auto",
            width="100%",
        ),
    )

