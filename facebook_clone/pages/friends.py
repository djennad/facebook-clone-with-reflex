"""Friends page: requests, suggestions and the friend list."""

import reflex as rx

from ..components.common import CARD_STYLE, TEXT_MUTED, profile_link, section_title
from ..components.layout import app_layout
from ..state import FriendsState, UserCard


def person_card(user: UserCard, *buttons: rx.Component) -> rx.Component:
    return rx.vstack(
        profile_link(
            user.id,
            rx.box(
                rx.cond(
                    user.avatar != "",
                    rx.image(src=user.avatar, width="100%", height="100%", object_fit="cover"),
                    rx.center(rx.text(user.initials, size="8", weight="bold", color="white"), height="100%"),
                ),
                aspect_ratio="1",
                width="100%",
                background="#1877F2",
            ),
            width="100%",
        ),
        rx.vstack(
            profile_link(user.id, rx.text(user.name, weight="bold", size="3", trim="both")),
            rx.text(rx.cond(user.subtitle != "", user.subtitle, " "), size="1", color=TEXT_MUTED),
            *buttons,
            padding="0 12px 12px",
            width="100%",
            spacing="2",
        ),
        style=CARD_STYLE,
        overflow="hidden",
        spacing="2",
    )


def section(title: str, items, render, empty: str) -> rx.Component:
    return rx.vstack(
        section_title(title),
        rx.cond(
            items.length() > 0,
            rx.grid(
                rx.foreach(items, render),
                columns=rx.breakpoints(initial="2", sm="3", md="4", lg="5"),
                spacing="3",
                width="100%",
            ),
            rx.text(empty, color=TEXT_MUTED, size="2"),
        ),
        width="100%",
        spacing="3",
    )


def full_button(label: str, on_click, **props) -> rx.Component:
    return rx.button(label, on_click=on_click, width="100%", **props)


def friends_page() -> rx.Component:
    return app_layout(
        rx.vstack(
            section(
                "Friend requests",
                FriendsState.requests,
                lambda u: person_card(
                    u,
                    full_button("Confirm", FriendsState.accept(u.id)),
                    full_button("Delete", FriendsState.remove(u.id), variant="soft", color_scheme="gray"),
                ),
                "When you have friend requests, you'll see them here.",
            ),
            rx.separator(),
            section(
                "People you may know",
                FriendsState.suggestions,
                lambda u: person_card(
                    u,
                    full_button("Add friend", FriendsState.add_friend(u.id), variant="soft"),
                ),
                "No suggestions right now.",
            ),
            rx.cond(
                FriendsState.sent.length() > 0,
                rx.fragment(
                    rx.separator(),
                    section(
                        "Sent requests",
                        FriendsState.sent,
                        lambda u: person_card(
                            u,
                            full_button("Cancel", FriendsState.remove(u.id), variant="soft", color_scheme="gray"),
                        ),
                        "",
                    ),
                ),
            ),
            rx.separator(),
            section(
                "All friends",
                FriendsState.friends,
                lambda u: person_card(
                    u,
                    full_button("Unfriend", FriendsState.remove(u.id), variant="soft", color_scheme="gray"),
                ),
                "You haven't added any friends yet.",
            ),
            max_width="1100px",
            margin="0 auto",
            padding="24px 16px",
            spacing="5",
        ),
    )
