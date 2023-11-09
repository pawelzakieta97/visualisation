import numpy as np
import numba
from numba import jit

from models.particle_system import ParticleSystem


class Pendulum(ParticleSystem):
    def __init__(self, particles: np.array, substeps: int = 100, *args, **kwargs):
        particles = np.array(particles).astype(float)
        links = np.arange(particles.shape[0])
        links = np.hstack((links[:-1, None], links[1:, None]))
        super().__init__(particle_pos=particles, links=links, *args, **kwargs)
        self.prev_pos = particles.copy()
        self.velocities = np.zeros_like(particles).astype(float)
        self.masses = np.ones(particles.shape[0]).astype(float)
        self.static = np.zeros(particles.shape[0]).astype(bool)
        distances = self.particle_pos[self.links]
        self.distances = np.linalg.norm(distances[:, 1, :] - distances[:, 0, :], axis=1)
        self.substeps = substeps
        self.compliances = np.ones_like(self.links)
        self.update_compliances()

    def update_compliances(self):
        self.compliances = 1 / self.masses[self.links]
        self.compliances[self.static[self.links]] = 0
        self.compliances /= self.compliances.sum(axis=1)[:, None]

    def simulate(self, dt: float, g: np.array):
        g = np.array(g).astype(float)
        for substep in range(self.substeps):
            self.integrate(dt / self.substeps, g[None, :])
            # self.solve_parallel()
            # self.solve_serial()
            solve_distance_constraints(self.particle_pos, self.distances, self.compliances, self.links)
            self.update_velocities(dt / self.substeps)
        self.update_meshes()

    def simulate_fast(self, dt, g):
        forces = np.ones_like(self.particle_pos) * np.array(g).astype(float)[None, :]
        masses = np.ones_like(self.particle_pos) * self.masses[:, None]
        static = np.ones_like(self.particle_pos) * self.static[:, None]
        res = simulate(self.particle_pos,
                       self.velocities,
                       self.distances,
                       masses,
                       static,
                       self.compliances,
                       self.links, dt, self.substeps,
                       forces)
        self.particle_pos, self.velocities = res
        self.update_meshes()

    def integrate(self, dt, forces):
        self.velocities += forces * dt / self.masses[:, None] * (1 - self.static)[:, None]
        self.prev_pos = self.particle_pos.copy()
        self.particle_pos += self.velocities * dt * (1 - self.static)[:, None]

    def solve_parallel(self):
        deltas = self.particle_pos[self.links, :2]
        deltas = deltas[:, 1, :] - deltas[:, 0, :]
        current_distances = np.linalg.norm(deltas, axis=1)
        dirs = deltas / current_distances[:, None]
        differences = self.distances - current_distances
        self.particle_pos[self.links[:, 0], :2] -= dirs * differences[:, None] * self.compliances[:, 0, None] * 0.5
        self.particle_pos[self.links[:, 1], :2] += dirs * differences[:, None] * self.compliances[:, 1, None] * 0.5

    def solve_serial(self):
        for distance, compliance, (p1, p2) in zip(self.distances, self.compliances, self.links):
            delta = self.particle_pos[p2, :] - self.particle_pos[p1, :]
            current_distance = np.linalg.norm(delta)
            direction = delta / current_distance
            difference = distance - current_distance
            self.particle_pos[p1, :] -= direction * difference * compliance[0]
            self.particle_pos[p2, :] += direction * difference * compliance[1]

    def update_velocities(self, dt):
        self.velocities = (self.particle_pos - self.prev_pos) / dt


@jit(nopython=True)
def solve_distance_constraints(particle_pos, distances, compliances, links):
    for distance, compliance, (p1, p2) in zip(distances, compliances, links):
        delta = particle_pos[p2, :] - particle_pos[p1, :]
        current_distance = (delta[0] ** 2 + delta[1] ** 2 + delta[2] ** 2) ** 0.5
        direction = delta / current_distance
        difference = distance - current_distance
        particle_pos[p1, :] -= direction * difference * compliance[0]
        particle_pos[p2, :] += direction * difference * compliance[1]


@jit(nopython=True)
def simulate(particle_pos, velocities,
             distances, masses,
             static, compliances,
             links, dt,
             substeps, g):
    for substep in range(substeps):
        prev_pos = particle_pos.copy()
        integrate(particle_pos, velocities, masses, static, dt / substeps, g)
        solve_distance_constraints(particle_pos, distances, compliances, links)
        velocities = update_velocities(particle_pos, prev_pos, dt / substeps)
    return particle_pos, velocities


@jit(nopython=True)
def integrate(particle_pos, velocities, masses, static, dt, forces):
    velocities += forces * dt / masses
    particle_pos += velocities * dt * (1 - static)


@jit(nopython=True)
def update_velocities(particle_pos, prev_pos, dt):
    return (particle_pos - prev_pos) / dt
