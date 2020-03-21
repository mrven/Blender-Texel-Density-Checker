import bpy


# Panel in 3D View
class VIEW3D_PT_texel_density_checker(bpy.types.Panel):
	bl_label = "Texel Density Checker"
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_category = "Texel Density"
	#bl_options = {'DEFAULT_CLOSED'}

	@classmethod
	def poll(self, context):
		return (context.object is not None)

	def draw(self, context):
		td = context.scene.td
		
		if context.active_object.type == 'MESH' and len(context.active_object.data.uv_layers) > 0:
			layout = self.layout

			#Split row
			row = layout.row()
			c = row.column()
			row = c.row()
			split = row.split(factor=0.5, align=True)
			c = split.column()
			c.label(text="Units:")
			split = split.split()
			c = split.column()
			c.prop(td, 'units', expand=False)
			#----

			#Split row
			row = layout.row()
			c = row.column()
			row = c.row()
			split = row.split(factor=0.5, align=True)
			c = split.column()
			c.label(text="Texture Size:")
			split = split.split()
			c = split.column()
			c.prop(td, 'texture_size', expand=False)
			#----

			if td.texture_size == '4':
				row = layout.row()
				c = row.column()
				row = c.row()
				split = row.split(factor=0.35, align=True)
				c = split.column()
				c.label(text="Width:")
				split = split.split(factor=0.65, align=True)
				c = split.column()
				c.prop(td, "custom_width")
				split = split.split()
				c = split.column()
				c.label(text="px")

				row = layout.row()
				c = row.column()
				row = c.row()
				split = row.split(factor=0.35, align=True)
				c = split.column()
				c.label(text="Height:")
				split = split.split(factor=0.65, align=True)
				c = split.column()
				c.prop(td, "custom_height")
				split = split.split()
				c = split.column()
				c.label(text="px")
		

			layout.separator()
			layout.separator()

			#Split row
			row = layout.row()
			c = row.column()
			row = c.row()
			split = row.split(factor=0.5, align=True)
			c = split.column()
			c.label(text="Checker Method:")
			split = split.split()
			c = split.column()
			c.prop(td, 'checker_method', expand=False)
			#----

			#Split row
			row = layout.row()
			c = row.column()
			row = c.row()
			split = row.split(factor=0.5, align=True)
			c = split.column()
			c.label(text="Checker Type:")
			split = split.split()
			c = split.column()
			c.prop(td, 'checker_type', expand=False)
			#----

			row = layout.row()
			row.operator("object.checker_assign", text="Assign Checker Material")

			row = layout.row()
			row.operator("object.checker_restore", text="Restore Materials")

			row = layout.row()
			row.operator("object.clear_checker_face_maps", text="Clear Stored Face Maps")

			layout.separator()
			layout.separator()

			if context.object.mode == 'EDIT':
				layout.separator()
				layout.prop(td, "selected_faces", text="Selected Faces")

			#Split row
			row = layout.row()
			c = row.column()
			row = c.row()
			split = row.split(factor=0.5, align=True)
			c = split.column()
			c.label(text="UV Space:")
			split = split.split()
			c = split.column()
			c.label(text=td.uv_space)
			#----
			
			cur_units = "px/cm"
			if td.units == '0':
				cur_units = "px/cm"
			if td.units == '1':
				cur_units = "px/m"
			if td.units == '2':
				cur_units = "px/in"
			if td.units == '3':
				cur_units = "px/ft"

			#Split row
			row = layout.row()
			c = row.column()
			row = c.row()
			split = row.split(factor=0.4, align=True)
			c = split.column()
			c.label(text="Density:")
			split = split.split()
			c = split.column()
			c.label(text=td.density + " " + cur_units)
			#----

			layout.operator("object.texel_density_check", text="Calculate TD")
			layout.operator("object.calculate_to_set", text="Calc -> Set Value")
			
			layout.separator()
			
			#Split row
			row = layout.row()
			c = row.column()
			row = c.row()
			split = row.split(factor=0.3, align=True)
			c = split.column()
			c.label(text="Set TD:")			
			split = split.split(factor=0.6, align=True)
			c = split.column()
			c.prop(td, "density_set")
			split = split.split()
			c = split.column()
			if td.units == '0':
				c.label(text="px/cm")
			if td.units == '1':
				c.label(text="px/m")
			if td.units == '2':
				c.label(text="px/in")
			if td.units == '3':
				c.label(text="px/ft")
			#----

			#Split row
			row = layout.row()
			c = row.column()
			row = c.row()
			split = row.split(factor=0.5, align=True)
			c = split.column()
			c.label(text="Set Method:")
			split = split.split()
			c = split.column()
			c.prop(td, 'set_method', expand=False)
			#----

			layout.operator("object.texel_density_set", text="Set My TD")
			
			#--Aligner Preset Buttons----
			row = layout.row()
			c = row.column()
			row = c.row()

			split = row.split(factor=0.33, align=True)
			c = split.column()
			if td.units == '0':
				c.operator("object.preset_set", text="20.48").td_value="20.48"
			if td.units == '1':
				c.operator("object.preset_set", text="2048").td_value="2048"
			if td.units == '2':
				c.operator("object.preset_set", text="52.019").td_value="52.019"
			if td.units == '3':
				c.operator("object.preset_set", text="624.23").td_value="624.23"
			
			split = split.split(factor=0.5, align=True)
			c = split.column()
			if td.units == '0':
				c.operator("object.preset_set", text="10.24").td_value="10.24"
			if td.units == '1':
				c.operator("object.preset_set", text="1024").td_value="1024"
			if td.units == '2':
				c.operator("object.preset_set", text="26.01").td_value="26.01"
			if td.units == '3':
				c.operator("object.preset_set", text="312.115").td_value="312.115"

			split = split.split()
			c = split.column()
			if td.units == '0':
				c.operator("object.preset_set", text="5.12").td_value="5.12"
			if td.units == '1':
				c.operator("object.preset_set", text="512").td_value="512"
			if td.units == '2':
				c.operator("object.preset_set", text="13.005").td_value="13.005"
			if td.units == '3':
				c.operator("object.preset_set", text="156.058").td_value="156.058"
				
			#--Aligner Preset Buttons----
			row = layout.row()
			c = row.column()
			row = c.row()
			split = row.split(factor=0.33, align=True)
			c = split.column()
			if td.units == '0':
				c.operator("object.preset_set", text="2.56").td_value="2.56"
				
			if td.units == '1':
				c.operator("object.preset_set", text="256").td_value="256"
				
			if td.units == '2':
				c.operator("object.preset_set", text="6.502").td_value="6.502"
				
			if td.units == '3':
				c.operator("object.preset_set", text="78.029").td_value="78.029"
				
			split = split.split(factor=0.5, align=True)
			c = split.column()
			if td.units == '0':
				c.operator("object.preset_set", text="1.28").td_value="1.28"
				
			if td.units == '1':
				c.operator("object.preset_set", text="128").td_value="128"
				
			if td.units == '2':
				c.operator("object.preset_set", text="3.251").td_value="3.251"
				
			if td.units == '3':
				c.operator("object.preset_set", text="39.014").td_value="39.014"
				
			split = split.split()
			c = split.column()
			if td.units == '0':
				c.operator("object.preset_set", text="0.64").td_value="0.64"
				
			if td.units == '1':
				c.operator("object.preset_set", text="64").td_value="64"
				
			if td.units == '2':
				c.operator("object.preset_set", text="1.626").td_value="1.626"
				
			if td.units == '3':
				c.operator("object.preset_set", text="19.507").td_value="19.507"
				
			layout.separator()
			layout.separator()

			if context.object.mode == 'OBJECT':
				layout.operator("object.texel_density_copy", text="TD from Active to Others")
				
			if context.object.mode == 'EDIT':
				#Split row
				row = layout.row()
				c = row.column()
				row = c.row()
				split = row.split(factor=0.3, align=True)
				c = split.column()
				c.label(text="Select:")
				split = split.split()
				c = split.column()
				c.prop(td, "select_mode", expand=False)
				#----
				#Split row
				row = layout.row()
				c = row.column()
				row = c.row()
				split = row.split(factor=0.4, align=True)
				c = split.column()
				if td.select_mode == "FACES_BY_TD" or td.select_mode == "ISLANDS_BY_TD":
					c.label(text="Texel:")
				elif td.select_mode == "ISLANDS_BY_SPACE":
					c.label(text="UV Space:")
				split = split.split(factor=0.6, align=True)
				c = split.column()
				c.prop(td, "select_value")
				split = split.split()
				c = split.column()
				if td.select_mode == "FACES_BY_TD" or td.select_mode == "ISLANDS_BY_TD":
					if td.units == '0':
						c.label(text="px/cm")
					if td.units == '1':
						c.label(text="px/m")
					if td.units == '2':
						c.label(text="px/in")
					if td.units == '3':
						c.label(text="px/ft")
				elif td.select_mode == "ISLANDS_BY_SPACE":
					c.label(text="%")
				#----
				#Split row
				row = layout.row()
				c = row.column()
				row = c.row()
				split = row.split(factor=0.6, align=True)
				c = split.column()
				c.label(text="Select Threshold:")
				split = split.split()
				c = split.column()
				c.prop(td, "select_threshold")
				#----
				if td.select_mode == "FACES_BY_TD":
					layout.operator("object.select_by_td_space", text="Select Faces By TD")
				elif td.select_mode == "ISLANDS_BY_TD":
					layout.operator("object.select_by_td_space", text="Select Islands By TD")
				elif td.select_mode == "ISLANDS_BY_SPACE":
					layout.operator("object.select_by_td_space", text="Select Islands By UV Space")


			layout.separator()
			layout.separator()

			#Split row
			row = layout.row()
			c = row.column()
			row = c.row()
			split = row.split(factor=0.5, align=True)
			c = split.column()
			c.label(text="Bake VC Mode:")
			split = split.split()
			c = split.column()
			c.prop(td, "bake_vc_mode", expand=False)
			#----

			if td.bake_vc_mode == "TD_FACES_TO_VC" or td.bake_vc_mode == "TD_ISLANDS_TO_VC":
				row = layout.row()
				row.label(text="Min/Max TD Values:")
				#Split row
				row = layout.row()
				c = row.column()
				row = c.row()
				split = row.split(factor=0.5, align=True)
				c = split.column()
				c.prop(td, "bake_vc_min_td")
				split = split.split()
				c = split.column()
				c.prop(td, "bake_vc_max_td")
				#----
				row = layout.row()
				row.prop(td, "bake_vc_show_gradient", text="Show Gradient")
				row = layout.row()
				row.operator("object.bake_td_uv_to_vc", text="Texel Density to VC")
			
			elif td.bake_vc_mode == "UV_ISLANDS_TO_VC":
				row = layout.row()
				row.operator("object.bake_td_uv_to_vc", text="UV Islands to VC")

			elif td.bake_vc_mode == "UV_SPACE_TO_VC":
				row = layout.row()
				row.label(text="Min/Max UV Space:")
				#Split row
				row = layout.row()
				c = row.column()
				row = c.row()
				split = row.split(factor=0.5, align=True)
				c = split.column()
				c.prop(td, "bake_vc_min_space")
				split = split.split()
				c = split.column()
				c.prop(td, "bake_vc_max_space")
				#----
				row = layout.row()
				row.prop(td, "bake_vc_show_gradient", text="Show Gradient")
				row = layout.row()
				row.operator("object.bake_td_uv_to_vc", text="UV Space to VC")

			row = layout.row()
			row.operator("object.clear_td_vc", text="Clear TD Vertex Colors")


