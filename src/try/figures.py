"""
Figures for the free sample lesson /try ("Print the Berliner Dom as a poster"), picks TF-3 and HA-1 (16 Nov 2026).

Drawn with NumPy + Pillow from the real /try photo (public/try-media/dom-480.png) and the real lesson rule
(the same if-chain as public/try-media/helpers.py screenprint()). Workshop diagram theme (CNT-07, P3): site
colours for lines and text, the lesson's three colours only where a figure shows the print.

Each figure is drawn twice per theme:
  <name>.<light|dark>.webp        1400 x 760 (700 x 380 at 2x), for wide screens
  <name>.<light|dark>.phone.webp  800 px wide, stacked, so the labels stay readable at 360-600 px

  four-pixels   four real pixels of the Dom: three numbers -> one brightness (step 1)
  if-order      the same two ifs in both orders: which band each pixel lands in (step 3, once it works)

Concept figures (TRB-3 a, 16 Nov 2026: the concept library's figures, in public/concepts/fig/ because /try is public):
  grid-zoom     a photo is a grid of numbers: a 6 x 6 patch of the Dom, each square its real colour and brightness,
                one pixel's three numbers worked out (concept "brightness", K1-K4)
  mask          brightness -> light < 110 -> BLUE or PAPER on the same patch: the still behind the threshold slider
                (concept "threshold", K5-K6)
  three-bands   two thresholds, three colours, and the poster they make (concept "bands", K8)
  dom-grey.png  the photo's brightness, 240 x 150, for the threshold slider (ThresholdExplorer)
  dom-shares.json  for every threshold 0-256, the share of the 144,000 pixels the lesson's rule inks
                (light < threshold, light = (red + green + blue) / 3, as helpers.paint): the slider's percentage

Fonts: DejaVu Sans / Sans Mono from matplotlib, the diagram theme's documented fallback.
Run: python src/try/figures.py      Author: Pixels2GenAI Project
"""
import json
import pathlib

import matplotlib
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parents[2]
PHOTO = ROOT / "public" / "try-media" / "dom-480.png"
OUT = ROOT / "public" / "try-media" / "fig"
CONCEPT_OUT = ROOT / "public" / "concepts" / "fig"
SHARES = ROOT / "src" / "content" / "concepts" / "dom-shares.json"
FONT_DIR = pathlib.Path(matplotlib.get_data_path()) / "fonts" / "ttf"

SITE = {  # the workshop diagram theme (site colours)
    "light": {"background": "#FFFCF3", "text": "#141418", "muted": "#5B5B63", "line": "#BDB9AE", "pink": "#B02E64"},
    "dark": {"background": "#1B1B1F", "text": "#F2EEE6", "muted": "#8C8880", "line": "#3C3C43", "pink": "#F4669A"},
}
# The lesson's colours (src/try/cells/*.py): the print keeps them in both themes.
BLUE, PINK, PAPER = (32, 40, 120), (235, 80, 125), (246, 238, 222)

# The four numbers of step 1 ([30, 200, 120, 90]) are real pixels of the photo: (row, col).
FOUR = [((143, 188), "shadow"), ((209, 440), "sky"), ((89, 256), "green dome"), ((143, 264), "stone")]


def font(size, mono=False, bold=False):
    name = "DejaVuSans" + ("Mono" if mono else "") + ("-Bold" if bold else "") + ".ttf"
    return ImageFont.truetype(str(FONT_DIR / name), size)


def rgb(hex_text):
    hex_text = hex_text.lstrip("#")
    return tuple(int(hex_text[i:i + 2], 16) for i in (0, 2, 4))


def load_photo():
    return np.asarray(Image.open(PHOTO).convert("RGB")).astype(int)


def brightness(photo):
    return photo.sum(axis=2) / 3


def three_colours(light, dark=90, mid=150):
    """The lesson's rule, in the right order."""
    if light < dark:
        return BLUE
    if light < mid:
        return PINK
    return PAPER


def wrong_order(light):
    """The lesson's rule as step 3 starts: the wide question first, so BLUE never shows."""
    if light < 150:
        return PINK
    if light < 90:
        return BLUE
    return PAPER


