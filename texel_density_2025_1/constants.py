# Asset Names
TD_VC_NAME = 'td_vis'
TD_MATERIAL_NAME = 'TD_Checker'


# URLs
TD_DOC_URL = 'https://github.com/mrven/Blender-Texel-Density-Checker#readme'
TD_REPORT_URL = 'https://github.com/mrven/Blender-Texel-Density-Checker/issues'


# Enums/Dictionaries/Lists
TD_PRESET_VALUES = {
    # px/cm
    '0': [
        ["20.48", "10.24", "5.12"],
        ["2.56", "1.28", "0.64"]
    ],
    #px/m
    '1': [
        ["2048", "1024", "512"],
        ["256", "128", "64"]
    ],
    #px/in
    '2': [
        ["52.019", "26.01", "13.005"],
        ["6.502", "3.251", "1.626"]
    ],
    # px/ft
    '3': [
        ["624.23", "312.115", "156.058"],
        ["78.029", "39.014", "19.507"]
    ]
}

TD_ANCHOR_ORIGIN_ITEMS = (('SELECTION', 'Selection', ''),
                          ('UV_CENTER', 'UV Center', ''),
                          ('UV_LEFT_BOTTOM', 'UV Left Bottom', ''),
                          ('UV_LEFT_TOP', 'UV Left Top', ''),
                          ('UV_RIGHT_BOTTOM', 'UV Right Bottom', ''),
                          ('UV_RIGHT_TOP', 'UV Right Top', ''),
                          ('2D_CURSOR', '2D Cursor', ''))

TD_TEXTURE_SIZE_ITEMS = (('512', '512px', ''),
                        ('1024', '1024px', ''),
                        ('2048', '2048px', ''),
                        ('4096', '4096px', ''),
                        ('CUSTOM', 'Custom', ''))

TD_UNITS_ITEMS = (('0', 'px/cm', ''),
				  ('1', 'px/m', ''),
				  ('2', 'px/in', ''),
				  ('3', 'px/ft', ''))

TD_SET_METHOD_ITEMS = (('EACH', 'Each', ''),
                       ('AVERAGE', 'Average', ''))

TD_CHECKER_METHOD_ITEMS = (('REPLACE', 'Replace', ''),
                           ('STORE', 'Store and Replace', ''))

TD_CHECKER_TYPE_ITEMS = (('COLOR_GRID', 'Color Grid', ''),
                         ('UV_GRID', 'UV Grid', ''))

TD_BAKE_VC_MODE_ITEMS = (('TD_FACES_TO_VC', 'Texel (by Face)', ''),
						 ('TD_ISLANDS_TO_VC', 'Texel (by Island)', ''),
						 ('UV_ISLANDS_TO_VC', 'UV Islands', ''),
						 ('UV_SPACE_TO_VC', 'UV Space (%)', ''),
						 ('DISTORTION', 'UV Distortion', ''))

TD_BAKE_UV_ISLANDS_MODE_ITEMS = (('ISLAND', 'By Island', ''),
                                 ('OVERLAP', 'By Overlap', ''))

TD_SELECT_MODE_ITEMS = (('FACES_BY_TD', 'Faces (by Texel)', ''),
                        ('ISLANDS_BY_TD', 'Islands (by Texel)', ''),
						('ISLANDS_BY_SPACE', 'Islands (by UV Space)', ''))

TD_SELECT_TYPE_ITEMS = (('EQUAL', 'Equal To', ''),
                        ('LESS', 'Less Than', ''),
                        ('GREATER', 'Greater Than', ''))


# Shaders
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