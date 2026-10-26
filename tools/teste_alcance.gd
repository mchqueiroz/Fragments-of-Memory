extends SceneTree
## Teste de alcance: para cada pista de cada cena, procura uma posição livre a 1–1,8 m de onde o RAIO do jogador a atinge de verdade
## (sem parede ou móvel na frente). Pista sem posição = pista que o jogador não consegue examinar.
## Uso: godot --headless --path . --script res://tools/teste_alcance.gd -- [cena.tscn ...]

var _scenes: Array = []
var _i := -1
var _t := 0.0
var _bad := 0


func _initialize() -> void:
	var a := OS.get_cmdline_user_args()
	if a.is_empty():
		for l in FileAccess.get_file_as_string("res://game/story.gd").split("\n"):
			var s := l.strip_edges()
			if s.begins_with('"res://rooms/') and s.find(".tscn") > 0:
				_scenes.append(s.split('"')[1])
	else:
		_scenes = a
	_next()


func _next() -> void:
	_i += 1
	_t = 0.0
	if _i >= _scenes.size():
		print("pistas inalcançáveis no total: ", _bad)
		quit()
		return
	change_scene_to_file(_scenes[_i])


func _process(delta: float) -> bool:
	_t += delta
	var cur := current_scene
	if cur == null or _t < 2.5 or cur.get("player") == null and cur.get("_player") == null:
		return false
	var st = root.get_node("Story")
	st.busy = false
	var pl = cur.player if cur.get("player") != null else cur._player
	var names := []
	for b in cur.find_children("*", "StaticBody3D", true, false):
		if b.has_meta("id") and b.has_meta("prompt"):
			names.append(b)
	var lost := []
	for b in names:
		var center: Vector3 = b.global_position
		var half := 0.0
		for c in b.get_children():
			if c is CollisionShape3D and c.shape is BoxShape3D:
				center = c.global_position
				half = maxf(c.shape.size.x, c.shape.size.z) * 0.5 * maxf(b.global_basis.get_scale().x, 0.01)
		var ok := false
		for rr in [0.5, 0.8, 1.1, 1.4]:                         # a distância conta a partir da borda da pista
			var r: float = half + rr
			for k in 16:
				var ang := TAU * k / 16.0
				var pos := Vector3(center.x + cos(ang) * r, 0.05, center.z + sin(ang) * r)
				if pl.test_move(Transform3D(Basis(), pos), Vector3.ZERO):
					continue
				pl.global_position = pos
				var toward := Vector3(pos.x - center.x, 0.0, pos.z - center.z).normalized()
				var aim := center + toward * maxf(half - 0.15, 0.0)                    # mira na face de perto, como uma pessoa faria
				var dx := aim.x - pos.x
				var dz := aim.z - pos.z
				pl.rotation.y = atan2(-dx, -dz)
				var eye: Vector3 = pl.head.global_position
				pl.head.rotation.x = atan2(aim.y - eye.y, Vector2(dx, dz).length())
				pl.head.force_update_transform()
				pl._ray.force_raycast_update()
				if pl._ray.is_colliding() and pl._ray.get_collider() == b:
					ok = true
					break
			if ok:
				break
		if not ok:
			lost.append(str(b.get_meta("id")))
	print("%-28s pistas=%2d  inalcançáveis=%s" % [_scenes[_i].get_file(), names.size(), lost])
	_bad += lost.size()
	_next()
	return false
