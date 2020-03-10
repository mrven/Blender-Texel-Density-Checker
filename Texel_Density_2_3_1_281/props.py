class TD_Addon_Props(PropertyGroup):
	uv_space: StringProperty(
		name="",
		description="wasting of uv space",
		default="0")
	
	density: StringProperty(
		name="",
		description="Texel Density",
		default="0")
	
	density_set: StringProperty(
		name="",
		description="Texel Density",
		default="0")
	
	tex_size = (('0','512px',''),('1','1024px',''),('2','2048px',''),('3','4096px',''), ('4','Custom',''))
	texture_size: EnumProperty(name="", items = tex_size, update = Change_Texture_Size)
	
	selected_faces: BoolProperty(
		name="Selected Faces",
		description="Operate only on selected faces",
		default = True)
	
	custom_width: StringProperty(
		name="",
		description="Custom Width",
		default="1024",
		update = Change_Texture_Size)
	
	custom_height: StringProperty(
		name="",
		description="Custom Height",
		default="1024",
		update = Change_Texture_Size)
	
	units_list = (('0','px/cm',''),('1','px/m',''), ('2','px/in',''), ('3','px/ft',''))
	units: EnumProperty(name="", items = units_list, update = Change_Units)
	
	select_td_threshold: StringProperty(
		name="",
		description="Select Threshold",
		default="0.1")
	
	set_method_list = (('0','Each',''),('1','Average',''))
	set_method: EnumProperty(name="", items = set_method_list)

	checker_method_list = (('0','Replace',''), ('1','Store and Replace',''))
	checker_method: EnumProperty(name="", items = checker_method_list)

	checker_type_list = (('COLOR_GRID','Color Grid',''),('UV_GRID','UV Grid',''))
	checker_type: EnumProperty(name="", items = checker_type_list, update = Change_Texture_Type)

	bake_vc_min_td: StringProperty(
		name="",
		description="Min TD",
		default="0.64",
		update = Filter_Bake_VC_Min_TD)

	bake_vc_max_td: StringProperty(
		name="",
		description="Max TD",
		default="10.24",
		update = Filter_Bake_VC_Max_TD)

	bake_vc_show_gradient: BoolProperty(
		name="Show Gradient",
		description="Show Gradient in Viewport",
		default = False,
		update = Show_Gradient)