extends Node
## Autoload "Settings": preferências do jogador, salvas em user://settings.cfg.
## Acessibilidade: o balanço de câmera pode ser desligado (muita gente enjoa); sensibilidade e Y invertido são padrão.

const PATH := "user://settings.cfg"

var sensitivity := 1.0 # multiplicador da sensibilidade do mouse/controle
var invert_y := false
var bob := 1.0         # 0 = sem balanço de cabeça, 1 = padrão
var fov := 70.0
var volume := 1.0      # volume geral (0 a 1)


func _ready() -> void:
	var cf := ConfigFile.new()
	if cf.load(PATH) == OK:
		sensitivity = cf.get_value("input", "sensitivity", sensitivity)
		invert_y = cf.get_value("input", "invert_y", invert_y)
		bob = cf.get_value("camera", "bob", bob)
		fov = cf.get_value("camera", "fov", fov)
		volume = cf.get_value("audio", "volume", volume)
	AudioServer.set_bus_volume_db(0, linear_to_db(maxf(volume, 0.0001)))


func save() -> void:
	var cf := ConfigFile.new()
	cf.set_value("input", "sensitivity", sensitivity)
	cf.set_value("input", "invert_y", invert_y)
	cf.set_value("camera", "bob", bob)
	cf.set_value("camera", "fov", fov)
	cf.set_value("audio", "volume", volume)
	cf.save(PATH)
