"""Gera rooms/text/<cena>.json: a camada de textos e mecânicas das cenas 11–30 (sobrepõe o JSON do gerador; ver Episodio._overlay).
Regra de escrita: Aleksey só diz o que viu ou suspeita naquele ponto; conclusões vêm dos flashes e das ligações do diário (tecla G).
Uso: python3 tools/textos.py"""
import json, os

OUT = os.path.join(os.path.dirname(__file__), "..", "rooms", "text")
T = {}

# ---- 11 · A6 · T−1 dia ----------------------------------------------------------------------------------------------------------------
T["sala_controle"] = {
    "watch": {"npc": "boris", "radius": 3.4, "limit": 1.4, "warn": "Boris se mexeu na cadeira. Devagar.", "fail": "Boris abriu os olhos. Recomeço, sem correr."},
    "clues": {
        "terminal": {"note": "Terminal do pulso. Pede uma credencial. A de Boris está no crachá dele, sobre a mesa.", "say": "Daqui se dispara tudo. E daqui se pode culpar qualquer um."},
        "cracha": {"note": "Crachá de Boris: «Волков Б. И.». Ele dorme com a credencial no pescoço.", "say": "A credencial dele, ao alcance de uma mão que não é a dele."},
        "foto": {"note": "Foto desbotada de dois garotos na neve: o mais velho com a mão no ombro do menor. Boris dorme com a mão sobre ela.",
                 "say": "Dois garotos na neve. Ele a segura até dormindo."},
        "camlog": {"note": "Log das câmeras do corredor, programado para amanhã: 23h15, apagamento por «B.V.». O nome de Boris ainda nem foi usado.",
                   "say": "Amanhã, 23h15. O culpado já tem iniciais."},
        "janela": {"note": "Pela janela: o hangar. Sob uma lona, o corpo comprido do Lethe.", "say": "A lona esconde o que ninguém devia ver."},
    },
}

# ---- 12 · F6 · 1992 -------------------------------------------------------------------------------------------------------------------
T["treinador"] = {
    "clues": {
        "tabuleiro": {"note": "O treinador deixou uma abertura no tabuleiro. Minhas mãos jogam como se já tivessem jogado a vida inteira.", "say": "Jogo sem pensar. Isso devia me assustar."},
        "cartilha": {"note": "Cartilha: «Aleksey Ivanovich Petrov, nascido em 1958, filho de professores, técnico em eletrônica». Releio até soar como memória.",
                     "say": "Decoro a vida que me contam. Ainda não soa como minha."},
        "caderno": {"note": "Caderno novo de capa preta. O treinador mandou: «Escreva tudo. Quem escreve, existe.»", "say": "Primeira página: a data e o nome que me deram."},
    },
    "talk": {"npc": "treinador", "hint": "O treinador espera, as mãos sobre o tabuleiro. Acho que posso falar com ele.",
             "lines": ["TREINADOR: Dois anos, Aleksey. Você aprende mais rápido do que devia.", "ALEKSEY: Rápido demais para quem não sabe nada.",
                       "TREINADOR: Quem não sabe nada não joga e4 sem olhar. Você sabe alguma coisa. O corpo lembra, mesmo que a cabeça não.",
                       {"q": "O treinador estende o caderno novo. O que você faz?", "opts": ["Escrever tudo, como ele mandou", "Confiar na memória"], "truth": [1, -1], "flag": "diario",
                        "reply": [["TREINADOR: Bom. Quem escreve, existe."], ["TREINADOR: Hm. Memória é o que mais falha em quem mais confia nela."]]},
                       "TREINADOR: Quando estiver pronto, Irina vai buscá-lo. Não conte a ninguém que você joga assim."],
             "note": "O treinador diz que o corpo lembra, mesmo que a cabeça não. Preciso escrever tudo.", "alt": "O treinador gosta de mim. Fico tranquilo."},
}

# ---- 13 · A7 · T−2 dias ---------------------------------------------------------------------------------------------------------------
T["telhado"] = {
    "clues": {
        "cidade": {"note": "A cidade a meus pés: fumaça no horizonte e, de pé, escuro, o bloco de concreto do Kosmos.", "say": "Moscou arde devagar. E o Kosmos fica intacto no meio."},
    },
    "talk": {"npc": "inter", "hint": "O intermediário acende um cigarro junto à antena. Acho que é a minha vez de falar.",
             "lines": ["INTERMEDIÁRIO: Pontual, Petrov. A cidade está pior do que ontem.", "INTERMEDIÁRIO: Irina manda dizer: o Lethe tem de estar armado em dois dias. Karpov não espera mais.",
                       "ALEKSEY: E Boris?", "INTERMEDIÁRIO: Boris é o homem de quem todos vão duvidar. Você sabe o que fazer.",
                       {"q": "O intermediário estende um envelope grosso. O que você faz?", "opts": ["Aceitar o envelope e o prazo", "Recusar: «Eu decido o que faço»"], "truth": [-1, 1], "flag": "pacto",
                        "trust": {"irina": [1, -1]},
                        "reply": [["INTERMEDIÁRIO: Sensato. Quem aceita sobrevive até o fim da semana."], ["INTERMEDIÁRIO: Todo mundo diz isso, Petrov. Até o primeiro tiro."]]},
                       "INTERMEDIÁRIO: Dois dias. Depois disso, ninguém mais lembra deste telhado."],
             "note": "No telhado, o intermediário de Irina falou do prazo: dois dias para armar o Lethe. Ofereceu um envelope grosso.", "alt": "Conversei com um conhecido no telhado."},
}

