# Fragments of Memory — Bíblia da história e plano de expansão (30 cenas)

Data: 2026-10-22 · Estado: **rascunho para aprovação** · Engine: Godot 4.6 (projeto atual em `Projetos/GitHub/Fragments-of-Memory`)

## 1. Intenção

Um jogo 3D em primeira pessoa, estética retrô (baixa resolução, dither, post-punk sombrio, sala claustrofóbica, referência: Buckshot Roulette, Return of the Obra Dinn, Signalis), cuja força é a **narrativa**: um homem sem memória reconstrói quem foi, e o jogador descobre, cena a cena, se ele é herói ou vilão. A resposta honesta é: **os dois**.

**Por quê:** o jogo precisa ser lembrado pelo enredo e pelo clima, não pela mecânica. Cada cena é um "fragmento" que muda o sentido dos anteriores.

**Metas**
- 30 cenas, cada uma durável (6–10 min, 2–3 ambientes conectados, vários objetos, 1–2 conversas, ao menos 1 escolha de peso). Duração total prevista: 3 a 5 horas.
- Estrutura de Memento: duas linhas que se alternam e convergem (ver §4).
- Segredo por baixo do segredo (§2), pistas obrigatórias, diário que a mente de Aleksey reescreve, 6 finais.
- Ancoragem histórica: Moscou, outubro de 1993.

**Não-metas:** combate, inventário complexo, mundo aberto, dublagem profissional (nesta fase), múltiplos idiomas.

**Anti-metas (seria fracasso mesmo funcionando):** cenas que são só "salas com bilhetes"; diálogos que explicam o twist em vez de deixar o jogador deduzir; escolhas que não mudam nada de verdade; finais que dizem ao jogador se ele "acertou".

## 2. Premissa e reviravoltas

**Moscou, noite de 3 para 4 de outubro de 1993** (T = 0). O Parlamento está cercado, tanques nas ruas, rádio e TV ao fundo. No laboratório do instituto Kosmos, **Aleksey Petrov** acorda ao lado do corpo do cientista **Sergei Morozov**, com uma arma quente na mão e nenhuma memória.

**Verdade (o que o jogador deduz ao longo do jogo)**
1. O **Lethe** não é um míssil. É um pulso que apaga a memória de tudo num raio de quilômetros: plantas, cientistas, espiões. **Quem o aciona esquece primeiro.** Nasceu quando Sergei tentava preservar a memória da esposa, **Lena**, que perdia a dela.
2. **Aleksey Petrov não existe.** É **Mikhail "Misha" Volkov**, físico, antigo protegido e melhor amigo de Sergei, coautor do Lethe. Em 1991 vendeu o projeto à KGB por ambição. Sergei, descobrindo, apagou a memória dele com o protótipo para salvá-lo da KGB. A KGB recolheu o homem apagado e o reconstruiu como agente: rosto refeito, nome novo.
3. **Boris Volkov**, chefe de segurança do Kosmos, é o **irmão mais velho** de Misha. Procura o irmão desde 1991 e suspeita do consultor novo ("mesmo jeito de andar", assobia a mesma canção). Aleksey o incrimina sem saber que destrói o próprio irmão.
4. **Irina Sokolova**, a controladora, foi **amante de Misha** antes do apagamento. Mantém Aleksey porque não consegue largá-lo, e teme que ele lembre e descubra que ela o entregou. Também está sendo purgada pelo **General Karpov** (voz, nunca visto), que quer o Lethe como arma política: apagar a memória dos defensores do Parlamento.
5. **Sergei sabe quem é Aleksey desde o primeiro aperto de mão** e deixa a história correr: se Misha recuperar a memória por conta própria e escolher o certo, ele se salva. Seu plano real é destruir o conhecimento do Lethe acionando-o no laboratório (apagando todos que o conhecem, ele incluído). Precisa que alguém aperte o botão. Quando Aleksey atira nele, a bala acerta o console: o pulso dispara. O tiro é o acidente que completa o plano.
6. A amnésia da cena inicial é o Lethe funcionando. E o diário escrito por Aleksey (a letra dele) é o que o jogador está lendo.

