import numpy as np
import torch


class Light:
    def get_light_direction(self, pos: np.array):
        ...

class SunLight(Light):
    def __init__(self, pos=None, color=None):
        if pos is None:
            pos = np.array([-1.0, 0.8, 0.5])
            pos /= np.linalg.norm(pos)
        if color is None:
            color = np.array([1, 0.92, 0.75]) * 8
        self.pos = pos
        self.color = color

    def get_light_direction(self, pos: np.array):
        return self.pos[None, :] * np.ones((pos.shape[0], 1))

    def get_light_direction_torch(self, pos: torch.Tensor):
        return torch.Tensor(self.pos[None, :]).to(pos.device) * torch.ones((pos.shape[0], 1)).to(pos.device)