def paint(photo, rule):
    """As helpers.paint: the rule once per brightness level, then a lookup for every pixel."""
    total = photo.sum(axis=2)
    table = np.array([rule(level / 3) for level in range(766)], dtype=np.uint8)
    return table[total]


def canvas(mode, width, height):
    colours = {k: rgb(v) for k, v in SITE[mode].items()}
    image = Image.new("RGB", (width, height), colours["background"])
    return image, ImageDraw.Draw(image), colours


def paste_array(image, array, x, y, width):
    picture = Image.fromarray(np.asarray(array, dtype=np.uint8))
    height = round(picture.height * width / picture.width)
    image.paste(picture.resize((width, height), Image.LANCZOS), (x, y))
    return height


def framed(image, draw, colours, array, x, y, width):
    """An image with a thin frame; returns its height."""
    height = paste_array(image, array, x, y, width)
    draw.rectangle([x, y, x + width, y + height], outline=colours["line"], width=2)
    return height


def ruler(image, draw, colours, x, y, width, thresholds, bands, labels):
    """The 0-255 brightness ruler: a grey ramp, the thresholds as ticks, and the ink bands under it."""
    ramp = np.tile(np.linspace(0, 255, width).astype(np.uint8)[None, :, None], (46, 1, 3))
    image.paste(Image.fromarray(ramp), (x, y))
    draw.rectangle([x, y, x + width, y + 46], outline=colours["line"], width=2)
    draw.text((x, y - 40), "0  black", font=font(27, mono=True), fill=colours["muted"], anchor="la")
    draw.text((x + width, y - 40), "255  white", font=font(27, mono=True), fill=colours["muted"], anchor="ra")
    edges = [0] + list(thresholds) + [256]
    for (low, high), colour, label in zip(zip(edges, edges[1:]), bands, labels):
        x0, x1 = x + round(low / 256 * width), x + round(high / 256 * width)
        draw.rectangle([x0, y + 62, x1, y + 120], fill=colour)
        text_colour = PAPER if colour in (BLUE, PINK) else (20, 20, 24)
        draw.text(((x0 + x1) / 2, y + 91), label, font=font(27, mono=True, bold=True), fill=text_colour, anchor="mm")
    draw.rectangle([x, y + 62, x + width, y + 120], outline=colours["line"], width=2)
    for value in thresholds:
        tick = x + round(value / 256 * width)
        draw.line([tick, y - 8, tick, y + 128], fill=colours["pink"], width=4)
        draw.text((tick, y - 40), str(value), font=font(26, mono=True, bold=True), fill=colours["pink"], anchor="ma")


def pixel_marker(draw, colours, x, y, width):
    """The triangle that follows a pixel at brightness 10 along a ruler."""
    tick = x + round(10 / 256 * width)
    draw.polygon([(tick, y + 136), (tick - 12, y + 158), (tick + 12, y + 158)], fill=colours["pink"])
    draw.text((tick + 20, y + 148), "a pixel at 10", font=font(26), fill=colours["pink"], anchor="lm")


def photo_with_circles(image, draw, colours, photo, x, y, width):
    """The photo with the four pixels of step 1 circled and numbered."""
    framed(image, draw, colours, photo, x, y, width)
    scale = width / photo.shape[1]
    for n, ((row, col), _) in enumerate(FOUR, 1):
        cx, cy = x + col * scale, y + row * scale
        draw.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], outline=(255, 255, 255), width=7)
        draw.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], outline=colours["pink"], width=4)
        draw.text((cx + 30, cy - 30), str(n), font=font(30, bold=True), fill=(255, 255, 255), anchor="mm",
                  stroke_width=4, stroke_fill=colours["pink"])
    return round(photo.shape[0] * scale)


