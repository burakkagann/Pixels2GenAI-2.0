import numpy as np
from PIL import Image

class MyRNN:
    """
    A simple Recurrent Neural Network for color sequence generation.

    Fill in the TODO sections to complete the implementation.
    """

    def __init__(self, hidden_size=16):
        np.random.seed(42)
        self.hidden_size = hidden_size

        # TODO: Initialize weight matrices
        # W_xh: transforms input (3) to hidden (hidden_size)
        # W_hh: transforms previous hidden to current hidden
        # W_hy: transforms hidden to output (3)
        self.W_xh = None  # Replace with: np.random.randn(3, hidden_size) * 0.3
        self.W_hh = None  # Replace with: np.eye(hidden_size) * 0.5 + np.random.randn(hidden_size, hidden_size) * 0.1
        self.W_hy = None  # Replace with: np.random.randn(hidden_size, 3) * 0.4

        # Biases (already done for you)
        self.b_h = np.zeros(hidden_size)
        self.b_y = np.array([0.5, 0.5, 0.5])  # Center around mid-gray

    def forward_step(self, x, h_prev):
        """
        Perform one step of the RNN forward pass.

        This function takes the current input and previous hidden state,
        and computes the new hidden state and output.

        Parameters:
            x (np.ndarray): Current input color, shape (3,)
            h_prev (np.ndarray): Previous hidden state, shape (hidden_size,)

        Returns:
            y (np.ndarray): Output color, shape (3,)
            h_new (np.ndarray): New hidden state, shape (hidden_size,)
        """
        # TODO: Compute new hidden state using the RNN formula:
        # h_new = tanh(W_xh * x + W_hh * h_prev + b_h)
        #
        # Hints:
        # - Use np.dot(x, self.W_xh) for matrix multiplication
        # - Use np.tanh() for the activation function
        h_new = None  # Replace this line

        # TODO: Compute output from hidden state:
        # y = W_hy * h_new + b_y
        # Then clip to valid color range [0, 1]
        #
        # Hints:
        # - Use np.dot(h_new, self.W_hy) for matrix multiplication
        # - Use np.clip(y, 0.0, 1.0) to keep colors valid
        y = None  # Replace this line

        return y, h_new

    def generate_sequence(self, seed_color, length=20):
        """
        Generate a sequence of colors starting from a seed color.

        The RNN generates colors autoregressively: each output becomes
        the input for the next step.

        Parameters:
            seed_color (list or np.ndarray): Starting color, e.g., [1.0, 0.2, 0.2]
            length (int): Number of colors to generate

        Returns:
            colors (np.ndarray): Array of generated colors, shape (length, 3)
        """
        # TODO: Initialize hidden state to zeros (no prior memory)
        # Shape should be (hidden_size,)
        h = None  # Replace this line

        # Start with the seed color in our list
        colors = [np.array(seed_color)]
        current = seed_color

        for _ in range(length - 1):
            # TODO: Generate next color and update hidden state
            # Call self.forward_step(current, h) to get next_color and new h
            pass  # Replace this line

            # TODO: Append next_color to colors list
            pass  # Replace this line

            # TODO: Update current for next iteration
            pass  # Replace this line

        return np.array(colors)

def visualize_sequence(colors, filename='my_rnn_output.png'):
    """
    Create a visualization of the color sequence.

    Parameters:
        colors (np.ndarray): Array of colors, shape (n_colors, 3)
        filename (str): Output filename
    """
    width, height = 500, 100
    n_colors = len(colors)
    stripe_width = width // n_colors

    img = np.zeros((height, width, 3), dtype=np.uint8)

    for i, color in enumerate(colors):
        x_start = i * stripe_width
        x_end = (i + 1) * stripe_width if i < n_colors - 1 else width
        rgb = (np.array(color) * 255).astype(np.uint8)
        img[:, x_start:x_end] = rgb

    Image.fromarray(img).save(filename)
    print(f"Saved visualization to: {filename}")

# =============================================================================
# Test Your Implementation
# =============================================================================

if __name__ == '__main__':
    # Create your RNN
    rnn = MyRNN(hidden_size=16)

    # Generate a sequence starting from a reddish color
    seed_color = [0.8, 0.2, 0.3]
    sequence = rnn.generate_sequence(seed_color, length=25)

    # Check if implementation is complete
    if sequence is None or len(sequence) == 0:
        print("ERROR: generate_sequence returned None or empty list")
        print("Make sure to complete all TODO sections!")
    else:
        print(f"Successfully generated {len(sequence)} colors!")
        print("\nFirst 5 colors:")
        for i, color in enumerate(sequence[:5]):
            if color is not None:
                print(f"  Step {i}: RGB({color[0]:.2f}, {color[1]:.2f}, {color[2]:.2f})")
            else:
                print(f"  Step {i}: None - TODO not completed")

        # Try to visualize
        try:
            visualize_sequence(sequence, 'my_rnn_output.png')
        except Exception as e:
            print(f"\nVisualization failed: {e}")
            print("Make sure all TODO sections are completed correctly.")
