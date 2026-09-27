import numpy as np
from PIL import Image

N_TILES = 16            # the image is cut into N_TILES x N_TILES tiles
N_FRAMES = 60
SCATTER_RADIUS = 250    # smaller than Exercise 1, so the spinning tiles stay on the canvas
SEED = 7


def ease_out_cubic(t):
    return 1 - (1 - t) ** 3


flower = np.array(Image.open('flower.png').convert('RGB'))
H, W, _ = flower.shape
th, tw = H // N_TILES, W // N_TILES
home_yx = [(r * th, c * tw) for r in range(N_TILES) for c in range(N_TILES)]   # each tile's home corner

# Random scatter: every tile starts up to SCATTER_RADIUS away from home
rng = np.random.default_rng(SEED)
angles = rng.uniform(0, 2 * np.pi, len(home_yx))
radii = rng.uniform(SCATTER_RADIUS * 0.5, SCATTER_RADIUS, len(home_yx))
start_offsets = np.stack([(radii * np.sin(angles)).astype(int),
                          (radii * np.cos(angles)).astype(int)], axis=1)

# One random start rotation per tile, computed once so it stays the same in every frame
start_rotations = rng.uniform(-180, 180, len(home_yx))

frames = []
for f in range(N_FRAMES):
    progress = ease_out_cubic(f / (N_FRAMES - 1))
    offsets = (start_offsets * (1 - progress)).astype(int)
    canvas_image = Image.new('RGB', (W, H), (12, 12, 12))   # a fresh canvas every frame
    for i, ((cy, cx), (dy, dx)) in enumerate(zip(home_yx, offsets)):
        y, x = cy + dy, cx + dx
        if not (0 <= y <= H - th and 0 <= x <= W - tw):
            continue                                        # still off the canvas
        tile_img = Image.fromarray(flower[cy:cy + th, cx:cx + tw])

        # The rotation shrinks to 0 as the tile arrives, in step with the translation
        angle = start_rotations[i] * (1 - progress)

        # expand=True grows the image so the rotated corners are kept; pasting at
        # (centre - rotated size / 2) keeps the tile centred on its destination
        rotated = tile_img.rotate(angle, expand=True, resample=Image.BILINEAR)
        rw, rh = rotated.size
        ry, rx = y + th // 2, x + tw // 2
        canvas_image.paste(rotated, (rx - rw // 2, ry - rh // 2))
    frames.append(canvas_image)

frames[0].save('flower_twirl.gif', save_all=True, append_images=frames[1:], duration=50, loop=0)
print(f"Saved flower_twirl.gif: {N_FRAMES} frames, {len(home_yx)} tiles")
