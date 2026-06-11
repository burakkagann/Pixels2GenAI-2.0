"""
arduino_serial.py — emulate an Arduino sensor stream (potentiometer +
photoresistor + ultrasonic distance) without hardware. Renders a small
"oscilloscope-style" dashboard of the three sensor traces over time.

Pixels2GenAI Project
"""

import math
import numpy as np
from PIL import Image, ImageDraw


SIZE = (720, 360)
N_FRAMES = 90
FPS = 30
TRACE_LEN = 90


def synth_sensor_packet(idx, n=N_FRAMES):
    """Pretend we're reading a serial line: 'pot:512 lux:80 dist:130\\n'."""
    t = idx / n
    # Potentiometer: 0-1023 (10-bit ADC), simulated as a slow sweep
    pot = int(512 + 400 * math.sin(2 * math.pi * t))
    # Photoresistor: 0-1023, falls when "covered" (every 30 frames)
    base = 750 + int(40 * math.sin(2 * math.pi * t * 2))
    covered = (idx % 30 < 8)
    lux = int(base * (0.2 if covered else 1.0))
    # Ultrasonic ranger (HC-SR04): 2-400 cm
    dist = int(100 + 80 * math.sin(2 * math.pi * t * 3 + 1))
    return f"pot:{pot} lux:{lux} dist:{dist}"


def parse(line):
    parts = line.strip().split()
    return {p.split(':')[0]: int(p.split(':')[1]) for p in parts}


def render(traces, current_packet, size=SIZE):
    img = Image.new('RGB', size, (18, 22, 32))
    draw = ImageDraw.Draw(img)
    w, h = size

    # Title
    draw.text((20, 12), 'Arduino sensor stream (synthetic)',
              fill=(220, 220, 240))
    # Latest packet on the right
    draw.text((360, 12), current_packet, fill=(140, 240, 180))

    panel_h = (h - 80) // 3
    panel_top = 60
    panel_padding = 20
    plot_left = 60
    plot_right = w - 20

    labels = [
        ('pot', 'Pot 0..1023', 1023, (255, 180, 90)),
        ('lux', 'Lux 0..1023', 1023, (110, 220, 255)),
        ('dist', 'Dist 0..200 cm', 200, (200, 120, 240)),
    ]

    for row, (key, label, vmax, color) in enumerate(labels):
        y_top = panel_top + row * panel_h
        y_bot = y_top + panel_h - panel_padding
        # Frame
        draw.rectangle([plot_left - 10, y_top, plot_right + 10, y_bot],
                       outline=(60, 70, 90))
        # Label
        draw.text((20, y_top + 4), label, fill=color)

        if not traces[key]:
            continue
        # Plot trace
        data = traces[key][-TRACE_LEN:]
        n = len(data)
        x_step = (plot_right - plot_left) / max(n - 1, 1)
        pts = [
            (plot_left + i * x_step,
             y_bot - (v / vmax) * (y_bot - y_top))
            for i, v in enumerate(data)
        ]
        draw.line(pts, fill=color, width=2)
        # Current value label at the right
        last_y = pts[-1][1]
        draw.text((plot_right + 14, last_y - 8),
                  f'{data[-1]}', fill=color)
    return img


traces = {'pot': [], 'lux': [], 'dist': []}
frames = []
for f in range(N_FRAMES):
    packet = synth_sensor_packet(f)
    data = parse(packet)
    for key, val in data.items():
        traces.setdefault(key, []).append(val)
    img = render(traces, packet)
    frames.append(img)

frames[0].save(
    'arduino_dashboard.gif',
    save_all=True,
    append_images=frames[1:],
    duration=int(1000 / FPS),
    loop=0,
    optimize=True,
)
frames[N_FRAMES * 2 // 3].save('arduino_dashboard.png')
print(f"Saved arduino_dashboard.gif — {N_FRAMES} frames")
