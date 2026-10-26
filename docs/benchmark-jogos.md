# Benchmark: jogos de sucesso no nicho de Fragments of Memory

Data: 2026-10-23. Nicho: narrativa em primeira pessoa, investigação, memória, retrô sombrio.
Fontes: busca na web (links no fim) para o que está citado; onde escrevi "(minha leitura)" é opinião minha, não dado das fontes.
Limite honesto: a busca devolveu pouco sobre Gone Home, Papers Please (fora de análises acadêmicas), Control e SOMA; essas linhas pesam menos.

## 1. O que cada referência ensina

| Jogo | Loop central | O que o fez dar certo | Lição para Fragments |
|---|---|---|---|
| **Return of the Obra Dinn** | Rever a morte congelada de cada tripulante e **deduzir** nome, causa e culpado num caderno | Grande Prêmio e prêmio de narrativa no IGF; puzzle de dedução + estilo visual 1-bit como parte do design. Críticas: identificar tudo fica trabalhoso; o protótipo "não escalou" para o jogo completo | O diário deve ser a mecânica, não um mural de notas. Cuidado com escopo: 60 mortes por 1 pessoa foi o limite |
| **Her Story / Telling Lies / Immortality** (Sam Barlow) | Buscar e comparar trechos de vídeo; o vídeo é a fase | Mecânica simples que ganha profundidade; omite as perguntas da polícia, e o jogador infere; confiança na não linearidade. Crítica: não linearidade traz problemas de ritmo | Esconder o que o jogador pode deduzir. Deixar a ordem da descoberta variar |
| **Gone Home / Edith Finch / Firewatch** | Andar e examinar espaços de uma casa ou floresta | Sem urgência, espaço para reflexão; a arquitetura conduz o ritmo; o jogador monta a história com pistas (Gone Home) em vez de assistir a eventos (Firewatch). Críticas: pouca interação, sensação de ser conduzido; Firewatch vive de voz e roteiro | Nossa base atual é esta. Funciona quando cada espaço conta uma história própria, e não quando é uma lista de 5 itens |
| **Outer Wilds** | Explorar um sistema em loop; progresso só por conhecimento | Sem inventário nem portões por item; informação é a moeda; o diário de bordo guarda o saber e o progresso fica na cabeça do jogador | Trocar itens por saber: o código 4-8-2-1 deve ser deduzido, não entregue |
| **Papers, Please** | Aplicar regras de fronteira sob pressão | Regras que apertam a cada dia; erro custa comida da família; dilema vem do sistema, não de cena roteirizada | Escolhas morais por restrição e custo (tempo, confiança), não por menu de 2 opções |
| **Disco Elysium** | Diálogo como combate; identidade como mecânica | Decisões com peso comparável, narrativa coerente em qualquer jogada; a filosofia do personagem está no texto | Escolhas devem mudar a leitura do mundo, e a amnésia pode ser o sistema de habilidades |
| **Signalis** | Exploração de survival horror com lore fragmentado | Atmosfera e estética PS1 elogiadas; narrativa fraturada em cronologia e entrega. Críticas: inventário e combate; coesão da história divide a crítica | Nossa estética retrô é um ativo. Inventário complicado é um risco (mantivemos mínimo) |
| **Vanishing of Ethan Carter** | Investigação aberta com visões | Metascore 82; não conduz o jogador. Críticas: "walking simulator", aviso inicial arrogante, retorno obrigatório sem aviso | Não fechar o jogador numa cena sem dizer o que falta (nosso contador resolve) |
| **Mouthwashing** (Steam, nota alta na lista consultada) | Narrativa curta e sombria, tempo embaralhado | Alta avaliação de jogadores num formato curto | (minha leitura) Curto e denso vence longo e uniforme |

## 2. Onde Fragments está hoje contra o nicho

| Critério dos melhores | Fragments hoje | Situação |
|---|---|---|
| Mecânica central própria (dedução, busca, loop) | Examinar pistas; dedução por ligação de notas (recém-criada, 9 ligações) | Fraco, mas com semente |
| Densidade de cada espaço | 20 das 30 cenas seguem o mesmo molde de 4 a 5 pistas | Fraco |
| Saber como progresso (Outer Wilds) | Itens simples; códigos entregues pelo texto | Médio |
| Pressão e custo (Papers, Please) | Prazos em algumas cenas, furtivo em 3, confiança em 3 personagens | Médio, recém-criado |
| Identidade visual e som | Pós-processo retrô, grão, som em camadas | Forte |
| Voz e performance (Firewatch) | Legendas e voz sintética em sílabas | Fraco |
| Duração por cena e escopo | 30 cenas, ~3-5 h planejadas | Risco (lição do Obra Dinn: protótipo não escalou) |
| Diário como centro | Painel de notas com distorção por `truth` | Médio |

