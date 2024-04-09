#version 330 core

// Input vertex data, different for all executions of this shader.
layout(location = 0) in vec3 vertexPosition_modelspace;
layout(location = 1) in vec3 vertexNormal_modelspace;

// Output data ; will be interpolated for each fragment.
out vec3 normal_worldspace;
out vec3 position_worldspace;
//out vec3 cameraPosition;
// Values that stay constant for the whole mesh.
uniform mat4 projectionView;
uniform mat4 objectTransformation;
uniform float ambient = 0.1;
void main(){	

	position_worldspace = vec3(objectTransformation * vec4(vertexPosition_modelspace, 1));
	normal_worldspace = mat3(objectTransformation) * vertexNormal_modelspace;
	gl_Position =  projectionView * vec4(position_worldspace,1);
}