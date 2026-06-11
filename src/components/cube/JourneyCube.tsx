/**
 * JourneyCube — the 3D spinning Pixels→GenAI cube.
 *
 * Six CSS-transformed faces, each painted per frame by sampling a procedural
 * pattern function through a precomputed OKLCH palette LUT. Mounted as a React
 * island; the rest of the landing page stays static HTML.
 *
 * Color settings (mode/palette/per-face/journey-palette crossfade) are locked
 * to the design defaults — steady · aurora · per-face on · journey-palette on
 * — and are not exposed in the UI.
 */

import { useEffect, useMemo, useRef, useState } from 'react';
import {
  LUTS,
  LUT_MAX,
  PALETTE_ORDER,
  slowNoise,
  type ColorMode,
  type PaletteName,
} from '@/lib/cubeColor';
import { RES, STAGE_FNS, STAGES } from '@/lib/cubePatterns';
import styles from './cube.module.css';

interface MutableState {
  j: number;
  freq: number;
  centers: number;
  speed: number;
  contrast: number;
  mode: ColorMode;
  palette: PaletteName;
  cycle: number;
  bands: number;
  perFace: boolean;
  journeyPal: boolean;
  paused: boolean;
}

interface FaceCanvas {
  cv: HTMLCanvasElement;
  ctx: CanvasRenderingContext2D;
  off: HTMLCanvasElement;
  octx: CanvasRenderingContext2D;
  buf: ImageData;
  phase: number;
  seed: number;
}

const FACE_KEYS = ['front', 'right', 'back', 'left', 'top', 'bottom'] as const;
type FaceKey = (typeof FACE_KEYS)[number];

const FACE_META: Record<FaceKey, { code: string; rot: string; idx: number }> = {
  front:  { code: 'F · front · 0°',    rot: 'f-front',  idx: 1 },
  right:  { code: 'R · right · 90°',   rot: 'f-right',  idx: 2 },
  back:   { code: 'B · back · 180°',   rot: 'f-back',   idx: 3 },
  left:   { code: 'L · left · 270°',   rot: 'f-left',   idx: 4 },
  top:    { code: 'U · top · 90°',     rot: 'f-top',    idx: 5 },
  bottom: { code: 'D · bottom · -90°', rot: 'f-bottom', idx: 6 },
};

const TAU3 = (Math.PI * 2) / 3;

// Local outward normals in FACE_KEYS order, CSS coords (+x right, +y down,
// +z toward viewer). Used for back-face culling: a face is front-facing when
// its transformed normal's screen-Z is positive.
const FACE_NORMALS: ReadonlyArray<readonly [number, number, number]> = [
  [0, 0, 1],   // front
  [1, 0, 0],   // right
  [0, 0, -1],  // back
  [-1, 0, 0],  // left
  [0, -1, 0],  // top
  [0, 1, 0],   // bottom
];
// Paint a face once its normal screen-Z exceeds this. Slightly negative so a
// face is repainted just before it rotates into view → never shows a stale frame.
const CULL_THRESHOLD = -0.1;

const DEFAULTS: MutableState = {
  j: 0,
  freq: 0.32,
  centers: 3,
  speed: 1.0,
  contrast: 1.0,
  mode: 'steady',
  palette: 'riso',
  cycle: 0.46,
  bands: 0,
  perFace: true,
  journeyPal: true,
  paused: false,
};

