import cv2
import numpy as np
from scipy.spatial import Delaunay
import os
import urllib.request
import time
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

def create_face_detector(model_path):
    """Create a MediaPipe Face Landmarker for video processing."""
    base_options = python.BaseOptions(model_asset_path=model_path)
    options = vision.FaceLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.VIDEO,
        num_faces=1
    )
    return vision.FaceLandmarker.create_from_options(options)

def detect_landmarks_video(detector, frame_rgb, timestamp_ms):
    """Detect facial landmarks in a video frame."""
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
    result = detector.detect_for_video(mp_image, timestamp_ms)

    if not result.face_landmarks:
        return None

    height, width = frame_rgb.shape[:2]
    landmarks = []
    for lm in result.face_landmarks[0]:
        x = lm.x * width
        y = lm.y * height
        landmarks.append([x, y])

    return np.array(landmarks)

def create_lowpoly_frame(frame_rgb, landmarks, show_edges=False):
    """Create a low-poly version of a video frame."""
    height, width = frame_rgb.shape[:2]

    # Add boundary points for full coverage
    corners = np.array([
        [0, 0], [width, 0], [width, height], [0, height],
        [width/2, 0], [width, height/2], [width/2, height], [0, height/2]
    ])
    points = np.vstack([landmarks, corners])

    # Compute Delaunay triangulation
    try:
        tri = Delaunay(points)
    except Exception:
        return frame_rgb  # Return original if triangulation fails

    # Create output image
    output = np.zeros_like(frame_rgb)

    # Draw each triangle
    for simplex in tri.simplices:
        triangle = points[simplex].astype(np.int32)

        # Calculate centroid for color sampling
        centroid = np.mean(triangle, axis=0).astype(int)
        cx = np.clip(centroid[0], 0, width - 1)
        cy = np.clip(centroid[1], 0, height - 1)

        # Get color from original image
        color = frame_rgb[cy, cx].tolist()

        # Draw filled triangle
        cv2.fillPoly(output, [triangle], color)

        # Optionally draw edges
        if show_edges:
            cv2.polylines(output, [triangle], True, (255, 255, 255), 1)

    return output

def main():
    print("=" * 50)
    print("Real-Time Low-Poly Face Art")
    print("=" * 50)
    print("\nControls:")
    print("  'q' - Quit")
    print("  's' - Save current frame")
    print("  'e' - Toggle edges")
    print("  'f' - Toggle FPS display")
    print("\nStarting webcam...")

    # Open webcam
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        print("Please check that your webcam is connected and not in use.")
        return

    # Set resolution (lower for better performance)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    # Create face detector
    detector = create_face_detector(model_path)

    # State variables
    show_edges = False
    show_fps = True
    frame_count = 0
    start_time = time.time()
    fps = 0

    print("Webcam opened successfully!")
    print("Position your face in front of the camera.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame from webcam.")
            break

        # Mirror the frame for more intuitive interaction
        frame = cv2.flip(frame, 1)

        # Convert BGR to RGB for MediaPipe
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Get timestamp for video mode
        timestamp_ms = int(cap.get(cv2.CAP_PROP_POS_MSEC))
        if timestamp_ms == 0:
            timestamp_ms = int((time.time() - start_time) * 1000)

        # Detect landmarks
        landmarks = detect_landmarks_video(detector, frame_rgb, timestamp_ms)

        if landmarks is not None:
            # Create low-poly version
            output_rgb = create_lowpoly_frame(frame_rgb, landmarks, show_edges)
            # Convert back to BGR for display
            output = cv2.cvtColor(output_rgb, cv2.COLOR_RGB2BGR)
        else:
            # Show original with "No face detected" message
            output = frame.copy()
            cv2.putText(output, "No face detected", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # Calculate and display FPS
        frame_count += 1
        elapsed = time.time() - start_time
        if elapsed > 0:
            fps = frame_count / elapsed

        if show_fps:
            cv2.putText(output, f"FPS: {fps:.1f}", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # Display edge status
        edge_status = "ON" if show_edges else "OFF"
        cv2.putText(output, f"Edges: {edge_status}", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        # Show the frame
        cv2.imshow(' Real-Time Low-Poly Face Triangulation (Press Q to quit)', output)

        # Handle key presses
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("\nQuitting...")
            break
        elif key == ord('s'):
            # Save current frame
            save_path = os.path.join(script_dir, "realtime_lowpoly_screenshot.png")
            cv2.imwrite(save_path, output)
            print(f"Screenshot saved to: {save_path}")
        elif key == ord('e'):
            show_edges = not show_edges
            print(f"Edges: {'ON' if show_edges else 'OFF'}")
        elif key == ord('f'):
            show_fps = not show_fps
            print(f"FPS display: {'ON' if show_fps else 'OFF'}")

    # Clean up
    cap.release()
    cv2.destroyAllWindows()
    detector.close()
    print("Done!")

if __name__ == '__main__':
    main()
