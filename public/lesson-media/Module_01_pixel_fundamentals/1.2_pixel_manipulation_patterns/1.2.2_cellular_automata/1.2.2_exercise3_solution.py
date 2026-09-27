# TODO 1 — beacon
grid[5:7, 5:7] = [[1, 1], [1, 0]]    # top-left block (provided)
grid[7:9, 7:9] = [[0, 1], [1, 1]]    # bottom-right block

# TODO 2 — glider
grid[20:23, 10:13] = [[0, 1, 0], [0, 0, 1], [1, 1, 1]]

# TODO 3 — evolution
for generation in range(20):
    grid = game_of_life_step(grid)
    print(f"Generation {generation + 1}: {np.sum(grid)} living cells")
