"""User profile page."""

import reflex as rx

from ..components.common import BRAND_COLOR, CARD_STYLE, TEXT_MUTED, card, profile_link, section_title, user_avatar
from ..components.layout import app_layout
from ..components.post import composer, post_list
from ..state import ProfileState, UserCard


def edit_profile_dialog() -> rx.Component:
    def field(label: str, control: rx.Component) -> rx.Component:
        return rx.vstack(rx.text(label, size="2", weight="medium"), control, spacing="1", width="100%")

    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Edit profile"),
            rx.form(
                rx.vstack(
                    rx.hstack(
                        field("First name", rx.input(name="first_name", default_value=ProfileState.first_name, width="100%")),
                        field("Last name", rx.input(name="last_name", default_value=ProfileState.last_name, width="100%")),
                        width="100%",
                    ),
                    field(
                        "Bio",
                        rx.text_area(
                            name="bio",
                            default_value=ProfileState.profile_bio,
                            placeholder="Describe who you are",
                            max_length=300,
                            width="100%",
                        ),
                    ),
                    field("City", rx.input(name="city", default_value=ProfileState.profile_city, width="100%")),
                    field(
                        "Profile picture URL",
                        rx.input(name="avatar_url", default_value=ProfileState.avatar, width="100%"),
                    ),
                    field(
                        "Cover photo URL",
                        rx.input(name="cover_url", default_value=ProfileState.profile_cover, width="100%"),
                    ),
                    rx.hstack(
                        rx.dialog.close(rx.button("Cancel", variant="soft", color_scheme="gray", type="button")),
                        rx.button("Save", type="submit"),
                        justify="end",
                        width="100%",
                    ),
                    spacing="3",
                ),
                on_submit=ProfileState.save_profile,
            ),
            max_width="480px",
        ),
        open=ProfileState.edit_open,
        on_open_change=ProfileState.set_edit_open,
    )


def friend_button() -> rx.Component:
    return rx.match(
        ProfileState.profile_friend_status,
        (
            "self",
            rx.button(
                rx.icon("pencil", size=16),
                "Edit profile",
                on_click=ProfileState.set_edit_open(True),
                variant="soft",
                color_scheme="gray",
                size="3",
            ),
        ),
        (
            "friends",
            rx.menu.root(
                rx.menu.trigger(
                    rx.button(rx.icon("user-check", size=16), "Friends", variant="soft", color_scheme="gray", size="3"),
                ),
                rx.menu.content(
                    rx.menu.item(
                        rx.hstack(rx.icon("user-x", size=16), rx.text("Unfriend")),
                        on_click=ProfileState.remove_friend,
                        color="red",
                    ),
                ),
            ),
        ),
        (
            "sent",
            rx.button(
                rx.icon("user-x", size=16),
                "Cancel request",
                on_click=ProfileState.remove_friend,
                variant="soft",
                size="3",
            ),
        ),
        (
            "received",
            rx.hstack(
                rx.button(rx.icon("user-check", size=16), "Confirm", on_click=ProfileState.accept_friend, size="3"),
                rx.button(
                    "Delete request",
                    on_click=ProfileState.remove_friend,
                    variant="soft",
                    color_scheme="gray",
                    size="3",
                ),
            ),
        ),
        rx.button(rx.icon("user-plus", size=16), "Add friend", on_click=ProfileState.add_friend, size="3"),
    )


