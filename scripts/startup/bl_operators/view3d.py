# SPDX-FileCopyrightText: 2011-2023 Blender Authors
#
# SPDX-License-Identifier: GPL-2.0-or-later

import bpy
from bpy.types import (
    Operator,
    FileHandler,
    Menu,
)
from bpy.props import (
    BoolProperty,
    EnumProperty,
)

bl_file_extensions_image_and_movie = ";".join((
    *bpy.path.extensions_image,
    *bpy.path.extensions_movie,
))


class VIEW3D_OT_edit_mesh_extrude_individual_move(Operator):
    """Extrude each individual face separately along local normals"""
    bl_label = "Extrude Individual and Move"
    bl_idname = "view3d.edit_mesh_extrude_individual_move"

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def execute(self, context):
        from bpy_extras.object_utils import object_report_if_active_shape_key_is_locked

        ob = context.object
        if object_report_if_active_shape_key_is_locked(ob, self):
            return {'CANCELLED'}

        mesh = ob.data
        select_mode = context.tool_settings.mesh_select_mode

        totface = mesh.total_face_sel
        totedge = mesh.total_edge_sel
        # totvert = mesh.total_vert_sel

        if select_mode[2] and totface == 1:
            bpy.ops.mesh.extrude_region_move(
                'INVOKE_REGION_WIN',
                TRANSFORM_OT_translate={
                    "orient_type": 'NORMAL',
                    "constraint_axis": (False, False, True),
                    "release_confirm": False,
                },
            )
        elif select_mode[2] and totface > 1:
            bpy.ops.mesh.extrude_faces_move(
                'INVOKE_REGION_WIN',
                TRANSFORM_OT_shrink_fatten={
                    "release_confirm": False,
                },
            )
        elif select_mode[1] and totedge >= 1:
            bpy.ops.mesh.extrude_edges_move(
                'INVOKE_REGION_WIN',
                TRANSFORM_OT_translate={
                    "release_confirm": False,
                },
            )
        else:
            bpy.ops.mesh.extrude_vertices_move(
                'INVOKE_REGION_WIN',
                TRANSFORM_OT_translate={
                    "release_confirm": False,
                },
            )

        # ignore return from operators above because they are 'RUNNING_MODAL',
        # and cause this one not to be freed. #24671.
        return {'FINISHED'}

    def invoke(self, context, _event):
        return self.execute(context)


class VIEW3D_OT_edit_mesh_extrude_move(Operator):
    """Extrude region together along the average normal"""
    bl_label = "Extrude and Move on Normals"
    bl_idname = "view3d.edit_mesh_extrude_move_normal"

    dissolve_and_intersect: BoolProperty(
        name="Dissolve and Intersect",
        default=False,
        description="Dissolves adjacent faces and intersects new geometry",
    )

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    @staticmethod
    def extrude_region(operator, context, use_vert_normals, dissolve_and_intersect):
        from bpy_extras.object_utils import object_report_if_active_shape_key_is_locked

        ob = context.object
        if object_report_if_active_shape_key_is_locked(ob, operator):
            return {'CANCELLED'}

        mesh = ob.data

        totface = mesh.total_face_sel
        totedge = mesh.total_edge_sel
        # totvert = mesh.total_vert_sel

        if totface >= 1:
            if use_vert_normals:
                bpy.ops.mesh.extrude_region_shrink_fatten(
                    'INVOKE_REGION_WIN',
                    TRANSFORM_OT_shrink_fatten={
                        "release_confirm": False,
                    },
                )
            elif dissolve_and_intersect:
                bpy.ops.mesh.extrude_manifold(
                    'INVOKE_REGION_WIN',
                    MESH_OT_extrude_region={
                        "use_dissolve_ortho_edges": True,
                    },
                    TRANSFORM_OT_translate={
                        "orient_type": 'NORMAL',
                        "constraint_axis": (False, False, True),
                        "release_confirm": False,
                    },
                )
            else:
                bpy.ops.mesh.extrude_region_move(
                    'INVOKE_REGION_WIN',
                    TRANSFORM_OT_translate={
                        "orient_type": 'NORMAL',
                        "constraint_axis": (False, False, True),
                        "release_confirm": False,
                    },
                )

        elif totedge == 1:
            bpy.ops.mesh.extrude_region_move(
                'INVOKE_REGION_WIN',
                TRANSFORM_OT_translate={
                    # Don't set the constraint axis since users will expect MMB
                    # to use the user setting, see: #61637
                    # "orient_type": 'NORMAL',
                    # Not a popular choice, too restrictive for retopology.
                    # "constraint_axis": (True, True, False),
                    "constraint_axis": (False, False, False),
                    "release_confirm": False,
                })
        else:
            bpy.ops.mesh.extrude_region_move(
                'INVOKE_REGION_WIN',
                TRANSFORM_OT_translate={
                    "release_confirm": False,
                },
            )

        # ignore return from operators above because they are 'RUNNING_MODAL',
        # and cause this one not to be freed. #24671.
        return {'FINISHED'}

    def execute(self, context):
        return VIEW3D_OT_edit_mesh_extrude_move.extrude_region(self, context, False, self.dissolve_and_intersect)

    def invoke(self, context, _event):
        return self.execute(context)


class VIEW3D_OT_edit_mesh_extrude_shrink_fatten(Operator):
    """Extrude region together along local normals"""
    bl_label = "Extrude and Move on Individual Normals"
    bl_idname = "view3d.edit_mesh_extrude_move_shrink_fatten"

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def execute(self, context):
        return VIEW3D_OT_edit_mesh_extrude_move.extrude_region(self, context, True, False)

    def invoke(self, context, _event):
        return self.execute(context)


class VIEW3D_OT_edit_mesh_extrude_manifold_normal(Operator):
    """Extrude manifold region along normals"""
    bl_label = "Extrude Manifold Along Normals"
    bl_idname = "view3d.edit_mesh_extrude_manifold_normal"

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def execute(self, context):
        from bpy_extras.object_utils import object_report_if_active_shape_key_is_locked

        if object_report_if_active_shape_key_is_locked(context.object, self):
            return {'CANCELLED'}
        bpy.ops.mesh.extrude_manifold(
            'INVOKE_REGION_WIN',
            MESH_OT_extrude_region={
                "use_dissolve_ortho_edges": True,
            },
            TRANSFORM_OT_translate={
                "orient_type": 'NORMAL',
                "constraint_axis": (False, False, True),
                "release_confirm": False,
            },
        )
        return {'FINISHED'}

    def invoke(self, context, _event):
        return self.execute(context)


