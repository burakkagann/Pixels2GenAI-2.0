"""
ant_starter.py - Exercise 3 scaffold. The main loop and rendering are
wired up. You implement `build_tour()` - the per-ant probabilistic city
selection.

Pixels2GenAI Project
"""

import numpy as np
from PIL import Image, ImageDraw
import imageio.v2 as imageio

WIDTH, HEIGHT = 480, 480
NUM_CITIES = 18
NUM_ANTS = 20
NUM_ITERS = 60
ALPHA = 1.0
BETA = 4.0
EVAPORATION = 0.12
Q = 100.0
FPS = 12


def build_tour(distances, pheromone, rng):
    """TODO: build one ant's tour through the cities.

    Algorithm:
      1. Start at a random city.
      2. While not all cities visited:
         - mask = boolean array of unvisited cities.
         - compute scores[c] = pheromone[current,c]^ALPHA * (1/distances[current,c])^BETA
         - zero out scores for visited cities.
         - sample next city with probability proportional to scores.
      3. Return the list of city indices in visit order.
    """
    return [0]  # replace me


def tour_length(tour, distances):
    return sum(distances[tour[i], tour[(i + 1) % len(tour)]]
               for i in range(len(tour)))


def main():
    rng = np.random.default_rng(0)
    cities = rng.uniform(40, WIDTH - 40, size=(NUM_CITIES, 2))
    distances = np.linalg.norm(cities[:, None] - cities[None, :], axis=-1) + 1e-6
    pheromone = np.ones_like(distances)

    best_tour, best_len = None, float('inf')
    frames = []

    for iter_idx in range(NUM_ITERS):
        tours = [build_tour(distances, pheromone, rng) for _ in range(NUM_ANTS)]
        lengths = [tour_length(t, distances) for t in tours]
        pheromone *= (1 - EVAPORATION)
        for t, L in zip(tours, lengths):
            deposit = Q / L
            for k in range(NUM_CITIES):
                a, b = t[k], t[(k + 1) % NUM_CITIES]
                pheromone[a, b] += deposit
                pheromone[b, a] += deposit
        idx = int(np.argmin(lengths))
        if lengths[idx] < best_len:
            best_len, best_tour = lengths[idx], tours[idx]

        img = Image.new('RGB', (WIDTH, HEIGHT), (8, 12, 24))
        d = ImageDraw.Draw(img)
        if best_tour:
            for k in range(NUM_CITIES):
                a, b = best_tour[k], best_tour[(k + 1) % NUM_CITIES]
                d.line([tuple(cities[a]), tuple(cities[b])],
                       fill=(250, 110, 120), width=2)
        for (x, y) in cities:
            d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=(255, 220, 90))
        frames.append(np.array(img))

    imageio.mimsave('ant_starter.gif', frames, fps=FPS)
    print(f'best length: {best_len:.2f}')


if __name__ == '__main__':
    main()
