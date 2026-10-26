"""Gera os modelos 3D do jogo (cômodos, móveis, personagens) com o Blender no terminal.

Uso:  blender -b -P tools/kit.py -- gabinete sergei chess plans
Saída: art/models/<nome>.glb   (colisão automática no Godot: objetos terminados em "-col")

Todo o texel segue 1 pixel = 1 cm, para a densidade de pixels ser igual em tudo (estilo PS1).
Eixos do Blender: X leste, Y norte (= frente do jogador, vira -Z no Godot), Z cima.
"""
import math
import os
import random
import sys

import bpy

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TEX = os.path.join(ROOT, "art", "tex")
OUT = os.path.join(ROOT, "art", "models")
os.makedirs(OUT, exist_ok=True)
TEXEL = 0.01

_mats = {}
_groups = {}
_xf = [0.0, 0.0, 0.0, 0.0]  # origem x, y, z e rotação em Z do conjunto atual (para móveis girados)
_bone = [None]  # osso ao qual as peças criadas agora pertencem (peso 1.0, "skinning rígido" estilo PS1)
_rig = [None]   # armature do personagem em construção


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    _mats.clear()
    _groups.clear()
    _xf[:] = [0.0, 0.0, 0.0, 0.0]
    _bone[0] = None
    _rig[0] = None


# Rugosidade por textura: superfícies lisas pegam brilho da luz (piso, metal, latão, oleado), o resto fica fosco.
ROUGH = {"metal": 0.42, "linoleum": 0.5, "parquet_square": 0.55, "parquet": 0.55, "brass": 0.3, "concrete": 0.78,
         "leather": 0.6, "oilcloth": 0.4, "missile_skin": 0.35, "paint_green": 0.7, "wood_dark": 0.72, "chessboard": 0.5}


def mat(tex=None, emit=None, strength=1.0, color=(0.5, 0.5, 0.5), emit_tex=False):
    """emit_tex=True: a própria textura vira emissão (telas e letreiros que brilham com o texto)."""
    key = (tex, emit, strength, color, emit_tex)
    if key in _mats:
        return _mats[key]
    m = bpy.data.materials.new(tex or "flat")
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = ROUGH.get(tex, 1.0)
    if "Specular IOR Level" in b.inputs:
        b.inputs["Specular IOR Level"].default_value = 0.0
    m["tile_u"] = m["tile_v"] = 1.0
    if tex:
        im = nt.nodes.new("ShaderNodeTexImage")
        im.image = bpy.data.images.load(os.path.join(TEX, tex + ".png"))
        im.interpolation = "Closest"
        nt.links.new(im.outputs["Color"], b.inputs["Base Color"])
        m["tile_u"] = im.image.size[0] * TEXEL
        m["tile_v"] = im.image.size[1] * TEXEL
    else:
        b.inputs["Base Color"].default_value = (*color, 1)
    if emit_tex and tex:
        nt.links.new(im.outputs["Color"], b.inputs["Emission Color"])
        b.inputs["Emission Strength"].default_value = strength
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1)
        b.inputs["Emission Strength"].default_value = strength
    _mats[key] = m
    return m


class Group:
    def __init__(self, m, collide):
        self.m, self.collide = m, collide
        self.V, self.F, self.UV, self.B = [], [], [], []


def G(m, collide):
    key = (m.name, id(m), collide)
    if key not in _groups:
        _groups[key] = Group(m, collide)
    return _groups[key]


def W(p):
    """Coordenada local do conjunto -> mundo."""
    c, s = math.cos(_xf[3]), math.sin(_xf[3])
    return (_xf[0] + p[0] * c - p[1] * s, _xf[1] + p[0] * s + p[1] * c, _xf[2] + p[2])


class xf:
    """with xf(x, y, rz): ...  — agrupa peças de um móvel e gira o conjunto."""
    def __init__(self, x=0.0, y=0.0, rz=0.0, z=0.0):
        self.new = [x, y, z, rz]

    def __enter__(self):
        self.old = _xf[:]
        _xf[:] = self.new

    def __exit__(self, *a):
        _xf[:] = self.old


