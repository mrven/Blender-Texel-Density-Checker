bl_info = {
	"name": "Texel Density Checker",
	"description": "Tools for for checking Texel Density and wasting of uv space",
	"author": "Ivan 'mrven' Vostrikov",
	"version": (1, 0, 3),
	"blender": (2, 7, 8),
	"location": "3D View > Toolshelf > Texel Density Checker",
	"wiki_url": "mrven.ru",
	"category": "Object",
}

import bpy
import bmesh
import math

#-------------------------------------------------------
class Texel_Density_Check(bpy.types.Operator):
	"""Check Density"""
	bl_idname = "object.texel_density_check"
	bl_label = "Check Texel Density"
	bl_options = {'REGISTER', 'UNDO'}
	
	def execute(self, context):
		#save current mode and active object
		actObj = bpy.context.scene.objects.active
		current_selected_obj = bpy.context.selected_objects
		try:
			actObjType = actObj.type
			start_mode = bpy.context.object.mode
		except:
			actObjType = 'None'
			start_mode = 'OBJECT'
		current_mode = start_mode
		
		#proceed if active object is mesh
		if (actObjType == 'MESH' and len(actObj.data.uv_layers) > 0):
			if (bpy.context.object.mode == 'EDIT') and (context.scene.selected_faces == True):
				bpy.ops.object.mode_set(mode='OBJECT')
				if (actObj.scale[0] != 1 or actObj.scale[1] != 1 or actObj.scale[2] != 1):
					self.report({'INFO'}, 'Scale of mesh is don\'t (1, 1, 1). Calculated TD may be incorrect')
				bpy.ops.object.select_all(action='DESELECT')
				actObj.select = True
				bpy.ops.object.duplicate()
				bpy.ops.object.mode_set(mode='EDIT')
				bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')
				#set default values
				Area=0
				gmArea = 0
				textureSizeCur = 1024
				
				#Get texture size from panel
				if bpy.context.scene.texture_size == '0':
					textureSizeCur = 512
				if bpy.context.scene.texture_size == '1':
					textureSizeCur = 1024
				if bpy.context.scene.texture_size == '2':
					textureSizeCur = 2048
				if bpy.context.scene.texture_size == '3':
					textureSizeCur = 4096
				#get bmesh from active object
				bpy.ops.object.mode_set(mode='OBJECT')
				face_count = len(bpy.context.active_object.data.polygons)
				selected_faces = []
				for faceid in range (0, face_count):
					if bpy.context.active_object.data.polygons[faceid].select == True:
						selected_faces.append(faceid)
						
				bpy.ops.object.mode_set(mode='EDIT')
				bm = bmesh.from_edit_mesh(bpy.context.active_object.data)
				bm.faces.ensure_lookup_table()
				for x in selected_faces:
					#set default values for multiplication of vectors (uv and physical area of object)
					multiVector = 0
					gmmultiVector = 0
					#UV Area calculating
					#get uv-coordinates of vertexes of current triangle
					loopA = bm.faces[x].loops[0][bm.loops.layers.uv.active].uv
					loopB = bm.faces[x].loops[1][bm.loops.layers.uv.active].uv
					loopC = bm.faces[x].loops[2][bm.loops.layers.uv.active].uv
					#get multiplication of vectors of current triangle
					multiVector = Vector2dMultiple(loopA, loopB, loopC)
					#Increment area of current tri to total uv area
					Area+=0.5*multiVector

					#Phisical Area calculating
					#get world coordinates of vertexes of current triangle
					gmloopA = bm.faces[x].loops[0].vert.co
					gmloopB = bm.faces[x].loops[1].vert.co
					gmloopC = bm.faces[x].loops[2].vert.co
					#get multiplication of vectors of current triangle
					gmmultiVector = Vector3dMultiple(gmloopA, gmloopB, gmloopC)
					#Increment area of current tri to total phisical area
					gmArea += 0.5*gmmultiVector
					
				bpy.ops.object.mode_set(mode='OBJECT')
				
				if len(selected_faces) > 0:
					#UV Area in percents
					UVspace = Area * 100
					
					#TexelDensity calculating from selected in panel texture size
					TexelDensity = (textureSizeCur*math.sqrt(Area))/(math.sqrt(gmArea)*100)

					#show calculated values on panel
					context.scene.uv_space = '%.3f' % round(UVspace, 3) + ' %'
					context.scene.density = '%.3f' % round(TexelDensity, 3) + ' px/cm'
				else:
					self.report({'INFO'}, 'Faces is don\'t selected')
				
				#delete duplicated object
				bpy.ops.object.delete()
				#select saved object
				for x in current_selected_obj:
					x.select = True
				bpy.context.scene.objects.active = actObj
				bpy.ops.object.mode_set(mode='EDIT')
			#--------------------------------------------------
			#Calculating for all mesh
			else:
				#if start mode = edit, change to object mode
				if current_mode == 'EDIT':
					bpy.ops.object.mode_set(mode='OBJECT')
					current_mode = 'OBJECT'
				#Duplicate active object and triangulate mesh
				if (actObj.scale[0] != 1 or actObj.scale[1] != 1 or actObj.scale[2] != 1):
					self.report({'INFO'}, 'Scale of mesh is don\'t (1, 1, 1). Calculated TD may be incorrect')
				if current_mode == 'OBJECT':
					bpy.ops.object.select_all(action='DESELECT')
					actObj.select = True
					bpy.ops.object.duplicate()
					bpy.ops.object.mode_set(mode='EDIT')
					bpy.ops.mesh.reveal()
					bpy.ops.mesh.select_all(action='DESELECT')
					bpy.ops.mesh.select_all(action='SELECT')
					bpy.ops.mesh.quads_convert_to_tris(quad_method='BEAUTY', ngon_method='BEAUTY')

				#set default values
				Area=0
				gmArea = 0
				textureSizeCur = 1024
				
				#Get texture size from panel
				if bpy.context.scene.texture_size == '0':
					textureSizeCur = 512
				if bpy.context.scene.texture_size == '1':
					textureSizeCur = 1024
				if bpy.context.scene.texture_size == '2':
					textureSizeCur = 2048
				if bpy.context.scene.texture_size == '3':
					textureSizeCur = 4096

				#get bmesh from active object
				bm = bmesh.from_edit_mesh(bpy.context.active_object.data)
				bm.faces.ensure_lookup_table()

				#get faces and round this
				face_count = len(bm.faces)
				for faceid in range (0, face_count):
					#set default values for multiplication of vectors (uv and physical area of object)
					multiVector = 0
					gmmultiVector = 0
					#UV Area calculating
					#get uv-coordinates of vertexes of current triangle
					loopA = bm.faces[faceid].loops[0][bm.loops.layers.uv.active].uv
					loopB = bm.faces[faceid].loops[1][bm.loops.layers.uv.active].uv
					loopC = bm.faces[faceid].loops[2][bm.loops.layers.uv.active].uv
					#get multiplication of vectors of current triangle
					multiVector = Vector2dMultiple(loopA, loopB, loopC)
					#Increment area of current tri to total uv area
					Area+=0.5*multiVector

					#Phisical Area calculating
					#get world coordinates of vertexes of current triangle
					gmloopA = bm.faces[faceid].loops[0].vert.co
					gmloopB = bm.faces[faceid].loops[1].vert.co
					gmloopC = bm.faces[faceid].loops[2].vert.co
					#get multiplication of vectors of current triangle
					gmmultiVector = Vector3dMultiple(gmloopA, gmloopB, gmloopC)
					#Increment area of current tri to total phisical area
					gmArea += 0.5*gmmultiVector
					
				#UV Area in percents
				UVspace = Area * 100
				
				#TexelDensity calculating from selected in panel texture size
				TexelDensity = (textureSizeCur*math.sqrt(Area))/(math.sqrt(gmArea)*100)
				
				#show calculated values on panel
				context.scene.uv_space = '%.3f' % round(UVspace, 3) + ' %'
				context.scene.density = '%.3f' % round(TexelDensity, 3) + ' px/cm'
				
				#set object mode and delete duplicated object
				bpy.ops.object.mode_set(mode='OBJECT')
				bpy.ops.object.delete()
				#select saved object and return into initial mode
				for x in current_selected_obj:
					x.select = True
				bpy.context.scene.objects.active = actObj
				
				bpy.ops.object.mode_set(mode=start_mode)
			
		else:
			
			self.report({'ERROR'}, 'Active object is not mesh or don\'t have UV')

		return {'FINISHED'}

