"""Gera personagens com esqueleto e animação (idle, talk) para o Godot.

Uso:  blender -b -P tools/character.py -- sergei
Técnica: partes "esculpidas" por seções (loft) e skinning rígido por osso, como em jogos PS1 (RE, Silent Hill).
Frente do modelo: -Y no Blender (+Z no glTF). Lado esquerdo do personagem = +X.
Personagens: sergei (idoso, óculos, cardigã) e boris (policial robusto, bigode, farda).
"""
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402
from mathutils import Euler, Vector  # noqa: E402

import kit  # noqa: E402
from kit import box, mat  # noqa: E402


class bone:
    """with bone("head"): ...  — tudo que for criado ali é pesado 100% a esse osso."""
    def __init__(self, name):
        self.name = name

    def __enter__(self):
        self.old = kit._bone[0]
        kit._bone[0] = self.name

    def __exit__(self, *a):
        kit._bone[0] = self.old


def loft(m, rings, n=10, cap_top=True, cap_bot=True, uv_fn=None, power=2.0):
    """Sólido por seções: rings = [(z, cx, cy, rx, ry), ...] de baixo para cima. power>2 deixa a seção mais quadrada."""
    g = kit.G(m, False)
    e = 2.0 / power

    def pt(r, k):
        z, cx, cy, rx, ry = r
        a = 2 * math.pi * k / n
        c, s = math.cos(a), math.sin(a)
        return kit.W((cx + rx * math.copysign(abs(c) ** e, c), cy + ry * math.copysign(abs(s) ** e, s), z))

    P = [[pt(r, k) for k in range(n)] for r in rings]
    uv = uv_fn or (lambda q: kit._auto_uv(m, q, (0.0, 0.0)))
    for i in range(len(rings) - 1):
        for k in range(n):
            j = (k + 1) % n
            q = [P[i][k], P[i][j], P[i + 1][j], P[i + 1][k]]
            kit._quad(g, q, uv(q))
    if cap_top:
        q = P[-1][:]
        kit._quad(g, q, uv(q))
    if cap_bot:
        q = P[0][::-1]
        kit._quad(g, q, uv(q))


# ----------------------------------------------------------------------------------------------
# Esqueleto
# ----------------------------------------------------------------------------------------------
def bones_spec():
    b = {
        "hips": ((0, 0, 0.88), (0, 0, 1.0), None),
        "spine": ((0, 0, 1.0), (0, 0, 1.28), "hips"),
        "chest": ((0, 0, 1.28), (0, 0, 1.50), "spine"),
        "neck": ((0, 0, 1.50), (0, 0, 1.61), "chest"),
        "head": ((0, 0, 1.61), (0, 0, 1.97), "neck"),
    }
    for sx, s in ((1, "L"), (-1, "R")):
        b[f"upper_arm.{s}"] = ((sx * 0.25, 0, 1.45), (sx * 0.27, 0, 1.17), "chest")
        b[f"forearm.{s}"] = ((sx * 0.27, 0, 1.17), (sx * 0.27, -0.02, 0.91), f"upper_arm.{s}")
        b[f"hand.{s}"] = ((sx * 0.27, -0.02, 0.91), (sx * 0.27, -0.03, 0.75), f"forearm.{s}")
        b[f"thigh.{s}"] = ((sx * 0.10, 0, 0.90), (sx * 0.10, 0, 0.50), "hips")
        b[f"shin.{s}"] = ((sx * 0.10, 0, 0.50), (sx * 0.10, 0, 0.10), f"thigh.{s}")
        b[f"foot.{s}"] = ((sx * 0.10, 0, 0.10), (sx * 0.10, -0.22, 0.04), f"shin.{s}")
    return b


def make_rig():
    data = bpy.data.armatures.new("Rig")
    arm = bpy.data.objects.new("Rig", data)
    bpy.context.scene.collection.objects.link(arm)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.mode_set(mode="EDIT")
    for name, (head, tail, parent) in bones_spec().items():
        eb = data.edit_bones.new(name)
        eb.head, eb.tail = head, tail
        if parent:
            eb.parent = data.edit_bones[parent]
            eb.use_connect = False
    bpy.ops.object.mode_set(mode="OBJECT")
    kit._rig[0] = arm
    return arm


