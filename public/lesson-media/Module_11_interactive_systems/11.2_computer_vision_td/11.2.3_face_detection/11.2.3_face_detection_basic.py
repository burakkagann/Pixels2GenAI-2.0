import cv2
import numpy as np
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

# Import MediaPipe after ensuring model exists
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# Load the sample face image
image_path = os.path.join(script_dir, "sample_face.jpg")
image = cv2.imread(image_path)

if image is None:
    print(f"Error: Could not load image from {image_path}")
    print("Please ensure sample_face.jpg exists in the same directory.")
    exit(1)

# Convert BGR (OpenCV format) to RGB (MediaPipe format)
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# Create a MediaPipe Image object
mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)

# Configure Face Landmarker
# output_face_blendshapes: outputs 52 facial blendshapes for expressions
# output_facial_transformation_matrixes: outputs face transformation matrix
# num_faces: maximum number of faces to detect
base_options = python.BaseOptions(model_asset_path=model_path)
options = vision.FaceLandmarkerOptions(
    base_options=base_options,
    output_face_blendshapes=True,
    output_facial_transformation_matrixes=True,
    num_faces=1
)

# Create the face landmarker
detector = vision.FaceLandmarker.create_from_options(options)

# Detect face landmarks
detection_result = detector.detect(mp_image)

# Create a copy of the image for drawing
annotated_image = image.copy()
height, width, _ = annotated_image.shape

# Check if any faces were detected
if detection_result.face_landmarks:
    print(f"Face detected! Found {len(detection_result.face_landmarks)} face(s)")

    # Get the first detected face
    face_landmarks = detection_result.face_landmarks[0]

    # Count the landmarks
    num_landmarks = len(face_landmarks)
    print(f"Number of landmarks detected: {num_landmarks}")

    # Draw all landmarks as small circles with color-coded regions
    # MediaPipe Face Mesh landmark indices:
    # 0-16: Face oval (jawline)
    # 17-67: Right eyebrow
    # 68-127: Left eyebrow
    # 128-159: Right eye
    # 160-191: Left eye
    # 192-223: Nose
    # 224-263: Outer lips
    # 264-295: Inner lips
    # 296-467: Face (cheeks, forehead)
    # 468-477: Irises

    for idx, landmark in enumerate(face_landmarks):
        # Convert normalized coordinates (0-1) to pixel coordinates
        x = int(landmark.x * width)
        y = int(landmark.y * height)

        # Color varies by facial region
        if idx >= 468:  # Irises
            color = (255, 255, 0)  # Cyan
            radius = 3
        elif idx < 17:  # Face oval (jawline)
            color = (0, 255, 0)  # Green
            radius = 2
        elif idx < 68:  # Right eyebrow
            color = (255, 0, 0)  # Blue
            radius = 2
        elif idx < 128:  # Left eyebrow
            color = (255, 0, 0)  # Blue
            radius = 2
        elif idx < 160:  # Right eye
            color = (255, 128, 0)  # Orange
            radius = 2
        elif idx < 192:  # Left eye
            color = (255, 128, 0)  # Orange
            radius = 2
        elif idx < 224:  # Nose
            color = (0, 255, 255)  # Yellow
            radius = 2
        elif idx < 296:  # Lips
            color = (0, 0, 255)  # Red
            radius = 2
        else:  # Face (cheeks, forehead)
            color = (128, 128, 128)  # Gray
            radius = 1

        cv2.circle(annotated_image, (x, y), radius, color, -1)

    # Print some key landmark positions
    print("\nKey landmark positions (pixel coordinates):")
    key_landmarks = {
        "Nose tip": 1,
        "Left eye (inner)": 133,
        "Right eye (inner)": 362,
        "Upper lip (center)": 13,
        "Lower lip (center)": 14,
        "Chin": 152,
        "Left iris center": 468,
        "Right iris center": 473
    }

    for name, idx in key_landmarks.items():
        if idx < len(face_landmarks):
            lm = face_landmarks[idx]
            x_px = int(lm.x * width)
            y_px = int(lm.y * height)
            print(f"  {name} (index {idx}): ({x_px}, {y_px})")

# Save the annotated image
output_path = os.path.join(script_dir, "face_detection_basic.png")
cv2.imwrite(output_path, annotated_image)
print(f"\nAnnotated image saved to: {output_path}")

# Clean up
detector.close()
