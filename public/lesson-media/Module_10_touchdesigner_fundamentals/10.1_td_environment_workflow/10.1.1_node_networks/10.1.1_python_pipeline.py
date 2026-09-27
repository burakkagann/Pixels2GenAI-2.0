import numpy as np
from scipy.ndimage import gaussian_filter

noise = np.random.rand(512, 512)        # step 1
adjusted = noise * 0.5 + 0.25            # step 2
blurred = gaussian_filter(adjusted, sigma=2)  # step 3
save_image(blurred, 'output.png')        # step 4
