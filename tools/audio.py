"""Sintetiza o áudio do jogo (numpy) em art/audio/*.wav — mono, 16 bits, 22,05 kHz (lo-fi proposital).

Uso: python3 tools/audio.py
Ambientação russa de 1993:
  * tema de Sergei: modo dórico em ré, bayan (acordeão de palhetas desafinadas), balalaica em trêmolo,
    coro grave de baixos em quintas paralelas, sino de Moscou; o motivo é G-D-E-D = 4-8-2-1;
  * rádio: locutor sem idioma com fonética eslava (ш, щ, ж, ч, р rolado, grupos тр/ст/вз), AM, pips de hora certa;
  * ambiente: vento de inverno, cano de aquecimento batendo, sino distante, rangidos do prédio.
Técnicas de som de cinema: toda fonte tem objeto visível; o mundo "esquece" junto com a imagem.
"""
import os
import sys
import wave

import numpy as np

SR = 22050
OUT = os.path.join(os.path.dirname(__file__), "..", "art", "audio")
os.makedirs(OUT, exist_ok=True)
RNG = np.random.default_rng(1993)


def t(secs):
    return np.arange(int(secs * SR)) / SR


def noise(secs, seed=None):
    r = RNG if seed is None else np.random.default_rng(seed)
    return r.standard_normal(int(secs * SR))


def band(x, lo=None, hi=None, order=2):
    """Filtro passa-faixa no domínio da frequência (circular, portanto seguro para loops)."""
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    g = np.ones_like(f)
    if lo:
        g *= 1 / (1 + (lo / np.maximum(f, 1e-3)) ** (2 * order))
    if hi:
        g *= 1 / (1 + (f / hi) ** (2 * order))
    return np.fft.irfft(X * g, len(x))


def reverb(x, secs=1.8, wet=0.35, seed=7, circular=True):
    """Reverb por convolução com ruído de decaimento exponencial (circular para manter o loop)."""
    n = len(x)
    ir_t = np.arange(int(secs * SR)) / SR
    ir = np.random.default_rng(seed).standard_normal(len(ir_t)) * np.exp(-ir_t * (6.9 / secs))
    ir = band(ir, lo=120, hi=5500)
    if circular:
        irp = np.zeros(n)
        irp[:min(n, len(ir))] = ir[:n]
        y = np.fft.irfft(np.fft.rfft(x) * np.fft.rfft(irp), n)
    else:
        size = 1 << int(np.ceil(np.log2(n + len(ir))))
        y = np.fft.irfft(np.fft.rfft(x, size) * np.fft.rfft(ir, size), size)[:n + len(ir)]
        x = np.pad(x, (0, len(y) - n))
    y = y / (np.max(np.abs(y)) + 1e-9) * (np.max(np.abs(x)) + 1e-9)
    return x * (1 - wet) + y * wet


def env_ad(n, attack=0.005, decay=0.1):
    tt = np.arange(n) / SR
    return np.minimum(tt / max(attack, 1e-4), 1.0) * np.exp(-tt / decay)


def save(name, x, peak=0.85):
    x = x / (np.max(np.abs(x)) + 1e-9) * peak
    with wave.open(os.path.join(OUT, name + ".wav"), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())


def put(x, s, at):
    """Soma o som `s` em `x` a partir de `at` segundos (cortando o excesso)."""
    i = int(at * SR)
    if 0 <= i < len(x):
        m = min(len(s), len(x) - i)
        x[i:i + m] += s[:m]


# --------------------------------------------------------------------------------------------
# Instrumentos russos
# --------------------------------------------------------------------------------------------
def bell(freq, dur, vel=1.0):
    """Sino de igreja: parciais inarmônicos com decaimentos diferentes."""
    k = t(dur)
    parts = ((0.5, 0.6, 1.0), (1.0, 1.0, 0.8), (1.19, 0.7, 0.6), (1.5, 0.5, 0.5), (2.0, 0.6, 0.4),
             (2.51, 0.4, 0.3), (3.0, 0.3, 0.25), (4.07, 0.25, 0.2))
    s = sum(a * np.sin(2 * np.pi * freq * r * k) * np.exp(-k / (dur * d / 3.5)) for r, a, d in parts)
    return s * np.minimum(k / 0.003, 1) * vel


def bayan(freq, dur, vel=1.0):
    """Acordeão de botões: duas palhetas levemente desafinadas (musette) e trêmolo lento."""
    k = t(dur)
    s = np.zeros(len(k))
    for det in (1.0, 1.006):
        for h in range(1, 14):
            s += np.sin(2 * np.pi * freq * det * h * k + h) / h ** 0.9
    trem = 1 + 0.07 * np.sin(2 * np.pi * 5.2 * k)
    env = np.minimum(k / 0.12, 1) * np.clip((dur - k) / 0.3, 0, 1) * (0.85 + 0.15 * np.exp(-k / 0.3))
    return s * trem * env * vel * 0.5


