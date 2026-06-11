"""
multi_machine.py — render a topology diagram showing a single
controller broadcasting sync messages to N render machines, with
animated packet flow along each link.

Pixels2GenAI Project
"""

import math
import numpy as np
from PIL import Image, ImageDraw


SIZE = (720, 480)
N_FRAMES = 60
FPS = 20
N_RENDER = 4


def render_frame(idx, n=N_FRAMES):
    img = Image.new('RGB', SIZE, (16, 18, 28))
    draw = ImageDraw.Draw(img)
    w, h = SIZE

    # Title
    draw.text((20, 14), 'Multi-machine sync — 1 controller + 4 renderers',
              fill=(220, 220, 240))

    # Controller node (top)
    cx, cy = w // 2, 90
    draw.rectangle([cx - 70, cy - 28, cx + 70, cy + 28],
                   fill=(50, 80, 130), outline=(120, 180, 240), width=2)
    draw.text((cx - 50, cy - 9), 'Controller', fill=(220, 240, 255))

    # Render machine nodes (along the bottom)
    render_y = 360
    render_xs = [
        int(w * (i + 1) / (N_RENDER + 1)) for i in range(N_RENDER)
    ]
    for i, rx in enumerate(render_xs):
        draw.rectangle([rx - 56, render_y - 26, rx + 56, render_y + 26],
                       fill=(60, 90, 60), outline=(140, 240, 140), width=2)
        draw.text((rx - 42, render_y - 8), f'Renderer {i + 1}',
                  fill=(220, 255, 220))

        # Link from controller to renderer
        draw.line([(cx, cy + 28), (rx, render_y - 26)],
                  fill=(70, 80, 110), width=2)

    # Animated packets flowing down each link
    t = (idx % 15) / 15
    for rx in render_xs:
        # Packet position along the link
        px = int(cx + (rx - cx) * t)
        py = int((cy + 28) + (render_y - 26 - (cy + 28)) * t)
        draw.ellipse([px - 7, py - 7, px + 7, py + 7],
                     fill=(255, 220, 110), outline=(50, 50, 30))
        draw.text((px + 10, py - 6), 'sync', fill=(255, 220, 110))

    # Show one renderer's screen
    panel_x, panel_y = 20, 130
    panel_w, panel_h = 200, 160
    draw.rectangle([panel_x, panel_y, panel_x + panel_w, panel_y + panel_h],
                   fill=(10, 12, 22), outline=(80, 100, 140))
    # Rotating disc as the synchronised content
    cx_p = panel_x + panel_w // 2
    cy_p = panel_y + panel_h // 2
    for k in range(6):
        ang = idx * 0.2 + k * math.pi / 3
        ex = cx_p + int(math.cos(ang) * 40)
        ey = cy_p + int(math.sin(ang) * 40)
        draw.line([(cx_p, cy_p), (ex, ey)], fill=(255, 180, 100), width=2)
    draw.ellipse([cx_p - 6, cy_p - 6, cx_p + 6, cy_p + 6], fill=(255, 240, 180))
    draw.text((panel_x + 4, panel_y + 4),
              'Each renderer shows the same frame', fill=(160, 180, 220))

    # Show network stats panel
    stats_x = w - 220
    draw.rectangle([stats_x, panel_y, stats_x + 200, panel_y + panel_h],
                   fill=(10, 12, 22), outline=(80, 100, 140))
    draw.text((stats_x + 8, panel_y + 8), 'Network', fill=(220, 220, 240))
    draw.text((stats_x + 8, panel_y + 30), 'Frame: ' + str(idx),
              fill=(180, 200, 220))
    draw.text((stats_x + 8, panel_y + 50), 'Sent: ' + str(idx * N_RENDER),
              fill=(180, 200, 220))
    draw.text((stats_x + 8, panel_y + 70),
              f'Skew: {int(t * 8)} ms', fill=(180, 200, 220))
    draw.text((stats_x + 8, panel_y + 90), 'Proto: UDP', fill=(180, 200, 220))

    return img


frames = [render_frame(f) for f in range(N_FRAMES)]
frames[0].save(
    'multi_machine.gif',
    save_all=True,
    append_images=frames[1:],
    duration=int(1000 / FPS),
    loop=0,
    optimize=True,
)
frames[N_FRAMES // 2].save('multi_machine.png')
print(f"Saved multi_machine.gif — {N_FRAMES} frames at {FPS} fps")
