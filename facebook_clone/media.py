"""Uploaded photos: resizing, storage in the database, and serving them."""

import io
from pathlib import Path

import reflex as rx
from PIL import Image, ImageOps, UnidentifiedImageError
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route

from .models import Media, get_session

MAX_UPLOAD_BYTES = 15 * 1024 * 1024
MAX_SIDE = 1600
MEDIA_PREFIX = "/media/"


def compress_image(raw: bytes) -> tuple[bytes, str]:
    """Fix phone rotation, shrink to MAX_SIDE and re-encode.

    Raises:
        ValueError: If the bytes aren't an image.
    """
    try:
        img = Image.open(io.BytesIO(raw))
        img = ImageOps.exif_transpose(img)
    except (UnidentifiedImageError, OSError) as e:
        raise ValueError("not an image") from e
    img.thumbnail((MAX_SIDE, MAX_SIDE))
    out = io.BytesIO()
    if img.mode in ("RGBA", "LA", "P"):
        img.save(out, format="PNG", optimize=True)
        return out.getvalue(), "image/png"
    img.convert("RGB").save(out, format="JPEG", quality=85, optimize=True)
    return out.getvalue(), "image/jpeg"


def save_media(owner_id: int, raw: bytes) -> str:
    """Store a photo and return the value to keep in Post.image_url."""
    data, content_type = compress_image(raw)
    with get_session() as session:
        media = Media(owner_id=owner_id, content_type=content_type, data=data)
        session.add(media)
        session.commit()
        return f"{MEDIA_PREFIX}{media.id}"


def delete_media(stored: str) -> None:
    media_id = stored.removeprefix(MEDIA_PREFIX)
    if stored.startswith(MEDIA_PREFIX) and media_id.isdigit():
        with get_session() as session:
            if media := session.get(Media, int(media_id)):
                session.delete(media)
                session.commit()


def display_url(stored: str) -> str:
    """Turn a stored image reference into a URL the browser can load."""
    if not stored or stored.startswith("http"):
        return stored
    backend = rx.config.get_config().api_url.rstrip("/")
    if stored.startswith(MEDIA_PREFIX):
        return backend + stored
    if stored.startswith("/"):
        return stored  # a file in assets/, served with the frontend
    # Older posts saved photos to disk, which the host may have wiped.
    if (rx.get_upload_dir() / Path(stored).name).is_file():
        return f"{backend}/_upload/{stored}"
    return ""


def serve_media(request: Request) -> Response:
    with get_session() as session:
        media = session.get(Media, request.path_params["media_id"])
        if media is None:
            return Response(status_code=404)
        return Response(
            media.data,
            media_type=media.content_type,
            headers={"Cache-Control": "public, max-age=31536000, immutable"},
        )


media_api = Starlette(routes=[Route("/media/{media_id:int}", serve_media)])
