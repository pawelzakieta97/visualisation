from typing import Iterable

import numpy as np

from models.compound_mesh import CompoundMesh
from models.mesh import Mesh
from models.multi_mesh import MultiMesh
from models.sphere import Sphere
from models.wireframe import Wireframe


class ParticleSystem(CompoundMesh):
    def __init__(self, particle_pos: np.array=None,
                 particle_count=None,
                 links=None, mode_2d=True, reference_mesh: Mesh = None):
        if particle_pos is None:
            if particle_count is None:
                particle_count = 100
            ndims = 2 if mode_2d else 3
            particle_pos = np.random.random((particle_count, 3))
            if mode_2d:
                particle_pos[:, 2] = 0
        self.particles = particle_pos
        self.particle_count = self.particles.shape[0]
        if links is None:
            links = np.array([])
        self.links = links
        self.reference_mesh = reference_mesh
        self.particles_mesh = None
        self.links_mesh = None
        self.update_meshes()

    def get_reference_mesh(self):
        if self.reference_mesh is None:
            self.reference_mesh = Sphere(radius=1/(self.particle_count**0.5)/10, vert_count=14)
        return self.reference_mesh

    def update_meshes(self):
        if self.particles_mesh is None:
            self.particles_mesh = MultiMesh(self.get_reference_mesh(), count=self.particle_count)
        self.particles_mesh.set_positions(self.particles)
        if self.links_mesh is None and self.links:
            lines = self.particles[self.links].reshape(-1, 3)
            self.links_mesh = Wireframe(lines, colors=np.ones_like(lines) * 0.8)

    def get_meshes(self) -> Iterable[Mesh]:
        meshes = [self.particles_mesh, self.links_mesh]
        return [m for m in meshes if m is not None]
