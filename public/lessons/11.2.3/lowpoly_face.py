import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from scipy.spatial import Delaunay
import os
import urllib.request
import tempfile
import shutil

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Download the face landmarker model if not present
model_path_src = os.path.join(script_dir, "face_landmarker.task")
if not os.path.exists(model_path_src):
    print("Downloading MediaPipe Face Landmarker model...")
    model_url = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
    urllib.request.urlretrieve(model_url, model_path_src)
    print("Model downloaded successfully!")

# Copy to temp dir (MediaPipe cannot handle Unicode in paths)
model_path = shutil.copy2(model_path_src, tempfile.mkdtemp())

# Import MediaPipe
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

def detect_face_landmarks(image_rgb, model_path):
    """
    Detect facial landmarks using MediaPipe Face Landmarker.

    Parameters:
        image_rgb: RGB image as numpy array
        model_path: Path to the face_landmarker.task model file

    Returns:
        List of (x, y) tuples for each landmark, or None if no face detected
    """
    # Create MediaPipe Image
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)

    # Configure and create detector
    base_options = python.BaseOptions(model_asset_path=model_path)
    options = vision.FaceLandmarkerOptions(
        base_options=base_options,
        num_faces=1
    )
    detector = vision.FaceLandmarker.create_from_options(options)

    # Detect landmarks
    result = detector.detect(mp_image)
    detector.close()

    if not result.face_landmarks:
        return None

    # Extract landmark coordinates as pixel positions
    height, width = image_rgb.shape[:2]
    landmarks = []
    for lm in result.face_landmarks[0]:
        x = lm.x * width
        y = lm.y * height
        landmarks.append((x, y))

    return landmarks

def create_lowpoly_face(image_rgb, landmarks, add_boundary=True):
    """
    Create a low-poly rendering of a face using Delaunay triangulation.

    Parameters:
        image_rgb: Original RGB image for color sampling
        landmarks: List of (x, y) landmark coordinates
        add_boundary: If True, add corner points for full coverage

    Returns:
        triangles: List of triangle vertex arrays
        colors: List of RGB colors for each triangle
        triangulation: The scipy Delaunay triangulation object
    """
    height, width = image_rgb.shape[:2]

    # Convert landmarks to numpy array
    points = np.array(landmarks)

    # Optionally add boundary points for better coverage
    if add_boundary:
        # Add corner points
        corners = np.array([
            [0, 0],
            [width, 0],
            [width, height],
            [0, height]
        ])
        # Add edge midpoints for smoother boundary
        edges = np.array([
            [width/2, 0],
            [width, height/2],
            [width/2, height],
            [0, height/2]
        ])
        points = np.vstack([points, corners, edges])

    # Compute Delaunay triangulation
    # This connects all points into non-overlapping triangles
    triangulation = Delaunay(points)

    # Build colored triangles
    triangles = []
    colors = []

    for simplex in triangulation.simplices:
        # Get the three vertices of this triangle
        triangle = points[simplex]
        triangles.append(triangle)

        # Calculate centroid for color sampling
        centroid = np.mean(triangle, axis=0)
        cx = int(np.clip(centroid[0], 0, width - 1))
        cy = int(np.clip(centroid[1], 0, height - 1))

        # Sample color from original image at centroid
        # Note: image is [row, col] = [y, x]
        color = image_rgb[cy, cx] / 255.0
        colors.append(color)

    return triangles, colors, triangulation

def render_lowpoly(triangles, colors, width, height, show_edges=False):
    """
    Render the low-poly triangles using matplotlib.

    Parameters:
        triangles: List of triangle vertex arrays
        colors: List of RGB colors for each triangle
        width, height: Image dimensions
        show_edges: If True, draw triangle edges

    Returns:
        Rendered figure
    """
    fig, ax = plt.subplots(figsize=(10, 10))

    # Create polygon collection for efficient rendering
    edge_color = 'white' if show_edges else 'none'
    line_width = 0.5 if show_edges else 0

    collection = PolyCollection(
        triangles,
        facecolors=colors,
        edgecolors=edge_color,
        linewidths=line_width
    )

    ax.add_collection(collection)
    ax.set_xlim(0, width)
    ax.set_ylim(height, 0)  # Flip Y-axis to match image coordinates
    ax.set_aspect('equal')
    ax.axis('off')

    return fig

# Main execution
if __name__ == '__main__':
    # Load the sample face image
    image_path = os.path.join(script_dir, "sample_face.jpg")
    image_bgr = cv2.imread(image_path)

    if image_bgr is None:
        print(f"Error: Could not load image from {image_path}")
        exit(1)

    # Convert BGR to RGB
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    height, width = image_rgb.shape[:2]

    print(f"Image size: {width} x {height}")
    print("Detecting facial landmarks...")

    # Detect landmarks
    landmarks = detect_face_landmarks(image_rgb, model_path)

    if landmarks is None:
        print("No face detected! Please use an image with a visible face.")
        exit(1)

    print(f"Detected {len(landmarks)} facial landmarks")

    # Create low-poly version
    print("Creating low-poly triangulation...")
    triangles, colors, triangulation = create_lowpoly_face(
        image_rgb, landmarks, add_boundary=True
    )

    print(f"Created {len(triangles)} triangles")

    # Render and save the low-poly result
    print("Rendering low-poly face art...")
    fig = render_lowpoly(triangles, colors, width, height, show_edges=False)

    output_path = os.path.join(script_dir, "lowpoly_face_output.png")
    fig.savefig(output_path, dpi=150, bbox_inches='tight', pad_inches=0)
    plt.close(fig)
    print(f"Low-poly image saved to: {output_path}")

    # Create comparison grid (original vs low-poly)
    print("Creating comparison grid...")
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))

    # Original image
    axes[0].imshow(image_rgb)
    axes[0].set_title('Original Image', fontsize=16, fontweight='bold')
    axes[0].axis('off')

    # Low-poly version
    collection = PolyCollection(
        triangles,
        facecolors=colors,
        edgecolors='none'
    )
    axes[1].add_collection(collection)
    axes[1].set_xlim(0, width)
    axes[1].set_ylim(height, 0)
    axes[1].set_aspect('equal')
    axes[1].set_title('Low-Poly Face Art', fontsize=16, fontweight='bold')
    axes[1].axis('off')

    plt.tight_layout()
    comparison_path = os.path.join(script_dir, "comparison_grid.png")
    fig.savefig(comparison_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"Comparison grid saved to: {comparison_path}")

    # Also create a version with edges for artistic effect
    fig = render_lowpoly(triangles, colors, width, height, show_edges=True)
    edges_path = os.path.join(script_dir, "lowpoly_face_edges.png")
    fig.savefig(edges_path, dpi=150, bbox_inches='tight', pad_inches=0)
    plt.close(fig)
    print(f"Low-poly with edges saved to: {edges_path}")

    print("\nDone! Check the generated images.")
