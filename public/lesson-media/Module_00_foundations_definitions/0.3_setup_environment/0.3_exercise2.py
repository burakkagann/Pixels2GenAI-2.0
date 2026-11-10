"""
A test card: a two-colour fade whose size, colours and file name you control.

Author: Pixels2GenAI Project
"""
import numpy as np
from PIL import Image

# ========== CONFIG: change these values ==========
WIDTH = 400                     # Pixels across
HEIGHT = 200                    # Pixels down
COLOUR_LEFT = (0, 131, 138)     # Red, green, blue, each from 0 to 255
COLOUR_RIGHT = (243, 239, 231)  # The colour the fade ends on
OUTPUT_FILE = "test_card.png"   # Saved in the folder you run this script from
# =================================================

left = np.array(COLOUR_LEFT)
right = np.array(COLOUR_RIGHT)

# How far along the fade each column is, from 0 at the left to 1 at the right.
position = np.linspace(0, 1, WIDTH)[:, np.newaxis]
one_row = left + (right - left) * position

# Repeat that row until the picture is HEIGHT rows tall.
picture = np.tile(one_row, (HEIGHT, 1, 1))

Image.fromarray(picture.astype(np.uint8)).save(OUTPUT_FILE)
print(f"Saved {OUTPUT_FILE}, {WIDTH} by {HEIGHT} pixels")
