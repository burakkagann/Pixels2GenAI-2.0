"""
websocket_demo.py — render a side-by-side comparison of three browser
realtime protocols: HTTP polling, WebSocket, and WebRTC. Animates the
data-flow pattern of each (request/response, persistent push, P2P media
stream) so the protocol semantics are visually obvious.

Pixels2GenAI Project
"""

import math
import numpy as np
from PIL import Image, ImageDraw


SIZE = (720, 540)
N_FRAMES = 80
FPS = 20


def render_frame(idx, n=N_FRAMES):
    img = Image.new('RGB', SIZE, (16, 18, 28))
    draw = ImageDraw.Draw(img)
    w, h = SIZE

    draw.text((20, 14),
              'Browser realtime protocols — HTTP poll vs WebSocket vs WebRTC',
              fill=(220, 220, 240))

    # Three rows; each row shows a client on the left and a server on the right
    row_h = (h - 80) // 3
    row_top = 50
    client_x = 100
    server_x = w - 120
    node_r = 26

    cycle = idx / n
    t_in_row = (idx % 16) / 16

    rows = [
        ('HTTP polling',
         '↺ poll every 1 s', (220, 130, 80)),
        ('WebSocket',
         'persistent duplex', (110, 200, 255)),
        ('WebRTC',
         'P2P media stream', (180, 130, 240)),
    ]

    for r, (name, sub, color) in enumerate(rows):
        cy = row_top + r * row_h + row_h // 2

        # Client node
        draw.ellipse([client_x - node_r, cy - node_r,
                      client_x + node_r, cy + node_r],
                     fill=(50, 60, 80), outline=color, width=2)
        draw.text((client_x - 22, cy - 8), 'Client', fill=color)

        # Server node
        draw.ellipse([server_x - node_r, cy - node_r,
                      server_x + node_r, cy + node_r],
                     fill=(50, 60, 80), outline=color, width=2)
        draw.text((server_x - 22, cy - 8), 'Server', fill=color)

        # Protocol label
        draw.text((20, cy - 24), name, fill=color)
        draw.text((20, cy + 6), sub, fill=(180, 190, 210))

        # Animate packets per row
        link_left = client_x + node_r
        link_right = server_x - node_r

        if r == 0:
            # HTTP polling: large request/response packets every 16 frames
            phase = (idx % 32) / 32
            if phase < 0.4:
                # Request going right
                px = int(link_left + (link_right - link_left) * (phase / 0.4))
                draw.rectangle([px - 12, cy - 10, px + 12, cy + 10],
                               fill=color, outline=(40, 40, 60))
                draw.text((px - 10, cy - 8), 'GET', fill=(20, 20, 30))
            elif phase < 0.5:
                pass    # gap
            elif phase < 0.9:
                # Response going left
                p2 = (phase - 0.5) / 0.4
                px = int(link_right - (link_right - link_left) * p2)
                draw.rectangle([px - 14, cy - 12, px + 14, cy + 12],
                               fill=color, outline=(40, 40, 60))
                draw.text((px - 12, cy - 8), '200', fill=(20, 20, 30))
        elif r == 1:
            # WebSocket: continuous small bidirectional packets
            # Right-going packet
            phase_r = (idx % 24) / 24
            px = int(link_left + (link_right - link_left) * phase_r)
            draw.ellipse([px - 6, cy - 12, px + 6, cy - 4], fill=color)
            # Left-going packet
            phase_l = ((idx + 12) % 24) / 24
            px2 = int(link_right - (link_right - link_left) * phase_l)
            draw.ellipse([px2 - 6, cy + 4, px2 + 6, cy + 12], fill=color)
            # Persistent link line
            draw.line([(link_left, cy), (link_right, cy)],
                      fill=(80, 100, 140), width=1)
        else:
            # WebRTC: dense packet stream with no server pull (the server is
            # the signalling channel, but media flows P2P)
            draw.line([(link_left, cy - 16), (link_right, cy - 16)],
                      fill=(80, 100, 140), width=1)
            draw.line([(link_left, cy + 16), (link_right, cy + 16)],
                      fill=(80, 100, 140), width=1)
            # Five small packets in flight
            for k in range(5):
                phase_k = ((idx + k * 4) % 16) / 16
                px = int(link_left + (link_right - link_left) * phase_k)
                draw.ellipse([px - 4, cy - 20, px + 4, cy - 12], fill=color)
                draw.ellipse([px - 4, cy + 12, px + 4, cy + 20], fill=color)
            draw.text((server_x - 30, cy + 32),
                      '(signalling only)', fill=(160, 180, 220))

    return img


frames = [render_frame(f) for f in range(N_FRAMES)]
frames[0].save(
    'websocket_compare.gif',
    save_all=True,
    append_images=frames[1:],
    duration=int(1000 / FPS),
    loop=0,
    optimize=True,
)
frames[N_FRAMES // 2].save('websocket_compare.png')
print(f"Saved websocket_compare.gif — {N_FRAMES} frames")