#-------------------------------------------------------
class Texel_Density_Set(bpy.types.Operator):
	"""Set Density"""
	bl_idname = "object.texel_density_set"
	bl_label = "Set Texel Density"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		message = "TD is changed"
		enSetTD = True
		actObj = bpy.context.scene.objects.active
		current_selected_obj = bpy.context.selected_objects
		
		try:
			bpy.ops.object.texel_density_check()
		except:
			message = "Try Calculate TD before"
			enSetTD = False
		densityCurrentValue = float(context.scene.density.strip(' px/cm'))
		try:
			densityNewValue = float(context.scene.density_set)
		except:
			densityNewValue = densityCurrentValue
			message = "Density value is wrong"
		if enSetTD:
			if (densityNewValue != 0):
				if (bpy.context.object.mode == 'EDIT') and (context.scene.selected_faces == True):
					scaleFac = densityNewValue/densityCurrentValue
					#check opened image editor window
					IE_area = 0
					flag_exist_area = False
					for area in range(len(bpy.context.screen.areas)):
						if bpy.context.screen.areas[area].type == 'IMAGE_EDITOR':
							IE_area = area
							flag_exist_area = True
							bpy.context.screen.areas[area].type = 'CONSOLE'
					
					bpy.context.area.type = 'IMAGE_EDITOR'
					bpy.ops.uv.select_all(action = 'SELECT')
					bpy.ops.transform.resize(value=(scaleFac, scaleFac, 1))
					bpy.ops.uv.average_islands_scale()
					bpy.context.area.type = 'VIEW_3D'
					
					bpy.ops.object.texel_density_check()
					
					if flag_exist_area == True:
						bpy.context.screen.areas[IE_area].type = 'IMAGE_EDITOR'

				else:
					scaleFac = densityNewValue/densityCurrentValue
					#check opened image editor window
					IE_area = 0
					flag_exist_area = False
					for area in range(len(bpy.context.screen.areas)):
						if bpy.context.screen.areas[area].type == 'IMAGE_EDITOR':
							IE_area = area
							flag_exist_area = True
							bpy.context.screen.areas[area].type = 'CONSOLE'
							
					start_mode = bpy.context.object.mode
					
					if start_mode == 'OBJECT':
						bpy.ops.object.mode_set(mode='EDIT')
					
					bpy.ops.mesh.reveal()
					bpy.ops.mesh.select_all(action='DESELECT')
					bpy.ops.mesh.select_all(action='SELECT')
					
					bpy.context.area.type = 'IMAGE_EDITOR'
					bpy.ops.uv.select_all(action = 'SELECT')
					bpy.ops.transform.resize(value=(scaleFac, scaleFac, 1))
					bpy.ops.uv.average_islands_scale()
					bpy.context.area.type = 'VIEW_3D'
					bpy.ops.object.mode_set(mode=start_mode)
					
					bpy.ops.object.texel_density_check()
					
					if flag_exist_area == True:
						bpy.context.screen.areas[IE_area].type = 'IMAGE_EDITOR'
			else:
				message = "Density must be greater than 0"
		self.report({'INFO'}, message)
		
		for x in current_selected_obj:
			x.select = True
		bpy.context.scene.objects.active = actObj
				
		return {'FINISHED'}
		
