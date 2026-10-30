"""Auditoria de posições: acusa objetos flutuando, enterrados ou atravessando outros, ao exportar cada cômodo.
Liga com a variável de ambiente AUDIT=<pasta>; o relatório sai em <pasta>/<modelo>.json e um resumo no terminal.

Cada chamada de props.* / furniture.* (ou peça solta do cômodo) vira um "objeto". Os testes usam a planta real de
cada peça (polígono convexo em XY + faixa em Z), não caixas alinhadas, para móveis girados não darem alarme falso.
"""
import json
import os
import sys

MODS = ("props.py", "furniture.py")
TOL = 0.025          # folga de contato (m)


class Audit:
    def __init__(self, out):
        self.out = out
        self.pairs = True        # False: só flutua/fura (primitivas soltas do Godot não dizem o que é um mesmo objeto)
        self.reset()
        sys.setprofile(self._prof)

    def reset(self):
        self.prims = []      # [grupo, pontos]
        self.groups = {}     # grupo -> rótulo
        self._depth = 0
        self._gid = 0
        self._cur = None

    def _prof(self, frame, event, arg):
        f = frame.f_code.co_filename
        if not f.endswith(MODS):
            return
        if event == "call":
            if self._depth == 0:
                self._gid += 1
                self._cur = "g%d" % self._gid
                a = frame.f_locals
                args = ", ".join("%s=%s" % (k, _short(a[k])) for k in frame.f_code.co_varnames[:frame.f_code.co_argcount] if k in a)
                self.groups[self._cur] = "%s.%s(%s)" % (os.path.basename(f)[:-3], frame.f_code.co_name, args)
            self._depth += 1
        elif event == "return":
            self._depth -= 1
            if self._depth == 0:
                self._cur = None

    def prim(self):
        if self._cur:
            key = self._cur
        else:                                                                  # peça solta: rótulo = linha do script que a criou
            self._gid += 1
            key = "p%d" % self._gid
            fr = sys._getframe(2)
            while fr and os.path.basename(fr.f_code.co_filename) == "kit.py":
                fr = fr.f_back
            self.groups[key] = "%s:%d" % (os.path.basename(fr.f_code.co_filename), fr.f_lineno) if fr else "?"
        self.prims.append([key, []])

    def quad(self, pts):
        if self.prims:
            self.prims[-1][1].extend(pts)

    # ---- análise ---------------------------------------------------------------------------------------------------
    def report(self, name):
        self._extra(name)
        P = []
        for key, pts in self.prims:
            if len(pts) < 3:
                continue
            xs, ys, zs = [p[0] for p in pts], [p[1] for p in pts], [p[2] for p in pts]
            P.append({"g": key, "poly": _hull([(p[0], p[1]) for p in pts]), "z0": min(zs), "z1": max(zs),
                      "x0": min(xs), "x1": max(xs), "y0": min(ys), "y1": max(ys)})
        for p in P:
            p["area"] = _area(p["poly"])
            p["big"] = (max(p["x1"] - p["x0"], p["y1"] - p["y0"]) > 2.6 or p["z1"] - p["z0"] > 2.6     # piso, teto, paredes
                        or (min(p["x1"] - p["x0"], p["y1"] - p["y0"]) <= 0.25 and p["z1"] - p["z0"] >= 2.0)  # trecho de parede
                        or self.groups[p["g"]].startswith("episodios.py"))                         # casca gerada do cômodo
        items = {}
        for p in P:
            items.setdefault(p["g"], []).append(p)
        floor = [p for p in P if p["big"] and p["z1"] < 0.05 and p["z0"] > -0.5]
        fx0, fx1 = (min(p["x0"] for p in floor), max(p["x1"] for p in floor)) if floor else (-1e9, 1e9)
        fy0, fy1 = (min(p["y0"] for p in floor), max(p["y1"] for p in floor)) if floor else (-1e9, 1e9)
        farea = (fx1 - fx0) * (fy1 - fy0) if floor else 0
        ceil = max((p["z0"] for p in P if p["big"] and p["z1"] - p["z0"] < 0.5 and p["z0"] > 1.0 and p["area"] > 0.5 * farea),
                   default=1e9)                                                                  # laje que cobre o cômodo (exterior: nenhuma)
        issues = []
        for g, ps in items.items():
            if any(p["big"] for p in ps):
                continue
            cx, cy = _where(ps)[:2]
            if not (fx0 <= cx <= fx1 and fy0 <= cy <= fy1):                     # paisagem do lado de fora da janela
                continue
            if floor and (min(p["z0"] for p in ps) < -0.03 or max(p["z1"] for p in ps) > ceil + 0.03):
                issues.append({"tipo": "fura", "obj": self.groups[g], "z": [round(min(p["z0"] for p in ps), 2),
                               round(max(p["z1"] for p in ps), 2)], "onde": _where(ps)})
                continue
            z0 = min(p["z0"] for p in ps)
            if z0 > TOL and not self._supported(g, ps, z0, P):
                issues.append({"tipo": "flutua", "obj": self.groups[g], "z": round(z0, 3), "onde": _where(ps)})
        seen = set()
        for i, a in enumerate(P if self.pairs else []):
            for b in P[i + 1:]:
                if a["g"] == b["g"] or (a["big"] and b["big"]):
                    continue
                if not (a["g"].startswith("g") or b["g"].startswith("g")):              # peças soltas do mesmo cômodo: modelagem
                    continue
                dz = min(a["z1"], b["z1"]) - max(a["z0"], b["z0"])
                if dz <= TOL or a["x1"] <= b["x0"] or b["x1"] <= a["x0"] or a["y1"] <= b["y0"] or b["y1"] <= a["y0"]:
                    continue
                inter = _area(_clip(a["poly"], b["poly"]))
                small = min(a["area"], b["area"]) or 1e-9
                if inter < 0.0015 or inter / small < 0.2:
                    continue
                pen = min(_pen(a["poly"], b["poly"]), dz)
                if pen < (0.06 if (a["big"] or b["big"]) else 0.02):                   # encostado/embutido na parede não aparece
                    continue
                pair = tuple(sorted((a["g"], b["g"])))
                if pair in seen:
                    continue
                seen.add(pair)
                issues.append({"tipo": "atravessa", "obj": self.groups[a["g"]], "com": self.groups[b["g"]],
                               "prof": round(pen, 3), "area": round(inter, 4), "onde": _where([a, b])})
        os.makedirs(self.out, exist_ok=True)
        with open(os.path.join(self.out, name + ".json"), "w") as f:
            json.dump(issues, f, ensure_ascii=False, indent=1)
        print("AUDITORIA %s: %d flutua, %d atravessa, %d fura" % (name, sum(i["tipo"] == "flutua" for i in issues),
                                                                  sum(i["tipo"] == "atravessa" for i in issues), sum(i["tipo"] == "fura" for i in issues)))
        self.reset()

    def _extra(self, name):
        """Personagens e modelos avulsos posicionados no Godot (AUDIT_EXTRA, gerado por tools/teste_posicoes.gd)."""
        path = os.environ.get("AUDIT_EXTRA", "")
        if not path or not os.path.exists(path):
            return
        e = json.load(open(path)).get(name, {})
        import math
        for x, y, z, who, pose in e.get("npcs", []):
            self._gid += 1
            key = "gnpc%d" % self._gid
            self.groups[key] = "personagem %s%s" % (who, " (%s)" % pose if pose else "")
            r, z0, z1 = (0.15, z + 0.48, z + 1.35) if pose else (0.2, z, z + 1.7)    # sentado: quadril no assento, pernas sob a mesa
            ring = [(x + r * math.cos(a * math.pi / 4), y + r * math.sin(a * math.pi / 4)) for a in range(8)]
            self.prims.append([key, [(px, py, z0) for px, py in ring] + [(px, py, z1) for px, py in ring]])
        for x0, y0, z0, x1, y1, z1, f in e.get("models", []):
            self._gid += 1
            key = "gmod%d" % self._gid
            self.groups[key] = "modelo %s" % f
            self.prims.append([key, [(px, py, pz) for px in (x0, x1) for py in (y0, y1) for pz in (z0, z1)]])

    def _supported(self, g, ps, z0, P):
        top = max(p["z1"] for p in ps)
        for q in P:                                                                   # pendurado: fio/haste entra pelo topo
            if q["g"] != g and q["z0"] <= top + TOL and q["z1"] > top - TOL and any(
                    _area(_clip(p["poly"], q["poly"])) > 0 for p in ps if p["z1"] > top - 0.05):
                return True
        base = [p for p in ps if p["z0"] < z0 + 0.01]
        for p in base:
            got = 0.0                                                                 # soma das pernas/apoios
            for q in P:
                if q["g"] == g:
                    continue
                if q["z0"] - TOL <= p["z0"] <= q["z1"] + TOL:                          # apoiado em cima ou encaixado
                    got += _area(_clip(p["poly"], q["poly"]))
                    if got >= min(p["area"] * 0.15, 0.0008):
                        return True
                if q["big"] and q["z1"] - q["z0"] > 1.0 and _gap(p, q) < 0.04:       # preso na parede
                    return True
                if (q["z0"] - TOL <= p["z0"] and p["z1"] <= q["z1"] + TOL and _gap(p, q) < 0.012
                        and min(p["x1"], q["x1"]) - max(p["x0"], q["x0"]) > -0.012
                        and min(p["y1"], q["y1"]) - max(p["y0"], q["y0"]) > -0.012):       # preso na face de um móvel
                    return True
        return False