# ---- 14 · F7 · mar/1992 ---------------------------------------------------------------------------------------------------------------
T["cemiterio"] = {
    "clues": {
        "caixao": {"note": "Caixão de pinho sobre a cova aberta. A placa diz: uma mulher de 34 anos. A tampa fechada esconde o rosto.", "say": "Quem é ela? A neve não responde."},
        "coroa": {"note": "Coroa de cravos vermelhos: «Лена — коллеги из «Космоса»». Num laço preto, por baixo, em letra menor: «Нам тебя не хватает, Миша».",
                  "say": "Cravos vermelhos. E um nome pequeno demais, escondido embaixo: Misha."},
        "lapide": {"note": "Lápide provisória de madeira: «Елена Морозова, 1958–1992».", "say": "Morozova. Esse sobrenome me é familiar. De onde?"},
        "sergei": {"note": "Um homem ao lado da cova, sem chapéu e sem lágrimas, a mão fechada num lenço. Não olha para ninguém.", "say": "Todos choram, menos ele. Ou ele já chorou tudo."},
    },
    "talk": {"npc": "boris", "hint": "Do outro lado da cova, um homem de farda me olha fixamente. Acho que ele quer falar.",
             "lines": ["BORIS: Eu conheço você?", "ALEKSEY: Não creio.", "BORIS: Você anda como meu irmão. O mesmo jeito de arrastar o pé esquerdo.",
                       {"q": "Ele não desvia o olhar. O que você faz?", "opts": ["Aproximar-se: «Meus pêsames pela perda.»", "Virar as costas e ir embora"], "truth": [1, -1], "flag": "encarou_boris",
                        "trust": {"boris": [1, -1]},
                        "reply": [["BORIS: ...Obrigado. Não, perdão. Você me lembrou alguém."], ["BORIS: Espere! ...Esquece. Esqueça."]]},
                       "BORIS: Meu irmão sumiu em agosto. Se um dia o vir, diga que o procuro."],
             "note": "No cemitério, um homem de farda me encarou e disse que eu ando como o irmão dele, desaparecido desde agosto de 1991.", "alt": "Um policial me confundiu com alguém. Besteira."},
}

# ---- 15 · A8 · T−3 dias ---------------------------------------------------------------------------------------------------------------
T["chave"] = {
    "clues": {
        "missil": {"note": "O Lethe aberto: dentro, nenhuma ogiva. Só uma cavidade de latão com bobinas. Não é uma bomba.", "say": "Por dentro é oco. Se não é bomba, é o quê?"},
        "painel": {"note": "Painel do pulso: o visor mostra «ОПЕРАТОР: —». Ninguém registrado como operador.", "say": "Operador: nenhum. Por que um painel espera alguém que não existe?"},
        "pasta": {"note": "Pasta «ЛЕТА»: protocolos de teste. Há um nome riscado na primeira linha da lista de cobaias; embaixo, a letra de Sergei: «foi o primeiro».",
                  "say": "Um nome riscado até furar o papel. Não consigo lê-lo."},
        "gravacao": {"note": "Gravador de fita: uma voz de mulher repete «Serioja, lembre de mim». A fita está gasta de tanto uso.", "say": "A mesma frase, em volta. A fita já está gasta."},
    },
    "talk": {"npc": "sergei", "hint": "Sergei me espera junto ao míssil. Acho que é hora de ouvi-lo.",
             "lines": ["SERGEI: Veja bem, Aleksey. Foi para isto que passei a vida. Não destrói cidades: devolve o descanso.", "ALEKSEY: Devolve? Ele apaga quem o opera.",
                       "SERGEI: O primeiro que o operou escolheu esquecer. Eu fui quem apertou o botão. Eu sei quem você é.",
                       {"q": "Sergei não desvia os olhos de você. O que você faz?", "opts": ["Negar: «Não sei do que o senhor está falando.»", "Perguntar: «Quem eu sou, Sergei?»"], "truth": [-1, 1], "flag": "sergei_sabe",
                        "trust": {"sergei": [-1, 1]},
                        "reply": [["SERGEI: Como queira. Nós dois sabemos mentir muito bem."], ["SERGEI: Ainda não, meu filho. A verdade, dita agora, o mataria."]]},
                       "SERGEI: Leve a chave. Quando chegar a hora, você vai precisar dela."],
             "note": "Sergei disse: «Eu sei quem você é.» E me entregou a chave do painel do pulso.", "alt": "Sergei me deu uma chave. Confia em mim."},
}