export default function JourneyCube() {
  // ---- React state: drives only the UI display (slider numbers, active tick).
  // The RAF loop reads from `stateRef` instead so it never causes re-renders.
  const [ui, setUi] = useState({
    j: DEFAULTS.j,
    freq: DEFAULTS.freq,
    centers: DEFAULTS.centers,
    speed: DEFAULTS.speed,
    contrast: DEFAULTS.contrast,
    paused: false,
  });

  // ---- Mutable state read inside RAF.
  const stateRef = useRef<MutableState>({ ...DEFAULTS });

  // ---- Refs for the six on-screen canvases (one per face).
  const canvasRefs = useRef<Record<FaceKey, HTMLCanvasElement | null>>({
    front: null, right: null, back: null, left: null, top: null, bottom: null,
  });

  // ---- Reset / Pause button handlers.
  const cubeElRef = useRef<HTMLDivElement>(null);
  const stageElRef = useRef<HTMLDivElement>(null);

  // Repaints the faces once when the RAF loop isn't doing it — under
  // reduced motion the loop never starts, and Pause early-returns before
  // painting, so slider changes would otherwise go unseen. Assigned
  // inside the setup effect where paintAll lives.
  const paintIdleRef = useRef<() => void>(() => {});

  // Setup the off-screen buffers + RAF loop once.
  useEffect(() => {
    const faces: FaceCanvas[] = [];
    const dpr = Math.min(window.devicePixelRatio || 1, 1.6);
    const resizers: Array<() => void> = [];

    FACE_KEYS.forEach((key, i) => {
      const cv = canvasRefs.current[key];
      if (!cv) return;
      const ctx = cv.getContext('2d');
      if (!ctx) return;

      const resize = () => {
        const r = cv.getBoundingClientRect();
        cv.width = Math.max(64, Math.floor(r.width * dpr));
        cv.height = Math.max(64, Math.floor(r.height * dpr));
      };
      resize();
      resizers.push(resize);

      const off = document.createElement('canvas');
      off.width = RES;
      off.height = RES;
      const octx = off.getContext('2d');
      if (!octx) return;
      const buf = octx.createImageData(RES, RES);
      // Alpha is constant 255; set it once here and only write RGB in the loop.
      const bd = buf.data;
      for (let p = 3; p < bd.length; p += 4) bd[p] = 255;
      // Smoothing defaults to true and a canvas resize restores that default,
      // so set it once instead of every frame.
      ctx.imageSmoothingEnabled = true;

      faces.push({ cv, ctx, off, octx, buf, phase: i * Math.PI / 3, seed: i * 17.31 });
    });

    if (!faces.length) return;

    const onResize = () => resizers.forEach((r) => r());
    window.addEventListener('resize', onResize);

    let t = 0;
    let last = performance.now();
    let rafId = 0;
    let acc = 0;
    let running = false;
    const FRAME = 1 / 30; // throttle the surface paint to ~30fps (the CSS spin stays 60fps)

    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

    // Paint every face once using the current `t`. Pulled out of the RAF loop so
    // reduced-motion can render a single static frame without animating.
    const paintAll = () => {
      const state = stateRef.current;

      const jx = state.j * (STAGES.length - 1);
      const lower = Math.floor(jx);
      const upper = Math.min(STAGES.length - 1, lower + 1);
      const blend = jx - lower;
      const fnL = STAGE_FNS[lower];
      const fnU = STAGE_FNS[upper];

      const freq = state.freq;
      const C = Math.max(1, Math.floor(state.centers));
      const con = state.contrast;
      const applyCon = con !== 1; // pow(n, 1) is a no-op; skip it at the default contrast

      const mode = state.mode;
      const lutA = LUTS[state.palette];
      const idxPal = PALETTE_ORDER.indexOf(state.palette);
      // #7 — at the resting position (j=0) the crossfade collapses to a no-op
      // but still costs 3 mul-adds/pixel; skip the second LUT entirely.
      const lutB = state.journeyPal && state.j > 0
        ? LUTS[PALETTE_ORDER[(idxPal + 1) % PALETTE_ORDER.length]]
        : null;
      const jBlend = lutB ? state.j : 0;
      const cycleOffset = mode === 'cycle' ? t * state.cycle * 0.12 : 0;
      const driftAmt = mode === 'drift' ? 0.15 + state.cycle * 0.85 : 0;
      const bands = state.bands | 0;
      const useBands = bands >= 2;
      const perFaceStride = state.perFace ? 1 / faces.length : 0;

      // Back-face culling: read the cube's live animated matrix once and skip
      // faces whose normal points away from the camera. Single style read per
      // frame; the CSS spin stays GPU-composited and untouched.
      const cubeEl = cubeElRef.current;
      let cull = false;
      let mZ0 = 0, mZ1 = 0, mZ2 = 0;
      if (cubeEl) {
        const tr = getComputedStyle(cubeEl).transform;
        if (tr && tr.startsWith('matrix')) {
          const m = new DOMMatrix(tr);
          mZ0 = m.m13; mZ1 = m.m23; mZ2 = m.m33; // screen-Z row of the rotation
          cull = true;
        }
      }

      for (let fi = 0; fi < faces.length; fi++) {
        if (cull) {
          const nrm = FACE_NORMALS[fi];
          const screenZ = mZ0 * nrm[0] + mZ1 * nrm[1] + mZ2 * nrm[2];
          if (screenZ <= CULL_THRESHOLD) continue; // back-facing → keep last paint
        }
        const fc = faces[fi];
        const data = fc.buf.data;
        const ph = fc.phase;
        const faceShift = perFaceStride * fi;

        for (let y = 0; y < RES; y++) {
          for (let x = 0; x < RES; x++) {
            const nx = x / RES;
            const ny = y / RES;
            const idx = (y * RES + x) * 4;

            if (mode === 'chromatic') {
              const ar = fnL(nx, ny, t, ph,            freq, C);
              const ag = fnL(nx, ny, t, ph + TAU3,     freq, C);
              const ab = fnL(nx, ny, t, ph + TAU3 * 2, freq, C);
              let nR = (ar + 1) * 0.5;
              let nG = (ag + 1) * 0.5;
              let nB = (ab + 1) * 0.5;
              if (blend > 0) {
                const br = fnU(nx, ny, t, ph,            freq, C);
                const bg = fnU(nx, ny, t, ph + TAU3,     freq, C);
                const bb = fnU(nx, ny, t, ph + TAU3 * 2, freq, C);
                nR = nR * (1 - blend) + ((br + 1) * 0.5) * blend;
                nG = nG * (1 - blend) + ((bg + 1) * 0.5) * blend;
                nB = nB * (1 - blend) + ((bb + 1) * 0.5) * blend;
              }
              if (nR < 0) nR = 0; else if (nR > 1) nR = 1;
              if (nG < 0) nG = 0; else if (nG > 1) nG = 1;
              if (nB < 0) nB = 0; else if (nB > 1) nB = 1;
              if (applyCon) {
                nR = Math.pow(nR, con);
                nG = Math.pow(nG, con);
                nB = Math.pow(nB, con);
              }
              const iR = (nR * LUT_MAX) | 0;
              const iG = (nG * LUT_MAX) | 0;
              const iB = (nB * LUT_MAX) | 0;
              let r = lutA[iR * 3];
              let g = lutA[iG * 3 + 1];
              let b = lutA[iB * 3 + 2];
              if (lutB) {
                r = r * (1 - jBlend) + lutB[iR * 3]     * jBlend;
                g = g * (1 - jBlend) + lutB[iG * 3 + 1] * jBlend;
                b = b * (1 - jBlend) + lutB[iB * 3 + 2] * jBlend;
              }
              data[idx]     = r | 0;
              data[idx + 1] = g | 0;
              data[idx + 2] = b | 0;
              continue;
            }

            // steady / cycle / drift
            const a = fnL(nx, ny, t, ph, freq, C);
            const bV = blend > 0 ? fnU(nx, ny, t, ph, freq, C) : a;
            const v = a * (1 - blend) + bV * blend;
            let n = (v + 1) * 0.5;
            if (n < 0) n = 0; else if (n > 1) n = 1;
            if (applyCon) n = Math.pow(n, con);

            let u = n;
            if (mode === 'cycle') {
              u = n + cycleOffset;
            } else if (mode === 'drift') {
              u = n + (slowNoise(nx, ny, t) - 0.5) * driftAmt;
            }
            u += faceShift;
            u = u - Math.floor(u);
            if (useBands) u = Math.floor(u * bands) / (bands - 1 || 1);
            if (u < 0) u = 0; else if (u > 1) u = 1;

            const li = (u * LUT_MAX) | 0;
            const off = li * 3;
            let r = lutA[off];
            let g = lutA[off + 1];
            let b = lutA[off + 2];
            if (lutB) {
              r = r * (1 - jBlend) + lutB[off]     * jBlend;
              g = g * (1 - jBlend) + lutB[off + 1] * jBlend;
              b = b * (1 - jBlend) + lutB[off + 2] * jBlend;
            }
            data[idx]     = r | 0;
            data[idx + 1] = g | 0;
            data[idx + 2] = b | 0;
          }
        }

        fc.octx.putImageData(fc.buf, 0, 0);
        // Opaque source filling the whole canvas → no clearRect needed.
        fc.ctx.drawImage(fc.off, 0, 0, fc.cv.width, fc.cv.height);
      }
    };

    const frame = (now: number) => {
      rafId = requestAnimationFrame(frame);
      const state = stateRef.current;
      const dt = Math.min(0.05, (now - last) / 1000);
      last = now;
      if (state.paused) return;        // #5 — Pause freezes the surface, not just the spin
      acc += dt;
      if (acc < FRAME) return;         // #3 — throttle the paint to ~30fps
      t += acc * state.speed * 1.2;    // advance by real elapsed time → speed unchanged
      acc = 0;
      paintAll();
    };

    const start = () => {
      if (running || reduceMotion.matches) return;
      running = true;
      last = performance.now();
      acc = 0;
      rafId = requestAnimationFrame(frame);
    };

    const stop = () => {
      running = false;
      cancelAnimationFrame(rafId);
    };

    // #1 — reduced motion: paint one static frame, never start the loop.
    if (reduceMotion.matches) {
      paintAll();
    }

    paintIdleRef.current = () => {
      if (reduceMotion.matches || stateRef.current.paused) paintAll();
    };

    // #2 — only animate while the cube is on-screen.
    const io = new IntersectionObserver(
      (entries) => {
        if (entries[0]?.isIntersecting ?? true) start();
        else stop();
      },
      { threshold: 0 },
    );
    if (stageElRef.current) io.observe(stageElRef.current);

    // Live-toggle the OS reduced-motion setting without a reload.
    const onMotionChange = () => {
      if (reduceMotion.matches) {
        stop();
        t = 0;
        paintAll();
      } else {
        start();
      }
    };
    reduceMotion.addEventListener('change', onMotionChange);

    return () => {
      stop();
      io.disconnect();
      reduceMotion.removeEventListener('change', onMotionChange);
      window.removeEventListener('resize', onResize);
      paintIdleRef.current = () => {};
    };
  }, []);

  // ---- Derived UI values
  const jx = ui.j * (STAGES.length - 1);
  const lower = Math.floor(jx);
  const upper = Math.min(STAGES.length - 1, lower + 1);
  const blend = jx - lower;
  const nearest = blend < 0.5 ? lower : upper;
  const currentStage = STAGES[nearest];
  const progressPct = Math.round(ui.j * 100);

  // ---- Slider change handler — writes both UI state and mutable ref.
  const updateSlider = <K extends 'j' | 'freq' | 'centers' | 'speed' | 'contrast'>(
    key: K,
    value: number,
  ) => {
    setUi((prev) => ({ ...prev, [key]: value }));
    stateRef.current[key] = value;
    paintIdleRef.current();
  };

  const handleTickClick = (i: number) => {
    const v = i / (STAGES.length - 1);
    updateSlider('j', v);
  };

  const handlePauseToggle = () => {
    setUi((prev) => {
      const paused = !prev.paused;
      stateRef.current.paused = paused; // freeze the surface paint too, not just the CSS spin
      return { ...prev, paused };
    });
  };

  const handleReset = () => {
    setUi({
      j: DEFAULTS.j,
      freq: DEFAULTS.freq,
      centers: DEFAULTS.centers,
      speed: DEFAULTS.speed,
      contrast: DEFAULTS.contrast,
      paused: false,
    });
    stateRef.current.j = DEFAULTS.j;
    stateRef.current.freq = DEFAULTS.freq;
    stateRef.current.centers = DEFAULTS.centers;
    stateRef.current.speed = DEFAULTS.speed;
    stateRef.current.contrast = DEFAULTS.contrast;
    stateRef.current.paused = false;
    paintIdleRef.current();
  };

  // ---- Cursor parallax: tilt perspective-origin on pointer move.
  // Hover-affordance only — on touch-primary devices a scrolling finger
  // would jitter the perspective, so the listeners are never attached.
  useEffect(() => {
    const stage = stageElRef.current;
    if (!stage) return;
    if (!window.matchMedia('(hover: hover) and (pointer: fine)').matches) return;
    const onMove = (e: PointerEvent) => {
      const r = stage.getBoundingClientRect();
      const tx = ((e.clientX - r.left) / r.width - 0.5) * 20;
      const ty = -((e.clientY - r.top) / r.height - 0.5) * 20;
      stage.style.perspectiveOrigin = `${50 + tx * 0.6}% ${45 + ty * 0.6}%`;
    };
    const onLeave = () => {
      stage.style.perspectiveOrigin = '50% 45%';
    };
    stage.addEventListener('pointermove', onMove);
    stage.addEventListener('pointerleave', onLeave);
    return () => {
      stage.removeEventListener('pointermove', onMove);
      stage.removeEventListener('pointerleave', onLeave);
    };
  }, []);

  const faceMetaEntries = useMemo(() => Object.entries(FACE_META) as Array<[FaceKey, typeof FACE_META[FaceKey]]>, []);

  return (
    <>
      <div ref={stageElRef} className={styles['cube-stage']} id="cubeStage">
        <div
          ref={cubeElRef}
          className={`${styles.cube}${ui.paused ? ' ' + styles.paused : ''}`}
          id="cube"
        >
          {faceMetaEntries.map(([key, meta]) => (
            <div key={key} className={`${styles.face} ${styles[meta.rot]}`}>
              <span className={`${styles.corner} ${styles.tl}`}></span>
              <span className={`${styles.corner} ${styles.tr}`}></span>
              <span className={`${styles.corner} ${styles.bl}`}></span>
              <span className={`${styles.corner} ${styles.br}`}></span>
              <canvas
                ref={(el) => {
                  canvasRefs.current[key] = el;
                }}
                data-face={key}
              />
              <div className={styles['lbl-top']}>{meta.code}</div>
              <div className={styles['lbl-bot']}>
                <span className={styles.ttl}>{currentStage.code} · {currentStage.name}</span>
                <span className={styles.n}>f {meta.idx} / 6</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div
        className={styles['cube-controls']}
        style={{ '--journey-accent': `var(--${currentStage.cycle})` } as React.CSSProperties}
      >
        <div className={styles['ctrl-head']}>
          <b>Pixels → GenAI</b>
          <span className={styles.live}><span className={styles.d}></span>{progressPct}%</span>
        </div>

        <div className={styles.journey}>
          <div className={styles['journey-endpoints']}>
            <span className={styles['ep-l']}>PIXELS · M 01</span>
            <span className={styles['ep-r']}>GENAI · M 12</span>
          </div>
          <div className={styles['journey-track']}>
            <input
              type="range"
              className={styles['journey-slider']}
              min="0"
              max="1"
              step="0.001"
              value={ui.j}
              onChange={(e) => updateSlider('j', parseFloat(e.target.value))}
              aria-label="Journey position"
            />
          </div>
          <div className={styles['journey-ticks']}>
            {STAGES.map((s, i) => {
              const cls = [
                styles.tick,
                i === nearest ? styles.active : '',
                i === lower || i === upper ? styles.near : '',
              ].filter(Boolean).join(' ');
              return (
                <button
                  key={s.code}
                  type="button"
                  className={cls}
                  onClick={() => handleTickClick(i)}
                  aria-label={`Jump to ${s.name}`}
                >
                  <b>{s.code}</b><span className={styles.tname}>{s.name}</span>
                </button>
              );
            })}
          </div>
        </div>

        <div className={styles.sliders}>
          <div className={styles.sl}>
            <label>frequency <span className={styles.v}>{ui.freq.toFixed(3)}</span>
              <input
                type="range" min="0.05" max="0.9" step="0.005"
                value={ui.freq}
                onChange={(e) => updateSlider('freq', parseFloat(e.target.value))}
                aria-label="Frequency"
              />
            </label>
          </div>
          <div className={styles.sl}>
            <label>complexity <span className={styles.v}>{ui.centers.toFixed(0)}</span>
              <input
                type="range" min="1" max="6" step="1"
                value={ui.centers}
                onChange={(e) => updateSlider('centers', parseInt(e.target.value, 10))}
                aria-label="Complexity"
              />
            </label>
          </div>
          <div className={styles.sl}>
            <label>speed <span className={styles.v}>{ui.speed.toFixed(2)}</span>
              <input
                type="range" min="0" max="3" step="0.05"
                value={ui.speed}
                onChange={(e) => updateSlider('speed', parseFloat(e.target.value))}
                aria-label="Speed"
              />
            </label>
          </div>
          <div className={styles.sl}>
            <label>contrast <span className={styles.v}>{ui.contrast.toFixed(2)}</span>
              <input
                type="range" min="0.4" max="2.4" step="0.05"
                value={ui.contrast}
                onChange={(e) => updateSlider('contrast', parseFloat(e.target.value))}
                aria-label="Contrast"
              />
            </label>
          </div>
        </div>

        <div className={styles['ctrl-foot']}>
          <span className={styles.note}>Drag the master slider to traverse the curriculum.</span>
          <span className={styles['btn-row']}>
            <button type="button" onClick={handlePauseToggle}>{ui.paused ? 'Resume' : 'Pause'}</button>
            <button type="button" onClick={handleReset}>Reset</button>
          </span>
        </div>
      </div>
    </>
  );
}
