#version 330 core

// Interpolated values from the vertex shaders
in vec3 normal_worldspace;
in vec3 position_worldspace;
in vec3 objectDiffuse;

// Ouput data
out vec3 color;

//uniform vec3 cameraPosition;
uniform vec3 lightPosition;
uniform vec3 lightColor;
//uniform vec3 objectDiffuse;
uniform vec3 objectReflectiveness;
uniform float objectGlossiness;
uniform vec3 cameraPosition;
//uniform float ambient = 0.2;

void main(){

	color = objectDiffuse;
}