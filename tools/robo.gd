extends SceneTree
## Robô de teste: joga o jogo sozinho a partir da cena dada, examina toda pista que aparece, responde 1 em todas as escolhas
## e avança as falas. Imprime uma linha por cena e avisa quando uma cena trava.
## Uso: godot --headless --path . --script res://tools/robo.gd -- res://rooms/laboratorio.tscn [limite_de_cenas]

var _scene := ""
var _since := 0.0
var _tried := {}
var _poke := 0.0
var _count := 0
var _limit := 99


func _initialize() -> void:
	var a := OS.get_cmdline_user_args()
	Engine.time_scale = 8.0
	if a.size() > 1:
		_limit = int(a[1])
	change_scene_to_file(a[0])


func _process(delta: float) -> bool:
	var st = root.get_node("Story")
	var cur := current_scene
	if st._choice == -2:
		var code = cur.get_script().get_script_constant_map().get("CODE") if cur and cur.get_script() else null
		st._choice = maxi(0, Array(st._options).find(code))                  # cadeado: digita o código certo
	if st._waiting:
		st._advance = true
	if cur == null:
		return false
	_since += delta
	if cur.scene_file_path != _scene:
		_scene = cur.scene_file_path
		_since = 0.0
		_tried.clear()
		_count += 1
		print("[%d] %s  verdade=%d confiança=%s itens=%s notas=%d" % [_count, _scene.get_file(), st.truth, st.trust, st.items.keys(), st.notes.size()])
		if _scene.ends_with("titulo.tscn") and _count > 1:
			print("FIM: a história chegou aos créditos")
			quit()
			return true
		if _count > _limit:
			quit()
			return true
	_poke += delta
	if _poke > 0.4 and not st.busy and _since > 3.0:
		_poke = 0.0
		if cur.has_method("_on_interacted"):
			if cur.get("_done") != null and cur.get("_player") != null and not cur._done.has("diario"):
				cur._done["diario"] = true                                           # a cena 1 exige ler o diário
				cur._after_clue()
			var fresh := false
			for b in get_nodes_in_group("clue"):
				var key := str(b.get_meta("id", ""))
				if not _tried.has(key):
					_tried[key] = true
					cur._on_interacted(b)
					fresh = true
					break
			if not fresh and _since > 20.0 and not _tried.has("#volta"):    # pistas que só abrem depois de outras: mais uma volta
				_tried.clear()
				_tried["#volta"] = true
			elif not fresh and _since > 25.0 and _scene.ends_with("kosmos_fora.tscn"):
				cur.player.position.z += 4.0                                 # cena de caminhada: anda até o portão
	if _since > 150.0:
		print("   TRAVADA: ", _scene.get_file(), " tentadas=", _tried.keys())
		_since = 0.0
		st.next_scene()
	return false
