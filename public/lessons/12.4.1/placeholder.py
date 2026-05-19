# =============================================================================
# IMPLEMENTATION SPECIFICATIONS
# =============================================================================

"""
KEY CONCEPTS TO IMPLEMENT:

1. VGG-19 Feature Extraction
   - Load pretrained VGG-19 (torchvision.models.vgg19)
   - Extract features from specific layers:
     - Content: conv4_2 (or conv5_2)
     - Style: conv1_1, conv2_1, conv3_1, conv4_1, conv5_1

2. Gram Matrix Computation
   def gram_matrix(features):
       # features shape: (batch, channels, height, width)
       b, c, h, w = features.size()
       features = features.view(b * c, h * w)
       gram = torch.mm(features, features.t())
       return gram / (c * h * w)  # Normalize

3. Loss Functions
   - Content Loss: MSE between feature maps
   - Style Loss: MSE between Gram matrices (weighted across layers)
   - Total Variation Loss: Smoothness regularization (optional)
   - Total Loss: alpha * content_loss + beta * style_loss + gamma * tv_loss

4. Optimization Loop
   - Initialize with content image (or noise)
   - Use L-BFGS or Adam optimizer
   - Iterate 200-1000 steps
   - Save intermediate results for animation

SUGGESTED STRUCTURE:
- simple_nst.py: Minimal working example
- nst_solution.py: Full implementation with visualization
- nst_starter.py: Template for students to complete
- fast_nst.py: Feed-forward approach (advanced)
"""

# =============================================================================
# EXPECTED OUTPUTS
# =============================================================================

"""
OUTPUT FILES TO GENERATE:

1. style_transfer_output.png
   - Main result: content image stylized

2. optimization_progress.gif
   - Animation showing iterations (every 50 steps)

3. gram_matrix_visualization.png
   - Heatmap of Gram matrix for style image

4. content_style_comparison.png
   - 3-panel: Content | Style | Output

5. layer_activations.png (optional)
   - Visualization of VGG layer activations
"""

# =============================================================================
# RESOURCES
# =============================================================================

"""
TUTORIALS:
- TensorFlow: https://www.tensorflow.org/tutorials/generative/style_transfer
- PyTorch: https://pytorch.org/tutorials/advanced/neural_style_tutorial.html
- V7 Labs: https://www.v7labs.com/blog/neural-style-transfer

PAPERS:
- Gatys et al. 2016: https://arxiv.org/abs/1508.06576
- Johnson et al. 2016 (Fast NST): https://arxiv.org/abs/1603.08155
- Huang & Belongie 2017 (AdaIN): https://arxiv.org/abs/1703.06868

GITHUB:
- https://github.com/jcjohnson/neural-style
- https://github.com/jcjohnson/fast-neural-style
- https://github.com/deepeshdm/Neural-Style-Transfer
"""

# =============================================================================
# DEPENDENCIES
# =============================================================================

DEPENDENCIES = [
    "torch",
    "torchvision",
    "PIL",
    "numpy",
    "matplotlib",
    "imageio",  # For GIF generation
]

# =============================================================================
# CONNECTION TO MODULE 12
# =============================================================================

"""
PEDAGOGICAL CONNECTIONS:

- FROM DCGAN (12.1.2):
  NST uses VGG-19 for feature extraction, similar to how discriminators
  learn hierarchical feature representations.

- FROM StyleGAN (12.1.3):
  StyleGAN separates style at different resolutions via AdaIN.
  NST separates content vs style through different layer statistics.
  Both demonstrate that neural networks encode style and content separately.

- TO VQ-VAE (12.3.2):
  NST shows continuous feature representations.
  VQ-VAE will introduce discrete representations via codebook.

- TO DIFFUSION (12.4):
  Optimization-based NST is similar to diffusion's iterative refinement,
  but NST optimizes pixels while diffusion denoises.
"""

if __name__ == "__main__":
    print("This is a placeholder file for Neural Style Transfer exercise.")
    print("Content will be generated based on the specifications above.")
    print()
    print("Key files to create:")
    print("  - simple_nst.py")
    print("  - nst_solution.py")
    print("  - nst_starter.py")
    print("  - README.rst (replace this placeholder)")
