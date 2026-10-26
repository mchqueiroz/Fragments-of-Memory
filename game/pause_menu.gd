class_name PauseMenu
extends CanvasLayer
## Menu de pausa/configurações (Esc): sensibilidade, balanço de câmera (acessibilidade), campo de visão, Y invertido, volume.
## Navegável com mouse, teclado e controle (foco automático). Salva em Settings.

var _panel := PanelContainer.new()
var _first: Control


func _ready() -> void:
	layer = 15
	process_mode = Node.PROCESS_MODE_ALWAYS
	visible = false
	var theme := Theme.new()
	theme.default_font_size = 9
	_panel.theme = theme
	_panel.set_anchors_and_offsets_preset(Control.PRESET_CENTER, Control.PRESET_MODE_MINSIZE)
	var box := VBoxContainer.new()
	box.custom_minimum_size = Vector2(230, 0)
	box.add_theme_constant_override("separation", 3)
	_panel.add_child(box)
	var title := Label.new()
	title.text = "PAUSADO"
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	box.add_child(title)
	_first = _slider(box, "Sensibilidade", 0.3, 2.5, Settings.sensitivity, func(v): Settings.sensitivity = v)
	_slider(box, "Balanço da câmera (0 = desligado)", 0.0, 1.0, Settings.bob, func(v): Settings.bob = v)
	_slider(box, "Campo de visão", 60.0, 90.0, Settings.fov, func(v): Settings.fov = v)
	_slider(box, "Volume", 0.0, 1.0, Settings.volume, func(v):
		Settings.volume = v
		AudioServer.set_bus_volume_db(0, linear_to_db(maxf(v, 0.0001))))
	var inv := CheckButton.new()
	inv.text = "Inverter eixo Y"
	inv.button_pressed = Settings.invert_y
	inv.toggled.connect(func(on: bool): Settings.invert_y = on)
	box.add_child(inv)
	var go := Button.new()
	go.text = "Continuar"
	go.pressed.connect(close)
	box.add_child(go)
	var title_btn := Button.new()
	title_btn.text = "Voltar ao título (o jogo já foi salvo)"
	title_btn.pressed.connect(func():
		close()
		get_tree().change_scene_to_file("res://rooms/titulo.tscn"))
	box.add_child(title_btn)
	var quit := Button.new()
	quit.text = "Sair do jogo"
	quit.pressed.connect(func(): get_tree().quit())
	box.add_child(quit)
	add_child(_panel)


func _slider(parent: Control, label: String, lo: float, hi: float, value: float, on_change: Callable) -> Control:
	var l := Label.new()
	l.text = label
	parent.add_child(l)
	var s := HSlider.new()
	s.min_value = lo
	s.max_value = hi
	s.step = 0.01
	s.value = value
	s.value_changed.connect(on_change)
	parent.add_child(s)
	return s


func open() -> void:
	visible = true
	get_tree().paused = true
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	_first.grab_focus()


func close() -> void:
	visible = false
	get_tree().paused = false
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
	Settings.save()


func _unhandled_input(event: InputEvent) -> void:
	if visible and event.is_action_pressed("ui_cancel"):
		close()
		get_viewport().set_input_as_handled()
