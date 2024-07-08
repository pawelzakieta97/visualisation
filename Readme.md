# Python 3D visualisation

3D visualisation engine based on OpenGL.

## Raytracing module
Opengl visualisation can be helpful for debugging other projects. 
To demonstrate, a ray tracing module has been added. 
It uses a AABB BVH to massively accelerate searching for closest ray-object intersection. 
This allows for efficient O(log(n)) rendering of complex meshes.
In order to traverse the BVH faster, it has been vectorized using numpy. 
It is possible to accelerate the process even further with pyTorch tensors.
![image](https://github.com/pawelzakieta97/visualisation/assets/28107745/fc95ad0a-6888-4aba-9f07-bfd3cab19255)

*2000x2000 image with 5k polygons took ~90 seconds including calculating the BVH*


![image](https://github.com/pawelzakieta97/visualisation/assets/28107745/736cfada-3b21-4be0-a7fb-f0f9f146729b)

*OpenGL visualization of the bvh used for the render*


![image](https://github.com/pawelzakieta97/visualisation/assets/28107745/a52474b2-9cdd-4c64-8ddb-7e51c8ce7f31)

*BVH traversal depth heatmap*

## Visualization features

![image](https://github.com/pawelzakieta97/visualisation/assets/28107745/642a8108-6e70-4904-af61-39da3c83a48a)
![image](https://github.com/pawelzakieta97/visualisation/assets/28107745/e898324a-ce98-4df3-b1ff-f5eb498583a8)

*Specualr highlights and shadows*

## Installation

`pip install -r requirements.txt`

### Troubleshooting
Known issues on Ubuntu
 - If you get
`Attempt to call an undefined function glutInit, check for bool(glutInit) before calling`
try
`sudo apt-get install freeglut3-dev`

 - If you get 
`Attempt to retrieve context when no valid context`
modify the condition https://github.com/mcfletch/pyopengl/blob/29b79e8966ba2930a5c44829b02dffc1ca600752/OpenGL/contextdata.py#L38
to omit the check for 0 value of context (for example change line 38 to `if context == 0 and False:`)

Known issues on Windows

 - If you get
`Attempt to call an undefined function glutInit, check for bool(glutInit) before calling`
Install PyOpenGL form downloaded whl according to your python version:
https://drive.google.com/drive/folders/1mz7faVsrp0e6IKCQh8MyZh-BcCqEGPwx
