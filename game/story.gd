extends CanvasLayer
## Autoload "Story": estado da narrativa e interface de texto.
##  * legenda/voz em off (say), escolhas (ask) e diálogo com falas e escolhas (talk);
##  * diário: lista de notas; quem nega a verdade (truth < 0) lê a versão distorcida que a mente de Aleksey edita;
##  * fade e cartela de título; `busy` trava o jogador durante conversas.

signal note_added(index: int)

## Ordem de jogo das cenas (estilo Memento: linhas A e F se alternam; ver a bíblia da história).
const ORDER: Array[String] = [
	"res://rooms/laboratorio.tscn", # A1  T+0        O Laboratório
	"res://rooms/cozinha.tscn",     # F1  jun/1991   A Cozinha dos Volkov
	"res://rooms/arquivos.tscn",    # A2  T−30 min   Os Arquivos
	"res://rooms/prototipo.tscn",   # F2  jul/1991   A Sala do Protótipo
	"res://rooms/gabinete.tscn",    # A3  T−2h30     O Gabinete
	"res://rooms/porao.tscn",       # F3  19/ago/1991 O Golpe
	"res://rooms/quarto.tscn",      # A4  T−6h       O Quarto de Lena
	"res://rooms/pulso.tscn",       # F4  21/ago/1991 O Pulso (fim do Ato I)
	"res://rooms/kosmos_fora.tscn", # abertura do Ato II: o Kosmos brutalista por fora
	"res://rooms/ruas.tscn",        # A5  T−10h      As Ruas do Parlamento
	"res://rooms/clinica.tscn",     # F5  set/1991   A Clínica
	"res://rooms/ep_sala_controle.tscn",  # A6  T−1 dia     A Sala de Controle
	"res://rooms/ep_treinador.tscn",  # F6  1992        O Treinador
	"res://rooms/ep_telhado.tscn",  # A7  T−2 dias    O Telhado
	"res://rooms/ep_cemiterio.tscn",  # F7  mar/1992    O Cemitério
	"res://rooms/ep_chave.tscn",  # A8  T−3 dias    A Noite da Chave
	"res://rooms/ep_parque.tscn",  # F8  ago/1993    O Parque Gorky
	"res://rooms/ep_apt_irina.tscn",  # A9  T−4 dias    O Apartamento de Irina
	"res://rooms/ep_museu.tscn",  # F9  ago/1993    O Museu Desativado
	"res://rooms/ep_interrogatorio.tscn",  # A10 T−6 dias    O Interrogatório de Boris
	"res://rooms/ep_entrevista.tscn",  # F10 ago/1993    A Entrevista de Segurança
	"res://rooms/ep_arquivos_mortos.tscn",  # A11 T−8 dias    Os Arquivos Mortos
	# cortada: "res://rooms/ep_lounge.tscn",  # F11 set/1993    O Lounge
	"res://rooms/ep_metro.tscn",  # A12 T−10 dias   O Metrô
	"res://rooms/ep_tabuleiro_sergei.tscn",  # F12 set/1993    O Tabuleiro
	# cortada: "res://rooms/ep_decreto.tscn",  # A13 T−12 dias   O Decreto
	"res://rooms/ep_apt_boris.tscn",  # F13 set/1993    O Apartamento de Boris
	"res://rooms/ep_corredor.tscn",  # A14 T−13 dias   O Corredor
	# cortada: "res://rooms/ep_telefone.tscn",  # F14 T−15 dias   O Telefone Vermelho
	"res://rooms/ep_piscar.tscn",  # F15 T−14 dias   O Piscar
	"res://rooms/ep_tiro.tscn",  #     T = 0        O Tiro (final)
]
var index := 0

var truth := 0
var flags := {}
var notes: Array = [] # cada item: [texto, versão distorcida, id]
var items := {}       # objetos que viajam entre cenas (peão, cartão...)
var trust := {"irina": 0, "boris": 0, "sergei": 0}   # o que cada um pensa de Aleksey: muda falas e o final
var deduced := {}     # ligações do diário já feitas
var resolved := {}    # perguntas do quadro de evidências já respondidas
var _seen_q := {}
var busy := false
var cp_scene := ""    # cena do último checkpoint (para tentar de novo sem duplicar notas)
var _cp := {}

const SAVE := "user://save.json"