class VIEW3D_OT_transform_gizmo_set(Operator):
    """Set the current transform gizmo"""
    bl_label = "Transform Gizmo Set"
    bl_options = {'REGISTER', 'UNDO'}
    bl_idname = "view3d.transform_gizmo_set"

    extend: BoolProperty(
        name="Extend",
        default=False,
    )
    type: EnumProperty(
        name="Type",
        items=(
            ('TRANSLATE', "Move", ""),
            ('ROTATE', "Rotate", ""),
            ('SCALE', "Scale", ""),
        ),
        options={'ENUM_FLAG'},
    )

    @classmethod
    def poll(cls, context):
        area = context.area
        return area and (area.type == 'VIEW_3D')

    def execute(self, context):
        space_data = context.space_data
        space_data.show_gizmo = True
        attrs = ("show_gizmo_object_translate", "show_gizmo_object_rotate", "show_gizmo_object_scale")
        attr_active = tuple(
            attrs[('TRANSLATE', 'ROTATE', 'SCALE').index(t)]
            for t in self.type
        )
        if self.extend:
            for attr in attrs:
                if attr in attr_active:
                    setattr(space_data, attr, True)
        else:
            for attr in attrs:
                setattr(space_data, attr, attr in attr_active)
        return {'FINISHED'}

    def invoke(self, context, event):
        if not self.properties.is_property_set("extend"):
            self.extend = event.shift
        return self.execute(context)


class VIEW3D_FH_empty_image(FileHandler):
    bl_idname = "VIEW3D_FH_empty_image"
    bl_label = "Add empty image"
    bl_import_operator = "OBJECT_OT_empty_image_add"
    bl_file_extensions = bl_file_extensions_image_and_movie

    @classmethod
    def poll_drop(cls, context):
        if not context.space_data or context.space_data.type != 'VIEW_3D':
            return False
        rv3d = context.space_data.region_3d
        return rv3d.view_perspective == 'PERSP' or rv3d.view_perspective == 'ORTHO'


class VIEW3D_FH_camera_background_image(FileHandler):
    bl_idname = "VIEW3D_FH_camera_background_image"
    bl_label = "Add camera background image"
    bl_import_operator = "VIEW3D_OT_camera_background_image_add"
    bl_file_extensions = bl_file_extensions_image_and_movie

    @classmethod
    def poll_drop(cls, context):
        if not context.space_data or context.space_data.type != 'VIEW_3D':
            return False
        rv3d = context.space_data.region_3d
        return rv3d.view_perspective == 'CAMERA'


class VIEW3D_FH_vdb_volume(FileHandler):
    bl_idname = "VIEW3D_FH_vdb_volume"
    bl_label = "OpenVDB volume"
    bl_import_operator = "OBJECT_OT_volume_import"
    bl_file_extensions = ".vdb"

    @classmethod
    def poll_drop(cls, context):
        return context.space_data and context.space_data.type == 'VIEW_3D'


# Custom Operators
class VIEW3D_OT_box_lasso(bpy.types.Operator):
    """Toggle between box and lasso select"""
    bl_idname = "view3d.box_lasso"
    bl_label = "    Box-Lasso"

    def execute(self, context):
        tool_settings = context.tool_settings
        obj = context.active_object
        object_mode = 'OBJECT' if obj is None else obj.mode
        from bl_ui.space_toolsystem_common import ToolSelectPanelHelper
        tool = ToolSelectPanelHelper.tool_active_from_context(context)

        if tool.idname == "builtin.select_box":
            for i in range(2):
                bpy.ops.wm.tool_set_by_id(name="builtin.select_lasso")
        else:
            for i in range(2):
                bpy.ops.wm.tool_set_by_id(name="builtin.select_box")

        return {'FINISHED'}


class VIEW3D_OT_box_select(bpy.types.Operator):
    """Switch to box select"""
    bl_idname = "view3d.box_select"
    bl_label = "    Box"

    def execute(self, context):
        tool_settings = context.tool_settings
        obj = context.active_object
        object_mode = 'OBJECT' if obj is None else obj.mode
        from bl_ui.space_toolsystem_common import ToolSelectPanelHelper
        tool = ToolSelectPanelHelper.tool_active_from_context(context)

        if hasattr(tool, "idname"):
            for i in range(2):
                if tool.idname == "builtin.select_circle" or tool.idname == "builtin.select_lasso" or tool.idname == "builtin.select":
                    bpy.ops.wm.tool_set_by_id(name="builtin.select_box")
                else:
                    bpy.ops.wm.tool_set_by_id(name="builtin.select_box", as_fallback=True)

        return {'FINISHED'}


class VIEW3D_OT_circle_select(bpy.types.Operator):
    """Switch to circle select"""
    bl_idname = "view3d.circle_select"
    bl_label = "    Circle"

    def execute(self, context):
        tool_settings = context.tool_settings
        obj = context.active_object
        object_mode = 'OBJECT' if obj is None else obj.mode
        from bl_ui.space_toolsystem_common import ToolSelectPanelHelper
        tool = ToolSelectPanelHelper.tool_active_from_context(context)

        for i in range(2):
            if tool.idname == "builtin.select_box" or tool.idname == "builtin.select_lasso" or tool.idname == "builtin.select":
                bpy.ops.wm.tool_set_by_id(name="builtin.select_circle")
            else:
                bpy.ops.wm.tool_set_by_id(name="builtin.select_circle", as_fallback=True)

        return {'FINISHED'}


class VIEW3D_OT_lasso_select(bpy.types.Operator):
    """Switch to lasso select"""
    bl_idname = "view3d.lasso_select"
    bl_label = "    Lasso"

    def execute(self, context):
        tool_settings = context.tool_settings
        obj = context.active_object
        object_mode = 'OBJECT' if obj is None else obj.mode
        from bl_ui.space_toolsystem_common import ToolSelectPanelHelper
        tool = ToolSelectPanelHelper.tool_active_from_context(context)

        for i in range(2):
            if tool.idname == "builtin.select_circle" or tool.idname == "builtin.select_box" or tool.idname == "builtin.select":
                bpy.ops.wm.tool_set_by_id(name="builtin.select_lasso")
            else:
                bpy.ops.wm.tool_set_by_id(name="builtin.select_lasso", as_fallback=True)

        return {'FINISHED'}


class VIEW3D_OT_tweak(bpy.types.Operator):
    """Switch to tweak"""
    bl_idname = "view3d.tweak"
    bl_label = "    Tweak"

    def execute(self, context):
        tool_settings = context.tool_settings
        obj = context.active_object
        object_mode = 'OBJECT' if obj is None else obj.mode
        from bl_ui.space_toolsystem_common import ToolSelectPanelHelper
        tool = ToolSelectPanelHelper.tool_active_from_context(context)

        for i in range(2):
            if tool.idname == "builtin.select_circle" or tool.idname == "builtin.select_box" or tool.idname == "builtin.select_lasso":
                bpy.ops.wm.tool_set_by_id(name="builtin.select")
            else:
                bpy.ops.wm.tool_set_by_id(name="builtin.select", as_fallback=True)

        return {'FINISHED'}


class VIEW3D_OT_directional_warning(bpy.types.Operator):
    """Operator is unavailable"""
    bl_idname = "view3d.directional_warning"
    bl_label = "Directional Warning"

    def invoke(self, context, event):
        self.report(
            {'INFO'},
            "This operator is either unavailable in this context or it may have been set to directional control: Edit->Preferences->Luke's Custom Build->Drag Select->Drag Direction")

        return {'FINISHED'}