def balalaika(freq, dur, vel=1.0, rate=13.0):
    """Balalaica: palhetada repetida rápida (trêmolo), cada palhetada com harmônicos que decaem."""
    pk = np.arange(int(0.28 * SR)) / SR
    pl = sum(np.sin(2 * np.pi * freq * h * pk) / h ** 1.1 * np.exp(-pk * (10 + 4 * h)) for h in range(1, 9))
    n = int(dur * SR)
    s = np.zeros(n)
    step = int(SR / rate)
    for i, pos in enumerate(range(0, n, step)):
        m = min(len(pl), n - pos)
        s[pos:pos + m] += pl[:m] * (1.0 if i % 2 == 0 else 0.78)
    return s * np.clip((dur - t(dur)) / 0.25, 0, 1) * vel


def choir(freq, dur, vel=1.0):
    """Coro de baixos (estilo basso profundo): vogal "o", quinta paralela, ataque lento."""
    k = t(dur)
    s = np.zeros(len(k))
    vib = 1 + 0.004 * np.sin(2 * np.pi * 5.0 * k)
    for f in (freq, freq * 1.5):
        ph = np.cumsum(f * vib) / SR
        for h in range(1, 26):
            fh = f * h
            a = np.exp(-((fh - 450) / 160) ** 2) + 0.5 * np.exp(-((fh - 800) / 220) ** 2) + 0.12 * np.exp(-((fh - 2600) / 500) ** 2)
            s += a * np.sin(2 * np.pi * h * ph)
    env = np.minimum(k / 1.2, 1) * np.clip((dur - k) / 1.6, 0, 1)
    return s * env * vel * 0.07


# --------------------------------------------------------------------------------------------
# Ambiente
# --------------------------------------------------------------------------------------------
def amb_room():
    secs = 24.0
    tt = t(secs)
    rumble = band(noise(secs, 11), 35, 500)
    hum = np.sin(2 * np.pi * 50 * tt) * 0.12 + np.sin(2 * np.pi * 100 * tt) * 0.06
    air = band(noise(secs, 12), 1800, 6500) * 0.04 * (0.6 + 0.4 * np.sin(2 * np.pi * tt / secs * 3))
    # vento de inverno batendo na janela: onda grave + assobio que muda de altura
    wind = band(noise(secs, 13), 100, 900) * (0.45 + 0.55 * np.sin(2 * np.pi * tt / secs * 2 + 1.0) ** 2) * 0.55
    whistle = band(noise(secs, 14), 650, 1050) * (0.3 + 0.7 * np.sin(2 * np.pi * tt / secs * 3) ** 2) * 0.18
    x = rumble * 0.45 + hum + air + wind + whistle
    for at in (4.1, 19.3):  # rangidos da madeira do prédio
        n = int(0.55 * SR)
        k = np.arange(n) / SR
        creak = np.sin(2 * np.pi * np.cumsum(420 - 160 * k / 0.55) / SR) * env_ad(n, 0.04, 0.22) * (0.7 + 0.3 * np.sin(2 * np.pi * 31 * k))
        put(x, creak * 0.08, at)
    for at in (7.7, 15.2):  # cano de aquecimento batendo (dilatação do metal)
        n = int(0.7 * SR)
        k = np.arange(n) / SR
        knock = sum(np.sin(2 * np.pi * f * (1 - 0.15 * k) * k) * a for f, a in ((138, 1.0), (373, 0.5), (718, 0.3), (1190, 0.15)))
        put(x, knock * np.exp(-k / 0.16) * np.minimum(k / 0.002, 1) * 0.16, at)
    far = bell(196.0, 6.0, 1.0)  # sino distante de uma igreja de Moscou, abafado e com eco
    far = band(np.pad(far, (0, 0)), lo=80, hi=1900)
    put(x, far * 0.1, 10.4)
    save("amb_room", x, 0.6)


def tinnitus():
    tt = t(6.0)
    x = (np.sin(2 * np.pi * 5200 * tt) * 0.5 + np.sin(2 * np.pi * 6100 * tt) * 0.25
         + np.sin(2 * np.pi * 3900 * tt) * 0.1) * (0.82 + 0.18 * np.sin(2 * np.pi * tt / 6.0 * 2))
    save("tinnitus", x, 0.5)


def heartbeat():
    secs = 1.2
    x = np.zeros(int(secs * SR))
    for at, amp in ((0.0, 1.0), (0.26, 0.7)):
        n = int(0.22 * SR)
        k = np.arange(n) / SR
        put(x, np.sin(2 * np.pi * (58 - 18 * k / 0.22) * k) * env_ad(n, 0.004, 0.07) * amp, at)
    save("heartbeat", x, 0.9)


