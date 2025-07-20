import bpy
import unittest
from .. import utils

class TestTexelDensityCheckOperator(unittest.TestCase):
	# TODO: Добавлять в сцену на старте объекта, чтобы была возможность тестить как один, так и несколько объектов
	# Возможно даже стоит добавить что-то из НЕ мешей и перебирать в тестах разные варианты активного объекта

	def setUp(self):
		print(f"Current backend: {utils.get_preferences().calculation_backend}")

		if bpy.context.object and bpy.context.object.mode != 'OBJECT':
			try:
				bpy.ops.object.mode_set(mode='OBJECT')
			except Exception:
				pass
		# Удаляем все объекты со сцены
		for obj in bpy.data.objects:
			obj.select_set(True)
		bpy.ops.object.delete()

		# Создаём новый куб с UV
		bpy.ops.mesh.primitive_cube_add(enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(1, 2, 1))
		self.obj = bpy.context.active_object

		# Переходим в OBJECT режим
		bpy.ops.object.mode_set(mode='OBJECT')

	def tearDown(self):
		# Всегда выйти из edit-mode, даже если тест неудачный
		if bpy.context.object and bpy.context.object.mode != 'OBJECT':
			try:
				bpy.ops.object.mode_set(mode='OBJECT')
			except Exception:
				pass

		# Удаляем все объекты после теста, чтобы чисто
		for obj in bpy.data.objects:
			obj.select_set(True)
		bpy.ops.object.delete()

		print(" ")

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

	# TD Check Single Selected Object in Object Mode
	def test_check_object_mode(self):
		print("----Run Test TD Check (in Object Mode)---")

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

		expected_density = '0.515'
		expected_uv_space = '37.5000 %'

		for i in range(3):  # Проверим трижды подряд
			with self.subTest(cycle=i):
				try:
					td.density = ''
					td.uv_space = ''

					result = bpy.ops.texel_density.check()

					print(f"Run {i + 1}: density={td.density}, uv_space={td.uv_space}")

					self.assertIn('FINISHED', result)
					self.assertEqual(td.density, expected_density)
					self.assertEqual(td.uv_space, expected_uv_space)
				except Exception as e:
					self.fail(f"Test failed on cycle try {i} with exception: {e}")
				finally:
					bpy.ops.object.mode_set(mode='OBJECT')

		if original_type:
			area.type = original_type

	# TD Check Single Selected Object in Edit Mode
	def test_check_edit_mode(self):
		print("----Run Test TD Check (in Edit Mode)---")

		area = bpy.context.area
		if not area:
			self.fail("Failed get area")

		if area.type != 'VIEW_3D':
			original_type = area.type
			area.type = 'VIEW_3D'
		else:
			original_type = None

		td = bpy.context.scene.td
		obj = bpy.context.active_object

		td.density = ''
		td.uv_space = ''

		expected_results = {
			0: ('0.453', '6.2500 %'),
			1: ('0.640', '6.2500 %'),
			2: ('0.453', '6.2500 %'),
			3: ('0.640', '6.2500 %'),
			4: ('0.453', '6.2500 %'),
			5: ('0.453', '6.2500 %'),
		}

		total_faces = len(obj.data.polygons)

		for i in range(total_faces):
			with self.subTest(face=i):
				try:
					bpy.ops.object.mode_set(mode='EDIT')
					bpy.ops.mesh.select_all(action='DESELECT')

					bpy.ops.object.mode_set(mode='OBJECT')
					obj.data.polygons[i].select = True

					bpy.ops.object.mode_set(mode='EDIT')
					result = bpy.ops.texel_density.check()

					actual_density = td.density
					actual_uv_space = td.uv_space

					print(f"[Face {i}] Density = {actual_density}, UV Space = {actual_uv_space}")

					bpy.ops.object.mode_set(mode='OBJECT')

					self.assertIn('FINISHED', result)
					self.assertEqual(actual_density, expected_results[i][0], f"Density mismatch on face {i}")
					self.assertEqual(actual_uv_space, expected_results[i][1], f"UV Space mismatch on face {i}")
				except Exception as e:
					self.fail(f"Test failed on face {i} with exception: {e}")
				finally:
					bpy.ops.object.mode_set(mode='OBJECT')

		if original_type:
			area.type = original_type


def run():
	suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestTexelDensityCheckOperator)
	runner = unittest.TextTestRunner()
	runner.run(suite)
