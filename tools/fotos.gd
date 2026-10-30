extends SceneTree
## Fotos de revisão: abre cada cena da história, gira o jogador em 4 direções a partir da partida e salva PNGs.
## Uso: godot --path . --script res://tools/fotos.gd -- <pasta> [cena.tscn ...]   (precisa de janela; não roda headless)

var _out := ""
var _list: Array = []


func _initialize() -> void:
	var a := OS.get_cmdline_user_args()
	_out = a[0]
	DirAccess.make_dir_recursive_absolute(_out)
	_list = a.slice(1) if a.size() > 1 else Array(root.get_node("Story").ORDER)
	_run.call_deferred()


func _run() -> void:
	var st = root.get_node("Story")
	for path in _list:
		change_scene_to_file(path)
		for i in 240:                                                     # deixa a intro e o carregamento assentarem
			await process_frame
		st.visible = false
		var room = current_scene
		var p = room.get("player")
		if p == null:
			continue
		var y0: float = p.rotation.y
		for k in 4:
			p.rotation.y = y0 + k * PI / 2
			p.head.rotation.x = -0.12
			for i in 20:
				await process_frame
			var img := root.get_texture().get_image()
			img.save_png("%s/%s_%d.png" % [_out, str(path).get_file().get_basename(), k])
		var cam := Camera3D.new()                                          # um retrato de cada personagem, de frente
		room.add_child(cam)
		var n := 0
		for actor in room.find_children("*", "Node3D", true, false):
			if not (actor.get_script() and actor.get_script().get_global_name() == "Actor"):
				continue
			var fwd := Vector3(sin(actor.rotation.y), 0, cos(actor.rotation.y))
			cam.global_position = actor.global_position + fwd * 2.0 + Vector3(0.6, 1.5, 0)
			cam.look_at(actor.global_position + Vector3(0, 0.9, 0))
			cam.make_current()
			for i in 20:
				await process_frame
			root.get_texture().get_image().save_png("%s/%s_npc%d.png" % [_out, str(path).get_file().get_basename(), n])
			n += 1
		cam.queue_free()
		st.visible = true
		print("FOTO ", path)
	quit()
