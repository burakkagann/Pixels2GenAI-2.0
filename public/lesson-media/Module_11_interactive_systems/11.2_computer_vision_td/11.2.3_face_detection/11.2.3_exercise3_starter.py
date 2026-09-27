import cv2
import numpy as np
from scipy.spatial import Delaunay
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# TODO 1: create FaceLandmarker with running_mode=LIVE_STREAM

# TODO 2: open VideoCapture(0)

# TODO 3: per frame: convert BGR to RGB, build mp.Image,
#         detect, triangulate, render, imshow
