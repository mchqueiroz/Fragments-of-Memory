extends Node
## Autoload "Sound": barramentos, ambiente, música, zumbido de ouvido ligado ao esquecimento e efeitos.
## Técnica: o ambiente e a música abaixam (duck) quando alguém fala; com o esquecimento alto o mundo
## fica abafado (passa-baixa) e o zumbido sobe — o som "esquece" junto com a imagem.

const DIR := "res://art/audio/%s.wav"

var _amb: AudioStreamPlayer
var _music: AudioStreamPlayer
var _tin: AudioStreamPlayer
var _lowpass := AudioEffectLowPassFilter.new()
var _duck := 0.0
var surface := "parquet"   # piso sob o jogador: parquet, concrete ou lino (passos)
var _room_fx := AudioEffectReverb.new()
var _cache := {}


func _ready() -> void:
	for b in ["Amb", "Music", "Sfx", "Voice"]:
		AudioServer.add_bus()
		var i := AudioServer.bus_count - 1
		AudioServer.set_bus_name(i, b)
		AudioServer.set_bus_send(i, "Master")
	_room_fx.damping = 0.6
	AudioServer.add_bus_effect(AudioServer.get_bus_index("Sfx"), _room_fx)
	var small := AudioEffectReverb.new()
	small.room_size = 0.3
	small.wet = 0.14
	AudioServer.add_bus_effect(AudioServer.get_bus_index("Voice"), small)
	_lowpass.cutoff_hz = 20500.0
	AudioServer.add_bus_effect(0, _lowpass)
	_tin = _loop("tinnitus", "Amb", -60.0)


func _stream(name: String, loop := false) -> AudioStreamWAV:
	var key := "%s%s" % [name, loop]
	if not _cache.has(key):
		var s := (load(DIR % name) as AudioStreamWAV).duplicate() as AudioStreamWAV
		if loop:
			s.loop_mode = AudioStreamWAV.LOOP_FORWARD
			s.loop_end = int(s.get_length() * s.mix_rate) # em quadros; data.size() engana quando o import comprime
		_cache[key] = s
	return _cache[key]


func _loop(name: String, bus: String, db: float) -> AudioStreamPlayer:
	var p := AudioStreamPlayer.new()
	p.stream = _stream(name, true)
	p.bus = bus
	p.volume_db = db
	add_child(p)
	p.play()
	return p


## Define o ambiente e a música da cena (troca com fade).
## `ground`: tipo de piso dos passos; `size`/`wet`: reverb da sala (hangar grande e frio x cozinha pequena e seca).
func scene(ambience: String, music: String, music_db := -16.0, ground := "parquet", size := 0.45, wet := 0.18) -> void:
	surface = ground
	_room_fx.room_size = size
	_room_fx.wet = wet
	if _amb:
		_amb.queue_free()
	_amb = _loop(ambience, "Amb", -9.0)
	_amb.set_meta("db", -9.0)                                          # a música é de music_for (trilha contínua entre cenas)


## Trilha por cena (sintetizada por tools/musica.py): post-punk frio nas cenas da linha A, post-punk quente nas memórias,
## techno brutalista nas de tensão, coro e sinos nas de luto. Mesma faixa em cenas seguidas = não reinicia (só ajusta o volume).
const MUSIC := {
	"titulo": ["mus_coro", -13.0], "laboratorio": ["mus_coro", -15.0], "cozinha": ["mus_postpunk_f", -16.0], "arquivos": ["mus_tecno", -18.0],
	"prototipo": ["mus_postpunk_f", -16.0], "gabinete": ["mus_coro", -15.0], "porao": ["mus_tecno", -17.0], "quarto": ["mus_coro", -14.0],
	"pulso": ["mus_tecno", -16.0], "kosmos_fora": ["mus_coro", -14.0], "ruas": ["mus_postpunk_a", -16.0], "clinica": ["mus_coro", -15.0],
	"sala_controle": ["mus_tecno", -18.0], "treinador": ["mus_postpunk_f", -16.0], "telhado": ["mus_postpunk_a", -16.0],
	"cemiterio": ["mus_coro", -13.0], "chave": ["mus_tecno", -17.0], "parque": ["mus_postpunk_f", -16.0], "apt_irina": ["mus_postpunk_a", -17.0],
	"museu": ["mus_postpunk_f", -17.0], "interrogatorio": ["mus_tecno", -19.0], "entrevista": ["mus_postpunk_f", -17.0],
	"arquivos_mortos": ["mus_tecno", -19.0], "metro": ["mus_postpunk_a", -16.0], "tabuleiro_sergei": ["mus_postpunk_f", -17.0],
	"apt_boris": ["mus_tecno", -19.0], "corredor": ["mus_tecno", -18.0], "piscar": ["mus_coro", -14.0], "tiro": ["mus_tecno", -12.0],
}
var _track := ""


