import numpy as np


class ParticleSystem:
    def __init__(self, particle_pos: np.array=None,
                 particle_count=100,
                 links=None, mode_2d=True):
        if particle_pos is None:
            ndims = 2 if mode_2d else 3
            particle_pos = np.random.random((particle_count, ndims))
        self.particles = particle_pos
        if links is None:
            links = np.array([])
        self.links = links
        self.particle_mesh = None
        self.links_mesh = None
