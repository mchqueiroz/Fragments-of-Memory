"""Gerador de episódios (cenas 11–30): lê as especificações de tools/ep/*.py e produz, para cada cena,
  * art/models/ep_<nome>.glb   (sala: casca com portas/janelas, móveis, adereços; só para cenas de interior)
  * rooms/data/<nome>.json      (tudo o que o Godot precisa: luzes, sons, personagens, pistas com colisores, diálogos, escolhas)
A cena do jogo é sempre rooms/episodio.gd lendo esse JSON (rooms/ep_<nome>.tscn).

Uso:  blender -b -P tools/episodios.py -- sala_controle treinador     (nomes) ou sem nomes = todas
Eixos: as especificações usam o Blender (x leste, y norte, z cima); o JSON grava Godot (x, z, -y). Exteriores já vêm em Godot.
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # noqa: E402, F401

import furniture  # noqa: E402
import kit  # noqa: E402
import props  # noqa: E402
from gabinete import flat, panel  # noqa: E402
from kit import box, mat  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA = os.path.join(ROOT, "rooms", "data")
os.makedirs(DATA, exist_ok=True)

THEMES = {
    "verde": dict(floor="linoleum", wall="plaster", panel="paint_green", ceil="plaster", trim="wood_dark", ph=1.2),
    "concreto": dict(floor="concrete", wall="concrete", panel=None, ceil="concrete", trim="metal", ph=0.0),
    "papel": dict(floor="parquet", wall="wallpaper", panel=None, ceil="plaster", trim="wood_dark", ph=0.0),
    "gesso": dict(floor="parquet_square", wall="plaster", panel=None, ceil="plaster", trim="wood_dark", ph=0.0),
    "azulejo": dict(floor="concrete", wall="plaster", panel="paint_green", ceil="plaster", trim="metal", ph=1.6),
}
_FACING = {"N": "-y", "S": "+y", "E": "-x", "W": "+x"}


def g(v):
    """Blender (x, y, z) -> Godot (x, z, -y)."""
    return [round(v[0], 3), round(v[2], 3), round(-v[1], 3)]


def gs(v):
    """Tamanho Blender (sx, sy, sz) -> Godot (sx, sz, sy)."""
    return [round(v[0], 3), round(v[2], 3), round(v[1], 3)]


def _wall(side, W, D, H, th, ops):
    hx, hy = W / 2, D / 2
    L = (W if side in "NS" else D) + 0.4
    fixed = {"N": hy, "S": -hy, "E": hx, "W": -hx}[side]
    sign = 1 if fixed > 0 else -1
    along_x = side in "NS"
    m = mat(th["wall"])

    def seg(a, b, z0, z1):
        if b - a < 0.01 or z1 - z0 < 0.01:
            return
        mid = (a + b) / 2
        c = (mid, fixed + sign * 0.1, (z0 + z1) / 2) if along_x else (fixed + sign * 0.1, mid, (z0 + z1) / 2)
        s = (b - a, 0.2, z1 - z0) if along_x else (0.2, b - a, z1 - z0)
        box(m, c, s)

    pos = -L / 2
    for (c, w, sill, head) in sorted(ops, key=lambda o: o[0]):
        seg(pos, c - w / 2, 0, H)
        seg(c - w / 2, c + w / 2, 0, sill)
        seg(c - w / 2, c + w / 2, head, H)
        pos = c + w / 2
    seg(pos, L / 2, 0, H)


def _opening_detail(side, W, D, c, w, sill, head, s):
    hx, hy = W / 2, D / 2
    fixed = {"N": hy, "S": -hy, "E": hx, "W": -hx}[side]
    sign = 1 if fixed > 0 else -1
    wd = mat("wood_dark")
    if sill > 0:                                                                   # janela: vidro, caixilho e (opcional) paisagem
        view = s.get("view")
        pane = mat(view, emit_tex=True, strength=1.3) if view else mat(None, emit=tuple(s.get("sky", (0.7, 0.8, 0.9))), strength=1.6, color=(0, 0, 0))
        zc = (sill + head) / 2
        if side in "NS":
            if view:
                panel(pane, (c, fixed, zc), (w - 0.1, 0.02, head - sill - 0.1), _FACING[side])
            else:
                box(pane, (c, fixed, zc), (w - 0.1, 0.02, head - sill - 0.1), col=False)
            for dx in (-w / 2, 0, w / 2):
                box(wd, (c + dx, fixed - sign * 0.04, zc), (0.05, 0.1, head - sill), col=False)
            for z in (sill, zc, head):
                box(wd, (c, fixed - sign * 0.04, z), (w + 0.04, 0.1, 0.05), col=False)
        else:
            if view:
                panel(pane, (fixed, c, zc), (0.02, w - 0.1, head - sill - 0.1), _FACING[side])
            else:
                box(pane, (fixed, c, zc), (0.02, w - 0.1, head - sill - 0.1), col=False)
            for dy in (-w / 2, 0, w / 2):
                box(wd, (fixed - sign * 0.04, c + dy, zc), (0.1, 0.05, head - sill), col=False)
            for z in (sill, zc, head):
                box(wd, (fixed - sign * 0.04, c, z), (0.1, w + 0.04, 0.05), col=False)
    else:                                                                           # porta entreaberta com fechaduras
        if side in "NS":
            props.door(side, c, fixed, w, head, angle=s.get("door_angle", 0.5))


def _panel_seg(m, side, fixed, mid, ln, ph):
    if side in "NS":
        box(m, (mid, fixed, ph / 2), (ln, 0.04, ph), col=False)
    else:
        box(m, (fixed, mid, ph / 2), (0.04, ln, ph), col=False)


def _clue_pos(c, boxes):
    if "on" in c:
        cx, cy, top, w, d = boxes[c["on"]]
        off = c.get("at", (0.0, 0.0))
        at = (cx + off[0], cy + off[1], top + c.get("dz", 0.1))
        size = c.get("size", (min(w, 0.5), min(d, 0.5), 0.25))
        return at, size
    return tuple(c["at"]), tuple(c.get("size", (0.4, 0.4, 0.4)))


def _spawn_item(it, at):
    x, y, z = at
    if it[0] == "flat":
        props.flat_tex(it[1], x, y, z - 0.09, it[2], it[3], rz=it[4] if len(it) > 4 else 0.2)
    else:
        getattr(props, it[0])(x, y, z - 0.1, **{k: tuple(v) if isinstance(v, list) else v for k, v in (it[1] if len(it) > 1 else {}).items()})


def build_room(name, s):
    kit.reset()
    W, D, H = s["size"]
    hx, hy = W / 2, D / 2
    th = THEMES[s.get("theme", "verde")]
    FL, CE = mat(th["floor"]), mat(th["ceil"])
    box(FL, (0, 0, -0.05), (W + 0.6, D + 0.6, 0.1))
    box(CE, (0, 0, H + 0.05), (W + 0.6, D + 0.6, 0.1))
    ops = {"N": [], "S": [], "E": [], "W": []}
    for (side, c, w, sill, head) in s.get("openings", []):
        ops[side].append((c, w, sill, head))
    for side in "NSEW":
        _wall(side, W, D, H, th, ops[side])
    for (side, c, w, sill, head) in s.get("openings", []):
        _opening_detail(side, W, D, c, w, sill, head, s)
    if th["panel"]:                                                                  # tinta até a cintura
        pm, ph = mat(th["panel"]), th["ph"]
        for side in "NSEW":
            L = (W if side in "NS" else D)
            fixed = {"N": hy, "S": -hy, "E": hx, "W": -hx}[side]
            sign = 1 if fixed > 0 else -1
            pos = -L / 2
            for (c, w, sill, head) in sorted(ops[side], key=lambda o: o[0]):
                if sill == 0:
                    a, b = pos, c - w / 2
                    if b - a > 0.05:
                        _panel_seg(pm, side, fixed - sign * 0.02, (a + b) / 2, b - a, ph)
                    pos = c + w / 2
            if L / 2 - pos > 0.05:
                _panel_seg(pm, side, fixed - sign * 0.02, (pos + L / 2) / 2, L / 2 - pos, ph)
    boxes = {}
    for t in s.get("things", []):
        tid, fname, x, y, rot = t[0], t[1], t[2], t[3], t[4]
        kw = t[5] if len(t) > 5 else {}
        res = getattr(furniture, fname)(x, y, **kw) if fname in ("crates", "pillar") else getattr(furniture, fname)(x, y, rot, **kw)
        if res:
            boxes[tid] = res
    for d in s.get("decor", []):                                                     # ("props"|"furniture", func, args..., {kwargs})
        mod = props if d[0] == "props" else furniture
        args = [a for a in d[2:] if not isinstance(a, dict)]
        kw = {k: tuple(v) if isinstance(v, list) else v for k, v in (d[-1] if isinstance(d[-1], dict) else {}).items()}
        getattr(mod, d[1])(*[tuple(a) if isinstance(a, list) else a for a in args], **kw)
    props.baseboard(mat(th["trim"]), hx, hy, 0.1, gaps=[(sd, c - w / 2, c + w / 2) for (sd, c, w, sill, head) in s.get("openings", []) if sill == 0])
    clues = []
    for c in s.get("clues", []):
        at, size = _clue_pos(c, boxes)
        if c.get("item"):
            _spawn_item(c["item"], at)
        out = {k: v for k, v in c.items() if k not in ("on", "at", "size", "item", "dz")}
        out["pos"], out["size"] = g(at), gs(size)
        clues.append(out)
    kit.export("ep_" + name)
    return clues


def convert(s):
    """Especificação (Blender) -> campos do JSON (Godot): luzes, partida, personagens, sons."""
    out = dict(s)
    out["lamps"] = [{"pos": g(l[:3]), "color": l[3], "energy": l[4], "range": l[5], "flicker": bool(l[6]) if len(l) > 6 else False}
                    for l in s.get("lamps", [])]
    st = s.get("start", [0, -1, 0])
    out["start"] = {"pos": [st[0], 0.05, -st[1]], "yaw": st[2]}
    out["size"] = [s["size"][0], s["size"][1], s["size"][2]]
    npcs = []
    for n in s.get("npcs", []):
        n = dict(n)
        n["pos"] = [n["at"][0], -n["at"][1]]
        n.pop("at", None)
        if "look" in n:
            n["look"] = [n["look"][0], -n["look"][1]]
        npcs.append(n)
    out["npcs"] = npcs
    out["models"] = [dict(m, pos=g(m["at"])) for m in s.get("models", [])]
    snd = dict(s.get("sound", {}))
    snd["emitters"] = [[e[0], g(e[1])] + list(e[2:]) for e in snd.get("emitters", [])]
    snd["life"] = [[e[0], e[1], e[2], e[3], g(e[4]), gs(e[5])] for e in snd.get("life", [])]
    out["sound"] = snd
    return out


def write_scene(name):
    with open(os.path.join(ROOT, "rooms", "ep_%s.tscn" % name), "w") as f:
        f.write('[gd_scene load_steps=2 format=3]\n\n[ext_resource type="Script" path="res://rooms/episodio.gd" id="1_ep"]\n\n'
                '[node name="%s" type="Node3D"]\nscript = ExtResource("1_ep")\ndata_path = "res://rooms/data/%s.json"\n' % (name.title().replace("_", ""), name))


def main():
    names = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    from ep import act2, act3, act4  # noqa: E402
    specs = {}
    for mod in (act2, act3, act4):
        specs.update(mod.SPECS)
    for name, s in specs.items():
        if names and name not in names:
            continue
        s = dict(s)
        s["name"] = name
        if s.get("kind", "room") == "room":
            clues = build_room(name, s)
            out = dict(convert(s), clues=clues, model="ep_" + name)
            for k in ("things", "decor", "openings"):
                out.pop(k, None)
        else:
            out = dict(s)
            out["clues"] = [dict({k: v for k, v in c.items() if k not in ("at", "size")}, pos=list(c["at"]), size=list(c.get("size", (0.5, 0.5, 0.5))))
                            for c in s.get("clues", [])]
        write_scene(name)
        with open(os.path.join(DATA, name + ".json"), "w") as f:
            json.dump(out, f, ensure_ascii=False, indent=1)
        print("EPISODIO", name, len(out["clues"]), "pistas")


if __name__ == "__main__":
    main()