def pixel_table(draw, colours, photo, x0, y0, row_height):
    """Per pixel: its three numbers, then its one brightness."""
    draw.text((x0, y0), "red, green, blue", font=font(26, mono=True), fill=colours["muted"])
    draw.text((x0 + 380, y0), "light", font=font(26, mono=True), fill=colours["muted"])
    for n, ((row, col), name) in enumerate(FOUR, 1):
        y = y0 + 50 + (n - 1) * row_height
        pixel = photo[row, col]
        light = round(pixel.sum() / 3)
        draw.text((x0, y + 40), str(n), font=font(30, bold=True), fill=colours["pink"], anchor="lm")
        draw.rectangle([x0 + 34, y, x0 + 114, y + 80], fill=tuple(int(v) for v in pixel), outline=colours["line"], width=2)
        draw.text((x0 + 132, y + 14), " ".join(f"{int(v):>3}" for v in pixel), font=font(28, mono=True), fill=colours["text"])
        draw.text((x0 + 132, y + 54), name, font=font(26), fill=colours["muted"])
        draw.text((x0 + 330, y + 28), "→", font=font(30), fill=colours["muted"])
        draw.rectangle([x0 + 380, y, x0 + 460, y + 80], fill=(light, light, light), outline=colours["line"], width=2)
        draw.text((x0 + 476, y + 40), str(light), font=font(32, mono=True, bold=True), fill=colours["text"], anchor="lm")


# ---------- wide (1400 x 760) ----------

def four_pixels(mode):
    image, draw, c = canvas(mode, 1400, 760)
    photo = load_photo()
    photo_with_circles(image, draw, c, photo, 60, 70, 720)
    draw.text((60, 640), "one pixel = three numbers, 0 to 255", font=font(26), fill=c["muted"])
    draw.text((60, 684), "brightness = (red + green + blue) / 3", font=font(26, mono=True), fill=c["text"])
    pixel_table(draw, c, photo, 840, 40, 150)
    return image



def three_bands(mode):
    image, draw, c = canvas(mode, 1400, 760)
    ruler(image, draw, c, 70, 90, 1260, [90, 150], [BLUE, PINK, PAPER], ["BLUE", "PINK", "PAPER"])
    for i, (test, ink) in enumerate([("light < 90", "BLUE"), ("light < 150", "PINK"), ("otherwise", "PAPER")]):
        draw.text((70, 270 + i * 52), f"{test:<12}→ {ink}", font=font(28, mono=True), fill=c["text"])
    framed(image, draw, c, paint(load_photo(), three_colours), 800, 250, 530)
    draw.text((70, 460), "two questions, three colours", font=font(27), fill=c["muted"])
    return image


IF_ORDERS = [
    (three_colours, "if light < 90 first", [BLUE, PINK, PAPER], ["BLUE", "PINK", "PAPER"], [90, 150]),
    (wrong_order, "if light < 150 first", [PINK, PAPER], ["PINK  (10 stops here)", "PAPER"], [150]),
]


def if_order(mode):
    image, draw, c = canvas(mode, 1400, 760)
    photo = load_photo()
    for i, (rule, title, bands, labels, edges) in enumerate(IF_ORDERS):
        y = 70 + i * 345
        draw.text((70, y), title, font=font(28, mono=True, bold=True), fill=c["text"])
        ruler(image, draw, c, 70, y + 100, 820, edges, bands, labels)
        framed(image, draw, c, paint(photo, rule), 960, y + 30, 370)
        pixel_marker(draw, c, 70, y + 100, 820)
    return image


# ---------- phone (800 px wide, stacked) ----------

def four_pixels_phone(mode):
    image, draw, c = canvas(mode, 800, 1250)
    photo = load_photo()
    h = photo_with_circles(image, draw, c, photo, 40, 40, 720)
    draw.text((40, 40 + h + 26), "one pixel = three numbers, 0 to 255", font=font(26), fill=c["muted"])
    draw.text((40, 40 + h + 68), "brightness = (red + green + blue) / 3", font=font(26, mono=True), fill=c["text"])
    pixel_table(draw, c, photo, 60, 40 + h + 140, 140)
    return image



def three_bands_phone(mode):
    image, draw, c = canvas(mode, 800, 970)
    ruler(image, draw, c, 40, 90, 720, [90, 150], [BLUE, PINK, PAPER], ["BLUE", "PINK", "PAPER"])
    for i, (test, ink) in enumerate([("light < 90", "BLUE"), ("light < 150", "PINK"), ("otherwise", "PAPER")]):
        draw.text((40, 250 + i * 52), f"{test:<12}→ {ink}", font=font(28, mono=True), fill=c["text"])
    draw.text((40, 420), "two questions, three colours", font=font(27), fill=c["muted"])
    framed(image, draw, c, paint(load_photo(), three_colours), 40, 480, 720)
    return image