**Regras temáticas**
- O jogador **não muda o passado**, só como Aleksey se lembra dele. Escolhas alteram a "verdade" (`Game.truth`), não os fatos.
- Esquecimento como **memória coletiva**: um país que prefere esquecer o passado soviético.
- Memória como **ferramenta de poder** (Karpov) e como **cuidado** (Sergei/Lena).

## 3. Personagens

| Personagem | Papel | Segredo / arco |
|---|---|---|
| **Aleksey Petrov / Mikhail "Misha" Volkov** (protagonista) | Agente que não sabe que é ex-cientista. Ambicioso, frio por fora, carente por dentro. | Mesmo traço ambicioso de antes: o apagamento não o tornou mau, só tirou o que o freava. |
| **Sergei Ivanovich Morozov** (1938–1993) | Criador do Lethe. Gentil, cansado, joga xadrez. | Penitência: apagou Misha para salvá-lo. Plano de sacrifício. |
| **Boris Volkov** | Chefe de segurança. Gruff, bebe, honesto. | Irmão de Misha. Quer proteger Sergei e achar o irmão. Incriminado por ele. |
| **Irina Sokolova** | Controladora da KGB. | Amou Misha; entregou-o. Teme ser apagada pelo Karpov. |
| **Lena Morozova** (1941–1992) | Esposa de Sergei, vive só em fitas e fotos. | Origem do Lethe. Fita onde ela pede: "Serioja, lembre de mim." |
| **General Karpov** (voz) | Antagonista. | Quer o Lethe como arma política. Controla o intermediário. |
| **Intermediário** (voz no telefone) | Comprador do "mercado negro". | Na verdade é homem do Karpov. |

## 4. Estrutura: duas linhas que convergem

- **Linha A (fria, azulada):** anda **para trás** a partir de T+0. Cenas de 1993, últimas semanas. Protagonista: Aleksey.
- **Linha F (quente, âmbar):** anda **para frente** a partir de 1991. As primeiras cenas mostram "Misha" (o jogador deduz que é Aleksey no meio do jogo). Protagonista: Misha, depois Aleksey.
- Elas se **alternam** e se encontram. A cena 30, **O Tiro** (T = 0), fecha as duas.
- Cada cena termina num **gatilho**: um objeto cuja interação lança o jogador na próxima memória (cartão, código, fotografia, fita). Esse objeto reaparece no começo da cena seguinte.

## 5. As 30 cenas (ordem de jogo)

Duração-alvo de cada cena: 6–10 min. Cada uma tem 2–3 ambientes, 6–10 objetos, 1–2 conversas, ao menos 1 escolha de peso. "Revela" = o que o jogador passa a poder deduzir.

### Ato I — O despertar (1–8)
1. **A1 · O Laboratório · T+0.** Aleksey acorda ao lado do corpo. *(existe; expandir para 3 ambientes: laboratório, sala de controle do pulso, corredor.)* Revela: um tiro, calma no rosto de Sergei, míssil "sabotado".
2. **F1 · A Cozinha dos Volkov · jun/1991.** Misha e Boris, jantar. Boris desconfia das reuniões secretas do irmão. Pai ensinava xadrez; Boris dá a Misha o **peão branco**. Escolha: mentir ou contar a Boris sobre a KGB. *Revela: Misha existe; ele e Boris são irmãos (sem o jogador saber o nome ainda).*
3. **A2 · Os Arquivos · −30 min.** *(existe; expandir: arquivos, sala do servidor, gaveta trancada.)* Log de Boris (falso). Revela: diário do técnico que é de Boris.
4. **F2 · A Sala do Protótipo · jul/1991.** Misha e Sergei criando o Lethe. Lena aparece doente; Sergei explica por quê. Revela: origem do Lethe.
5. **A3 · O Gabinete · −2h30.** *(existe; expandir.)* Sergei dá o código 4-8-2-1 e fala do "peão". Revela: ele sabe quem é Aleksey.
6. **F3 · O Golpe · 19/ago/1991.** Noite do golpe de Estado, tanques em Moscou. Irina recruta Misha; ele vende as plantas. Escolha: vender ou recusar (o fato acontece igual; muda o que Misha sente). Revela: o pecado original.
7. **A4 · O Quarto de Lena · −6h.** Casa de Sergei. Fitas cassete de Lena. A voz dela: "Serioja, lembre de mim." Revela: o coração do Lethe.
8. **F4 · O Pulso · 21/ago/1991.** Sergei descobre a venda. A KGB vai prendê-lo. Sergei aciona o protótipo em Misha. O jogador vive o apagamento. Revela: o Lethe já foi usado nele.