# ---- 16 · F8 · ago/1993 ---------------------------------------------------------------------------------------------------------------
T["parque"] = {
    "clues": {"placa": {"say": "Parque de cultura e descanso. Hoje, descanso me soa a senha."}},
    "talk": {"npc": "irina", "hint": "Irina me espera num banco, os óculos escuros na mão. Acho que é hora de falar.",
             "lines": ["IRINA: Aleksey. Você está bem. Os dois anos fizeram bem.", "ALEKSEY: Fizeram de mim outra pessoa.",
                       "IRINA: Foi para isso. Escute: na segunda você começa no Kosmos, como consultor. Sergei Morozov será seu contato.",
                       "IRINA: Karpov quer o Lethe. Você é meus olhos lá dentro. Quando eu pedir, você age.",
                       {"q": "Irina pousa a mão em seu braço. O que você diz?", "opts": ["Aceitar a missão sem perguntas", "Perguntar: «O que eu ganho com isso?»"], "truth": [-1, 1], "flag": "missao_aceita",
                        "trust": {"irina": [1, -1]},
                        "reply": [["IRINA: Esse é o homem que eu preparei."], ["IRINA: Uma vida. Nada mais. É mais do que a maioria recebe."]]},
                       "IRINA: Hoje é o último dia de sol, Aleksey. Aproveite."],
             "note": "Irina me deu a missão: entrar no Kosmos como consultor. Sergei Morozov será meu contato. Karpov quer o Lethe.", "alt": "Começo a trabalhar no Kosmos na segunda. Bom emprego."},
}

# ---- 17 · A9 · T−4 dias ---------------------------------------------------------------------------------------------------------------
T["apt_irina"] = {
    "clues": {
        "mala": {"note": "Mala pronta ao pé da cama, fechada com cinto. Dentro, passaportes de três nomes diferentes.", "say": "Uma mala sempre pronta. Quem vive assim espera ter de sumir."},
        "ordem": {"note": "Pasta na escrivaninha: «ПРИКАЗ №14: И. Лебедева — к стиранию», assinada por Karpov. A ordem é para apagar a própria Irina.", "say": "A ordem é para Irina. Quem manda apagar quem apaga?"},
        "foto_karpov": {"note": "Retrato de Irina jovem, abraçada a um oficial com o rosto raspado a canivete: só ficou o uniforme.", "say": "O rosto do oficial foi arranhado. Só restou o uniforme."},
    },
    "talk": {"npc": "irina", "hint": "Irina me olha do sofá, sem o casaco de sempre. Acho que é hora de ouvi-la.",
             "lines": ["IRINA: Aleksey. Sente-se. Estou cansada de ser a mulher forte.", "IRINA: Karpov me marcou para o apagamento. Depois que o Lethe sair, eu sobro.",
                       "ALEKSEY: Você me trouxe até aqui.", "IRINA: E você pode me salvar. Fique comigo, Aleksey. Uma noite, só uma.",
                       {"q": "Irina se aproxima. O que você faz?", "opts": ["Prometer ajuda: «Eu protejo você.»", "Manter distância: «Isso não é comigo.»"], "truth": [1, -1], "flag": "ajudou_irina",
                        "trust": {"irina": [2, -2]},
                        "reply": [["IRINA: ...Obrigada. (Baixinho:) Se me trair, o Lethe também chega até você."], ["IRINA: Entendo. Eu faria igual. (O olhar dela esfria.)"]]},
                       "IRINA: Eu o escolhi por ser só. Ser só é a única coisa que Karpov não consegue comprar."],
             "note": "Irina está marcada para o apagamento por Karpov e me pediu ajuda, com carinho e com ameaça.", "alt": "Irina me convidou para jantar. Foi agradável."},
}

# ---- 18 · F9 · ago/1993 ---------------------------------------------------------------------------------------------------------------
T["museu"] = {
    "clues": {
        "capsula": {"note": "Cápsula de reentrada na vitrine. A placa original foi trocada por um papel: «Лета-1: испытательный образец».",
                    "say": "Lethe-1, amostra de teste, numa vitrine de museu. Quem esconderia um protótipo à vista?"},
        "livro": {"note": "Livro de visitas. A última assinatura é de 21 de agosto de 1991: «М. Волков».", "say": "Última visita: agosto de 1991, M. Volkov. Depois, ninguém mais."},
        "lonas": {"note": "Sob uma lona, um tabuleiro de xadrez antigo, sem o peão branco.", "say": "Um tabuleiro velho sob a lona. Falta o peão branco."},
    },
    "talk": {"npc": "sergei", "hint": "Sergei me espera no centro do salão, a mão estendida. Acho que é hora do primeiro aperto.",
             "lines": ["SERGEI: Aleksey Petrov. Prazer. Eu sou Sergei Morozov.", "ALEKSEY: Irina disse que o senhor seria meu contato.",
                       "SERGEI: (Segura sua mão um pouco mais que o necessário.) Eu conheço essas mãos.",
                       "SERGEI: Isto é seu. Um peão branco. Perdi-o há muito tempo e o encontrei hoje, em um bolso velho.",
                       {"q": "Sergei estende o peão. O que você faz?", "opts": ["Aceitar o peão", "Recusar: «Não é meu.»"], "truth": [1, -1], "flag": "peao_aceito",
                        "trust": {"sergei": [1, -1]}, "give": ["peao", ""],
                        "reply": [["SERGEI: (Quase sorri.) Então é seu."], ["SERGEI: Como quiser. Mas ele sabe de quem é."]]},
                       "SERGEI: Começamos amanhã, Aleksey. Seja bem-vindo ao Kosmos."],
             "note": "Sergei me apertou a mão como quem reconhece e me estendeu um peão branco: diz que é meu.", "alt": "Sergei me apresentou ao Kosmos. Simpático."},
}