def _pose(arm, name, wx, wy, wz, frame):
    """Rotação em eixos do MUNDO (relativa ao repouso) convertida para o espaço local do osso."""
    pb = arm.pose.bones[name]
    M = pb.bone.matrix_local.to_3x3()
    R = Euler((wx, wy, wz)).to_matrix()
    pb.rotation_mode = "QUATERNION"
    pb.rotation_quaternion = (M.inverted() @ R @ M).to_quaternion()
    pb.keyframe_insert("rotation_quaternion", frame=frame)


def make_action(arm, name, frames, pose_fn):
    """pose_fn(phase) -> {osso: (wx, wy, wz)} com phase em [0, 2π). O primeiro e o último quadro são iguais (loop)."""
    arm.animation_data_create()
    act = bpy.data.actions.new(name)
    arm.animation_data.action = act
    for f in range(frames + 1):
        phase = 2 * math.pi * (f % frames) / frames
        pose = pose_fn(phase)
        for bn in arm.pose.bones.keys():
            _pose(arm, bn, *pose.get(bn, (0, 0, 0)), frame=1 + f)
        pb = arm.pose.bones["hips"]                                            # "drop": abaixa o corpo inteiro (sentar)
        pb.location = pb.bone.matrix_local.to_3x3().inverted() @ Vector((0, 0, -pose.get("drop", 0.0)))
        pb.keyframe_insert("location", frame=1 + f)
    track = arm.animation_data.nla_tracks.new()
    track.strips.new(name, 1, act)
    arm.animation_data.action = None


def idle(p):
    s = math.sin
    return {
        "chest": (0.014 * s(p), 0, 0.01 * s(p + 1.0)),
        "spine": (0.006 * s(p + 0.4), 0, 0),
        "head": (0.02 * s(p + 0.8), 0.05 * s(p + 2.0), 0.015 * s(p)),
        "upper_arm.L": (0, 0.02 * s(p), 0),
        "upper_arm.R": (0, -0.02 * s(p), 0),
        "hips": (0.004 * s(p), 0, 0),
    }


def talk(p):
    s = math.sin
    d = idle(p)
    d["upper_arm.R"] = (-0.55 + 0.18 * s(2 * p), -0.1, 0)
    d["forearm.R"] = (-0.75 + 0.22 * s(2 * p + 1.0), 0, 0)
    d["hand.R"] = (0.25 * s(3 * p), 0, 0)
    d["upper_arm.L"] = (-0.12 + 0.05 * s(2 * p + 2.0), 0.03, 0)
    d["head"] = (0.04 * s(2 * p), 0.08 * s(p + 2.0), 0.02 * s(p))
    d["chest"] = (0.02 * s(2 * p), 0.03 * s(p), 0)
    return d


def sit(p):
    """Sentado à mesa: coxas na horizontal, canelas na vertical, antebraços apoiados no tampo (0,75 m)."""
    d = idle(p)
    d["drop"] = 0.42
    for s in "LR":
        d[f"thigh.{s}"] = (-math.pi / 2, 0, 0)
        d[f"shin.{s}"] = (math.pi / 2, 0, 0)
        d[f"upper_arm.{s}"] = (-0.35, 0, 0)
        d[f"forearm.{s}"] = (-1.25, 0, 0)
    d["chest"] = (0.05 + 0.014 * math.sin(p), 0, 0)                          # leve inclinação para a mesa
    return d


def sit_talk(p):
    d = sit(p)
    t = talk(p)
    for k in ("upper_arm.R", "forearm.R", "hand.R", "head", "chest"):
        d[k] = t[k]
    return d


def sleep(p):
    """Dormindo debruçado sobre a mesa, a cabeça sobre os braços cruzados."""
    d = sit(p)
    b = 0.012 * math.sin(p)                                                    # respiração lenta
    d["spine"] = (0.45 + b, 0, 0)                                              # x positivo inclina para a frente (-y)
    d["chest"] = (0.45, 0, 0)
    d["neck"] = (0.25, 0, 0)
    d["head"] = (0.2, 0.25, 0)
    for s, side in (("L", 1), ("R", -1)):
        d[f"upper_arm.{s}"] = (-1.0, 0, 0)
        d[f"forearm.{s}"] = (-0.3, 0, -side * 1.3)                             # antebraços cruzados para dentro
    return d