# Panel in UV Editor
class UV_PT_texel_density_checker(bpy.types.Panel):
	bl_label = "Texel Density Checker"
	bl_space_type = "IMAGE_EDITOR"
	bl_region_type = "UI"
	bl_category = "Texel Density"

	@classmethod
	def poll(self, context):
		return (context.object is not None)

	def draw(self, context):
		td = context.scene.td
		
		if context.object.mode == 'EDIT' and context.space_data.mode == 'UV' and len(context.active_object.data.uv_layers) > 0:
			layout = self.layout
			#Split row
			row = layout.row()
			c = row.column()
			row = c.row()
			split = row.split(factor=0.5, align=True)
			c = split.column()
			c.label(text="Units:")
			split = split.split()
			c = split.column()
			c.prop(td, 'units', expand=False)
			#----

			#Split row
			row = layout.row()
			c = row.column()
			row = c.row()
			split = row.split(factor=0.5, align=True)
			c = split.column()
			c.label(text="Texture Size:")
			split = split.split()
			c = split.column()
			c.prop(td, 'texture_size', expand=False)
			#----

			if td.texture_size == '4':
				row = layout.row()
				c = row.column()
				row = c.row()
				split = row.split(factor=0.35, align=True)
				c = split.column()
				c.label(text="Width:")
				split = split.split(factor=0.65, align=True)
				c = split.column()
				c.prop(td, "custom_width")
				split = split.split()
				c = split.column()
				c.label(text="px")

				row = layout.row()
				c = row.column()
				row = c.row()
				split = row.split(factor=0.35, align=True)
				c = split.column()
				c.label(text="Height:")
				split = split.split(factor=0.65, align=True)
				c = split.column()
				c.prop(td, "custom_height")
				split = split.split()
				c = split.column()
				c.label(text="px")	

			layout.separator()
			layout.separator()

			layout.prop(td, "selected_faces", text="Selected Faces")

			#Split row
			row = layout.row()
			c = row.column()
			row = c.row()
			split = row.split(factor=0.5, align=True)
			c = split.column()
			c.label(text="UV Space:")
			split = split.split()
			c = split.column()
			c.label(text=td.uv_space)
			#----

			cur_units = "px/cm"
			if td.units == '0':
				cur_units = "px/cm"
			if td.units == '1':
				cur_units = "px/m"
			if td.units == '2':
				cur_units = "px/in"
			if td.units == '3':
				cur_units = "px/ft"

			#Split row
			row = layout.row()
			c = row.column()
			row = c.row()
			split = row.split(factor=0.4, align=True)
			c = split.column()
			c.label(text="Density:")
			split = split.split()
			c = split.column()
			c.label(text=td.density + " " + cur_units)
			#----

			layout.operator("object.texel_density_check", text="Calculate TD")
			layout.operator("object.calculate_to_set", text="Calc -> Set Value")
			
			layout.separator()
			
			#Split row
			row = layout.row()
			c = row.column()
			row = c.row()
			split = row.split(factor=0.3, align=True)
			c = split.column()
			c.label(text="Set TD:")			
			split = split.split(factor=0.6, align=True)
			c = split.column()
			c.prop(td, "density_set")
			split = split.split()
			c = split.column()
			if td.units == '0':
				c.label(text="px/cm")
			if td.units == '1':
				c.label(text="px/m")
			if td.units == '2':
				c.label(text="px/in")
			if td.units == '3':
				c.label(text="px/ft")
			#----
			
			#Split row
			row = layout.row()
			c = row.column()
			row = c.row()
			split = row.split(factor=0.5, align=True)
			c = split.column()
			c.label(text="Set Method:")
			split = split.split()
			c = split.column()
			c.prop(td, 'set_method', expand=False)
			#----

			layout.operator("object.texel_density_set", text="Set My TD")
			
			#--Aligner Preset Buttons----
			row = layout.row()
			c = row.column()
			row = c.row()
			split = row.split(factor=0.33, align=True)
			c = split.column()
			if td.units == '0':
				c.operator("object.preset_set", text="20.48").td_value="20.48"
				
			if td.units == '1':
				c.operator("object.preset_set", text="2048").td_value="2048"
				
			if td.units == '2':
				c.operator("object.preset_set", text="52.019").td_value="52.019"
				
			if td.units == '3':
				c.operator("object.preset_set", text="624.23").td_value="624.23"
				
			split = split.split(factor=0.5, align=True)
			c = split.column()
			if td.units == '0':
				c.operator("object.preset_set", text="10.24").td_value="10.24"
				
			if td.units == '1':
				c.operator("object.preset_set", text="1024").td_value="1024"
				
			if td.units == '2':
				c.operator("object.preset_set", text="26.01").td_value="26.01"
				
			if td.units == '3':
				c.operator("object.preset_set", text="312.115").td_value="312.115"
				
			split = split.split()
			c = split.column()
			if td.units == '0':
				c.operator("object.preset_set", text="5.12").td_value="5.12"
				
			if td.units == '1':
				c.operator("object.preset_set", text="512").td_value="512"
				
			if td.units == '2':
				c.operator("object.preset_set", text="13.005").td_value="13.005"
				
			if td.units == '3':
				c.operator("object.preset_set", text="156.058").td_value="156.058"
				
				
			#--Aligner Preset Buttons----
			row = layout.row()
			c = row.column()
			row = c.row()
			split = row.split(factor=0.33, align=True)
			c = split.column()
			if td.units == '0':
				c.operator("object.preset_set", text="2.56").td_value="2.56"
				
			if td.units == '1':
				c.operator("object.preset_set", text="256").td_value="256"
				
			if td.units == '2':
				c.operator("object.preset_set", text="6.502").td_value="6.502"
				
			if td.units == '3':
				c.operator("object.preset_set", text="78.029").td_value="78.029"
				
			split = split.split(factor=0.5, align=True)
			c = split.column()
			if td.units == '0':
				c.operator("object.preset_set", text="1.28").td_value="1.28"
				
			if td.units == '1':
				c.operator("object.preset_set", text="128").td_value="128"
				
			if td.units == '2':
				c.operator("object.preset_set", text="3.251").td_value="3.251"
				
			if td.units == '3':
				c.operator("object.preset_set", text="39.014").td_value="39.014"
				
			split = split.split()
			c = split.column()
			if td.units == '0':
				c.operator("object.preset_set", text="0.64").td_value="0.64"
				
			if td.units == '1':
				c.operator("object.preset_set", text="64").td_value="64"
				
			if td.units == '2':
				c.operator("object.preset_set", text="1.626").td_value="1.626"
				
			if td.units == '3':
				c.operator("object.preset_set", text="19.507").td_value="19.507"
				
			layout.separator()
			layout.separator()

			#Split row
			row = layout.row()
			c = row.column()
			row = c.row()
			split = row.split(factor=0.3, align=True)
			c = split.column()
			c.label(text="Select:")
			split = split.split()
			c = split.column()
			c.prop(td, "select_mode", expand=False)
			#----
			#Split row
			row = layout.row()
			c = row.column()
			row = c.row()
			split = row.split(factor=0.4, align=True)
			c = split.column()
			if td.select_mode == "FACES_BY_TD" or td.select_mode == "ISLANDS_BY_TD":
				c.label(text="Texel:")
			elif td.select_mode == "ISLANDS_BY_SPACE":
				c.label(text="UV Space:")
			split = split.split(factor=0.6, align=True)
			c = split.column()
			c.prop(td, "select_value")
			split = split.split()
			c = split.column()
			if td.select_mode == "FACES_BY_TD" or td.select_mode == "ISLANDS_BY_TD":
				if td.units == '0':
					c.label(text="px/cm")
				if td.units == '1':
					c.label(text="px/m")
				if td.units == '2':
					c.label(text="px/in")
				if td.units == '3':
					c.label(text="px/ft")
			elif td.select_mode == "ISLANDS_BY_SPACE":
				c.label(text="%")
			#----
			#Split row
			row = layout.row()
			c = row.column()
			row = c.row()
			split = row.split(factor=0.6, align=True)
			c = split.column()
			c.label(text="Select Threshold:")
			split = split.split()
			c = split.column()
			c.prop(td, "select_threshold")
			#----
			if td.select_mode == "FACES_BY_TD":
				layout.operator("object.select_by_td_space", text="Select Faces By TD")
			elif td.select_mode == "ISLANDS_BY_TD":
				layout.operator("object.select_by_td_space", text="Select Islands By TD")
			elif td.select_mode == "ISLANDS_BY_SPACE":
				layout.operator("object.select_by_td_space", text="Select Islands By UV Space")


classes = (
    VIEW3D_PT_texel_density_checker,
    UV_PT_texel_density_checker,
)	


def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)
