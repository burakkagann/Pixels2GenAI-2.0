import cv2
import numpy as np
from scipy.spatial import Delaunay
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

image = cv2.cvtColor(cv2.imread('sample_face.jpg'), cv2.COLOR_BGR2RGB)
mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=image)

detector = vision.FaceLandmarker.create_from_options(
    vision.FaceLandmarkerOptions(
        base_options=python.BaseOptions(model_asset_path='face_landmarker.task'),
        num_faces=1,
    ))
landmarks = np.array([
    [lm.x * image.shape[1], lm.y * image.shape[0]]
    for lm in detector.detect(mp_img).face_landmarks[0]
])

# Triangulate
tri = Delaunay(landmarks)

# Fill each triangle with the average colour of its centroid
output = np.zeros_like(image)
for simplex in tri.simplices:
    pts = landmarks[simplex].astype(np.int32)
    centroid = pts.mean(axis=0).astype(int)
    color = image[centroid[1], centroid[0]].tolist()
    cv2.fillPoly(output, [pts], color)

cv2.imwrite('lowpoly.png', cv2.cvtColor(output, cv2.COLOR_RGB2BGR))
