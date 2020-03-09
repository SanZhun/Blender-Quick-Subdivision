# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "Quick subdivision",
    "author": "BlessingSail",
    "version": (0, 4),
    "blender": (2, 82, 0),
    "location": "View3D",
    "description": "Quickly change brush strength and add subdivision",
    "warning": "",
    "category": "Object"
}
import bpy
# from bpy import context
from bpy.props import FloatProperty, IntProperty

# import rna_keymap_ui


# -----------------------------------------------------------------------------
#    Operators
# -----------------------------------------------------------------------------
class Scale_strength(bpy.types.Operator):
    bl_idname = "brush.scale_strength"
    bl_label = "Scale sculpt/paint brush strength"

    scale: FloatProperty(name="Scale",
                         default=1,
                         min=0,
                         max=2,
                         soft_min=0,
                         soft_max=2)

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.selected_objects
        # The 'poll' function can be thought as the bouncer that determines if the operator
        #  should be allowed to go on and process something. The return value of the poll
        #  function determines if the execute function is called.

    def execute(self, context):
        if context.scene.tool_settings.unified_paint_settings.use_unified_strength is True:
            strength = context.scene.tool_settings.unified_paint_settings.strength
            if context.scene.tool_settings.unified_paint_settings.strength > 1:
                context.scene.tool_settings.unified_paint_settings.strength = strength + 0.1
            else:
                context.scene.tool_settings.unified_paint_settings.strength = strength * self.scale

        else:
            strength = context.tool_settings.sculpt.brush.strength
            if context.tool_settings.sculpt.brush.strength > 1:
                context.tool_settings.sculpt.brush.strength = strength + 0.1
            else:
                context.tool_settings.sculpt.brush.strength = strength * self.scale

        return {'FINISHED'}


class Add_subdivision_simple(bpy.types.Operator):
    bl_idname = "object.add_subdivision_simple"
    bl_label = "Quckly add simple subdivision"
    bl_options = {'REGISTER', 'UNDO'}

    level: IntProperty(name="Level",
                       default=0,
                       min=0,
                       max=5,
                       soft_min=0,
                       soft_max=5)

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.selected_objects

    def execute(self, context):
        bpy.ops.object.modifier_add(type='SUBSURF')
        context.object.modifiers["Subdivision"].subdivision_type = 'SIMPLE'
        context.object.modifiers["Subdivision"].levels = self.level
        context.object.modifiers["Subdivision"].render_levels = self.level
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Subdivision")

        return {'FINISHED'}


# -----------------------------------------------------------------------------
#    Preferences
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
#    Keymap
# -----------------------------------------------------------------------------

# store keymaps here to access after registration; Notice that user keymaps = addons keymaps + active keymaps
active_keymap_items = []
addon_keymap_items = []

# 修改default keymap 需要加timer, 详见https://blenderartists.org/t/removing-a-specific-default-hotkey-shortcut-via-a-script/1163540/2
# import bpy,_thread,time
# def thrd_func():
#     time.sleep(.1)
#     print('item count:',len(km.keymap_items))
# _thread.start_new_thread(thrd_func,())


# -----------------------------------------------------------------------------
#    Register
# -----------------------------------------------------------------------------
def register():
    bpy.utils.register_class(Scale_strength)
    bpy.utils.register_class(Add_subdivision_simple)
    # bpy.types.VIEW3D_MT_object.append(menu_func)

    # handle the keymap
    wm = bpy.context.window_manager

    numList = ['ONE', 'TWO', 'THREE', 'FOUR', 'FIVE']
    addons_keymaps = wm.keyconfigs.addon.keymaps
    active_keymaps = wm.keyconfigs.active.keymaps

    for mode in ("Object Mode", "Sculpt"):

        # 反激活 'active keymap'下 '物体模式'和'雕刻模式'中'细分设置'
        if mode in active_keymaps:
            km = active_keymaps[mode]
            for kmi in km.keymap_items:
                if kmi.idname == "object.subdivision_set":
                    kmi.active = False
                    active_keymap_items.append((kmi))  # 用于unregister时的溯源

        # 在'addon keymap'下的 '物体模式'和'雕刻模式'里 注册Quick subdivision 的快捷键, 默认为Ctrl 1, 2, 3, 4, 5
        if mode in addons_keymaps:
            km = addons_keymaps[mode]
        else:
            km = addons_keymaps.new(name=mode, space_type="EMPTY")

        for i in range(0, 5):
            kmi = km.keymap_items.new(idname=Add_subdivision_simple.bl_idname,
                                      type=numList[i],
                                      value='PRESS',
                                      ctrl=True,
                                      alt=False)
            kmi.properties.level = i + 1  # 对应细分程度

            addon_keymap_items.append((km, kmi))  # 用于unregister时的溯源


def unregister():
    bpy.utils.unregister_class(Scale_strength)
    bpy.utils.unregister_class(Add_subdivision_simple)

    # 删除本插件在addon keymap中的注册的键
    for km, kmi in addon_keymap_items:
        km.keymap_items.remove(kmi)

    wm = bpy.context.window_manager

    for km, kmi in addon_keymap_items:
        if km in wm.keyconfigs.addon.keymaps.values():
            if len(km.keymap_items) == 0:
                wm.keyconfigs.addon.keymaps.remove(km)

    addon_keymap_items.clear()

    # 重新激活 active keymap 中被本插件屏蔽的键
    for kmi in active_keymap_items:
        kmi.active = True

    active_keymap_items.clear()


if __name__ == "__main__":
    register()
