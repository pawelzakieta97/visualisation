from abc import ABC, abstractmethod

import numpy as np
#
# from group import Group


class Renderable(ABC):
    @abstractmethod
    def get_bb(self):
        pass
