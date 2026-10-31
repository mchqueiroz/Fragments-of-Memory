# Fragments of Memory

> Moscou, noite de 3 para 4 de outubro de 1993. O Parlamento está cercado, há tanques nas ruas.
> No laboratório do instituto Kosmos, um homem acorda ao lado de um cadáver, com uma arma quente na mão
> e nenhuma memória. O diário no bolso diz que o nome dele é Aleksey Petrov.

Jogo narrativo de investigação em primeira pessoa, 3D em baixa resolução, feito em **Godot 4.6**.
Não há combate: você examina objetos, conversa, escolhe e, no **quadro de evidências**, liga as provas
até entender quem foi o homem que acordou no laboratório. A história anda em duas linhas que se alternam
e convergem no tiro da cena final:

- **Linha A (fria, azulada)** — 1993, andando **para trás** a partir do despertar.
- **Linha F (quente, âmbar)** — 1991 em diante, andando **para frente**.

São 28 cenas jogáveis em quatro atos, de 3 a 5 horas, e quatro finais que dependem do que você descobriu
e de como escolheu lembrar. O jogo não diz se você acertou.

## Como jogar

Executáveis prontos para Linux e Windows ficam em [Releases](https://github.com/mchqueiroz/Fragments-of-Memory/releases).
Para rodar a partir do código, use o [Godot 4.6](https://godotengine.org/download/) (versão padrão, não a .NET).

```sh
git clone https://github.com/mchqueiroz/Fragments-of-Memory.git
cd Fragments-of-Memory
godot --path .            # ou abra o project.godot no editor e aperte F5
```

Para gerar executáveis (precisa dos *export templates* do Godot 4.6 instalados):

```sh
godot --headless --path . --export-release "Linux"   build/linux/FragmentsOfMemory.x86_64
godot --headless --path . --export-release "Windows" build/windows/FragmentsOfMemory.exe
```

O jogo salva sozinho ao entrar em cada cena; **Continuar** na tela de título retoma dali.
Ao terminar a história, o save é apagado e o próximo **Novo jogo** começa limpo.

### Controles

| Ação | Teclado / mouse | Controle |
|---|---|---|
| Andar | W A S D | analógico esquerdo |
| Olhar | mouse | analógico direito |
| Correr / agachar | Shift / Ctrl ou C | L3 / B |
| Examinar, falar, avançar fala | E | A |
| Isqueiro | F | Y |
| Diário | Tab | Back |
| Ligar notas do diário | G | RB |
| Quadro de evidências | B | LB |
| Soltar a arma | Q | X |
| Escolhas | 1–9, ou W/S e E | analógico e A |
| Pausa / opções | Esc | |
| Tela cheia | F11 | |

### Opções

Na pausa ou em **Opções**, na tela de título: sensibilidade, eixo Y invertido, balanço da câmera (pode ser desligado
para quem enjoa), campo de visão, legendas grandes, **qualidade gráfica**, tela cheia, sincronia vertical e volumes separados (geral,
música, efeitos, vozes). Tudo fica salvo em `user://settings.cfg`.

| Qualidade | Sombras | Oclusão (SSAO) | Névoa |
|---|---|---|---|
| Alta | 2 luzes principais | sim | volumétrica |
| Média | 1 luz principal | não | volumétrica |
| Baixa | nenhuma | não | simples |

Na Alta, quase todas as cenas mantêm 60 fps numa GPU integrada (AMD Lucienne); o quadro mais lento medido foi de 20 ms.

### Mecânicas

- **Diário** — tudo o que Aleksey vê vira nota, na letra dele. Notas que não provam nada vão se
  apagando e podem voltar distorcidas: a memória dele reescreve o que não foi fixado.
- **Quadro de evidências (B)** — cada pergunta só se resolve com as notas certas. Resolver fixa as
  provas e aproxima Aleksey da verdade; algumas escolhas só aparecem depois de certas perguntas resolvidas.
- **Confiança** — Irina, Boris e Sergei lembram como você os tratou; isso muda falas e o desfecho.
- **Furtividade** — em algumas cenas, ser visto faz a cena recomeçar do último ponto seguro.

## Estrutura do projeto

```
game/          núcleo: Story (história, save, diário, quadro), jogador, som, menus
rooms/         cenas. As 11 primeiras têm script próprio (*.gd); as demais (ep_*.tscn) usam rooms/episodio.gd
rooms/data/    especificação gerada de cada cena (pistas, NPCs, escolhas, finais)
rooms/text/    textos revisados que sobrepõem os de rooms/data
art/           modelos .glb, texturas, áudio
tools/         geradores (Blender/Python) e robôs de teste
docs/          bíblia da história, benchmark, créditos
```

A ordem das cenas fica em `Story.ORDER` (`game/story.gd`).

### Regerar as cenas por especificação

As cenas `ep_*` vêm de especificações em Python (`tools/ep/act2.py`, `act3.py`, `act4.py`):

```sh
blender -b -P tools/episodios.py -- tiro metro    # regera modelo, JSON e .tscn só dessas cenas
python3 tools/textos.py                           # regrava os textos revisados (rooms/text)
```

### Testes

Um robô joga o jogo sozinho, examina todas as pistas, escolhe e avança; avisa se alguma cena travar.
`tools/testes.sh` roda tudo e sai com erro se algo falhar. O CI do GitHub roda esse script a cada push e,
numa tag `v*`, gera os executáveis e publica a Release com o texto do [CHANGELOG](CHANGELOG.md).

```sh
tools/testes.sh ~/caminho/do/godot                                # save, quadro e a partida completa até os créditos
godot --headless --path . --script res://tools/robo.gd -- res://rooms/laboratorio.tscn 40
godot --headless --path . --script res://tools/teste_quadro.gd
godot --headless --path . --script res://tools/teste_save.gd        # save atômico, save antigo e corrompido
godot --path . --script res://tools/desempenho.gd                   # ms por quadro e draw calls de cada cena (QUALIDADE=0|1|2)
```

### Auditoria de posições

Os cômodos são montados por código, então um número errado vira objeto flutuando ou atravessando outro.
Três verificações pegam isso:

```sh
# 1. Geometria do Blender: objetos flutuando, atravessando outros ou furando piso/teto (relatório em /tmp/aud)
AUDIT=/tmp/aud blender -b -P tools/episodios.py          # ou tools/cozinha.py, tools/lab.py ...
# 2. Godot: personagens dentro de móveis/paredes e modelos avulsos (xadrez, plantas) fora do apoio
DUMP=/tmp/extra.json godot --headless --path . --script res://tools/teste_posicoes.gd
# 3. Primitivas criadas no Godot (exteriores: multidões, bancos, roda-gigante)
python3 tools/auditoria_godot.py /tmp/extra.json /tmp/aud
```

Com `AUDIT_EXTRA=/tmp/extra.json`, o passo 1 também testa os personagens e modelos posicionados no Godot
contra a geometria real dos cômodos. Para revisar no olho, `tools/fotos.gd` fotografa cada cena em quatro direções
e faz um retrato de cada personagem (precisa de janela).

## Créditos

Criação, roteiro e código: **Michael Queiroz**. O exterior do Kosmos é o modelo brutalista feito à mão
pelo autor. Música, efeitos e a maior parte das vozes são sintetizados por código próprio; as vozes russas
reais vêm do LibriVox (domínio público). Detalhes e licenças em [docs/CREDITS.md](docs/CREDITS.md).

Código sob licença [MIT](LICENSE).
