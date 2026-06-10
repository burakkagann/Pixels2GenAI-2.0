import cv2
import numpy as np

# Open webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam")
    exit()

print("Background Subtraction Demo")
print("Press 'r' to reset background, 'q' to quit")

# Read first frame as initial background
ret, background = cap.read()
if not ret:
    print("Error: Could not read initial frame")
    exit()

# Convert background to grayscale for comparison
background_gray = cv2.cvtColor(background, cv2.COLOR_BGR2GRAY)
background_gray = cv2.GaussianBlur(background_gray, (21, 21), 0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Convert current frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    # Calculate absolute difference between background and current frame
    # This highlights areas where movement has occurred
    diff = cv2.absdiff(background_gray, gray)

    # Apply threshold to create binary mask
    # Pixels with difference > 25 are considered "motion"
    _, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)

    # Optional: Clean up the mask with morphological operations
    thresh = cv2.dilate(thresh, None, iterations=2)

    # Create colored visualization: show motion areas in green
    motion_overlay = frame.copy()
    motion_overlay[thresh > 0] = [0, 255, 0]  # Green where motion detected

    # Blend original frame with motion overlay
    output = cv2.addWeighted(frame, 0.7, motion_overlay, 0.3, 0)

    # Add text label
    cv2.putText(output, "Motion Detection Active", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Show multiple views
    cv2.imshow('Original', frame)
    cv2.imshow('Motion Mask', thresh)
    cv2.imshow('Motion Overlay', output)

    # Handle key presses
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('r'):
        # Reset background to current frame
        background_gray = gray.copy()
        print("Background reset!")

cap.release()
cv2.destroyAllWindows()
