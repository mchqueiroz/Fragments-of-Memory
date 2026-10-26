"""Gera as vozes das falas "NOME: texto" (espeak-ng pt-br + filtro de fita/rádio de 1993) em art/audio/vo/<sha1[:12]>.wav.
A chave é o SHA-1 da fala exatamente como aparece no jogo; para trocar por gravações de verdade, basta substituir o arquivo
de mesmo nome (art/audio/vo/manifest.json lista chave -> personagem -> texto). Depois: godot --headless --import.
Uso: python3 tools/vozes.py"""
import glob, hashlib, json, os, re, subprocess, tempfile

ROOT = os.path.join(os.path.dirname(__file__), "..")
OUT = os.path.join(ROOT, "art", "audio", "vo")
# personagem -> (variante espeak, tom 0-99, velocidade, filtro)
VOICES = {
    "ALEKSEY": ("m4", 42, 150, "radio"), "MISHA": ("m4", 52, 158, "radio"), "BORIS": ("m3", 28, 140, "radio"),
    "SERGEI": ("m1", 36, 128, "radio"), "IRINA": ("f2", 58, 150, "radio"), "LENA": ("f4", 62, 120, "tape"),
    "TREINADOR": ("m2", 33, 135, "radio"), "INTERMEDIÁRIO": ("m5", 45, 160, "radio"), "KARPOV": ("m6", 20, 125, "phone"),
}
FILTERS = {
    "radio": "highpass=f=180,lowpass=f=4200,acompressor=threshold=0.08:ratio=4,aecho=0.8:0.6:35:0.18,volume=2.2",
    "phone": "highpass=f=400,lowpass=f=2800,acompressor=threshold=0.06:ratio=6,aresample=8000,volume=2.6",
    "tape": "highpass=f=150,lowpass=f=3200,tremolo=f=5:d=0.25,aecho=0.8:0.5:60:0.3,volume=2.0",
}
NAMES = "|".join(VOICES)
LINE = re.compile(r'"((?:%s)(?: \([^)]*\))?: (?:[^"\\]|\\.)*)"' % NAMES)


def lines():
    seen = {}
    files = glob.glob(os.path.join(ROOT, "rooms", "data", "*.json")) + glob.glob(os.path.join(ROOT, "rooms", "text", "*.json")) + \
        glob.glob(os.path.join(ROOT, "rooms", "*.gd")) + glob.glob(os.path.join(ROOT, "tools", "textos.py"))
    for f in files:
        txt = open(f, encoding="utf-8").read()
        if f.endswith(".json"):
            # JSON: percorre os valores para obter a string já decodificada
            def walk(x):
                if isinstance(x, str):
                    if re.match(r"^(?:%s)(?: \([^)]*\))?: " % NAMES, x):
                        seen[x] = True
                elif isinstance(x, list):
                    for y in x:
                        walk(y)
                elif isinstance(x, dict):
                    for y in x.values():
                        walk(y)
            walk(json.loads(txt))
        else:
            for m in LINE.finditer(txt):
                try:
                    seen[json.loads('"%s"' % m.group(1))] = True
                except ValueError:
                    pass
    return list(seen)


def speak(line, path):
    who, text = line.split(": ", 1)
    who = who.split(" (")[0]
    text = re.sub(r"\([^)]*\)", " ", text).replace("...", " , ").replace("«", "").replace("»", "")
    variant, pitch, speed, flt = VOICES[who]
    with tempfile.NamedTemporaryFile(suffix=".wav") as raw:
        subprocess.run(["espeak-ng", "-v", "pt-br+" + variant, "-p", str(pitch), "-s", str(speed), "-w", raw.name, text], check=True)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw.name, "-af", FILTERS[flt], "-ar", "22050", "-ac", "1", path], check=True)


def main():
    os.makedirs(OUT, exist_ok=True)
    manifest = {}
    for line in lines():
        key = hashlib.sha1(line.encode("utf-8")).hexdigest()[:12]
        path = os.path.join(OUT, key + ".wav")
        manifest[key] = {"personagem": line.split(": ", 1)[0], "texto": line.split(": ", 1)[1]}
        if not os.path.exists(path):                      # não sobrescreve gravações trocadas à mão
            speak(line, path)
    with open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=1)
    print(len(manifest), "falas")


main()