def if_order_phone(mode):
    image, draw, c = canvas(mode, 800, 1230)
    photo = load_photo()
    for i, (rule, title, bands, labels, edges) in enumerate(IF_ORDERS):
        y = 40 + i * 620
        draw.text((40, y), title, font=font(28, mono=True, bold=True), fill=c["text"])
        ruler(image, draw, c, 40, y + 100, 720, edges, bands, labels)
        pixel_marker(draw, c, 40, y + 100, 720)
        framed(image, draw, c, paint(photo, rule), 40, y + 290, 400)
    return image




# ---------- concept figures (public/concepts/fig) ----------

PATCH = (55, 215)          # top-left (row, col) of the 6 x 6 patch: the dome's lantern, dark gaps and light stone
SIZE = 6
WORKED = (5, 1)            # the patch cell worked out by hand: (90, 88, 83) -> 87, the concept's worked example
MASK_THRESHOLD = 110       # the threshold slider starts here, so the still and the slider agree


def patch():
    photo = load_photo()
    r, c = PATCH
    block = photo[r:r + SIZE, c:c + SIZE]
    return photo, block, np.round(block.sum(axis=2) / 3).astype(int)


def on(colour):
    """Text colour that reads on a fill."""
    return (20, 20, 24) if sum(colour) / 3 > 140 else (250, 248, 242)


def grid(draw, colours, x, y, cell, fills, texts, size=28, mark=None):
    for i in range(SIZE):
        for j in range(SIZE):
            fill = tuple(int(v) for v in fills[i][j])
            x0, y0 = x + j * cell, y + i * cell
            draw.rectangle([x0, y0, x0 + cell, y0 + cell], fill=fill, outline=colours["background"], width=2)
            draw.text((x0 + cell / 2, y0 + cell / 2), str(texts[i][j]), font=font(size, mono=True, bold=True),
                      fill=on(fill), anchor="mm")
    if mark:
        i, j = mark
        draw.rectangle([x + j * cell - 2, y + i * cell - 2, x + (j + 1) * cell + 2, y + (i + 1) * cell + 2],
                       outline=colours["pink"], width=6)


def photo_with_box(image, draw, c, photo, x, y, width):
    h = framed(image, draw, c, photo, x, y, width)
    s = width / photo.shape[1]
    r0, c0 = PATCH
    bx, by = x + c0 * s, y + r0 * s
    draw.rectangle([bx - 6, by - 6, bx + SIZE * s + 6, by + SIZE * s + 6], outline=(255, 255, 255), width=6)
    draw.rectangle([bx - 6, by - 6, bx + SIZE * s + 6, by + SIZE * s + 6], outline=c["pink"], width=3)
    return h, (bx + SIZE * s + 6, by)


def worked_line(draw, c, block, x, y, size=26):
    """The marked pixel's three numbers and their average: K3 and K4 in one line."""
    red, green, blue = (int(v) for v in block[WORKED])
    draw.text((x, y), f"marked: ({red} + {green} + {blue}) / 3 = {round((red + green + blue) / 3)}",
              font=font(size, mono=True, bold=True), fill=c["pink"])


