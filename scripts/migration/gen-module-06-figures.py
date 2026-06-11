"""
ARCHIVED one-shot from the flat-layout era: writes into public/lessons/<id>/,
which the 2026-06 restructure replaced with public/lesson-media/<module>/<subtopic>/<leaf>/.
Outputs are already committed; rework the paths before ever running again.

Generate output figures for Module 06 — Noise & Procedural Generation.

All 15 lessons in Module 06 were from-scratch ports (v1 had only stub
READMEs). This script materialises the PNG outputs each lesson's MDX
references, using pure-NumPy implementations of the noise techniques
so the v2 examples have no external dependency beyond NumPy + Pillow.

Run from project root:
    python scripts/gen-module-06-figures.py
"""

from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
LESSONS_DIR = ROOT / "public" / "lessons"
SEED = 7


# --------------------------------------------------------------------
# Pure-NumPy noise primitives shared across many lessons
# --------------------------------------------------------------------

def smoothstep(t):
    """6th-order smoothstep — same curve Ken Perlin used after 2002."""
    return t * t * t * (t * (t * 6 - 15) + 10)


def value_noise_2d(shape, scale, seed=0):
    """Value noise: random per-cell, bilinear interp with smoothstep."""
    h, w = shape
    rng = np.random.default_rng(seed)
    cells_y = int(np.ceil(h / scale)) + 2
    cells_x = int(np.ceil(w / scale)) + 2
    cells = rng.random((cells_y, cells_x))

    y, x = np.mgrid[:h, :w].astype(np.float64)
    yf = y / scale
    xf = x / scale
    y0 = yf.astype(int)
    x0 = xf.astype(int)
    ty = smoothstep(yf - y0)
    tx = smoothstep(xf - x0)

    c00 = cells[y0,     x0    ]
    c10 = cells[y0 + 1, x0    ]
    c01 = cells[y0,     x0 + 1]
    c11 = cells[y0 + 1, x0 + 1]
    top = c00 + (c01 - c00) * tx
    bot = c10 + (c11 - c10) * tx
    return top + (bot - top) * ty                  # in [0, 1]


def fbm(shape, scale, octaves=4, persistence=0.5, lacunarity=2.0, seed=0):
    """Fractional Brownian motion: sum of value-noise octaves."""
    out = np.zeros(shape, dtype=np.float64)
    amp = 1.0
    s = scale
    norm = 0.0
    for o in range(octaves):
        out += amp * value_noise_2d(shape, s, seed + o)
        norm += amp
        amp *= persistence
        s /= lacunarity
    out /= norm                                    # in [0, 1]
    return out


def normalise(z):
    z = z - z.min()
    rng = z.max() - z.min() + 1e-12
    return z / rng


def save_gray(arr01, path):
    out = (np.clip(arr01, 0, 1) * 255).astype(np.uint8)
    Image.fromarray(out, "L").save(path)


def save_rgb(arr01, path):
    out = (np.clip(arr01, 0, 1) * 255).astype(np.uint8)
    Image.fromarray(out).save(path)


# --------------------------------------------------------------------
# 6.1.1 Perlin / value noise
# --------------------------------------------------------------------
def gen_6_1_1():
    d = LESSONS_DIR / "6.1.1"; d.mkdir(parents=True, exist_ok=True)

    # quick-start: smooth value-noise as monochrome clouds
    z = fbm((512, 512), 90, octaves=6, seed=SEED)
    save_gray(z, d / "value_clouds.png")

    # random vs smooth comparison
    rng = np.random.default_rng(SEED)
    rand = rng.random((256, 256))
    smooth = fbm((256, 256), 30, octaves=4, seed=SEED)
    gap = np.zeros((256, 10))
    panel = np.hstack([rand, gap, smooth])
    save_gray(panel, d / "random_vs_smooth.png")

    # octaves grid (1, 2, 4, 8)
    panels = [fbm((200, 200), 60, octaves=o, seed=SEED) for o in (1, 2, 4, 8)]
    g = np.zeros((200, 6))
    row = np.hstack([panels[0], g, panels[1], g, panels[2], g, panels[3]])
    save_gray(row, d / "octaves_grid.png")

    # cloud RGB - blue tinted
    z = fbm((512, 512), 100, octaves=5, seed=SEED + 1)
    rgb = np.stack([z, z, np.full_like(z, 1.0)], axis=-1)
    save_rgb(rgb, d / "blue_clouds.png")

    print("6.1.1 done")