def _short(v):
    if isinstance(v, float):
        return "%.2f" % v
    if isinstance(v, (tuple, list)) and len(v) <= 4 and all(isinstance(x, (int, float)) for x in v):
        return "(" + ",".join("%.2f" % x for x in v) + ")"
    s = repr(v)
    return s if len(s) < 24 else s[:20] + "…"


def _where(ps):
    return [round(sum(p["x0"] + p["x1"] for p in ps) / (2 * len(ps)), 2), round(sum(p["y0"] + p["y1"] for p in ps) / (2 * len(ps)), 2),
            round(min(p["z0"] for p in ps), 2)]


def _pen(a, b):
    """Penetração horizontal (SAT): menor sobreposição das projeções nos eixos das arestas dos dois polígonos."""
    best = 1e9
    for poly in (a, b):
        for i in range(len(poly)):
            ex, ey = poly[i][0] - poly[i - 1][0], poly[i][1] - poly[i - 1][1]
            n = (ey ** 2 + ex ** 2) ** 0.5
            if n < 1e-9:
                continue
            ax, ay = -ey / n, ex / n
            pa = [x * ax + y * ay for x, y in a]
            pb = [x * ax + y * ay for x, y in b]
            best = min(best, min(max(pa), max(pb)) - max(min(pa), min(pb)))
    return max(best, 0.0)