# ---- 19 · A10 · T−6 dias --------------------------------------------------------------------------------------------------------------
T["interrogatorio"] = {
    "clues": {"pasta": {"note": "Pasta com a etiqueta «ВОЛКОВ М. И. — изъято» (retirado). Dentro, um recorte de jornal da noite do golpe de 1991. Boris guarda um caso que não fechou.",
                        "say": "Boris leva um desaparecido para dentro do trabalho."}},
    "talk": {"npc": "boris", "hint": "Boris me indica a cadeira, sem sorrir. Acho que vai começar.",
             "lines": ["BORIS: Senta, Petrov. Cinco minutos. Quem é você, afinal?", "ALEKSEY: Técnico em eletrônica. Está no meu prontuário.",
                       "BORIS: Prontuário. Eu li. Tem coisa demais que o senhor não sabe sobre o senhor.",
                       "BORIS: Dê três passos até a porta e volte. (Ele me observa andar.) ...Você arrasta o pé esquerdo.",
                       {"q": "Boris assobia baixinho quatro notas: G-D-E-D. Ele espera. Rápido: o que você faz?", "opts": ["Assobiar a melodia de volta, sem pensar", "Ficar em silêncio"],
                        "seconds": 8, "default": 1, "truth": [-1, 1], "flag": "assobiou", "trust": {"boris": [-1, 1]},
                        "reply": [["BORIS: (A boca entreaberta.) Onde aprendeu essa canção, Petrov?", "ALEKSEY: Não sei. Veio sozinha."], ["BORIS: Silêncio. Interessante. Quem se cala sabe de algo."]]},
                       "BORIS: Pode ir. Por enquanto."],
             "note": "Boris me testou: o andar, o assobio. Ele suspeita que eu seja o irmão dele. Não sei se tenho medo ou esperança.", "alt": "Boris me interrogou. Rotina."},
}

# ---- 20 · F10 · ago/1993 --------------------------------------------------------------------------------------------------------------
T["entrevista"] = {
    "clues": {
        "retrato": {"note": "Um porta-retratos virado para baixo na mesa de Boris. Ele o desvira quando está sozinho e o esconde quando alguém entra. Dois garotos na neve.",
                    "say": "Ele esconde essa foto de quem entra. Por quê?"},
        "diploma": {"say": "Ivanovich, como eu. Será só o patronímico mais comum da Rússia?"},
    },
    "talk": {"npc": "boris", "hint": "Boris se recosta na cadeira e cruza os braços. Acho que vai começar a entrevista.",
             "lines": ["BORIS: Petrov. Currículo limpo demais. De onde você veio?", "ALEKSEY: De Leningrado. Pais professores, falecidos.",
                       "BORIS: ...E o jeito de andar? Você arrasta o pé. Teve acidente?",
                       {"q": "Boris olha para o seu pé esquerdo. O que você responde?", "opts": ["Responder com a biografia decorada", "Admitir: «Não sei. Não lembro.»"],
                        "seconds": 10, "default": 0, "truth": [-1, 1], "flag": "admitiu", "trust": {"boris": [-1, 2]},
                        "reply": [["BORIS: Decorada. Bem decorada."], ["BORIS: (Longo silêncio.) Também não lembro certas coisas. Muito bem, Petrov."]]},
                       "BORIS: Contratado. Mas ouça: não me agrada quem assobia no corredor. Não faça isso."],
             "note": "Boris me contratou, mas me olhou como quem quase sabe. Não gosta de quem assobia.", "alt": "Fui contratado. Boris é chato mas justo."},
}

# ---- 21 · A11 · T−8 dias --------------------------------------------------------------------------------------------------------------
T["arquivos_mortos"] = {
    "timer": {"seconds": 150, "warns": [[100, "Passos no andar de cima. O vigia faz a ronda."], [45, "A ronda desce a escada. Pouco tempo."]],
              "fail": "A luz do vigia varreu a porta. Saio e tento de novo, sem pressa."},
    "clues": {"ficha": {"note": "Ficha: «ВОЛКОВ Михаил Иванович, 1960 г.р. — изъято 21.08.1991, ЛЕТА». A foto 3x4 é o meu rosto, sem as faixas. Eu sou Mikhail Volkov.",
                        "say": "O mundo estala: meu rosto, 1991, um nome. A lembrança pisca e some."}},
}

