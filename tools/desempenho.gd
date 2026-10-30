extends SceneTree
## Desempenho por cena: média e pior quadro (ms) girando a câmera 360°, chamadas de desenho e memória de vídeo.
## Uso: godot --path . --script res://tools/desempenho.gd   (precisa de janela; vsync desligado durante a medição)

func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	await process_frame
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)    # depois de Settings aplicar as preferências
	var q := OS.get_environment("QUALIDADE")
	if q != "":
		root.get_node("Settings").quality = int(q)
	var worst := 0.0
	for path in root.get_node("Story").ORDER:
		change_scene_to_file(path)
		for i in 120:
			await process_frame
		var p = current_scene.get("player")
		var ts: Array[float] = []
		var calls := 0
		for i in 240:
			if p:
				p.rotation.y += TAU / 240.0
			var t0 := Time.get_ticks_usec()
			await process_frame
			ts.append((Time.get_ticks_usec() - t0) / 1000.0)
			calls = maxi(calls, int(Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME)))
		ts.sort()
		var avg: float = ts.reduce(func(a, b): return a + b, 0.0) / ts.size()
		var p99: float = ts[int(ts.size() * 0.99)]
		worst = maxf(worst, p99)
		print("DESEMP %-28s média %5.2f ms  p99 %5.2f ms  draw calls %4d  vram %d MB" % [str(path).get_file(), avg, p99, calls,
				int(Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED) / 1048576)])
	print("PIOR p99 %.2f ms" % worst)
	quit()
