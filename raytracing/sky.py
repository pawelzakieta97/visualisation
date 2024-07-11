import numpy as np
import torch


class Sky:
    def __init__(self, horizon_color=None, zenith_color=None, floor_color=None):
        if horizon_color is None:
            horizon_color = np.array([1, 1, 1])
        if zenith_color is None:
            zenith_color = np.array([0, 0.5, 1])
        if floor_color is None:
            floor_color = np.array([0.25, 0.25, 0.25])
        self.horizon_color = horizon_color
        self.zenith_color = zenith_color
        self.floor_color = floor_color

    def get_color(self, ray_starts: np.array, ray_directions: np.array):
        zenith_weight = ray_directions[:, 1].copy()
        zenith_weight[ray_directions[:, 1]<0] = 0
        horizon_weight = 1 - ray_directions[:, 1]
        horizon_weight[ray_directions[:, 1]<0] = 0
        floor_weight = ray_directions[:, 1] < 0
        return (zenith_weight[:, None] * self.zenith_color[None, :] +
                horizon_weight[:, None] * self.horizon_color[None, :] +
                floor_weight[:, None] * self.floor_color[None, :])
    def get_color_torch(self, ray_starts: torch.Tensor, ray_directions: torch.Tensor):
        device = ray_directions.device
        zenith_weight = ray_directions[:, 1].clone()
        zenith_weight[ray_directions[:, 1]<0] = 0
        horizon_weight = 1 - ray_directions[:, 1]
        horizon_weight[ray_directions[:, 1]<0] = 0
        floor_weight = ray_directions[:, 1] < 0
        return (zenith_weight[:, None] * torch.Tensor(self.zenith_color[None, :]).to(device) +
                horizon_weight[:, None] * torch.Tensor(self.horizon_color[None, :]).to(device) +
                floor_weight[:, None] * torch.Tensor(self.floor_color[None, :]).to(device))