## Ligações do diário (tecla C): duas notas que, lado a lado, revelam algo. a/b = "cena:pista" das notas; la/lb = rótulo curto.
const DEDUCTIONS := [
	{"id": "logs", "a": "arquivos:log", "b": "sala_controle:camlog", "la": "log dos arquivos, 23h15", "lb": "log das câmeras, 23h15",
	 "note": "Dois logs, mesmo horário, mesmas iniciais 'B.V.'. Ninguém erra duas vezes do mesmo jeito: alguém está montando Boris como culpado.",
	 "alt": "Os logs confirmam: Boris."},
	{"id": "irmaos", "a": "sala_controle:foto", "b": "entrevista:retrato", "la": "foto sob a mão de Boris", "lb": "foto virada na mesa dele",
	 "note": "Boris dorme com a mão sobre a foto e a esconde de quem entra. Ele guarda alguém de si mesmo.",
	 "alt": "Boris é sentimental. Fraqueza."},
	{"id": "data", "a": "museu:livro", "b": "arquivos_mortos:ficha", "la": "última visita ao museu", "lb": "ficha retirada",
	 "note": "21 de agosto de 1991: a última visita de M. Volkov ao museu e o dia em que a ficha dele foi 'retirada'. Alguém o levou embora naquela noite.",
	 "alt": "Datas parecidas. Burocracia."},
	{"id": "misha", "a": "cemiterio:coroa", "b": "tabuleiro_sergei:jogo", "la": "o laço 'Misha' no funeral", "lb": "o nome que escapou na partida",
	 "note": "'Misha' no laço do funeral de Lena e 'Misha' na minha boca diante de Sergei. O nome me conhece antes de eu conhecê-lo.",
	 "alt": "Misha é um apelido comum."},
	{"id": "peoes", "a": "tabuleiro_sergei:pecas", "b": "apt_boris:cama", "la": "o peão que Sergei me deu", "lb": "o peão sob o travesseiro de Boris",
	 "note": "Dois peões brancos, lascados do mesmo jeito. Saíram do mesmo jogo, da mesma mão: a de um pai que ensinava xadrez a dois filhos.",
	 "alt": "Peões de xadrez são todos iguais."},
	{"id": "irina", "a": "apt_irina:ordem", "b": "metro:conversa", "la": "ordem de apagar Irina", "lb": "o prazo que Irina me deu",
	 "note": "Karpov assina a ordem de apagar Irina, e Irina me dá dez dias para armar o Lethe. Ela me empurra para o botão antes que o botão chegue nela.",
	 "alt": "Irina trabalha demais."},
	{"id": "sexta", "a": "corredor:quadro", "b": "sala_controle:janela", "la": "aviso de evacuação na sexta", "lb": "o Lethe sob a lona",
	 "note": "Evacuar o prédio e esconder o Lethe sob uma lona: o pulso será disparado com a casa vazia de quem ainda pode escolher esquecer.",
	 "alt": "Exercício de evacuação. Nada demais."},
	{"id": "cadernos", "a": "laboratorio:caderno", "b": "piscar:diario", "la": "'não confie em Boris'", "lb": "'não confie em Sergei'",
	 "note": "Duas letras no mesmo diário: uma manda desconfiar de Boris, outra de Sergei. Alguém escolhe por mim em quem eu confio.",
	 "alt": "Meu diário se contradiz. Só isso."},
	{"id": "lena", "a": "quarto:cartao", "b": "chave:gravacao", "la": "'Serioja, lembre de mim'", "lb": "a fita que Sergei não desliga",
	 "note": "Lena pediu para ser lembrada, e Sergei ouve a fita até gastar. O Lethe nasceu desse pedido que ele não conseguiu atender.",
	 "alt": "Sergei é um homem sentimental."},
]

