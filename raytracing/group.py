import numpy as np

from raytracing.sphere import Sphere
from raytracing.renderable import Renderable


class Group(Renderable):
    def __init__(self, elements):
        self.elements = elements
        self._bb = None

    def get_bb(self):
        if self._bb is None:
            bbs = np.array([element.get_bb() for element in self.elements])
            self._bb = np.stack((bbs[:,0,:].min(axis=0), bbs[:,1,:].max(axis=0)))
        return self._bb

    def get_elements(self):
        """
        Returns leaf elements
        """
        elements = []
        for element in self.elements:
            if isinstance(element, Group):
                elements += element.get_elements()
            else:
                elements.append(element)
        return elements

    def get_all_elements(self):
        """
        Returns all leaf and node elements
        """
        elements = [self]
        for element in self.elements:
            if isinstance(element, Group):
                elements += element.get_all_elements()
            else:
                elements.append(element)
        return elements

    def serialize(self):
        all_elements = self.get_all_elements()
        id_to_element = {}
        element_to_id = {}
        for element in all_elements:
            if type(element) not in element_to_id:
                element_to_id[type(element)] = {}
                id_to_element[type(element)] = {}
            element_id = len(element_to_id[type(element)])
            element_to_id[type(element)][element] = element_id
            id_to_element[type(element)][element_id] = element

        group_child_types = [None] * len(id_to_element[Group])
        group_child_indexes = [None] * len(id_to_element[Group])
        group_bbs = [None] * len(id_to_element[Group])

        children_data = {}

        for element_type in id_to_element.keys():
            if element_type == Group:
                for group_id, group in id_to_element[Group].items():
                    group_child_types[group_id] = [type(element) for element in group.elements]
                    group_child_indexes[group_id] = [element_to_id[type(element)][element] for element in
                                                     group.elements]
                    group_bbs[group_id] = group.get_bb()
            else:
                if element_type not in children_data:
                    children_data[element_type] = [None] * len(id_to_element[element_type])
                for leaf_id, leaf in id_to_element[element_type].items():
                    children_data[element_type][leaf_id] = leaf.serialize()

        group_child_indexes_size = max([len(e) for e in group_child_indexes])
        for group_child_index, group_child_type in zip(group_child_indexes, group_child_types):
            group_child_index += [-1] * (group_child_indexes_size - len(group_child_index))
            group_child_type += [-1] * (group_child_indexes_size - len(group_child_type))
        return group_child_types, group_child_indexes, group_bbs, children_data

    def get_bbs(self):
        elements = [self]
        bbs = []
        while elements:
            level_bbs = []
            new_elements = []
            for element in elements:
                if not isinstance(element, Group):
                    continue
                bb = element.get_bb()
                level_bbs.append(bb)
                new_elements += element.elements
            elements = new_elements
            bbs.append(level_bbs)
        return bbs

if __name__ == '__main__':
    spheres = [Sphere(radius=2), Sphere(np.array([2,0,0]))]
    group = Group(spheres)
    group.get_bb()