class VIEW3D_MT_drag_misc(Menu):
    bl_label = "Miscellaneous Drag"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        tool_settings = context.tool_settings
        inputs = context.preferences.inputs
        view = context.space_data
        obj = context.active_object
        object_mode = 'OBJECT' if obj is None else obj.mode

        if hasattr(view, 'shading'):
            shading = view.shading
            overlay = view.overlay
            has_pose_mode = (
                (object_mode == 'POSE') or
                (object_mode == 'WEIGHT_PAINT' and context.pose_object is not None)
            )
            if has_pose_mode:
                draw_depressed = overlay.show_xray_bone
            elif shading.type == 'WIREFRAME':
                draw_depressed = shading.show_xray_wireframe
            else:
                draw_depressed = shading.show_xray
            if shading.type == 'WIREFRAME':
                xray = shading.show_xray_wireframe and shading.xray_alpha_wireframe < 1.0
            elif shading.type == 'SOLID':
                xray = shading.show_xray and shading.xray_alpha < 1.0
            else:
                xray = False
            if xray:
                fdot_draw_depressed = not overlay.show_face_center_xray
            else:
                fdot_draw_depressed = overlay.show_face_center
        else:
            draw_draw_depressed = False
            fdot_draw_depressed = False

        from bl_ui.space_toolsystem_common import ToolSelectPanelHelper
        tool = ToolSelectPanelHelper.tool_active_from_context(context)

        enable_backface_button = True
        depress_bface = False

        if inputs.drag_mode == 'SPLIT' and tool == "builtin.select_lasso":
            depress_bface = inputs.backface_lasso != 'DEFAULT'

            if inputs.drag_direction_lasso == 'LEFT_RIGHT' or inputs.drag_direction_lasso == 'UP_DOWN':
                if inputs.drag_direction_mode == 'EVERYTHING' or (
                        inputs.drag_direction_mode == 'SELECTIVE' and inputs.direction_backface):
                    enable_backface_button = False
        elif inputs.drag_mode == 'SPLIT' and tool == "builtin.select_circle":
            depress_bface = inputs.backface_circle != 'DEFAULT'
        else:
            depress_bface = inputs.backface_box != 'DEFAULT'

            if inputs.drag_mode == 'SPLIT' and inputs.drag_direction_box == 'LEFT_RIGHT' or inputs.drag_direction_box == 'UP_DOWN':
                if inputs.drag_direction_mode == 'EVERYTHING' or (
                        inputs.drag_direction_mode == 'SELECTIVE' and inputs.direction_backface):
                    enable_backface_button = False

        if enable_backface_button:
            pie.operator("view3d.toggle_backface", icon='NORMALS_FACE', depress=depress_bface)
        else:
            pie.operator("view3d.directional_warning", text="Backface", icon='CANCEL')
        pie.operator("view3d.toggle_facedots", text="Facedots", icon='SNAP_FACE_CENTER', depress=fdot_draw_depressed)
        pie.operator("view3d.toggle_xray", icon='XRAY', depress=draw_depressed)
        pie.prop(inputs, "facedot_priority", icon='PIVOT_BOUNDBOX')


class VIEW3D_MT_drag_mode(Menu):
    bl_label = "Select Mode"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        tool_settings = context.tool_settings
        inputs = context.preferences.inputs
        enable_object_button = True
        objicon = 'OBJECT_TOUCH'
        enable_face_button = True
        facicon = 'FACE_DEFAULT'
        enable_edge_button = True
        edgicon = 'EDGE_DEFAULT'

        from bl_ui.space_toolsystem_common import ToolSelectPanelHelper
        tool = ToolSelectPanelHelper.tool_active_from_context(context)

        if inputs.drag_mode == 'SPLIT' and tool == "builtin.select_lasso":
            if inputs.object_select_lasso == 'OBJECT_ENCLOSE':
                objicon = 'OBJECT_ENCLOSE'
            elif inputs.object_select_lasso == 'OBJECT_ORIGIN':
                objicon = 'LIGHTPROBE_SPHERE'

            if inputs.face_select_lasso == 'FACE_TOUCH':
                facicon = 'FACE_TOUCH'
            elif inputs.face_select_lasso == 'FACE_ENCLOSE':
                facicon = 'FACE_ENCLOSE'
            elif inputs.face_select_lasso == 'FACE_CENTER':
                facicon = 'LIGHTPROBE_PLANE'

            if inputs.edge_select_lasso == 'EDGE_TOUCH':
                edgicon = 'EDGE_TOUCH'
            elif inputs.edge_select_lasso == 'EDGE_ENCLOSE':
                edgicon = 'EDGE_ENCLOSE'

            if inputs.drag_direction_lasso == 'LEFT_RIGHT' or inputs.drag_direction_lasso == 'UP_DOWN':
                if inputs.drag_direction_mode == 'EVERYTHING' or (
                        inputs.drag_direction_mode == 'SELECTIVE' and inputs.direction_object):
                    enable_object_button = False
                if inputs.drag_direction_mode == 'EVERYTHING' or (
                        inputs.drag_direction_mode == 'SELECTIVE' and inputs.direction_face):
                    enable_face_button = False
                if inputs.drag_direction_mode == 'EVERYTHING' or (
                        inputs.drag_direction_mode == 'SELECTIVE' and inputs.direction_edge):
                    enable_edge_button = False
        elif inputs.drag_mode == 'SPLIT' and tool == "builtin.select_circle":
            if inputs.object_select_circle == 'OBJECT_ENCLOSE':
                objicon = 'OBJECT_ENCLOSE'
            elif inputs.object_select_circle == 'OBJECT_ORIGIN':
                objicon = 'LIGHTPROBE_SPHERE'

            if inputs.face_select_circle == 'FACE_TOUCH':
                facicon = 'FACE_TOUCH'
            elif inputs.face_select_circle == 'FACE_ENCLOSE':
                facicon = 'FACE_ENCLOSE'
            elif inputs.face_select_circle == 'FACE_CENTER':
                facicon = 'LIGHTPROBE_PLANE'

            if inputs.edge_select_circle == 'EDGE_ENCLOSE':
                edgicon = 'EDGE_ENCLOSE'
        else:
            if inputs.object_select_box == 'OBJECT_ENCLOSE':
                objicon = 'OBJECT_ENCLOSE'
            elif inputs.object_select_box == 'OBJECT_ORIGIN':
                objicon = 'LIGHTPROBE_SPHERE'

            if inputs.face_select_box == 'FACE_TOUCH':
                facicon = 'FACE_TOUCH'
            elif inputs.face_select_box == 'FACE_ENCLOSE':
                facicon = 'FACE_ENCLOSE'
            elif inputs.face_select_box == 'FACE_CENTER':
                facicon = 'LIGHTPROBE_PLANE'

            if inputs.edge_select_box == 'EDGE_TOUCH':
                edgicon = 'EDGE_TOUCH'
            elif inputs.edge_select_box == 'EDGE_ENCLOSE':
                edgicon = 'EDGE_ENCLOSE'

            if inputs.drag_mode == 'SPLIT' and inputs.drag_direction_box == 'LEFT_RIGHT' or inputs.drag_direction_box == 'UP_DOWN':
                if inputs.drag_direction_mode == 'EVERYTHING' or (
                        inputs.drag_direction_mode == 'SELECTIVE' and inputs.direction_object):
                    enable_object_button = False
                if inputs.drag_direction_mode == 'EVERYTHING' or (
                        inputs.drag_direction_mode == 'SELECTIVE' and inputs.direction_face):
                    enable_face_button = False
                if inputs.drag_direction_mode == 'EVERYTHING' or (
                        inputs.drag_direction_mode == 'SELECTIVE' and inputs.direction_edge):
                    enable_edge_button = False

        if enable_object_button:
            pie.operator("view3d.cycle_object", icon=objicon)
        else:
            pie.operator("view3d.directional_warning", text="Object", icon='CANCEL')
        if enable_face_button:
            pie.operator("view3d.cycle_face", icon=facicon)
        else:
            pie.operator("view3d.directional_warning", text="Face", icon='CANCEL')
        if enable_edge_button:
            pie.operator("view3d.cycle_edge", icon=edgicon)
        else:
            pie.operator("view3d.directional_warning", text="Edge", icon='CANCEL')


