"""Login and sign-up page."""

import reflex as rx

from ..components.common import BRAND, BRAND_COLOR, PAGE_BG, TEXT_MUTED
from ..state import AuthState


def error_callout() -> rx.Component:
    return rx.cond(
        AuthState.auth_error != "",
        rx.callout(AuthState.auth_error, icon="triangle-alert", color_scheme="red", size="1", width="100%"),
    )


def signup_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button("Create an account", variant="ghost", size="2"),
        ),
        rx.dialog.content(
            rx.dialog.title("Create an account", size="6", margin_bottom="0"),
            rx.separator(margin_y="12px"),
            rx.form(
                rx.vstack(
                    rx.hstack(
                        rx.input(name="first_name", placeholder="First name", size="3", flex="1"),
                        rx.input(name="last_name", placeholder="Last name", size="3", flex="1"),
                        width="100%",
                    ),
                    rx.input(name="email", placeholder="Email address", type="email", size="3", width="100%"),
                    rx.input(
                        name="password",
                        placeholder="New password",
                        type="password",
                        size="3",
                        width="100%",
                    ),
                    rx.text(
                        f"Join {BRAND} to share posts and photos with your friends.",
                        size="1",
                        color=TEXT_MUTED,
                    ),
                    error_callout(),
                    rx.center(
                        rx.button(
                            "Sign Up",
                            type="submit",
                            size="3",
                            width="100%",
                        ),
                        width="100%",
                    ),
                    spacing="3",
                ),
                on_submit=AuthState.signup,
            ),
            max_width="430px",
        ),
    )


def login_page() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.vstack(
                rx.image(src="/logo.svg", alt=BRAND, width="64px", height="64px"),
                rx.heading(BRAND, size="8", color=BRAND_COLOR, weight="bold"),
                rx.text(
                    "Share moments with the people you care about.",
                    size="4",
                    color=TEXT_MUTED,
                    text_align="center",
                ),
                align="center",
                spacing="2",
            ),
            rx.box(
                rx.vstack(
                    rx.heading("Log in", size="5"),
                    rx.form(
                        rx.vstack(
                            rx.input(
                                name="email",
                                placeholder="Email address",
                                type="email",
                                size="3",
                                width="100%",
                                auto_focus=True,
                            ),
                            rx.input(
                                name="password",
                                placeholder="Password",
                                type="password",
                                size="3",
                                width="100%",
                            ),
                            error_callout(),
                            rx.button("Log in", type="submit", size="3", width="100%"),
                            spacing="3",
                        ),
                        on_submit=AuthState.login,
                        width="100%",
                    ),
                    rx.hstack(
                        rx.text("New here?", size="2", color=TEXT_MUTED),
                        signup_dialog(),
                        align="center",
                        justify="center",
                        width="100%",
                    ),
                    spacing="4",
                ),
                background="white",
                border_radius="16px",
                border="1px solid #E4E2EE",
                padding="24px",
                width="100%",
            ),
            rx.text(
                rx.text.strong("Demo account: "),
                "amina@example.com / password",
                size="2",
                color=TEXT_MUTED,
            ),
            align="center",
            spacing="5",
            width="100%",
            max_width="380px",
            padding="24px 16px",
        ),
        background=PAGE_BG,
        min_height="100vh",
    )