## Quadro de evidências (tecla B), à la Obra Dinn: perguntas do caso que o jogador responde SÓ quando tem provas nas notas.
## Uma pergunta aparece quando há ao menos uma nota-prova; resolve se a resposta é certa e há `n` provas. Errar e "sem prova" soam iguais.
const LEDGER := [
	{"id": "identidade", "q": "Quem sou eu, de verdade?", "opts": ["Aleksey Petrov", "Mikhail Volkov", "Sergei Morozov", "Ninguém"], "ok": 1, "n": 3,
	 "need": ["arquivos_mortos:ficha", "clinica:passaporte", "cemiterio:coroa", "entrevista:crachas", "apt_boris:foto", "museu:livro", "cozinha:peao"],
	 "note": "Eu sou Mikhail Volkov, Misha. Aleksey Petrov é um nome que me deram em setembro de 1991, junto com um rosto novo.", "alt": "Sou Aleksey Petrov. O resto é ruído."},
	{"id": "boris", "q": "O que Boris é para mim?", "opts": ["Um inimigo", "Meu chefe de segurança, nada mais", "Meu irmão mais velho", "Um desconhecido"], "ok": 2, "n": 2,
	 "need": ["sala_controle:foto", "entrevista:retrato", "apt_boris:foto", "apt_boris:cama", "cemiterio:conversa", "interrogatorio:conversa", "cozinha:peao"],
	 "note": "Boris é meu irmão mais velho. Ele me procura desde 1991 sem saber que eu estou diante dele, e eu o incrimino sem saber que o destruo.", "alt": "Boris é só um policial desconfiado."},
	{"id": "logs", "q": "Quem apagou o log às 23h15?", "opts": ["Boris", "Sergei", "Eu, com a credencial de Boris", "Irina"], "ok": 2, "n": 3,
	 "need": ["arquivos:log", "sala_controle:camlog", "sala_controle:cracha", "sala_controle:terminal"],
	 "note": "Fui eu: copiei a credencial de Boris e programei o apagamento para as 23h15. O log acusa Boris porque eu o escrevi.", "alt": "O log não mente: foi Boris."},
	{"id": "lethe", "q": "O que o Lethe faz a quem o aciona?", "opts": ["Destrói o prédio", "Apaga a memória dele primeiro", "Mata todos num raio", "Nada: está sabotado"], "ok": 1, "n": 2,
	 "need": ["laboratorio:console", "chave:painel", "gabinete:plantas", "pulso:proto", "quarto:cartao", "chave:missil"],
	 "note": "O Lethe é um pulso que apaga a memória. Quem o aciona esquece primeiro. Não é uma bomba, é um esquecimento em escala.", "alt": "O Lethe é só um míssil quebrado."},
	{"id": "lena", "q": "Por que o Lethe existe?", "opts": ["Arma política de Karpov", "Para Lena não esquecer o marido", "Para apagar a oposição", "Experimento da KGB"], "ok": 1, "n": 2,
	 "need": ["quarto:cartao", "chave:gravacao", "prototipo:fita", "gabinete:plantas"],
	 "note": "O Lethe nasceu do pedido de Lena, 'Serioja, lembre de mim'. Sergei tentou preservar a memória dela e criou uma máquina de esquecer. Karpov só a roubou.", "alt": "O Lethe é projeto de Estado, nada mais."},
	{"id": "apagou", "q": "Quem apagou a minha memória, e por quê?", "opts": ["Karpov, para me punir", "Sergei, para me salvar da KGB", "Irina, para me controlar", "Boris, por vingança"], "ok": 1, "n": 3,
	 "need": ["pulso:proto", "porao:venda", "chave:pasta", "arquivos_mortos:ficha", "tabuleiro_sergei:conversa", "museu:conversa"],
	 "note": "Foi Sergei, na noite de 21 de agosto de 1991. Eu vendi as plantas à KGB, ele descobriu e me apagou antes que eles me levassem. Depois a KGB me refez.", "alt": "Fui apagado por inimigos. Não sei de quem."},
	{"id": "irina", "q": "Quem condenou Irina?", "opts": ["Sergei", "Boris", "Karpov", "Eu"], "ok": 2, "n": 2,
	 "need": ["apt_irina:ordem", "lounge:dossie", "apt_irina:conversa", "decreto:conversa", "metro:conversa"],
	 "note": "Karpov assinou a ordem de apagar Irina. Ela me usa para chegar ao Lethe antes de ser apagada por ele.", "alt": "Irina é minha chefe e está bem."},
	{"id": "sergei", "q": "Por que Sergei deixou tudo correr?", "opts": ["Foi traído por Boris", "Quer que eu me lembre sozinho e destruir o Lethe com ele", "Obedece a Karpov", "Quer vender o Lethe"], "ok": 1, "n": 3,
	 "need": ["chave:conversa", "museu:conversa", "tabuleiro_sergei:conversa", "corredor:conversa", "piscar:conversa", "pulso:proto", "gabinete:plantas"],
	 "note": "Sergei me reconheceu no primeiro aperto de mão e nada disse. Quer que eu me lembre por conta própria, e quer acionar o Lethe no laboratório para apagar quem o conhece, ele incluído.", "alt": "Sergei é um velho gentil."},
]
var _vo := Label.new()
var _band := ColorRect.new()   # faixa escura atrás da legenda: lê-se em qualquer cena
var _toast := Label.new()
var _voice := AudioStreamPlayer.new()   # voz das falas "NOME: texto" (art/audio/vo/<sha1>.wav, ver tools/vozes.py)
var _title := Label.new()
var _fade := ColorRect.new()
var _options: PackedStringArray
var _choice := -1   # -2 = esperando resposta
var _cursor := 0
var _advance := false
var _waiting := false