# ----------------------------------------------------------------------------------------------
# Corpo
# ----------------------------------------------------------------------------------------------
def build_person(face="face_sergei_neutral", top="cardigan", legs="trousers", hair="hair_grey", glasses=True,
                 mustache=False, tie=(0.30, 0.06, 0.07), shoulders=1.0, long_hair=False, kind="plain"):
    FACE = mat(face)
    TOP, LEG, HAIR = mat(top), mat(legs), mat(hair)
    SKIN = mat(None, color=(0.72, 0.57, 0.47))
    SHIRT = mat(None, color=(0.78, 0.76, 0.68))
    TIE = mat(None, color=tie)
    S = shoulders
    SHOE = mat(None, color=(0.05, 0.04, 0.04))
    FR = mat(None, color=(0.04, 0.04, 0.05))
    BUTTON = mat(None, color=(0.12, 0.09, 0.06))

    HC_Y = 0.012  # centro (y) da cabeça

    def head_uv(q):
        cy = sum(p[1] for p in q) / len(q)
        cz = sum(p[2] for p in q) / len(q)
        if cy < HC_Y - 0.04 and 1.62 < cz < 1.94:  # voltada para a frente: projeção planar do rosto pintado
            return [((p[0]) / 0.21 + 0.5, (p[2] - 1.615) / 0.33) for p in q]
        return [(0.97, 0.5)] * len(q)

    with bone("hips"):
        loft(LEG, [(0.78, 0, 0, 0.17, 0.10), (0.88, 0, 0, 0.19, 0.11), (1.00, 0, 0, 0.19, 0.115)])
    with bone("spine"):
        loft(TOP, [(1.00, 0, 0, 0.19 * S, 0.115), (1.12, 0, 0, 0.20 * S, 0.12), (1.28, 0, 0, 0.215 * S, 0.125)],
             cap_bot=False, cap_top=False)
    with bone("chest"):
        loft(TOP, [(1.28, 0, 0, 0.215 * S, 0.125), (1.40, 0, 0, 0.255 * S, 0.13), (1.47, 0, 0, 0.22 * S, 0.115),
                   (1.53, 0, 0, 0.085, 0.075)], cap_bot=False)
        if kind in ("plain", "uniform"):                                         # camisa e gravata (Lena e Irina não usam)
            box(SHIRT, (0, -0.126, 1.38), (0.11, 0.012, 0.28), col=False)
            box(TIE, (0, -0.134, 1.36), (0.035, 0.012, 0.25), col=False)
        for z in (1.30, 1.20, 1.10):
            box(BUTTON, (0.075, -0.134, z - 0.02), (0.014, 0.01, 0.014), col=False)
        for sx in ((1, -1) if kind in ("plain", "uniform") else ()):
            box(SHIRT, (sx * 0.04, -0.118, 1.51), (0.055, 0.02, 0.08), col=False, rz=sx * 0.35)  # colarinho
    with bone("neck"):
        loft(SKIN, [(1.49, 0, 0, 0.060, 0.060), (1.62, 0, -0.004, 0.052, 0.055)], n=8)
    with bone("head"):
        loft(FACE, [(1.615, 0, HC_Y - 0.005, 0.045, 0.060), (1.66, 0, HC_Y, 0.085, 0.092),
                    (1.73, 0, HC_Y, 0.105, 0.112), (1.80, 0, HC_Y, 0.110, 0.118),
                    (1.88, 0, HC_Y, 0.098, 0.108), (1.94, 0, HC_Y, 0.060, 0.070)], n=10, uv_fn=head_uv)
        box(SKIN, (0, -0.112, 1.745), (0.034, 0.05, 0.075), col=False)
        if mustache:
            box(HAIR, (0, -0.118, 1.697), (0.08, 0.022, 0.02), col=False)            # nariz
        box(SKIN, (0, -0.095, 1.80), (0.15, 0.04, 0.025), col=False)             # arco superciliar
        for sx in (1, -1):
            box(SKIN, (sx * 0.112, 0.01, 1.765), (0.02, 0.045, 0.075), col=False)  # orelhas
        loft(HAIR, [(1.86, 0, HC_Y + 0.018, 0.116, 0.126), (1.915, 0, HC_Y + 0.012, 0.100, 0.112),
                    (1.975, 0, HC_Y + 0.008, 0.055, 0.065)], n=10, cap_bot=False)
        box(HAIR, (0, HC_Y + 0.105, 1.74), (0.20, 0.03, 0.19), col=False)        # nuca
        for sx in (1, -1):
            box(HAIR, (sx * 0.108, HC_Y + 0.045, 1.80), (0.02, 0.15, 0.10), col=False)  # laterais
        if long_hair:                                                              # cabelo comprido até os ombros
            box(HAIR, (0, HC_Y + 0.115, 1.62), (0.25, 0.05, 0.40), col=False)
            for sx in (1, -1):
                box(HAIR, (sx * 0.118, HC_Y + 0.03, 1.66), (0.03, 0.16, 0.32), col=False)
        for sx in ((1, -1) if glasses else ()):                                  # óculos
            cx = sx * 0.047
            for c, s in (((cx, -0.119, 1.783), (0.075, 0.008, 0.008)), ((cx, -0.119, 1.727), (0.075, 0.008, 0.008)),
                         ((cx - 0.037, -0.119, 1.755), (0.008, 0.008, 0.064)), ((cx + 0.037, -0.119, 1.755), (0.008, 0.008, 0.064))):
                box(FR, c, s, col=False)
            box(FR, (sx * 0.1, -0.06, 1.783), (0.008, 0.12, 0.008), col=False)   # haste
        if glasses:
            box(FR, (0, -0.119, 1.775), (0.03, 0.008, 0.008), col=False)

    for sx, s in ((1, "L"), (-1, "R")):
        with bone(f"upper_arm.{s}"):
            loft(TOP, [(1.16, sx * 0.272, 0, 0.050, 0.052), (1.30, sx * 0.272, 0, 0.060, 0.062),
                       (1.45, sx * 0.255, 0, 0.068, 0.066)], n=8)
        with bone(f"forearm.{s}"):
            loft(TOP, [(0.92, sx * 0.272, -0.025, 0.042, 0.042), (1.05, sx * 0.272, -0.012, 0.047, 0.047),
                       (1.17, sx * 0.272, 0, 0.052, 0.052)], n=8)
            loft(SHIRT, [(0.90, sx * 0.272, -0.026, 0.044, 0.044), (0.935, sx * 0.272, -0.025, 0.044, 0.044)], n=8)
        with bone(f"hand.{s}"):
            loft(SKIN, [(0.76, sx * 0.272, -0.034, 0.030, 0.018), (0.83, sx * 0.272, -0.032, 0.042, 0.026),
                        (0.91, sx * 0.272, -0.026, 0.038, 0.030)], n=8)
            box(SKIN, (sx * 0.31, -0.05, 0.86), (0.014, 0.03, 0.06), col=False)  # polegar
        with bone(f"thigh.{s}"):
            loft(LEG, [(0.50, sx * 0.10, 0, 0.062, 0.068), (0.70, sx * 0.10, 0, 0.078, 0.084),
                       (0.90, sx * 0.10, 0, 0.088, 0.095)], n=8)
        with bone(f"shin.{s}"):
            loft(LEG, [(0.10, sx * 0.10, 0, 0.043, 0.048), (0.30, sx * 0.10, 0, 0.052, 0.058),
                       (0.50, sx * 0.10, 0, 0.062, 0.068)], n=8)
        with bone(f"foot.{s}"):
            box(SHOE, (sx * 0.10, -0.075, 0.05), (0.095, 0.27, 0.10), col=False)
            box(SHOE, (sx * 0.10, -0.17, 0.035), (0.085, 0.10, 0.07), col=False)

    # ---- acessórios: cinto, dedos, relógio, sola do sapato, lapelas e bolsos; extras por `kind` (uniform, coat, shawl) ----------------
    BELT = mat(None, color=(0.06, 0.05, 0.04))
    BRASS_ = mat(None, color=(0.75, 0.62, 0.25))
    SOLE = mat(None, color=(0.22, 0.20, 0.18))
    DARKTOP = mat(None, color=(0.10, 0.10, 0.11))
    with bone("spine"):
        box(BELT, (0, 0, 1.0), (0.395, 0.245, 0.04), col=False)
        box(BRASS_, (0, -0.126, 1.0), (0.05, 0.01, 0.034), col=False)
        for sx in (1, -1):
            box(DARKTOP, (sx * 0.10, -0.128, 1.14), (0.09, 0.012, 0.04), col=False)          # aba de bolso
    with bone("chest"):
        for sx in (1, -1):
            box(DARKTOP, (sx * 0.075, -0.13, 1.35), (0.05, 0.012, 0.20), col=False, rz=sx * 0.12)   # lapela
        if kind == "uniform":
            for sx in (1, -1):
                box(BRASS_, (sx * 0.20, 0, 1.495), (0.085, 0.12, 0.012), col=False)           # dragonas
            box(BRASS_, (-0.09, -0.134, 1.36), (0.04, 0.01, 0.05), col=False)                 # distintivo
            box(BRASS_, (0.09, -0.134, 1.22), (0.016, 0.01, 0.016), col=False)
        if kind == "coat":
            box(DARKTOP, (0, -0.075, 1.52), (0.34, 0.04, 0.08), col=False)                    # gola alta
            box(mat(None, color=(0.55, 0.10, 0.12)), (0, 0, 1.55), (0.16, 0.15, 0.05), col=False)   # cachecol
        if kind == "shawl":
            box(mat(None, color=(0.58, 0.46, 0.38)), (0, 0, 1.46), (0.52, 0.30, 0.07), col=False)    # xale sobre os ombros
    for sx, s_ in ((1, "L"), (-1, "R")):
        with bone(f"hand.{s_}"):
            for i in range(4):
                box(SKIN, (sx * 0.272 + (i - 1.5) * 0.012, -0.033, 0.735), (0.010, 0.024, 0.055 - 0.004 * abs(i - 1.5)), col=False)
        with bone(f"foot.{s_}"):
            box(SOLE, (sx * 0.10, -0.075, 0.012), (0.098, 0.275, 0.025), col=False)
            box(SOLE, (sx * 0.10, -0.17, 0.012), (0.088, 0.105, 0.025), col=False)
    with bone("forearm.L"):
        box(mat(None, color=(0.6, 0.6, 0.62)), (0.272, -0.025, 0.95), (0.098, 0.098, 0.022), col=False)    # relógio de pulso
        box(mat(None, color=(0.85, 0.85, 0.80)), (0.272, -0.075, 0.95), (0.034, 0.008, 0.026), col=False)


