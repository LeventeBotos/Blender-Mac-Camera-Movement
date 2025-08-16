bl_info = {
    "name": "Better FPS Camera Navigation (macOS optimized)",
    "blender": (3, 0, 0),
    "category": "3D View",
}

import bpy
from bpy.types import Operator
from mathutils import Vector

class VIEW3D_OT_fps_navigation(Operator):
    bl_idname = "view3d.fps_navigation"
    bl_label = "FPS Navigation"
    bl_options = {"REGISTER", "GRAB_CURSOR", "BLOCKING"}

    speed = 0.12
    sensitivity = 0.0025
    boost_factor = 3.0
    slow_factor = 0.3

    def modal(self, context, event):
        rv3d = context.region_data

        # Mouse look (relative movement on macOS)
        if event.type == "MOUSEMOVE":
            dx = event.mouse_prev_x - event.mouse_x
            dy = event.mouse_prev_y - event.mouse_y
            rv3d.view_rotation.rotate_axis("Z", dx * self.sensitivity)
            rv3d.view_rotation.rotate_axis("X", dy * self.sensitivity)

        # Movement vectors
        forward = rv3d.view_rotation @ Vector((0, 0, -1))
        right = rv3d.view_rotation @ Vector((1, 0, 0))
        up = Vector((0, 0, 1))

        # Speed modifiers (Shift = sprint, Option = slow walk)
        speed = self.speed
        if event.shift:   # sprint
            speed *= self.boost_factor
        if event.alt:     # crouch/slow
            speed *= self.slow_factor

        # WASD + QE
        if event.type == "W": rv3d.view_location += forward * speed
        if event.type == "S": rv3d.view_location -= forward * speed
        if event.type == "A": rv3d.view_location -= right * speed
        if event.type == "D": rv3d.view_location += right * speed
        if event.type == "E": rv3d.view_location += up * speed
        if event.type == "Q": rv3d.view_location -= up * speed

        # Exit (ESC only — right click unreliable on Magic Mouse)
        if event.type == "ESC":
            context.window.cursor_modal_restore()
            return {"CANCELLED"}

        return {"RUNNING_MODAL"}

    def invoke(self, context, event):
        context.window.cursor_modal_set("CROSSHAIR")
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}

def register():
    bpy.utils.register_class(VIEW3D_OT_fps_navigation)

def unregister():
    bpy.utils.unregister_class(VIEW3D_OT_fps_navigation)

if __name__ == "__main__":
    register()
