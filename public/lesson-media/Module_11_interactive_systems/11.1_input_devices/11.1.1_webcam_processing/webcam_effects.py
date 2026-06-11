import cv2
import numpy as np

# Open webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open webcam")
    exit()

# Current effect mode (1 = original)
current_effect = 1

print("Webcam Effects Demo")
print("Press 1-5 to switch effects, 'q' to quit")
print("1: Original  2: Grayscale  3: Blur  4: Edges  5: Negative")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Apply selected effect
    if current_effect == 1:
        # Original - no processing
        output = frame

    elif current_effect == 2:
        # Grayscale - convert color to single channel
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Convert back to 3 channels for display consistency
        output = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

    elif current_effect == 3:
        # Blur - smooth the image using Gaussian blur
        output = cv2.GaussianBlur(frame, (21, 21), 0)

    elif current_effect == 4:
        # Edge Detection - find edges using Canny algorithm
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        output = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

    elif current_effect == 5:
        # Negative - invert all colors
        output = 255 - frame

    # Add text showing current effect
    effect_names = {1: "Original", 2: "Grayscale", 3: "Blur", 4: "Edges", 5: "Negative"}
    cv2.putText(output, f"Effect: {effect_names[current_effect]}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow('Webcam Effects', output)

    # Handle key presses
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key in [ord('1'), ord('2'), ord('3'), ord('4'), ord('5')]:
        current_effect = int(chr(key))
        print(f"Switched to: {effect_names[current_effect]}")

cap.release()
cv2.destroyAllWindows()
