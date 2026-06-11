"""
fluid.py - A grid-based Eulerian fluid simulation. Velocity and density are
stored as two 2D arrays. Each frame: advect (move quantities along the flow),
diffuse (smooth out gradients), and project (enforce mass conservation by
removing divergence). The result is realistic ink-in-water swirl.

Pixels2GenAI Project
"""

import numpy as np
from PIL import Image
import imageio.v2 as imageio

# ---------- CONFIG ----------
GRID = 96                       # grid resolution (NxN)
SCALE = 4                       # pixel scale for rendering
NUM_FRAMES = 140
FPS = 24

DT = 0.18                       # time step
VISCOSITY = 1.0e-4              # how fast velocity gradients smooth
DIFFUSION = 1.0e-4              # how fast density gradients smooth
SOLVER_ITERS = 14               # Gauss-Seidel iterations per project step

INJECT_STRENGTH = 70.0          # ink strength per source
SWIRL_STRENGTH = 110.0          # injected velocity per source
# ----------------------------


def diffuse(field, diff, dt):
    a = dt * diff * GRID * GRID
    for _ in range(SOLVER_ITERS):
        field[1:-1, 1:-1] = (
            field[1:-1, 1:-1]
            + a * (field[2:, 1:-1] + field[:-2, 1:-1]
                   + field[1:-1, 2:] + field[1:-1, :-2])
        ) / (1 + 4 * a)
    return field


def advect(field, vx, vy, dt):
    out = np.zeros_like(field)
    dt0 = dt * GRID

    xs, ys = np.meshgrid(np.arange(GRID), np.arange(GRID), indexing='xy')
    px = xs - dt0 * vx
    py = ys - dt0 * vy
    px = np.clip(px, 0.5, GRID - 1.5)
    py = np.clip(py, 0.5, GRID - 1.5)

    i0 = px.astype(int)
    j0 = py.astype(int)
    i1 = i0 + 1
    j1 = j0 + 1
    s1 = px - i0
    s0 = 1 - s1
    t1 = py - j0
    t0 = 1 - t1

    out[ys, xs] = (
        s0 * (t0 * field[j0, i0] + t1 * field[j1, i0])
        + s1 * (t0 * field[j0, i1] + t1 * field[j1, i1])
    )
    return out


def project(vx, vy):
    div = np.zeros_like(vx)
    p = np.zeros_like(vx)
    div[1:-1, 1:-1] = -0.5 * (
        vx[1:-1, 2:] - vx[1:-1, :-2] + vy[2:, 1:-1] - vy[:-2, 1:-1]
    ) / GRID

    for _ in range(SOLVER_ITERS):
        p[1:-1, 1:-1] = (
            div[1:-1, 1:-1]
            + p[2:, 1:-1] + p[:-2, 1:-1] + p[1:-1, 2:] + p[1:-1, :-2]
        ) / 4

    vx[1:-1, 1:-1] -= 0.5 * GRID * (p[1:-1, 2:] - p[1:-1, :-2])
    vy[1:-1, 1:-1] -= 0.5 * GRID * (p[2:, 1:-1] - p[:-2, 1:-1])
    return vx, vy


def render(density, palette_offset=0):
    norm = np.clip(density / max(density.max(), 1e-3), 0, 1)
    img = np.zeros((GRID, GRID, 3), dtype=np.float32)
    img[..., 0] = 0.30 + 0.70 * norm
    img[..., 1] = 0.10 + 0.30 * norm**0.8
    img[..., 2] = 0.45 + 0.55 * (1 - norm)**1.5
    img = (img * 255).clip(0, 255).astype(np.uint8)
    # upscale via repeat
    return np.repeat(np.repeat(img, SCALE, axis=0), SCALE, axis=1)


def main():
    np.random.seed(0)
    vx = np.zeros((GRID, GRID), dtype=np.float64)
    vy = np.zeros((GRID, GRID), dtype=np.float64)
    density = np.zeros((GRID, GRID), dtype=np.float64)

    sources = [
        (GRID // 4, GRID // 2, +SWIRL_STRENGTH, -SWIRL_STRENGTH * 0.2),
        (3 * GRID // 4, GRID // 2, -SWIRL_STRENGTH, +SWIRL_STRENGTH * 0.2),
    ]

    frames = []
    for frame in range(NUM_FRAMES):
        for cx, cy, ux, uy in sources:
            density[cy - 2:cy + 3, cx - 2:cx + 3] += INJECT_STRENGTH * DT
            vx[cy - 2:cy + 3, cx - 2:cx + 3] += ux * DT
            vy[cy - 2:cy + 3, cx - 2:cx + 3] += uy * DT

        vx = diffuse(vx, VISCOSITY, DT)
        vy = diffuse(vy, VISCOSITY, DT)
        vx, vy = project(vx, vy)
        vx = advect(vx, vx, vy, DT)
        vy = advect(vy, vx, vy, DT)
        vx, vy = project(vx, vy)

        density = diffuse(density, DIFFUSION, DT)
        density = advect(density, vx, vy, DT)
        density *= 0.995    # mild fade

        frame_img = render(density)
        frames.append(frame_img)
        if frame == NUM_FRAMES // 2:
            Image.fromarray(frame_img).save('fluid_frame.png')

    imageio.mimsave('fluid.gif', frames, fps=FPS)
    Image.fromarray(frames[-1]).save('fluid_final.png')
    print(f'Wrote fluid.gif ({NUM_FRAMES} frames)')


if __name__ == '__main__':
    main()
