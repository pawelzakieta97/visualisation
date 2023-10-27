#version 330 core

// Input vertex data, different for all executions of this shader.
layout(location = 0) in vec3 vertexPosition_modelspace;
layout(location = 1) in vec3 vertexColor;
layout(location = 2) in vec3 vertexNormal_modelspace;

// Output data ; will be interpolated for each fragment.
out vec3 fragmentColor;
out vec3 normal_worldspace;
out vec3 position_worldspace;
out vec3 cameraPositionWorldspace;
//out vec3 cameraPosition;
// Values that stay constant for the whole mesh.
uniform mat4 MVP;
uniform mat4 cameraTransformation;
uniform vec3 cameraPosition;
uniform mat4 objectTransformation;
uniform vec3 lightPosition;
uniform vec3 lightColor;
uniform vec3 objectDiffuse;
uniform vec3 objectReflectiveness;
uniform float objectGlossiness;
uniform float ambient = 0.1;
void main(){	

	// Output position of the vertex, in clip space : MVP * position
	position_worldspace = vec3(objectTransformation * vec4(vertexPosition_modelspace, 1));
	normal_worldspace = mat3(objectTransformation) * vertexNormal_modelspace;
//	normal_worldspace = vertexNormal_modelspace;
//	position_worldspace = vertexPosition_modelspace + vec3(-5,0,0);

	gl_Position =  MVP * vec4(position_worldspace,1);

	// The color of each vertex will be interpolated
	// to produce the color of each fragment
	fragmentColor = vertexColor;
	vec3 p2l = lightPosition - position_worldspace;
	fragmentColor = objectDiffuse * clamp(dot(normal_worldspace, normalize(p2l)), 0, 1) + ambient;
}