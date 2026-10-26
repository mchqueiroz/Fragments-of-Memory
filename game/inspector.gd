class_name Inspector
extends CanvasLayer
## Modo "examinar" (como em Gone Home e Resident Evil): o objeto vem para perto, gira com o mouse e o fundo escurece.
## O objeto é um clone mostrado num SubViewport próprio (não atravessa paredes) e passa pelo mesmo pós-processo retrô.

signal closed

var _pivot := Node3D.new()
var _cam := Camera3D.new()
var _yaw := 0.5
var _pitch := 0.35
var _dist := 0.55
var _armed := false


func show_object(src: Node3D, caption: String) -> void:
	layer = 9 # abaixo do pós-processo (10): o objeto também ganha dither e paleta
	var dim := ColorRect.new()
	dim.color = Color(0, 0, 0, 0.78)
	dim.set_anchors_preset(Control.PRESET_FULL_RECT)
	dim.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(dim)
	var box := SubViewportContainer.new()
	box.stretch = true
	box.set_anchors_preset(Control.PRESET_FULL_RECT)
	box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(box)
	var vp := SubViewport.new()
	vp.transparent_bg = true
	vp.own_world_3d = true
	vp.size = Vector2i(480, 270)
	vp.msaa_3d = Viewport.MSAA_DISABLED
	box.add_child(vp)
	var env := Environment.new()
	env.background_mode = Environment.BG_CLEAR_COLOR
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(0.45, 0.42, 0.40)
	var we := WorldEnvironment.new()
	we.environment = env
	vp.add_child(we)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-40, 35, 0)
	sun.light_energy = 1.1
	vp.add_child(sun)
	var warm := OmniLight3D.new()
	warm.position = Vector3(0.4, 0.35, 0.7)
	warm.light_color = Color(1.0, 0.75, 0.45)
	warm.light_energy = 1.6
	warm.omni_range = 3.0
	vp.add_child(warm)
	_cam.fov = 35.0
	_cam.position = Vector3(0, 0, _dist)
	vp.add_child(_cam)
	vp.add_child(_pivot)

	var obj := src.duplicate() as Node3D
	_pivot.add_child(obj)
	obj.transform = Transform3D.IDENTITY
	var bounds := AABB()
	var first := true
	for mi in obj.find_children("*", "MeshInstance3D", true, false):
		var a: AABB = (mi as MeshInstance3D).global_transform * (mi as MeshInstance3D).get_aabb()
		bounds = a if first else bounds.merge(a)
		first = false
	obj.position = -bounds.get_center()
	_pivot.scale = Vector3.ONE * (0.32 / maxf(bounds.get_longest_axis_size(), 0.01))

	var cl := CanvasLayer.new()
	cl.layer = 12 # acima do pós-processo: texto legível
	add_child(cl)
	var lab := Label.new()
	lab.text = "%s\n\n[mouse] girar   [roda] aproximar   [E] devolver" % caption
	lab.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_WIDE)
	lab.offset_top = -64
	lab.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	lab.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	lab.add_theme_font_size_override("font_size", 10)
	cl.add_child(lab)
	await get_tree().create_timer(0.3).timeout # o E que abriu não fecha na hora
	_armed = true


func _process(delta: float) -> void:
	var s := Input.get_vector("look_left", "look_right", "look_up", "look_down")
	_yaw += s.x * 2.4 * delta
	_pitch = clampf(_pitch + s.y * 2.4 * delta, -1.4, 1.4)
	_pivot.rotation = Vector3(_pitch, _yaw, 0.0)
	_cam.position.z = lerpf(_cam.position.z, _dist, 1.0 - exp(-10.0 * delta))


func _unhandled_input(event: InputEvent) -> void:
	if not _armed:
		return
	if event is InputEventMouseMotion:
		_yaw += event.relative.x * 0.01
		_pitch = clampf(_pitch + event.relative.y * 0.01, -1.4, 1.4)
	elif event is InputEventMouseButton and event.pressed:
		if event.button_index == MOUSE_BUTTON_WHEEL_UP:
			_dist = clampf(_dist - 0.06, 0.3, 0.9)
		elif event.button_index == MOUSE_BUTTON_WHEEL_DOWN:
			_dist = clampf(_dist + 0.06, 0.3, 0.9)
		elif event.button_index == MOUSE_BUTTON_RIGHT:
			_close()
	elif event.is_action_pressed("interact") or event.is_action_pressed("ui_cancel"):
		_close()
	get_viewport().set_input_as_handled()


func _close() -> void:
	closed.emit()
	queue_free()
