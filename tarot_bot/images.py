"""Image d'un tirage : les cartes tirées côte à côte (à l'envers = retournées), assemblées avec Pillow.

Les scans viennent du tarot de Nicolas Conver (1760, BnF, domaine public), nommés par numéro de carte
(assets/cards/NN.jpg). Une carte sans scan est remplacée par une carte « non illustrée » générée.
Pillow est facultatif : sans lui (ou avec SEND_IMAGES=0), le tirage reste en texte seul.
"""
from __future__ import annotations

import io
import logging
import textwrap
import unicodedata
from pathlib import Path

from .cards import Card

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:  # Pillow facultatif
    Image = None

log = logging.getLogger("tarot")

ASSETS = Path(__file__).parent / "assets" / "cards"
FONT = Path(__file__).parent / "assets" / "fonts" / "DejaVuSerif.ttf"  # licence : assets/fonts/DejaVu-LICENSE.txt
RATIO = 1.82  # hauteur / largeur d'une carte
BG, PARCHMENT, INK, LABEL = (30, 26, 40), (233, 221, 192), (60, 45, 35), (230, 220, 200)


def available() -> bool:
    return Image is not None


def has_scan(card: Card) -> bool:
    return (ASSETS / f"{card.number:02d}.jpg").exists()


def _font(size: int):
    """(police, accents gérés). La police intégrée à Pillow n'a pas les accents : on embarque DejaVu Serif."""
    try:
        return ImageFont.truetype(str(FONT), size), True
    except OSError:
        pass
    try:
        return ImageFont.load_default(size=size), False
    except TypeError:  # Pillow < 10.1 : police bitmap
        return ImageFont.load_default(), False


def _fold(text: str) -> str:
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()


def _placeholder(card: Card, w: int, h: int):
    img = Image.new("RGB", (w, h), PARCHMENT)
    d = ImageDraw.Draw(img)
    d.rectangle((6, 6, w - 7, h - 7), outline=INK, width=3)
    d.rectangle((14, 14, w - 15, h - 15), outline=INK, width=1)
    font, accents = _font(max(18, w // 10))
    name = card.name if accents else _fold(card.name)
    lines = textwrap.wrap(name, 14)
    size = getattr(font, "size", 16)
    y = h // 2 - len(lines) * size // 2
    for line in lines:
        d.text((w // 2, y), line, fill=INK, font=font, anchor="mt")
        y += int(size * 1.3)
    return img


def _tile(drawn, w: int, h: int):
    path = ASSETS / f"{drawn.card.number:02d}.jpg"
    if path.exists():
        img = Image.open(path).convert("RGB").resize((w, h), Image.LANCZOS)
    else:
        img = _placeholder(drawn.card, w, h)
    return img.rotate(180) if drawn.reversed else img


def render_spread(reading) -> bytes | None:
    """JPEG du tirage, ou None si Pillow est absent ou en cas d'erreur (le texte part quand même)."""
    if Image is None:
        return None
    try:
        n = len(reading.cards)
        w = {1: 360, 3: 300}.get(n, 250)
        h = round(w * RATIO)
        pad, gap, label_h = 24, 18, 44
        font, accents = _font(max(16, w // 14))
        canvas = Image.new("RGB", (pad * 2 + n * w + (n - 1) * gap, pad * 2 + h + label_h), BG)
        d = ImageDraw.Draw(canvas)
        for i, drawn in enumerate(reading.cards):
            x = pad + i * (w + gap)
            canvas.paste(_tile(drawn, w, h), (x, pad))
            label = f"{i + 1}. {drawn.card.name}" + (" (envers)" if drawn.reversed else "")
            d.text((x + w // 2, pad + h + 10), label if accents else _fold(label), fill=LABEL, font=font, anchor="mt")
        out = io.BytesIO()
        canvas.save(out, "JPEG", quality=88)
        return out.getvalue()
    except Exception:
        log.exception("Image du tirage non générée")
        return None