# ---- 22 · F11 · set/1993 --------------------------------------------------------------------------------------------------------------
T["lounge"] = {
    "clues": {"dossie": {"note": "Dossiê sobre a mesa: fotografias de Sergei, de Boris, do Kosmos à noite, e «Лебедев И.» como contato. Reconheço a minha letra nas legendas.",
                         "say": "Alguém fotografou todos nós. E eu ajudei."}},
}

# ---- 23 · A12 · T−10 dias -------------------------------------------------------------------------------------------------------------
T["metro"] = {
    "clues": {
        "relogio": {"note": "Relógio da estação parado em 3h12. Irina marcou comigo às 3h.", "say": "O relógio parou. Ou me fez esperar."},
        "trilhos": {"note": "Os trilhos vibram sem trem: um rumor pesado, longe. Algo grande se move na cidade.", "say": "Os trilhos tremem sem trem."},
        "banco": {"note": "Um maço de cigarros esquecido e um papel dobrado: «10 dias. Não me procure.» Irina deixou o recado antes de chegar.", "say": "Um recado deixado como quem avisa o fim."},
    },
    "talk": {"npc": "irina", "hint": "Irina me espera sob a luz tremida da plataforma. Acho que vai falar.",
             "lines": ["IRINA: Dez dias, Aleksey. É tudo o que você tem.", "ALEKSEY: Para fazer o quê, exatamente?",
                       "IRINA: Armar o Lethe. Karpov quer que ele saia do Kosmos com todos dentro. Depois disso, ninguém mais lembra de nada.",
                       {"q": "Um trem se aproxima ao longe. Responda antes que ele chegue.", "opts": ["Perguntar: «E se eu me recusar?»", "Concordar: «Está bem. Dez dias.»"],
                        "seconds": 12, "default": 1, "truth": [1, -1], "flag": "recusou_irina", "trust": {"irina": [-1, 1]},
                        "reply": [["IRINA: Então você morre de verdade, em vez de esquecer."], ["IRINA: Bom. Você é meu melhor, Aleksey."]]},
                       "IRINA: O trem chegou. Eu desço aqui. Você, a outra estação."],
             "note": "No metrô, Irina me deu dez dias para armar o Lethe, o plano de Karpov para apagar todo o Kosmos.", "alt": "Irina me deu um prazo apertado no trabalho."},
}

# ---- 24 · F12 · set/1993 --------------------------------------------------------------------------------------------------------------
T["tabuleiro_sergei"] = {
    "needed": ["pecas", "foto", "estante", "jogo"],
    "clues": {
        "pecas": {"note": "Tabuleiro armado: as brancas comigo, as pretas com Sergei. Falta um peão branco do meu lado.", "say": "Falta um peão no meu lado.",
                  "uses": {"item": "peao", "note": "Pus o peão que Sergei me deu no lugar vazio. Encaixou como se tivesse nascido ali.", "say": "O peão cabe no vazio do tabuleiro. Como se tivesse sido feito para ele."}},
        "foto": {"note": "Foto de um casal, com um canto queimado. O canto queimado me diz alguma coisa.", "say": "Esse canto queimado... eu já vi isto."},
        "estante": {"optional": False, "note": "Estante de livros de xadrez: «Дебюты», «Королевский гамбит». Em um deles, a lápis, uma linha: 1.e4 e5 2.Cf3 Cc6.",
                    "say": "Todos esses livros e uma só linha sublinhada: e4, e5, Cf3, Cc6."},
        "jogo": {"note": "A partida com Sergei: minhas mãos conhecem aberturas que eu não aprendi.", "say": "A mão sabe. A boca falou. E Sergei ouviu.",
                 "ask": {"q": "Sergei abre com 1.e4 e você responde 1...e5. Ele joga 2.Cf3 e espera. Seu lance?",
                         "opts": ["2... Cc6: defender o peão com o cavalo", "2... f6: defesa passiva", "2... d6: a defesa Philidor"], "truth": [1, 0, 0], "flag": "falou_misha", "correct": 0, "must": True,
                         "reply": [["SERGEI: Cc6. Sempre Cc6. (Ele fica pálido.)", "ALEKSEY: Meu pai... quer dizer... Misha ensinava assim.", "SERGEI: Quem é Misha, Aleksey?"],
                                   ["SERGEI: f6. Hm. Não é o seu estilo. Tente de novo."], ["SERGEI: Philidor. Ousado, quando não se sabe o que faz. Tente de novo."]]}},
    },
    "talk": {"npc": "sergei", "hint": "Sergei me olha sem piscar. Acho que devo falar com ele.",
             "lines": ["SERGEI: Você jogou como alguém que eu perdi.", "ALEKSEY: Desculpe. Não sei por que falei aquele nome.",
                       {"q": "Sergei serve chá. O que você diz?", "opts": ["Perguntar: «Quem é Misha, Sergei?»", "Mudar de assunto: «Falemos do trabalho.»"], "truth": [1, -1], "flag": "perguntou_misha",
                        "trust": {"sergei": [1, -1]},
                        "reply": [["SERGEI: Um aluno meu. Talentoso. Perdi-o em 1991. (Ele se afasta.)"], ["SERGEI: ...Claro. O trabalho. Sempre o trabalho."]]},
                       "SERGEI: Volte amanhã. Jogaremos outra vez."],
             "note": "Sergei ouviu a palavra Misha escapar de mim e fingiu não notar. Ele sabe, e eu quase sei.", "alt": "Joguei xadrez com Sergei. Divertido."},
}

