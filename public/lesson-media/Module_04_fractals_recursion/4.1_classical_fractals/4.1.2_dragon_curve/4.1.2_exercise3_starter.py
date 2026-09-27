def invert_sequence(sequence):
    """Swap all L's and R's."""
    # TODO 1: return a string with every L replaced by R and every R by L
    pass

def generate_dragon_sequence(initial_turn, depth):
    """Build the dragon curve sequence recursively."""
    if depth == 0:
        # TODO 2: return the base case
        pass
    # TODO 3: get the previous depth's sequence (recursive call)
    previous = None
    # TODO 4: build the second half — reverse, then invert
    second_half = None
    # TODO 5: combine: previous + 'R' (the new fold) + second_half
    return None

# Self-test
test = generate_dragon_sequence('R', 3)
assert test == 'RRLRRLLRRRLLRLL', f"Got {test!r}"
print("All good — depth 3 sequence matches the expected dragon string.")