### Ato II — O disfarce (9–16)
9. **A5 · As Ruas do Parlamento · −10h.** Moscou em chamas, Irina: "Hoje à noite acabamos." Revela: pressão de Karpov.
10. **F5 · A Clínica · set/1991.** Misha acorda, rosto enfaixado. Irina lhe dá o nome **Aleksey Petrov**. Escolha: aceitar o nome. **A identidade fica clara para o jogador.**
11. **A6 · A Sala de Controle · −1 dia.** *(existe; expandir.)* Aleksey forja o acesso de Boris. Boris dorme sobre a foto do irmão.
12. **F6 · O Treinador · 1992.** Dois anos de treino. O diário nasce ("escreva tudo"). Aleksey joga xadrez perfeito sem saber por quê.
13. **A7 · O Telhado · −2 dias.** *(existe; expandir.)* O pacto com o intermediário.
14. **F7 · O Cemitério · mar/1992.** Funeral de Lena. Aleksey observa de longe. Boris está lá e o encara: "mesmo jeito de andar". Escolha: aproximar-se ou virar as costas.
15. **A8 · A Noite da Chave · −3 dias.** *(existe como F; passa para A.)* Sergei mostra o Lethe e diz: "Eu sei quem você é."
16. **F8 · O Parque Gorky · ago/1993.** *(existe.)* Irina entrega a missão: infiltrar a Kosmos.

### Ato III — A amizade como armadilha (17–24)
17. **A9 · O Apartamento de Irina · −4 dias.** Ela pede ajuda; foi marcada para apagamento. Cena de intimidade e ameaça.
18. **F9 · O Museu Desativado · ago/1993.** *(existe.)* Primeiro aperto de mão. Sergei devolve o peão: ele reconhece Misha.
19. **A10 · O Interrogatório de Boris · −6 dias.** Boris conduz Aleksey a uma sala de interrogatório e testa o assobio, o jeito de andar.
20. **F10 · A Entrevista de Segurança · ago/1993.** Boris contrata Aleksey sem saber; quase reconhece.
21. **A11 · Os Arquivos Mortos · −8 dias.** Aleksey encontra a ficha **MIKHAIL VOLKOV**. Gatilho visual: a memória "pisca".
22. **F11 · O Lounge · set/1993.** *(existe.)* O dossiê e a nota cínica.
23. **A12 · O Metrô · −10 dias.** *(existe.)* Irina: 48 horas.
24. **F12 · O Tabuleiro · set/1993.** Partida de xadrez com Sergei, **mini-puzzle**: a abertura que o pai ensinou. Se o jogador acerta, Aleksey fala "Misha" sem querer.

### Ato IV — Convergência (25–30)
25. **A13 · O Decreto · −12 dias.** 21/set/1993: o decreto de Yeltsin na TV da cantina. Karpov aperta Irina.
26. **F13 · O Apartamento de Boris · set/1993.** Aleksey vigia Boris, vê a foto dos dois irmãos. Primeiro lampejo de memória (um segundo, sem som).
27. **A14 · O Corredor · −13 dias.** Sergei finge não ter ouvido "Misha".
28. **F14 · O Telefone Vermelho · −15 dias.** Aleksey liga para Irina: "Estou começando a lembrar." Ela responde com medo.
29. **F15 · O Piscar · −14 dias.** Aleksey recupera a memória por dez segundos no corredor, diz seu nome verdadeiro, esquece de novo. Sergei viu.
30. **O Tiro · T = 0.** O laboratório. Sergei, Karpov ao telefone, Boris à porta, Irina em segundo plano. O tiro, o pulso, a escolha final.

