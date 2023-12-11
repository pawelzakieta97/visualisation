#version 330
in vec3 fragmentColor;
 
void main(void){
  gl_FragColor = vec4(0.2,0.2,0.2,0);
  gl_FragColor = vec4(fragmentColor, 0);

}