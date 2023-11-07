import numpy as np

from models.particle_system import ParticleSystem


class Pendulum(ParticleSystem):
    def __init__(self, particles: np.array, substeps: int = 10):
        particles = np.array(particles).astype(float)
        links = np.arange(particles.shape[0])
        links = np.hstack((links[:-1, None], links[1:, None]))
        super().__init__(particle_pos=particles, links=links)
        self.prev_pos = particles.copy()
        self.velocities = np.zeros_like(particles).astype(float)
        self.masses = np.ones(particles.shape[0]).astype(float)
        self.static = np.zeros(particles.shape[0]).astype(bool)
        distances = self.particles[self.links]
        self.distances = np.linalg.norm(distances[:, 1, :] - distances[:, 0, :], axis=1)
        self.substeps = substeps
        self.compliances = np.ones_like(self.links)
        self.update_compliances()

    def update_compliances(self):
        self.compliances = 1 / self.masses[self.links]
        self.compliances[self.static[self.links]] = 0
        self.compliances /= self.compliances.sum(axis=1) [:, None]

    def simulate(self, dt: float, g: np.array):
        g = np.array(g).astype(float)
        for substep in range(self.substeps):
            self.integrate(dt/self.substeps, g[None, :])
            self.solve_parallel()
            self.update_velocities(dt/self.substeps)
        self.update_meshes()

    def integrate(self, dt, forces):
        self.velocities += forces * dt / self.masses[:, None] * (1 - self.static)[:, None]
        self.prev_pos = self.particles.copy()
        self.particles += self.velocities * dt * (1 - self.static)[:, None]

    def solve_parallel(self):
        deltas = self.particles[self.links, :2]
        deltas = deltas[:, 1, :] - deltas[:, 0, :]
        current_distances = np.linalg.norm(deltas, axis=1)
        differences = self.distances - current_distances
        self.particles[self.links[:, 0], :2] -= deltas * differences[:, None] * self.compliances[:, 0, None] * 0.5
        self.particles[self.links[:, 1], :2] += deltas * differences[:, None] * self.compliances[:, 1, None] * 0.5
        pass

    def update_velocities(self, dt):
        self.velocities = (self.particles - self.prev_pos) / dt
