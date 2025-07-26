VERTEX_SHADER_TEXT_3_0 = '''
	in vec2 position;
	out vec3 pos;

	void main()
	{
		pos = vec3(position, 0.0f);
		gl_Position = vec4(position, 0.0f, 1.0f);
	}
	'''

FRAGMENT_SHADER_TEXT_3_0 = '''
	uniform float pos_x_min;
	uniform float pos_x_max;

	in vec3 pos;

	void main()
	{
		vec4 b = vec4(0.0f, 0.0f, 1.0f, 1.0f);
		vec4 c = vec4(0.0f, 1.0f, 1.0f, 1.0f);
		vec4 g = vec4(0.0f, 1.0f, 0.0f, 1.0f);
		vec4 y = vec4(1.0f, 1.0f, 0.0f, 1.0f);
		vec4 r = vec4(1.0f, 0.0f, 0.0f, 1.0f);

		float pos_x_25 = (pos_x_max - pos_x_min) * 0.25 + pos_x_min;
		float pos_x_50 = (pos_x_max - pos_x_min) * 0.5 + pos_x_min;
		float pos_x_75 = (pos_x_max - pos_x_min) * 0.75 + pos_x_min;

		float blendColor1 = (pos.x - pos_x_min)/(pos_x_25 - pos_x_min);
		float blendColor2 = (pos.x - pos_x_25)/(pos_x_50 - pos_x_25);
		float blendColor3 = (pos.x - pos_x_50)/(pos_x_75 - pos_x_50);
		float blendColor4 = (pos.x - pos_x_75)/(pos_x_max - pos_x_75);

		gl_FragColor = (c * blendColor1 + b * (1 - blendColor1)) * step(pos.x, pos_x_25) +
						(g * blendColor2 + c * (1 - blendColor2)) * step(pos.x, pos_x_50) * step(pos_x_25, pos.x) +
						(y * blendColor3 + g * (1 - blendColor3)) * step(pos.x, pos_x_75) * step(pos_x_50, pos.x) +
						(r * blendColor4 + y * (1 - blendColor4)) * step(pos.x, pos_x_max) * step(pos_x_75, pos.x);
	}
	'''

VERTEX_SHADER_TEXT_3_3 = '''
	//in vec2 position;
	//out vec3 pos;

	void main()
	{
		pos = vec3(position, 0.0f);
		gl_Position = vec4(position, 0.0f, 1.0f);
	}
	'''

FRAGMENT_SHADER_TEXT_3_3 = '''
	//uniform float pos_x_min;
	//uniform float pos_x_max;

	//in vec3 pos;

	void main()
	{
		// Pure Colors
		vec4 b = vec4(0.0f, 0.0f, 1.0f, 1.0f);	// Blue	0%
		vec4 c = vec4(0.0f, 1.0f, 1.0f, 1.0f);	// Cyan	25%
		vec4 g = vec4(0.0f, 1.0f, 0.0f, 1.0f);	// Green	50%
		vec4 y = vec4(1.0f, 1.0f, 0.0f, 1.0f);	// Yellow	75%
		vec4 r = vec4(1.0f, 0.0f, 0.0f, 1.0f);	// Red	100%

		// Screen Space Coordinates for Intermediate Pure Colors
		float pos_x_25 = (pos_x_max - pos_x_min) * 0.25 + pos_x_min;
		float pos_x_50 = (pos_x_max - pos_x_min) * 0.5 + pos_x_min;
		float pos_x_75 = (pos_x_max - pos_x_min) * 0.75 + pos_x_min;

		// Intermediate Blend Values (0% - 25% => 0 - 1, 25% - 50% => 0 - 1, etc.)
		float blendColor1 = (pos.x - pos_x_min)/(pos_x_25 - pos_x_min);
		float blendColor2 = (pos.x - pos_x_25)/(pos_x_50 - pos_x_25);
		float blendColor3 = (pos.x - pos_x_50)/(pos_x_75 - pos_x_50);
		float blendColor4 = (pos.x - pos_x_75)/(pos_x_max - pos_x_75);

		// Calculate Final Colors - Pure Colors and Blends between them 
		FragColor = (c * blendColor1 + b * (1 - blendColor1)) * step(pos.x, pos_x_25) +
						(g * blendColor2 + c * (1 - blendColor2)) * step(pos.x, pos_x_50) * step(pos_x_25, pos.x) +
						(y * blendColor3 + g * (1 - blendColor3)) * step(pos.x, pos_x_75) * step(pos_x_50, pos.x) +
						(r * blendColor4 + y * (1 - blendColor4)) * step(pos.x, pos_x_max) * step(pos_x_75, pos.x);
	}
	'''