def _quad(g, pts, uvs):
    i = len(g.V)
    g.V.extend(pts)
    g.UV.extend(uvs)
    g.B.extend([_bone[0]] * len(pts))
    g.F.append(tuple(range(i, i + len(pts))))


def _auto_uv(m, pts, off):
    """UV planar em metros reais, pelo eixo dominante da normal da face."""
    (ax, ay, az), (bx, by, bz), (cx, cy, cz) = pts[0], pts[1], pts[2]
    u = (bx - ax, by - ay, bz - az)
    v = (cx - ax, cy - ay, cz - az)
    n = (abs(u[1] * v[2] - u[2] * v[1]), abs(u[2] * v[0] - u[0] * v[2]), abs(u[0] * v[1] - u[1] * v[0]))
    k = n.index(max(n))
    tu, tv = m["tile_u"], m["tile_v"]
    out = []
    for x, y, z in pts:
        a, b = ((y, z), (x, z), (x, y))[k]
        out.append((a / tu + off[0], b / tv + off[1]))
    return out


def box(m, c, s, col=True, rz=0.0, uv=(0.0, 0.0), face_uv=None):
    """Caixa com centro c e tamanho s (no sistema local do conjunto)."""
    g = G(m, col)
    hx, hy, hz = s[0] / 2, s[1] / 2, s[2] / 2
    base = [(-hx, -hy, -hz), (hx, -hy, -hz), (hx, hy, -hz), (-hx, hy, -hz),
            (-hx, -hy, hz), (hx, -hy, hz), (hx, hy, hz), (-hx, hy, hz)]
    cr, sr = math.cos(rz), math.sin(rz)
    pts = [W((c[0] + x * cr - y * sr, c[1] + x * sr + y * cr, c[2] + z)) for x, y, z in base]
    faces = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (2, 3, 7, 6), (3, 0, 4, 7), (1, 2, 6, 5)]
    for fi, f in enumerate(faces):
        p = [pts[i] for i in f]
        _quad(g, p, face_uv(fi) if face_uv else _auto_uv(m, p, uv))


def cyl(m, c, r, h, n=8, r2=None, col=False, axis="z", uv=(0.0, 0.0)):
    g = G(m, col)
    r2 = r if r2 is None else r2
    ang = [2 * math.pi * i / n for i in range(n)]

    def P(radius, a, z):
        x, y = radius * math.cos(a), radius * math.sin(a)
        if axis == "x":
            x, z = z, x
        return W((c[0] + x, c[1] + y, c[2] + z))

    flip = axis == "x"
    circ = 2 * math.pi * max(r, r2)
    for i in range(n):
        j = (i + 1) % n
        q = [P(r, ang[i], -h / 2), P(r, ang[j], -h / 2), P(r2, ang[j], h / 2), P(r2, ang[i], h / 2)]
        u0, u1 = i / n * circ / m["tile_u"] + uv[0], (i + 1) / n * circ / m["tile_u"] + uv[0]
        v0, v1 = uv[1], h / m["tile_v"] + uv[1]
        uvs = [(u0, v0), (u1, v0), (u1, v1), (u0, v1)]
        if flip:
            q.reverse()
            uvs.reverse()
        _quad(g, q, uvs)
    for z, rad, order in ((h / 2, r2, 1), (-h / 2, r, -1)):
        poly = [P(rad, a, z) for a in ang][::order * (-1 if flip else 1)]
        uvs = [((p[0]) / m["tile_u"], (p[1]) / m["tile_v"]) for p in poly]
        _quad(g, poly, uvs)


def flush(prefix=""):
    for g in _groups.values():
        name = f"{prefix}{g.m.name}" + ("-col" if g.collide else "")
        me = bpy.data.meshes.new(name)
        me.from_pydata(g.V, [], g.F)
        me.update()
        uvl = me.uv_layers.new(name="UVMap")
        for poly in me.polygons:
            for li in poly.loop_indices:
                uvl.data[li].uv = g.UV[me.loops[li].vertex_index]
        me.materials.append(g.m)
        o = bpy.data.objects.new(name, me)
        bpy.context.scene.collection.objects.link(o)
        if _rig[0] is not None and any(g.B):
            for bn in sorted({b for b in g.B if b}):
                o.vertex_groups.new(name=bn).add([i for i, b in enumerate(g.B) if b == bn], 1.0, "REPLACE")
            o.modifiers.new("Armature", "ARMATURE").object = _rig[0]
            o.parent = _rig[0]
    _groups.clear()


