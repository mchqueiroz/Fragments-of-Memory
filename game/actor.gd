class_name Actor
extends Node3D
## Personagem animado: esqueleto (idle/talk), rosto por quadros (piscar e boca) e olhar que acompanha o jogador.
## O modelo olha para +Z (frente do glTF), por isso a rotação usa atan2(x, z).

var target: Node3D
## Timbre da voz-sílaba: "low" (Sergei, Boris) ou "high" (Irina). `voice_pitch` afina cada personagem.
var voice_tag := "low"
var voice_pitch := 1.0
var _voice := AudioStreamPlayer3D.new()
var _was_open := false
var _anim: AnimationPlayer
var _face: StandardMaterial3D
var _tex := {}
var _talk := 0.0
var _blink := 2.5
var _mouth_t := 0.0


func setup(model: String, face_prefix: String, look_at_node: Node3D) -> void:
	target = look_at_node
	var m: Node3D = (load("res://art/models/%s.glb" % model) as PackedScene).instantiate()
	add_child(m)
	_anim = m.find_child("AnimationPlayer", true, false)
	for n in _anim.get_animation_list():
		if n in ["idle", "talk"]:
			_anim.get_animation(n).loop_mode = Animation.LOOP_LINEAR
	_anim.play("idle")
	for mi in m.find_children("*", "MeshInstance3D", true, false):
		var mesh := (mi as MeshInstance3D).mesh
		for s in mesh.get_surface_count():
			var mat := mesh.surface_get_material(s)
			if mat is StandardMaterial3D:
				mat.texture_filter = BaseMaterial3D.TEXTURE_FILTER_NEAREST_WITH_MIPMAPS
				if mat.resource_name.begins_with(face_prefix):
					_face = mat
	for st in ["neutral", "blink", "talk"]:
		_tex[st] = load("res://art/tex/%s_%s.png" % [face_prefix, st])
	_face.albedo_texture = _tex["neutral"]
	_voice.bus = "Voice"
	_voice.unit_size = 4.0
	_voice.position.y = 1.7
	_voice.volume_db = -3.0
	add_child(_voice)


## Fala por `seconds`: gesticula e mexe a boca.
func speak(seconds: float) -> void:
	_talk = seconds
	if _anim.current_animation != "talk":
		_anim.play("talk", 0.35)


func _process(delta: float) -> void:
	var to := target.global_position - global_position
	to.y = 0.0
	if to.length() > 0.05:
		rotation.y = lerp_angle(rotation.y, atan2(to.x, to.z), 1.0 - exp(-3.0 * delta))
	var state := "neutral"
	_blink -= delta
	if _blink < 0.0:
		state = "blink"
		if _blink < -0.12:
			_blink = randf_range(2.0, 5.0)
	if _talk > 0.0:
		_talk -= delta
		_mouth_t += delta
		var open := int(_mouth_t * 9.0) % 2 == 0
		if open and state != "blink":
			state = "talk"
		if open and not _was_open and not Story.vo_on(): # cada abertura de boca = uma sílaba (some quando há voz gravada)
			_voice.stream = load("res://art/audio/voice_%s_%d.wav" % [voice_tag, randi() % 6])
			_voice.pitch_scale = voice_pitch * randf_range(0.9, 1.1)
			_voice.play()
		_was_open = open
		if _talk <= 0.0:
			_anim.play("idle", 0.5)
	_face.albedo_texture = _tex[state]
