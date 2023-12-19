#version 330 core
layout (location = 0) in vec3 vertexPosition_modelspace; // Input vertex

uniform mat4 MVP; // lightspace transformation
uniform mat4 objectTransformation; // Model transformation
out vec3 position_worldspace;

void main() {
    position_worldspace = vec3(objectTransformation * vec4(vertexPosition_modelspace, 1));
	gl_Position =  MVP * vec4(position_worldspace,1);
}