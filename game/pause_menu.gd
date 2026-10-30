class_name PauseMenu
extends CanvasLayer
## Menu de pausa/opções (Esc). Duas colunas: Jogo (controles, câmera) e Vídeo/Áudio. Com `from_title`, vira a tela de
## opções do título (sem pausar, sem "voltar ao título"). Navegável com mouse, teclado e controle. Salva em Settings.

signal closed

var from_title := false
var _panel := PanelContainer.new()
var _first: Control


func _ready() -> void:
	layer = 15
	process_mode = Node.PROCESS_MODE_ALWAYS
	visible = false
	var theme := Theme.new()
	theme.default_font_size = 9
	_panel.theme = theme
	var bg := StyleBoxFlat.new()                                          # fundo opaco: o menu se lê sobre qualquer cena
	bg.bg_color = Color(0.05, 0.045, 0.055, 0.95)
	bg.border_color = Color(0.45, 0.10, 0.11)
	bg.set_border_width_all(1)
	bg.set_content_margin_all(8)
	_panel.add_theme_stylebox_override("panel", bg)
	var outer := VBoxContainer.new()
	outer.add_theme_constant_override("separation", 4)
	_panel.add_child(outer)
	var title := Label.new()
	title.text = "OPÇÕES" if from_title else "PAUSADO"
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	outer.add_child(title)
	var cols := HBoxContainer.new()
	cols.add_theme_constant_override("separation", 14)
	outer.add_child(cols)
	var left := _column(cols, "JOGO")
	var right := _column(cols, "VÍDEO E ÁUDIO")

	_first = _slider(left, "Sensibilidade", 0.3, 2.5, Settings.sensitivity, func(v): Settings.sensitivity = v)
	_check(left, "Inverter eixo Y", Settings.invert_y, func(on): Settings.invert_y = on)
	_slider(left, "Balanço da câmera (0 = desligado)", 0.0, 1.0, Settings.bob, func(v): Settings.bob = v)
	_slider(left, "Campo de visão", 60.0, 90.0, Settings.fov, func(v): Settings.fov = v)

	var q := OptionButton.new()
	for n in Settings.QUALITY_NAMES:
		q.add_item("Qualidade: " + n)
	q.selected = Settings.quality
	q.item_selected.connect(func(i: int):
		Settings.quality = i
		Settings.apply_graphics())
	right.add_child(q)
	_check(right, "Tela cheia (F11)", Settings.fullscreen, func(on):
		Settings.fullscreen = on
		Settings.apply_display())
	_check(right, "Sincronia vertical", Settings.vsync, func(on):
		Settings.vsync = on
		Settings.apply_display())
	for a in [["Volume geral", "volume"], ["Música", "music"], ["Efeitos", "sfx"], ["Vozes", "voice"]]:
		var key: String = a[1]
		_slider(right, a[0], 0.0, 1.0, Settings.get(key), func(v):
			Settings.set(key, v)
			Settings.apply_audio())

	var row := HBoxContainer.new()
	row.alignment = BoxContainer.ALIGNMENT_CENTER
	row.add_theme_constant_override("separation", 6)
	outer.add_child(row)
	_button(row, "Voltar" if from_title else "Continuar", close)
	if not from_title:
		_button(row, "Título (jogo salvo)", func():
			close()
			get_tree().change_scene_to_file("res://rooms/titulo.tscn"))
		_button(row, "Sair do jogo", func(): get_tree().quit())
	var center := CenterContainer.new()                                   # centraliza qualquer que seja o tamanho do painel
	center.set_anchors_preset(Control.PRESET_FULL_RECT)
	center.add_child(_panel)
	add_child(center)


func _column(parent: Control, label: String) -> VBoxContainer:
	var c := VBoxContainer.new()
	c.custom_minimum_size = Vector2(190, 0)
	c.add_theme_constant_override("separation", 2)
	var l := Label.new()
	l.text = label
	l.modulate = Color(1, 1, 1, 0.55)
	c.add_child(l)
	parent.add_child(c)
	return c


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


func _check(parent: Control, label: String, on: bool, on_toggle: Callable) -> void:
	var c := CheckButton.new()
	c.text = label
	c.button_pressed = on
	c.toggled.connect(on_toggle)
	parent.add_child(c)


func _button(parent: Control, label: String, fn: Callable) -> void:
	var b := Button.new()
	b.text = label
	b.pressed.connect(fn)
	parent.add_child(b)


func open() -> void:
	visible = true
	if not from_title:
		get_tree().paused = true
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	_first.grab_focus()


func close() -> void:
	visible = false
	Settings.save()
	if not from_title:
		get_tree().paused = false
		Input.mouse_mode = Input.MOUSE_MODE_CAPTURED
	closed.emit()


func _unhandled_input(event: InputEvent) -> void:
	if visible and event.is_action_pressed("ui_cancel"):
		close()
		get_viewport().set_input_as_handled()
