"""
ant_colony.py - Ant Colony Optimisation visualisation for the Travelling
Salesman Problem. Each iteration, simulated ants build a tour by choosing
the next city probabilistically based on (pheromone^alpha)*(visibility^beta).
After the tours are built, pheromones evaporate and the best tour gets a
deposit boost. Over time the colony converges on a short tour.

Pixels2GenAI Project
"""

import numpy as np
from PIL import Image, ImageDraw
import imageio.v2 as imageio

# ---------- CONFIG ----------
WIDTH, HEIGHT = 480, 480
NUM_CITIES = 20
NUM_ANTS = 25
NUM_ITERS = 80
ALPHA = 1.0           # pheromone weight
BETA = 4.0            # visibility weight (1/distance)
EVAPORATION = 0.12    # pheromone evaporation per iter
Q = 100.0             # pheromone deposit constant

BG = (8, 12, 24)
CITY_COLOUR = (255, 220, 90)
EDGE_COLOUR = (90, 160, 240)
BEST_COLOUR = (250, 110, 120)
FPS = 12
# ----------------------------


def initial_setup(seed=42):
    rng = np.random.default_rng(seed)
    cities = rng.uniform(40, WIDTH - 40, size=(NUM_CITIES, 2))
    distances = np.linalg.norm(cities[:, None] - cities[None, :], axis=-1) + 1e-6
    pheromone = np.ones_like(distances)
    return cities, distances, pheromone


def build_tour(distances, pheromone, rng):
    n = distances.shape[0]
    start = rng.integers(0, n)
    visited = [start]
    while len(visited) < n:
        current = visited[-1]
        mask = np.ones(n, dtype=bool)
        mask[visited] = False
        probs = (pheromone[current] ** ALPHA) * ((1.0 / distances[current]) ** BETA)
        probs[~mask] = 0
        total = probs.sum()
        if total <= 0:
            choice = rng.choice(np.where(mask)[0])
        else:
            choice = rng.choice(n, p=probs / total)
        visited.append(int(choice))
    return visited


def tour_length(tour, distances):
    return sum(distances[tour[i], tour[(i + 1) % len(tour)]]
               for i in range(len(tour)))


def render(cities, pheromone, best_tour, iter_idx, best_len):
    img = Image.new('RGB', (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(img)

    max_p = pheromone.max()
    n = len(cities)
    for i in range(n):
        for j in range(i + 1, n):
            strength = pheromone[i, j] / max_p
            if strength < 0.05:
                continue
            alpha = int(40 + 215 * strength**1.4)
            colour = tuple(int(EDGE_COLOUR[k] * strength) for k in range(3))
            draw.line([tuple(cities[i]), tuple(cities[j])], fill=colour, width=1)

    if best_tour is not None:
        for k in range(n):
            a, b = best_tour[k], best_tour[(k + 1) % n]
            draw.line([tuple(cities[a]), tuple(cities[b])],
                      fill=BEST_COLOUR, width=2)

    for x, y in cities:
        draw.ellipse([x - 4, y - 4, x + 4, y + 4], fill=CITY_COLOUR)

    draw.text((10, 10), f'iter {iter_idx:>3}', fill=(220, 220, 220))
    if best_len:
        draw.text((10, 28), f'best {best_len:.1f}', fill=(220, 220, 220))
    return np.array(img)


def main():
    rng = np.random.default_rng(0)
    cities, distances, pheromone = initial_setup()

    best_tour = None
    best_len = np.inf
    frames = []

    for iter_idx in range(NUM_ITERS):
        tours = [build_tour(distances, pheromone, rng) for _ in range(NUM_ANTS)]
        lengths = [tour_length(t, distances) for t in tours]

        pheromone *= (1 - EVAPORATION)
        for t, length in zip(tours, lengths):
            deposit = Q / length
            for k in range(NUM_CITIES):
                a, b = t[k], t[(k + 1) % NUM_CITIES]
                pheromone[a, b] += deposit
                pheromone[b, a] += deposit

        iter_best = int(np.argmin(lengths))
        if lengths[iter_best] < best_len:
            best_len = lengths[iter_best]
            best_tour = tours[iter_best]

        frames.append(render(cities, pheromone, best_tour, iter_idx, best_len))

    imageio.mimsave('ant_colony.gif', frames, fps=FPS)
    Image.fromarray(frames[-1]).save('ant_colony_final.png')
    print(f'best tour length: {best_len:.2f}')


if __name__ == '__main__':
    main()