#-------------------------------------------------------
class Texel_Density_Copy(bpy.types.Operator):
	"""Copy Density"""
	bl_idname = "object.texel_density_copy"
	bl_label = "Copy Texel Density"
	bl_options = {'REGISTER', 'UNDO'}

	def execute(self, context):
		message = "TD is copied"
		enCopyTD = True
		current_selected_obj = bpy.context.selected_objects
		actObj = bpy.context.scene.objects.active
		try:
			bpy.ops.object.texel_density_check()
		except:
			message = "Try Calculate TD before"
			enCopyTD = False
		densitySourceObject = float(context.scene.density.strip(' px/cm'))
		
		if enCopyTD:
			for x in current_selected_obj:
				bpy.ops.object.select_all(action='DESELECT')
				if (x.type == 'MESH' and len(x.data.uv_layers) > 0):
					x.select = True
					bpy.context.scene.objects.active = x
					bpy.ops.object.texel_density_check()
					densityCurrentValue = float(context.scene.density.strip(' px/cm'))
					scaleFac = densitySourceObject/densityCurrentValue
				
					IE_area = 0
					flag_exist_area = False
					for area in range(len(bpy.context.screen.areas)):
						if bpy.context.screen.areas[area].type == 'IMAGE_EDITOR':
							IE_area = area
							flag_exist_area = True
							bpy.context.screen.areas[area].type = 'CONSOLE'
					
					bpy.ops.object.mode_set(mode='EDIT')
					
					bpy.ops.mesh.reveal()
					bpy.ops.mesh.select_all(action='DESELECT')
					bpy.ops.mesh.select_all(action='SELECT')
					
					bpy.context.area.type = 'IMAGE_EDITOR'
					bpy.ops.uv.select_all(action = 'SELECT')
					bpy.ops.transform.resize(value=(scaleFac, scaleFac, 1))
					bpy.ops.uv.average_islands_scale()
					bpy.context.area.type = 'VIEW_3D'
					bpy.ops.object.mode_set(mode='OBJECT')
				
					if flag_exist_area == True:
						bpy.context.screen.areas[IE_area].type = 'IMAGE_EDITOR'
		
		for x in current_selected_obj:
			x.select = True
		bpy.context.scene.objects.active = actObj
		
		self.report({'INFO'}, message)
		return {'FINISHED'}
		
