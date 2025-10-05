"""
Mock para PyTorch - mantém a interface original mas sem dependências externas
"""
import numpy as np
from typing import Any, Dict, List, Tuple, Optional
import random

class MockTensor:
    """Mock do torch.Tensor"""
    
    def __init__(self, data):
        if isinstance(data, (list, tuple)):
            self.data = np.array(data)
        else:
            self.data = data
    
    def __getitem__(self, key):
        return MockTensor(self.data[key])
    
    def __setitem__(self, key, value):
        self.data[key] = value
    
    def item(self):
        return float(self.data)
    
    def numpy(self):
        return self.data
    
    def shape(self):
        return self.data.shape
    
    def size(self, dim=None):
        if dim is None:
            return self.data.shape
        return self.data.shape[dim]
    
    def detach(self):
        return MockTensor(self.data.copy())
    
    def cpu(self):
        return self
    
    def cuda(self):
        return self
    
    def to(self, device):
        return self
    
    def float(self):
        return MockTensor(self.data.astype(np.float32))
    
    def long(self):
        return MockTensor(self.data.astype(np.int64))
    
    def int(self):
        return MockTensor(self.data.astype(np.int32))
    
    def mean(self, dim=None):
        if dim is None:
            return MockTensor(np.mean(self.data))
        return MockTensor(np.mean(self.data, axis=dim))
    
    def sum(self, dim=None):
        if dim is None:
            return MockTensor(np.sum(self.data))
        return MockTensor(np.sum(self.data, axis=dim))
    
    def max(self, dim=None):
        if dim is None:
            return MockTensor(np.max(self.data))
        return MockTensor(np.max(self.data, axis=dim))
    
    def min(self, dim=None):
        if dim is None:
            return MockTensor(np.min(self.data))
        return MockTensor(np.min(self.data, axis=dim))
    
    def argmax(self, dim=None):
        if dim is None:
            return MockTensor(np.argmax(self.data))
        return MockTensor(np.argmax(self.data, axis=dim))
    
    def argmin(self, dim=None):
        if dim is None:
            return MockTensor(np.argmin(self.data))
        return MockTensor(np.argmin(self.data, axis=dim))
    
    def view(self, *shape):
        return MockTensor(self.data.reshape(shape))
    
    def reshape(self, *shape):
        return MockTensor(self.data.reshape(shape))
    
    def squeeze(self, dim=None):
        if dim is None:
            return MockTensor(np.squeeze(self.data))
        return MockTensor(np.squeeze(self.data, axis=dim))
    
    def unsqueeze(self, dim):
        return MockTensor(np.expand_dims(self.data, axis=dim))
    
    def transpose(self, dim0, dim1):
        return MockTensor(np.swapaxes(self.data, dim0, dim1))
    
    def permute(self, *dims):
        return MockTensor(np.transpose(self.data, dims))
    
    def clone(self):
        return MockTensor(self.data.copy())
    
    def requires_grad_(self, requires_grad=True):
        return self
    
    def backward(self, gradient=None):
        pass
    
    def grad(self):
        return None
    
    def zero_(self):
        self.data.fill(0)
        return self
    
    def fill_(self, value):
        self.data.fill(value)
        return self
    
    def __add__(self, other):
        if isinstance(other, MockTensor):
            return MockTensor(self.data + other.data)
        return MockTensor(self.data + other)
    
    def __sub__(self, other):
        if isinstance(other, MockTensor):
            return MockTensor(self.data - other.data)
        return MockTensor(self.data - other)
    
    def __mul__(self, other):
        if isinstance(other, MockTensor):
            return MockTensor(self.data * other.data)
        return MockTensor(self.data * other)
    
    def __truediv__(self, other):
        if isinstance(other, MockTensor):
            return MockTensor(self.data / other.data)
        return MockTensor(self.data / other)
    
    def __pow__(self, other):
        if isinstance(other, MockTensor):
            return MockTensor(self.data ** other.data)
        return MockTensor(self.data ** other)
    
    def __neg__(self):
        return MockTensor(-self.data)
    
    def __abs__(self):
        return MockTensor(np.abs(self.data))
    
    def __len__(self):
        return len(self.data)
    
    def __repr__(self):
        return f"MockTensor({self.data})"

class MockModule:
    """Mock base para módulos PyTorch"""
    
    def __init__(self):
        self.training = True
        self._parameters = {}
        self._modules = {}
    
    def train(self, mode=True):
        self.training = mode
        return self
    
    def eval(self):
        self.training = False
        return self
    
    def parameters(self):
        return []
    
    def named_parameters(self):
        return []
    
    def modules(self):
        return []
    
    def named_modules(self):
        return []
    
    def state_dict(self):
        return {}
    
    def load_state_dict(self, state_dict):
        pass
    
    def forward(self, *args, **kwargs):
        raise NotImplementedError
    
    def __call__(self, *args, **kwargs):
        return self.forward(*args, **kwargs)

