"""People search results."""

import reflex as rx

from ..components.common import TEXT_MUTED, card, profile_link, user_avatar
from ..components.layout import app_layout
from ..state import SearchResult, SearchState


def result_row(result: SearchResult) -> rx.Component:
    user = result.user
    return card(
        rx.hstack(
            profile_link(user.id, user_avatar(user.avatar, user.initials, size="5")),
            rx.vstack(
                profile_link(user.id, rx.text(user.name, weight="bold", size="3")),
                rx.cond(user.subtitle != "", rx.text(user.subtitle, size="2", color=TEXT_MUTED)),
                spacing="1",
                flex="1",
            ),
            rx.match(
                result.status,
                ("self", rx.fragment()),
                ("friends", rx.badge("Friends", size="2", color_scheme="gray")),
                ("sent", rx.badge("Request sent", size="2")),
                ("received", rx.button("Confirm", on_click=SearchState.accept(user.id))),
                rx.button(rx.icon("user-plus", size=16), "Add friend", variant="soft", on_click=SearchState.add_friend(user.id)),
            ),
            align="center",
            width="100%",
        ),
    )


def search_page() -> rx.Component:
    return app_layout(
        rx.vstack(
            rx.heading("People", size="5"),
            rx.form(
                rx.input(
                    rx.input.slot(rx.icon("search", size=16)),
                    name="q",
                    default_value=SearchState.query,
                    key=SearchState.query,
                    placeholder="Search for people by name or email",
                    size="3",
                    width="100%",
                ),
                on_submit=SearchState.submit_search,
                width="100%",
            ),
            rx.cond(
                SearchState.results.length() > 0,
                rx.foreach(SearchState.results, result_row),
                rx.cond(
                    SearchState.query != "",
                    rx.text("We didn't find any results for “", SearchState.query, "”.", color=TEXT_MUTED),
                    rx.text("Type a name to find people.", color=TEXT_MUTED),
                ),
            ),
            max_width="680px",
            margin="0 auto",
            padding="24px 16px",
            spacing="3",
        ),
    )