# --------------------------------------------------------------------------------------------
# Passos, relógio, objetos
# --------------------------------------------------------------------------------------------
def steps():
    for i in range(4):
        n = int(0.30 * SR)
        r = np.random.default_rng(100 + i)
        thump = np.sin(2 * np.pi * (85 + 8 * i) * np.arange(n) / SR) * env_ad(n, 0.003, 0.05)
        click = band(r.standard_normal(n), 300, 2600) * env_ad(n, 0.002, 0.035)
        creak = np.zeros(n)
        if i % 2 == 1:
            k = np.arange(n) / SR
            creak = np.sin(2 * np.pi * np.cumsum(380 + 220 * k) / SR) * env_ad(n, 0.05, 0.09) * 0.25
        save(f"step_parquet_{i}", thump * 0.9 + click * 0.9 + creak, 0.8)


def steps_floors():
    """Passos de concreto (duro, com eco) e de linóleo (surdo, com rangido de borracha)."""
    for i in range(4):
        n = int(0.5 * SR)
        r = np.random.default_rng(200 + i)
        thump = np.sin(2 * np.pi * (70 + 6 * i) * np.arange(n) / SR) * env_ad(n, 0.002, 0.04)
        click = band(r.standard_normal(n), 700, 5200) * env_ad(n, 0.001, 0.025)
        x = reverb(thump * 0.7 + click * 1.1, 0.7, 0.3, seed=300 + i, circular=False)[:n]
        save(f"step_concrete_{i}", x, 0.8)
        r = np.random.default_rng(250 + i)
        n = int(0.3 * SR)
        thump = np.sin(2 * np.pi * (105 + 7 * i) * np.arange(n) / SR) * env_ad(n, 0.004, 0.05)
        click = band(r.standard_normal(n), 200, 1700) * env_ad(n, 0.003, 0.04)
        sq = np.zeros(n)
        if i % 2 == 0:
            k = np.arange(n) / SR
            sq = np.sin(2 * np.pi * np.cumsum(1900 + 500 * k * 3) / SR) * env_ad(n, 0.01, 0.025) * 0.18
        save(f"step_lino_{i}", thump * 0.9 + click * 0.8 + sq, 0.75)


def swan_lake():
    """Tema do cisne em estilo de TV velha (loop de 16 s): oboé, harpa e cordas, tom de si menor; passa por um alto-falante pequeno.
    Composição de Tchaikovsky (domínio público), sintetizada aqui: não é gravação de ninguém."""
    secs = 16.0
    x = np.zeros(int(secs * SR))
    hz = lambda m: 440.0 * 2 ** ((m - 69) / 12)
    # (nota MIDI, início em s, duração em s): frase ascendente, pausa, resposta descendente
    mel = ((78, 0.0, 2.4), (74, 2.5, 0.9), (76, 3.5, 0.9), (78, 4.5, 0.9), (79, 5.5, 1.7), (78, 7.3, 0.9),
           (76, 8.3, 0.9), (74, 9.3, 1.1), (73, 10.5, 1.1), (71, 11.7, 1.1), (73, 12.9, 1.0), (71, 14.0, 1.9))
    for m, at, dur in mel:
        k = t(dur)
        f0 = hz(m)
        vib = 1 + 0.01 * np.sin(2 * np.pi * 5.2 * k) * np.minimum(k / 0.4, 1)
        tone = sum(np.sin(2 * np.pi * np.cumsum(f0 * h * vib) / SR) / h for h in (1, 2, 3, 4)) * 0.4   # timbre anasalado de oboé
        env = np.minimum(k / 0.08, 1) * np.clip((dur - k) / 0.15, 0, 1)
        put(x, tone * env, at)
    for bar in range(8):                       # harpa: arpejo de si menor sob a melodia
        for j, m in enumerate((47, 54, 59, 62, 59, 54)):
            f0 = hz(m)
            k = t(0.9)
            put(x, np.sin(2 * np.pi * f0 * k) * np.exp(-k / 0.35) * 0.35, bar * 2.0 + j * 0.3)
    k = t(secs)
    pad = (np.sin(2 * np.pi * hz(47) * k) + 0.6 * np.sin(2 * np.pi * hz(54) * k)) * 0.12 * (0.7 + 0.3 * np.sin(2 * np.pi * k / 8))
    x = band(x + pad, 280, 4200) + noise(secs, 91) * 0.012     # alto-falante pequeno + chiado de sintonia
    save("swan_lake", x, 0.6)


