from dataclasses import dataclass

import numpy as np


@dataclass
class Material:
    diffuse: np.array = np.array([0.5, 0.5, 0.5])
    reflectiveness: np.array = np.array([1, 1, 1])
    glossiness: float = 0.5
