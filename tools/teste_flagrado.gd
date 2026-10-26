extends SceneTree
## Teste do relógio: examina uma pista, estoura o relógio e confere que a cena recomeçou sem a nota (rollback).
## Uso: godot --headless --path . --script res://tools/teste_flagrado.gd

var _t := 0.0
var _phase := 0
var _first = null


func _initialize() -> void:
	Engine.time_scale = 8.0
	change_scene_to_file("res://rooms/ep_apt_boris.tscn")


func _process(delta: float) -> bool:
	_t += delta
	var cur := current_scene
	var st = root.get_node("Story")
	if cur == null or _t < 4.0:
		return false
	if _phase == 0:
		_first = cur
		for b in get_nodes_in_group("clue"):
			cur._on_interacted(b)
			break
		print("antes: notas=", st.notes.size())
		cur._clock = 0.3
		_phase = 1
	elif _phase == 1 and current_scene != _first and _t > 12.0:
		print("depois do flagrado: notas=", st.notes.size(), " relógio=", current_scene._clock, " (esperado notas=0)")
		quit()
	elif _t > 60.0:
		print("TEMPO ESGOTADO")
		quit()
	return false