def tanks():
    """Rumor de blindados na rua (loop de 8 s): grave que faz o vidro tremer, esteiras que rangem de longe."""
    secs = 8.0
    k = t(secs)
    low = band(noise(secs, 71), 18, 90) * (0.6 + 0.4 * np.sin(2 * np.pi * k / secs * 2))
    rattle = band(noise(secs, 72), 900, 2600) * (np.sin(2 * np.pi * 14 * k) > 0.6) * 0.12 * (0.5 + 0.5 * np.sin(2 * np.pi * k / secs))
    clank = np.zeros(len(k))
    for at in (1.3, 3.9, 6.2):
        n = int(0.4 * SR)
        put(clank, band(noise(0.4, int(at * 10)), 1500, 4500) * env_ad(n, 0.002, 0.07) * 0.5, at)
    save("tanks", low * 2.0 + rattle + clank * 0.4, 0.7)


def pipes_knock():
    """Cano batendo na parede do vizinho: três pancadas metálicas que ressoam e morrem."""
    x = np.zeros(int(3.2 * SR))
    for at, f in ((0.0, 190.0), (0.55, 215.0), (0.85, 175.0)):
        k = t(1.4)
        hit = (np.sin(2 * np.pi * f * k) + 0.6 * np.sin(2 * np.pi * f * 2.3 * k) + 0.3 * np.sin(2 * np.pi * f * 4.1 * k)) * np.exp(-k / 0.35)
        put(x, hit * 0.7 + band(noise(1.4, int(f)), 400, 2500) * np.exp(-k / 0.04) * 0.4, at)
    save("pipes_knock", reverb(x, 1.2, 0.35, circular=False)[:len(x)], 0.7)


def tram_pass():
    """Bonde/trólebus passando na rua lá fora: ronco grave que sobe e desce, trilhos que estalam, sino ao longe."""
    secs = 9.0
    k = t(secs)
    env = np.sin(np.pi * k / secs) ** 2
    rumble = band(noise(secs, 41), 25, 140) * env
    rails = np.zeros(len(k))
    for at in np.arange(1.5, 7.5, 0.28):
        n = int(0.05 * SR)
        put(rails, band(noise(0.05, int(at * 100)), 900, 3500) * env_ad(n, 0.001, 0.015) * (env[min(int(at * SR), len(env) - 1)] ** 1.5), at)
    bell = np.zeros(len(k))
    put(bell, np.sin(2 * np.pi * 1480 * t(1.0)) * np.exp(-t(1.0) / 0.25) * 0.15, 7.6)
    save("tram_pass", reverb(rumble * 1.5 + rails * 0.5 + bell, 1.0, 0.3, circular=False)[:len(k)], 0.7)


def siren_far():
    """Sirene de viatura, bem ao longe, subindo e descendo."""
    secs = 8.0
    k = t(secs)
    f = 700 + 220 * np.sin(2 * np.pi * k / 2.4)
    wail = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * k / secs) ** 2
    save("siren_far", reverb(band(wail, 300, 1800), 1.6, 0.5, circular=False)[:len(k)], 0.5)


def neighbor_music():
    """Vizinho tocando bayan atrás da parede fina (loop de 12 s), abafado: só os graves e médios passam."""
    secs = 12.0
    x = np.zeros(int(secs * SR))
    hz = lambda m: 440.0 * 2 ** ((m - 69) / 12)
    tune = ((69, 0.0, 0.6), (72, 0.6, 0.6), (71, 1.2, 0.6), (69, 1.8, 1.2), (67, 3.0, 0.6), (69, 3.6, 0.6), (68, 4.2, 0.6), (64, 4.8, 1.4),
            (69, 6.4, 0.6), (72, 7.0, 0.6), (76, 7.6, 0.6), (74, 8.2, 0.6), (72, 8.8, 0.6), (71, 9.4, 0.6), (69, 10.0, 1.8))
    for m, at, d_ in tune:
        put(x, bayan(hz(m), d_), at)
    save("neighbor_music", band(reverb(x, 0.8, 0.2), 120, 1500), 0.5)


def fluorescent_buzz():
    """Zumbido de lâmpada fluorescente (loop de 4 s): 100 Hz com harmônicos e falhas de tensão."""
    secs = 4.0
    k = t(secs)
    hum = sum(np.sin(2 * np.pi * 100 * h * k) / h for h in (1, 2, 3, 5)) * (0.8 + 0.2 * np.sin(2 * np.pi * 0.5 * k))
    flick = band(noise(secs, 52), 2500, 7000) * (np.sin(2 * np.pi * 7 * k) > 0.93) * 0.3
    save("fluorescent_buzz", hum * 0.4 + flick, 0.45)


def upstairs_steps():
    """Passos de alguém no apartamento de cima: pancadas surdas no teto, ritmo de quem anda de um lado a outro."""
    x = np.zeros(int(5.0 * SR))
    for at in (0.2, 0.9, 1.6, 2.3, 3.5, 4.2):
        k = t(0.4)
        put(x, np.sin(2 * np.pi * 62 * k) * np.exp(-k / 0.09) + band(noise(0.4, int(at * 10)), 100, 400) * np.exp(-k / 0.05) * 0.5, at)
    save("upstairs_steps", reverb(x, 0.9, 0.3, circular=False)[:len(x)], 0.6)


