import bpy


# Panel in 3D View
class VIEW3D_PT_texel_density_checker(bpy.types.Panel):
	bl_label = "Texel Density Checker"
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_category = "Texel Density"

	@classmethod
	def poll(self, context):
		return (context.object is not None)

	def draw(self, context):
		td = context.scene.td
		
		if context.active_object.type == 'MESH' and len(context.active_object.data.uv_layers) > 0:
			layout = self.layout

			row = layout.row(align=True)
			row.label(text="Units:")
			row.prop(td, 'units', expand=False)
			
			box = layout.box()
			row = box.row(align=True)
			row.label(text="Texture Size:")
			row.prop(td, 'texture_size', expand=False)
			#----

			if td.texture_size == '4':
				row = box.row(align=True)
				row.label(text="Width:")
				row.prop(td, "custom_width")
				row.label(text="px")

				row = box.row(align=True)
				row.label(text="Height:")
				row.prop(td, "custom_height")
				row.label(text="px")
		
			box = layout.box()	
			row = box.row(align=True)
			row.label(text="Checker Method:")
			row.prop(td, 'checker_method', expand=False)
			
			row = box.row()
			row.label(text="Checker Type:")
			row.prop(td, 'checker_type', expand=False)
			
			row = box.row()
			row.operator("object.checker_assign", text="Assign Checker Material")

			if td.checker_method == '1':
				row = box.row()
				row.operator("object.checker_restore", text="Restore Materials")
				row = box.row()
				row.operator("object.clear_checker_face_maps", text="Clear Stored Face Maps")
			
			if context.object.mode == 'EDIT':
				row = layout.row()
				row.prop(td, "selected_faces", text="Selected Faces")

			box = layout.box()
			row = box.row(align=True)
			row.label(text="UV Space:")
			row.label(text=td.uv_space)
			
			cur_units = "px/cm"
			if td.units == '0':
				cur_units = "px/cm"
			if td.units == '1':
				cur_units = "px/m"
			if td.units == '2':
				cur_units = "px/in"
			if td.units == '3':
				cur_units = "px/ft"

			row = box.row(align=True)
			row.label(text="Density:")
			row.label(text=td.density + " " + cur_units)
			
			row = box.row()
			row.operator("object.texel_density_check", text="Calculate TD")
			row = box.row()
			row.operator("object.calculate_to_set", text="Calc -> Set Value")
			if context.object.mode == 'EDIT':
				row = box.row()
				row.operator("object.calculate_to_select", text="Calc -> Select Value")
			

			box = layout.box()
			row = box.row(align=True)
			row.label(text="Set TD:")			
			row.prop(td, "density_set")
			if td.units == '0':
				row.label(text="px/cm")
			if td.units == '1':
				row.label(text="px/m")
			if td.units == '2':
				row.label(text="px/in")
			if td.units == '3':
				row.label(text="px/ft")
			
			row = box.row(align=True)
			row.label(text="Set Method:")
			row.prop(td, 'set_method', expand=False)
			
			row = box.row()
			row.operator("object.texel_density_set", text="Set My TD")
			
			row = box.row(align=True)
			if td.units == '0':
				row.operator("object.preset_set", text="20.48").td_value="20.48"
				row.operator("object.preset_set", text="10.24").td_value="10.24"
				row.operator("object.preset_set", text="5.12").td_value="5.12"
			if td.units == '1':
				row.operator("object.preset_set", text="2048").td_value="2048"
				row.operator("object.preset_set", text="1024").td_value="1024"
				row.operator("object.preset_set", text="512").td_value="512"
			if td.units == '2':
				row.operator("object.preset_set", text="52.019").td_value="52.019"
				row.operator("object.preset_set", text="26.01").td_value="26.01"
				row.operator("object.preset_set", text="13.005").td_value="13.005"
			if td.units == '3':
				row.operator("object.preset_set", text="624.23").td_value="624.23"
				row.operator("object.preset_set", text="312.115").td_value="312.115"
				row.operator("object.preset_set", text="156.058").td_value="156.058"
							
			row = box.row(align=True)
			if td.units == '0':
				row.operator("object.preset_set", text="2.56").td_value="2.56"
				row.operator("object.preset_set", text="1.28").td_value="1.28"
				row.operator("object.preset_set", text="0.64").td_value="0.64"
			if td.units == '1':
				row.operator("object.preset_set", text="256").td_value="256"
				row.operator("object.preset_set", text="128").td_value="128"
				row.operator("object.preset_set", text="64").td_value="64"
			if td.units == '2':
				row.operator("object.preset_set", text="6.502").td_value="6.502"
				row.operator("object.preset_set", text="3.251").td_value="3.251"
				row.operator("object.preset_set", text="1.626").td_value="1.626"
			if td.units == '3':
				row.operator("object.preset_set", text="78.029").td_value="78.029"
				row.operator("object.preset_set", text="39.014").td_value="39.014"
				row.operator("object.preset_set", text="19.507").td_value="19.507"
					
			if context.object.mode == 'OBJECT':
				row = layout.row()
				row.operator("object.texel_density_copy", text="TD from Active to Others")
				
			if context.object.mode == 'EDIT':
				box = layout.box()
				row = box.row(align=True)
				row.label(text="Select:")
				row.prop(td, "select_mode", expand=False)
				
				row = box.row(align=True)
				row.label(text="Select Type:")
				row.prop(td, "select_type", expand=False)
				
				row = box.row(align=True)
				if td.select_mode == "FACES_BY_TD" or td.select_mode == "ISLANDS_BY_TD":
					row.label(text="Texel:")
				elif td.select_mode == "ISLANDS_BY_SPACE":
					row.label(text="UV Space:")
				
				row.prop(td, "select_value")
				
				if td.select_mode == "FACES_BY_TD" or td.select_mode == "ISLANDS_BY_TD":
					if td.units == '0':
						row.label(text="px/cm")
					if td.units == '1':
						row.label(text="px/m")
					if td.units == '2':
						row.label(text="px/in")
					if td.units == '3':
						row.label(text="px/ft")
				elif td.select_mode == "ISLANDS_BY_SPACE":
					row.label(text="%")

				if td.select_type == "EQUAL":
					row = box.row(align=True)
					row.label(text="Select Threshold:")
					row.prop(td, "select_threshold")

				row = box.row()
				if td.select_mode == "FACES_BY_TD":
					row.operator("object.select_by_td_space", text="Select Faces By TD")
				elif td.select_mode == "ISLANDS_BY_TD":
					row.operator("object.select_by_td_space", text="Select Islands By TD")
				elif td.select_mode == "ISLANDS_BY_SPACE":
					row.operator("object.select_by_td_space", text="Select Islands By UV Space")


			box = layout.box()
			row = box.row(align=True)
			row.label(text="Bake VC Mode:")
			row.prop(td, "bake_vc_mode", expand=False)
			
			if td.bake_vc_mode == "TD_FACES_TO_VC" or td.bake_vc_mode == "TD_ISLANDS_TO_VC":
				row = box.row(align=True)
				row.label(text="Min TD Value:")
				row.label(text="Max TD Value:")
				
				row = box.row(align=True)
				row.prop(td, "bake_vc_min_td")
				row.prop(td, "bake_vc_max_td")
				
				row = box.row()
				row.prop(td, "bake_vc_show_gradient", text="Show Gradient")
				row = box.row()
				row.operator("object.bake_td_uv_to_vc", text="Texel Density to VC")
			
			elif td.bake_vc_mode == "UV_ISLANDS_TO_VC":
				row = box.row(align=True)
				row.label(text="Island Detect Mode:")
				row.prop(td, "uv_islands_to_vc_mode", expand=False)
				
				row = box.row()
				row.operator("object.bake_td_uv_to_vc", text="UV Islands to VC")

			elif td.bake_vc_mode == "UV_SPACE_TO_VC":
				row = box.row(align=True)
				row.label(text="Min UV Space:")
				row.label(text="Max UV Space:")

				row = box.row(align=True)
				row.prop(td, "bake_vc_min_space")
				row.prop(td, "bake_vc_max_space")
				
				row = box.row()
				row.prop(td, "bake_vc_show_gradient", text="Show Gradient")
				row = box.row()
				row.operator("object.bake_td_uv_to_vc", text="UV Space to VC")

			row = box.row()
			row.operator("object.clear_td_vc", text="Clear TD Vertex Colors")


