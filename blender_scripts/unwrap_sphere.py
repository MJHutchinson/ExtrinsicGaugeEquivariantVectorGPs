import bpy
import bmesh
import math
from functools import partial
import numpy as np
import os
from mathutils import Vector
from mathutils import Euler

# directory = os.getcwd()
base_dir = os.path.expanduser(
    "~/Documents/projects/ExtrinsicGaugeEquivariantVectorGPs/"
)
scripts_dir = os.path.join(base_dir, "blender_scripts")
data_dir = os.path.join(base_dir, "blender")
texture_path = os.path.join(base_dir, "blender", "textures")
col_dir = os.path.join(base_dir, "blender", "col")

os.makedirs(os.path.join(data_dir, "blank_to_wrong", "renders"), exist_ok=True)

with open(os.path.join(scripts_dir, "render.py")) as file:
    exec(file.read())

reset_scene()
set_renderer_settings(num_samples=16 if bpy.app.background else 128)
(cam_axis, cam_obj) = setup_camera(
    distance=15.5,
    angle=(0, 0, 0),
    lens=85,
    height=1500,
)
setup_lighting(
    shifts=(-10, -10, 10),
    sizes=(9, 18, 15),
    energies=(1500, 150, 1125),
    horizontal_angles=(-np.pi / 6, np.pi / 3, np.pi / 3),
    vertical_angles=(-np.pi / 3, -np.pi / 6, np.pi / 4),
)
set_resolution(1080, aspect=(16, 9))

bd_obj = create_backdrop(location=(0, 0, -2), scale=(10, 5, 5))
arr_obj = create_vector_arrow(color=(1, 0, 0, 1))

frames = 60

# for frame in [0, 29, 59]:
for frame in range(frames):
    print(frame)
    frame_name = f"frame_{frame}"
    bm = import_bmesh(os.path.join(data_dir, "unwrap_sphere", f"{frame_name}.obj"))
    import_color(bm, color=(0.8, 1, 1, 1))
    earth_obj = add_mesh(bm, name=frame_name)
    earth_mat = add_vertex_colors(earth_obj)
    add_texture(earth_mat, os.path.join(texture_path, "mercator_rot.png"))
    vf_bm = import_vector_field(
        os.path.join(data_dir, "unwrap_sphere", f"{frame_name}.csv")
    )
    vf_obj = add_vector_field(
        vf_bm, arr_obj, scale=3, name=frame_name + "_vector_field"
    )
    bpy.ops.object.empty_add(
        type="PLAIN_AXES", align="WORLD", location=(0, 0, 0), scale=(1, 1, 1)
    )
    empty = bpy.context.selected_objects[0]
    earth_obj.parent = empty
    vf_obj.parent = empty
    empty.rotation_euler = Euler((0, 0, math.radians(90)), "XYZ")
    bpy.context.scene.render.filepath = os.path.join(
        data_dir, "unwrap_sphere", "renders", f"frame_{frame:04d}.png"
    )
    bpy.ops.render.render(use_viewport=True, write_still=True)
    for modifier in vf_obj.modifiers:
        bpy.data.node_groups.remove(modifier.node_group, do_unlink=True)
    bpy.data.objects.remove(earth_obj, do_unlink=True)
    bpy.data.objects.remove(vf_obj, do_unlink=True)
    bpy.data.objects.remove(empty, do_unlink=True)