def crowd_murmur():
    """Multidão ao longe (loop de 8 s): rumor de vozes (ruído modulado em faixa de voz) com gritos esparsos e ritmo de palavras de ordem."""
    secs = 8.0
    k = t(secs)
    base = band(noise(secs, 61), 180, 1400) * (0.55 + 0.25 * np.sin(2 * np.pi * k / secs * 3) + 0.2 * np.sin(2 * np.pi * k / secs * 7))
    chant = band(noise(secs, 62), 250, 900) * (np.sin(2 * np.pi * 1.6 * k) > 0.2) * 0.35        # palavra de ordem em coro, ritmada
    shouts = np.zeros(len(k))
    for at in (1.2, 3.4, 5.9):
        d_ = 0.5
        f = 420 + 90 * np.sin(2 * np.pi * 3 * t(d_))
        put(shouts, np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t(d_) / d_) * 0.12, at)
    save("crowd_murmur", base + chant + shouts, 0.55)


def fire_crackle():
    """Fogueira em barril (loop de 5 s): sopro grave e estalos de brasa."""
    secs = 5.0
    k = t(secs)
    roar = band(noise(secs, 65), 60, 400) * (0.7 + 0.3 * np.sin(2 * np.pi * k * 2.1))
    pops = np.zeros(len(k))
    r = np.random.default_rng(66)
    for at in r.uniform(0.1, secs - 0.2, 40):
        n = int(0.03 * SR)
        put(pops, band(noise(0.03, int(at * 100)), 1500, 6000) * env_ad(n, 0.0005, 0.006) * r.uniform(0.2, 0.8), at)
    save("fire_crackle", roar * 0.8 + pops * 0.5, 0.5)


def gunshots_far():
    """Tiros isolados e uma rajada curta, muito longe, com eco de ruas (6 s)."""
    x = np.zeros(int(6.0 * SR))
    for at in (0.3, 2.4, 2.55, 2.7, 2.85, 4.9):
        n = int(0.25 * SR)
        k = t(0.25)
        crack = band(noise(0.25, int(at * 50)), 800, 5000) * np.exp(-k / 0.012) + np.sin(2 * np.pi * 90 * k) * np.exp(-k / 0.06) * 0.5
        put(x, crack, at)
    save("gunshots_far", reverb(x, 1.8, 0.55, circular=False)[:len(x)], 0.5)


def drip():
    """Pingo do soro/torneira (loop de 3 s): uma gota que bate na água e ressoa no azulejo."""
    x = np.zeros(int(3.0 * SR))
    k = t(0.5)
    plop = np.sin(2 * np.pi * np.cumsum(900 + 1400 * np.exp(-k / 0.03)) / SR) * np.exp(-k / 0.06)
    put(x, plop, 0.2)
    put(x, plop * 0.4, 1.7)
    save("drip", reverb(x, 1.4, 0.5, circular=True), 0.5)


def clock():
    x = np.zeros(int(2.0 * SR))
    for at, f0 in ((0.0, 3200), (1.0, 2500)):
        n = int(0.05 * SR)
        k = np.arange(n) / SR
        tick = band(np.random.default_rng(int(f0)).standard_normal(n), 1500, 5000) * env_ad(n, 0.001, 0.012)
        tick += np.sin(2 * np.pi * f0 * k) * env_ad(n, 0.001, 0.01) * 0.4
        put(x, tick, at)
    save("clock_loop", reverb(x, 0.5, 0.2), 0.7)


def sfx_objects():
    n = int(0.55 * SR)
    p = band(noise(0.55, 31), 1800, 7500) * (np.random.default_rng(32).random(n) ** 3) * env_ad(n, 0.01, 0.2)
    save("paper", p, 0.6)
    n = int(0.18 * SR)
    k = np.arange(n) / SR
    wood = (np.sin(2 * np.pi * 780 * k) * 0.6 + np.sin(2 * np.pi * 1310 * k) * 0.3) * env_ad(n, 0.001, 0.03)
    wood += band(np.random.default_rng(33).standard_normal(n), 800, 4000) * env_ad(n, 0.001, 0.012)
    save("chess_click", wood, 0.7)
    secs = 1.6
    k = t(secs)
    f = 180 + 120 * np.sin(2 * np.pi * 0.6 * k) + 60 * k
    creak = np.sin(2 * np.pi * np.cumsum(f) / SR) * (0.5 + 0.5 * np.sin(2 * np.pi * 7 * k)) * np.minimum(k / 0.15, 1) * np.exp(-k / 1.0)
    creak += band(noise(secs, 34), 400, 1800) * 0.15 * np.exp(-k / 1.0)
    save("door_creak", reverb(creak, 0.8, 0.25, circular=False), 0.6)
    secs = 1.4
    k = t(secs)
    bl = sum(np.sin(2 * np.pi * f * k) * a for f, a in ((392, 1.0), (588, 0.5), (783, 0.3), (1180, 0.15)))
    save("pickup", reverb(bl * np.exp(-k * 3.2) * np.minimum(k / 0.004, 1), 1.6, 0.4, circular=False), 0.6)
    secs = 0.6
    k = t(secs)
    pen = band(noise(secs, 35), 2500, 7000) * (0.5 + 0.5 * np.sin(2 * np.pi * 19 * k)) * np.minimum(k / 0.03, 1) * np.minimum((secs - k) / 0.05, 1)
    save("pen", pen, 0.5)