def profile_header() -> rx.Component:
    return rx.box(
        rx.box(
            rx.box(
                rx.cond(
                    ProfileState.profile_cover != "",
                    rx.image(src=ProfileState.profile_cover, width="100%", height="100%", object_fit="cover"),
                ),
                height=["200px", "280px", "400px"],
                background="linear-gradient(180deg, #a8c0ff 0%, #3f2b96 100%)",
                border_radius="0 0 8px 8px",
                overflow="hidden",
            ),
            rx.flex(
                rx.box(
                    rx.avatar(
                        src=ProfileState.profile.avatar,
                        fallback=ProfileState.profile.initials,
                        radius="full",
                        size="9",
                        variant="solid",
                        color_scheme="violet",
                        style={"border": "4px solid white", "width": "168px", "height": "168px"},
                    ),
                    margin_top="-84px",
                ),
                rx.vstack(
                    rx.heading(ProfileState.profile.name, size="8"),
                    rx.text(
                        ProfileState.profile_friend_count,
                        rx.cond(ProfileState.profile_friend_count == 1, " friend", " friends"),
                        color=TEXT_MUTED,
                        weight="medium",
                    ),
                    rx.hstack(
                        rx.foreach(
                            ProfileState.profile_friends[:8],
                            lambda f: profile_link(
                                f.id,
                                rx.box(
                                    user_avatar(f.avatar, f.initials, size="2"),
                                    border="2px solid white",
                                    border_radius="50%",
                                    margin_left="-8px",
                                ),
                            ),
                        ),
                        padding_left="8px",
                        spacing="0",
                    ),
                    spacing="1",
                    align=rx.breakpoints(initial="center", md="start"),
                    flex="1",
                    padding_top=rx.breakpoints(initial="0", md="24px"),
                ),
                rx.box(friend_button(), padding_top=rx.breakpoints(initial="0", md="64px")),
                direction=rx.breakpoints(initial="column", md="row"),
                align=rx.breakpoints(initial="center", md="start"),
                gap="16px",
                padding="0 32px 16px",
            ),
            max_width="1100px",
            margin="0 auto",
        ),
        background="white",
        box_shadow="0 1px 2px rgba(0, 0, 0, 0.1)",
        width="100%",
    )


def intro_card() -> rx.Component:
    def row(icon: str, *text) -> rx.Component:
        return rx.hstack(rx.icon(icon, size=20, color="#8C939D"), rx.text(*text, size="3"), align="center")

    return card(
        rx.vstack(
            section_title("Intro"),
            rx.cond(
                ProfileState.profile_bio != "",
                rx.text(ProfileState.profile_bio, text_align="center", width="100%"),
            ),
            rx.cond(
                ProfileState.is_own_profile,
                rx.button(
                    "Edit details",
                    on_click=ProfileState.set_edit_open(True),
                    variant="soft",
                    color_scheme="gray",
                    width="100%",
                ),
            ),
            rx.cond(
                ProfileState.profile_city != "",
                row("house", "Lives in ", rx.text.strong(ProfileState.profile_city)),
            ),
            row("clock", "Joined ", ProfileState.profile_joined),
            spacing="3",
        ),
    )


def friend_tile(user: UserCard) -> rx.Component:
    return profile_link(
        user.id,
        rx.vstack(
            rx.box(
                rx.cond(
                    user.avatar != "",
                    rx.image(src=user.avatar, width="100%", height="100%", object_fit="cover"),
                    rx.center(rx.text(user.initials, size="6", weight="bold", color="white"), height="100%"),
                ),
                aspect_ratio="1",
                width="100%",
                border_radius="8px",
                overflow="hidden",
                background=BRAND_COLOR,
            ),
            rx.text(user.name, size="1", weight="medium", trim="both"),
            spacing="1",
        ),
    )


def friends_card() -> rx.Component:
    return card(
        rx.vstack(
            rx.hstack(
                section_title("Friends"),
                rx.spacer(),
                rx.cond(ProfileState.is_own_profile, rx.link("See all friends", href="/friends", size="2")),
                width="100%",
            ),
            rx.text(ProfileState.profile_friend_count, " friends", color=TEXT_MUTED, size="2"),
            rx.grid(rx.foreach(ProfileState.profile_friends, friend_tile), columns="3", spacing="3", width="100%"),
            spacing="2",
        ),
    )


def profile_page() -> rx.Component:
    return app_layout(
        rx.cond(
            ProfileState.profile_not_found,
            rx.center(
                rx.vstack(
                    rx.heading("This content isn't available right now"),
                    rx.link("Go to News Feed", href="/"),
                    align="center",
                ),
                padding="80px 16px",
            ),
            rx.fragment(
                profile_header(),
                rx.flex(
                    rx.vstack(
                        intro_card(),
                        friends_card(),
                        width=rx.breakpoints(initial="100%", md="40%"),
                        spacing="4",
                        position=rx.breakpoints(initial="static", md="sticky"),
                        top="72px",
                    ),
                    rx.vstack(
                        rx.cond(ProfileState.is_own_profile, composer()),
                        rx.box(section_title("Posts"), style=CARD_STYLE, padding="12px 16px"),
                        post_list(),
                        flex="1",
                        width="100%",
                        spacing="4",
                    ),
                    direction=rx.breakpoints(initial="column", md="row"),
                    align="start",
                    gap="16px",
                    max_width="1100px",
                    margin="0 auto",
                    padding="16px",
                ),
                edit_profile_dialog(),
            ),
        ),
    )