func _ready() -> void:
	layer = 13
	process_mode = Node.PROCESS_MODE_ALWAYS
	_vo.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_WIDE)
	_vo.offset_left = 36.0    # margem: a legenda nunca encosta nas bordas
	_vo.offset_right = -36.0
	_vo.offset_top = -118
	_vo.offset_bottom = -22
	_vo.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_vo.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_vo.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_vo.add_theme_font_size_override("font_size", 11)
	_vo.add_theme_constant_override("line_spacing", 2)
	_vo.add_theme_constant_override("outline_size", 4)
	_vo.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.9))
	_title.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	_title.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_title.add_theme_font_size_override("font_size", 14)
	_title.modulate.a = 0.0
	_fade.color = Color.BLACK
	_fade.modulate.a = 0.0
	_fade.set_anchors_preset(Control.PRESET_FULL_RECT)
	_fade.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_band.color = Color(0, 0, 0, 0.5)
	_band.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	_band.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_band.modulate.a = 0.0
	_toast.set_anchors_and_offsets_preset(Control.PRESET_TOP_RIGHT)
	_toast.offset_left = -90
	_toast.offset_top = 6
	_toast.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	_toast.add_theme_font_size_override("font_size", 8)
	_toast.modulate.a = 0.0
	_voice.bus = "Voice"
	for n in [_band, _vo, _title, _fade, _toast, _voice]:
		add_child(n)
	await get_tree().process_frame # ao abrir uma cena direto (F6), descobre em que ponto da ORDER ela está
	if get_tree().current_scene:
		index = maxi(ORDER.find(get_tree().current_scene.scene_file_path), 0)


func _process(delta: float) -> void:
	var on := _vo.text != ""
	var h: float = _vo.get_line_count() * (_vo.get_line_height() + 2.0)
	var mid := (_vo.offset_top + _vo.offset_bottom) / 2.0
	_band.offset_top = mid - h / 2.0 - 6.0
	_band.offset_bottom = mid + h / 2.0 + 6.0
	_band.modulate.a = lerpf(_band.modulate.a, 1.0 if on else 0.0, 1.0 - exp(-12.0 * delta))


func _unhandled_input(event: InputEvent) -> void:
	if _choice == -2:
		if event is InputEventKey and event.pressed:
			var n: int = event.keycode - KEY_1
			if n >= 0 and n < _options.size():
				_choice = n
				get_viewport().set_input_as_handled()
		if event.is_action_pressed("forward") or event.is_action_pressed("backward"):
			_cursor = posmod(_cursor + (-1 if event.is_action_pressed("forward") else 1), _options.size())
			_render_choice()
		elif event.is_action_pressed("interact"):
			_choice = _cursor
			get_viewport().set_input_as_handled()
	elif _waiting and event.is_action_pressed("interact"):
		_advance = true
		get_viewport().set_input_as_handled()


## Legenda / voz em off por `seconds`.
## Toca a gravação da fala (se existir). Sem arquivo, a fala segue só em texto.
func _vo_play(text: String) -> void:
	var path := "res://art/audio/vo/%s.wav" % text.sha1_text().substr(0, 12)
	if ResourceLoader.exists(path):
		_voice.stop()
		_voice.stream = load(path)
		_voice.play()


func vo_on() -> bool:
	return _voice.playing


func say(text: String, seconds := 4.0) -> void:
	_vo.offset_top = -118.0
	_vo.text = text
	_vo_play(text)
	await get_tree().create_timer(seconds).timeout
	if _vo.text == text:
		_vo.text = ""