def _animated(name, **look):
    arm = make_rig()
    build_person(**look)
    make_action(arm, "idle", 72, idle)
    make_action(arm, "talk", 72, talk)
    make_action(arm, "sit", 72, sit)
    make_action(arm, "sit_talk", 72, sit_talk)
    make_action(arm, "sleep", 120, sleep)
    kit.export(name)


def sergei():
    _animated("sergei")


def boris():
    """Policial de 40 anos, ombros largos, bigode, farda azul-acinzentada, sem óculos."""
    _animated("boris", face="face_boris_neutral", top="uniform", legs="trousers", hair="hair_dark", glasses=False,
              mustache=True, tie=(0.12, 0.14, 0.18), shoulders=1.14, kind="uniform")


def lena():
    """Lena, 30 anos, doente: pálida, vestido lilás, ombros estreitos."""
    _animated("lena", face="face_lena_neutral", top="dress_lena", legs="dress_lena", hair="hair_lena", glasses=False,
              tie=(0.42, 0.36, 0.46), shoulders=0.85, long_hair=True, kind="shawl")


def irina():
    """Irina, 35 anos, da KGB: casaco escuro, cabelo ruivo comprido, batom vermelho, postura firme."""
    _animated("irina", face="face_irina_neutral", top="coat_irina", legs="coat_irina", hair="hair_irina", glasses=False,
              tie=(0.55, 0.10, 0.12), shoulders=0.95, long_hair=True, kind="coat")


def treinador():
    """Treinador de xadrez e de memória: agasalho azul, cabelo grisalho, 55 anos."""
    _animated("treinador", face="face_trainer_neutral", top="tracksuit", legs="trousers", hair="hair_grey", glasses=False,
              shoulders=1.05, kind="plain")


def intermediario():
    """Intermediário do telhado: casaco marrom, bigode, chapéu de feltro baixo."""
    _animated("intermediario", face="face_inter_neutral", top="coat_dark", legs="trousers", hair="hair_dark", glasses=False,
              mustache=True, tie=(0.1, 0.1, 0.1), shoulders=1.08, kind="coat")


JOBS = {"sergei": sergei, "boris": boris, "lena": lena, "irina": irina, "treinador": treinador, "intermediario": intermediario}

if __name__ == "__main__":
    names = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else list(JOBS)
    for n in names:
        kit.reset()
        JOBS[n]()
