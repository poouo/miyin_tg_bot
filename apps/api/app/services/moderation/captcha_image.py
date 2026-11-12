"""Animated GIF captcha used by the join verification flow.

The image shows CAPTCHA_LENGTH random letters. Every frame re-draws the letters
with a different rotation / offset / wave distortion and a different set of
interference lines, noise and "scan bars", so no single frame is clean enough to
OCR reliably, while a human watching the animation can still read the letters.
"""

from __future__ import annotations

import io
import math
from functools import lru_cache
from random import SystemRandom

from PIL import Image, ImageDraw, ImageFont

# Letters that are easy to confuse with each other (I/L, O/Q) are left out.
CAPTCHA_ALPHABET = "ABCDEFGHJKMNPRSTUVWXYZ"
CAPTCHA_LENGTH = 4
OPTION_COUNT = 4

IMAGE_WIDTH = 320
IMAGE_HEIGHT = 120
FRAME_COUNT = 14
FRAME_DURATION_MS = 130

_rng = SystemRandom()

_FONT_CANDIDATES = (
    "DejaVuSans-Bold.ttf",
    "DejaVuSerif-Bold.ttf",
    "LiberationSans-Bold.ttf",
    "FreeSansBold.ttf",
    "arialbd.ttf",
    "Arial Bold.ttf",
    "verdanab.ttf",
    "georgiab.ttf",
)
_FONT_SIZE = 64


@lru_cache(maxsize=1)
def _load_fonts() -> tuple[ImageFont.FreeTypeFont, ...]:
    fonts: list[ImageFont.FreeTypeFont] = []
    for name in _FONT_CANDIDATES:
        try:
            fonts.append(ImageFont.truetype(name, _FONT_SIZE))
        except OSError:
            continue
    if fonts:
        return tuple(fonts[:3])
    # Pillow >= 10.1 ships a built-in scalable font, so slim containers without
    # any system fonts still work.
    return (ImageFont.load_default(size=_FONT_SIZE),)


def generate_captcha_text(length: int = CAPTCHA_LENGTH) -> str:
    """Random distinct letters, e.g. 'KRDM'."""
    return "".join(_rng.sample(CAPTCHA_ALPHABET, length))


def build_letter_options(answer: str, count: int = OPTION_COUNT) -> list[str]:
    """Return `count` shuffled options containing `answer`.

    Each distractor keeps some letters of the answer and replaces two positions,
    so a solver that only reads part of the picture cannot tell the answer apart
    from the distractors.
    """
    answer = answer.upper()
    options = [answer]
    attempts = 0
    while len(options) < max(2, count) and attempts < 200:
        attempts += 1
        positions = _rng.sample(range(len(answer)), min(2, len(answer)))
        chars = list(answer)
        for pos in positions:
            # real answers never repeat a letter, so distractors must not either
            pool = [c for c in CAPTCHA_ALPHABET if c not in chars]
            chars[pos] = _rng.choice(pool)
        candidate = "".join(chars)
        if candidate not in options:
            options.append(candidate)
    _rng.shuffle(options)
    return options


def _random_dark_color() -> tuple[int, int, int]:
    return (_rng.randint(10, 130), _rng.randint(10, 130), _rng.randint(10, 130))


def _background() -> Image.Image:
    base = (_rng.randint(215, 250), _rng.randint(215, 250), _rng.randint(215, 250))
    image = Image.new("RGB", (IMAGE_WIDTH, IMAGE_HEIGHT), base)
    draw = ImageDraw.Draw(image)
    # soft colour blobs
    for _ in range(6):
        x = _rng.randint(-20, IMAGE_WIDTH)
        y = _rng.randint(-20, IMAGE_HEIGHT)
        r = _rng.randint(25, 60)
        tint = tuple(min(255, c + _rng.randint(-25, 5)) for c in base)
        draw.ellipse((x, y, x + r, y + r), fill=tint)
    # static speckles (identical on every frame, keeps the GIF small)
    for _ in range(260):
        x = _rng.randint(0, IMAGE_WIDTH - 1)
        y = _rng.randint(0, IMAGE_HEIGHT - 1)
        shade = _rng.randint(150, 215)
        draw.point((x, y), fill=(shade, shade, shade))
    return image