# ---- 25 · A13 · T−12 dias -------------------------------------------------------------------------------------------------------------
T["decreto"] = {
    "clues": {"telefone": {"note": "Karpov ligou para a cantina. Quer o Lethe armado no dia três, e sabe onde eu almoço.", "say": "A voz de Karpov: seca, fria, sem rosto.",
                           "ask": {"q": "O telefone vermelho toca. É Karpov: «Petrov. Dia três. Não me decepcione.» Responda.", "opts": ["Obedecer: «Sim, camarada.»", "Desligar sem responder"],
                                   "seconds": 10, "default": 1, "truth": [-1, 1], "flag": "obedeceu_karpov", "correct": 0,
                                   "reply": [["KARPOV (ao telefone): Bom. Irina fala bem de você."], ["KARPOV (ao telefone): ...Petrov? Alô?"]]}}},
    "talk": {"npc": "irina", "hint": "Irina me observa sem tocar na sopa. Acho que ela quer falar.",
             "lines": ["IRINA: Você viu a TV. Dissolveram o Parlamento. Agora nada nos protege.", "IRINA: Karpov apertou. Quer o Lethe armado antes da primeira neve.", "ALEKSEY: E você?",
                       {"q": "Irina olha por cima do ombro. O que você diz?", "opts": ["Perguntar: «Você ainda está marcada?»", "Dizer: «Faço o que for preciso.»"], "truth": [1, -1], "flag": "perguntou_marcada",
                        "trust": {"irina": [1, -1]},
                        "reply": [["IRINA: Sempre. Até o último dia."], ["IRINA: Eu sei. Foi por isso que o escolhi."]]},
                       "IRINA: Coma. Hoje a sopa é o único jeito de fingir normalidade."],
             "note": "O decreto de Ieltsin e a pressão de Karpov sobre Irina: tudo se fecha em torno de nós.", "alt": "Almocei na cantina. Estava ótimo."},
}

# ---- 26 · F13 · set/1993 --------------------------------------------------------------------------------------------------------------
T["apt_boris"] = {
    "intro": [["Boris foi para o turno. Entro sem ser convidado: não posso ser visto aqui.", 5.0]],
    "timer": {"seconds": 110, "warns": [[60, "A porta do prédio bateu lá embaixo. Pode ser ninguém."], [28, "Passos subindo a escada. Preciso terminar e sair."]],
              "fail": "A chave girou na fechadura. Boris voltou cedo. Recomeço, com mais cuidado."},
    "clues": {
        "foto": {"note": "Porta-retratos: dois garotos na neve, o mais velho com a mão no ombro do menor. Por um segundo, sem som, eu estive lá.", "say": "Um segundo de neve, sem som. Uma mão no meu ombro."},
        "farda": {"note": "Farda de milícia no armário aberto, passada a ferro com capricho.", "say": "Passada a ferro todo dia. Ele só tem isso."},
        "cama": {"note": "Cama arrumada com precisão militar. Debaixo do travesseiro, um velho peão de xadrez, branco, lascado.", "say": "Debaixo do travesseiro, um peão branco, igual ao que Sergei me deu."},
        "mesa": {"note": "Cadernos de relatório de Boris: página após página sobre «М. Волков» e «А. Петров», lado a lado.", "say": "Dois nomes lado a lado. Ele está comparando."},
        "tv": {"optional": False},
    },
}

# ---- 27 · A14 · T−13 dias -------------------------------------------------------------------------------------------------------------
T["corredor"] = {
    "clues": {"quadro": {"note": "Quadro de avisos: «Всем сотрудникам — в пятницу эвакуация». Evacuação na sexta.", "say": "Evacuação na sexta. Quem manda evacuar um prédio de pedra?"}},
    "talk": {"npc": "sergei", "hint": "Sergei vem do fundo do corredor devagar. Acho que ele quer passar por mim.",
             "lines": ["ALEKSEY: ...Misha. (Escapa dos meus lábios.)", "SERGEI: (Sem parar de andar.) Boa tarde, Petrov.", "ALEKSEY: O senhor ouviu?",
                       {"q": "Sergei não se vira. O que você faz?", "opts": ["Insistir: «Eu disse Misha. O senhor ouviu.»", "Fingir: «Nada. Falei sozinho.»"], "truth": [1, -1], "flag": "insistiu_misha",
                        "trust": {"sergei": [1, -1]},
                        "reply": [["SERGEI: Não ouvi nada. (A voz dele falha.)"], ["SERGEI: Também falo sozinho. É coisa da idade."]]},
                       "SERGEI: Vá para casa. Descanse. Amanhã é outro dia."],
             "note": "Disse «Misha» sem querer no corredor. Sergei fingiu não ouvir: a mentira dele foi mais alta que a palavra.", "alt": "Cumprimentei Sergei no corredor."},
}

