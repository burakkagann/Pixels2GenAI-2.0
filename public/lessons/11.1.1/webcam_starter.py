import cv2
import numpy as np

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam")
    exit()

# Read the first frame and store it as "previous"
ret, previous_frame = cap.read()
previous_gray = cv2.cvtColor(previous_frame, cv2.COLOR_BGR2GRAY)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Convert current frame to grayscale
    current_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # TODO: Calculate the absolute difference between current and previous
    # Hint: Use cv2.absdiff(previous_gray, current_gray)
    diff = None  # Replace None with your code

    # TODO: Apply a threshold to create a binary motion mask
    # Hint: Use cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
    motion_mask = None  # Replace None with your code

    # Display results
    cv2.imshow('Webcam', frame)
    if diff is not None:
        cv2.imshow('Difference', diff)
    if motion_mask is not None:
        cv2.imshow('Motion Mask', motion_mask)

    # Update previous frame for next iteration
    previous_gray = current_gray.copy()

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
