# SPDX-FileCopyrightText: 2009-2023 Blender Authors
#
# SPDX-License-Identifier: GPL-2.0-or-later

from __future__ import annotations

# support reloading sub-modules
if "bpy" in locals():
    from importlib import reload
    _modules_loaded[:] = [reload(val) for val in _modules_loaded]
    del reload

_modules = [
    "add_mesh_torus",
    "anim",
    "assets",
    "bone_selection_sets",
    "clip",
    "connect_to_output",
    "console",
    "constraint",
    "copy_global_transform",
    "file",
    "geometry_nodes",
    "grease_pencil",
    "image",
    "image_as_planes",
    "mesh",
    "node",
    "object",
    "object_align",
    "object_quick_effects",
    "object_randomize_transform",
    "presets",
    "render",
    "rigidbody",
    "screen_play_rendered_anim",
    "sequencer",
    "spreadsheet",
    "userpref",
    "uvcalc_follow_active",
    "uvcalc_lightmap",
    "uvcalc_transform",
    "vertexpaint_dirt",
    "view3d",
    "world",
    "wm",
]

import bpy

if bpy.app.build_options.freestyle:
    _modules.append("freestyle")

__import__(name=__name__, fromlist=_modules)
_namespace = globals()
_modules_loaded = [_namespace[name] for name in _modules]
del _namespace


def register():
    from bpy.utils import register_class
    from . import (
        bone_selection_sets,
        copy_global_transform,
    )

    for mod in _modules_loaded:
        for cls in mod.classes:
            register_class(cls)

    bone_selection_sets.register()
    copy_global_transform.register()
    bpy.types.Scene.left_pie = {}
    bpy.types.Scene.left_pie_name = {}
    bpy.types.Scene.left_pie_icon = {}
    bpy.types.Scene.right_pie = {}
    bpy.types.Scene.right_pie_name = {}
    bpy.types.Scene.right_pie_icon = {}
    bpy.types.Scene.down_pie = {}
    bpy.types.Scene.down_pie_name = {}
    bpy.types.Scene.down_pie_icon = {}
    bpy.types.Scene.up_pie = {}
    bpy.types.Scene.up_pie_name = {}
    bpy.types.Scene.up_pie_icon = {}
    bpy.types.Scene.ul_pie = {}
    bpy.types.Scene.ul_pie_name = {}
    bpy.types.Scene.ul_pie_icon = {}
    bpy.types.Scene.ur_pie = {}
    bpy.types.Scene.ur_pie_name = {}
    bpy.types.Scene.ur_pie_icon = {}
    bpy.types.Scene.dl_pie = {}
    bpy.types.Scene.dl_pie_name = {}
    bpy.types.Scene.dl_pie_icon = {}
    bpy.types.Scene.dr_pie = {}
    bpy.types.Scene.dr_pie_name = {}
    bpy.types.Scene.dr_pie_icon = {}


def unregister():
    from bpy.utils import unregister_class
    from . import (
        bone_selection_sets,
        copy_global_transform,
    )

    bone_selection_sets.unregister()
    copy_global_transform.unregister()

    for mod in reversed(_modules_loaded):
        for cls in reversed(mod.classes):
            if cls.is_registered:
                unregister_class(cls)
    del bpy.types.Scene.left_pie
    del bpy.types.Scene.left_pie_name
    del bpy.types.Scene.left_pie_icon
    del bpy.types.Scene.right_pie
    del bpy.types.Scene.right_pie_name
    del bpy.types.Scene.right_pie_icon
    del bpy.types.Scene.down_pie
    del bpy.types.Scene.down_pie_name
    del bpy.types.Scene.down_pie_icon
    del bpy.types.Scene.up_pie
    del bpy.types.Scene.up_pie_name
    del bpy.types.Scene.up_pie_icon
    del bpy.types.Scene.ul_pie
    del bpy.types.Scene.ul_pie_name
    del bpy.types.Scene.ul_pie_icon
    del bpy.types.Scene.ur_pie
    del bpy.types.Scene.ur_pie_name
    del bpy.types.Scene.ur_pie_icon
    del bpy.types.Scene.dl_pie
    del bpy.types.Scene.dl_pie_name
    del bpy.types.Scene.dl_pie_icon
    del bpy.types.Scene.dr_pie
    del bpy.types.Scene.dr_pie_name
    del bpy.types.Scene.dr_pie_icon
