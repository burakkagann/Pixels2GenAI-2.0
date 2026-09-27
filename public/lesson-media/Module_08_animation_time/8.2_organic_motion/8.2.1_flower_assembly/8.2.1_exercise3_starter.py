# inside the frame loop, after computing progress and offsets:
for i, ((cy, cx), (dy, dx)) in enumerate(zip(home_yx, offsets)):
    y, x = cy + dy, cx + dx
    if not (0 <= y <= H - th and 0 <= x <= W - tw):
        continue

    tile_arr = flower[cy:cy+th, cx:cx+tw]
    tile_img = Image.fromarray(tile_arr)

    # TODO 1: pick a per-tile random start_rotation (e.g., uniform in [-180, 180])
    #         (store these outside the frame loop, computed once)

    # TODO 2: current rotation = start_rotation * (1 - progress)

    # TODO 3: rotate the tile and paste into the canvas (canvas is now a PIL image)