def grid_zoom(mode, phone=False):
    photo, block, light = patch()
    if not phone:
        image, draw, c = canvas(mode, 1400, 760)
        h, (bx, by) = photo_with_box(image, draw, c, photo, 50, 90, 640)
        gx, gy, cell = 800, 60, 90
        draw.line([bx, by, gx, gy], fill=c["pink"], width=3)
        draw.line([bx, by + 12, gx, gy + SIZE * cell], fill=c["pink"], width=3)
        grid(draw, c, gx, gy, cell, block, light, mark=WORKED)
        draw.text((50, 90 + h + 30), "300 rows × 480 columns = 144,000 pixels", font=font(28), fill=c["text"])
        draw.text((50, 90 + h + 76), "each pixel: red, green, blue, each 0 to 255", font=font(26), fill=c["muted"])
        draw.text((gx, gy + SIZE * cell + 24), "the number: each pixel's brightness", font=font(26), fill=c["muted"])
        worked_line(draw, c, block, gx, gy + SIZE * cell + 66)
        return image
    image, draw, c = canvas(mode, 800, 1340)
    h, (bx, by) = photo_with_box(image, draw, c, photo, 40, 40, 720)
    gx, gy, cell = 130, 40 + h + 70, 90
    draw.line([bx, by, gx + SIZE * cell, gy], fill=c["pink"], width=3)
    grid(draw, c, gx, gy, cell, block, light, mark=WORKED)
    y = gy + SIZE * cell + 34
    draw.text((40, y), "300 rows × 480 columns = 144,000 pixels", font=font(28), fill=c["text"])
    draw.text((40, y + 46), "each pixel: red, green, blue, 0 to 255", font=font(26), fill=c["muted"])
    draw.text((40, y + 86), "number = brightness (0 black, 255 white)", font=font(26), fill=c["muted"])
    worked_line(draw, c, block, 40, y + 136, size=28)
    return image


def mask(mode, phone=False, threshold=MASK_THRESHOLD):
    _, _, light = patch()
    grey = [[(v, v, v) for v in row] for row in light]
    truth = light < threshold
    tf = [["T" if t else "F" for t in row] for row in truth]
    tf_fill = [[(205, 205, 210) if t else (90, 90, 96) for t in row] for row in truth]
    inks = [[BLUE if t else PAPER for t in row] for row in truth]
    blank = [["" for _ in row] for row in truth]
    panels = [(grey, light, "light"), (tf_fill, tf, f"light < {threshold}"), (inks, blank, "BLUE or PAPER")]
    if not phone:
        image, draw, c = canvas(mode, 1400, 760)
        cell = 64
        for k, (fills, texts, label) in enumerate(panels):
            x = 60 + k * 470
            draw.text((x, 110), label, font=font(28, mono=True, bold=True), fill=c["text"])
            grid(draw, c, x, 170, cell, fills, texts, size=24)
            if k < 2:
                draw.text((x + SIZE * cell + 45, 170 + SIZE * cell / 2), "→", font=font(40), fill=c["muted"], anchor="mm")
        draw.text((60, 620), "One question per pixel. T = True gets ink, F = False stays paper.", font=font(27), fill=c["muted"])
        draw.text((60, 666), "The True/False grid is a mask: it marks where the ink goes.", font=font(27), fill=c["muted"])
        return image
    image, draw, c = canvas(mode, 800, 1340)
    cell = 56
    for k, (fills, texts, label) in enumerate(panels):
        y = 40 + k * 430
        x = 400 - SIZE * cell // 2
        draw.text((x, y), label, font=font(28, mono=True, bold=True), fill=c["text"])
        grid(draw, c, x, y + 50, cell, fills, texts, size=22)
        if k < 2:
            draw.text((x + SIZE * cell / 2, y + 50 + SIZE * cell + 22), "↓", font=font(36), fill=c["muted"], anchor="mm")
    draw.text((40, 1290), "T = True gets ink. The T/F grid is a mask.", font=font(27), fill=c["muted"])
    return image


def explorer_assets(photo):
    """The slider's two inputs: a small grey copy of the photo and the exact ink share per threshold."""
    grey = Image.fromarray(np.round(brightness(photo)).astype(np.uint8), "L").resize((240, 150), Image.LANCZOS)
    grey.save(CONCEPT_OUT / "dom-grey.png", optimize=True)
    total = photo.sum(axis=2)                    # light < t  <=>  red + green + blue < 3 t
    shares = [round(float((total < 3 * t).mean()), 4) for t in range(257)]
    SHARES.parent.mkdir(parents=True, exist_ok=True)
    SHARES.write_text(json.dumps({"source": "public/try-media/dom-480.png", "pixels": int(total.size),
                                  "shares": shares}) + "\n", encoding="utf-8")
    print("ink share at 60, 90, 110, 120:", [round(shares[t] * 100, 1) for t in (60, 90, 110, 120)], "%")


# ---- Go further targets (GF-2, 19 Nov 2026; chained 19 Nov, GFC-1 b): the end picture of each task, drawn from the task's
# solution file (cells/chain_*.py) with the real helpers, so the target is what the solution makes ----
YELLOW = (245, 200, 60)
PURPLE = (120, 60, 140)


