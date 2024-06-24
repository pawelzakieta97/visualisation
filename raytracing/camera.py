import numpy as np

from transformations import look_at


class Camera:
    def __init__(self, width=320, height=240, fov=np.pi / 2, position=None, yaw=0, pitch=0):
        if position is None:
            position = np.array([0, 0, 0])
        self.position = position
        self.M = look_at(position=position, yaw=yaw, pitch=pitch)
        self.fov = fov
        self.width = width
        self.height = height
        self.f = width / 2 * np.tan(fov/2)
        pass

    def get_rays(self, flatten=True):
        ray_dir_x, ray_dir_y = np.meshgrid(np.arange(-self.width//2, self.width//2) + 0.5,
                                           np.arange(-self.height//2, self.height//2) + 0.5)
        ray_dir_z = np.ones_like(ray_dir_x) * -self.f
        ray_dir = np.stack((ray_dir_x, ray_dir_y, ray_dir_z), axis=-1)
        ray_dir /= np.linalg.norm(ray_dir, axis=-1)[:, :, None]
        ray_dir = (self.M[:3, :3] @ ray_dir.reshape(-1,3).T).T.reshape(self.height, self.width, 3)

        ray_starts = np.zeros((self.height, self.width, 3))
        ray_starts = np.concatenate((ray_starts, np.ones((240, 320, 1))), axis=-1)
        ray_starts = (self.M @ ray_starts.reshape(-1,4).T).T.reshape(self.height, self.width, 4)[:,:,:3]
        if flatten:
            ray_starts = ray_starts.reshape(-1, 3)
            ray_dir = ray_dir.reshape(-1, 3)
        return ray_starts, ray_dir


if __name__ == '__main__':
    c = Camera(position=np.array([0,0,10]), yaw=np.pi/2)
    rays = c.get_rays()
    pass