## Mostra opções (teclas 1..n, ou cima/baixo + E) e devolve o índice escolhido.
## Com `seconds` > 0 a escolha tem prazo: estourado, vale `default` (padrão: a última opção, o silêncio).
func ask(question: String, options: PackedStringArray, seconds := 0.0, default := -1) -> int:
	_options = options
	_cursor = 0
	_choice = -2
	_question = question
	_left = seconds
	busy = true
	_render_choice()
	while _choice == -2:
		await get_tree().process_frame
		if seconds > 0.0:
			_left -= get_process_delta_time()
			_render_choice()
			if _left <= 0.0:
				_choice = default if default >= 0 else options.size() - 1
	_left = 0.0
	_vo.text = ""
	busy = false
	return _choice


var _question := ""
var _left := 0.0


func _render_choice() -> void:
	var lines := [_question + ("   [%d]" % ceili(maxf(_left, 0.0)) if _left > 0.0 else "")]
	_vo.offset_top = -22.0 - maxf(96.0, (_options.size() + 1) * 15.0 + 12.0)
	for i in _options.size():
		lines.append("%s %d  %s" % ["▸" if i == _cursor else " ", i + 1, _options[i]])
	_vo.text = "\n".join(lines)


## Diálogo: String = fala (E avança); Dictionary {q, opts, truth, trust?, reply?, flag?, seconds?} = escolha;
## {text, when} = fala que só existe se `when` (ver test) for verdadeiro.
func talk(lines: Array) -> void:
	busy = true
	await get_tree().process_frame # o E que abriu a conversa não conta como "avançar"
	for l in lines:
		if l is Dictionary and l.has("q"):
			var i := await ask(l["q"], PackedStringArray(l["opts"]), float(l.get("seconds", 0.0)), int(l.get("default", -1)))
			busy = true
			apply(l, i)
			if l.has("reply"):
				await talk(l["reply"][i])
				busy = true
		else:
			var txt := str(l)
			if l is Dictionary:
				if not test(l.get("when", {})):
					continue
				txt = str(l["text"])
			_vo.text = txt + "  ▸"
			_vo_play(txt)
			_advance = false
			_waiting = true
			while not _advance:
				await get_tree().process_frame
			_waiting = false
			_voice.stop()
	_vo.text = ""
	busy = false


## Efeitos da opção `i` de uma escolha: peso na verdade, confiança de cada personagem e flag.
func apply(l: Dictionary, i: int) -> void:
	if l.has("truth"):
		truth += int(l["truth"][i])
	if l.has("trust"):
		for k in l["trust"]:
			trust[k] = int(trust.get(k, 0)) + int(l["trust"][k][i])
	if l.has("flag"):
		flags[l["flag"]] = (i == int(l["correct"])) if l.has("correct") else i
	if l.has("give") and str(l["give"][i]) != "":
		give(str(l["give"][i]))


## Condição de fala/final: {trust, gte|lt} · {flag, is} · {item}.
func test(c: Dictionary) -> bool:
	if c.has("trust"):
		var v: int = int(trust.get(c["trust"], 0))
		if c.has("gte") and v < int(c["gte"]):
			return false
		if c.has("lt") and v >= int(c["lt"]):
			return false
	if c.has("flag") and bool(flags.get(c["flag"], false)) != bool(c.get("is", true)):
		return false
	if c.has("item") and not items.has(c["item"]):
		return false
	if c.has("ledger_gte") and resolved.size() < int(c["ledger_gte"]):
		return false
	return true


func give(item: String) -> void:
	items[item] = true


func add_note(text: String, alt := "", id := "") -> void:
	notes.append([text, alt, id, index, false])
	note_added.emit(notes.size() - 1)
	for q in LEDGER:                                            # a primeira prova de uma pergunta abre a pergunta no quadro
		if not _seen_q.has(q["id"]) and not resolved.has(q["id"]) and _proofs(q) > 0:
			_seen_q[q["id"]] = true
			_toast.text = "? nova pergunta no quadro  [B]"
			_toast.modulate.a = 0.9
			create_tween().tween_property(_toast, "modulate:a", 0.0, 2.5).set_delay(2.5)


func has_note(id: String) -> bool:
	for n in notes:
		if n.size() > 2 and n[2] == id:
			return true
	return false