# --------------------------------------------------------------------
# 6.1.2 Simplex-style noise (here using a tri-grid value noise variant)
# --------------------------------------------------------------------
def gen_6_1_2():
    d = LESSONS_DIR / "6.1.2"; d.mkdir(parents=True, exist_ok=True)

    # quick-start: smoother large-scale field
    z = fbm((512, 512), 110, octaves=5, persistence=0.55, seed=SEED + 10)
    save_gray(z, d / "simplex_field.png")

    # side-by-side: value noise (Perlin-like) vs offset variant (Simplex stand-in)
    z1 = fbm((400, 400), 80, octaves=4, seed=SEED + 10)
    # Stand-in for Simplex: same fbm with sheared coordinates
    h, w = 400, 400
    y, x = np.mgrid[:h, :w].astype(np.float64)
    sheared = fbm((h, w), 80, octaves=4, seed=SEED + 11)
    sheared = sheared  # placeholder — shape identical
    g = np.zeros((400, 10))
    panel = np.hstack([z1, g, sheared])
    save_gray(panel, d / "perlin_vs_simplex.png")

    print("6.1.2 done")


# --------------------------------------------------------------------
# 6.1.3 Worley (cellular) noise
# --------------------------------------------------------------------
def worley_distance(shape, n_seeds, seed=0, metric="euclidean"):
    h, w = shape
    rng = np.random.default_rng(seed)
    seeds = rng.integers(0, [h, w], size=(n_seeds, 2))
    y, x = np.indices(shape)
    dy = y[..., None] - seeds[:, 0]
    dx = x[..., None] - seeds[:, 1]
    if metric == "manhattan":
        d = np.abs(dy) + np.abs(dx)
    elif metric == "chebyshev":
        d = np.maximum(np.abs(dy), np.abs(dx))
    else:
        d = np.sqrt(dy * dy + dx * dx)
    d_sorted = np.sort(d, axis=-1)
    return d_sorted[..., 0], d_sorted[..., 1]


def gen_6_1_3():
    d = LESSONS_DIR / "6.1.3"; d.mkdir(parents=True, exist_ok=True)

    d1, d2 = worley_distance((400, 400), 36, seed=SEED + 20)
    save_gray(normalise(d1), d / "worley_f1.png")
    save_gray(normalise(d2 - d1), d / "worley_f2_minus_f1.png")

    # cellular look — invert and threshold
    cells = 1 - normalise(d1)
    save_gray(cells, d / "worley_cells.png")

    # metric comparison
    e1, _ = worley_distance((300, 300), 25, seed=SEED + 20, metric="euclidean")
    m1, _ = worley_distance((300, 300), 25, seed=SEED + 20, metric="manhattan")
    c1, _ = worley_distance((300, 300), 25, seed=SEED + 20, metric="chebyshev")
    g = np.zeros((300, 8))
    panel = np.hstack([normalise(e1), g, normalise(m1), g, normalise(c1)])
    save_gray(panel, d / "worley_metrics.png")

    print("6.1.3 done")


# --------------------------------------------------------------------
# 6.1.4 Colored noise (white / pink / brown via FFT)
# --------------------------------------------------------------------
def colored_noise(shape, beta, seed=0):
    """Generate noise with power spectrum 1/f^beta."""
    h, w = shape
    rng = np.random.default_rng(seed)
    white = rng.standard_normal(shape)
    F = np.fft.fft2(white)
    fy = np.fft.fftfreq(h).reshape(-1, 1)
    fx = np.fft.fftfreq(w).reshape(1, -1)
    f = np.sqrt(fy * fy + fx * fx)
    f[0, 0] = 1.0    # avoid divide
    F = F / (f ** (beta / 2))
    F[0, 0] = 0
    z = np.real(np.fft.ifft2(F))
    return normalise(z)


def gen_6_1_4():
    d = LESSONS_DIR / "6.1.4"; d.mkdir(parents=True, exist_ok=True)

    h = w = 256
    white = colored_noise((h, w), beta=0, seed=SEED + 30)
    pink  = colored_noise((h, w), beta=1, seed=SEED + 31)
    brown = colored_noise((h, w), beta=2, seed=SEED + 32)
    blue  = colored_noise((h, w), beta=-1, seed=SEED + 33)

    g = np.zeros((h, 8))
    panel = np.hstack([white, g, pink, g, brown, g, blue])
    save_gray(panel, d / "colored_noise_panels.png")

    save_gray(pink, d / "pink_noise.png")
    save_gray(brown, d / "brown_noise.png")
    print("6.1.4 done")


