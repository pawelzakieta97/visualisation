import numpy as np
import torch


def uniform_sphere(n):
    ys = np.random.random(n) * 2 - 1
    rs = np.sqrt(1 - ys**2)
    w = np.random.random(n) * 2 * np.pi
    xs = np.cos(w) * rs
    zs = np.sin(w) * rs
    return np.concatenate((xs[:, None], ys[:, None], zs[:, None]), axis=1)

def uniform_sphere_torch(n, device='cpu'):
    ys = torch.rand(n).to(device) * 2 - 1
    rs = torch.sqrt(1 - ys**2)
    w = torch.rand(n).to(device) * 2 * torch.pi
    xs = torch.cos(w) * rs
    zs = torch.sin(w) * rs
    return torch.concatenate((xs[:, None], ys[:, None], zs[:, None]), axis=1)


def uniform_sphere2(n):
    """
    sanity check for my math
    """
    a = np.random.random(n) * np.pi - np.pi/2
    rs = np.cos(a)
    w = np.random.random(n) * 2 * np.pi
    ys = np.sin(a)
    xs = np.cos(w) * rs
    zs = np.sin(w) * rs
    return np.concatenate((xs[:, None], ys[:, None], zs[:, None]), axis=1)