# ---- 28 · F14 · T−15 dias -------------------------------------------------------------------------------------------------------------
T["telefone"] = {
    "clues": {"telefone": {"say": "O medo dela diz mais que as palavras.",
                           "ask": {"q": "Você disca o número de Irina. Do outro lado, a voz dela. O que você diz?", "opts": ["«Estou começando a lembrar.»", "Desligar sem falar"], "truth": [1, -1],
                                   "flag": "contou_lembrar", "correct": 0, "trust": {"irina": [1, -1]},
                                   "reply": [["IRINA (ao telefone): ...Não diga isso ao telefone. Estou indo aí.", "(A voz dela treme. Ela está com medo.)"], ["(Do outro lado, só a respiração dela. Depois, o sinal de linha.)"]]}}},
}

# ---- 29 · F15 · T−14 dias -------------------------------------------------------------------------------------------------------------
T["piscar"] = {
    "add_clues": [{"id": "diario", "prompt": "Folhear o diário", "pos": [-4.5, 1.0, -1.3], "size": [0.5, 0.4, 0.4],
                   "note": "Meu diário, quarenta páginas: «Escreva tudo». Folheio e acho uma letra que não é minha, ao lado das minhas: «não confie em Sergei». Quem escreveu?",
                   "alt": "Meu diário. Tudo em ordem.", "say": "Há uma frase no meu diário que eu não escrevi. Ou escrevi e esqueci."}],
    "clues": {"espelho": {"ask": {"q": "No vidro, o seu reflexo estala. Por dez segundos você lembra de tudo. Depressa: o que você diz em voz alta?",
                                  "opts": ["«Eu sou Mikhail Volkov. Sou Misha.»", "Calar e deixar passar"], "seconds": 10, "default": 1, "truth": [2, -1], "flag": "disse_nome", "correct": 0,
                                  "trust": {"sergei": [1, -1]},
                                  "reply": [["ALEKSEY: Eu sou Mikhail Volkov! Eu me lembro! Sergei... foi você!", "(Um estalo. A memória vai embora, como a maré.)"], ["(Dez segundos de tudo. Depois, de novo o nada, a boca fechada.)"]]}}},
}

# ---- 30 · T = 0 -----------------------------------------------------------------------------------------------------------------------
T["tiro"] = {
    "clues": {
        "telefone": {"ask": {"q": "Karpov, ao telefone: «Arme o Lethe, Petrov. Agora.» O que você diz?", "opts": ["«Sim, camarada.»", "«Não.» e desligar", "Deixar tocar"],
                             "seconds": 12, "default": 2, "truth": [-2, 2, 0], "flag": "obedeceu_final", "correct": 0,
                             "reply": [["KARPOV (ao telefone): Bom menino."], ["KARPOV (ao telefone): Você morreu para mim, Petrov."], ["(O telefone toca até se calar.)"]]}},
        "console": {"uses": {"item": "cartao", "note": "Com o cartão de acesso que Sergei me deu, a tampa do painel cede sem esforço.", "say": "O cartão abre a tampa. Sergei me deixou entrar até aqui."}},
        "peao": {"uses": {"item": "peao", "note": "O peão que Sergei me devolveu cabe na minha mão como se nunca a tivesse deixado.", "say": "Pequeno, lascado, meu. Um peão chega ao fim do tabuleiro e vira o que quiser."}},
        "arma": {"ask": {"q": "A arma está na sua mão. Sergei sorri, Boris espera, Irina desvia o olhar. Decida.", "opts": ["Atirar em Sergei", "Baixar a arma", "Dizer: «Eu sou Mikhail Volkov. Eu sou Misha.»"],
                         "seconds": 25, "default": 1, "truth": [-2, 1, 3], "flag": "final_nome", "correct": 2, "trust": {"boris": [-2, 1, 3], "sergei": [-3, 1, 2]},
                         "reply": [["(O estampido enche a sala. O pulso sobe, branco.)"], ["(Você solta a arma. Ela cai com um som seco. O pulso sobe, branco, de qualquer jeito.)"],
                                   ["MISHA: Eu sou Mikhail Volkov. Boris, eu sou o seu irmão.", "(O pulso sobe, branco, mas desta vez ele não o apaga: ele o ilumina.)"]]}},
    },
    "finale": {"endings": [
        {"flag": ["final_nome", True], "when": {"item": "peao", "trust": "boris", "gte": 4}, "title": "O IRMÃO",
         "text": "O nome saiu inteiro e Boris não precisou de mais nada. Ele tirou do bolso um peão branco, igual ao seu, e fechou a mão do irmão em volta dos dois. Sergei desligou o gravador de Lena. O Lethe ficou em silêncio, e os dois saíram juntos na neve de outubro, arrastando o pé esquerdo no mesmo compasso."},
        {"flag": ["final_nome", True], "title": "MISHA",
         "text": "Sua voz tremeu, mas o nome saiu inteiro: Mikhail Volkov. Boris deu um passo à frente, as mãos abertas. Sergei baixou a cabeça e, pela primeira vez em dois anos, desligou o gravador de Lena. O Lethe ficou em silêncio. Você lembrou. E, desta vez, escolheu lembrar."},
        {"max": -3, "title": "O OPERADOR",
         "text": "Você obedeceu a todos, e o Lethe acendeu. O operador esqueceu primeiro, como sempre. Em algum lugar, um homem de terno acorda ao lado de um corpo, com uma arma quente na mão e nenhuma memória."},
        {"min": 3, "title": "A TESTEMUNHA",
         "text": "Você investigou, duvidou, perguntou. Não impediu o pulso, mas deixou rastros: um diário, um caderno, um peão. Quem vier depois saberá onde procurar. A verdade sobrevive a quem a esquece."},
        {"title": "O CICLO", "text": "O tiro. O pulso. Um teto branco. Um nome que não é seu. Tudo recomeça."}]},
}