# --------------------------------------------------------------------------------------------
# Fonética eslava sintética (rádio e vozes): vogais por formantes + consoantes ш щ ж ч р т к
# --------------------------------------------------------------------------------------------
VOWELS = {"a": (750, 1200), "o": (520, 900), "u": (320, 800), "e": (500, 1800), "i": (300, 2200), "y": (360, 1500)}


def vowel(f0, dur, f1, f2, trill=False, seed=0):
    m = int(dur * SR)
    k = np.arange(m) / SR
    base = f0 * (1 + 0.015 * np.sin(2 * np.pi * 4.5 * k))
    ph = np.cumsum(base) / SR
    s = np.zeros(m)
    for h in range(1, 30):
        fh = base * h
        a = np.exp(-((fh - f1) / 170) ** 2) + 0.6 * np.exp(-((fh - f2) / 290) ** 2)
        s += a * np.sin(2 * np.pi * h * ph) / h ** 0.3
    s *= np.sin(np.pi * np.arange(m) / m) ** 1.4
    if trill:  # "р" rolado: amplitude pulsando ~28 Hz
        s *= 0.55 + 0.45 * (np.sin(2 * np.pi * 28 * k) > 0)
    return s


def fric(dur, lo, hi, amp=1.0, seed=0):
    m = int(dur * SR)
    s = band(np.random.default_rng(seed).standard_normal(m), lo, hi)
    return s * np.sin(np.pi * np.arange(m) / m) ** 0.7 * amp


def burst(lo, hi, seed=0, dur=0.012):
    m = int(dur * SR)
    return band(np.random.default_rng(seed).standard_normal(m), lo, hi) * env_ad(m, 0.0005, dur / 3) * 1.6


def consonant(kind, f0, seed):
    if kind == "sh":
        return fric(0.09, 2600, 7500, 0.9, seed)
    if kind == "shch":
        return np.concatenate([burst(1800, 5000, seed, 0.01), fric(0.11, 2300, 7000, 0.9, seed)])
    if kind == "zh":
        f = fric(0.085, 1400, 4800, 0.55, seed)
        return f + vowel(f0 * 0.9, 0.085, 280, 1400)[:len(f)] * 0.5
    if kind == "ch":
        return np.concatenate([burst(2200, 6500, seed, 0.014), fric(0.05, 2500, 7000, 0.8, seed)])
    if kind == "tr":
        return np.concatenate([burst(900, 4000, seed, 0.01), vowel(f0, 0.05, 400, 1400, trill=True)])
    if kind == "kr":
        return np.concatenate([burst(700, 3500, seed, 0.012), vowel(f0, 0.05, 400, 1200, trill=True)])
    if kind == "st":
        return np.concatenate([fric(0.045, 3800, 8500, 0.7, seed), burst(1000, 4500, seed + 1, 0.01)])
    if kind == "vz":
        f = fric(0.05, 900, 3200, 0.3, seed)
        return f + vowel(f0 * 0.9, 0.05, 300, 1100)[:len(f)] * 0.6
    if kind == "t":
        return burst(900, 4200, seed)
    if kind == "k":
        return burst(600, 3200, seed)
    if kind == "r":
        return vowel(f0, 0.07, 450, 1300, trill=True)
    if kind == "m":
        return vowel(f0, 0.06, 280, 900) * 0.6
    return np.zeros(0)


PRE = ["", "", "sh", "zh", "ch", "tr", "st", "vz", "kr", "shch", "t", "k"]
POST = ["", "", "", "r", "sh", "k", "t", "m"]


def word(f0, r, seed):
    out = []
    for j in range(int(r.integers(2, 5))):  # 2 a 4 sílabas por palavra
        pre = PRE[int(r.integers(len(PRE)))]
        v = list(VOWELS)[int(r.integers(len(VOWELS)))]
        post = POST[int(r.integers(len(POST)))]
        pitch = f0 * (1 + 0.06 * np.sin(j + seed) + (0.05 if j == 0 else 0.0))
        parts = [consonant(pre, pitch, seed * 7 + j), vowel(pitch, r.uniform(0.07, 0.15), *VOWELS[v]), consonant(post, pitch, seed * 11 + j)]
        out.extend(parts)
    return np.concatenate([p for p in out if len(p)])


