"""
midi_osc.py — simulate a MIDI/OSC control stream by generating fake
events and rendering them as a piano roll + parameter knob dashboard.
Output: an animated GIF showing notes lighting up + knobs sweeping.

Pixels2GenAI Project
"""

import math
import numpy as np
from PIL import Image, ImageDraw


SIZE = (720, 360)
N_FRAMES = 90
FPS = 30


def synth_events(n_frames=N_FRAMES, n_notes=8, n_knobs=4, seed=21):
    """Generate per-frame {note_id: velocity} and {knob_id: value}."""
    rng = np.random.default_rng(seed)
    notes_per_frame = []
    knobs_per_frame = []
    knob_state = rng.uniform(0.2, 0.6, n_knobs)
    knob_target = knob_state.copy()
    active = np.zeros(n_notes, dtype=np.int32)
    velocity = np.zeros(n_notes, dtype=np.float32)

    for f in range(n_frames):
        # Scheduled MIDI note-ons: 16th-note pattern across the 8 notes
        if f % 4 == 0:
            note_id = (f // 4) % n_notes
            active[note_id] = 8       # frames the note stays "on"
            velocity[note_id] = rng.uniform(0.5, 1.0)
        if f % 12 == 0:
            note_id = ((f // 12) * 3) % n_notes
            active[note_id] = 12
            velocity[note_id] = rng.uniform(0.7, 1.0)

        # Decay active notes
        velocity *= 0.92
        active = np.maximum(active - 1, 0)
        velocity[active <= 0] = 0
        notes_per_frame.append(velocity.copy())

        # Knobs: drift toward random targets
        if f % 30 == 0:
            knob_target = rng.uniform(0.1, 0.9, n_knobs)
        knob_state = knob_state * 0.9 + knob_target * 0.1
        knobs_per_frame.append(knob_state.copy())

    return notes_per_frame, knobs_per_frame


def render_frame(notes, knobs, size=SIZE):
    img = Image.new('RGB', size, (16, 18, 28))
    draw = ImageDraw.Draw(img)
    w, h = size

    # Left half: piano-roll of notes
    n_notes = len(notes)
    key_w = (w // 2 - 40) // n_notes
    key_h = h - 80
    for i, v in enumerate(notes):
        x0 = 20 + i * key_w
        y0 = 40
        # Background "key"
        draw.rectangle([x0, y0, x0 + key_w - 4, y0 + key_h],
                       fill=(38, 42, 56), outline=(60, 70, 90))
        # Active bar from bottom up
        if v > 0:
            bar_h = int(v * (key_h - 10))
            y_top = y0 + key_h - bar_h
            # Colour by velocity
            r = int(120 + 135 * v)
            g = int(200 - 100 * v)
            b = int(240 - 80 * v)
            draw.rectangle([x0 + 4, y_top, x0 + key_w - 8, y0 + key_h - 4],
                           fill=(r, g, b))
        # Label
        draw.text((x0 + 4, h - 36), f'N{i}', fill=(160, 170, 200))

    draw.text((20, 14), 'MIDI notes', fill=(220, 225, 240))

    # Right half: knob dashboard
    n_knobs = len(knobs)
    knob_x0 = w // 2 + 30
    knob_y_centre = h // 2 - 10
    knob_radius = 36
    knob_spacing = (w // 2 - 60) // n_knobs

    draw.text((knob_x0, 14), 'CC knobs', fill=(220, 225, 240))
    for i, v in enumerate(knobs):
        cx = knob_x0 + i * knob_spacing + knob_spacing // 2
        cy = knob_y_centre
        # Outer ring
        draw.ellipse([cx - knob_radius, cy - knob_radius,
                      cx + knob_radius, cy + knob_radius],
                     outline=(160, 170, 200), width=2)
        # Knob indicator: rotation from -135deg to +135deg by value
        angle = -135 + 270 * v
        rad = math.radians(angle)
        end_x = cx + (knob_radius - 8) * math.sin(rad)
        end_y = cy - (knob_radius - 8) * math.cos(rad)
        draw.line([(cx, cy), (end_x, end_y)], fill=(110, 200, 255), width=4)
        # Value label
        draw.text((cx - 18, cy + knob_radius + 8),
                  f'CC{i}: {int(v * 127):3d}', fill=(220, 225, 240))

    return img


notes_seq, knobs_seq = synth_events()
frames = [render_frame(notes_seq[i], knobs_seq[i]) for i in range(N_FRAMES)]

frames[0].save(
    'midi_dashboard.gif',
    save_all=True,
    append_images=frames[1:],
    duration=int(1000 / FPS),
    loop=0,
    optimize=True,
)
frames[N_FRAMES // 2].save('midi_dashboard.png')
print(f"Saved midi_dashboard.gif — {N_FRAMES} frames")
