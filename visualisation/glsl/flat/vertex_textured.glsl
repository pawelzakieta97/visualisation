#version 330 core

// Input vertex data, different for all executions of this shader.
layout(location = 0) in vec3 vertexPosition_modelspace;
layout(location = 1) in vec2 vertexUV;

out vec3 position_worldspace;
out vec2 UV;
//out vec3 cameraPosition;
// Values that stay constant for the whole mesh.
uniform mat4 MVP;
uniform mat4 objectTransformation;
void main(){	

	position_worldspace = vec3(objectTransformation * vec4(vertexPosition_modelspace, 1));
	gl_Position =  MVP * vec4(position_worldspace,1);
	UV = vertexUV;
}