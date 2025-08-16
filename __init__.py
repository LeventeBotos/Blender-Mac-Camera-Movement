bl_info = {
    "name": "Perfect FPS Camera Navigation (macOS ready)",
    "blender": (3, 0, 0),
    "category": "3D View",
    "version": (1, 0),
    "author": "Levente Botos",
    "description": "Smooth WASD + mouse FPS-style navigation with sprint, crouch, cursor lock, and scroll speed control",
}

import bpy
from bpy.types import Operator
from mathutils import Vector
import time


class VIEW3D_OT_fps_navigation(Operator):
    bl_idname = "view3d.perfect_fps_navigation"
    bl_label = "Perfect FPS Navigation"
    bl_options = {"REGISTER", "GRAB_CURSOR", "BLOCKING"}

    # Settings
    base_speed: float = 0.15
    sensitivity: float = 0.002
    boost_factor: float = 3.0
    slow_factor: float = 0.3
    smoothing: float = 0.2

    def __init__(self):
        self.velocity = Vector((0, 0, 0))
        self.last_time = time.time()

    def modal(self, context, event):
        rv3d = context.region_data
        now = time.time()
        dt = now - self.last_time
        self.last_time = now

        # Exit
        if event.type in {"ESC"}:
            context.window.cursor_modal_restore()
            return {"CANCELLED"}

        # Adjust speed with scroll (trackpad two-finger scroll or mouse wheel)
        if event.type in {"WHEELUPMOUSE"} and event.value == "PRESS":
            self.base_speed *= 1.1
        if event.type in {"WHEELDOWNMOUSE"} and event.value == "PRESS":
            self.base_speed *= 0.9

        # Mouse look
        if event.type == "MOUSEMOVE":
            dx = event.mouse_prev_x - event.mouse_x
            dy = event.mouse_prev_y - event.mouse_y
            rv3d.view_rotation.rotate_axis("Z", dx * self.sensitivity)
            rv3d.view_rotation.rotate_axis("X", dy * self.sensitivity)

        # Movement directions
        forward = rv3d.view_rotation @ Vector((0, 0, -1))
        right = rv3d.view_rotation @ Vector((1, 0, 0))
        up = Vector((0, 0, 1))

        # Speed modifiers
        speed = self.base_speed
        if event.shift:  # sprint
            speed *= self.boost_factor
        if event.alt:  # crouch/slow
            speed *= self.slow_factor

        # Key input vector
        move = Vector((0, 0, 0))
        if event.type == "W": move += forward
        if event.type == "S": move -= forward
        if event.type == "A": move -= right
        if event.type == "D": move += right
        if event.type == "E": move += up
        if event.type == "Q": move -= up

        # Normalize
        if move.length > 0:
            move.normalize()
            target_vel = move * speed
        else:
            target_vel = Vector((0, 0, 0))

        # Smooth acceleration
        self.velocity = self.velocity.lerp(target_vel, self.smoothing)

        # Apply movement
        rv3d.view_location += self.velocity * (dt * 60)  # scale with frame time

        return {"RUNNING_MODAL"}

    def invoke(self, context, event):
        context.window.cursor_modal_set("NONE")  # lock cursor
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}


def menu_func(self, context):
    self.layout.operator(VIEW3D_OT_fps_navigation.bl_idname)


def register():
    bpy.utils.register_class(VIEW3D_OT_fps_navigation)
    bpy.types.VIEW3D_MT_view.append(menu_func)


def unregister():
    bpy.utils.unregister_class(VIEW3D_OT_fps_navigation)
    bpy.types.VIEW3D_MT_view.remove(menu_func)


if __name__ == "__main__":
    register()