class _Glyph:
    """One letter with the parameters that stay constant across frames."""

    def __init__(self, char: str, index: int) -> None:
        self.char = char
        self.font = _rng.choice(_load_fonts())
        self.color = _random_dark_color()
        self.angle = _rng.uniform(-24, 24)
        # the glyph is centred inside an (_FONT_SIZE + 24) px mask, so these
        # offsets put the four letters roughly in the middle of the picture
        self.x = 10 + index * 66 + _rng.randint(-3, 4)
        self.y = _rng.randint(12, 26)
        self.mask = self._render_mask()

    def _render_mask(self) -> Image.Image:
        size = _FONT_SIZE + 24
        mask = Image.new("L", (size, size), 0)
        ImageDraw.Draw(mask).text(
            (size // 2, size // 2),
            self.char,
            font=self.font,
            fill=255,
            anchor="mm",
            stroke_width=1,
            stroke_fill=255,
        )
        return mask

    def frame_layer(self, frame: int) -> tuple[Image.Image, tuple[int, int]]:
        angle = self.angle + _rng.uniform(-7, 7)
        rotated = self.mask.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
        layer = Image.new("RGBA", rotated.size, self.color + (0,))
        layer.putalpha(rotated)
        dx = _rng.randint(-3, 3)
        dy = _rng.randint(-3, 3)
        return layer, (int(self.x) + dx, int(self.y) + dy)


def _wave(layer: Image.Image, amplitude: float, period: float, phase: float) -> Image.Image:
    width, height = layer.size
    out = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    step = 2
    for x in range(0, width, step):
        dy = int(round(amplitude * math.sin(2 * math.pi * x / period + phase)))
        out.paste(layer.crop((x, 0, min(x + step, width), height)), (x, dy))
    return out


def _draw_interference(
    image: Image.Image,
    palette: list[tuple[int, int, int]],
    frame: int,
    base_background: Image.Image,
) -> None:
    draw = ImageDraw.Draw(image)

    # wavy lines in the same colours as the letters, moving every frame
    for _ in range(4):
        color = _rng.choice(palette)
        y0 = _rng.randint(10, IMAGE_HEIGHT - 10)
        amp = _rng.randint(6, 18)
        period = _rng.randint(40, 90)
        phase = _rng.uniform(0, 2 * math.pi)
        points = [
            (x, y0 + amp * math.sin(2 * math.pi * x / period + phase))
            for x in range(0, IMAGE_WIDTH + 6, 6)
        ]
        draw.line(points, fill=color, width=_rng.randint(2, 3))

    # random straight strokes crossing the letters
    for _ in range(3):
        color = _rng.choice(palette)
        draw.line(
            (
                _rng.randint(0, IMAGE_WIDTH),
                _rng.randint(0, IMAGE_HEIGHT),
                _rng.randint(0, IMAGE_WIDTH),
                _rng.randint(0, IMAGE_HEIGHT),
            ),
            fill=color,
            width=2,
        )

    # background-coloured bars sweeping across the picture hide a different part
    # of every letter in every frame
    for _ in range(2):
        bar_x = (frame * (IMAGE_WIDTH // FRAME_COUNT) * 2 + _rng.randint(0, IMAGE_WIDTH)) % IMAGE_WIDTH
        bar_w = _rng.randint(4, 8)
        region = (bar_x, 0, min(IMAGE_WIDTH, bar_x + bar_w), IMAGE_HEIGHT)
        image.paste(base_background.crop(region), region[:2])

    # per-frame speckles
    for _ in range(90):
        x = _rng.randint(0, IMAGE_WIDTH - 1)
        y = _rng.randint(0, IMAGE_HEIGHT - 1)
        draw.ellipse((x, y, x + 1, y + 1), fill=_rng.choice(palette))


def render_captcha_gif(text: str) -> bytes:
    """Render `text` as an animated GIF and return the encoded bytes."""
    text = text.upper()
    background = _background()
    glyphs = [_Glyph(char, index) for index, char in enumerate(text)]
    palette = [g.color for g in glyphs]

    frames: list[Image.Image] = []
    for frame_index in range(FRAME_COUNT):
        frame = background.copy()
        text_layer = Image.new("RGBA", (IMAGE_WIDTH, IMAGE_HEIGHT), (0, 0, 0, 0))
        for glyph in glyphs:
            layer, position = glyph.frame_layer(frame_index)
            _paste_clipped(text_layer, layer, position)
        text_layer = _wave(
            text_layer,
            amplitude=_rng.uniform(2.5, 5.0),
            period=_rng.uniform(55, 85),
            phase=frame_index * (2 * math.pi / FRAME_COUNT) + _rng.uniform(0, 1),
        )
        frame.paste(text_layer, (0, 0), text_layer)
        _draw_interference(frame, palette, frame_index, background)
        frames.append(frame.convert("P", palette=Image.Palette.ADAPTIVE, colors=64))

    buffer = io.BytesIO()
    frames[0].save(
        buffer,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        duration=FRAME_DURATION_MS,
        loop=0,
        optimize=False,
        disposal=1,
    )
    return buffer.getvalue()


def _paste_clipped(target: Image.Image, layer: Image.Image, position: tuple[int, int]) -> None:
    """alpha_composite that tolerates layers hanging over the edge of `target`."""
    x, y = position
    left = max(0, -x)
    top = max(0, -y)
    right = min(layer.width, target.width - x)
    bottom = min(layer.height, target.height - y)
    if right <= left or bottom <= top:
        return
    target.alpha_composite(layer.crop((left, top, right, bottom)), (x + left, y + top))
