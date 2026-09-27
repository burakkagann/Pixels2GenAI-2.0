import torch
from diffusers import StableDiffusionPipeline

pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16,
).to("cuda")
pipe.load_lora_weights("models/fabric_lora")     # folder with both downloaded files

prompt = "a beautiful dress made of sks african fabric pattern, fashion photography"
image = pipe(prompt, guidance_scale=7.5).images[0]
image.save("personalized_fabric.png")