def _gap(a, b):
    dx = max(b["x0"] - a["x1"], a["x0"] - b["x1"], 0)
    dy = max(b["y0"] - a["y1"], a["y0"] - b["y1"], 0)
    return max(dx, dy)


def _hull(pts):
    pts = sorted(set((round(x, 4), round(y, 4)) for x, y in pts))
    if len(pts) < 3:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lo, hi = [], []
    for p in pts:
        while len(lo) >= 2 and cross(lo[-2], lo[-1], p) <= 0:
            lo.pop()
        lo.append(p)
    for p in reversed(pts):
        while len(hi) >= 2 and cross(hi[-2], hi[-1], p) <= 0:
            hi.pop()
        hi.append(p)
    return lo[:-1] + hi[:-1]


def _area(poly):
    if len(poly) < 3:
        return 0.0
    return abs(sum(poly[i][0] * poly[i - 1][1] - poly[i - 1][0] * poly[i][1] for i in range(len(poly)))) / 2


def _clip(subj, clip):
    """Sutherland–Hodgman: interseção de dois polígonos convexos (anti-horários)."""
    out = subj
    for i in range(len(clip)):
        if not out:
            break
        a, b = clip[i - 1], clip[i]
        inp, out = out, []

        def inside(p):
            return (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0]) >= -1e-9

        def cut(p, q):
            x1, y1, x2, y2 = p[0], p[1], q[0], q[1]
            x3, y3, x4, y4 = a[0], a[1], b[0], b[1]
            d = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
            if abs(d) < 1e-12:
                return q
            t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / d
            return (x1 + t * (x2 - x1), y1 + t * (y2 - y1))
        for j in range(len(inp)):
            p, q = inp[j - 1], inp[j]
            if inside(q):
                if not inside(p):
                    out.append(cut(p, q))
                out.append(q)
            elif inside(p):
                out.append(cut(p, q))
    return out


if __name__ == "__main__":                                                     # autoteste rápido (python3 tools/auditoria.py)
    sq = _hull([(0, 0), (1, 0), (1, 1), (0, 1)])
    assert abs(_area(sq) - 1) < 1e-9
    assert abs(_area(_clip(sq, _hull([(0.5, 0.5), (1.5, 0.5), (1.5, 1.5), (0.5, 1.5)]))) - 0.25) < 1e-9
    assert _area(_clip(sq, _hull([(2, 2), (3, 2), (3, 3), (2, 3)]))) == 0
    assert abs(_pen(sq, _hull([(0.9, 0), (2, 0), (2, 1), (0.9, 1)])) - 0.1) < 1e-9
    print("ok")