## Diário, tecla C: o jogador escolhe quais duas lembranças se encaixam. Acertar vira uma nota nova e pesa na verdade;
## errar não custa nada, mas nada se revela. Entre as certas entram pares falsos feitos só com notas que ele já tem.
func confront() -> void:
	var real: Array = []
	var owned: Array = []
	for d in DEDUCTIONS:
		if has_note(d["a"]):
			owned.append(d["la"])
		if has_note(d["b"]):
			owned.append(d["lb"])
		if has_note(d["a"]) and has_note(d["b"]) and not deduced.has(d["id"]):
			real.append(d)
	if real.is_empty():
		say("Ainda não vejo ligação entre o que anotei.", 3.5)
		return
	var opts: Array = []
	for d in real.slice(0, 3):
		opts.append([d["la"] + "  ×  " + d["lb"], d])
	if owned.size() >= 3:
		var tries := 0
		while opts.size() < real.slice(0, 3).size() + 2 and tries < 20:
			tries += 1
			var a: String = owned.pick_random()
			var b: String = owned.pick_random()
			var key := a + "  ×  " + b
			var dup := a == b
			for o in opts:
				if o[0] == key or o[0] == b + "  ×  " + a:
					dup = true
			for d in DEDUCTIONS:
				if (d["la"] == a and d["lb"] == b) or (d["la"] == b and d["lb"] == a):
					dup = true
			if not dup:
				opts.append([key, null])
	opts.shuffle()
	var names := PackedStringArray()
	for o in opts:
		names.append(o[0])
	names.append("Fechar o diário")
	var c := await ask("Quais duas lembranças se encaixam?", names)
	if c >= opts.size():
		return
	var pick = opts[c][1]
	if pick == null:
		say("Não se encaixam. Alguma coisa me escapa.", 3.5)
		return
	deduced[pick["id"]] = true
	truth += 1
	add_note(pick["note"], pick["alt"], "ded_" + pick["id"])
	fix_notes([pick["a"], pick["b"], "ded_" + pick["id"]])
	Sound.play("pickup", "Sfx", -2.0)
	say("Encaixou. " + str(pick["note"]).split(".")[0] + ".", 5.0)


## Texto da nota como Aleksey a "lembra" agora: quem nega a verdade lê a versão distorcida, e o que não foi confirmado
## (ligado no diário ou provado no quadro) se apaga aos poucos: o Lethe continua trabalhando.
func note_text(i: int) -> String:
	var n: Array = notes[i]
	var t: String = n[1] if truth < 0 and n[1] != "" else n[0]
	if n.size() < 5 or bool(n[4]):
		return t
	var age: int = index - int(n[3])
	if age <= 5:
		return t
	var p := minf(0.05 * (age - 5), 0.45)
	var rng := RandomNumberGenerator.new()
	rng.seed = hash(t) + i
	var out := ""
	for ch in t:
		out += "_" if ch != " " and rng.randf() < p else ch
	return out


func fix_notes(ids: Array) -> void:
	for n in notes:
		if n.size() > 4 and n[2] in ids:
			n[4] = true


func _proofs(q: Dictionary) -> int:
	var c := 0
	for id in q["need"]:
		if has_note(id):
			c += 1
	return c


func is_resolved(id: String) -> bool:
	return resolved.has(id)


## Tecla B: o quadro de evidências. Lista as perguntas abertas; responder certo COM provas as resolve e fixa as notas-prova.
func board() -> void:
	while true:
		var open: Array = []
		for q in LEDGER:
			if not resolved.has(q["id"]) and _proofs(q) > 0:
				open.append(q)
		var names := PackedStringArray()
		for q in open.slice(0, 4):
			names.append("?  " + q["q"])
		names.append("Fechar o quadro   (%d/%d resolvidas)" % [resolved.size(), LEDGER.size()])
		if open.is_empty():
			say("O quadro está vazio. Preciso de mais provas.", 3.5)
			return
		var c := await ask("QUADRO DE EVIDÊNCIAS", names)
		if c >= mini(open.size(), 4):
			return
		var q: Dictionary = open[c]
		var a := await ask(q["q"], PackedStringArray(q["opts"]) + PackedStringArray(["Voltar"]))
		if a >= q["opts"].size():
			continue
		if a == int(q["ok"]) and _proofs(q) >= int(q["n"]):
			resolved[q["id"]] = true
			truth += 2
			fix_notes(q["need"])
			add_note(q["note"], q["alt"], "led_" + q["id"])
			fix_notes(["led_" + q["id"]])
			Sound.play("pickup", "Sfx", -2.0)
			await say("Resolvido. " + str(q["note"]).split(".")[0] + ".", 5.5)
			return
		await say("Não consigo sustentar isso com o que anotei.", 3.5)


