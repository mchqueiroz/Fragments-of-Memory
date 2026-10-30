extends Node
## Autoload "Settings": preferências do jogador, salvas em user://settings.cfg.
## Acessibilidade: o balanço de câmera pode ser desligado (muita gente enjoa); sensibilidade e Y invertido são padrão.
## Vídeo: a qualidade decide quantas luzes projetam sombra (cada sombra omni redesenha a sala 6 vezes), SSAO e névoa
## volumétrica; é aplicada sozinha a cada cena nova e na hora em que muda no menu.

const PATH := "user://settings.cfg"
const QUALITY_NAMES := ["Baixa", "Média", "Alta"]
const SHADOWS := [0, 1, 2]                 # luzes com sombra por qualidade (as mais fortes da cena)
const ATLAS := [1024, 2048, 4096]

var sensitivity := 1.0 # multiplicador da sensibilidade do mouse/controle
var invert_y := false
var bob := 1.0         # 0 = sem balanço de cabeça, 1 = padrão
var fov := 70.0
var volume := 1.0      # volume geral (0 a 1)
var music := 1.0
var sfx := 1.0         # efeitos e ambiente
var voice := 1.0
var quality := 2       # 0 baixa, 1 média, 2 alta
var fullscreen := false
var vsync := true

var _scene: Node


func _ready() -> void:
	var cf := ConfigFile.new()
	if cf.load(PATH) == OK:
		sensitivity = cf.get_value("input", "sensitivity", sensitivity)
		invert_y = cf.get_value("input", "invert_y", invert_y)
		bob = cf.get_value("camera", "bob", bob)
		fov = cf.get_value("camera", "fov", fov)
		volume = cf.get_value("audio", "volume", volume)
		music = cf.get_value("audio", "music", music)
		sfx = cf.get_value("audio", "sfx", sfx)
		voice = cf.get_value("audio", "voice", voice)
		quality = clampi(cf.get_value("video", "quality", quality), 0, 2)
		fullscreen = cf.get_value("video", "fullscreen", fullscreen)
		vsync = cf.get_value("video", "vsync", vsync)
	apply_audio()
	apply_display()


func save() -> void:
	var cf := ConfigFile.new()
	cf.set_value("input", "sensitivity", sensitivity)
	cf.set_value("input", "invert_y", invert_y)
	cf.set_value("camera", "bob", bob)
	cf.set_value("camera", "fov", fov)
	cf.set_value("audio", "volume", volume)
	cf.set_value("audio", "music", music)
	cf.set_value("audio", "sfx", sfx)
	cf.set_value("audio", "voice", voice)
	cf.set_value("video", "quality", quality)
	cf.set_value("video", "fullscreen", fullscreen)
	cf.set_value("video", "vsync", vsync)
	cf.save(PATH)


func apply_audio() -> void:
	for pair in [["Master", volume], ["Music", music], ["Sfx", sfx], ["Amb", sfx], ["Voice", voice]]:
		var i := AudioServer.get_bus_index(pair[0])
		if i >= 0:
			AudioServer.set_bus_volume_db(i, linear_to_db(maxf(pair[1], 0.0001)))


func apply_display() -> void:
	DisplayServer.window_set_mode(DisplayServer.WINDOW_MODE_FULLSCREEN if fullscreen else DisplayServer.WINDOW_MODE_WINDOWED)
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_ENABLED if vsync else DisplayServer.VSYNC_DISABLED)


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_F11:
		fullscreen = not fullscreen
		apply_display()
		save()


func _process(_delta: float) -> void:
	var s := get_tree().current_scene
	if s != _scene and s != null:
		_scene = s
		await get_tree().process_frame                                    # as salas criam luzes no _ready
		await get_tree().process_frame
		apply_graphics()


## Aplica a qualidade à cena atual: sombras só nas luzes mais fortes, SSAO e névoa volumétrica conforme o nível.
func apply_graphics() -> void:
	var s := get_tree().current_scene
	if s == null:
		return
	get_viewport().positional_shadow_atlas_size = ATLAS[quality]
	for we in s.find_children("*", "WorldEnvironment", true, false):
		var env: Environment = we.environment
		if env == null:
			continue
		if not env.has_meta("fog_density"):
			env.set_meta("fog_density", env.volumetric_fog_density)
			env.set_meta("vol_fog", env.volumetric_fog_enabled)
			env.set_meta("ssao", env.ssao_enabled)
		env.ssao_enabled = bool(env.get_meta("ssao")) and quality >= 2
		env.volumetric_fog_enabled = bool(env.get_meta("vol_fog")) and quality >= 1
		env.fog_enabled = bool(env.get_meta("vol_fog")) and quality == 0      # névoa simples no lugar da volumétrica
		if env.fog_enabled:
			env.fog_light_color = env.volumetric_fog_albedo * 0.25
			env.fog_density = float(env.get_meta("fog_density")) * 0.6
	var player = s.get("player")
	var lights: Array = []
	for l in s.find_children("*", "Light3D", true, false):
		if l is DirectionalLight3D:
			if not l.has_meta("sh"):
				l.set_meta("sh", l.shadow_enabled)
			l.shadow_enabled = bool(l.get_meta("sh")) and quality >= 1
		elif not (player and player.is_ancestor_of(l)):                    # a chama do isqueiro cuida de si
			lights.append(l)
	lights.sort_custom(func(a, b): return a.light_energy * _reach(a) > b.light_energy * _reach(b))
	for i in lights.size():
		lights[i].shadow_enabled = i < SHADOWS[quality]


func _reach(l: Light3D) -> float:
	return l.omni_range if l is OmniLight3D else (l.spot_range if l is SpotLight3D else 1.0)