# Panel in UV Editor
class UV_PT_texel_density_checker(bpy.types.Panel):
	bl_label = "Texel Density Checker"
	bl_space_type = "IMAGE_EDITOR"
	bl_region_type = "UI"
	bl_category = "Texel Density"

	@classmethod
	def poll(self, context):
		return (context.object is not None) and context.mode == 'EDIT_MESH'

	def draw(self, context):
		td = context.scene.td
		
		if context.object.mode == 'EDIT' and context.space_data.mode == 'UV' and len(context.active_object.data.uv_layers) > 0:
			layout = self.layout

			row = layout.row(align=True)
			row.label(text="Units:")
			row.prop(td, 'units', expand=False)
			
			box = layout.box()
			row = box.row(align=True)
			row.label(text="Texture Size:")
			row.prop(td, 'texture_size', expand=False)
			
			if td.texture_size == '4':
				row = box.row(align=True)
				row.label(text="Width:")
				row.prop(td, "custom_width")
				row.label(text="px")

				row = box.row(align=True)
				row.label(text="Height:")
				row.prop(td, "custom_height")
				row.label(text="px")	

			row = layout.row()
			row.prop(td, "selected_faces", text="Selected Faces")

			box = layout.box()
			row = box.row(align=True)
			row.label(text="UV Space:")
			row.label(text=td.uv_space)
			
			cur_units = "px/cm"
			if td.units == '0':
				cur_units = "px/cm"
			if td.units == '1':
				cur_units = "px/m"
			if td.units == '2':
				cur_units = "px/in"
			if td.units == '3':
				cur_units = "px/ft"

			row = box.row(align=True)
			row.label(text="Density:")
			row.label(text=td.density + " " + cur_units)
			
			row = box.row()
			row.operator("object.texel_density_check", text="Calculate TD")
			row = box.row()
			row.operator("object.calculate_to_set", text="Calc -> Set Value")
			row = box.row()
			row.operator("object.calculate_to_select", text="Calc -> Select Value")
			
			box = layout.box()
			row = box.row(align=True)
			row.label(text="Set TD:")			
			row.prop(td, "density_set")
			
			if td.units == '0':
				row.label(text="px/cm")
			if td.units == '1':
				row.label(text="px/m")
			if td.units == '2':
				row.label(text="px/in")
			if td.units == '3':
				row.label(text="px/ft")
			
			row = box.row(align=True)
			row.label(text="Set Method:")
			row.prop(td, 'set_method', expand=False)
			
			row = box.row()
			row.operator("object.texel_density_set", text="Set My TD")
			
			row = box.row(align=True)
			if td.units == '0':
				row.operator("object.preset_set", text="20.48").td_value="20.48"
				row.operator("object.preset_set", text="10.24").td_value="10.24"
				row.operator("object.preset_set", text="5.12").td_value="5.12"
				
			if td.units == '1':
				row.operator("object.preset_set", text="2048").td_value="2048"
				row.operator("object.preset_set", text="1024").td_value="1024"
				row.operator("object.preset_set", text="512").td_value="512"
				
			if td.units == '2':
				row.operator("object.preset_set", text="52.019").td_value="52.019"
				row.operator("object.preset_set", text="26.01").td_value="26.01"
				row.operator("object.preset_set", text="13.005").td_value="13.005"
				
			if td.units == '3':
				row.operator("object.preset_set", text="624.23").td_value="624.23"
				row.operator("object.preset_set", text="312.115").td_value="312.115"
				row.operator("object.preset_set", text="156.058").td_value="156.058"
				
			row = box.row(align=True)
			if td.units == '0':
				row.operator("object.preset_set", text="2.56").td_value="2.56"
				row.operator("object.preset_set", text="1.28").td_value="1.28"
				row.operator("object.preset_set", text="0.64").td_value="0.64"

			if td.units == '1':
				row.operator("object.preset_set", text="256").td_value="256"
				row.operator("object.preset_set", text="128").td_value="128"
				row.operator("object.preset_set", text="64").td_value="64"

			if td.units == '2':
				row.operator("object.preset_set", text="6.502").td_value="6.502"
				row.operator("object.preset_set", text="3.251").td_value="3.251"
				row.operator("object.preset_set", text="1.626").td_value="1.626"

			if td.units == '3':
				row.operator("object.preset_set", text="78.029").td_value="78.029"
				row.operator("object.preset_set", text="39.014").td_value="39.014"
				row.operator("object.preset_set", text="19.507").td_value="19.507"

			box = layout.box()
			row = box.row(align=True)
			row.label(text="Select:")
			row.prop(td, "select_mode", expand=False)
			
			row = box.row(align=True)
			row.label(text="Select Type:")
			row.prop(td, "select_type", expand=False)
			
			row = box.row(align=True)
			if td.select_mode == "FACES_BY_TD" or td.select_mode == "ISLANDS_BY_TD":
				row.label(text="Texel:")
			elif td.select_mode == "ISLANDS_BY_SPACE":
				row.label(text="UV Space:")
			row.prop(td, "select_value")
			
			if td.select_mode == "FACES_BY_TD" or td.select_mode == "ISLANDS_BY_TD":
				if td.units == '0':
					row.label(text="px/cm")
				if td.units == '1':
					row.label(text="px/m")
				if td.units == '2':
					row.label(text="px/in")
				if td.units == '3':
					row.label(text="px/ft")
			elif td.select_mode == "ISLANDS_BY_SPACE":
				row.label(text="%")

			if td.select_type == "EQUAL":
				row = box.row(align=True)
				row.label(text="Select Threshold:")
				row.prop(td, "select_threshold")
				#----
			
			row = box.row()
			if td.select_mode == "FACES_BY_TD":
				row.operator("object.select_by_td_space", text="Select Faces By TD")
			elif td.select_mode == "ISLANDS_BY_TD":
				row.operator("object.select_by_td_space", text="Select Islands By TD")
			elif td.select_mode == "ISLANDS_BY_SPACE":
				row.operator("object.select_by_td_space", text="Select Islands By UV Space")


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
