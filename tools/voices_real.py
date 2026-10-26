"""Processa gravações REAIS em russo (domínio público, LibriVox) para o rádio e a fita de Lena.

Uso: python3 -I tools/voices_real.py --radio <kamen_01.mp3> --tape <eugeneonegin_03.mp3>
Fontes e licenças: docs/CREDITS.md. Só usamos autores livres no mundo todo (Mandelstam m.1938, Pushkin m.1837);
poemas de Akhmatova (m.1966) ficam de fora, pois o TEXTO ainda é protegido na Rússia e na UE.
Saída: art/audio/radio_real.wav (leitura de poesia num rádio AM de 1993) e art/audio/lena_tape.wav (fita cassete).
"""
import argparse
import os
import subprocess
import wave

import numpy as np

SR = 22050
OUT = os.path.join(os.path.dirname(__file__), "..", "art", "audio")
os.makedirs(OUT, exist_ok=True)


def decode(path, start, dur):
    """Decodifica um trecho (mono, 22,05 kHz) com o ffmpeg para um array float."""
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(start), "-t", str(dur), "-i", path,
                        "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True)
    x = np.frombuffer(r.stdout, dtype=np.float32).astype(float)
    return x / (np.sqrt(np.mean(x ** 2)) + 1e-9) * 0.12


def band(x, lo=None, hi=None, order=2):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    g = np.ones_like(f)
    if lo:
        g *= 1 / (1 + (lo / np.maximum(f, 1e-3)) ** (2 * order))
    if hi:
        g *= 1 / (1 + (f / hi) ** (2 * order))
    return np.fft.irfft(X * g, len(x))


def loop_xfade(x, secs=1.5):
    """Torna o trecho um loop sem estalo: funde o final com o começo."""
    n = int(secs * SR)
    y = x[:-n].copy()
    ramp = np.linspace(0, 1, n)
    y[:n] = y[:n] * ramp + x[-n:] * (1 - ramp)
    return y


def save(name, x, peak=0.85):
    x = x / (np.max(np.abs(x)) + 1e-9) * peak
    with wave.open(os.path.join(OUT, name + ".wav"), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())


def radio(src):
    rng = np.random.default_rng(1993)
    x = decode(src, 150, 75)
    n = len(x)
    tt = np.arange(n) / SR
    x = band(x, 350, 3000)                                                    # banda estreita do AM
    fade = 0.80 + 0.20 * np.sin(2 * np.pi * 0.11 * tt + 1.0) * np.sin(2 * np.pi * 0.037 * tt + 0.3)
    x = np.tanh(2.6 * x) * fade                                              # distorção suave e "fading" de sinal
    hiss = band(rng.standard_normal(n), 300, 3300) * 0.045
    crackle = band((rng.random(n) > 0.9993).astype(float) * rng.uniform(0.4, 1.4, n), 500, 5000) * 0.8
    whistle = np.sin(2 * np.pi * 1850 * tt) * 0.006 * (0.5 + 0.5 * np.sin(2 * np.pi * 0.05 * tt))
    save("radio_real", band(loop_xfade(x + hiss + crackle + whistle), 280, 3400), 0.7)


def tape(src):
    rng = np.random.default_rng(1992)
    x = decode(src, 300, 85)
    n = len(x)
    tt = np.arange(n) / SR
    wow = tt + 0.0012 * np.sin(2 * np.pi * 0.55 * tt) + 0.0003 * np.sin(2 * np.pi * 6.0 * tt)  # oscilação de velocidade
    x = np.interp(wow, tt, x)
    x = band(x, 140, 5200)
    x = np.tanh(1.6 * x)
    x += band(rng.standard_normal(n), 2500, 9000) * 0.03 + np.sin(2 * np.pi * 50 * tt) * 0.004   # chiado e zumbido
    drop = np.ones(n)
    for at in rng.uniform(5, n / SR - 5, 4):                                 # falhas de oxidação da fita
        i = int(at * SR)
        drop[i:i + int(0.12 * SR)] *= 0.25
    save("lena_tape", loop_xfade(x * drop), 0.8)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--radio", required=True)
    ap.add_argument("--tape", required=True)
    a = ap.parse_args()
    radio(a.radio)
    tape(a.tape)
    print("ok: radio_real.wav e lena_tape.wav em", os.path.abspath(OUT))
