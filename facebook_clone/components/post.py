"""Post composer and post card."""

import reflex as rx

from ..state import AuthState, CommentView, PostsState, PostView
from .common import CARD_STYLE, FB_BLUE, TEXT_MUTED, card, profile_link, user_avatar

UPLOAD_ID = "post_image_upload"


def composer_dialog() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
            rx.vstack(
                rx.hstack(
                    rx.spacer(),
                    rx.dialog.title("Create post", margin="0", size="5"),
                    rx.spacer(),
                    rx.dialog.close(
                        rx.icon_button(rx.icon("x"), radius="full", variant="soft", color_scheme="gray"),
                    ),
                    width="100%",
                    align="center",
                ),
                rx.separator(),
                rx.hstack(
                    user_avatar(AuthState.avatar, AuthState.user_initials),
                    rx.text(AuthState.full_name, weight="bold"),
                    align="center",
                ),
                rx.text_area(
                    value=PostsState.new_post_text,
                    on_change=PostsState.set_new_post_text,
                    placeholder=f"What's on your mind, {AuthState.first_name}?",
                    variant="soft",
                    color_scheme="gray",
                    size="3",
                    rows="5",
                    width="100%",
                    background="transparent",
                    auto_focus=True,
                ),
                rx.cond(
                    PostsState.new_post_image != "",
                    rx.box(
                        rx.cond(
                            PostsState.new_post_image.to(str).startswith("http") | PostsState.new_post_image.to(str).startswith("/"),
                            rx.image(src=PostsState.new_post_image, width="100%", border_radius="8px"),
                            rx.image(
                                src=rx.get_upload_url(PostsState.new_post_image),
                                width="100%",
                                border_radius="8px",
                            ),
                        ),
                        rx.icon_button(
                            rx.icon("x", size=16),
                            on_click=PostsState.set_new_post_image(""),
                            radius="full",
                            color_scheme="gray",
                            position="absolute",
                            top="8px",
                            right="8px",
                        ),
                        position="relative",
                        width="100%",
                    ),
                ),
                rx.hstack(
                    rx.text("Add to your post", weight="medium", size="2"),
                    rx.spacer(),
                    rx.upload.root(
                        rx.tooltip(
                            rx.icon_button(
                                rx.icon("image", color="#45BD62"),
                                variant="ghost",
                                radius="full",
                                type="button",
                            ),
                            content="Photo",
                        ),
                        id=UPLOAD_ID,
                        accept={"image/*": [".png", ".jpg", ".jpeg", ".gif", ".webp"]},
                        max_files=1,
                        no_drag=True,
                        on_drop=PostsState.handle_image_upload(rx.upload_files(upload_id=UPLOAD_ID)),
                    ),
                    rx.popover.root(
                        rx.popover.trigger(
                            rx.icon_button(
                                rx.icon("link", color=FB_BLUE),
                                variant="ghost",
                                radius="full",
                                type="button",
                            ),
                        ),
                        rx.popover.content(
                            rx.input(
                                placeholder="Paste an image URL",
                                value=PostsState.new_post_image,
                                on_change=PostsState.set_new_post_image,
                                width="280px",
                            ),
                        ),
                    ),
                    padding="8px 12px",
                    border="1px solid #CED0D4",
                    border_radius="8px",
                    width="100%",
                    align="center",
                ),
                rx.button(
                    "Post",
                    on_click=PostsState.create_post,
                    disabled=(PostsState.new_post_text.strip() == "") & (PostsState.new_post_image == ""),
                    width="100%",
                    size="3",
                ),
                spacing="3",
            ),
            max_width="500px",
        ),
        open=PostsState.composer_open,
        on_open_change=PostsState.set_composer_open,
    )


def composer() -> rx.Component:
    def action(icon: str, color: str, label: str) -> rx.Component:
        return rx.button(
            rx.icon(icon, color=color),
            rx.text(label, color=TEXT_MUTED, display=["none", "inline"]),
            variant="ghost",
            color_scheme="gray",
            size="3",
            flex="1",
            on_click=PostsState.set_composer_open(True),
        )

    return card(
        rx.vstack(
            rx.hstack(
                profile_link(AuthState.user_id, user_avatar(AuthState.avatar, AuthState.user_initials)),
                rx.box(
                    rx.text(f"What's on your mind, {AuthState.first_name}?", color=TEXT_MUTED),
                    on_click=PostsState.set_composer_open(True),
                    background="#F0F2F5",
                    border_radius="20px",
                    padding="8px 12px",
                    flex="1",
                    cursor="pointer",
                    _hover={"background": "#E4E6E9"},
                ),
                width="100%",
                align="center",
            ),
            rx.separator(),
            rx.hstack(
                action("video", "#F3425F", "Live video"),
                action("images", "#45BD62", "Photo/video"),
                action("smile", "#F7B928", "Feeling/activity"),
                width="100%",
            ),
            spacing="3",
        ),
        composer_dialog(),
    )


def comment_item(comment: CommentView) -> rx.Component:
    return rx.hstack(
        profile_link(
            comment.author_id,
            user_avatar(comment.author_avatar, comment.author_initials, size="2"),
        ),
        rx.vstack(
            rx.box(
                profile_link(comment.author_id, rx.text(comment.author_name, weight="bold", size="2")),
                rx.text(comment.content, size="2", white_space="pre-wrap"),
                background="#F0F2F5",
                border_radius="18px",
                padding="8px 12px",
            ),
            rx.hstack(
                rx.text(comment.time_ago, size="1", color=TEXT_MUTED),
                rx.cond(
                    comment.can_delete,
                    rx.link(
                        "Delete",
                        size="1",
                        weight="bold",
                        color=TEXT_MUTED,
                        on_click=PostsState.delete_comment(comment.id),
                        cursor="pointer",
                    ),
                ),
                padding_left="12px",
                spacing="3",
            ),
            spacing="1",
        ),
        align="start",
        spacing="2",
    )


