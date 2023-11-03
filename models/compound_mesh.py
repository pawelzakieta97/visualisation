from typing import Iterable

from models.mesh import Mesh


class CompoundMesh:
    def get_meshes(self) -> Iterable[Mesh]:
        raise NotImplemented