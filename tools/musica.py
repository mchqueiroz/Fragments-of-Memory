"""Sintetiza a trilha (numpy/scipy): post-punk e techno brutalista, melancólicos, de sabor russo (menor harmônica, coros, ferro e concreto).
Gera art/audio/mus_*.wav (estéreo 32 kHz, loop perfeito). Faixas:
  mus_tecno      techno brutalista, 124 bpm, ré menor: bumbo seco, baixo em semicolcheias, clanks industriais, arpejo triste
  mus_postpunk_a post-punk frio, 128 bpm, mi menor: baixo em colcheias, guitarra com chorus e eco, tons de bateria
  mus_postpunk_f post-punk quente/saudoso, 100 bpm, lá menor: mais suave, pads, memória
  mus_coro       drone com coro (vogais) e sinos, sem bateria: cemitério, quarto, clínica
Uso: python3 tools/musica.py [faixa ...]      (depois: godot --headless --import)"""
import os, sys, wave
import numpy as np
import scipy.signal as sg

SR = 32000
OUT = os.path.join(os.path.dirname(__file__), "..", "art", "audio")
rng = np.random.default_rng(1993)


def hz(m): return 440.0 * 2 ** ((m - 69) / 12.0)
def sos(kind, fc, order=2): return sg.butter(order, np.array(fc) / (SR / 2), kind, output="sos")
def lp(x, fc, o=2): return sg.sosfilt(sos("low", fc, o), x)
def hp(x, fc, o=2): return sg.sosfilt(sos("high", fc, o), x)
def bp(x, lo, hi, o=2): return sg.sosfilt(sos("band", [lo, hi], o), x)
def tt(n): return np.arange(n) / SR


def saw(f, n, vib=0.0, vr=5.0, ph0=0.0):
    t = tt(n)
    f = f * (1 + vib * np.sin(2 * np.pi * vr * t))
    return 2 * ((np.cumsum(f) / SR + ph0) % 1.0) - 1


def kick():
    t = tt(int(0.5 * SR))
    f = 42 + 110 * np.exp(-t * 32)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 6.5)
    x += hp(rng.standard_normal(len(t)), 2500) * np.exp(-t * 90) * 0.25          # clique do ataque
    return np.tanh(x * 1.8)


def clap():
    n = int(0.45 * SR)
    t = tt(n)
    x = bp(rng.standard_normal(n), 900, 3800)
    e = np.exp(-t * 14) + 0.7 * np.exp(-((t - 0.012) ** 2) * 1e5) + 0.5 * np.exp(-((t - 0.024) ** 2) * 1e5)
    return x * e * 0.8


def hat(open_=False):
    n = int((0.16 if open_ else 0.04) * SR)
    return hp(rng.standard_normal(n), 7500) * np.exp(-tt(n) * (22 if open_ else 110)) * 0.5


def tom(f0):
    t = tt(int(0.4 * SR))
    f = f0 * (1 + 0.6 * np.exp(-t * 18))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9) * 0.9


def clank(base):
    n = int(0.9 * SR)
    t = tt(n)
    x = sum(np.sin(2 * np.pi * base * r * t) * np.exp(-t * d) for r, d in [(1, 5), (2.76, 8), (5.4, 13), (8.93, 21)])
    return (x + bp(rng.standard_normal(n), 1500, 6000) * np.exp(-t * 40) * 0.6) * 0.35


def bass_note(m, dur, cut=420, drive=2.0):
    n = int(dur * SR)
    x = saw(hz(m), n) + 0.5 * saw(hz(m) * 1.004, n)
    x = lp(x, cut, 3) * np.minimum(1, tt(n) * 250) * np.exp(-tt(n) * 1.6)
    return np.tanh((x + 0.8 * np.sin(2 * np.pi * hz(m) * tt(n))) * drive) * 0.55


def pluck(m, dur=0.6, bright=2600):
    n = int(dur * SR)
    t = tt(n)
    x = saw(hz(m), n) + saw(hz(m) * 1.006, n) + saw(hz(m) * 0.994, n)
    return lp(x, bright, 2) * np.exp(-t * 4.5) * 0.3


def lead(m, dur=0.35):
    n = int(dur * SR)
    x = saw(hz(m), n, 0.004, 5.5) * 0.6 + np.sin(2 * np.pi * hz(m) * 2 * tt(n)) * 0.15
    return lp(x, 3000, 2) * np.minimum(1, tt(n) * 80) * np.exp(-tt(n) * 5) * 0.45


