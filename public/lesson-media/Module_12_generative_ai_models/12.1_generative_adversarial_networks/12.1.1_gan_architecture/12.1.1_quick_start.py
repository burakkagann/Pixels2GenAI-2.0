import torch
import torch.nn as nn

# Target distribution the Generator will eventually learn
DATA_MEAN = 4.0
DATA_STDDEV = 1.25

class Generator(nn.Module):
    def __init__(self):
        super().__init__()
        self.layer1 = nn.Linear(1, 5)
        self.layer2 = nn.Linear(5, 5)
        self.layer3 = nn.Linear(5, 1)

    def forward(self, x):
        x = torch.tanh(self.layer1(x))
        x = torch.tanh(self.layer2(x))
        return self.layer3(x)

generator = Generator()
noise = torch.rand(100, 1)
output = generator(noise)
print(f"Generated {len(output)} numbers")
print(f"Mean: {output.mean():.2f}, Std: {output.std():.2f}")
