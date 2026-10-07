"""Page layout shared by all logged-in pages."""

import reflex as rx

from ..state import AuthState
from .common import PAGE_BG
from .navbar import navbar


def app_layout(*children, **props) -> rx.Component:
    return rx.box(
        rx.cond(
            AuthState.is_logged_in,
            rx.fragment(
                navbar(),
                rx.box(*children, padding_top="56px", **props),
            ),
            rx.center(rx.spinner(size="3"), height="100vh"),
        ),
        background=PAGE_BG,
        min_height="100vh",
    )