def helper_poster(stage):
    """Run cells/<stage>.py as the page does (helpers + np in scope) and return the last image it shows."""
    import sys
    sys.path.insert(0, str(ROOT / "public" / "try-media"))
    import helpers
    helpers._P2G_MEDIA_ROOT = str(ROOT / "public" / "try-media")
    shown = []
    scope = {name: getattr(helpers, name) for name in dir(helpers) if not name.startswith("__")}
    scope.update(np=np, show=lambda image, label="": shown.append(np.asarray(image)))
    exec(compile((ROOT / "src" / "try" / "cells" / f"{stage}.py").read_text(encoding="utf-8"), stage, "exec"), scope)
    return shown[-1]


TARGETS = {  # figure name: (stage file, title, subtitle, legend)
    "four": ("chain_four", "four colours", "", [("BLUE", BLUE), ("PINK", PINK), ("YELLOW", YELLOW), ("PAPER", PAPER)]),
    "grain": ("chain_grain", "four colours", "GRAIN = 20", [("BLUE", BLUE), ("PINK", PINK), ("YELLOW", YELLOW), ("PAPER", PAPER)]),
    "bands": ("chain_bands", "five colours", "GRAIN = 20", [("BLUE", BLUE), ("PURPLE", PURPLE), ("PINK", PINK), ("YELLOW", YELLOW), ("PAPER", PAPER)]),
}


def swatch(draw, c, x, y, size, colour, label):
    draw.rectangle([x, y, x + size, y + size], fill=colour, outline=c["line"], width=2)
    draw.text((x + size + 18, y + size / 2), label, font=font(30, mono=True, bold=True), fill=c["text"], anchor="lm")


def further_target(which, mode, phone=False):
    stage, title, subtitle, legend = TARGETS[which]
    poster = helper_poster(stage)
    if phone:
        image, draw, c = canvas(mode, 800, 700)
        framed(image, draw, c, poster, 40, 90, 720)
        draw.text((40, 36), f"Target: {title}" + (f", {subtitle}" if subtitle else ""), font=font(30, mono=True, bold=True), fill=c["text"])
        for i, (label, colour) in enumerate(legend):
            swatch(draw, c, 40 + (i % 3) * 250, 580 + (i // 3) * 56, 36, colour, label)
        return image
    image, draw, c = canvas(mode, 1400, 560)
    framed(image, draw, c, poster, 60, 30, 820)
    draw.text((980, 70), "Target", font=font(26), fill=c["muted"])
    draw.text((980, 112), title, font=font(34, mono=True, bold=True), fill=c["text"])
    if subtitle:
        draw.text((980, 156), subtitle, font=font(26, mono=True), fill=c["muted"])
    for i, (label, colour) in enumerate(legend):
        swatch(draw, c, 980, 210 + i * 62, 40, colour, label)
    return image


def save_all(folder, figures):
    folder.mkdir(parents=True, exist_ok=True)
    for name, wide, phone in figures:
        for mode in ("light", "dark"):
            for suffix, make in (("", wide), (".phone", phone)):
                path = folder / f"{name}.{mode}{suffix}.webp"
                make(mode).save(path, quality=82, method=6)
                print(path.relative_to(ROOT), path.stat().st_size // 1024, "KB")


def main():
    save_all(OUT, [("four-pixels", four_pixels, four_pixels_phone), ("if-order", if_order, if_order_phone)])
    save_all(CONCEPT_OUT, [("grid-zoom", grid_zoom, lambda mode: grid_zoom(mode, phone=True)),
                           ("mask", mask, lambda mode: mask(mode, phone=True)),
                           ("three-bands", three_bands, three_bands_phone)])
    save_all(OUT, [(f"go-further-{which}", lambda mode, which=which: further_target(which, mode),
                    lambda mode, which=which: further_target(which, mode, phone=True)) for which in TARGETS])
    photo = load_photo()
    explorer_assets(photo)
    print("step 1 pixels:", [round(photo[r, k].sum() / 3) for (r, k), _ in FOUR])


if __name__ == "__main__":
    main()
