def Filter_Gradient_OffsetX(self, context):
	offsetXFiltered = bpy.context.preferences.addons[__name__].preferences.offsetX.replace(',', '.')
	
	try:
		offsetX = int(offsetXFiltered)
	except:
		offsetX = 20

	if (offsetX < 0):
		offsetX = 20
	
	bpy.context.preferences.addons[__name__].preferences.offsetX = str(offsetX)


def Filter_Gradient_OffsetY(self, context):	
	offsetYFiltered = bpy.context.preferences.addons[__name__].preferences.offsetY.replace(',', '.')
	
	try:
		offsetY = int(offsetYFiltered)
	except:
		offsetY = 20

	if (offsetY < 0):
		offsetY = 20

	bpy.context.preferences.addons[__name__].preferences.offsetY = str(offsetY)


class TD_Addon_Preferences(bpy.types.AddonPreferences):
	bl_idname = __name__

	offsetX: StringProperty(
		name="Offset X",
		description="Offset X from Anchor",
		default="250", update = Filter_Gradient_OffsetX)

	offsetY: StringProperty(
		name="Offset Y",
		description="Offset Y from Anchor",
		default="20", update = Filter_Gradient_OffsetY)

	anchorPosList = (('LEFT_TOP','Left Top',''),('LEFT_BOTTOM','Left Bottom',''), 
						('RIGHT_TOP','Right Top',''), ('RIGHT_BOTTOM','Right Bottom',''))
	anchorPos: EnumProperty(name="Anchor Position", items = anchorPosList, default = 'LEFT_BOTTOM')

	def draw(self, context):
		layout = self.layout
		layout.label(text='Texel Density Viewport Panel:')
		layout.prop(self, 'anchorPos', expand=False)
		layout.prop(self, 'offsetX')
		layout.prop(self, 'offsetY')