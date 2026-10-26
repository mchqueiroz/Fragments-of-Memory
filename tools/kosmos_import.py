"""Importa o modelo brutalista do Kosmos feito à mão pelo usuário e exporta só a geometria.

Uso: blender -b /caminho/KOSMOS.blend --disable-autoexec -P tools/kosmos_import.py   -> art/models/kosmos.glb
O .blend é dado do usuário (aberto sem autoexec). Câmeras e luzes saem; o material (concreto em triplanar) vem do Godot.
Eixos: Blender (x, y, z) -> Godot (x, z, -y). Unidades em metros: o bloco tem ~240 x 100 x 20 m.
"""
import os

import bpy

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "art", "models", "kosmos.glb")
for o in list(bpy.data.objects):
    if o.type != "MESH":
        bpy.data.objects.remove(o, do_unlink=True)
bpy.ops.object.select_all(action="SELECT")
bpy.ops.export_scene.gltf(filepath=OUT, export_format="GLB", use_selection=True, export_apply=True, export_yup=True,
                          export_materials="NONE")
print("EXPORTADO", OUT, len(bpy.data.objects), "objetos")