def export(name):
    flush()
    path = os.path.join(OUT, name + ".glb")
    extra = {"export_animations": True, "export_animation_mode": "ACTIONS"} if _rig[0] is not None else {}
    bpy.ops.export_scene.gltf(filepath=path, export_format="GLB", export_apply=False,
                              export_image_format="AUTO", export_yup=True, **extra)
    print("EXPORTADO", path)


# ----------------------------------------------------------------------------------------------
# Cômodo: Gabinete de Sergei
# ----------------------------------------------------------------------------------------------
def gabinete():
    random.seed(11)
    WP, PQ, PL = mat("wallpaper"), mat("parquet"), mat("plaster")
    WD, LT, MT, PP = mat("wood_dark"), mat("leather"), mat("metal"), mat("paper")
    RG, BK, CUR = mat("rug"), mat("books"), mat("cardigan")
    NIGHT = mat(None, emit=(0.03, 0.06, 0.14), strength=0.4, color=(0, 0, 0))
    LIGHTS = mat(None, emit=(1.0, 0.8, 0.4), strength=2.5, color=(0, 0, 0))
    AMBER = mat(None, emit=(1.0, 0.65, 0.25), strength=1.6, color=(0.4, 0.3, 0.1))
    GREEN = mat(None, emit=(0.25, 0.8, 0.45), strength=1.2, color=(0.1, 0.3, 0.15))
    BLACK = mat(None, color=(0.05, 0.05, 0.06))
    DARK = mat(None, color=(0.04, 0.05, 0.08))
    Wd, Dd, H = 6.4, 5.6, 3.3  # largura x, profundidade y, altura
    hx, hy = Wd / 2, Dd / 2

    # piso, teto, vigas
    box(PQ, (0, 0, -0.05), (Wd + 0.6, Dd + 0.6, 0.1))
    box(PL, (0, 0, H + 0.05), (Wd + 0.6, Dd + 0.6, 0.1))
    for y in (-1.2, 1.2):
        box(WD, (0, y, H - 0.1), (Wd, 0.25, 0.2))
    # paredes (wallpaper) com vãos: porta (sul) e duas janelas (norte)
    box(WP, (-hx - 0.1, 0, H / 2), (0.2, Dd + 0.4, H))
    box(WP, (hx + 0.1, 0, H / 2), (0.2, Dd + 0.4, H))
    for x0, x1 in ((-hx - 0.2, 1.6), (2.6, hx + 0.2)):  # sul, a porta fica entre 1.6 e 2.6
        box(WP, ((x0 + x1) / 2, -hy - 0.1, H / 2), (x1 - x0, 0.2, H))
    box(WP, (2.1, -hy - 0.1, 2.2 + (H - 2.2) / 2), (1.0, 0.2, H - 2.2))
    sill, head = 0.95, 2.55
    wins = (-1.6, 1.6)
    for x0, x1 in ((-hx - 0.2, -2.2), (-1.0, 1.0), (2.2, hx + 0.2)):  # norte, entre as janelas
        box(WP, ((x0 + x1) / 2, hy + 0.1, H / 2), (x1 - x0, 0.2, H))
    for xc in wins:
        box(WP, (xc, hy + 0.1, sill / 2), (1.2, 0.2, sill))
        box(WP, (xc, hy + 0.1, head + (H - head) / 2), (1.2, 0.2, H - head))
        # moldura, travessas, vidro noturno, parapeito, cortinas, radiador
        for dx in (-0.62, 0.62):
            box(WD, (xc + dx, hy - 0.04, (sill + head) / 2), (0.06, 0.1, head - sill + 0.1), col=False)
        for z in (sill - 0.03, head + 0.03):
            box(WD, (xc, hy - 0.04, z), (1.3, 0.1, 0.06), col=False)
        box(WD, (xc, hy - 0.04, (sill + head) / 2), (0.03, 0.06, head - sill), col=False)
        box(WD, (xc, hy - 0.04, (sill + head) / 2 + 0.1), (1.2, 0.06, 0.03), col=False)
        box(NIGHT, (xc, hy + 0.12, (sill + head) / 2), (1.2, 0.02, head - sill), col=False)
        box(WD, (xc, hy - 0.2, sill - 0.04), (1.5, 0.35, 0.06), col=False)
        for dx in (-0.85, 0.85):
            box(CUR, (xc + dx, hy - 0.18, 1.75), (0.45, 0.14, 2.5), col=False)
        box(MT, (xc, hy - 0.12, 0.42), (1.0, 0.12, 0.6))
        for k in range(8):
            box(MT, (xc - 0.42 + k * 0.12, hy - 0.12, 0.42), (0.03, 0.14, 0.62), col=False)
    # horizonte noturno atrás do vidro: silhuetas e janelas acesas
    for i in range(14):
        x = -2.4 + i * 0.36
        h = random.uniform(1.0, 2.2)
        box(DARK, (x, hy + 0.9, h / 2 + 0.4), (0.34, 0.1, h), col=False)
        for _ in range(random.randint(1, 4)):
            box(LIGHTS, (x + random.uniform(-0.1, 0.1), hy + 0.84, random.uniform(0.7, h + 0.3)), (0.05, 0.02, 0.05), col=False)
    # lambril (parte baixa em madeira), rodapé, friso, sanca
    for z0, h0 in ((0.0, 1.0),):
        for (c, s) in (((-hx + 0.02, 0, z0 + h0 / 2), (0.04, Dd, h0)), ((hx - 0.02, 0, z0 + h0 / 2), (0.04, Dd, h0)),
                       ((0, hy - 0.02, z0 + h0 / 2), (Wd, 0.04, h0)), ((0, -hy + 0.02, z0 + h0 / 2), (Wd, 0.04, h0))):
            box(WD, c, s, col=False)
    for (c, s) in (((-hx + 0.04, 0, 1.0), (0.08, Dd, 0.06)), ((hx - 0.04, 0, 1.0), (0.08, Dd, 0.06)),
                   ((0, hy - 0.04, 1.0), (Wd, 0.08, 0.06)), ((0, -hy + 0.04, 1.0), (Wd, 0.08, 0.06)),
                   ((-hx + 0.05, 0, H - 0.08), (0.1, Dd, 0.14)), ((hx - 0.05, 0, H - 0.08), (0.1, Dd, 0.14)),
                   ((0, hy - 0.05, H - 0.08), (Wd, 0.1, 0.14)), ((0, -hy + 0.05, H - 0.08), (Wd, 0.1, 0.14))):
        box(PL if c[2] > 2 else WD, c, s, col=False)
    # porta
    for dx in (-0.55, 0.55):
        box(WD, (2.1 + dx, -hy + 0.04, 1.1), (0.1, 0.12, 2.2), col=False)
    box(WD, (2.1, -hy + 0.04, 2.25), (1.2, 0.12, 0.1), col=False)
    box(WD, (2.1, -hy + 0.02, 1.05), (0.98, 0.05, 2.1))
    box(MT, (1.7, -hy + 0.08, 1.0), (0.04, 0.06, 0.12), col=False)

    # tapete, estantes (parede oeste)
    box(RG, (0, 0.1, 0.011), (3.6, 2.6, 0.02), col=False)
    with xf(-hx + 0.2, 0.0):
        box(WD, (-0.16, 0, 1.55), (0.03, 4.2, 3.1))
        for y in (-2.1, 2.1):
            box(WD, (0, y, 1.55), (0.36, 0.05, 3.1))
        for k in range(7):
            z = 0.12 + k * 0.5
            box(WD, (0, 0, z), (0.36, 4.2, 0.04))
            if k == 6:
                break
            y = -2.0
            while y < 1.95:
                w = random.uniform(0.03, 0.07)
                d = random.uniform(0.2, 0.3)
                h = random.uniform(0.22, 0.4)
                box(BK, (-0.14 + d / 2, y + w / 2, z + 0.02 + h / 2), (d, w, h), col=False,
                    uv=(random.random(), 0.0))
                y += w + 0.002
                if random.random() < 0.05:
                    y += random.uniform(0.1, 0.3)
    # mesa de trabalho (centro norte) + cadeira
    with xf(0, 1.55):
        box(WD, (0, 0, 0.74), (2.2, 0.95, 0.06))
        for dx in (-0.85, 0.85):
            box(WD, (dx, 0, 0.36), (0.55, 0.85, 0.7))
            for k in range(3):
                box(MT, (dx, -0.43, 0.14 + k * 0.22), (0.1, 0.02, 0.025), col=False)
        box(WD, (0, 0.36, 0.45), (1.1, 0.04, 0.5), col=False)
        # sobre a mesa
        box(PP, (0.25, -0.05, 0.775), (0.42, 0.55, 0.01), col=False, rz=0.15)
        box(PP, (0.55, 0.1, 0.775), (0.3, 0.4, 0.01), col=False, rz=-0.3)
        box(BLACK, (0.78, 0.15, 0.8), (0.2, 0.22, 0.07), col=False)
        box(BLACK, (0.78, 0.15, 0.86), (0.12, 0.07, 0.04), col=False)
        box(MT, (-0.3, 0.05, 0.8), (0.36, 0.3, 0.1), col=False)  # máquina de escrever
        box(BLACK, (-0.3, 0.05, 0.86), (0.3, 0.2, 0.03), col=False)
        cyl(PP, (-0.6, -0.1, 0.8), 0.04, 0.5, n=8, axis="x", col=False)  # rolos de planta
        cyl(MT, (0.05, 0.3, 0.775), 0.06, 0.03, n=8, col=False)           # cinzeiro
        # abajur de banqueiro
        box(MT, (-0.85, 0.0, 0.79), (0.2, 0.14, 0.04), col=False)
        box(MT, (-0.85, 0.0, 0.93), (0.03, 0.03, 0.26), col=False)
        box(GREEN, (-0.85, 0.0, 1.07), (0.34, 0.14, 0.12), col=False)
    with xf(0, 2.35, math.pi):  # cadeira atrás da mesa (olhando para o sul)
        box(LT, (0, 0, 0.48), (0.5, 0.5, 0.1))
        box(LT, (0, 0.22, 0.85), (0.5, 0.08, 0.7))
        for dx in (-0.2, 0.2):
            for dy in (-0.2, 0.2):
                box(WD, (dx, dy, 0.22), (0.05, 0.05, 0.44), col=False)
    # sofá + mesa de centro (leste)
    with xf(2.45, -0.6, math.pi / 2):
        box(LT, (0, 0, 0.25), (2.0, 0.9, 0.5))
        box(LT, (0, 0.38, 0.75), (2.0, 0.18, 0.55))
        for dx in (-0.95, 0.95):
            box(LT, (dx, 0, 0.55), (0.18, 0.9, 0.4))
    with xf(1.15, -0.6):
        box(WD, (0, 0, 0.45), (0.7, 1.1, 0.05))
        for dx in (-0.3, 0.3):
            for dy in (-0.5, 0.5):
                box(WD, (dx, dy, 0.21), (0.05, 0.05, 0.42), col=False)
    # poltrona de leitura
    with xf(-0.6, -1.4, math.radians(30)):
        box(LT, (0, 0, 0.25), (0.8, 0.8, 0.5))
        box(LT, (0, 0.32, 0.75), (0.8, 0.16, 0.55))
        for dx in (-0.36, 0.36):
            box(LT, (dx, 0, 0.55), (0.12, 0.8, 0.3))
    # arquivo de aço, cabideiro com casaco
    with xf(-2.6, -2.3):
        box(MT, (0, 0, 0.65), (0.5, 0.6, 1.3))
        for k in range(4):
            box(BLACK, (0, -0.31, 0.2 + k * 0.3), (0.4, 0.02, 0.22), col=False)
            box(MT, (0, -0.33, 0.2 + k * 0.3), (0.12, 0.02, 0.03), col=False)
    with xf(0.9, -2.45):
        cyl(WD, (0, 0, 0.9), 0.025, 1.8, n=6)
        box(WD, (0, 0, 0.03), (0.4, 0.4, 0.06), col=False)
        box(mat("trousers"), (0, 0.02, 1.35), (0.42, 0.14, 0.9), col=False)  # casaco
    # abajur de pé (canto nordeste)
    with xf(2.7, 2.3):
        cyl(MT, (0, 0, 0.8), 0.02, 1.6, n=6)
        box(MT, (0, 0, 0.02), (0.3, 0.3, 0.04), col=False)
        cyl(AMBER, (0, 0, 1.55), 0.22, 0.3, n=8, r2=0.12, col=False)
    # quadros (leste) e luminárias de parede (sul)
    for y in (-1.7, -0.7, 0.4):
        box(WD, (hx - 0.05, y, 1.95), (0.03, 0.5, 0.64), col=False)
        box(PP, (hx - 0.07, y, 1.95), (0.02, 0.42, 0.56), col=False)
    for x in (-1.7, 0.1):
        box(MT, (x, -hy + 0.08, 2.1), (0.06, 0.1, 0.1), col=False)
        box(AMBER, (x, -hy + 0.16, 2.15), (0.14, 0.12, 0.2), col=False)
    # tubulação aparente no teto e cano vertical
    cyl(MT, (0, -hy + 0.25, H - 0.35), 0.05, Wd, n=8, axis="x", col=False)
    cyl(MT, (-hx + 0.3, -hy + 0.25, H / 2 - 0.2), 0.04, H - 0.5, n=8, col=False)
    # pendente central
    box(BLACK, (0, 0.0, H - 0.5), (0.015, 0.015, 0.8), col=False)
    cyl(MT, (0, 0.0, H - 1.0), 0.28, 0.2, n=8, r2=0.1, col=False)
    box(LIGHTS, (0, 0.0, H - 1.09), (0.07, 0.07, 0.07), col=False)
    # rádio sobre o arquivo de aço e relógio de parede: fontes visíveis do rádio de 1993 e do tique-taque
    with xf(-2.6, -2.3):
        box(WD, (0, 0, 1.40), (0.34, 0.16, 0.2), col=False)
        box(BLACK, (-0.06, -0.082, 1.40), (0.16, 0.01, 0.12), col=False)  # alto-falante
        box(AMBER, (0.1, -0.082, 1.44), (0.08, 0.01, 0.03), col=False)    # visor do dial
        box(MT, (0.1, -0.085, 1.37), (0.03, 0.02, 0.03), col=False)       # botão
    box(WD, (-0.9, -hy + 0.03, 2.45), (0.34, 0.05, 0.34), col=False)
    box(PP, (-0.9, -hy + 0.058, 2.45), (0.28, 0.01, 0.28), col=False)
    box(BLACK, (-0.9, -hy + 0.066, 2.50), (0.012, 0.01, 0.1), col=False)  # ponteiro dos minutos
    box(BLACK, (-0.88, -hy + 0.066, 2.45), (0.08, 0.01, 0.012), col=False)  # ponteiro das horas
    export("gabinete")


