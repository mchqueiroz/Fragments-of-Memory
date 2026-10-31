#!/usr/bin/env bash
# Roda os testes automáticos e sai com código 1 se algum falhar. Usado no CI (.github/workflows/ci.yml).
# Uso: tools/testes.sh [caminho_do_godot]
set -u
GODOT="${1:-${GODOT:-godot}}"
cd "$(dirname "$0")/.."
falhas=0

roda() {  # nome, texto que precisa aparecer, script, args...
	local nome="$1" ok="$2"; shift 2
	local out
	out="$("$GODOT" --headless --path . --script "$@" 2>&1)"
	if grep -qE "SCRIPT ERROR|TRAVADA|Assertion failed" <<<"$out" || ! grep -qF "$ok" <<<"$out"; then
		echo "FALHOU: $nome"
		grep -E "SCRIPT ERROR|TRAVADA|Assertion|^\[|   at:" <<<"$out" | tail -30
		falhas=$((falhas + 1))
	else
		echo "ok: $nome"
	fi
}

"$GODOT" --headless --path . --import >/dev/null 2>&1
roda "save" "SAVE OK" res://tools/teste_save.gd
roda "quadro" "3 provas: resolvida=true notas=4" res://tools/teste_quadro.gd
roda "partida completa" "FIM: a história chegou aos créditos" res://tools/robo.gd -- res://rooms/laboratorio.tscn 99
exit $((falhas > 0))