*(A ordem exata e os títulos dos Atos podem ser ajustados; a regra é: A andando para trás, F para frente, alternando e fechando em O Tiro.)*

## 6. Mecânicas de jogo

- **Pistas obrigatórias**: toda cena exige examinar todas as pistas antes do gatilho.
- **Escolhas** com peso em `Game.truth` e em **flags** nomeadas; respostas e consequências nas falas seguintes.
- **Diário que se reescreve**: se `truth < 0`, as notas mostram a versão distorcida (já implementado).
- **Confronto de notas (novo)**: o jogador pode abrir o diário e **escolher duas notas que se contradizem**; acertar revela um fragmento (ex.: "o log de Boris é forjado") e aumenta `truth`.
- **Itens que viajam (novo)**: peão, rolos de filme, foto rasgada, fita da Lena, isqueiro de Boris. Cada item muda de significado conforme a cena e é usado no final.
- **Mini-puzzles (novo)**: partida de xadrez (cena 24), cofre 4-8-2-1, montagem da foto.
- **Fragmentos escondidos (novo)**: 1 por cena (letras do nome **MIKHAIL VOLKOV**); coletar todos abre um final.
- **Ambiente vivo**: rádio e TV de 1993 ao fundo, trilha por cena, passos, rangidos.

## 7. Finais (6)

1. **Confissão** — lembrar + aceitar a verdade.
2. **O Herói Falso** — lembrar, mas negar a verdade.
3. **O Presente** — esquecer + aceitar.
4. **O Esquecido** — esquecer + negar.
5. **O Irmão** *(oculto)* — todos os fragmentos + foto: Boris o reconhece.
6. **A Última Partida** *(oculto)* — vencer o puzzle de xadrez e, no final, apertar o botão por vontade própria: o Lethe apaga todos, e o mundo esquece.

Em todos, a mensagem final é: herói ou vilão? Os dois.

## 8. Impacto técnico (resumo; o plano detalhado virá depois)

- **Ambientes múltiplos por cena** (portas liberadas por pistas). `memory.gd` passa a montar vários cômodos a partir de `story.gd`.
- **Estado persistente**: `Game.items`, flags, fragmentos; **salvar/continuar** (30 cenas não cabem numa sessão).
- **Tela de diário interativa** com seleção de notas e confronto.
- **Puzzle de xadrez** (cena 24) e cofre (código).
- **Áudio**: trilha por cena, rádio de 1993, passos. Começar com síntese procedural; trilha de verdade quando você quiser.
- **Dados**: `story.gd` passa de 1 arquivo para 1 arquivo por ato (`story_act1.gd` …), por tamanho.
- **Ferramentas**: manter o robô de teste que joga o jogo inteiro e o gerador de capturas.

## 9. Produção

Entrega por **atos**, cada um jogável e revisável antes de seguir:
- **Ato I** primeiro (cenas 1–8): inclui o motor novo (cômodos, itens, save, diário interativo).
- Depois Ato II, III, IV. Em cada ato: escrever → construir → testar com o robô → capturar → revisar com você.

## 10. Decisões que tomei sozinho (marcadas como minhas)

- "Durável" = 6–10 min por cena, 3–5 h no total.
- Ambientação em **outubro de 1993**, com eventos reais ao fundo (decreto 1400, cerco do Parlamento).
- Boris é irmão de Misha; Irina foi amante dele; Karpov é o antagonista; Lena é a origem do Lethe.
- A linha F mostra "Misha" nas primeiras cenas; a identidade se confirma na cena 10.
- Seis finais, dois deles ocultos.
- Sem dublagem nesta fase; falas em texto e voz em off por legenda.

## 11. Para você decidir

- Aceita as **reviravoltas** do §2 (Aleksey = Misha; Boris irmão; Irina amante; Sergei apagou Misha para salvá-lo)?
- Quer que o **Karpov** apareça em carne e osso no final, ou fique só como voz?
- **Ritmo:** prefere cenas de 6 min (mais ágeis) ou 10 min (mais imersivas)?