# --------------------------------------------------------------------------------------------
# Rádio de 1993: locutor sem idioma com fonética eslava, AM, crepitar, "pips" de hora certa
# --------------------------------------------------------------------------------------------
def radio():
    secs = 20.0
    n = int(secs * SR)
    r = np.random.default_rng(1993)
    voice = np.zeros(n)
    pos = 0.4
    seed = 0
    while pos < secs - 3.2:
        for _ in range(int(r.integers(5, 11))):  # uma frase = várias palavras
            w = word(104 + r.uniform(-8, 14), r, seed)
            seed += 1
            put(voice, w, pos)
            pos += len(w) / SR + r.uniform(0.03, 0.09)
        pos += r.uniform(1.0, 2.0)  # respiro entre frases
    carrier = band(noise(secs, 41), 300, 3200)
    crackle = band((r.random(n) > 0.9992).astype(float) * r.uniform(0.5, 1.5, n), 600, 5000)
    x = np.tanh(2.0 * (voice / (np.max(np.abs(voice)) + 1e-9) * 0.65 + carrier * 0.07 + crackle * 0.7))
    for at in (16.5, 17.5, 18.5, 19.5):  # pips de hora certa
        m = int(0.1 * SR)
        k = np.arange(m) / SR
        put(x, np.sin(2 * np.pi * 1000 * k) * 0.25 * np.minimum(k / 0.003, 1) * np.minimum((0.1 - k) / 0.01, 1), at)
    save("radio_1993", band(x, 280, 3400), 0.7)


# --------------------------------------------------------------------------------------------
# Tema de Sergei — modo dórico em ré; motivo G-D-E-D (4-8-2-1)
# --------------------------------------------------------------------------------------------
N = {"C2": 65.41, "D2": 73.42, "G2": 98.0, "A2": 110.0, "D3": 146.83, "F3": 174.61, "A3": 220.0, "C4": 261.63,
     "D4": 293.66, "E4": 329.63, "F4": 349.23, "G4": 392.0, "A4": 440.0, "B4": 493.88, "C5": 523.25, "D5": 587.33,
     "E5": 659.26}


def theme_sergei():
    secs = 48.0
    x = np.zeros(int(secs * SR))
    for at, nm in ((0, "D2"), (8, "C2"), (16, "D2"), (24, "G2"), (32, "D2"), (40, "C2")):  # i - VII - i - IV (dórico)
        put(x, choir(N[nm], 9.5), at)
    mel = [  # frase 1: o motivo 4-8-2-1 (G D E D); depois uma resposta, o motivo em oitava alta e a resolução
        (2.0, "G4", 2.4), (4.6, "D5", 2.4), (7.2, "E4", 2.0), (9.4, "D4", 3.6),
        (17.0, "F4", 2.2), (19.4, "A4", 2.2), (21.8, "G4", 2.2), (24.2, "E4", 3.4),
        (28.0, "G4", 2.2), (30.6, "B4", 2.2), (33.2, "A4", 2.2), (35.8, "D5", 3.0),
        (39.0, "G4", 2.6), (41.8, "D5", 2.6), (44.4, "E4", 1.8), (46.2, "D4", 1.8)]
    for at, nm, d in mel:
        put(x, bayan(N[nm], d, 0.9), at)
    for base, notes in ((12.0, ("D3", "A3", "F3", "A3")), (28.5, ("D3", "F3", "A3", "C4")), (42.5, ("D3", "A3", "D4", "A3"))):
        for i, nm in enumerate(notes):
            put(x, balalaika(N[nm], 1.3, 0.55), base + i * 1.1)
    put(x, bell(146.83, 12.0, 0.5), 0.3)
    put(x, bell(110.0, 12.0, 0.45), 24.0)
    x = band(x, 50, 4500)
    save("theme_sergei", reverb(x, 2.8, 0.45), 0.55)


# --------------------------------------------------------------------------------------------
# Vozes-sílaba: cada personagem com timbre próprio; agora com consoantes e "р" rolado
# --------------------------------------------------------------------------------------------
def voices():
    pre = ["", "sh", "r", "k", "zh", "ch"]
    vows = list(VOWELS)
    for tag, f0, glide in (("low", 108, 0.9), ("high", 205, 1.15)):
        for i in range(6):
            f1, f2 = VOWELS[vows[i % len(vows)]]
            v = vowel(f0 * (1 + 0.06 * (i - 2)), 0.15, f1, f2)
            v *= np.linspace(1.0, glide * 0.94, len(v))
            c = consonant(pre[i], f0, 300 + i)
            s = np.concatenate([c * 0.8, v]) if len(c) else v
            s *= np.minimum(np.arange(len(s)) / SR / 0.012, 1) * np.exp(-np.arange(len(s)) / SR / 0.11)
            save(f"voice_{tag}_{i}", s, 0.6)


