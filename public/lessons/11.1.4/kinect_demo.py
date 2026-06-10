"""
kinect_demo.py — simulate a Kinect depth-sensor frame with a 320x240
synthetic depth map (the user's torso + raised arms) plus a stick-figure
skeleton overlay. Demonstrates the (depth, skeleton) data products of
modern body-tracking sensors without requiring hardware.

Pixels2GenAI Project
"""

import math
import numpy as np
from PIL import Image, ImageDraw


SIZE = (320, 240)
N_FRAMES = 90


def synth_depth(frame, size=SIZE):
    """Return a synthetic depth map (HxW uint8) where higher = closer."""
    w, h = size
    depth = np.full((h, w), 30, dtype=np.uint8)   # far wall
    t = frame / (N_FRAMES - 1)

    # Body torso position bobs slightly
    cx = w // 2
    cy = h // 2 + int(4 * math.sin(2 * math.pi * t))

    # Torso ellipse — closest to camera
    yy, xx = np.mgrid[:h, :w]
    torso = ((xx - cx) / 26) ** 2 + ((yy - cy) / 38) ** 2 < 1
    depth[torso] = 215

    # Head — slightly behind
    head_cy = cy - 60
    head = ((xx - cx) / 14) ** 2 + ((yy - head_cy) / 16) ** 2 < 1
    depth[head] = 195

    # Arms: rotating sinusoidally
    arm_phase = math.sin(2 * math.pi * t)
    for sign in (-1, 1):
        a = sign * (0.7 + 0.3 * arm_phase)
        for s in np.linspace(0, 1, 30):
            ax = int(cx + sign * 20 + sign * s * 60 * math.cos(a))
            ay = int(cy - 20 + s * 60 * math.sin(a))
            if 2 <= ax < w - 2 and 2 <= ay < h - 2:
                depth[ay - 3:ay + 3, ax - 3:ax + 3] = 175

    return depth, cx, cy, arm_phase


def skeleton_from_phase(cx, cy, arm_phase):
    """Return joint positions corresponding to the synthetic body pose."""
    head = (cx, cy - 60)
    neck = (cx, cy - 32)
    torso = (cx, cy)
    pelvis = (cx, cy + 25)
    left_arm = (cx - int(20 + 60 * math.cos(0.7 + 0.3 * arm_phase)),
                cy - 20 + int(60 * math.sin(0.7 + 0.3 * arm_phase)))
    right_arm = (cx + int(20 + 60 * math.cos(0.7 + 0.3 * arm_phase)),
                 cy - 20 + int(60 * math.sin(0.7 + 0.3 * arm_phase)))
    left_foot = (cx - 18, cy + 75)
    right_foot = (cx + 18, cy + 75)
    return {
        'head': head, 'neck': neck, 'torso': torso, 'pelvis': pelvis,
        'left_hand': left_arm, 'right_hand': right_arm,
        'left_foot': left_foot, 'right_foot': right_foot,
    }


def render_frame(frame_idx, scale=2):
    depth, cx, cy, arm_phase = synth_depth(frame_idx)

    # Map depth to a viridis-like cool→warm palette
    h, w = depth.shape
    img = np.zeros((h, w, 3), dtype=np.uint8)
    norm = depth.astype(np.float32) / 255
    img[..., 0] = (30 + 220 * norm).clip(0, 255).astype(np.uint8)
    img[..., 1] = (70 + 100 * norm).clip(0, 255).astype(np.uint8)
    img[..., 2] = (120 + 60 * (1 - norm)).clip(0, 255).astype(np.uint8)

    pil = Image.fromarray(img).resize((w * scale, h * scale), Image.NEAREST)

    # Draw skeleton on top
    draw = ImageDraw.Draw(pil)
    skel = skeleton_from_phase(cx, cy, arm_phase)
    bones = [
        ('head', 'neck'), ('neck', 'torso'), ('torso', 'pelvis'),
        ('neck', 'left_hand'), ('neck', 'right_hand'),
        ('pelvis', 'left_foot'), ('pelvis', 'right_foot'),
    ]
    for a, b in bones:
        x1, y1 = skel[a][0] * scale, skel[a][1] * scale
        x2, y2 = skel[b][0] * scale, skel[b][1] * scale
        draw.line([(x1, y1), (x2, y2)], fill=(255, 255, 110), width=3)
    for j in skel.values():
        x, y = j[0] * scale, j[1] * scale
        draw.ellipse([x - 5, y - 5, x + 5, y + 5],
                     fill=(255, 230, 110), outline=(80, 60, 20))

    return pil


frames = [render_frame(f) for f in range(N_FRAMES)]
frames[0].save(
    'kinect_skeleton.gif',
    save_all=True,
    append_images=frames[1:],
    duration=80,
    loop=0,
    optimize=True,
)
frames[N_FRAMES // 2].save('kinect_skeleton.png')
print(f"Saved kinect_skeleton.gif and kinect_skeleton.png — {N_FRAMES} frames")
