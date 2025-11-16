import bpy
import importlib
import pkgutil
import sys


class RunTests(bpy.types.Operator):
    bl_idname = "object.texel_density_run_tests"
    bl_label = "Run Texel Density Tests"
    bl_description = "Run all Texel Density tests"

    def execute(self, context):
        try:
            addon_name = __package__
            tests_pkg_name = f"{addon_name}.tests"
            tests_pkg = importlib.import_module(tests_pkg_name)

            for finder, name, ispkg in pkgutil.iter_modules(tests_pkg.__path__, tests_pkg_name + "."):
                if not ispkg:
                    test_mod = importlib.import_module(name)
                    if hasattr(test_mod, "run") and callable(test_mod.run):
                        self.report({'INFO'}, f"Running {name}.run()")
                        test_mod.run()

            self.report({'INFO'}, "All Texel Density tests completed successfully.")

        except Exception as e:
            self.report({'ERROR'}, f"Error running tests: {e}")
            return {'CANCELLED'}

        return {'FINISHED'}


def register():
    bpy.utils.register_class(RunTests)


def unregister():
    bpy.utils.unregister_class(RunTests)
