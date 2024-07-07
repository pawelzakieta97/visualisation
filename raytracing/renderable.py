from abc import ABC, abstractmethod


INF_DISTANCE = 9999999


class Renderable(ABC):
    @abstractmethod
    def get_bb(self):
        pass

    _type_id = {}

    @classmethod
    def get_type_id(cls):
        if cls not in Renderable._type_id:
            Renderable._type_id[cls] = len(Renderable._type_id)
        return Renderable._type_id[cls]


