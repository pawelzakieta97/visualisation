import numpy as np

from models.particle_system import ParticleSystem


class Pendulum(ParticleSystem):
    def __init__(self, particles: np.array, substeps: int = 10):
        particles = np.array(particles).astype(float)
        links = np.arange(particles.shape[0])
        links = np.hstack((links[:-1, None], links[1:, None]))
        super().__init__(particle_pos=particles, links=links)
        self.velocities = np.zeros_like(particles).astype(float)
        self.masses = np.ones(particles.shape[0]).astype(float)
        distances = self.particles[self.links]
        self.distances = np.linalg.norm(distances[:, 1, :] - distances[:, 0, :], axis=1)
        self.substeps = substeps

    def simulate(self, dt: float, g: np.array):
        g = np.array(g).astype(float)
        for substep in range(self.substeps):
            self.integrate(dt/self.substeps, g[None, :])
        self.update_meshes()

    def integrate(self, dt, forces):
        self.particles += self.velocities * dt
        self.velocities += forces * dt / self.masses[:, None]

    def solve(self):
        distances = self.particles[self.links]
        self.distances = np.linalg.norm(distances[:, 1, :] - distances[:, 0, :], axis=1)