#version 330 core

// Interpolated values from the vertex shaders
in vec3 fragmentColor;
in vec3 normal_worldspace;
in vec3 position_worldspace;
in vec3 cameraPositionWorldspace;

// Ouput data
out vec3 color;

uniform vec3 cameraPosition;
uniform vec3 lightPosition;
uniform vec3 lightColor;
uniform vec3 objectDiffuse;
uniform vec3 objectReflectiveness;
uniform float objectGlossiness;
uniform float ambient = 0.1;

void main(){

	// Output color = color specified in the vertex shader, 
	// interpolated between all 3 surrounding vertices
	color = fragmentColor;
//	color = normal_worldspace;
//	vec3 p2c = cameraPositionWorldspace - position_worldspace;
//	color = vec3(0,0,0);
//	color = fragmentColor * clamp(dot(normal_worldspace, normalize(p2c)), 0, 1);
//	color = (fragmentColor * clamp(dot(normal_worldspace, normalize(p2c)), 0, 1) + objectDiffuse)/2;
//	color = cameraPositionWorldspace;
//	color = (objectDiffuse + lightColor)/2;

}