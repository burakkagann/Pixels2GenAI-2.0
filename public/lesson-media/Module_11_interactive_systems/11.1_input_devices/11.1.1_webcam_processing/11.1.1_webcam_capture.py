import cv2
import numpy as np

# Open the default webcam (index 0)
cap = cv2.VideoCapture(0)

# Check if webcam opened successfully
if not cap.isOpened():
    print("Error: Could not open webcam")
    exit()

print("Webcam opened successfully!")
print("Press 'q' to quit, 's' to save current frame")

while True:
    # Read a frame from the webcam
    # ret: True if frame was captured successfully
    # frame: The captured image as a NumPy array (height, width, 3)
    ret, frame = cap.read()

    if not ret:
        print("Error: Could not read frame")
        break

    # Display the frame in a window
    # Note: OpenCV uses BGR color order, not RGB
    cv2.imshow('Webcam Feed', frame)

    # Wait for key press (1ms delay allows video to play smoothly)
    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        # Quit when 'q' is pressed
        break
    elif key == ord('s'):
        # Save current frame when 's' is pressed
        cv2.imwrite('webcam_frame.png', frame)
        print(f"Frame saved! Shape: {frame.shape}, dtype: {frame.dtype}")

# Clean up: release webcam and close windows
cap.release()
cv2.destroyAllWindows()
print("Webcam released")
