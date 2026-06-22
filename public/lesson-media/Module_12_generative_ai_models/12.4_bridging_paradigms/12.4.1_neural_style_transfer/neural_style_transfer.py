"""Optimization-based Neural Style Transfer (Gatys et al., 2015).

Re-implementation of the original NST algorithm using a pre-trained VGG-19.
Content loss is MSE on a deep feature map; style loss is MSE on Gram matrices
across multiple layers. Image pixels are the optimization variable.

Usage:
    python neural_style_transfer.py --content path/to/photo.jpg \\
                                    --style   path/to/painting.jpg \\
                                    --output  styled.jpg

Author: Pixels2GenAI Project
"""

import argparse
from pathlib import Path

import torch
import torch.nn as nn
import torch.optim as optim
from PIL import Image
from torchvision import models, transforms
from torchvision.utils import save_image


# VGG-19 layer indices that capture content (deep) and style (multi-scale).
CONTENT_LAYERS = {"conv_4"}
STYLE_LAYERS = {"conv_1", "conv_2", "conv_3", "conv_4", "conv_5"}


def load_image(path: Path, size: int = 512, device: torch.device = None) -> torch.Tensor:
    image = Image.open(path).convert("RGB")
    transform = transforms.Compose([
        transforms.Resize((size, size)),
        transforms.ToTensor(),
    ])
    return transform(image).unsqueeze(0).to(device)


def gram_matrix(features: torch.Tensor) -> torch.Tensor:
    """Channel-wise Gram matrix; captures feature co-activation statistics."""
    batch, channels, h, w = features.size()
    flat = features.view(batch * channels, h * w)
    return (flat @ flat.t()) / (batch * channels * h * w)


class StyleTransferVGG(nn.Module):
    """Wraps VGG-19 conv layers; exposes named feature maps at each conv block."""

    def __init__(self):
        super().__init__()
        vgg = models.vgg19(weights=models.VGG19_Weights.DEFAULT).features
        for p in vgg.parameters():
            p.requires_grad_(False)

        self.layers = nn.ModuleDict()
        block_idx = 0
        for layer in vgg.children():
            if isinstance(layer, nn.Conv2d):
                block_idx += 1
                self.layers[f"conv_{block_idx}"] = layer
            elif isinstance(layer, nn.MaxPool2d):
                self.layers[f"pool_{block_idx}"] = layer
            elif isinstance(layer, nn.ReLU):
                self.layers[f"relu_{block_idx}"] = nn.ReLU(inplace=False)

    def forward(self, x: torch.Tensor) -> dict[str, torch.Tensor]:
        out = {}
        for name, layer in self.layers.items():
            x = layer(x)
            if name in CONTENT_LAYERS or name in STYLE_LAYERS:
                out[name] = x
            if name == "conv_5":
                break
        return out


def style_transfer(
    content_path: Path,
    style_path: Path,
    output_path: Path,
    *,
    size: int = 512,
    steps: int = 300,
    content_weight: float = 1.0,
    style_weight: float = 1e6,
    device: torch.device | None = None,
) -> None:
    device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device: {device}")

    content = load_image(content_path, size=size, device=device)
    style = load_image(style_path, size=size, device=device)

    # Optimize the pixels directly; initialise from the content image.
    target = content.clone().requires_grad_(True)
    model = StyleTransferVGG().to(device).eval()
    optimizer = optim.LBFGS([target], max_iter=1)

    with torch.no_grad():
        content_feats = model(content)
        style_feats = {k: gram_matrix(v) for k, v in model(style).items()
                       if k in STYLE_LAYERS}

    step = [0]

    def closure() -> torch.Tensor:
        optimizer.zero_grad()
        target_feats = model(target)

        c_loss = sum(
            nn.functional.mse_loss(target_feats[k], content_feats[k])
            for k in CONTENT_LAYERS
        )
        s_loss = sum(
            nn.functional.mse_loss(gram_matrix(target_feats[k]), style_feats[k])
            for k in STYLE_LAYERS
        )
        loss = content_weight * c_loss + style_weight * s_loss
        loss.backward()

        step[0] += 1
        if step[0] % 25 == 0:
            print(f"  step {step[0]:3d}  content={c_loss.item():.4f}  "
                  f"style={s_loss.item():.6f}  total={loss.item():.4f}")
        return loss

    print(f"Optimising for {steps} steps...")
    for _ in range(steps):
        optimizer.step(closure)

    target.data.clamp_(0, 1)
    save_image(target.cpu(), output_path)
    print(f"Saved: {output_path}")


def main() -> None:
    ap = argparse.ArgumentParser(description="Optimization-based Neural Style Transfer.")
    ap.add_argument("--content", type=Path, required=True, help="Content image path.")
    ap.add_argument("--style", type=Path, required=True, help="Style image path.")
    ap.add_argument("--output", type=Path, default=Path("styled.jpg"), help="Output path.")
    ap.add_argument("--size", type=int, default=512, help="Square image size.")
    ap.add_argument("--steps", type=int, default=300, help="Optimisation steps.")
    ap.add_argument("--content-weight", type=float, default=1.0)
    ap.add_argument("--style-weight", type=float, default=1e6)
    args = ap.parse_args()

    style_transfer(
        args.content, args.style, args.output,
        size=args.size, steps=args.steps,
        content_weight=args.content_weight,
        style_weight=args.style_weight,
    )


if __name__ == "__main__":
    main()