# ----------------------------------------------------------------------------------------------
# Personagem: Sergei (idoso, cabelo grisalho, óculos, cardigã)
# ----------------------------------------------------------------------------------------------
def head_uv(fi):
    if fi == 2:  # face voltada para -Y (frente do modelo)
        return [(0.0, 0.0), (0.92, 0.0), (0.92, 1.0), (0.0, 1.0)]
    return [(0.97, 0.5)] * 4


def character(skin="face_sergei", top="cardigan", legs="trousers", hair="hair_grey", glasses=True):
    FACE, TOP, LEG, HAIR = mat(skin), mat(top), mat(legs), mat(hair)
    SKIN = mat(None, color=(0.70, 0.56, 0.46))
    SHIRT = mat(None, color=(0.75, 0.74, 0.68))
    SHOE = mat(None, color=(0.05, 0.04, 0.04))
    FR = mat(None, color=(0.04, 0.04, 0.05))
    for sx in (-1, 1):
        box(SHOE, (sx * 0.1, -0.03, 0.05), (0.11, 0.26, 0.1), col=False)
        box(LEG, (sx * 0.1, 0, 0.5), (0.15, 0.17, 0.8), col=False)
        box(TOP, (sx * 0.29, 0, 1.28), (0.11, 0.13, 0.34), col=False)          # braço
        box(TOP, (sx * 0.29, -0.03, 0.97), (0.10, 0.12, 0.30), col=False)      # antebraço
        box(SKIN, (sx * 0.29, -0.04, 0.78), (0.09, 0.09, 0.1), col=False)      # mão
    box(LEG, (0, 0, 0.92), (0.40, 0.23, 0.2), col=False)
    box(TOP, (0, 0, 1.28), (0.46, 0.25, 0.52), col=False)
    box(SHIRT, (0, -0.125, 1.45), (0.14, 0.02, 0.16), col=False)               # colarinho
    box(SKIN, (0, 0, 1.58), (0.11, 0.11, 0.08), col=False)                     # pescoço
    box(FACE, (0, 0, 1.73), (0.21, 0.23, 0.26), col=False, face_uv=head_uv)    # cabeça
    box(SKIN, (0, -0.125, 1.70), (0.04, 0.05, 0.08), col=False)                # nariz
    for sx in (-1, 1):
        box(SKIN, (sx * 0.115, 0, 1.72), (0.025, 0.05, 0.08), col=False)       # orelhas
    box(HAIR, (0, 0.03, 1.87), (0.23, 0.25, 0.08), col=False)                  # cabelo (topo)
    box(HAIR, (0, 0.11, 1.74), (0.23, 0.04, 0.2), col=False)                   # cabelo (nuca)
    for sx in (-1, 1):
        box(HAIR, (sx * 0.112, 0.03, 1.78), (0.02, 0.2, 0.12), col=False)
    if glasses:
        for sx in (-1, 1):
            cx = sx * 0.055
            for (c, s) in (((cx, -0.121, 1.745), (0.085, 0.01, 0.01)), ((cx, -0.121, 1.695), (0.085, 0.01, 0.01)),
                           ((cx - 0.042, -0.121, 1.72), (0.01, 0.01, 0.06)), ((cx + 0.042, -0.121, 1.72), (0.01, 0.01, 0.06))):
                box(FR, c, s, col=False)
        box(FR, (0, -0.121, 1.745), (0.03, 0.01, 0.01), col=False)


