import bpy
import bmesh
import math
from functools import partial
import numpy as np
import os
from mathutils import Vector
from mathutils import Euler

# directory = os.getcwd()
base_dir = os.path.expanduser("~/Documents/projects/ExtrinsicGaugeEquivariantVectorGPs/")
scripts_dir = os.path.join(base_dir, "blender_scripts")
data_dir = os.path.join(base_dir, "blender")
texture_path = os.path.join(base_dir, "textures")
col_dir = os.path.join(base_dir, "col")

os.makedirs(os.path.join(data_dir, 'torus', 'renders'), exist_ok=True)

with open(os.path.join(scripts_dir, "render.py")) as file:
    exec(file.read())

reset_scene()
set_renderer_settings(num_samples = 2048 if bpy.app.background else 128)
setup_layers()
setup_compositor(mask_center = (0.5,0.3125), mask_size = (0.675,0.325), shadow_color_correction_exponent = 2.75)
(cam_axis, cam_obj) = setup_camera(distance = 9.125, angle = (-np.pi/16, 0, 0), lens = 85, height = 2560, crop = (1/5,9/10,0,10/11))
setup_lighting(shifts = (-10,-10,10), sizes = (9,18,15), energies = (1500,150,1125),
               horizontal_angles = (-np.pi/6, np.pi/3, np.pi/3), vertical_angles = (-np.pi/3, -np.pi/6, np.pi/4))
set_resolution(1080)

bd_obj = create_backdrop(location=(0, 0, -0.25), scale=(10, 5, 5))
arr_obj = create_vector_arrow(color=(0, 0, 0, 1))

set_object_collections(backdrop = [bd_obj], instancing = [arr_obj])

bm = import_bmesh(os.path.join(data_dir, "torus", "torus.obj"))
import_color(bm, name='white', color = (0.7,0.7,0.7,1))
obj = add_mesh(bm, name="torus")
klein_mat = add_vertex_colors(obj)

vf_bm = import_vector_field(
    os.path.join(data_dir, "torus", f"sample_vecs.csv")
)
vf_obj = add_vector_field(
    vf_bm, arr_obj, scale=1.5, name="sample"
)

set_object_collections(object = [obj, vf_obj])

bpy.ops.object.select_all(action='DESELECT')
obj.select_set(True)
bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='MEDIAN')

bpy.ops.object.empty_add(type='PLAIN_AXES', align='WORLD', location=obj.location, scale=(1, 1, 1))
empty = bpy.context.selected_objects[0]

bpy.ops.object.select_all(action='DESELECT')
obj.select_set(True)
empty.select_set(True)
bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)

bpy.ops.object.select_all(action='DESELECT')
vf_obj.select_set(True)
empty.select_set(True)
bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)

empty.rotation_euler = Euler((math.radians(0),math.radians(0),math.radians(0)), "XYZ")
empty.location = (0,0,0)
# empty.scale = (0.5, 0.5, 0.5)

bpy.context.scene.render.filepath = os.path.join(
    data_dir, "torus", "renders", 'torus.png'
)
if bpy.app.background:
    bpy.ops.render.render(use_viewport=True, write_still=True)
