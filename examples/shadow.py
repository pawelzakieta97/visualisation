import numpy as np

from PIL import Image
from models.mesh import Mesh
from models.multi_mesh import merge_meshes
from models.primitives.cube import Cube
from models.primitives.sphere import Sphere
from visualisation.material import Material
from visualisation.meshViewer import MeshViewWindow
from transformations import levels, get_translation_matrix

if __name__ == "__main__":
    win = MeshViewWindow(add_floorgrid=False, orthographic=False, target_fps=60)
    win.light.cast_shadows = True
    win.light.position = np.array([0.1, 4, 0])
    image_data = np.array(Image.open('../resources/dirt.jpg'))
    plane = Mesh(vertices=np.array([[-1, 0, -1],
                                    [-1, 0, 1],
                                    [1, 0, 1],
                                    [1, 0, -1]]) * 10,
                 triangle_indices=np.array([[0, 1, 2], [2, 3, 0]]),
                 uv=np.array([[0, 0],
                              [1, 0],
                              [1, 1],
                              [0, 1]]))
    sphere = Sphere(smoothness=4, init_uv=True)

    # merged_cubes = merge_meshes(cubes, as_mesh=True)
    # cube_obj = win.add_object(merged_cubes)
    sphere.transform(get_translation_matrix(dy=2, dx=0))
    plane = win.add_object(plane)
    sphere_obj = win.add_object(sphere)

    glossiness = levels(image_data.mean(axis=2), low=0.1, high=1)
    diffuse = levels(image_data, high=0.5)
    reflectiveness = levels(image_data, low=0, high=0.4)
    plane.material = Material(diffuse=diffuse,
                              reflectiveness=reflectiveness,
                              glossiness=glossiness
                              )
    sphere_obj.material = Material(diffuse=diffuse,
                              reflectiveness=reflectiveness,
                              glossiness=glossiness
                              )
    cubes = []
    for i in range(500):
        cube = Cube()
        cube.scale(scale=np.random.random(3))
        cube.set_position(x=np.random.random() * 20 - 10, z=np.random.random() * 20 - 10)
        cubes.append(cube)
        cube_obj = win.add_object(cube)
        cube_obj.material = plane.material

    def tick():
        tick.i += 1
        sphere.set_position(position=[2 * np.cos(tick.i / 20),
                                      2,
                                      2 * np.sin(tick.i / 20)])


    tick.i = 0
    win.run(tick)
