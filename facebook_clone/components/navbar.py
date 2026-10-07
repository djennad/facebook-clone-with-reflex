"""Top navigation bar."""

import reflex as rx

from ..state import AuthState, SearchState
from .common import FB_BLUE, TEXT_MUTED, user_avatar


def logo() -> rx.Component:
    return rx.link(
        rx.center(
            rx.text("f", size="8", weight="bold", color="white", line_height="1", margin_top="8px"),
            width="40px",
            height="40px",
            border_radius="50%",
            background=FB_BLUE,
            overflow="hidden",
        ),
        href="/",
        underline="none",
    )


def search_box() -> rx.Component:
    return rx.form(
        rx.input(
            rx.input.slot(rx.icon("search", size=16, color=TEXT_MUTED)),
            name="q",
            placeholder="Search Facebook",
            radius="full",
            size="3",
            variant="soft",
            color_scheme="gray",
            width=["40px", "40px", "240px"],
        ),
        on_submit=SearchState.submit_search,
        reset_on_submit=True,
    )


def nav_tab(icon: str, href: str, route_prefix: str) -> rx.Component:
    path = AuthState.router.url.path
    is_active = (
        (path == "/") | (path == "")
        if route_prefix == "/"
        else path.to(str).contains(route_prefix)
    )
    return rx.link(
        rx.center(
            rx.icon(icon, size=26, color=rx.cond(is_active, FB_BLUE, TEXT_MUTED)),
            height="56px",
            width=["64px", "80px", "112px"],
            border_bottom=rx.cond(is_active, f"3px solid {FB_BLUE}", "3px solid transparent"),
            _hover={"background": rx.cond(is_active, "transparent", "#F2F2F2")},
            border_radius=rx.cond(is_active, "0", "8px"),
        ),
        href=href,
        underline="none",
    )


def account_menu() -> rx.Component:
    return rx.menu.root(
        rx.menu.trigger(
            rx.box(
                user_avatar(AuthState.avatar, AuthState.user_initials, size="3"),
                cursor="pointer",
                aria_label="Account",
            ),
        ),
        rx.menu.content(
            rx.menu.item(
                rx.hstack(
                    user_avatar(AuthState.avatar, AuthState.user_initials, size="2"),
                    rx.text(AuthState.full_name, weight="bold"),
                    align="center",
                ),
                on_click=rx.redirect(f"/profile/{AuthState.user_id}"),
                height="auto",
                padding="8px",
            ),
            rx.menu.separator(),
            rx.menu.item(
                rx.hstack(rx.icon("users", size=16), rx.text("Friends")),
                on_click=rx.redirect("/friends"),
            ),
            rx.menu.item(
                rx.hstack(rx.icon("log-out", size=16), rx.text("Log Out")),
                on_click=AuthState.logout,
            ),
            min_width="240px",
        ),
    )


def navbar() -> rx.Component:
    return rx.hstack(
        rx.hstack(logo(), search_box(), align="center", spacing="2", flex="1"),
        rx.hstack(
            nav_tab("house", "/", "/"),
            nav_tab("users", "/friends", "/friends"),
            nav_tab("circle-user-round", f"/profile/{AuthState.user_id}", "/profile"),
            spacing="1",
            justify="center",
        ),
        rx.hstack(
            rx.icon_button(
                rx.icon("message-circle", size=20),
                radius="full",
                variant="soft",
                color_scheme="gray",
                size="3",
                display=["none", "none", "flex"],
            ),
            rx.icon_button(
                rx.icon("bell", size=20),
                radius="full",
                variant="soft",
                color_scheme="gray",
                size="3",
                on_click=rx.redirect("/friends"),
                display=["none", "none", "flex"],
            ),
            account_menu(),
            align="center",
            justify="end",
            spacing="2",
            flex="1",
        ),
        position="fixed",
        top="0",
        left="0",
        right="0",
        height="56px",
        padding_x="16px",
        background="white",
        box_shadow="0 1px 2px rgba(0, 0, 0, 0.15)",
        align="center",
        z_index="100",
    )
