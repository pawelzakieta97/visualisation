#version 330 core

// Interpolated values from the vertex shaders
in vec3 normal_worldspace;
in vec3 position_worldspace;
in vec2 UV;

// Ouput data
out vec3 color;

//uniform vec3 cameraPosition;
uniform vec3 lightPosition;
uniform vec3 lightColor;
uniform vec3 objectDiffuse;
uniform vec3 objectReflectiveness;
uniform float objectGlossiness;
uniform vec3 cameraPosition;
uniform sampler2D diffuseSampler;
uniform sampler2D reflectivenessSampler;
uniform sampler2D glossinessSampler;
uniform sampler2D depthSampler;
uniform mat4 lightTransformation;
//uniform float ambient = 0.2;

void main(){

	vec3 nnormal_worldspace = normalize(normal_worldspace);
	vec3 p2c = cameraPosition - position_worldspace;
	vec3 c2p = position_worldspace - cameraPosition;
	p2c = normalize(p2c);
	c2p = normalize(c2p);
	vec3 p2l = lightPosition - position_worldspace;
	p2l = normalize(p2l);
	color = vec3(0,0,0);
	// AMBIENT
	float ambient=0.3;

	// use texture if diffuse/reflectiveness/glossiness negative
	vec3 diffuse = objectDiffuse;
	vec3 reflectiveness = objectReflectiveness;
	float glossiness = objectGlossiness;
	if (diffuse[0] < 0) diffuse = texture(diffuseSampler, UV).rgb;
	float depth = texture(depthSampler, UV).r;
	if (reflectiveness[0] < 0) reflectiveness = texture(reflectivenessSampler, UV).rgb;
	if (glossiness < 0) glossiness = texture(glossinessSampler, UV).r;

	color += diffuse * ambient;
	// DIFFUSE

	vec4 pos_lightspace = lightTransformation * vec4(position_worldspace, 1);
	vec4 pos_lightspace_scaled = pos_lightspace/pos_lightspace[3]/2 + 0.5;
	if ((pos_lightspace_scaled[0] > 0) &&
		(pos_lightspace_scaled[0] < 1) &&
		(pos_lightspace_scaled[1] > 0) &&
		(pos_lightspace_scaled[1] < 1)){
			float reference_distance = texture(depthSampler, vec2(pos_lightspace_scaled[0], pos_lightspace_scaled[1])).r;
			if (reference_distance < pos_lightspace_scaled[2] - 0.001) return;
	}


	color += clamp(dot(nnormal_worldspace, p2l), 0, 1) * lightColor * diffuse;
	// SPECULAR
	vec3 r = c2p - 2 * dot(nnormal_worldspace, c2p) * nnormal_worldspace;
	r = -p2l + 2 * nnormal_worldspace * dot(nnormal_worldspace, p2l);
//	r = -p2c;
	float specular_factor;
	float glossinessMultiplier = (1/(1.001 - glossiness));
	if (dot(nnormal_worldspace, p2l) < 0) specular_factor = 0;
	else specular_factor = pow(clamp(dot(p2c, normalize(r)), 0, 1), glossinessMultiplier);

	color += specular_factor * lightColor * reflectiveness;

	//volumetric
//	float norm = length(cameraPosition - position_worldspace);
//	float resolution = 0.1;
//	vec3 p = cameraPosition;
//	float distance = 0;
//	float max_distance = min(100, norm);
//	while (distance < norm){
//		distance += resolution;
//		p += c2p * resolution;
//		vec4 pos_lightspace = lightTransformation * vec4(p, 1);
//		vec4 pos_lightspace_scaled = pos_lightspace/pos_lightspace[3]/2 + 0.5;
//		if ((pos_lightspace_scaled[0] > 0) &&
//			(pos_lightspace_scaled[0] < 1) &&
//			(pos_lightspace_scaled[1] > 0) &&
//			(pos_lightspace_scaled[1] < 1)){
//				float reference_distance = texture(depthSampler, vec2(pos_lightspace_scaled[0], pos_lightspace_scaled[1])).r;
//				if (reference_distance < pos_lightspace_scaled[2] - 0.001) continue;
//			else {
//					color = color * 0.9 + 0.08;
//				}
//
//		}
//	}

	// reinhardt epxosure
//	color = 1 / (1 + 1/color);

	}