class VIEW3D_OT_cycle_shading(bpy.types.Operator):
    """Cycle Shading Mode"""
    bl_idname = "view3d.cycle_shading"
    bl_label = "Cycle Shading Mode"

    def invoke(self, context, event):
        inputs = context.preferences.inputs
        view = context.space_data

        if view.type == 'VIEW_3D':
            shading = view.shading
        else:
            shading = context.scene.display.shading

        if shading.type == 'SOLID':
            if inputs.shading_cycle_material:
                bpy.context.space_data.shading.type = 'MATERIAL'
            elif inputs.shading_cycle_render:
                bpy.context.space_data.shading.type = 'RENDERED'
            elif inputs.shading_cycle_wire:
                bpy.context.space_data.shading.type = 'WIREFRAME'
            else:
                self.report(
                    {'INFO'},
                    "You need to enable at least 2 shading modes in the cycle: Edit-> Preferences -> Luke's Custom Build -> Visual -> Shading Button = Cycle -> Click some shading icons on the right")
        elif shading.type == 'MATERIAL':
            if inputs.shading_cycle_render:
                bpy.context.space_data.shading.type = 'RENDERED'
            elif inputs.shading_cycle_wire:
                bpy.context.space_data.shading.type = 'WIREFRAME'
            elif inputs.shading_cycle_solid:
                bpy.context.space_data.shading.type = 'SOLID'
            else:
                self.report(
                    {'INFO'},
                    "You need to enable at least 2 shading modes in the cycle: Edit-> Preferences -> Luke's Custom Build -> Visual -> Shading Button = Cycle -> Click some shading icons on the right")
        elif shading.type == 'RENDERED':
            if inputs.shading_cycle_wire:
                bpy.context.space_data.shading.type = 'WIREFRAME'
            elif inputs.shading_cycle_solid:
                bpy.context.space_data.shading.type = 'SOLID'
            elif inputs.shading_cycle_material:
                bpy.context.space_data.shading.type = 'MATERIAL'
            else:
                self.report(
                    {'INFO'},
                    "You need to enable at least 2 shading modes in the cycle: Edit-> Preferences -> Luke's Custom Build -> Visual -> Shading Button = Cycle -> Click some shading icons on the right")
        else:
            if inputs.shading_cycle_solid:
                bpy.context.space_data.shading.type = 'SOLID'
            elif inputs.shading_cycle_material:
                bpy.context.space_data.shading.type = 'MATERIAL'
            elif inputs.shading_cycle_render:
                bpy.context.space_data.shading.type = 'RENDERED'
            else:
                self.report(
                    {'INFO'},
                    "You need to enable at least 2 shading modes in the cycle: Edit-> Preferences -> Luke's Custom Build -> Visual -> Shading Button = Cycle -> Click some shading icons on the right")

        for win in bpy.context.window_manager.windows:
            for area in win.screen.areas:
                area.tag_redraw()

        return {'FINISHED'}