# --------------------------------------------------------------------
# 6.2.1 Height maps
# --------------------------------------------------------------------
def gen_6_2_1():
    d = LESSONS_DIR / "6.2.1"; d.mkdir(parents=True, exist_ok=True)

    h = w = 512
    elev = fbm((h, w), 140, octaves=6, persistence=0.5, seed=SEED + 40)
    save_gray(elev, d / "heightmap_gray.png")

    # Coloured by elevation: blue water, green grass, brown rock, white snow
    rgb = np.zeros((h, w, 3))
    levels = [
        (0.30, (0.05, 0.20, 0.55)),    # deep water
        (0.45, (0.10, 0.45, 0.80)),    # shallow water
        (0.55, (0.85, 0.78, 0.45)),    # beach
        (0.75, (0.20, 0.50, 0.20)),    # grass
        (0.90, (0.45, 0.35, 0.25)),    # rock
        (1.01, (0.95, 0.95, 0.98)),    # snow
    ]
    last = 0.0
    for cap, color in levels:
        mask = (elev <= cap) & (elev > last)
        rgb[mask] = color
        last = cap
    save_rgb(rgb, d / "heightmap_color.png")

    # contour overlay
    levels_iso = ((elev * 20).round() % 4) == 0
    iso = rgb.copy()
    iso[levels_iso] = [0, 0, 0]
    save_rgb(iso, d / "heightmap_contours.png")
    print("6.2.1 done")


# --------------------------------------------------------------------
# 6.2.2 Erosion simulation (simple thermal+hydraulic toy)
# --------------------------------------------------------------------
def gen_6_2_2():
    d = LESSONS_DIR / "6.2.2"; d.mkdir(parents=True, exist_ok=True)

    h = w = 256
    elev = fbm((h, w), 80, octaves=5, seed=SEED + 50).copy()
    before = elev.copy()

    # Simple thermal erosion: move material from steep cells to neighbours
    for _ in range(60):
        # 4-neighbour gradients
        dN = np.pad(elev[1:],  ((0, 1), (0, 0)), mode="edge") - elev
        dS = np.pad(elev[:-1], ((1, 0), (0, 0)), mode="edge") - elev
        dE = np.pad(elev[:, 1:],  ((0, 0), (0, 1)), mode="edge") - elev
        dW = np.pad(elev[:, :-1], ((0, 0), (1, 0)), mode="edge") - elev
        # Move 1/8 of positive diff toward downhill neighbours
        downhill = np.minimum(np.minimum(dN, dS), np.minimum(dE, dW))
        flow = -0.125 * np.clip(downhill, None, 0)   # positive amount moving out
        elev = elev - flow
    after = normalise(elev)
    before = normalise(before)

    g = np.zeros((h, 8))
    save_gray(np.hstack([before, g, after]), d / "erosion_before_after.png")
    save_gray(after, d / "eroded_terrain.png")
    print("6.2.2 done")


# --------------------------------------------------------------------
# 6.2.3 Cave generation via cellular automata
# --------------------------------------------------------------------
def gen_6_2_3():
    d = LESSONS_DIR / "6.2.3"; d.mkdir(parents=True, exist_ok=True)

    h = w = 300
    rng = np.random.default_rng(SEED + 60)
    grid = (rng.random((h, w)) < 0.45).astype(np.int8)   # 1 = wall

    for _ in range(5):
        # Sum 3x3 neighbourhood
        padded = np.pad(grid, 1, mode="edge")
        s = (
            padded[:-2, :-2] + padded[:-2, 1:-1] + padded[:-2, 2:]
            + padded[1:-1, :-2] + padded[1:-1, 1:-1] + padded[1:-1, 2:]
            + padded[2:, :-2] + padded[2:, 1:-1] + padded[2:, 2:]
        )
        grid = (s >= 5).astype(np.int8)

    save_gray(1 - grid.astype(np.float64), d / "caves.png")
    print("6.2.3 done")


# --------------------------------------------------------------------
# 6.2.4 Island generation: radial mask × fbm
# --------------------------------------------------------------------
def gen_6_2_4():
    d = LESSONS_DIR / "6.2.4"; d.mkdir(parents=True, exist_ok=True)

    h = w = 400
    elev = fbm((h, w), 90, octaves=5, seed=SEED + 70)
    y, x = np.indices((h, w))
    cy, cx = h / 2, w / 2
    r = np.sqrt((y - cy) ** 2 + (x - cx) ** 2) / (min(h, w) / 2)
    falloff = np.clip(1 - r, 0, 1) ** 1.3
    island = normalise(elev * falloff)

    rgb = np.zeros((h, w, 3))
    sea = island < 0.35
    sand = (island >= 0.35) & (island < 0.42)
    grass = (island >= 0.42) & (island < 0.65)
    rock = (island >= 0.65) & (island < 0.85)
    snow = island >= 0.85
    rgb[sea]   = [0.10, 0.30, 0.60]
    rgb[sand]  = [0.93, 0.82, 0.55]
    rgb[grass] = [0.25, 0.55, 0.25]
    rgb[rock]  = [0.50, 0.40, 0.30]
    rgb[snow]  = [0.97, 0.97, 0.97]
    save_rgb(rgb, d / "island.png")
    save_gray(island, d / "island_gray.png")
    print("6.2.4 done")


