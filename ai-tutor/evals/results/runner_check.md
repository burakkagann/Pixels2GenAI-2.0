# Runner check (in-browser Python, Milestone 1b)

Date: 2026-09-24. Pyodide 314.0.7 in headless Chromium, through public/runner/python-worker.mjs.

## UI test

- Run buttons on 3.2.1 (Module 3): 2
- After clicking Run: "Ran in 1.4 s in your browser.", 1 output image(s) shown
- Run buttons on 4.1.1 (Module 4, out of scope): 0
- **Result: passed** (screenshot: runner_ui_3.2.1.png)

## Script check

- Complete scripts (not starters/templates): **120 of 124 ran successfully (97%)**
- Starter/template files (expected to stop at their TODOs): 28, of which 20 ran anyway
- Run time of successful scripts: median 0.1 s, slowest 80.0 s

| Module | Complete scripts | Ran | Share |
|---|---|---|---|
| Module_01 | 15 | 14 | 93% |
| Module_02 | 38 | 38 | 100% |
| Module_03 | 44 | 44 | 100% |
| Module_04 | 14 | 13 | 93% |
| Module_05 | 5 | 3 | 60% |
| Module_06 | 1 | 1 | 100% |
| Module_08 | 7 | 7 | 100% |

### Slowest successful scripts

| Script | Run time |
|---|---|
| `Module_08_animation_time/8.4_generative_animation/8.4.3_animated_fractals/animated_fractal.py` | 80.0 s |
| `Module_05_simulation_emergent_behavior/5.3_physics_simulations/5.3.3_double_pendulum_chaos/double_pendulum.py` | 51.5 s |
| `Module_08_animation_time/8.3_cinematic_effects/8.3.2_thank_you/thank_you.py` | 10.4 s |
| `Module_08_animation_time/8.2_organic_motion/8.2.2_infinite_blossom/infinite_blossom.py` | 7.7 s |
| `Module_05_simulation_emergent_behavior/5.1_particle_systems/5.1.1_sand/sand_simulation.py` | 7.2 s |

### Failures (complete scripts)

| Script | Error (last line) |
|---|---|
| `Module_01_pixel_fundamentals/1.1_grayscale_color_basics/1.1.1_color_basics/rgb_additive_mixing_diagram.py` | FileNotFoundError: [Errno 44] No such file or directory: '../../../../../images/rgb_additive_mixing.png' |
| `Module_04_fractals_recursion/4.1_classical_fractals/4.1.3_mandelbrot/mandelbrot.py` | ImportError: cannot import name 'imshow' from 'scipy.misc' (/lib/python3.14/site-packages/scipy/misc/__init__.py) |
| `Module_05_simulation_emergent_behavior/5.1_particle_systems/5.1.1_sand/sand.py` | cv2.error: OpenCV(4.11.0) /home/runner/work/pyodide-recipes/pyodide-recipes/packages/opencv-python/build/opencv-python-4.11.0.86/opencv/modules/highgui/src/window.cpp:1301: error: (-2:Unspecified erro |
| `Module_05_simulation_emergent_behavior/5.2_flocking_swarms/5.2.1_boids/boids.py` | ValueError: need at least one array to stack |