#-------------------------------------------------------
#FUNCTIONS
def Vector2dMultiple(A, B, C):
	return abs((B[0]- A[0])*(C[1]- A[1])-(B[1]- A[1])*(C[0]- A[0]))

def Vector3dMultiple(A, B, C):
	result = 0
	vectorX = 0
	vectorY = 0
	vectorZ = 0
	
	vectorX = (B[1]- A[1])*(C[2]- A[2])-(B[2]- A[2])*(C[1]- A[1])
	vectorY = -1*((B[0]- A[0])*(C[2]- A[2])-(B[2]- A[2])*(C[0]- A[0]))
	vectorZ = (B[0]- A[0])*(C[1]- A[1])-(B[1]- A[1])*(C[0]- A[0])
	
	result = math.sqrt(math.pow(vectorX, 2) + math.pow(vectorY, 2) + math.pow(vectorZ, 2))
	return result

#-------------------------------------------------------
# Panel 
class VIEW3D_PT_texel_density_checker(bpy.types.Panel):
	bl_label = "Texel Density Checker"
	bl_space_type = "VIEW_3D"
	bl_region_type = "TOOLS"
	bl_options = {'DEFAULT_CLOSED'}

	@classmethod
	def poll(self, context):
		return (context.object is not None)

	def draw(self, context):
		layout = self.layout
		layout.label("Texture Size:")
		row = layout.row()
		row.prop(context.scene, 'texture_size', expand=False)
		if context.object.mode == 'EDIT':
			layout.separator()
			layout.prop(context.scene, "selected_faces", text="Selected Faces")
		layout.separator()
		layout.label("Filling UV Space:")
		row = layout.row()
		row.prop(context.scene, "uv_space")
		row.enabled = False
		layout.label("Texel Density:")
		row = layout.row()
		row.prop(context.scene, "density")
		row.enabled = False
		layout.operator("object.texel_density_check", text="Calculate TD")
		layout.separator()
		layout.label("Set Texel Density")
		layout.prop(context.scene, "density_set")
		layout.operator("object.texel_density_set", text="Set My TD")
		if context.object.mode == 'OBJECT':
			layout.separator()
			layout.operator("object.texel_density_copy", text="TD from Active to Others")
	
		
#-------------------------------------------------------		
def register():
	bpy.utils.register_module(__name__)
	bpy.types.Scene.uv_space = bpy.props.StringProperty(
		name="UV Space",
		description="wasting of uv space",
		default="0")
	bpy.types.Scene.density = bpy.props.StringProperty(
		name="Density",
		description="Texel Density",
		default="0")
	bpy.types.Scene.density_set = bpy.props.StringProperty(
		name="Density",
		description="Texel Density",
		default="0")
	tex_size = (('0','512px',''),('1','1024px',''),('2','2048px',''),('3','4096px',''))
	bpy.types.Scene.texture_size = bpy.props.EnumProperty(name="Size", items = tex_size)
	bpy.types.Scene.selected_faces = bpy.props.BoolProperty(
		name="Selected Faces",
		description="Operate only with selected faces",
		default = False) 

def unregister():
	bpy.utils.unregister_module(__name__)
	del bpy.types.Scene.texture_size
	del bpy.types.Scene.uv_space
	del bpy.types.Scene.density
	del bpy.types.Scene.density_set
	del bpy.types.Scene.selected_faces

if __name__ == "__main__":
	register()