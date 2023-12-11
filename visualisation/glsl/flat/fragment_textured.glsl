#version 330 core

in vec2 UV;

// Ouput data
out vec3 color;

uniform sampler2D myTextureSampler;
//uniform float ambient = 0.2;

void main(){
	color = texture(myTextureSampler, UV).rgb;
	color[0] = UV[0];
	color[1] = UV[1];
	}