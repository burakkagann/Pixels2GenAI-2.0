import cv2
import numpy as np

cap = cv2.VideoCapture(0)
ok, prev = cap.read()
prev_gray = cv2.GaussianBlur(cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY), (21, 21), 0)

while True:
    ok, cur = cap.read()
    cur_gray = cv2.GaussianBlur(cv2.cvtColor(cur, cv2.COLOR_BGR2GRAY), (21, 21), 0)

    # TODO 1: per-pixel absolute difference between current and previous gray frames

    # TODO 2: threshold the diff to a binary motion mask at value 25

    # TODO 3: copy the current frame, paint green wherever the mask is set

    prev_gray = cur_gray.copy()
    cv2.imshow('Motion', out)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
