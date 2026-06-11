import cv2
import numpy as np
from scipy.spatial import Delaunay
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# Load image
image_bgr = cv2.imread("sample_face.jpg")
image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
height, width = image_rgb.shape[:2]

# TODO 1: Create MediaPipe detector and detect landmarks
# Hint: Use vision.FaceLandmarker.create_from_options()
detector = ...
mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)
result = ...

# TODO 2: Extract landmark coordinates as numpy array
landmarks = []
for lm in result.face_landmarks[0]:
    # Convert normalized coordinates to pixels
    ...

landmarks = np.array(landmarks)

# TODO 3: Add boundary points (corners + edge midpoints)
corners = np.array([...])
all_points = np.vstack([landmarks, corners])

# TODO 4: Apply Delaunay triangulation
triangulation = ...

# TODO 5: Render each triangle with sampled color
output = np.zeros_like(image_rgb)
for simplex in triangulation.simplices:
    triangle = all_points[simplex].astype(np.int32)
    # Calculate centroid and sample color
    ...
    # Fill triangle
    cv2.fillPoly(output, [triangle], color)

# Save result
cv2.imwrite("my_lowpoly_face.png", cv2.cvtColor(output, cv2.COLOR_RGB2BGR))
