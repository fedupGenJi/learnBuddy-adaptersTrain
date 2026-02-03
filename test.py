import torch
from torch.nn import Parameter

print("torch:", torch.__version__)
print("torch file:", torch.__file__)

# This should NEVER error
print("isinstance(True, Parameter):", isinstance(True, Parameter))

# This should work
p = Parameter(torch.randn(2, 2))
print("made parameter:", p.shape)
