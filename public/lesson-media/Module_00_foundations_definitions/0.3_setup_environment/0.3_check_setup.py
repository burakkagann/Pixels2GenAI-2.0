"""
Check which of the course's kits this Python can use, then save a picture to prove
that images work. A missing kit is fine if you have not reached its modules yet.

Author: Pixels2GenAI Project
"""
import importlib.util
import sys

import numpy as np
from PIL import Image

KITS = {
    "Core kit (Modules 0 to 10)": ["numpy", "PIL", "matplotlib", "scipy", "imageio", "pandas", "cv2"],
    "Camera kit (Module 11)": ["mediapipe"],
    "Model kit (Module 12 onward)": ["torch", "torchvision", "tqdm"],
}

in_browser = sys.platform == "emscripten"
python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
print(f"Python {sys.version.split()[0]}")

if in_browser:
    # The Run button fetches what a script imports, so there are no kits to check here.
    print("Running on this page, in your browser. Nothing is installed on your computer.")
else:
    if python_version != "3.11":
        print("Note: this course's scripts are tested on Python 3.11.")

    # find_spec looks a package up without importing it. Importing the model kit
    # would take many seconds, and we only need to know whether it is there.
    for kit_name, package_names in KITS.items():
        missing = [name for name in package_names if importlib.util.find_spec(name) is None]
        if missing:
            print(f"{kit_name}: not installed yet (missing {', '.join(missing)})")
        else:
            print(f"{kit_name}: ready")

# The check every lesson depends on: can this Python make an image and save it?
ramp = np.linspace(0, 1, 400)[np.newaxis, :, np.newaxis]
teal = np.array([0, 131, 138])
paper = np.array([243, 239, 231])
picture = (paper + (teal - paper) * ramp) * np.ones((120, 400, 3))

Image.fromarray(picture.astype(np.uint8)).save("setup_check.png")
print("Saved setup_check.png")
