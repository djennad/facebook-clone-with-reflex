"""Shared UI building blocks."""

import reflex as rx

BRAND = "sudfa+"
BRAND_COLOR = "#6E56CF"
BRAND_SOFT = "#F1EDFE"
PAGE_BG = "#F5F4F9"
TEXT_MUTED = "#65676B"
HOVER_BG = "#F2F2F2"

CARD_STYLE = {
    "background": "white",
    "border_radius": "8px",
    "box_shadow": "0 1px 2px rgba(0, 0, 0, 0.2)",
    "width": "100%",
}


def card(*children, **props) -> rx.Component:
    return rx.box(*children, style=CARD_STYLE, padding="12px 16px", **props)


def user_avatar(src, fallback, size: str = "3") -> rx.Component:
    return rx.avatar(
        src=src,
        fallback=fallback,
        radius="full",
        size=size,
        color_scheme="violet",
        variant="solid",
    )


def profile_link(user_id, *children, **props) -> rx.Component:
    return rx.link(
        *children,
        href=f"/profile/{user_id}",
        underline="none",
        color="inherit",
        **props,
    )


def sidebar_item(icon: str, label, href: str = "#", **props) -> rx.Component:
    return rx.link(
        rx.hstack(
            rx.center(
                rx.icon(icon, size=20, color=BRAND_COLOR),
                width="36px",
                height="36px",
                border_radius="50%",
                background=BRAND_SOFT,
            ),
            rx.text(label, weight="medium", size="2"),
            align="center",
            spacing="3",
        ),
        href=href,
        underline="none",
        color="inherit",
        padding="8px",
        border_radius="8px",
        width="100%",
        _hover={"background": "#E4E6E9"},
        **props,
    )


def section_title(text: str) -> rx.Component:
    return rx.text(text, size="4", weight="bold", color="#050505")
