import reflex as rx

config = rx.Config(
    app_name="facebook_clone",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.RadixThemesPlugin(
            theme=rx.theme(appearance="light", accent_color="blue", radius="medium"),
        ),
    ],
)