## Vai para a próxima cena da ORDER (com fade). Depois da última, mostra a cartela "em construção".
func next_scene() -> void:
	index += 1
	await fade_to(1.0, 1.2)
	if index >= ORDER.size():
		end_game()
		return
	save_game()
	get_tree().change_scene_to_file(ORDER[index])


func reset() -> void:
	truth = 0
	flags = {}
	notes = []
	items = {}
	trust = {"irina": 0, "boris": 0, "sergei": 0}
	deduced = {}
	resolved = {}
	_seen_q = {}
	cp_scene = ""


func new_game() -> void:
	reset()
	index = 0
	get_tree().change_scene_to_file(ORDER[0])


## Fim da história: o save some (o próximo "Novo jogo" começa limpo) e volta ao título.
func end_game() -> void:
	DirAccess.remove_absolute(ProjectSettings.globalize_path(SAVE))
	reset()
	index = 0
	await fade_to(0.0, 0.1)
	get_tree().change_scene_to_file("res://rooms/titulo.tscn")


func has_save() -> bool:
	return FileAccess.file_exists(SAVE)


## Salva ao entrar em cada cena (30 cenas não cabem numa sessão).
func save_game() -> void:
	var tmp := SAVE + ".tmp"                                              # grava ao lado e troca: queda de energia não corrompe o save
	var f := FileAccess.open(tmp, FileAccess.WRITE)
	if f == null:
		return
	f.store_string(JSON.stringify({"version": 1, "index": index, "truth": truth, "flags": flags, "notes": notes, "items": items, "trust": trust, "deduced": deduced, "resolved": resolved, "seen_q": _seen_q}))
	f.close()
	if DirAccess.rename_absolute(ProjectSettings.globalize_path(tmp), ProjectSettings.globalize_path(SAVE)) != OK:
		return
	_toast.text = "● salvo"
	_toast.modulate.a = 0.8
	create_tween().tween_property(_toast, "modulate:a", 0.0, 2.5).set_delay(1.5)


func continue_game() -> void:
	var d = JSON.parse_string(FileAccess.get_file_as_string(SAVE))
	if not d is Dictionary:
		new_game()
		return
	reset()                                                               # campos ausentes (save antigo/incompleto) ficam no padrão
	index = clampi(int(d.get("index", 0)), 0, ORDER.size() - 1)
	truth = int(d.get("truth", 0))
	flags = d.get("flags", {}) if d.get("flags") is Dictionary else {}
	notes = d.get("notes", []) if d.get("notes") is Array else []
	items = d.get("items", {}) if d.get("items") is Dictionary else {}
	var tr = d.get("trust", {})
	if tr is Dictionary:
		for k in tr:
			trust[k] = int(tr[k])
	deduced = d.get("deduced", {}) if d.get("deduced") is Dictionary else {}
	resolved = d.get("resolved", {}) if d.get("resolved") is Dictionary else {}
	_seen_q = d.get("seen_q", {}) if d.get("seen_q") is Dictionary else {}
	get_tree().change_scene_to_file(ORDER[index])


## Ponto de retorno da cena (ao ser flagrado, a cena recomeça sem duplicar notas).
func checkpoint(scene: String) -> void:
	cp_scene = scene
	_cp = {"n": notes.size(), "truth": truth, "flags": flags.duplicate(), "trust": trust.duplicate(), "items": items.duplicate(), "ded": deduced.duplicate(), "res": resolved.duplicate(), "sq": _seen_q.duplicate()}


func rollback() -> void:
	notes.resize(int(_cp["n"]))
	truth = int(_cp["truth"])
	flags = _cp["flags"].duplicate()
	trust = _cp["trust"].duplicate()
	items = _cp["items"].duplicate()
	deduced = _cp["ded"].duplicate()
	resolved = _cp["res"].duplicate()
	_seen_q = _cp["sq"].duplicate()


func fade_to(alpha: float, secs := 0.8) -> void:
	var t := create_tween()
	t.tween_property(_fade, "modulate:a", alpha, secs)
	await t.finished


## Cartela de título (ex.: "T + 0 / O LABORATÓRIO").
func card(when: String, place: String, secs := 3.5) -> void:
	_title.text = "%s\n%s" % [when, place]
	move_child(_title, get_child_count() - 1) # por cima do fade: a cartela aparece mesmo na tela preta
	_title.modulate.a = 1.0
	await get_tree().create_timer(secs).timeout
	create_tween().tween_property(_title, "modulate:a", 0.0, 1.5)