class VIEW3D_MT_drag_select(Menu):
    bl_label = "Drag Select"

    def draw(self, context):
        layout = self.layout
        pie = layout.menu_pie()
        tool_settings = context.tool_settings
        inputs = context.preferences.inputs
        view = context.space_data
        obj = context.active_object
        object_mode = 'OBJECT' if obj is None else obj.mode

        if inputs.drag_mode != 'DEFAULT':
            enable_auto_xray_button = True
            depress_auto_xray = False
            enable_select_through_button = True
            # enable_select_through_button = object_mode == 'EDIT'
            depress_select_through = False
            enable_backface_button = True
            depress_bface = False
            enable_object_button = True
            objicon = 'OBJECT_TOUCH'
            enable_face_button = True
            facicon = 'FACE_DEFAULT'
            enable_edge_button = True
            edgicon = 'EDGE_DEFAULT'
            active_tool = False

            if hasattr(view, 'shading'):
                shading = view.shading
                overlay = view.overlay
                has_pose_mode = (
                    (object_mode == 'POSE') or
                    (object_mode == 'WEIGHT_PAINT' and context.pose_object is not None)
                )
                if has_pose_mode:
                    draw_depressed = overlay.show_xray_bone
                elif shading.type == 'WIREFRAME':
                    draw_depressed = shading.show_xray_wireframe
                else:
                    draw_depressed = shading.show_xray
                if shading.type == 'WIREFRAME':
                    xray = shading.show_xray_wireframe and shading.xray_alpha_wireframe < 1.0
                elif shading.type == 'SOLID':
                    xray = shading.show_xray and shading.xray_alpha < 1.0
                else:
                    xray = False
                if xray:
                    fdot_draw_depressed = not overlay.show_face_center_xray
                else:
                    fdot_draw_depressed = overlay.show_face_center
            else:
                draw_depressed = False
                fdot_draw_depressed = False

            from bl_ui.space_toolsystem_common import ToolSelectPanelHelper
            tool = ToolSelectPanelHelper.tool_active_from_context(context)

            if hasattr(tool, 'idname'):
                if hasattr(tool, 'idname_fallback') and tool.idname_fallback != "":
                    space_type, mode = ToolSelectPanelHelper._tool_key_from_context(context)
                    _cls = ToolSelectPanelHelper._tool_class_from_space_type(space_type)
                    tool = _cls._tool_get_by_id_active(context, _cls.tool_fallback_id)[0].idname

                    if tool_settings.workspace_tool_type == 'DEFAULT':
                        active_tool = True
                else:
                    tool = tool.idname

            if inputs.drag_mode == 'SPLIT' and tool == "builtin.select_circle":
                depress_auto_xray = (object_mode == 'EDIT' and inputs.auto_xray_circle == 'AUTO_XRAY_EDIT') or (
                    object_mode == 'OBJECT' and inputs.auto_xray_circle == 'AUTO_XRAY_OBJECT') or inputs.auto_xray_circle == 'AUTO_XRAY_BOTH'
                depress_select_through = inputs.select_through_circle
                depress_bface = inputs.backface_circle != 'DEFAULT'

                if inputs.object_select_circle == 'OBJECT_ENCLOSE':
                    objicon = 'OBJECT_ENCLOSE'
                elif inputs.object_select_circle == 'OBJECT_ORIGIN':
                    objicon = 'LIGHTPROBE_SPHERE'

                if inputs.face_select_circle == 'FACE_TOUCH':
                    facicon = 'FACE_TOUCH'
                elif inputs.face_select_circle == 'FACE_ENCLOSE':
                    facicon = 'FACE_ENCLOSE'
                elif inputs.face_select_circle == 'FACE_CENTER':
                    facicon = 'LIGHTPROBE_PLANE'

                if inputs.edge_select_circle == 'EDGE_ENCLOSE':
                    edgicon = 'EDGE_ENCLOSE'
                else:
                    edgicon = 'EDGE_TOUCH'

            elif inputs.drag_mode == 'SPLIT' and tool == "builtin.select_lasso":
                depress_auto_xray = (object_mode == 'EDIT' and inputs.auto_xray_lasso == 'AUTO_XRAY_EDIT') or (
                    object_mode == 'OBJECT' and inputs.auto_xray_lasso == 'AUTO_XRAY_OBJECT') or inputs.auto_xray_lasso == 'AUTO_XRAY_BOTH'
                depress_select_through = inputs.select_through_lasso
                depress_bface = inputs.backface_lasso != 'DEFAULT'

                if inputs.drag_direction_lasso == 'LEFT_RIGHT' or inputs.drag_direction_lasso == 'UP_DOWN':
                    if inputs.drag_direction_mode == 'EVERYTHING':
                        enable_auto_xray_button = False
                        enable_select_through_button = False
                        enable_object_button = False
                        enable_face_button = False
                        enable_edge_button = False
                        enable_backface_button = False
                    else:
                        if inputs.direction_auto_xray:
                            enable_auto_xray_button = False
                        if inputs.direction_select_through:
                            enable_select_through_button = False
                        if inputs.direction_object:
                            enable_object_button = False
                        if inputs.direction_face:
                            enable_face_button = False
                        if inputs.direction_edge:
                            enable_edge_button = False
                        if inputs.direction_backface:
                            enable_backface_button == False

                if inputs.object_select_lasso == 'OBJECT_ENCLOSE':
                    objicon = 'OBJECT_ENCLOSE'
                elif inputs.object_select_lasso == 'OBJECT_ORIGIN':
                    objicon = 'LIGHTPROBE_SPHERE'

                if inputs.face_select_lasso == 'FACE_TOUCH':
                    facicon = 'FACE_TOUCH'
                elif inputs.face_select_lasso == 'FACE_ENCLOSE':
                    facicon = 'FACE_ENCLOSE'
                elif inputs.face_select_lasso == 'FACE_CENTER':
                    facicon = 'LIGHTPROBE_PLANE'

                if inputs.edge_select_lasso == 'EDGE_TOUCH':
                    edgicon = 'EDGE_TOUCH'
                elif inputs.edge_select_lasso == 'EDGE_ENCLOSE':
                    edgicon = 'EDGE_ENCLOSE'

            else:
                depress_auto_xray = (object_mode == 'EDIT' and inputs.auto_xray_box == 'AUTO_XRAY_EDIT') or (
                    object_mode == 'OBJECT' and inputs.auto_xray_box == 'AUTO_XRAY_OBJECT') or inputs.auto_xray_box == 'AUTO_XRAY_BOTH'
                depress_select_through = inputs.select_through_box
                depress_bface = inputs.backface_box != 'DEFAULT'

                if inputs.drag_mode == 'SPLIT' and inputs.drag_direction_box == 'LEFT_RIGHT' or inputs.drag_direction_box == 'UP_DOWN':
                    if inputs.drag_direction_mode == 'EVERYTHING':
                        enable_auto_xray_button = False
                        enable_select_through_button = False
                        enable_object_button = False
                        enable_face_button = False
                        enable_edge_button = False
                        enable_backface_button = False
                    else:
                        if inputs.direction_auto_xray:
                            enable_auto_xray_button = False
                        if inputs.direction_select_through:
                            enable_select_through_button = False
                        if inputs.direction_object:
                            enable_object_button = False
                        if inputs.direction_face:
                            enable_face_button = False
                        if inputs.direction_edge:
                            enable_edge_button = False
                        if inputs.direction_backface:
                            enable_backface_button == False

                if inputs.object_select_box == 'OBJECT_ENCLOSE':
                    objicon = 'OBJECT_ENCLOSE'
                elif inputs.object_select_box == 'OBJECT_ORIGIN':
                    objicon = 'LIGHTPROBE_SPHERE'

                if inputs.face_select_box == 'FACE_TOUCH':
                    facicon = 'FACE_TOUCH'
                elif inputs.face_select_box == 'FACE_ENCLOSE':
                    facicon = 'FACE_ENCLOSE'
                elif inputs.face_select_box == 'FACE_CENTER':
                    facicon = 'LIGHTPROBE_PLANE'

                if inputs.edge_select_box == 'EDGE_TOUCH':
                    edgicon = 'EDGE_TOUCH'
                elif inputs.edge_select_box == 'EDGE_ENCLOSE':
                    edgicon = 'EDGE_ENCLOSE'

            op = bpy.types.Scene.left_pie
            for i in range(8):
                # update slice values
                if i == 1:
                    op = bpy.types.Scene.right_pie
                elif i == 2:
                    op = bpy.types.Scene.down_pie
                elif i == 3:
                    op = bpy.types.Scene.up_pie
                elif i == 4:
                    op = bpy.types.Scene.ul_pie
                elif i == 5:
                    op = bpy.types.Scene.ur_pie
                elif i == 6:
                    op = bpy.types.Scene.dl_pie
                elif i == 7:
                    op = bpy.types.Scene.dr_pie

                if op == "MISC_LIST":
                    col = pie.split().column()
                    if enable_backface_button:
                        col.operator("view3d.toggle_backface", icon='NORMALS_FACE', depress=depress_bface)
                    else:
                        col.operator("view3d.directional_warning", text="Backface", icon='CANCEL')
                    col.operator(
                        "view3d.toggle_facedots",
                        text="Facedots",
                        icon='SNAP_FACE_CENTER',
                        depress=fdot_draw_depressed)
                    col.prop(inputs, "facedot_priority", icon='PIVOT_BOUNDBOX')
                    col.operator("view3d.toggle_xray", icon='XRAY', depress=draw_depressed)
                elif op == "MISC_MENU":
                    pie.operator("wm.call_menu_pie", text="Miscellaneous").name = "VIEW3D_MT_drag_misc"
                elif op == "MODE_LIST":
                    col = pie.split().column()
                    if enable_object_button:
                        col.operator("view3d.cycle_object", icon=objicon)
                    else:
                        col.operator("view3d.directional_warning", text="Object", icon='CANCEL')
                    if enable_face_button:
                        col.operator("view3d.cycle_face", icon=facicon)
                    else:
                        col.operator("view3d.directional_warning", text="Face", icon='CANCEL')
                    if enable_edge_button:
                        col.operator("view3d.cycle_edge", icon=edgicon)
                    else:
                        col.operator("view3d.directional_warning", text="Edge", icon='CANCEL')
                elif op == "MODE_MENU":
                    pie.operator("wm.call_menu_pie", text="Select Mode").name = "VIEW3D_MT_drag_mode"
                elif op == "TOOL_LIST":
                    col = pie.split().column()
                    col.operator("view3d.tweak", icon_value=ToolSelectPanelHelper()._icon_value_from_icon_handle(
                        "ops.generic.select"), depress=tool == "builtin.select" and not active_tool)
                    col.operator("view3d.box_select", icon_value=ToolSelectPanelHelper()._icon_value_from_icon_handle(
                        "ops.generic.select_box"), depress=tool == "builtin.select_box" and not active_tool)
                    col.operator("view3d.circle_select", icon_value=ToolSelectPanelHelper()._icon_value_from_icon_handle(
                        "ops.generic.select_circle"), depress=tool == "builtin.select_circle" and not active_tool)
                    col.operator("view3d.lasso_select", icon_value=ToolSelectPanelHelper()._icon_value_from_icon_handle(
                        "ops.generic.select_lasso"), depress=tool == "builtin.select_lasso" and not active_tool)
                    col.prop_enum(
                        tool_settings,
                        "workspace_tool_type",
                        value='DEFAULT',
                        icon='TOOL_SETTINGS',
                        text="Active Tool")
                elif op == "TOOL_MENU":
                    pie.operator("wm.toolbar_fallback_pie", text="Tools")
                elif op == "ACTIVE_TOOL":
                    pie.prop_enum(
                        tool_settings,
                        "workspace_tool_type",
                        value='DEFAULT',
                        icon='TOOL_SETTINGS',
                        text="Active Tool")
                elif op == "AUTO_XRAY":
                    if enable_auto_xray_button:
                        pie.operator("view3d.toggle_auto_xray", icon='AUTO_XRAY', depress=depress_auto_xray)
                    else:
                        pie.operator("view3d.directional_warning", text="Auto X-Ray", icon='CANCEL')
                elif op == "BACKFACE":
                    if enable_backface_button:
                        pie.operator("view3d.toggle_backface", icon='NORMALS_FACE', depress=depress_bface)
                    else:
                        pie.operator("view3d.directional_warning", text="Backface", icon='CANCEL')
                elif op == "BOX":
                    pie.operator("view3d.box_select", icon_value=ToolSelectPanelHelper()._icon_value_from_icon_handle(
                        "ops.generic.select_box"), depress=tool == "builtin.select_box" and not active_tool)
                elif op == "CIRCLE":
                    pie.operator("view3d.circle_select", icon_value=ToolSelectPanelHelper()._icon_value_from_icon_handle(
                        "ops.generic.select_circle"), depress=tool == "builtin.select_circle" and not active_tool)
                elif op == "EDGE":
                    if enable_edge_button:
                        pie.operator("view3d.cycle_edge", icon=edgicon)
                    else:
                        pie.operator("view3d.directional_warning", text="Edge", icon='CANCEL')
                elif op == "FACE":
                    if enable_face_button:
                        pie.operator("view3d.cycle_face", icon=facicon)
                    else:
                        pie.operator("view3d.directional_warning", text="Face", icon='CANCEL')
                elif op == "FACEDOT":
                    pie.operator("view3d.toggle_facedots", icon='SNAP_FACE_CENTER')
                elif op == "FACEDOT_PRIORITY":
                    pie.prop(inputs, "facedot_priority", icon='PIVOT_BOUNDBOX')
                elif op == "LASSO":
                    pie.operator("view3d.lasso_select", icon_value=ToolSelectPanelHelper()._icon_value_from_icon_handle(
                        "ops.generic.select_lasso"), depress=tool == "builtin.select_lasso" and not active_tool)
                elif op == "OBJECT":
                    if enable_object_button:
                        pie.operator("view3d.cycle_object", icon=objicon)
                    else:
                        pie.operator("view3d.directional_warning", text="Object", icon='CANCEL')
                elif op == "SELECT_THROUGH":
                    if enable_select_through_button:
                        pie.operator(
                            "view3d.toggle_select_through",
                            icon='SELECT_THROUGH',
                            depress=depress_select_through)
                    else:
                        pie.operator("view3d.directional_warning", text="Select Through", icon='CANCEL')
                elif op == "TWEAK":
                    pie.operator("view3d.tweak", icon_value=ToolSelectPanelHelper()._icon_value_from_icon_handle(
                        "ops.generic.select"), depress=tool == "builtin.select" and not active_tool)
                elif op == "XRAY":
                    pie.operator("view3d.toggle_xray", icon='XRAY', depress=draw_depressed)
                else:
                    pie.separator()


