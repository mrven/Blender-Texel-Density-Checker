import os
import json
import bpy
from bpy.utils import user_resource

from .utils import get_preferences

saving_enabled = False

def get_prefs_path():
    config_dir = user_resource('CONFIG', path='texel_density', create=True)
    os.makedirs(config_dir, exist_ok=True)
    return os.path.join(config_dir, 'preferences.json')


def save_addon_prefs():
    prefs = bpy.context.preferences.addons[__package__].preferences
    data = {}
    for prop in prefs.bl_rna.properties:
        key = prop.identifier
        if key == "rna_type":
            continue
        value = getattr(prefs, key)
        data[key] = value
    with open(get_prefs_path(), 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)


def load_or_initialize_prefs():
    prefs = bpy.context.preferences.addons[__package__].preferences
    path = get_prefs_path()

    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for k, v in data.items():
                if hasattr(prefs, k):
                    setattr(prefs, k, v)
        except Exception as e:
            print(f"[TD Prefs] Failed to load: {e}")
    else:
        print(f"[TD Prefs] No preferences file found at {path}")
        save_addon_prefs()


def copy_prefs_to_props(force = False):
    props = getattr(bpy.context.scene, "td", None)

    if props is None:
        return

    prefs = bpy.context.preferences.addons[__package__].preferences

    if not getattr(props, "initialized", False) or force:
        props.units = prefs.default_units
        props.texture_size = prefs.default_texture_size
        if prefs.default_texture_size == 'CUSTOM':
            props.custom_width = prefs.default_custom_width
            props.custom_height = prefs.default_custom_height
        props.selected_faces = prefs.default_selected_faces
        props.checker_method = prefs.default_checker_method
        props.checker_type = prefs.default_checker_type
        props.checker_uv_scale = prefs.default_checker_uv_scale
        props.density_set = prefs.default_density_set
        props.set_method = prefs.default_set_method
        props.rescale_anchor = prefs.default_rescale_anchor
        props.select_mode = prefs.default_select_mode
        props.select_type = prefs.default_select_type
        props.select_value = prefs.default_select_value
        if prefs.default_select_type == 'EQUAL':
            props.select_threshold = prefs.default_select_threshold
        props.bake_vc_mode = prefs.default_bake_vc_mode
        if prefs.default_bake_vc_mode in {'TD_FACES_TO_VC', 'TD_ISLANDS_TO_VC'}:
            props.bake_vc_auto_min_max = prefs.default_bake_vc_auto_min_max
            props.bake_vc_min_td = prefs.default_bake_vc_min_td
            props.bake_vc_max_td = prefs.default_bake_vc_max_td
        if prefs.default_bake_vc_mode == 'UV_ISLANDS_TO_VC':
            props.uv_islands_to_vc_mode = prefs.default_uv_islands_to_vc_mode
        if prefs.default_bake_vc_mode == 'UV_SPACE_TO_VC':
            props.bake_vc_min_space = prefs.default_bake_vc_min_space
            props.bake_vc_max_space = prefs.default_bake_vc_max_space
        if prefs.default_bake_vc_mode == 'DISTORTION':
            props.bake_vc_distortion_range = prefs.default_bake_vc_distortion_range
        if prefs.default_bake_vc_mode in {'TD_FACES_TO_VC',
                                          'TD_ISLANDS_TO_VC',
                                          'UV_SPACE_TO_VC',
                                          'DISTORTION'}:
            props.bake_vc_show_gradient = prefs.default_bake_vc_show_gradient

        props.initialized = True


def load_default_prefs():
    default_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "default_prefs.json")
    try:
        with open(default_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[TD Prefs] Failed to load default prefs: {e}")
        return {}


def apply_defaults_from_file():
    prefs = bpy.context.preferences.addons[__package__].preferences
    defaults = load_default_prefs()
    if not defaults:
        return False

    for key, value in defaults.items():
        try:
            prop_type = type(getattr(prefs, key))
            setattr(prefs, key, prop_type(value))
        except Exception as e:
            print(f"[TD Prefs] Failed to apply {key}: {e}")
    return True