## 3. Direções possíveis (você tem liberdade para mudar tudo)

**A. Fragments como jogo de dedução (recomendo).** O diário vira um **quadro de evidências**: pessoas, eventos e datas a preencher (como o caderno do Obra Dinn). Cada cena é um "fragmento" curto (5 a 8 min) com 3 a 4 pistas **densas**; o objetivo da cena é confirmar uma afirmação do quadro, não "examinar tudo". O código do cofre, a identidade de Misha, quem forjou o log: tudo deduzido. A amnésia vira regra: notas **degradam** com o tempo (o Lethe), e confrontar duas notas as fixa.
- Porque: mecânica própria, reaproveita o diário, as ligações (tecla G), a confiança e o pipeline de cenas.
- Custo: reescrever o diário e o formato de cena; reduzir clues por cena e aumentar a densidade.

**B. Fragments como thriller de pressão e diálogo (Papers, Please + Disco Elysium).** Poucas cenas longas de conversa com tempo, suspeita e regras que apertam; o resto é exploração leve.
- Porque: dá custo real às escolhas.
- Risco: exige muito mais escrita de diálogo e um sistema de diálogo robusto.

**C. Manter o walking sim e só polir (Gone Home).** Menos mudança, menos risco, mas o jogo continua "só procurar".

**Recomendação: A, com elementos de B nas 5 cenas de Boris, Sergei e Irina.** (minha leitura) É o que resolve "só procurar a sala" sem jogar fora o trabalho de arte e som.

## 4. O que mudaria em A, em ordem

1. Cortar a lista: 30 cenas para ~18 fragmentos densos, fundindo as cenas que repetem o mesmo beat (várias de Boris e Irina).
2. Quadro de evidências no lugar do diário linear (pessoas × eventos × datas), com a dedução como ação principal.
3. Cada cena com uma pergunta ("Quem forjou o log?"), 3 a 4 pistas, e uma pista **que só faz sentido com um fato de outra cena** (conhecimento como chave).
4. Degradação de notas e custo de tempo (o Lethe como relógio global).
5. Voz: decidir entre gravar vozes, usar síntese melhor ou texto mais enxuto; hoje é o ponto fraco frente a Firewatch.
6. Teste com jogadores reais em 2 cenas antes de escalar (lição do Obra Dinn: protótipo não escalou).

## 5. Fontes

- [Return of the Obra Dinn (Wikipedia)](https://en.wikipedia.org/wiki/Return_of_the_Obra_Dinn) · [Emily Short](https://emshort.blog/2019/06/06/return-of-the-obra-dinn-lucas-pope/) · [Inverse, retrospectiva](https://inverse.com/gaming/return-of-the-obra-dinn-fifth-anniversary-retrospective)
- [Her Story (Wikipedia)](https://en.wikipedia.org/wiki/Her_Story_(video_game)) · [Destructoid, Sam Barlow](https://destructoid.com/?p=242054) · [PC Gamer, Her Story](https://pcgamer.com/the-story-behind-her-story/3) · [Immortality, AV Club](https://www.avclub.com/immortality-game-review)
- [Edith Finch, pacing e agência](https://mechanicsofmagic.com/2026/04/24/what-remains-of-edith-finch-critical-play-walking-simulators/) · [Firewatch, PC Gamer](https://pcgamer.com/firewatch-review) · [Quarter to Three, Firewatch vs Gone Home](https://www.quartertothree.com/fp/?p=37992)
- [Outer Wilds, Scientific Gamer](https://scientificgamer.com/thoughts-outer-wilds) · [Gamingtrend](https://gamingtrend.com/reviews/little-big-universe-outer-wilds-review)
- [Papers, Please (Wikipedia)](https://en.wikipedia.org/wiki/Papers,_Please) · [Morrissette, Game Studies](https://gamestudies.org/1701/articles/morrissette)
- [Disco Elysium, Reverse Shot](https://reverseshot.org/features/2788/righteous_skills) · [Post45](https://post45.org/?p=23224)
- [Signalis, God Is A Geek](https://godisageek.com/reviews/signalis-review/) · [The Sixth Axis](https://www.thesixthaxis.com/2022/11/04/signalis-review/)
- [Vanishing of Ethan Carter, GameSpot](https://gamespot.com/games/the-vanishing-of-ethan-carter/reviews/) · [Keengamer](https://www.keengamer.com/articles/reviews/the-vanishing-of-ethan-carter-review/)
- [wasdland, lista de mistério](https://www.wasdland.com/games/mystery/?page=2)
