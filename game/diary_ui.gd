class_name DiaryUI
extends CanvasLayer
## Diário de Aleksey: tela de leitura simples (sem braços). Duas páginas por vez, com as notas de Story;
## quem nega a verdade (truth < 0) lê a versão que a mente reescreve (Story.note_text).

var _page := 0
var _dim := ColorRect.new()
var _book := Control.new()
var _left := Label.new()
var _right := Label.new()
var _nums := Label.new()
var _hint := Label.new()


func _ready() -> void:
	layer = 12
	visible = false
	_dim.color = Color(0, 0, 0, 0.62)
	_dim.set_anchors_preset(Control.PRESET_FULL_RECT)
	_dim.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_dim)
	_book.position = Vector2(80, 36)
	_book.size = Vector2(320, 198)
	add_child(_book)
	var cover := ColorRect.new()
	cover.color = Color(0.08, 0.07, 0.08)
	cover.size = _book.size
	_book.add_child(cover)
	for i in 2: # duas folhas de papel envelhecido
		var p := ColorRect.new()
		p.color = Color(0.78, 0.72, 0.56)
		p.position = Vector2(8 + i * 156, 8)
		p.size = Vector2(148, 182)
		_book.add_child(p)
	var spine := ColorRect.new()
	spine.color = Color(0.25, 0.2, 0.15)
	spine.position = Vector2(158, 8)
	spine.size = Vector2(4, 182)
	_book.add_child(spine)
	for pair in [[_left, 14.0], [_right, 170.0]]:
		var l: Label = pair[0]
		l.position = Vector2(pair[1], 16)
		l.size = Vector2(136, 160)
		l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		l.add_theme_font_size_override("font_size", 9)
		l.add_theme_constant_override("line_spacing", 1)
		l.add_theme_color_override("font_color", Color(0.08, 0.08, 0.24))
		_book.add_child(l)
	_nums.position = Vector2(14, 176)
	_nums.size = Vector2(296, 12)
	_nums.add_theme_font_size_override("font_size", 7)
	_nums.add_theme_color_override("font_color", Color(0.3, 0.25, 0.2))
	_book.add_child(_nums)
	_hint.text = "[A] [D] virar página     [G] ligar lembranças     [Tab] fechar"
	_hint.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_WIDE)
	_hint.offset_top = -26
	_hint.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_hint.add_theme_font_size_override("font_size", 8)
	add_child(_hint)
	Story.note_added.connect(func(_i): _refresh())


func set_open(on: bool) -> void:
	visible = on
	if on:
		_hint.text = "[A] [D] virar página   [G] ligar lembranças   [B] quadro   [Tab] fechar\nNotas sem prova se apagam com o tempo." + ("\nNo bolso: " + ", ".join(Story.items.keys()) if not Story.items.is_empty() else "")
		_refresh()
		Sound.play("paper", "Sfx", -6.0)


func flip(dir: int) -> void:
	var n := Story.notes.size()
	_page = clampi(_page + 2 * dir, 0, maxi(n - 1, 0))
	_refresh()
	Sound.play("paper", "Sfx", -10.0, 1.15)


func _refresh() -> void:
	var n := Story.notes.size()
	if n == 0:
		_left.text = "(páginas em branco)"
		_right.text = ""
		_nums.text = ""
		return
	_page = clampi(_page, 0, n - 1)
	_left.text = Story.note_text(_page)
	_right.text = Story.note_text(_page + 1) if _page + 1 < n else ""
	_nums.text = "%d%s%d / %d" % [_page + 1, " ".repeat(120), mini(_page + 2, n), n]