def sergei():
    character()
    export("sergei")


# ----------------------------------------------------------------------------------------------
# Itens interativos
# ----------------------------------------------------------------------------------------------
def chess():
    CB, WD = mat("chessboard"), mat("wood_dark")
    LIGHT = mat(None, color=(0.82, 0.74, 0.58))
    DARK = mat(None, color=(0.12, 0.07, 0.05))
    box(WD, (0, 0, 0.0), (0.46, 0.46, 0.04), col=False)
    box(CB, (0, 0, 0.022), (0.4, 0.4, 0.004), col=False, uv=(0, 0))
    random.seed(5)
    cells = [(i, j) for i in range(8) for j in range(8)]
    for (i, j) in cells:
        if random.random() < 0.28:
            m = LIGHT if random.random() < 0.5 else DARK
            x, y = -0.175 + i * 0.05, -0.175 + j * 0.05
            h = random.choice([0.05, 0.05, 0.07, 0.09])
            cyl(m, (x, y, 0.024 + h / 2), 0.016, h, n=8, r2=0.01, col=False)
    export("chess")


def plans():
    PP, BL = mat("paper"), mat(None, color=(0.15, 0.25, 0.45))
    box(PP, (0, 0, 0.0), (0.7, 0.5, 0.01), col=False)
    box(BL, (0.0, 0.0, 0.006), (0.66, 0.46, 0.002), col=False)
    for k in range(6):
        box(PP, (-0.2 + k * 0.08, -0.1 + (k % 2) * 0.12, 0.008), (0.05, 0.05, 0.002), col=False)
    export("plans")


JOBS = {"gabinete": gabinete, "sergei": sergei, "chess": chess, "plans": plans}

if __name__ == "__main__":
    names = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else list(JOBS)
    for n in names:
        reset()
        JOBS[n]()