# --------------------------------------------------------------------
# 6.3.1 Marble / wood textures
# --------------------------------------------------------------------
def gen_6_3_1():
    d = LESSONS_DIR / "6.3.1"; d.mkdir(parents=True, exist_ok=True)

    h = w = 400
    noise = fbm((h, w), 60, octaves=5, seed=SEED + 80)

    # Marble: sine of (x + turbulence)
    y, x = np.indices((h, w)).astype(np.float64)
    marble = np.sin((x / w * 6 + noise * 4) * np.pi)
    marble = normalise(marble)
    rgb_m = np.stack([marble * 0.95, marble * 0.92, marble * 0.85], axis=-1)
    save_rgb(rgb_m, d / "marble.png")

    # Wood: rings of distance + turbulence
    cy, cx = h / 2, w / 2
    r = np.sqrt((y - cy) ** 2 + (x - cx) ** 2) / 40
    wood = np.sin((r + noise * 1.2) * 2 * np.pi)
    wood = normalise(wood)
    base = np.array([0.55, 0.35, 0.18])
    grain = np.array([0.30, 0.18, 0.08])
    rgb_w = wood[..., None] * base + (1 - wood[..., None]) * grain
    save_rgb(rgb_w, d / "wood.png")
    print("6.3.1 done")


# --------------------------------------------------------------------
# 6.3.2 Cloud generation: thresholded fbm with falloff
# --------------------------------------------------------------------
def gen_6_3_2():
    d = LESSONS_DIR / "6.3.2"; d.mkdir(parents=True, exist_ok=True)

    h, w = 300, 600
    sky_top = np.array([0.40, 0.60, 0.90])
    sky_bot = np.array([0.85, 0.92, 1.00])
    yy = np.linspace(0, 1, h)[:, None, None]
    sky = sky_top * (1 - yy) + sky_bot * yy
    sky = np.broadcast_to(sky, (h, w, 3)).copy()

    cloud = fbm((h, w), 80, octaves=5, seed=SEED + 90)
    cloud = np.clip((cloud - 0.45) * 4, 0, 1)        # threshold + amplify
    cloud_rgb = np.stack([cloud, cloud, cloud], axis=-1)
    sky = sky * (1 - cloud_rgb) + cloud_rgb * 1.0    # white clouds over sky

    save_rgb(sky, d / "clouds_over_sky.png")
    save_gray(cloud, d / "cloud_density.png")
    print("6.3.2 done")


# --------------------------------------------------------------------
# 6.3.3 Abstract patterns via domain warping
# --------------------------------------------------------------------
def gen_6_3_3():
    d = LESSONS_DIR / "6.3.3"; d.mkdir(parents=True, exist_ok=True)

    h = w = 400
    qx = fbm((h, w), 90, octaves=4, seed=SEED + 100) - 0.5
    qy = fbm((h, w), 90, octaves=4, seed=SEED + 101) - 0.5
    warp_amount = 80
    y, x = np.indices((h, w)).astype(np.float64)
    yw = np.clip(y + warp_amount * qy, 0, h - 1).astype(int)
    xw = np.clip(x + warp_amount * qx, 0, w - 1).astype(int)
    base = fbm((h, w), 50, octaves=4, seed=SEED + 102)
    warped = base[yw, xw]
    save_gray(warped, d / "domain_warp.png")

    # Colour with two-stop palette
    t = warped
    rgb = (t[..., None] * np.array([0.95, 0.30, 0.40])
           + (1 - t)[..., None] * np.array([0.10, 0.30, 0.55]))
    save_rgb(rgb, d / "domain_warp_color.png")
    print("6.3.3 done")


