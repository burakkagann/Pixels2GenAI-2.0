"""
Helpers for the free sample lesson "Print the Berliner Dom as a poster" (/try).
They are loaded into every code cell, so cells stay short.
show() is provided by the page's runner: it draws an image under the cell.

Author: Pixels2GenAI Project
"""
import io

import numpy as np
from PIL import Image

PHOTO_FILE = "dom-480.png"   # 300 x 480, the photo the built /try uses


def _media_bytes(name):
    """Read a file from /try-media/ (browser) or from disk (offline tests)."""
    try:
        from js import Uint8Array, XMLHttpRequest
    except ImportError:
        import pathlib
        return (pathlib.Path(globals().get("_P2G_MEDIA_ROOT", ".")) / name).read_bytes()
    request = XMLHttpRequest.new()
    request.open("GET", "/try-media/" + name, False)
    request.responseType = "arraybuffer"
    request.send()
    return bytes(Uint8Array.new(request.response).to_py())


def load_photo():
    """The photo as numbers: 300 rows x 480 columns x 3 (red, green, blue), each 0-255."""
    image = Image.open(io.BytesIO(_media_bytes(PHOTO_FILE))).convert("RGB")
    return np.asarray(image).astype(int)


def swatches(pixels, size=60):
    """A few pixels drawn as big squares side by side."""
    pixels = np.asarray(pixels)
    return np.repeat(np.repeat(pixels[None, :, :], size, axis=0), size, axis=1)


def grey_swatches(numbers, size=60):
    """Brightness numbers drawn as grey squares."""
    return swatches([[n, n, n] for n in numbers], size)


def ink_swatches(numbers, threshold, ink=(32, 40, 120), paper=(246, 238, 222), size=60):
    """Each number as a square: ink where it is below the threshold, paper where not."""
    return swatches([list(ink) if n < threshold else list(paper) for n in numbers], size)


def paint(photo, rule):
    """Run rule(light) on every pixel's brightness (the average of its three numbers).
    Same answer as a loop over all 144,000 pixels; it asks the rule once per brightness level, so it is fast."""
    light = photo.sum(axis=2)                      # 0..765: three times the brightness
    table = np.array([rule(level / 3) for level in range(766)], dtype=int)
    return table[light]


def screenprint(photo, dark, mid, ink, tone, paper):
    """Three flat colours: ink below `dark`, tone below `mid`, paper above."""
    def rule(light):
        if light < dark:
            return ink
        if light < mid:
            return tone
        return paper
    return paint(photo, rule)
