# Python 3D visualisation

3D visualisation engine based on OpenGL.
![image](https://github.com/pawelzakieta97/visualisation/assets/28107745/e9b26b73-cd9f-4a4b-b5c8-231541489503)
![image](https://github.com/pawelzakieta97/visualisation/assets/28107745/309c7ff3-bbe5-4003-a17e-d584377a0671)
![image](https://github.com/pawelzakieta97/visualisation/assets/28107745/642a8108-6e70-4904-af61-39da3c83a48a)
![image](https://github.com/pawelzakieta97/visualisation/assets/28107745/e898324a-ce98-4df3-b1ff-f5eb498583a8)


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

## Raytracing module
Opengl visualisation can be helpful for debugging other projects. 
To demonstrate, a ray tracing module has been added. 
It uses a AABB BVH to massively accelerate searching for closest ray-object intersection. 
This allows for efficient (O(log(n))) rendering of complex meshes
![image](https://github.com/pawelzakieta97/visualisation/assets/28107745/fc95ad0a-6888-4aba-9f07-bfd3cab19255)


