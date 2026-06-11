"""
audio_reactivity.py — synthesize a fake audio waveform (no PyAudio
required), compute its short-time FFT spectrum per frame, and render an
animated audio-reactive visualization. Demonstrates the
audio -> FFT -> bins -> visual pipeline without hardware.

Pixels2GenAI Project
"""

import math
import numpy as np
from PIL import Image, ImageDraw


SIZE = (640, 360)
N_FRAMES = 90
FPS = 30
SAMPLE_RATE = 22050
WINDOW_SIZE = 1024
N_BINS = 32


def synth_audio(duration_s, sr=SAMPLE_RATE):
    """Two-bar synthetic loop: kick + hat + sustained pad."""
    t = np.arange(int(duration_s * sr)) / sr
    audio = np.zeros_like(t)

    # Kick on each beat (4 per second of loop)
    beat_period = duration_s / 4
    for k in range(4):
        beat_t = k * beat_period
        env = np.exp(-(t - beat_t) ** 2 / 0.002) * (t >= beat_t)
        audio += env * 0.8 * np.sin(2 * np.pi * 60 * (t - beat_t))

    # Hi-hat: short bursts in between beats
    for k in range(8):
        hat_t = k * beat_period / 2 + beat_period / 4
        env = np.exp(-((t - hat_t) / 0.015) ** 2) * (t >= hat_t)
        rng = np.random.default_rng(k)
        audio += env * 0.3 * rng.standard_normal(len(t))

    # Sustained pad: low E note (~165 Hz)
    audio += 0.15 * np.sin(2 * np.pi * 165 * t) * np.linspace(0.5, 1.0, len(t))

    # Normalise
    return audio / np.max(np.abs(audio))


def spectrum(window, n_bins=N_BINS):
    """Magnitude spectrum compressed to n_bins (log-spaced)."""
    fft = np.abs(np.fft.rfft(window * np.hanning(len(window))))
    # Log-spaced bin edges from 20 Hz to Nyquist
    n = len(fft)
    log_edges = np.logspace(np.log10(1), np.log10(n - 1), n_bins + 1).astype(int)
    bins = np.array([fft[log_edges[i]:log_edges[i + 1] + 1].mean()
                     for i in range(n_bins)])
    # Normalise + smoothing
    bins = bins / (bins.max() + 1e-9)
    return bins


def render_frame(bins, prev_bins, size=SIZE):
    """Render one visualization frame from the bin amplitudes."""
    img = Image.new('RGB', size, (12, 14, 22))
    draw = ImageDraw.Draw(img)
    w, h = size

    # Smooth with previous bins (exponential smoothing)
    if prev_bins is not None:
        bins = 0.6 * bins + 0.4 * prev_bins

    # Horizontal bar visualizer
    n = len(bins)
    bar_w = (w - 60) // n
    max_h = h - 80
    for i, amp in enumerate(bins):
        bh = int(amp * max_h)
        x0 = 30 + i * bar_w + 1
        y0 = h - 30 - bh
        # Colour: VU-meter green→yellow→red
        if amp < 0.5:
            color = (int(80 + amp * 250), 220, int(80))
        elif amp < 0.8:
            color = (255, int(240 - (amp - 0.5) * 400), 60)
        else:
            color = (255, int(80), 60)
        draw.rectangle([x0, y0, x0 + bar_w - 2, h - 30], fill=color)

    # Pulse circle in the centre — driven by average amplitude
    centre_x, centre_y = w // 2, h // 2 - 40
    pulse = bins.mean()
    radius = int(20 + pulse * 50)
    draw.ellipse(
        [centre_x - radius, centre_y - radius,
         centre_x + radius, centre_y + radius],
        outline=(220, 220, 240), width=2,
    )

    # Inner filled disc for accent
    inner_r = max(4, int(radius * 0.5))
    draw.ellipse(
        [centre_x - inner_r, centre_y - inner_r,
         centre_x + inner_r, centre_y + inner_r],
        fill=(255, 200, 120),
    )
    return img, bins


# Generate audio + render frames
duration = N_FRAMES / FPS
audio = synth_audio(duration)
hop = len(audio) // N_FRAMES

frames = []
prev_bins = None
for i in range(N_FRAMES):
    start = i * hop
    end = start + WINDOW_SIZE
    window = audio[start:end] if end <= len(audio) else np.pad(
        audio[start:], (0, end - len(audio)))
    bins = spectrum(window)
    img, prev_bins = render_frame(bins, prev_bins)
    frames.append(img)

# Save the GIF
frames[0].save(
    'audio_viz.gif',
    save_all=True,
    append_images=frames[1:],
    duration=int(1000 / FPS),
    loop=0,
    optimize=True,
)
frames[N_FRAMES // 2].save('audio_viz.png')

# Also render a still snapshot of the spectrum at a beat moment
beat_window = audio[hop * 5:hop * 5 + WINDOW_SIZE]
beat_bins = spectrum(beat_window)
strip_img, _ = render_frame(beat_bins, None)
strip_img.save('spectrum_snapshot.png')

print(f"Saved audio_viz.gif and audio_viz.png — {N_FRAMES} frames at {FPS} fps")
