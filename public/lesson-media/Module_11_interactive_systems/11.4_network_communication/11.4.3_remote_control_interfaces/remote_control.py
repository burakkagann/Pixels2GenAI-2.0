"""
remote_control.py — render a "mobile-phone remote" mockup: a phone-shaped
panel showing a touchable UI (slider, knob, RGB picker, big button) on the
left, a generative-art preview window driven by those controls on the
right, and animated WebSocket packets flowing between them.

Pixels2GenAI Project
"""

import math
import numpy as np
from PIL import Image, ImageDraw


SIZE = (720, 480)
N_FRAMES = 80
FPS = 20


def render_frame(idx, n=N_FRAMES):
    img = Image.new('RGB', SIZE, (16, 18, 28))
    draw = ImageDraw.Draw(img)
    w, h = SIZE
    t = idx / n

    draw.text((20, 14), 'Remote control surface — phone UI → WebSocket → visualization',
              fill=(220, 220, 240))

    # Phone (left)
    phone_w, phone_h = 220, 360
    phone_x = 30
    phone_y = 70
    draw.rounded_rectangle([phone_x, phone_y, phone_x + phone_w, phone_y + phone_h],
                           radius=22, fill=(28, 30, 40), outline=(160, 170, 200), width=2)
    # Phone screen
    sx, sy = phone_x + 14, phone_y + 36
    sw, sh = phone_w - 28, phone_h - 64
    draw.rounded_rectangle([sx, sy, sx + sw, sy + sh],
                           radius=10, fill=(40, 44, 60))

    # Animated controls (driven by time)
    slider_y = sy + 30
    knob_y = sy + 130
    color_y = sy + 220

    # Slider — large rectangle with sliding knob
    sl_x0 = sx + 16
    sl_x1 = sx + sw - 16
    draw.rectangle([sl_x0, slider_y + 16, sl_x1, slider_y + 18], fill=(80, 90, 110))
    sl_v = 0.5 + 0.4 * math.sin(2 * math.pi * t * 1.4)
    knob_x = int(sl_x0 + (sl_x1 - sl_x0) * sl_v)
    draw.ellipse([knob_x - 12, slider_y, knob_x + 12, slider_y + 32],
                 fill=(120, 200, 255), outline=(40, 60, 90))
    draw.text((sl_x0, slider_y - 18),
              f'Speed: {sl_v:.2f}', fill=(220, 230, 255))

    # Knob (rotary)
    knob_cx = sx + sw // 2
    knob_cy = knob_y + 40
    kn_v = 0.5 + 0.5 * math.sin(2 * math.pi * t * 2 + 1)
    draw.ellipse([knob_cx - 32, knob_cy - 32, knob_cx + 32, knob_cy + 32],
                 outline=(160, 170, 200), width=2)
    ang = -135 + 270 * kn_v
    rad = math.radians(ang)
    ex = knob_cx + 26 * math.sin(rad)
    ey = knob_cy - 26 * math.cos(rad)
    draw.line([(knob_cx, knob_cy), (ex, ey)], fill=(255, 180, 90), width=4)
    draw.text((sl_x0, knob_y - 12),
              f'Density: {int(kn_v * 100)}', fill=(220, 230, 255))

    # RGB colour picker (3 vertical sliders)
    rgb = (
        int(127 + 110 * math.sin(2 * math.pi * t * 1.3)),
        int(127 + 110 * math.sin(2 * math.pi * t * 1.5 + 1)),
        int(127 + 110 * math.sin(2 * math.pi * t * 1.7 + 2)),
    )
    draw.rectangle([sx + 16, color_y, sx + sw - 16, color_y + 30],
                   fill=rgb, outline=(80, 90, 110))
    draw.text((sl_x0, color_y - 12),
              f'Hue: RGB({rgb[0]},{rgb[1]},{rgb[2]})',
              fill=(220, 230, 255))

    # Big button at bottom
    btn_y = color_y + 60
    is_pressed = (idx % 32) > 24
    btn_color = (90, 220, 120) if is_pressed else (50, 130, 80)
    draw.rounded_rectangle([sx + 30, btn_y, sx + sw - 30, btn_y + 50],
                           radius=14, fill=btn_color, outline=(20, 40, 30), width=2)
    draw.text((sx + sw // 2 - 30, btn_y + 16), 'TRIGGER',
              fill=(20, 30, 20))

    # WebSocket link visualization
    link_y = phone_y + phone_h // 2
    preview_x = w - 250
    draw.line([(phone_x + phone_w + 8, link_y), (preview_x - 8, link_y)],
              fill=(80, 100, 140), width=1)
    draw.line([(phone_x + phone_w + 8, link_y + 18), (preview_x - 8, link_y + 18)],
              fill=(80, 100, 140), width=1)

    # Send arrow with the current packet at a phase
    phase_r = (idx % 14) / 14
    px = int((phone_x + phone_w + 8) +
             ((preview_x - 8) - (phone_x + phone_w + 8)) * phase_r)
    draw.ellipse([px - 4, link_y - 4, px + 4, link_y + 4], fill=(110, 200, 255))
    draw.text((px - 16, link_y - 22), '{slider:0.8, btn:1}',
              fill=(110, 200, 255))

    # Preview window
    pv_w, pv_h = 220, 200
    pv_x = preview_x
    pv_y = phone_y + 40
    draw.rectangle([pv_x, pv_y, pv_x + pv_w, pv_y + pv_h],
                   fill=(10, 14, 22), outline=(80, 100, 140))
    draw.text((pv_x, pv_y - 18), 'Visualization preview',
              fill=(220, 220, 240))

    # The preview: a swirling particle field whose density depends on the knob,
    # whose colour depends on the RGB picker, whose speed depends on the slider
    n_particles = 60 + int(kn_v * 80)
    rng = np.random.default_rng(0)
    for k in range(n_particles):
        base_angle = rng.uniform(0, 2 * math.pi)
        radius = rng.uniform(8, pv_w // 2 - 10)
        angle = base_angle + idx * (0.04 + sl_v * 0.08)
        cx = pv_x + pv_w // 2 + radius * math.cos(angle)
        cy = pv_y + pv_h // 2 + radius * math.sin(angle) * 0.7
        draw.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=rgb)

    if is_pressed:
        draw.text((pv_x + pv_w // 2 - 28, pv_y + pv_h + 4),
                  'TRIGGERED', fill=(90, 220, 120))

    return img


frames = [render_frame(f) for f in range(N_FRAMES)]
frames[0].save(
    'remote_control.gif',
    save_all=True,
    append_images=frames[1:],
    duration=int(1000 / FPS),
    loop=0,
    optimize=True,
)
frames[N_FRAMES // 3].save('remote_control.png')
print(f"Saved remote_control.gif — {N_FRAMES} frames")
