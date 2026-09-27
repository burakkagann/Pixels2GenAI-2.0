import torch
from diffusers import StableDiffusionControlNetPipeline, ControlNetModel
from PIL import Image
import cv2, numpy as np

# Load ControlNet + base SD pipeline
controlnet = ControlNetModel.from_pretrained("./models/controlnet_fill50k")
pipe = StableDiffusionControlNetPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5", controlnet=controlnet,
    torch_dtype=torch.float16,
).to("cuda")

# Build a Canny edge map from any image
image = cv2.imread("sample_inputs/circle.png")
edges = cv2.Canny(image, 100, 200)
edge_image = Image.fromarray(np.stack([edges]*3, axis=-1))

result = pipe(
    prompt="a vibrant african fabric pattern",
    image=edge_image,
    num_inference_steps=30, guidance_scale=7.5,
).images[0]
result.save("controlnet_output.png")
