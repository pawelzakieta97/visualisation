#version 330 core

// Interpolated values from the vertex shaders
in vec3 normal_worldspace;
in vec3 position_worldspace;
in vec3 cameraPos;
in vec2 UV;

// Ouput data
out vec3 color;

//uniform vec3 cameraPosition;
uniform vec3 lightPosition;
uniform vec3 lightColor;
//uniform vec3 objectDiffuse;
uniform vec3 objectReflectiveness;
uniform float objectGlossiness;
uniform vec3 cameraPosition;
uniform sampler2D myTextureSampler;
//uniform float ambient = 0.2;

void main(){

	vec3 nnormal_worldspace = normalize(normal_worldspace);
	vec3 c2p = position_worldspace - cameraPosition;
	c2p = normalize(c2p);
	vec3 p2l = lightPosition - position_worldspace;
	p2l = normalize(p2l);
	color = vec3(0,0,0);
	// AMBIENT
	float ambient=0.3;
	vec3 objectDiffuse = texture(myTextureSampler, UV).rgb;
	color += objectDiffuse * ambient;
	// DIFFUSE
	color += clamp(dot(nnormal_worldspace, p2l), 0, 1) * lightColor * objectDiffuse;
	// SPECULAR
	vec3 r = c2p - 2 * dot(nnormal_worldspace, c2p) * nnormal_worldspace;
//	r = -p2c;
	float specular_factor;
	float glossinessMultiplier = (1/(1.01 - objectGlossiness));
	if (dot(nnormal_worldspace, p2l) < 0) specular_factor = 0;
	else specular_factor = pow(clamp(dot(p2l, normalize(r)), 0, 1), glossinessMultiplier) * glossinessMultiplier * 0.2;

	color += specular_factor * lightColor * objectReflectiveness;
	}