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

			layout.label(text="Texture Size:")

			row = layout.row()
			row.prop(td, 'texture_size', expand=False)

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
			row = layout.row()
			row.label(text="Checker Material Method:")
			row = layout.row()
			row.prop(td, 'checker_method', expand=False)
			row = layout.row()
			row.label(text="Checker Type:")
			row = layout.row()
			row.prop(td, 'checker_type', expand=False)
			row = layout.row()
			row.operator("object.checker_assign", text="Assign Checker Material")

			row = layout.row()
			row.operator("object.checker_restore", text="Restore Materials")

			if context.object.mode == 'EDIT':
				layout.separator()
				layout.prop(td, "selected_faces", text="Selected Faces")
			
			layout.separator()
			layout.label(text="Filled UV Space:")
			row = layout.row()
			row.prop(td, "uv_space")
			row.enabled = False
			layout.label(text="Texel Density:")
			row = layout.row()
			c = row.column()
			row = c.row()
			split = row.split(factor=0.65, align=True)
			c = split.column()
			c.prop(td, "density")
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
			row.enabled = False
			layout.operator("object.texel_density_check", text="Calculate TD")
			layout.operator("object.calculate_to_set", text="Calc -> Set Value")
			layout.separator()
			layout.label(text="Set Texel Density")
			
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

			row = layout.row()
			c = row.column()
			row = c.row()
			split = row.split(factor=0.65, align=True)
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
				c.operator("object.preset_set", text="52.0192").td_value="52.0192"
			if td.units == '3':
				c.operator("object.preset_set", text="624.2304").td_value="624.2304"
			
			split = split.split(factor=0.5, align=True)
			c = split.column()
			if td.units == '0':
				c.operator("object.preset_set", text="10.24").td_value="10.24"
			if td.units == '1':
				c.operator("object.preset_set", text="1024").td_value="1024"
			if td.units == '2':
				c.operator("object.preset_set", text="26.0096").td_value="26.0096"
			if td.units == '3':
				c.operator("object.preset_set", text="312.1152").td_value="312.1152"

			split = split.split()
			c = split.column()
			if td.units == '0':
				c.operator("object.preset_set", text="5.12").td_value="5.12"
			if td.units == '1':
				c.operator("object.preset_set", text="512").td_value="512"
			if td.units == '2':
				c.operator("object.preset_set", text="13.0048").td_value="13.0048"
			if td.units == '3':
				c.operator("object.preset_set", text="156.0576").td_value="156.0576"
				
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
				c.operator("object.preset_set", text="6.5024").td_value="6.5024"
				
			if td.units == '3':
				c.operator("object.preset_set", text="78.0288").td_value="78.0288"
				
			split = split.split(factor=0.5, align=True)
			c = split.column()
			if td.units == '0':
				c.operator("object.preset_set", text="1.28").td_value="1.28"
				
			if td.units == '1':
				c.operator("object.preset_set", text="128").td_value="128"
				
			if td.units == '2':
				c.operator("object.preset_set", text="3.2512").td_value="3.2512"
				
			if td.units == '3':
				c.operator("object.preset_set", text="39.0144").td_value="39.0144"
				
			split = split.split()
			c = split.column()
			if td.units == '0':
				c.operator("object.preset_set", text="0.64").td_value="0.64"
				
			if td.units == '1':
				c.operator("object.preset_set", text="64").td_value="64"
				
			if td.units == '2':
				c.operator("object.preset_set", text="1.6256").td_value="1.6256"
				
			if td.units == '3':
				c.operator("object.preset_set", text="19.5072").td_value="19.5072"
				
			
			if context.object.mode == 'OBJECT':
				layout.separator()
				layout.operator("object.texel_density_copy", text="TD from Active to Others")
				
			if context.object.mode == 'EDIT':
				layout.separator()
				layout.operator("object.select_same_texel", text="Select Faces with same TD")
				#Split row
				row = layout.row()
				c = row.column()
				row = c.row()
				split = row.split(factor=0.6, align=True)
				c = split.column()
				c.label(text="Select Threshold:")
				split = split.split()
				c = split.column()
				c.prop(td, "select_td_threshold")
				#----

			layout.separator()
			row = layout.row()
			row.operator("object.clear_checker_face_maps", text="Clear Stored Face Maps")

			
			layout.separator()
			row = layout.row()
			row.label(text="TD to Vertex Colors")
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
			layout.separator()
			row = layout.row()
			row.prop(td, "bake_vc_show_gradient", text="Show Gradient")
			layout.separator()
			row = layout.row()
			row.operator("object.bake_td_uv_to_vc", text="TD to Vertex Color").mode = 'TD'
			row = layout.row()
			row.operator("object.bake_td_uv_to_vc", text="UV to Vertex Color").mode = 'UV'
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

			layout.label(text="Texture Size:")

			row = layout.row()
			row.prop(td, 'texture_size', expand=False)

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
			layout.prop(td, "selected_faces", text="Selected Faces")
			
			layout.separator()
			layout.label(text="Filled UV Space:")
			row = layout.row()
			row.prop(td, "uv_space")
			row.enabled = False
			layout.label(text="Texel Density:")
			row = layout.row()
			c = row.column()
			row = c.row()
			split = row.split(factor=0.65, align=True)
			c = split.column()
			c.prop(td, "density")
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
			row.enabled = False
			layout.operator("object.texel_density_check", text="Calculate TD")
			layout.operator("object.calculate_to_set", text="Calc -> Set Value")
			layout.separator()
			layout.label(text="Set Texel Density")
			
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

			row = layout.row()
			c = row.column()
			row = c.row()
			split = row.split(factor=0.65, align=True)
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
				c.operator("object.preset_set", text="52.0192").td_value="52.0192"
				
			if td.units == '3':
				c.operator("object.preset_set", text="624.2304").td_value="624.2304"
				
			split = split.split(factor=0.5, align=True)
			c = split.column()
			if td.units == '0':
				c.operator("object.preset_set", text="10.24").td_value="10.24"
				
			if td.units == '1':
				c.operator("object.preset_set", text="1024").td_value="1024"
				
			if td.units == '2':
				c.operator("object.preset_set", text="26.0096").td_value="26.0096"
				
			if td.units == '3':
				c.operator("object.preset_set", text="312.1152").td_value="312.1152"
				
			split = split.split()
			c = split.column()
			if td.units == '0':
				c.operator("object.preset_set", text="5.12").td_value="5.12"
				
			if td.units == '1':
				c.operator("object.preset_set", text="512").td_value="512"
				
			if td.units == '2':
				c.operator("object.preset_set", text="13.0048").td_value="13.0048"
				
			if td.units == '3':
				c.operator("object.preset_set", text="156.0576").td_value="156.0576"
				
				
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
				c.operator("object.preset_set", text="6.5024").td_value="6.5024"
				
			if td.units == '3':
				c.operator("object.preset_set", text="78.0288").td_value="78.0288"
				
			split = split.split(factor=0.5, align=True)
			c = split.column()
			if td.units == '0':
				c.operator("object.preset_set", text="1.28").td_value="1.28"
				
			if td.units == '1':
				c.operator("object.preset_set", text="128").td_value="128"
				
			if td.units == '2':
				c.operator("object.preset_set", text="3.2512").td_value="3.2512"
				
			if td.units == '3':
				c.operator("object.preset_set", text="39.0144").td_value="39.0144"
				
			split = split.split()
			c = split.column()
			if td.units == '0':
				c.operator("object.preset_set", text="0.64").td_value="0.64"
				
			if td.units == '1':
				c.operator("object.preset_set", text="64").td_value="64"
				
			if td.units == '2':
				c.operator("object.preset_set", text="1.6256").td_value="1.6256"
				
			if td.units == '3':
				c.operator("object.preset_set", text="19.5072").td_value="19.5072"
				
				
			layout.separator()
			layout.operator("object.select_same_texel", text="Select Faces with same TD")
			#Split row
			row = layout.row()
			c = row.column()
			row = c.row()
			split = row.split(factor=0.6, align=True)
			c = split.column()
			c.label(text="Select Threshold:")
			split = split.split()
			c = split.column()
			c.prop(td, "select_td_threshold")
			#----


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
