extends SceneTree
## Checa no Godot o que o auditor do Blender não vê: personagens e modelos avulsos (xadrez, plantas...) posicionados
## por código/JSON. Acusa personagem dentro de móvel ou parede, e modelo flutuando ou enterrado.
## Uso: godot --headless --path . --script res://tools/teste_posicoes.gd [-- cena.tscn ...]

var _bad := 0
var _dump := {}   # com DUMP=<arquivo>: posições de personagens e modelos avulsos para tools/auditoria.py (eixos do Blender)


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	var a := OS.get_cmdline_user_args()
	var list: Array = a if a.size() > 0 else Array(root.get_node("Story").ORDER)
	for path in list:
		change_scene_to_file(path)
		for i in 30:
			await physics_frame
		_check(current_scene, str(path).get_file())
	if OS.get_environment("DUMP") != "":
		var f := FileAccess.open(OS.get_environment("DUMP"), FileAccess.WRITE)
		f.store_string(JSON.stringify(_dump))
	print("TOTAL ", _bad)
	quit(1 if _bad > 0 else 0)


func _check(scene: Node, tag: String) -> void:
	var space := (scene as Node3D).get_world_3d().direct_space_state
	var player = scene.get("player")
	var skip: Array[RID] = []
	if player:
		skip.append(player.get_rid())
	for c in scene.find_children("*", "CollisionObject3D", true, false):
		if c.is_in_group("clue") or c is Area3D:
			skip.append(c.get_rid())
	for actor in scene.find_children("*", "Node3D", true, false):
		if not (actor.get_script() and actor.get_script().get_global_name() == "Actor"):
			continue
		var p: Vector3 = actor.global_position
		var mine: Array[RID] = skip.duplicate()
		for c in actor.find_children("*", "CollisionObject3D", true, false):
			mine.append(c.get_rid())
		var cap := CapsuleShape3D.new()
		var seated: bool = actor.pose != ""
		cap.radius = 0.16 if seated else 0.2
		cap.height = 0.6 if seated else 1.2
		var q := PhysicsShapeQueryParameters3D.new()
		q.shape = cap
		q.transform = Transform3D(Basis(), p + Vector3(0, 1.15 if seated else 0.9, 0))   # sentado: só o tronco (as pernas vão sob a mesa)
		q.exclude = mine
		var hits := space.intersect_shape(q, 8)
		for h in hits:
			_report(tag, "personagem %s dentro de %s" % [actor.name, _path(h["collider"])], p)
		var ray := PhysicsRayQueryParameters3D.create(p + Vector3(0, 0.4, 0), p + Vector3(0, -1.5, 0))
		ray.exclude = mine
		var r := space.intersect_ray(ray)
		if r and absf(r["position"].y - p.y) > 0.06:
			_report(tag, "personagem %s com os pés %.2f m %s do piso" % [actor.name, absf(r["position"].y - p.y),
					"acima" if p.y > r["position"].y else "abaixo"], p)
	var models: Array = []
	for n in scene.get_children():
		if n is Node3D and str(n.scene_file_path).begins_with("res://art/models/"):
			models.append(n)
	if models.size() > 0:
		models.sort_custom(func(x, y): return _aabb(x).get_volume() > _aabb(y).get_volume())
		var e := {"npcs": [], "models": []}
		for actor in scene.find_children("*", "Node3D", true, false):
			if actor.get_script() and actor.get_script().get_global_name() == "Actor":
				var g: Vector3 = actor.global_position
				e["npcs"].append([g.x, -g.z, g.y, str(actor.get_meta("id", actor.name)), actor.pose])
		for m in models.slice(1):
			var b := _aabb(m)
			e["models"].append([b.position.x, -b.end.z, b.position.y, b.end.x, -b.position.z, b.end.y, m.scene_file_path.get_file()])
		_dump[models[0].scene_file_path.get_file().get_basename()] = e
	var prims := []                                                                   # primitivas criadas no Godot (exteriores)
	for mi in scene.find_children("*", "MeshInstance3D", true, false):
		if not (mi.mesh is PrimitiveMesh) or mi.mesh is QuadMesh:                     # quads: decalques, cartazes, céu
			continue
		var b: AABB = mi.mesh.get_aabb()
		var pts := []
		for k in 8:
			var w: Vector3 = mi.global_transform * (b.position + b.size * Vector3(k & 1, (k >> 1) & 1, (k >> 2) & 1))
			pts.append([w.x, -w.z, w.y])
		var o: Vector3 = mi.global_position
		prims.append(["%s %s em (%.2f, %.2f, %.2f)" % [mi.mesh.get_class(), b.size, o.x, o.y, o.z], pts])
	if prims.size() > 0:
		_dump["prims:" + tag] = prims
	if models.size() > 1:
		for m in models.slice(1):                                                    # o maior é a casca do cômodo
			var b := _aabb(m)
			var own: Array[RID] = skip.duplicate()
			for c in m.find_children("*", "CollisionObject3D", true, false):
				own.append(c.get_rid())
			var c0 := Vector3(b.get_center().x, b.position.y, b.get_center().z)
			var ray := PhysicsRayQueryParameters3D.create(c0 + Vector3(0, 0.3, 0), c0 + Vector3(0, -3, 0))
			ray.exclude = own
			var r := space.intersect_ray(ray)
			if r and absf(r["position"].y - c0.y) > 0.03:
				_report(tag, "modelo %s %s %.2f m" % [m.scene_file_path.get_file(), "flutua" if c0.y > r["position"].y else "enterrado",
						absf(r["position"].y - c0.y)], c0)


func _aabb(n: Node3D) -> AABB:
	var out := AABB()
	var first := true
	for mi in n.find_children("*", "MeshInstance3D", true, false):
		var b: AABB = mi.global_transform * mi.get_aabb()
		out = b if first else out.merge(b)
		first = false
	return out


func _path(o: Object) -> String:
	var n := o as Node
	return str(n.get_parent().name) + "/" + str(n.name) if n and n.get_parent() else str(o)


func _report(tag: String, msg: String, p: Vector3) -> void:
	_bad += 1
	print("  %s: %s  em (%.2f, %.2f, %.2f)" % [tag, msg, p.x, p.y, p.z])