func music_for(scene_path: String) -> void:
	var key := scene_path.get_file().get_basename().trim_prefix("ep_")
	var m: Array = MUSIC.get(key, ["mus_coro", -15.0])
	if m[0] == _track and _music and is_instance_valid(_music):
		_music.set_meta("db", float(m[1]))
		create_tween().tween_property(_music, "volume_db", float(m[1]), 2.0)
		return
	var old := _music
	_music = _loop(str(m[0]), "Music", -60.0)
	_music.set_meta("db", float(m[1]))
	_track = str(m[0])
	create_tween().tween_property(_music, "volume_db", float(m[1]), 3.0)
	if old and is_instance_valid(old):
		var tw := create_tween()
		tw.tween_property(old, "volume_db", -60.0, 2.5)
		tw.tween_callback(old.queue_free)


## Toca um efeito curto (2D).
func play(name: String, bus := "Sfx", db := 0.0, pitch := 1.0) -> void:
	var p := AudioStreamPlayer.new()
	p.stream = _stream(name)
	p.bus = bus
	p.volume_db = db
	p.pitch_scale = pitch
	p.finished.connect(p.queue_free)
	add_child(p)
	p.play()


## Fonte sonora no espaço (rádio, relógio): loop 3D preso a uma posição da cena.
func emitter(parent: Node, name: String, pos: Vector3, db := -8.0, unit := 2.5, cutoff := 20500.0) -> AudioStreamPlayer3D:
	var p := AudioStreamPlayer3D.new()
	p.attenuation_filter_cutoff_hz = cutoff # baixo = som abafado, como atrás de uma parede
	p.stream = _stream(name, true)
	p.bus = "Amb"
	p.volume_db = db
	p.unit_size = unit
	p.max_distance = 14.0
	p.position = pos
	parent.add_child(p)
	p.play()
	return p


## Toca um som uma vez, posicional (3D), e se apaga sozinho: eventos de ambiente (cano batendo, bonde, sirene).
func once(parent: Node, name: String, pos: Vector3, db := -10.0, unit := 3.0, cutoff := 20500.0) -> void:
	var p := AudioStreamPlayer3D.new()
	p.attenuation_filter_cutoff_hz = cutoff
	p.stream = _stream(name)
	p.bus = "Amb"
	p.volume_db = db
	p.unit_size = unit
	p.max_distance = 30.0
	p.position = pos
	parent.add_child(p)
	p.finished.connect(p.queue_free)
	p.play()


## Liga a audição ao esquecimento: 0 = normal, ~0.3 = abafado com zumbido.
func attention(forget: float) -> void:
	var k := clampf(forget / 0.28, 0.0, 1.0)
	_tin.volume_db = lerpf(-60.0, -27.0, k * k)
	_lowpass.cutoff_hz = lerpf(20500.0, 2600.0, k)


## Abaixa ambiente e música enquanto alguém fala.
func duck(on: bool) -> void:
	var tw := create_tween()
	tw.tween_method(_set_duck, _duck, 1.0 if on else 0.0, 0.6)


func _set_duck(v: float) -> void:
	_duck = v
	if _amb:
		_amb.volume_db = float(_amb.get_meta("db")) - 7.0 * v
	if _music:
		_music.volume_db = float(_music.get_meta("db")) - 9.0 * v