VOWELS = {"a": [(800, 1.0), (1150, 0.5), (2900, 0.2)], "o": [(450, 1.0), (800, 0.4), (2830, 0.15)], "u": [(325, 1.0), (700, 0.3), (2700, 0.1)]}


def choir(ms, dur, vowel="o", a=1.4, r=1.8):
    n = int((dur + r) * SR)
    t = tt(n)
    src = sum(saw(hz(m) * c, n, 0.006, 4.6 + 0.3 * i, ph0=rng.random()) for i, m in enumerate(ms) for c in (0.997, 1.003)) / len(ms)
    x = sum(bp(src, max(f - f * 0.12, 80), f + f * 0.12) * g for f, g in VOWELS[vowel])
    env = np.minimum(1, t / a) * np.minimum(1, np.maximum(0, (dur + r - t)) / r)
    return x * env * 0.5


def bell(m):
    n = int(2.8 * SR)
    t = tt(n)
    return sum(np.sin(2 * np.pi * hz(m) * r * t) * np.exp(-t * d) * g for r, d, g in [(1, 1.5, 1), (2.01, 2.4, 0.5), (2.76, 3.2, 0.35), (5.4, 5, 0.2)]) * 0.28


class Mix:
    def __init__(self, total):
        self.n = total
        self.bus = {}

    def put(self, name, start, x, gain=1.0, pan=0.0):
        b = self.bus.setdefault(name, np.zeros((2, self.n)))
        gl, gr = gain * np.cos((pan + 1) * np.pi / 4), gain * np.sin((pan + 1) * np.pi / 4)
        idx = (start + np.arange(len(x))) % self.n                      # dá a volta: o loop fecha sem emenda
        np.add.at(b[0], idx, x * gl)
        np.add.at(b[1], idx, x * gr)

    def reverb(self, name, wet, secs=2.2, tone=3500):
        b = self.bus[name]
        k = int(secs * SR)
        ir = lp(rng.standard_normal(k), tone) * np.exp(-tt(k) * 2.6)
        ir[: int(0.02 * SR)] *= np.linspace(0, 1, int(0.02 * SR))
        ir /= np.sqrt((ir ** 2).sum())
        out = np.zeros_like(b)
        for c in range(2):
            ir_c = np.roll(ir, c * 37)
            y = sg.fftconvolve(np.concatenate([b[c], b[c][:k]]), ir_c)[: self.n + k]
            out[c] = y[: self.n]
            out[c][:k] += y[self.n: self.n + k][:k] if len(y) >= self.n + k else 0
        self.bus[name] = b * (1 - wet) + out * wet

    def echo(self, name, delay_s, fb=0.45, taps=5, tone=2500):
        b = self.bus[name]
        out = b.copy()
        for k in range(1, taps + 1):
            sh = int(delay_s * SR * k)
            out[0] += np.roll(lp(b[1], tone), sh) * fb ** k                 # ping-pong
            out[1] += np.roll(lp(b[0], tone), sh) * fb ** k
        self.bus[name] = out