class VIEW3D_OT_drag_select(bpy.types.Operator):
    """Drag select menu"""
    bl_idname = "pie.drag_select"
    bl_label = "Drag Select"

    pie_filling = [
        ('MISC_LIST', "Misc List", "A list of miscellaneous drag select options", 0),
        ('MISC_MENU', "Misc Menu", "A menu of miscellaneous drag select options", 1),
        ('MODE_LIST', "Mode List", "A list of drag select modes", 2),
        ('MODE_MENU', "Mode Menu", "A menu of drag select modes", 3),
        ('TOOL_LIST', "Tool List", "A list of drag select tools", 4),
        ('TOOL_MENU', "Tool Menu", "A menu of drag select tools", 5),
        ('ACTIVE_TOOL', "Active Tool", "Set fallback to active tool", 6),
        ('AUTO_XRAY', "Auto X-Ray", "Toggle automatic X-Ray", 7),
        ('BACKFACE', "Backface Filter", "Toggle rear-facing mesh filter", 8),
        ('BOX', "Box", "Use box select", 9),
        ('CIRCLE', "Circle", "Use circle select", 10),
        ('EDGE', "Edge", "Change edge select mode", 11),
        ('FACE', "Face", "Change face select mode", 12),
        ('FACEDOT', "Facedots", "Toggle face center visibility", 13),
        ('FACEDOT_PRIORITY', "Facedot Priority", "Toggle facedot selection priority", 14),
        ('LASSO', "Lasso", "Use lasso select", 15),
        ('OBJECT', "Object", "Change object select mode", 16),
        ('SELECT_THROUGH', "Select Through", "Toggle select through", 17),
        ('TWEAK', "Tweak", "Use tweak", 18),
        ('XRAY', "X-Ray", "Toggle X-Ray shading", 19),
        ('EMPTY', "Empty", "Empty pie slice", 20),
    ]

    Left: EnumProperty(
        name="Left",
        description="Content for the left pie slice",
        items=pie_filling,
        default='CIRCLE',
    )

    Right: EnumProperty(
        name="Right",
        description="Content for the right pie slice",
        items=pie_filling,
        default='FACE',
    )

    Down: EnumProperty(
        name="Down",
        description="Content for the down pie slice",
        items=pie_filling,
        default='MISC_LIST',
    )

    Up: EnumProperty(
        name="Up",
        description="Content for the up pie slice",
        items=pie_filling,
        default='SELECT_THROUGH',
    )

    UpLeft: EnumProperty(
        name="UpLeft",
        description="Content for the up-left pie slice",
        items=pie_filling,
        default='BOX',
    )

    UpRight: EnumProperty(
        name="UpRight",
        description="Content for the up-right pie slice",
        items=pie_filling,
        default='OBJECT',
    )

    DownLeft: EnumProperty(
        name="DownLeft",
        description="Content for the down-left pie slice",
        items=pie_filling,
        default='LASSO',
    )

    DownRight: EnumProperty(
        name="DownRight",
        description="Content for the down-right pie slice",
        items=pie_filling,
        default='EDGE',
    )

    def invoke(self, context, event):
        bpy.types.Scene.left_pie = self.Left
        bpy.types.Scene.right_pie = self.Right
        bpy.types.Scene.up_pie = self.Up
        bpy.types.Scene.down_pie = self.Down
        bpy.types.Scene.ul_pie = self.UpLeft
        bpy.types.Scene.ur_pie = self.UpRight
        bpy.types.Scene.dl_pie = self.DownLeft
        bpy.types.Scene.dr_pie = self.DownRight
        bpy.ops.wm.call_menu_pie(name="VIEW3D_MT_drag_select")
        return {'FINISHED'}


