"""Login and sign-up page."""

import reflex as rx

from ..components.common import BRAND, FB_BLUE, PAGE_BG, TEXT_MUTED
from ..state import AuthState


def error_callout() -> rx.Component:
    return rx.cond(
        AuthState.auth_error != "",
        rx.callout(AuthState.auth_error, icon="triangle-alert", color_scheme="red", size="1", width="100%"),
    )


def signup_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.trigger(
            rx.button(
                "Create new account",
                color_scheme="green",
                size="3",
                weight="bold",
                padding_x="16px",
            ),
        ),
        rx.dialog.content(
            rx.dialog.title("Sign Up", size="7", margin_bottom="0"),
            rx.dialog.description("It's quick and easy.", color=TEXT_MUTED),
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
                        "By clicking Sign Up, you agree to be friends with everyone. Just kidding.",
                        size="1",
                        color=TEXT_MUTED,
                    ),
                    error_callout(),
                    rx.center(
                        rx.button(
                            "Sign Up",
                            type="submit",
                            color_scheme="green",
                            size="3",
                            width="200px",
                            weight="bold",
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
        rx.flex(
            rx.vstack(
                rx.heading(
                    BRAND,
                    size="9",
                    color=FB_BLUE,
                    weight="bold",
                    letter_spacing="-2px",
                    font_size=["44px", "56px", "60px"],
                ),
                rx.text(
                    f"Connect with friends and the world around you on {BRAND}.",
                    size="6",
                    font_size=["20px", "24px", "28px"],
                    line_height="1.3",
                ),
                max_width="500px",
                align=rx.breakpoints(initial="center", md="start"),
                text_align=["center", "center", "left"],
                spacing="2",
            ),
            rx.vstack(
                rx.box(
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
                            rx.button("Log In", type="submit", size="4", width="100%", weight="bold"),
                            spacing="3",
                        ),
                        on_submit=AuthState.login,
                    ),
                    rx.center(
                        rx.link("Forgotten password?", href="#", size="2"),
                        padding_y="12px",
                    ),
                    rx.separator(),
                    rx.center(signup_dialog(), padding_top="20px"),
                    background="white",
                    border_radius="8px",
                    box_shadow="0 2px 4px rgba(0,0,0,.1), 0 8px 16px rgba(0,0,0,.1)",
                    padding="16px",
                    width=["100%", "396px"],
                ),
                rx.text(
                    rx.text.strong("Demo login: "),
                    "mark@example.com / password",
                    size="2",
                    color=TEXT_MUTED,
                ),
                align="center",
                spacing="4",
            ),
            direction=rx.breakpoints(initial="column", md="row"),
            align="center",
            justify="center",
            gap=["32px", "32px", "80px"],
            padding="20px",
            max_width="1000px",
            width="100%",
        ),
        background=PAGE_BG,
        min_height="100vh",
    )
