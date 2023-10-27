from dataclasses import dataclass

import numpy as np


@dataclass
class Light:
    position: np.array
    color: np.array