def finish(m, name, drive=1.15):
    mix = sum(m.bus.values())
    mix = np.tanh(mix * drive)
    mix = hp(mix, 28, 2)
    mix /= max(np.abs(mix).max(), 1e-6) / 0.89
    pcm = (mix.T * 32767).astype("<i2")
    with wave.open(os.path.join(OUT, name + ".wav"), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print(name, round(m.n / SR, 1), "s")


def sidechain(m, kick_times, depth=0.55, rel=0.22):
    env = np.ones(m.n)
    t = tt(int(rel * SR))
    shape = 1 - depth * np.exp(-t * 9)
    for s in kick_times:
        idx = (s + np.arange(len(t))) % m.n
        env[idx] = np.minimum(env[idx], shape)
    return env


# ---- as faixas -----------------------------------------------------------------------------------------------------------------------

def tecno():
    bpm, bars = 124, 32
    sps = int(round(60 / bpm / 4 * SR))                      # amostras por semicolcheia
    m = Mix(bars * 16 * sps)
    prog = [("Dm", 38, [50, 53, 57]), ("Dm", 38, [50, 53, 57]), ("Bb", 34, [46, 50, 53]), ("Bb", 34, [46, 50, 53]),
            ("Gm", 31, [43, 46, 50]), ("Gm", 31, [43, 46, 50]), ("A", 33, [45, 49, 52]), ("A", 33, [45, 49, 52])]
    mel = {"Dm": [69, 74, 77, 76], "Bb": [65, 70, 74, 72], "Gm": [74, 70, 67, 69], "A": [73, 76, 81, 79]}
    K, C, Hc, Cl = kick(), clap(), hat(), clank(210)
    kt = []
    for bar in range(bars):
        sec = bar // 8                                            # 0 abertura, 1 groove, 2 melodia, 3 queda
        name, root, chord = prog[bar % 8]
        b0 = bar * 16 * sps
        for beat in range(4):
            s = b0 + beat * 4 * sps
            m.put("drums", s, K, 0.7)
            kt.append(s)
        if sec >= 1:
            for e in range(8):
                m.put("drums", b0 + (e * 2 + 1) * sps * 1, hat(e % 4 == 3), 0.5, 0.35 if e % 2 else -0.35) if False else None
            for e in range(4):
                m.put("drums", b0 + (e * 4 + 2) * sps, hat(e == 3), 0.55, 0.3)
            for q in range(16):
                if q % 2 == 1:
                    m.put("drums", b0 + q * sps, hat(), 0.18, -0.3 if q % 4 == 1 else 0.3)
        if sec in (2,):
            m.put("drums", b0 + 4 * sps, C, 0.55, 0.0)
            m.put("drums", b0 + 12 * sps, C, 0.55, 0.0)
        if sec == 0 and bar % 2 == 1:
            m.put("metal", b0 + 10 * sps, Cl, 0.6, rng.uniform(-0.7, 0.7))
        if sec >= 1:
            pat = [1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0]
            for q, on in enumerate(pat):
                if on:
                    note = root + (12 if q in (6, 14) else 0) + (3 if (bar % 8 == 7 and q in (10, 11)) else 0)
                    m.put("bass", b0 + q * sps, bass_note(note, 0.2, 380 + 220 * (sec == 3)), 0.7, 0.0)
        elif bar % 2 == 0:
            m.put("bass", b0, bass_note(root, 4 * 4 * sps / SR, 260), 0.8, 0.0)
        if bar % 2 == 0:
            m.put("pad", b0, choir(chord, 2 * 16 * sps / SR - 1.0, "o"), 1.0 if sec != 1 else 0.6, rng.uniform(-0.4, 0.4))
        if sec == 2:
            for q in range(8):
                m.put("lead", b0 + q * 2 * sps, lead(mel[name][q % 4] - (12 if q >= 4 else 0)), 0.9, 0.2 if q % 2 else -0.2)
        if sec >= 1 and sec != 3:
            for q in (0, 6, 11):
                m.put("lead", b0 + q * sps, pluck(chord[q % 3] + 24, 0.5, 3200), 0.7, 0.5)
    sc = sidechain(m, kt)
    for k in ("bass", "pad", "lead"):
        if k in m.bus:
            m.bus[k] = m.bus[k] * sc
    m.reverb("pad", 0.55, 3.0)
    m.reverb("lead", 0.35, 2.0)
    m.echo("lead", 3 * sps / SR, 0.4)
    m.reverb("metal", 0.5, 1.6)
    if "drums" in m.bus:
        m.reverb("drums", 0.08, 0.9)
    finish(m, "mus_tecno", 1.25)


def postpunk(name, bpm, bars, prog, key_lead, bright, drive, warm):
    sps = int(round(60 / bpm / 4 * SR))
    m = Mix(bars * 16 * sps)
    K, S, Hc = kick(), clap(), hat()
    toms = [tom(f) for f in (95, 120, 150)]
    kt = []
    for bar in range(bars):
        chord_i = (bar // 2) % len(prog)
        root, chord, melo = prog[chord_i]
        b0 = bar * 16 * sps
        sec = bar // 8
        for s16 in (0, 10) if not warm else (0, 8):
            m.put("drums", b0 + s16 * sps, K, 0.8 if not warm else 0.6)
            kt.append(b0 + s16 * sps)
        for s16 in (4, 12):
            m.put("drums", b0 + s16 * sps, S if not warm else hat(True), 0.55, 0.1)
        if not warm or sec >= 1:
            for e in range(8):
                m.put("drums", b0 + e * 2 * sps, hat(), 0.4 if e % 2 else 0.28, 0.3)
        if bar % 4 == 3:                                                    # virada de toms
            for i, q in enumerate((12, 13, 14, 15)):
                m.put("drums", b0 + q * sps, toms[i % 3], 0.7, -0.4 + 0.25 * i)
        for e in range(8):                                                  # baixo em colcheias, pegada de Hook
            note = root + (12 if e in (3, 7) else 0) + (-2 if (e == 5 and bar % 4 == 3) else 0)
            m.put("bass", b0 + e * 2 * sps, bass_note(note, 0.3, 700 if not warm else 480, 2.4), 0.8)
        for e in range(8):                                                  # guitarra: arpejo com chorus e eco
            m.put("gtr", b0 + e * 2 * sps, pluck(chord[(e * 2 if e % 2 == 0 else e) % 3] + 12 + (12 if e % 4 == 3 else 0), 0.5, bright), 1.1, -0.3 + 0.08 * e)
        if bar % 2 == 0:
            m.put("pad", b0, choir(chord, 2 * 16 * sps / SR - 0.8, "a" if not warm else "o"), 0.45 if not warm else 0.7, rng.uniform(-0.4, 0.4))
        if sec >= 1 and bar % 2 == 1:                                       # frase melancólica de guitarra solo
            for i, mm in enumerate(melo):
                m.put("lead", b0 + (i * 4) * sps, lead(mm + key_lead, 0.6), 0.9, 0.45)
    sc = sidechain(m, kt, 0.3)
    m.bus["pad"] = m.bus["pad"] * sc
    m.echo("gtr", 3 * sps / SR, 0.42)
    m.echo("lead", 6 * sps / SR, 0.45)
    m.reverb("gtr", 0.3, 1.8)
    m.reverb("pad", 0.5, 3.0)
    m.reverb("lead", 0.4, 2.4)
    m.reverb("drums", 0.14 if not warm else 0.25, 1.1)
    finish(m, name, drive)


def coro():
    bars, bpm = 16, 60                                                        # 16 compassos de 4 s = 64 s
    sps = int(round(60 / bpm / 4 * SR))
    m = Mix(bars * 16 * sps)
    chords = [([38, 45, 50, 53], "o"), ([34, 41, 46, 50], "u"), ([31, 38, 43, 46], "o"), ([33, 40, 45, 49], "a")]
    for i, (ch, v) in enumerate(chords):
        s = i * 4 * 16 * sps
        m.put("pad", s, choir(ch + [ch[1] + 12, ch[2] + 12], 4 * 16 * sps / SR - 1.5, v, 3.0, 3.0), 1.6, 0.0)
    m.put("sub", 0, np.sin(2 * np.pi * hz(26) * tt(m.n)) * (0.5 + 0.2 * np.sin(2 * np.pi * tt(m.n) * (1 / 64.0 * 2))), 0.05)
    for i, (when, note) in enumerate([(5, 74), (19, 81), (31, 77), (44, 69), (55, 76)]):
        m.put("bell", int(when * SR), bell(note), 0.9, rng.uniform(-0.6, 0.6))
    m.put("metal", int(26 * SR), clank(130), 0.35, 0.4)
    m.reverb("pad", 0.6, 4.5, 2500)
    m.reverb("bell", 0.65, 3.5)
    m.reverb("metal", 0.7, 3.0)
    finish(m, "mus_coro", 1.0)


def main():
    which = sys.argv[1:] or ["tecno", "pa", "pf", "coro"]
    if "tecno" in which:
        tecno()
    if "pa" in which:      # mi menor, frio: Em | C | D | Bm (baixos em 40/36/38/35)
        postpunk("mus_postpunk_a", 128, 32,
                 [(40, [52, 55, 59], [71, 67, 64, 66]), (36, [48, 52, 55], [64, 67, 72, 71]), (38, [50, 54, 57], [66, 69, 74, 73]), (35, [47, 50, 54], [66, 62, 59, 62])],
                 0, 3000, 1.2, False)
    if "pf" in which:      # lá menor, quente: Am | F | C | G
        postpunk("mus_postpunk_f", 100, 32,
                 [(45, [57, 60, 64], [76, 72, 69, 72]), (41, [53, 57, 60], [77, 72, 69, 65]), (48, [48, 52, 55], [79, 76, 72, 76]), (43, [55, 59, 62], [74, 71, 67, 71])],
                 0, 2200, 1.1, True)
    if "coro" in which:
        coro()


main()