class VIEW3D_OT_pie_operator(bpy.types.Operator):
    bl_idname = "pie.operator"
    bl_label = ""
    bl_options = {'UNDO'}

    slice_bite: bpy.props.IntVectorProperty(size=2)

    def invoke(self, context, event):
        # get the right slice
        if self.slice_bite[0] == 1:
            op = bpy.types.Scene.right_pie
        elif self.slice_bite[0] == 2:
            op = bpy.types.Scene.down_pie
        elif self.slice_bite[0] == 3:
            op = bpy.types.Scene.up_pie
        elif self.slice_bite[0] == 4:
            op = bpy.types.Scene.ul_pie
        elif self.slice_bite[0] == 5:
            op = bpy.types.Scene.ur_pie
        elif self.slice_bite[0] == 6:
            op = bpy.types.Scene.dl_pie
        elif self.slice_bite[0] == 7:
            op = bpy.types.Scene.dr_pie
        else:
            op = bpy.types.Scene.left_pie
        # split the slice into bites, remove lead/trail spaces, and ensure our bite looks like bpy
        ops = op.split(";;")
        op = ops[self.slice_bite[1]].strip()
        if op[:4] == "bpy.":
            exec(op)
        else:
            print("Not a valid operator, it needs to start with 'bpy.'")
        # reset slice values
        bpy.types.Scene.left_pie = ""
        bpy.types.Scene.left_pie_name = ""
        bpy.types.Scene.left_pie_icon = ""
        bpy.types.Scene.right_pie = ""
        bpy.types.Scene.right_pie_name = ""
        bpy.types.Scene.right_pie_icon = ""
        bpy.types.Scene.down_pie = ""
        bpy.types.Scene.down_pie_name = ""
        bpy.types.Scene.down_pie_icon = ""
        bpy.types.Scene.up_pie = ""
        bpy.types.Scene.up_pie_name = ""
        bpy.types.Scene.up_pie_icon = ""
        bpy.types.Scene.ul_pie = ""
        bpy.types.Scene.ul_pie_name = ""
        bpy.types.Scene.ul_pie_icon = ""
        bpy.types.Scene.ur_pie = ""
        bpy.types.Scene.ur_pie_name = ""
        bpy.types.Scene.ur_pie_icon = ""
        bpy.types.Scene.dl_pie = ""
        bpy.types.Scene.dl_pie_name = ""
        bpy.types.Scene.dl_pie_icon = ""
        bpy.types.Scene.dr_pie = ""
        bpy.types.Scene.dr_pie_name = ""
        bpy.types.Scene.dr_pie_icon = ""
        return {'FINISHED'}