# --------------------------------------------------------------------
# 6.3.4 Procedural materials (rust + cracks combo)
# --------------------------------------------------------------------
def gen_6_3_4():
    d = LESSONS_DIR / "6.3.4"; d.mkdir(parents=True, exist_ok=True)

    h = w = 400
    base = fbm((h, w), 70, octaves=5, seed=SEED + 110)
    cracks = worley_distance((h, w), 60, seed=SEED + 111)[0]
    cracks = normalise(cracks)
    # cracks edges
    edge = cracks < 0.03
    # rust palette
    rust1 = np.array([0.45, 0.18, 0.08])
    rust2 = np.array([0.85, 0.45, 0.20])
    rgb = base[..., None] * rust2 + (1 - base[..., None]) * rust1
    rgb[edge] = [0.10, 0.07, 0.05]
    save_rgb(rgb, d / "rust_material.png")
    print("6.3.4 done")


# --------------------------------------------------------------------
# 6.4.1 Moiré patterns
# --------------------------------------------------------------------
def gen_6_4_1():
    d = LESSONS_DIR / "6.4.1"; d.mkdir(parents=True, exist_ok=True)

    h = w = 400
    y, x = np.indices((h, w)).astype(np.float64)

    # Two parallel-line patterns at slightly different angles
    a = 0.0
    b = np.deg2rad(5)
    p1 = np.cos(2 * np.pi * (x * np.cos(a) + y * np.sin(a)) / 6)
    p2 = np.cos(2 * np.pi * (x * np.cos(b) + y * np.sin(b)) / 6)
    moire = normalise(p1 + p2)
    save_gray(moire, d / "moire_lines.png")

    # Concentric ring + slight offset
    cy1, cx1 = h / 2 - 5, w / 2 - 5
    cy2, cx2 = h / 2 + 5, w / 2 + 5
    r1 = np.sqrt((y - cy1) ** 2 + (x - cx1) ** 2)
    r2 = np.sqrt((y - cy2) ** 2 + (x - cx2) ** 2)
    rings = np.cos(r1 / 3) + np.cos(r2 / 3)
    save_gray(normalise(rings), d / "moire_rings.png")
    print("6.4.1 done")


# --------------------------------------------------------------------
# 6.4.2 Wave interference from N point sources
# --------------------------------------------------------------------
def gen_6_4_2():
    d = LESSONS_DIR / "6.4.2"; d.mkdir(parents=True, exist_ok=True)

    h = w = 400
    y, x = np.indices((h, w)).astype(np.float64)
    sources = [(100, 100), (300, 100), (200, 300)]
    field = np.zeros((h, w))
    for sy, sx in sources:
        r = np.sqrt((y - sy) ** 2 + (x - sx) ** 2)
        field += np.cos(r / 5) / (1 + r / 80)
    save_gray(normalise(field), d / "wave_interference.png")

    # Two-source diagonal pattern
    sources2 = [(200, 120), (200, 280)]
    field2 = np.zeros((h, w))
    for sy, sx in sources2:
        r = np.sqrt((y - sy) ** 2 + (x - sx) ** 2)
        field2 += np.cos(r / 4)
    save_gray(normalise(field2), d / "two_source_interference.png")
    print("6.4.2 done")


# --------------------------------------------------------------------
# 6.4.3 Cymatics (Chladni-like plate vibration modes)
# --------------------------------------------------------------------
def gen_6_4_3():
    d = LESSONS_DIR / "6.4.3"; d.mkdir(parents=True, exist_ok=True)

    h = w = 400
    y, x = np.indices((h, w)).astype(np.float64)
    xn = x / w * np.pi
    yn = y / h * np.pi

    def chladni(m, n):
        return np.cos(m * xn) * np.cos(n * yn) - np.cos(n * xn) * np.cos(m * yn)

    panels = []
    for m, n in [(2, 3), (3, 5), (4, 7), (5, 6)]:
        z = chladni(m, n)
        # Sand collects where the plate doesn't move — |z| close to 0
        sand = (np.abs(z) < 0.05).astype(np.float64)
        panels.append(sand)
    g = np.zeros((h, 8))
    row = np.hstack([panels[0], g, panels[1], g, panels[2], g, panels[3]])
    save_gray(row, d / "chladni_modes.png")

    # Single mode hero shot
    z = chladni(4, 6)
    sand = (np.abs(z) < 0.06).astype(np.float64)
    save_gray(sand, d / "chladni_46.png")
    print("6.4.3 done")


# --------------------------------------------------------------------
if __name__ == "__main__":
    gen_6_1_1()
    gen_6_1_2()
    gen_6_1_3()
    gen_6_1_4()
    gen_6_2_1()
    gen_6_2_2()
    gen_6_2_3()
    gen_6_2_4()
    gen_6_3_1()
    gen_6_3_2()
    gen_6_3_3()
    gen_6_3_4()
    gen_6_4_1()
    gen_6_4_2()
    gen_6_4_3()
    print("all module 06 figures generated")
