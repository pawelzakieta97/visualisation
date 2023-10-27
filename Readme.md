# Python 3D visualisation

3D visualisation engine based on OpenGL.
![image](https://github.com/pawelzakieta97/visualisation/assets/28107745/e9b26b73-cd9f-4a4b-b5c8-231541489503)


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
