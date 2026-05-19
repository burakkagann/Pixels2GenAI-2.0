import torch
import torch.nn as nn
import functools

class UnetSkipConnectionBlock(nn.Module):
    """
    U-Net building block with skip connection.

    Defines the submodule with skip connection:
    ---input---|--downsampling--[submodule]--upsampling--|--output---
                |________________skip connection_________|

    Args:
        outer_nc: Number of filters in the outer conv layer
        inner_nc: Number of filters in the inner conv layer
        input_nc: Number of channels in input images (None = same as outer_nc)
        submodule: Previously defined submodule (for recursive construction)
        outermost: Is this the outermost block?
        innermost: Is this the innermost block?
        norm_layer: Normalization layer
        use_dropout: Use dropout layers?
    """

    def __init__(self, outer_nc, inner_nc, input_nc=None,
                 submodule=None, outermost=False, innermost=False,
                 norm_layer=nn.BatchNorm2d, use_dropout=False):
        super().__init__()
        self.outermost = outermost

        if input_nc is None:
            input_nc = outer_nc

        # Downsampling layer
        downconv = nn.Conv2d(input_nc, inner_nc, kernel_size=4,
                             stride=2, padding=1, bias=False)
        downrelu = nn.LeakyReLU(0.2, True)
        downnorm = norm_layer(inner_nc)

        # Upsampling layer
        uprelu = nn.ReLU(True)
        upnorm = norm_layer(outer_nc)

        if outermost:
            # Outermost block: no normalization on input, Tanh on output
            upconv = nn.ConvTranspose2d(inner_nc * 2, outer_nc,
                                        kernel_size=4, stride=2,
                                        padding=1)
            down = [downconv]
            up = [uprelu, upconv, nn.Tanh()]
            model = down + [submodule] + up

        elif innermost:
            # Innermost block: no skip connection, no normalization
            upconv = nn.ConvTranspose2d(inner_nc, outer_nc,
                                        kernel_size=4, stride=2,
                                        padding=1, bias=False)
            down = [downrelu, downconv]
            up = [uprelu, upconv, upnorm]
            model = down + up

        else:
            # Intermediate blocks: standard skip connection
            upconv = nn.ConvTranspose2d(inner_nc * 2, outer_nc,
                                        kernel_size=4, stride=2,
                                        padding=1, bias=False)
            down = [downrelu, downconv, downnorm]
            up = [uprelu, upconv, upnorm]

            if use_dropout:
                model = down + [submodule] + up + [nn.Dropout(0.5)]
            else:
                model = down + [submodule] + up

        self.model = nn.Sequential(*model)

    def forward(self, x):
        if self.outermost:
            return self.model(x)
        else:
            # Add skip connection
            return torch.cat([x, self.model(x)], 1)

class UnetGenerator(nn.Module):
    """
    U-Net Generator for Pix2Pix.

    Constructs the U-Net from the innermost layer to the outermost layer,
    with skip connections at each level.

    For 256x256 images: 8 downsampling layers -> 1x1 bottleneck
    For 128x128 images: 7 downsampling layers -> 1x1 bottleneck

    Args:
        input_nc: Number of channels in input images (3 for RGB)
        output_nc: Number of channels in output images (3 for RGB)
        num_downs: Number of downsamplings in U-Net (8 for 256x256)
        ngf: Number of filters in the last conv layer (64 default)
        norm_layer: Type of normalization layer
        use_dropout: Use dropout in decoder
    """

    def __init__(self, input_nc=3, output_nc=3, num_downs=8, ngf=64,
                 norm_layer=nn.BatchNorm2d, use_dropout=False):
        super().__init__()

        # Build U-Net structure from innermost to outermost
        # Innermost block
        unet_block = UnetSkipConnectionBlock(ngf * 8, ngf * 8, input_nc=None,
                                              submodule=None, norm_layer=norm_layer,
                                              innermost=True)

        # Add intermediate layers with ngf * 8 filters
        for i in range(num_downs - 5):
            unet_block = UnetSkipConnectionBlock(ngf * 8, ngf * 8, input_nc=None,
                                                  submodule=unet_block,
                                                  norm_layer=norm_layer,
                                                  use_dropout=use_dropout)

        # Gradually reduce the number of filters
        unet_block = UnetSkipConnectionBlock(ngf * 4, ngf * 8, input_nc=None,
                                              submodule=unet_block,
                                              norm_layer=norm_layer)
        unet_block = UnetSkipConnectionBlock(ngf * 2, ngf * 4, input_nc=None,
                                              submodule=unet_block,
                                              norm_layer=norm_layer)
        unet_block = UnetSkipConnectionBlock(ngf, ngf * 2, input_nc=None,
                                              submodule=unet_block,
                                              norm_layer=norm_layer)

        # Outermost block
        self.model = UnetSkipConnectionBlock(output_nc, ngf, input_nc=input_nc,
                                              submodule=unet_block, outermost=True,
                                              norm_layer=norm_layer)

    def forward(self, input):
        """Standard forward pass."""
        return self.model(input)

def create_facades_generator(pretrained_path=None):
    """
    Create a facades generator, optionally loading pre-trained weights.

    Args:
        pretrained_path: Path to pre-trained weights file

    Returns:
        UnetGenerator configured for facades (256x256, RGB)
    """
    # Create generator with facades configuration
    # 8 downsampling layers for 256x256 images
    generator = UnetGenerator(
        input_nc=3,
        output_nc=3,
        num_downs=8,
        ngf=64,
        norm_layer=nn.BatchNorm2d,
        use_dropout=True  # Dropout used in original pix2pix training
    )

    if pretrained_path is not None:
        print(f"Loading pre-trained weights from: {pretrained_path}")
        state_dict = torch.load(pretrained_path, map_location='cpu')

        # Handle different weight formats
        if isinstance(state_dict, dict) and 'model' in state_dict:
            state_dict = state_dict['model']

        generator.load_state_dict(state_dict, strict=False)
        print("Weights loaded successfully!")

    return generator

def count_parameters(model):
    """Count total trainable parameters in a model."""
    return sum(p.numel() for p in model.parameters() if p.requires_grad)

if __name__ == '__main__':
    """Test the facades generator architecture."""
    print("=" * 60)
    print("Testing Facades Generator Architecture")
    print("=" * 60)
    print()

    # Create generator
    generator = UnetGenerator(input_nc=3, output_nc=3, num_downs=8, ngf=64)

    # Test with sample input
    batch_size = 1
    test_input = torch.randn(batch_size, 3, 256, 256)

    print(f"Input shape:  {test_input.shape}")

    with torch.no_grad():
        output = generator(test_input)

    print(f"Output shape: {output.shape}")
    print(f"Output range: [{output.min():.2f}, {output.max():.2f}]")
    print(f"Parameters:   {count_parameters(generator):,}")
    print()

    # Check for pretrained weights
    from pathlib import Path
    weights_path = Path('checkpoints/facades_generator.pth')

    if weights_path.exists():
        print(f"Pre-trained weights found at: {weights_path}")
        generator = create_facades_generator(str(weights_path))
    else:
        print("Pre-trained weights not found.")
        print("Run 'python download_pretrained.py' to download.")

    print()
    print("Architecture test passed!")
