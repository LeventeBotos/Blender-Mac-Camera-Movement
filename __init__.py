bl_info = {
    "name": "Camera Navigation (macOS Optimized)",
    "blender": (3, 0, 0),
    "category": "3D View",
    "author": "Levente Botos",
    "description": "Smooth WASD + mouse/trackpad FPS-style navigation, optimized for macOS",
    "version": (1, 1),
}

import bpy
from bpy.types import Operator
from mathutils import Vector, Quaternion
import time


class VIEW3D_OT_fps_navigation(Operator):
    bl_idname = "view3d.fps_navigation_mac"
    bl_label = "FPS Navigation (macOS)"
    bl_options = {"REGISTER", "GRAB_CURSOR", "BLOCKING"}

    base_speed: float = 0.08    # slower default for Mac trackpads
    sensitivity: float = 0.0015 # lower sensitivity (trackpads are more sensitive)
    boost_factor: float = 2.5   # sprint multiplier
    slow_factor: float = 0.4    # crouch multiplier
    smoothing: float = 0.25     # movement smoothing

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

        # Adjust speed with trackpad scroll
        if event.type == "WHEELUPMOUSE" and event.value == "PRESS":
            self.base_speed *= 1.1
        if event.type == "WHEELDOWNMOUSE" and event.value == "PRESS":
            self.base_speed *= 0.9

        # Mouse / Trackpad look
        if event.type == "MOUSEMOVE":
            dx = event.mouse_prev_x - event.mouse_x
            dy = event.mouse_prev_y - event.mouse_y

            # yaw around global Z (smooth)
            rv3d.view_rotation = Quaternion((0, 0, 1), dx * self.sensitivity) @ rv3d.view_rotation
            # pitch around local X (inverted for natural feel on trackpad)
            rv3d.view_rotation = Quaternion((1, 0, 0), -dy * self.sensitivity) @ rv3d.view_rotation

        # Movement vectors
        forward = rv3d.view_rotation @ Vector((0, 0, -1))
        right = rv3d.view_rotation @ Vector((1, 0, 0))
        up = Vector((0, 0, 1))

        # Speed modifiers
        speed = self.base_speed
        if event.shift:  # sprint
            speed *= self.boost_factor
        if event.alt:    # crouch
            speed *= self.slow_factor

        # Key input
        move = Vector((0, 0, 0))
        if event.type == "W": move += forward
        if event.type == "S": move -= forward
        if event.type == "A": move -= right
        if event.type == "D": move += right
        if event.type == "E": move += up
        if event.type == "Q": move -= up

        # Normalize & apply smoothing
        if move.length > 0:
            move.normalize()
            target_vel = move * speed
        else:
            target_vel = Vector((0, 0, 0))

        self.velocity = self.velocity.lerp(target_vel, self.smoothing)
        rv3d.view_location += self.velocity * (dt * 60)

        return {"RUNNING_MODAL"}

    def invoke(self, context, event):
        context.window.cursor_modal_set("NONE")  # lock cursor to center
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}


def menu_func(self, context):
    self.layout.operator(VIEW3D_OT_fps_navigation.bl_idname, text="FPS Navigation (macOS)")


def register():
    bpy.utils.register_class(VIEW3D_OT_fps_navigation)
    bpy.types.VIEW3D_MT_view.append(menu_func)


def unregister():
    bpy.utils.unregister_class(VIEW3D_OT_fps_navigation)
    bpy.types.VIEW3D_MT_view.remove(menu_func)


if __name__ == "__main__":
    register()
