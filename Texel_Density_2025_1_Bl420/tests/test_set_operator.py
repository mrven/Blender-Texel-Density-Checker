import bpy
import unittest
from .. import utils

class TestTexelDensitySetOperator(unittest.TestCase):
	# Тест кейсы:
	# • в обжект моде 3д вью
	# • в эдит моде 3д вью с/без селектед фейсес
	# • в юв эдиторе с/без синком выделения
	# • в юв эдиторе с/без селектед фейсес
	# • кейсы, когда полигоны не выделены
	# • кейсы, когда нет юв
	# • кейсы, когда юв маленькое
	# • кейсы с несколькими мешами в обжект и эдит моде
	# • кейсы со сменой размера текстур
	# • кейсы со сменой юнитов
	# • кейс, когда нет активного объекта

	#  Лучше всего тесты держать атомарными и делать по одной проверке в функции, чтобы не повышать сложность тестов

	# All Tests start in object mode
	def setUp(self):
		print(f"Current backend: {utils.get_preferences().calculation_backend}")

		if bpy.context.object and bpy.context.object.mode != 'OBJECT':
			try:
				bpy.ops.object.mode_set(mode='OBJECT')
			except Exception:
				pass

		for obj in bpy.data.objects:
			obj.select_set(True)
		bpy.ops.object.delete()

		# Added UV Sphere
		bpy.ops.mesh.primitive_uv_sphere_add(radius=1, enter_editmode=False, align='WORLD', location=(2, 0, 0), scale=(2, 2, 2))
		self.sphere = bpy.context.active_object

		# Added Cube
		bpy.ops.mesh.primitive_cube_add(enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 2, 1))
		self.cube = bpy.context.active_object

		bpy.ops.object.mode_set(mode='OBJECT')

	# All Tests finish clean up and return to object mode
	def tearDown(self):
		# Always return to Object Mode
		if bpy.context.object and bpy.context.object.mode != 'OBJECT':
			try:
				bpy.ops.object.mode_set(mode='OBJECT')
			except Exception:
				pass

		# Clean up scene
		for obj in bpy.data.objects:
			obj.select_set(True)
		bpy.ops.object.delete()

		print(" ")

	# TD Set Single Selected Object in Object Mode
	def test_set_object_mode(self):
		print("----Run Test TD Set (in Object Mode)---")

		area = bpy.context.area
		if not area:
			self.fail("Failed get area")

		if area.type != 'VIEW_3D':
			original_type = area.type
			area.type = 'VIEW_3D'
		else:
			original_type = None

		td = bpy.context.scene.td
		bpy.ops.object.mode_set(mode='OBJECT')
		bpy.ops.object.select_all(action='DESELECT')
		bpy.context.view_layer.objects.active = self.cube
		bpy.context.view_layer.objects.active.select_set(True)

		expected_density = '1.280'
		expected_uv_space = '250.0000'

		for i in range(3):  # Three times check
			with self.subTest(cycle=i):
				try:
					td.density = ''
					td.uv_space = ''
					td.density_set = '1.28'

					result = bpy.ops.texel_density.set()

					print(f"Run {i + 1}: density={td.density}, uv_space={td.uv_space} %")

					self.assertIn('FINISHED', result)
					self.assertEqual(td.density, expected_density)
					self.assertEqual(td.uv_space, expected_uv_space)
				except Exception as e:
					self.fail(f"Test failed on cycle try {i} with exception: {e}")
				finally:
					bpy.ops.object.mode_set(mode='OBJECT')

		if original_type:
			area.type = original_type

def run():
	suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestTexelDensitySetOperator)
	runner = unittest.TextTestRunner()
	runner.run(suite)