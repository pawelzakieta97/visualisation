from visualisation.renderable import Renderable

from PIL import Image
import numpy as np

from visualisation.texture import Texture

if __name__ == '__main__':
    image_data = np.array(Image.open('../resources/lena.png'))
    t = Texture(image_data)
    pass