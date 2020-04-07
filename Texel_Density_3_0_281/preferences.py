import bpy

from bpy.props import (
		StringProperty,
		EnumProperty,
        )


def Filter_Gradient_Offset_X(self, context):
	offset_x_filtered = bpy.context.preferences.addons[__package__].preferences['offset_x'].replace(',', '.')
	
	try:
		offset_x = int(offset_x_filtered)
	except:
		offset_x = 20

	if (offset_x < 0):
		offset_x = 20
	
	bpy.context.preferences.addons[__package__].preferences['offset_x'] = str(offset_x)
	return None


def Filter_Gradient_Offset_Y(self, context):	
	offset_y_filtered = bpy.context.preferences.addons[__package__].preferences['offset_y'].replace(',', '.')
	
	try:
		offset_y = int(offset_y_filtered)
	except:
		offset_y = 20

	if (offset_y < 0):
		offset_y = 20

	bpy.context.preferences.addons[__package__].preferences['offset_y'] = str(offset_y)
	return None


class TD_Addon_Preferences(bpy.types.AddonPreferences):
	bl_idname = __package__

	offset_x: StringProperty(
		name="Offset X",
		description="Offset X from Anchor",
		default="250", update = Filter_Gradient_Offset_X)

	offset_y: StringProperty(
		name="Offset Y",
		description="Offset Y from Anchor",
		default="20", update = Filter_Gradient_Offset_Y)

	anchor_pos_list = (('LEFT_TOP','Left Top',''),('LEFT_BOTTOM','Left Bottom',''), 
						('RIGHT_TOP','Right Top',''), ('RIGHT_BOTTOM','Right Bottom',''))
	anchor_pos: EnumProperty(name="Position Anchor", items = anchor_pos_list, default = 'LEFT_BOTTOM')

	def draw(self, context):
		layout = self.layout
		layout.label(text='Texel Density Gradient Position:')
		layout.prop(self, 'anchor_pos', expand=False)
		layout.prop(self, 'offset_x')
		layout.prop(self, 'offset_y')


classes = (
    TD_Addon_Preferences,
)	


def register():
	for cls in classes:
		bpy.utils.register_class(cls)


def unregister():
	for cls in reversed(classes):
		bpy.utils.unregister_class(cls)