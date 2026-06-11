"""
walk_cycle.py — procedural stick-figure walk: arms and legs swing in
opposition, body bobs slightly on each step, rendered as both a 6-frame
sprite-sheet strip and as an animated GIF.

Pixels2GenAI Project
"""

import math
import numpy as np
from PIL import Image, ImageDraw


CELL = 140
N_FRAMES = 8
ARM_SWING_RAD = 0.7      # radians peak swing
LEG_SWING_RAD = 0.55
LIMB_LEN = 35
BODY = (220, 230, 245)
ACCENT = (110, 200, 255)


def joint(x, y, length, angle_rad):
    """Polar endpoint at angle from vertical (0 = down)."""
    return int(x + length * math.sin(angle_rad)), int(y + length * math.cos(angle_rad))


def render_pose(frame_idx, n=N_FRAMES, color=BODY, accent=ACCENT):
    img = Image.new('RGBA', (CELL, CELL), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    t = frame_idx / n      # phase in [0, 1)
    phase = 2 * math.pi * t

    cx = CELL // 2
    body_top = 30
    body_bot = 80
    head_r = 12

    # Vertical bob: 2 steps per cycle, so cos(2*phase) is the bob rhythm
    bob = int(2 * (1 - math.cos(2 * phase))) - 2

    # Head + body
    draw.ellipse(
        [cx - head_r, body_top - head_r + bob,
         cx + head_r, body_top + head_r + bob],
        fill=color, outline=accent, width=2,
    )
    draw.line(
        [(cx, body_top + head_r + bob), (cx, body_bot + bob)],
        fill=color, width=4,
    )

    hip_y = body_bot + bob

    # Arms: shoulder at body top + small offset
    shoulder_y = body_top + head_r + 8 + bob
    arm_phase = phase
    arm_angle_r = math.sin(arm_phase) * ARM_SWING_RAD
    arm_angle_l = -arm_angle_r
    # Right arm
    arx, ary = joint(cx, shoulder_y, LIMB_LEN, math.pi + arm_angle_r)
    draw.line([(cx, shoulder_y), (arx, ary)], fill=color, width=4)
    # Left arm
    alx, aly = joint(cx, shoulder_y, LIMB_LEN, math.pi + arm_angle_l)
    draw.line([(cx, shoulder_y), (alx, aly)], fill=color, width=4)

    # Legs: opposite phase from arms
    leg_angle_r = math.sin(phase + math.pi) * LEG_SWING_RAD
    leg_angle_l = -leg_angle_r
    # Right leg
    lrx, lry = joint(cx, hip_y, LIMB_LEN, math.pi + leg_angle_r)
    draw.line([(cx, hip_y), (lrx, lry)], fill=accent, width=4)
    # Left leg
    llx, lly = joint(cx, hip_y, LIMB_LEN, math.pi + leg_angle_l)
    draw.line([(cx, hip_y), (llx, lly)], fill=accent, width=4)

    # Ground line
    draw.line([(8, CELL - 8), (CELL - 8, CELL - 8)], fill=(80, 95, 120), width=1)
    return img


# Sprite-sheet strip
sheet = Image.new('RGBA', (CELL * N_FRAMES, CELL), (18, 20, 30, 255))
for i in range(N_FRAMES):
    pose = render_pose(i)
    sheet.paste(pose, (i * CELL, 0), pose)
draw = ImageDraw.Draw(sheet)
for i in range(1, N_FRAMES):
    draw.line([(i * CELL, 0), (i * CELL, CELL)], fill=(60, 65, 85))
sheet.save('walk_cycle_sheet.png')

# Animated GIF — repeat the cycle twice for a clear loop
frames = []
for cycle in range(2):
    for i in range(N_FRAMES):
        pose = render_pose(i)
        bg = Image.new('RGB', (CELL, CELL), (18, 20, 30))
        bg.paste(pose, (0, 0), pose)
        frames.append(bg)

frames[0].save(
    'walk_cycle.gif',
    save_all=True,
    append_images=frames[1:],
    duration=120,
    loop=0,
    optimize=True,
)
print(f"Saved walk_cycle_sheet.png ({N_FRAMES} cells) and walk_cycle.gif")
