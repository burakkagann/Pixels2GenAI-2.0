def invert_sequence(sequence):
    return ''.join('L' if c == 'R' else 'R' for c in sequence)

def generate_dragon_sequence(initial_turn, depth):
    if depth == 0:
        return initial_turn
    previous = generate_dragon_sequence(initial_turn, depth - 1)
    second_half = invert_sequence(previous[::-1])
    return previous + 'R' + second_half

assert generate_dragon_sequence('R', 3) == 'RRLRRLLRRRLLRLL'
