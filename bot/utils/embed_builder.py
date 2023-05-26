"""
utils.embed_builder
----------------

This module creates Discord embeds.

:Date: 10-07-2022
"""

from datetime import datetime
from typing import Optional

from disnake import Colour
from disnake import Embed

MAX_EMBED_DESCRIPTION_LENGTH = 4096
MAX_EMBED_FIELD_TITLE_LENGTH = 256
MAX_EMBED_FIELD_FOOTER_LENGTH = 2048


def __trim(text: str, limit: int) -> str:
    """ Limit text to a certain number of characters. """
    return text[: limit - 3].strip() + "..." if len(text) > limit else text


def embed_information(
        title: str,
        description: str = None,
        footer: Optional[str] = None,
        url: Optional[str] = None,
        image: Optional[str] = None,
        thumbnail: Optional[str] = None
    ) -> Embed:
    """ Embed an information message with greyple colour. """
    return build_embed(title, description, footer, url, Colour.greyple(), image, thumbnail)


def embed_error(
        title: str,
        description: str = None,
        footer: Optional[str] = None,
        url: Optional[str] = None,
        image: Optional[str] = None,
        thumbnail: Optional[str] = None
    ) -> Embed:
    """ Embed an error message with red colour. """
    return build_embed(title, description, footer, url, Colour.red(), image, thumbnail)


def build_embed(
        title: str,
        description: Optional[str] = None,
        footer: Optional[str] = None,
        url: Optional[str] = None,
        colour: Colour = Colour.default(),
        image: Optional[str] = None,
        thumbnail: Optional[str] = None,
    ) -> Embed:
    """ Embed a message with an optional description, footer, and url. """
    embed = Embed(
        title = title,
        colour = colour
    )
    if description:
        embed.description = __trim(description, MAX_EMBED_DESCRIPTION_LENGTH)
    if footer:
        embed.set_footer(text = __trim(footer, MAX_EMBED_FIELD_FOOTER_LENGTH))
    if url:
        embed.url = url
    if image:
        embed.set_image(url = image)
    if thumbnail:
        embed.set_thumbnail(url = thumbnail)
    embed.timestamp = datetime.utcnow()
    return embed