class MockLinear(MockModule):
    """Mock do torch.nn.Linear"""
    
    def __init__(self, in_features, out_features, bias=True):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.bias = bias
        
        # Pesos aleatórios mock
        self.weight = MockTensor(np.random.randn(out_features, in_features) * 0.1)
        if bias:
            self.bias = MockTensor(np.random.randn(out_features) * 0.1)
        else:
            self.bias = None
    
    def forward(self, x):
        if isinstance(x, MockTensor):
            x_data = x.data
        else:
            x_data = x
        
        # Simulação simples de multiplicação de matriz
        if len(x_data.shape) == 1:
            x_data = x_data.reshape(1, -1)
        
        result = np.dot(x_data, self.weight.data.T)
        if self.bias is not None:
            result += self.bias.data
        
        return MockTensor(result)

class MockReLU(MockModule):
    """Mock do torch.nn.ReLU"""
    
    def forward(self, x):
        if isinstance(x, MockTensor):
            return MockTensor(np.maximum(0, x.data))
        return np.maximum(0, x)

class MockSigmoid(MockModule):
    """Mock do torch.nn.Sigmoid"""
    
    def forward(self, x):
        if isinstance(x, MockTensor):
            return MockTensor(1 / (1 + np.exp(-x.data)))
        return 1 / (1 + np.exp(-x))

class MockTanh(MockModule):
    """Mock do torch.nn.Tanh"""
    
    def forward(self, x):
        if isinstance(x, MockTensor):
            return MockTensor(np.tanh(x.data))
        return np.tanh(x)

class MockMSELoss(MockModule):
    """Mock do torch.nn.MSELoss"""
    
    def forward(self, input, target):
        if isinstance(input, MockTensor):
            input_data = input.data
        else:
            input_data = input
            
        if isinstance(target, MockTensor):
            target_data = target.data
        else:
            target_data = target
        
        return MockTensor(np.mean((input_data - target_data) ** 2))

class MockAdam:
    """Mock do torch.optim.Adam"""
    
    def __init__(self, params, lr=0.001, **kwargs):
        self.params = params
        self.lr = lr
    
    def step(self):
        pass
    
    def zero_grad(self):
        pass

class MockScheduler:
    """Mock do torch.optim.lr_scheduler"""
    
    def __init__(self, optimizer, **kwargs):
        self.optimizer = optimizer
    
    def step(self):
        pass

# Mock do módulo torch
class MockTorch:
    """Mock do módulo torch principal"""
    
    def __init__(self):
        self.float32 = np.float32
        self.float64 = np.float64
        self.int32 = np.int32
        self.int64 = np.int64
        self.long = np.int64
    
    def tensor(self, data, dtype=None, device=None):
        return MockTensor(data)
    
    def zeros(self, *shape, dtype=None, device=None):
        return MockTensor(np.zeros(shape))
    
    def ones(self, *shape, dtype=None, device=None):
        return MockTensor(np.ones(shape))
    
    def randn(self, *shape, dtype=None, device=None):
        return MockTensor(np.random.randn(*shape))
    
    def rand(self, *shape, dtype=None, device=None):
        return MockTensor(np.random.rand(*shape))
    
    def arange(self, start, end=None, step=1, dtype=None, device=None):
        if end is None:
            end = start
            start = 0
        return MockTensor(np.arange(start, end, step))
    
    def linspace(self, start, end, steps, dtype=None, device=None):
        return MockTensor(np.linspace(start, end, steps))
    
    def save(self, obj, path):
        # Mock save - não faz nada
        pass
    
    def load(self, path):
        # Mock load - retorna None
        return None
    
    def no_grad(self):
        return self
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        pass

# Mock do módulo torch.nn
class MockTorchNN:
    """Mock do módulo torch.nn"""
    
    def __init__(self):
        self.Linear = MockLinear
        self.ReLU = MockReLU
        self.Sigmoid = MockSigmoid
        self.Tanh = MockTanh
        self.MSELoss = MockMSELoss
        self.Module = MockModule

# Mock do módulo torch.optim
class MockTorchOptim:
    """Mock do módulo torch.optim"""
    
    def __init__(self):
        self.Adam = MockAdam

# Criar instâncias mock
torch = MockTorch()
torch.nn = MockTorchNN()
torch.optim = MockTorchOptim()