class VIEW3D_MT_pie_custom(Menu):
    bl_label = "Pie"

    def draw(self, context):
        from bl_ui.space_toolsystem_common import ToolSelectPanelHelper
        layout = self.layout
        pie = layout.menu_pie()
        op = bpy.types.Scene.left_pie
        name = bpy.types.Scene.left_pie_name
        icon = bpy.types.Scene.left_pie_icon
        error_id = "Left"

        for i in range(8):
            # update slice values
            if i == 1:
                op = bpy.types.Scene.right_pie
                name = bpy.types.Scene.right_pie_name
                icon = bpy.types.Scene.right_pie_icon
                error_id = "Right"
            elif i == 2:
                op = bpy.types.Scene.down_pie
                name = bpy.types.Scene.down_pie_name
                icon = bpy.types.Scene.down_pie_icon
                error_id = "Down"
            elif i == 3:
                op = bpy.types.Scene.up_pie
                name = bpy.types.Scene.up_pie_name
                icon = bpy.types.Scene.up_pie_icon
                error_id = "Up"
            elif i == 4:
                op = bpy.types.Scene.ul_pie
                name = bpy.types.Scene.ul_pie_name
                icon = bpy.types.Scene.ul_pie_icon
                error_id = "UpLeft"
            elif i == 5:
                op = bpy.types.Scene.ur_pie
                name = bpy.types.Scene.ur_pie_name
                icon = bpy.types.Scene.ur_pie_icon
                error_id = "UpRight"
            elif i == 6:
                op = bpy.types.Scene.dl_pie
                name = bpy.types.Scene.dl_pie_name
                icon = bpy.types.Scene.dl_pie_icon
                error_id = "DownLeft"
            elif i == 7:
                op = bpy.types.Scene.dr_pie
                name = bpy.types.Scene.dr_pie_name
                icon = bpy.types.Scene.dr_pie_icon
                error_id = "DownRight"

            if op != "":
                ops = op.split(";;")
                # multi-operator column
                if len(ops) > 1:
                    col = pie.split().column()
                    names = name.split(";;")
                    icons = icon.split(";;")
                    # everything with a value has been split to match the number of operators
                    if ((name == "" or len(names) == len(ops)) and (icon == "" or len(icons) == len(ops))):
                        for k in range(len(ops)):
                            # icons and names
                            if icon != "" and name != "":
                                if icons[k] != "":
                                    if len(icons[k]) > 5 and (icons[k][3] == "." or icons[k][5] == "."):
                                        if names[k] != "":
                                            col.operator(
                                                "pie.operator",
                                                text="    " + names[k],
                                                icon_value=ToolSelectPanelHelper()._icon_value_from_icon_handle(
                                                    icons[k])).slice_bite = (
                                                i,
                                                k)
                                        else:
                                            col.operator(
                                                "pie.operator",
                                                text=names[k],
                                                icon_value=ToolSelectPanelHelper()._icon_value_from_icon_handle(
                                                    icons[k])).slice_bite = (
                                                i,
                                                k)
                                    else:
                                        col.operator("pie.operator", text=names[k], icon=icons[k]).slice_bite = (i, k)
                                else:
                                    col.operator("pie.operator", text=names[k]).slice_bite = (i, k)
                            # icons
                            elif icon != "":
                                if icons[k] != "":
                                    if len(icons[k]) > 5 and (icons[k][3] == "." or icons[k][5] == "."):
                                        col.operator(
                                            "pie.operator",
                                            text="",
                                            icon_value=ToolSelectPanelHelper()._icon_value_from_icon_handle(
                                                icons[k])).slice_bite = (
                                            i,
                                            k)
                                    else:
                                        col.operator("pie.operator", text="", icon=icons[k]).slice_bite = (i, k)
                                else:
                                    col.operator("pie.operator", text="").slice_bite = (i, k)
                            # names
                            elif name != "":
                                col.operator("pie.operator", text=names[k]).slice_bite = (i, k)
                            # neither
                            else:
                                col.operator("pie.operator", text="").slice_bite = (i, k)
                    # imbalanced names/icons
                    else:
                        if icon != "" and name != "":
                            print(error_id + " pie slice is imbalanced - Operators:" + str(len(ops)) +
                                  " Names:" + str(len(names)) + " Icons:" + str(len(icons)))
                        elif icon != "":
                            print(error_id + " pie slice is imbalanced - Operators:" +
                                  str(len(ops)) + " Icons:" + str(len(icons)))
                        else:
                            print(error_id + " pie slice is imbalanced - Operators:" +
                                  str(len(ops)) + " Names:" + str(len(names)))
                # single operator
                else:
                    if icon != "":
                        if len(icon) > 5 and (icon[3] == "." or icon[5] == "."):
                            if name != "":
                                pie.operator(
                                    "pie.operator",
                                    text="    " + name,
                                    icon_value=ToolSelectPanelHelper()._icon_value_from_icon_handle(icon)).slice_bite = (
                                    i,
                                    0)
                            else:
                                pie.operator(
                                    "pie.operator",
                                    text=name,
                                    icon_value=ToolSelectPanelHelper()._icon_value_from_icon_handle(icon)).slice_bite = (
                                    i,
                                    0)
                        else:
                            pie.operator("pie.operator", text=name, icon=icon).slice_bite = (i, 0)
                    else:
                        pie.operator("pie.operator", text=name).slice_bite = (i, 0)
            # empty slice
            else:
                pie.separator()


class VIEW3D_OT_pie_custom(bpy.types.Operator):
    """Customizable pie menu"""
    bl_idname = "pie.custom"
    bl_label = "Pie"

    Left: bpy.props.StringProperty()
    Name_L: bpy.props.StringProperty()
    Icon_L: bpy.props.StringProperty()
    Right: bpy.props.StringProperty()
    Name_R: bpy.props.StringProperty()
    Icon_R: bpy.props.StringProperty()
    Down: bpy.props.StringProperty()
    Name_D: bpy.props.StringProperty()
    Icon_D: bpy.props.StringProperty()
    Up: bpy.props.StringProperty()
    Name_U: bpy.props.StringProperty()
    Icon_U: bpy.props.StringProperty()
    UpLeft: bpy.props.StringProperty()
    Name_UL: bpy.props.StringProperty()
    Icon_UL: bpy.props.StringProperty()
    UpRight: bpy.props.StringProperty()
    Name_UR: bpy.props.StringProperty()
    Icon_UR: bpy.props.StringProperty()
    DownLeft: bpy.props.StringProperty()
    Name_DL: bpy.props.StringProperty()
    Icon_DL: bpy.props.StringProperty()
    DownRight: bpy.props.StringProperty()
    Name_DR: bpy.props.StringProperty()
    Icon_DR: bpy.props.StringProperty()

    def invoke(self, context, event):
        bpy.types.Scene.left_pie = self.Left
        bpy.types.Scene.left_pie_name = self.Name_L
        bpy.types.Scene.left_pie_icon = self.Icon_L
        bpy.types.Scene.right_pie = self.Right
        bpy.types.Scene.right_pie_name = self.Name_R
        bpy.types.Scene.right_pie_icon = self.Icon_R
        bpy.types.Scene.down_pie = self.Down
        bpy.types.Scene.down_pie_name = self.Name_D
        bpy.types.Scene.down_pie_icon = self.Icon_D
        bpy.types.Scene.up_pie = self.Up
        bpy.types.Scene.up_pie_name = self.Name_U
        bpy.types.Scene.up_pie_icon = self.Icon_U
        bpy.types.Scene.ul_pie = self.UpLeft
        bpy.types.Scene.ul_pie_name = self.Name_UL
        bpy.types.Scene.ul_pie_icon = self.Icon_UL
        bpy.types.Scene.ur_pie = self.UpRight
        bpy.types.Scene.ur_pie_name = self.Name_UR
        bpy.types.Scene.ur_pie_icon = self.Icon_UR
        bpy.types.Scene.dl_pie = self.DownLeft
        bpy.types.Scene.dl_pie_name = self.Name_DL
        bpy.types.Scene.dl_pie_icon = self.Icon_DL
        bpy.types.Scene.dr_pie = self.DownRight
        bpy.types.Scene.dr_pie_name = self.Name_DR
        bpy.types.Scene.dr_pie_icon = self.Icon_DR
        bpy.ops.wm.call_menu_pie(name="VIEW3D_MT_pie_custom")

        return {'FINISHED'}


classes = (
    VIEW3D_OT_edit_mesh_extrude_individual_move,
    VIEW3D_OT_edit_mesh_extrude_move,
    VIEW3D_OT_edit_mesh_extrude_shrink_fatten,
    VIEW3D_OT_edit_mesh_extrude_manifold_normal,
    VIEW3D_OT_transform_gizmo_set,
    VIEW3D_FH_camera_background_image,
    VIEW3D_FH_empty_image,
    VIEW3D_FH_vdb_volume,
    VIEW3D_OT_box_lasso,
    VIEW3D_OT_box_select,
    VIEW3D_OT_circle_select,
    VIEW3D_OT_lasso_select,
    VIEW3D_OT_tweak,
    VIEW3D_OT_directional_warning,
    VIEW3D_MT_drag_misc,
    VIEW3D_MT_drag_mode,
    VIEW3D_OT_cycle_shading,
    VIEW3D_MT_drag_select,
    VIEW3D_OT_drag_select,
    VIEW3D_OT_pie_operator,
    VIEW3D_MT_pie_custom,
    VIEW3D_OT_pie_custom,
)