def post_card(post: PostView) -> rx.Component:
    action_style = {
        "variant": "ghost",
        "color_scheme": "gray",
        "size": "3",
        "flex": "1",
    }
    return rx.box(
        rx.vstack(
            # Header
            rx.hstack(
                profile_link(post.author_id, user_avatar(post.author_avatar, post.author_initials)),
                rx.vstack(
                    profile_link(post.author_id, rx.text(post.author_name, weight="bold", size="2")),
                    rx.hstack(
                        rx.text(post.time_ago, size="1", color=TEXT_MUTED),
                        rx.text("·", size="1", color=TEXT_MUTED),
                        rx.icon("earth", size=12, color=TEXT_MUTED),
                        spacing="1",
                        align="center",
                    ),
                    spacing="0",
                ),
                rx.spacer(),
                rx.cond(
                    post.can_delete,
                    rx.menu.root(
                        rx.menu.trigger(
                            rx.icon_button(
                                rx.icon("ellipsis"), variant="ghost", color_scheme="gray", radius="full"
                            ),
                        ),
                        rx.menu.content(
                            rx.menu.item(
                                rx.hstack(rx.icon("trash-2", size=16), rx.text("Move to trash")),
                                on_click=PostsState.delete_post(post.id),
                                color="red",
                            ),
                        ),
                    ),
                ),
                width="100%",
                align="center",
                padding="12px 16px 0",
            ),
            # Body
            rx.cond(
                post.content != "",
                rx.text(post.content, size="3", white_space="pre-wrap", padding_x="16px"),
            ),
            rx.cond(
                post.image_url != "",
                rx.image(
                    src=rx.cond(post.image_is_upload, rx.get_upload_url(post.image_url), post.image_url),
                    width="100%",
                    max_height="600px",
                    object_fit="cover",
                    loading="lazy",
                ),
            ),
            # Counts
            rx.hstack(
                rx.cond(
                    post.like_count > 0,
                    rx.hstack(
                        rx.center(
                            rx.icon("thumbs-up", size=10, color="white", fill="white"),
                            width="18px",
                            height="18px",
                            border_radius="50%",
                            background=FB_BLUE,
                        ),
                        rx.text(post.like_count, size="2", color=TEXT_MUTED),
                        spacing="1",
                        align="center",
                    ),
                ),
                rx.spacer(),
                rx.cond(
                    post.comment_count > 0,
                    rx.text(
                        post.comment_count,
                        rx.cond(post.comment_count == 1, " comment", " comments"),
                        size="2",
                        color=TEXT_MUTED,
                    ),
                ),
                width="100%",
                padding_x="16px",
            ),
            # Actions
            rx.box(
                rx.hstack(
                    rx.button(
                        rx.icon(
                            "thumbs-up",
                            size=18,
                            fill=rx.cond(post.liked, FB_BLUE, "none"),
                        ),
                        "Like",
                        on_click=PostsState.toggle_like(post.id),
                        color=rx.cond(post.liked, FB_BLUE, TEXT_MUTED),
                        **action_style,
                    ),
                    rx.button(
                        rx.icon("message-circle", size=18),
                        "Comment",
                        on_click=rx.call_script(
                            "document.querySelector('[data-comment-for=\"" + post.id.to(str) + "\"]')?.focus()"
                        ),
                        color=TEXT_MUTED,
                        **action_style,
                    ),
                    rx.button(
                        rx.icon("share-2", size=18),
                        "Share",
                        on_click=rx.toast("Sharing is coming soon!"),
                        color=TEXT_MUTED,
                        **action_style,
                    ),
                    width="100%",
                    padding_y="4px",
                ),
                border_top="1px solid #CED0D4",
                border_bottom="1px solid #CED0D4",
                margin_x="16px",
                width="calc(100% - 32px)",
            ),
            # Comments
            rx.vstack(
                rx.foreach(post.comments, comment_item),
                rx.hstack(
                    user_avatar(AuthState.avatar, AuthState.user_initials, size="2"),
                    rx.form(
                        # The post id travels with the form: submit handlers are
                        # hoisted out of rx.foreach, so they can't close over `post`.
                        rx.el.input(type="hidden", name="post_id", value=post.id),
                        rx.input(
                            name="comment",
                            custom_attrs={"data-comment-for": post.id},
                            placeholder="Write a comment...",
                            radius="full",
                            variant="soft",
                            color_scheme="gray",
                            width="100%",
                            auto_complete=False,
                        ),
                        on_submit=PostsState.add_comment,
                        reset_on_submit=True,
                        flex="1",
                    ),
                    width="100%",
                    align="center",
                ),
                width="100%",
                padding="0 16px 12px",
                spacing="2",
            ),
            spacing="3",
        ),
        style=CARD_STYLE,
        overflow="hidden",
    )


def post_list() -> rx.Component:
    return rx.cond(
        PostsState.posts.length() > 0,
        rx.vstack(rx.foreach(PostsState.posts, post_card), spacing="4", width="100%"),
        card(
            rx.center(
                rx.vstack(
                    rx.icon("newspaper", size=40, color=TEXT_MUTED),
                    rx.text("No posts yet", weight="bold"),
                    rx.text(
                        "Add friends or share something to fill this space.",
                        color=TEXT_MUTED,
                        size="2",
                    ),
                    align="center",
                ),
                padding="24px",
            ),
        ),
    )