# --------------------------------------------------------------------------------------------
# Transição de memória: swell com reverb invertido + baque grave
# --------------------------------------------------------------------------------------------
def transition():
    secs = 3.4
    n = int(secs * SR)
    k = np.arange(n) / SR
    seed = band(noise(secs, 51), 200, 3000) * env_ad(n, 0.002, 0.08)
    seed += np.sin(2 * np.pi * 196 * k) * env_ad(n, 0.01, 0.2) * 0.8
    wash = reverb(seed, 3.0, 1.0, circular=False)[:n]
    rev = wash[::-1] * np.minimum(k / 2.4, 1.0) ** 2
    boom = np.sin(2 * np.pi * (46 - 14 * np.clip(k - 2.9, 0, 1)) * k) * env_ad(n, 0.0001, 0.3)
    hit = np.zeros(n)
    i = int(2.9 * SR)
    hit[i:] = boom[:n - i]
    save("transition", rev * 0.9 + hit * 1.2, 0.8)


def lighter():
    """Isqueiro: tampa metálica (clique agudo), faísca da pedra e o 'fump' da chama; ao fechar, um estalo seco."""
    on = np.zeros(int(0.9 * SR))
    k = np.arange(int(0.05 * SR)) / SR
    put(on, (np.sin(2 * np.pi * 2600 * k) + band(np.random.default_rng(61).standard_normal(len(k)), 2500, 9000) * 0.8)
        * env_ad(len(k), 0.0005, 0.008), 0.0)
    n = int(0.07 * SR)
    put(on, band(np.random.default_rng(62).standard_normal(n), 2000, 9000) * env_ad(n, 0.001, 0.03) * 0.9, 0.09)
    m = int(0.5 * SR)
    kk = np.arange(m) / SR
    put(on, band(np.random.default_rng(63).standard_normal(m), 150, 1100) * np.minimum(kk / 0.03, 1) * np.exp(-kk / 0.18) * 0.7, 0.14)
    save("lighter_on", on, 0.7)
    off = np.zeros(int(0.3 * SR))
    k2 = np.arange(int(0.04 * SR)) / SR
    put(off, (np.sin(2 * np.pi * 1700 * k2) * 0.7 + band(np.random.default_rng(64).standard_normal(len(k2)), 1500, 7000))
        * env_ad(len(k2), 0.0005, 0.012), 0.0)
    save("lighter_off", off, 0.6)


def whistle():
    """O assobio de Misha: o motivo G-D-E-D (4-8-2-1) em tom assobiado, com vibrato e ar."""
    notes = ((392.0, 0.0, 0.7), (587.33, 0.85, 0.75), (329.63, 1.8, 0.7), (293.66, 2.7, 1.3))
    x = np.zeros(int(4.4 * SR))
    for f0, at, dur in notes:
        k = t(dur)
        vib = 1 + 0.012 * np.sin(2 * np.pi * 5.6 * k) * np.minimum(k / 0.25, 1)
        tone = np.sin(2 * np.pi * np.cumsum(f0 * vib) / SR) + 0.12 * np.sin(2 * np.pi * np.cumsum(2 * f0 * vib) / SR)
        air = band(noise(dur, int(f0)), 1800, 6000) * 0.10
        env = np.minimum(k / 0.05, 1) * np.clip((dur - k) / 0.12, 0, 1)
        put(x, (tone * 0.55 + air) * env, at)
    save("whistle_motif", reverb(x, 0.6, 0.15, circular=False)[:len(x)], 0.5)


def kettle():
    """Chaleira no fogo: vapor chiando e um apito agudo que sobe e treme (loop de 6 s)."""
    secs = 6.0
    k = t(secs)
    steam = band(noise(secs, 81), 2500, 8000) * (0.5 + 0.5 * np.sin(2 * np.pi * k / secs * 2)) * 0.5
    f = 2100 + 260 * np.sin(2 * np.pi * k / secs) + 40 * np.sin(2 * np.pi * 9 * k)
    pipe = np.sin(2 * np.pi * np.cumsum(f) / SR) * (0.3 + 0.2 * np.sin(2 * np.pi * k / secs * 3))
    save("kettle", steam + pipe * 0.45, 0.5)


if __name__ == "__main__" and len(sys.argv) > 1:   # com nomes (ex.: swan_lake tanks), gera só essas funções
    for _n in sys.argv[1:]:
        globals()[_n]()
elif __name__ == "__main__":
    amb_room(); tinnitus(); heartbeat(); steps(); clock(); sfx_objects(); radio(); theme_sergei(); voices(); transition(); lighter()
    whistle(); kettle(); steps_floors()
    print("áudio em", os.path.abspath(OUT), "-", len(os.listdir(OUT)), "arquivos")
