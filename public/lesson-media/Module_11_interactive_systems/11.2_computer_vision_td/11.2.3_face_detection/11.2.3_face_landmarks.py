import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch, Circle, Ellipse, Polygon
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
    """Detect facial landmarks using MediaPipe."""
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)

    base_options = python.BaseOptions(model_asset_path=model_path)
    options = vision.FaceLandmarkerOptions(
        base_options=base_options,
        num_faces=1
    )
    detector = vision.FaceLandmarker.create_from_options(options)
    result = detector.detect(mp_image)
    detector.close()

    if not result.face_landmarks:
        return None

    height, width = image_rgb.shape[:2]
    landmarks = []
    for lm in result.face_landmarks[0]:
        x = lm.x * width
        y = lm.y * height
        landmarks.append((x, y))

    return landmarks

def get_landmark_region(idx):
    """
    Return the facial region name and color for a landmark index.

    MediaPipe Face Mesh has 478 landmarks organized into regions.
    The exact indices are based on the MediaPipe face mesh topology.
    """
    # Define regions with colors (approximate index ranges)
    if idx >= 468:  # Irises
        return "Irises", "#00FFFF"  # Cyan
    elif idx in [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288,
                 397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136,
                 172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109]:
        return "Face Oval", "#00FF00"  # Green
    elif idx in range(33, 134) or idx in range(263, 364):
        return "Eyes", "#FF8000"  # Orange
    elif idx in range(17, 33) or idx in range(133, 168) or idx in range(168, 198):
        return "Eyebrows", "#0000FF"  # Blue
    elif idx in range(1, 17) or idx in range(195, 263):
        return "Nose", "#FFFF00"  # Yellow
    elif idx in [61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 409, 270,
                 269, 267, 0, 37, 39, 40, 185, 78, 191, 80, 81, 82, 13, 312,
                 311, 310, 415, 308, 324, 318, 402, 317, 14, 87, 178, 88, 95]:
        return "Lips", "#FF0000"  # Red
    else:
        return "Face Surface", "#808080"  # Gray

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

    print("Detecting facial landmarks...")
    landmarks = detect_face_landmarks(image_rgb, model_path)

    if landmarks is None:
        print("No face detected!")
        exit(1)

    print(f"Detected {len(landmarks)} landmarks")

    # Create visualization
    fig, axes = plt.subplots(1, 2, figsize=(16, 8))

    # Left: Original image with landmarks
    axes[0].imshow(image_rgb)
    axes[0].set_title('Facial Landmarks (478 points)', fontsize=14, fontweight='bold')
    axes[0].axis('off')

    # Draw landmarks with color-coded regions
    region_colors = {}
    for idx, (x, y) in enumerate(landmarks):
        region, color = get_landmark_region(idx)
        region_colors[region] = color

        # Vary marker size by region importance
        if region == "Irises":
            size = 40
        elif region in ["Eyes", "Lips"]:
            size = 15
        else:
            size = 8

        axes[0].scatter(x, y, c=color, s=size, alpha=0.8, edgecolors='white', linewidths=0.3)

    # Add legend
    legend_patches = [Patch(facecolor=color, label=region)
                     for region, color in region_colors.items()]
    axes[0].legend(handles=legend_patches, loc='upper right', fontsize=10)

    # Right: Face mesh regions diagram
    axes[1].set_xlim(0, 400)
    axes[1].set_ylim(0, 500)
    axes[1].set_aspect('equal')
    axes[1].axis('off')
    axes[1].set_title('Face Mesh Regions', fontsize=14, fontweight='bold')

    # Draw a schematic face with labeled regions
    # Face outline
    face_outline = Circle((200, 250), 150, fill=False, edgecolor='#00FF00', linewidth=3)
    axes[1].add_patch(face_outline)
    axes[1].text(200, 420, 'Face Oval', ha='center', fontsize=11, color='#00FF00', fontweight='bold')

    # Eyes
    left_eye = Ellipse((140, 200), 50, 25, fill=True, facecolor='#FF8000', alpha=0.5)
    right_eye = Ellipse((260, 200), 50, 25, fill=True, facecolor='#FF8000', alpha=0.5)
    axes[1].add_patch(left_eye)
    axes[1].add_patch(right_eye)
    axes[1].text(200, 170, 'Eyes', ha='center', fontsize=11, color='#FF8000', fontweight='bold')

    # Eyebrows
    axes[1].plot([110, 170], [160, 155], color='#0000FF', linewidth=8, solid_capstyle='round')
    axes[1].plot([230, 290], [155, 160], color='#0000FF', linewidth=8, solid_capstyle='round')
    axes[1].text(200, 130, 'Eyebrows', ha='center', fontsize=11, color='#0000FF', fontweight='bold')

    # Nose
    nose = Polygon([[200, 200], [180, 280], [220, 280]], fill=True, facecolor='#FFFF00', alpha=0.5)
    axes[1].add_patch(nose)
    axes[1].text(200, 260, 'Nose', ha='center', fontsize=11, color='#FFFF00', fontweight='bold')

    # Lips
    lips = Ellipse((200, 320), 60, 25, fill=True, facecolor='#FF0000', alpha=0.5)
    axes[1].add_patch(lips)
    axes[1].text(200, 360, 'Lips', ha='center', fontsize=11, color='#FF0000', fontweight='bold')

    # Irises
    left_iris = Circle((140, 200), 8, fill=True, facecolor='#00FFFF')
    right_iris = Circle((260, 200), 8, fill=True, facecolor='#00FFFF')
    axes[1].add_patch(left_iris)
    axes[1].add_patch(right_iris)
    axes[1].text(200, 210, 'Irises', ha='center', fontsize=9, color='#00FFFF', fontweight='bold')

    # Face surface annotation
    axes[1].text(80, 280, 'Face\nSurface', ha='center', fontsize=10, color='#808080', fontweight='bold')
    axes[1].text(320, 280, 'Face\nSurface', ha='center', fontsize=10, color='#808080', fontweight='bold')

    # Landmark count summary
    summary_text = """MediaPipe Face Mesh
478 Total Landmarks

Key Regions:
• Face Oval: ~36 points
• Eyes: ~128 points
• Eyebrows: ~44 points
• Nose: ~40 points
• Lips: ~40 points
• Irises: 10 points
• Face Surface: ~180 points"""

    axes[1].text(200, 480, summary_text, ha='center', va='top', fontsize=9,
                family='monospace', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    plt.tight_layout()

    # Save the visualization
    output_path = os.path.join(script_dir, "face_landmarks.png")
    fig.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"Face landmarks visualization saved to: {output_path}")

    # Create annotated face mesh regions diagram using real face image
    fig2, ax2 = plt.subplots(figsize=(10, 12))
    ax2.imshow(image_rgb)
    ax2.set_title('MediaPipe Face Mesh Regions (478 Landmarks)', fontsize=16, fontweight='bold')
    ax2.axis('off')

    # Draw landmarks with color-coded regions (larger dots for readability)
    for idx, (x, y) in enumerate(landmarks):
        region, color = get_landmark_region(idx)
        if region == "Irises":
            size = 60
        elif region in ["Eyes", "Lips"]:
            size = 25
        else:
            size = 15
        ax2.scatter(x, y, c=color, s=size, alpha=0.9, edgecolors='white', linewidths=0.3)

    # Region colors for legend
    region_colors_map = {
        "Face Oval": "#00FF00",
        "Eyes": "#FF8000",
        "Eyebrows": "#0000FF",
        "Nose": "#FFFF00",
        "Lips": "#FF0000",
        "Irises": "#00FFFF",
        "Face Surface": "#808080"
    }

    # Add legend at the bottom
    legend_patches = [Patch(facecolor=color, label=region, edgecolor='white')
                     for region, color in region_colors_map.items()]
    ax2.legend(handles=legend_patches, loc='upper center', bbox_to_anchor=(0.5, -0.02),
              ncol=4, fontsize=9, framealpha=0.9)

    plt.tight_layout()
    regions_path = os.path.join(script_dir, "face_mesh_regions.png")
    fig2.savefig(regions_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig2)
    print(f"Face mesh regions diagram saved to: {regions_path}")

    print("\nDone!")
