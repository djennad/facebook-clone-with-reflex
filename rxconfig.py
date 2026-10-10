import os

import reflex as rx

# The public URL the browser uses to reach the backend. Render sets
# RENDER_EXTERNAL_URL automatically; elsewhere set API_URL yourself.
api_url = os.environ.get("API_URL") or os.environ.get("RENDER_EXTERNAL_URL")

config = rx.Config(
    app_name="facebook_clone",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.RadixThemesPlugin(
            theme=rx.theme(appearance="light", accent_color="blue", radius="medium"),
        ),
    ],
    **({"api_url": api_url} if api_url else {}),
)
