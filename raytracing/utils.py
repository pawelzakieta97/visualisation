import numpy as np


def uniform_sphere(n):
    ys = np.random.random(n) * 2 - 1
    rs = np.sqrt(1 - ys**2)
    w = np.random.random(n) * 2 * np.pi
    xs = np.cos(w) * rs
    zs = np.sin(w) * rs
    return np.concatenate((xs[:, None], ys[:, None], zs[:, None]), axis=1)


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