# ---- densidade: cada cena exige só as pistas-prova e faz UMA pergunta (ver o quadro de evidências em game/story.gd) -------------------------
NEEDED = {
    "sala_controle": ["terminal", "cracha", "foto", "camlog"], "treinador": ["tabuleiro", "cartilha", "caderno"], "telhado": ["antena", "tanque", "cidade"],
    "cemiterio": ["coroa", "lapide", "sergei"], "chave": ["missil", "painel", "pasta"], "parque": ["placa", "roda", "lago"],
    "apt_irina": ["ordem", "mala", "foto_karpov"], "museu": ["capsula", "livro", "busto"], "interrogatorio": ["espelho", "gravador", "pasta"],
    "entrevista": ["curriculo", "retrato", "crachas"], "arquivos_mortos": ["gaveta", "ficha", "estante"], "lounge": ["dossie", "nota", "tv"],
    "metro": ["relogio", "mapa", "banco"], "tabuleiro_sergei": ["pecas", "estante", "jogo"], "decreto": ["tv", "jornal", "telefone"],
    "apt_boris": ["foto", "cama", "mesa"], "corredor": ["lockers", "quadro", "janela"], "telefone": ["diario", "janela", "telefone"], "piscar": ["diario", "espelho"],
}
QUESTION = {
    "sala_controle": "Quem vai levar a culpa amanhã?", "treinador": "Quem estão me treinando para ser?", "telhado": "Quem está por trás do prazo?",
    "cemiterio": "Quem era ela, e quem a chora?", "chave": "O que o Lethe é por dentro?", "parque": "O que Irina quer de mim?",
    "apt_irina": "Irina é caçadora ou caça?", "museu": "Por que Sergei quer me ver?", "interrogatorio": "O que Boris suspeita?",
    "entrevista": "O que Boris esconde?", "arquivos_mortos": "O que havia na ficha que sumiu?", "lounge": "Para quem Irina trabalha?",
    "metro": "O que Irina espera de mim?", "tabuleiro_sergei": "Que nome eu quase disse?", "decreto": "Quem aperta Irina?",
    "apt_boris": "O que Boris já sabe?", "corredor": "O que Sergei ouviu?", "telefone": "Quem escreveu no meu diário?",
    "piscar": "O que eu vi por dez segundos?", "tiro": "Quem eu escolho ser?",
}
for n, ids in NEEDED.items():
    T[n]["needed"] = ids
for n, q in QUESTION.items():
    T[n]["question"] = q
# o último lance depende do que foi deduzido: sem a identidade resolvida no quadro, o nome não vem
T["tiro"]["clues"]["arma"]["ask"]["gates"] = {"2": {"ledger": "identidade", "text": "Tentar dizer um nome... mas qual?", "as": 1,
                                                    "fail": "(A boca abre. Nenhum nome vem. Falta prova demais que eu não reuni.)"}}
T["tiro"]["finale"]["endings"].insert(2, {"when": {"ledger_gte": 6}, "title": "O ARQUIVISTA",
    "text": "Você não impediu o pulso, mas montou o quadro inteiro, peça por peça: quem foi, quem traiu, quem salvou. Quando o branco veio, as respostas já estavam fixadas. Quem achar o seu caderno saberá a verdade sem ter de esquecê-la de novo."})

os.makedirs(OUT, exist_ok=True)
for name, data in T.items():
    with open(os.path.join(OUT, name + ".json"), "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
print(len(T), "cenas")
