extends SceneTree
## Teste do quadro de evidências: com provas suficientes a resposta certa resolve; sem provas, não.
## Uso: godot --headless --path . --script res://tools/teste_quadro.gd

var _st
var _asked := 0


func _initialize() -> void:
	Engine.time_scale = 8.0
	_st = root.get_node("Story")
	_st.reset()


var _started := false


func _process(_d: float) -> bool:
	if not _started:
		_started = true
		_run()
	if _st._choice == -2:
		if _st._question == "QUADRO DE EVIDÊNCIAS":
			_asked += 1
			_st._choice = 0 if _asked % 2 == 1 else _st._options.size() - 1     # abre a 1ª pergunta; na volta, fecha
		else:
			for q in _st.LEDGER:
				if q["q"] == _st._question:
					_st._choice = int(q["ok"])
	return false


func _run() -> void:
	for id in ["arquivos_mortos:ficha", "clinica:passaporte"]:
		_st.add_note("x", "", id)
	await _st.board()
	print("2 provas: resolvida=", _st.resolved.has("identidade"), "  (esperado false)")
	_st.add_note("x", "", "cemiterio:coroa")
	_asked = 0
	await _st.board()
	print("3 provas: resolvida=", _st.resolved.has("identidade"), " notas=", _st.notes.size(), "  (esperado true, 4)")
	quit()
