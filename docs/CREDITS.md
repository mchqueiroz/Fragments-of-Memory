# Créditos e licenças

## Vozes reais em russo (domínio público)

As gravações vêm do **LibriVox** (leituras de voluntários), publicadas no Internet Archive com a marca
**Public Domain Mark 1.0** (<http://creativecommons.org/publicdomain/mark/1.0/>). Os leitores dedicaram as
gravações ao domínio público; não é exigida atribuição, mas ela é feita aqui por cortesia.

| Uso no jogo | Obra (texto) | Leitor(a) | Item no Internet Archive |
|---|---|---|---|
| Rádio de 1993 (`radio_real.wav`) | *Камень*, Óssip Mandelstam (1891–1938) | Mark Chulsky | `kamen_1501_librivox` |
| Fita de Lena (`lena_tape.wav`) | *Евгений Онегин*, cap. 3, Aleksandr Pushkin (1799–1837) | Xenium5 | `eugene_onegin_1801_librivox` |

Os trechos são processados (filtro de AM, ruído, oscilação de fita) por `tools/voices_real.py`.

**Cuidado com o texto, não só a gravação:** o domínio público do LibriVox vale para os EUA. Para vender em outros
países o **texto** também precisa estar livre lá. Por isso só usamos autores mortos há mais de 70 anos
(Mandelstam, Pushkin; Chekhov, Gumilyov e Khodasevich também seriam seguros). **Não usar** Akhmatova (m. 1966) nem
Georgy Ivanov (m. 1958): o texto ainda é protegido na Rússia e na União Europeia.

## Vozes sintetizadas

- Murmúrios dos personagens, locutor-gibberish e música: sintetizados por `tools/audio.py` (código próprio).
- `espeak-ng` (GPL) está instalado na máquina e pode gerar voz robótica em russo (útil para o "intermediário");
  verificar a licença antes de distribuir qualquer saída.
- Vozes do **Piper TTS** em russo (denis, dmitri, irina, ruslan): o repositório é MIT, mas a licença de cada voz
  **não está confirmada** (a voz "ruslan" usa um conjunto de dados que pode ser não comercial). Não usar antes de checar.
- **Mozilla Common Voice** (russo) é CC0, mas os termos de uso proíbem re-hospedar o conjunto de dados; não incluir clipes no jogo.

## Cenas 3–8 (síntese própria)
- `swan_lake.wav`: estilização sintetizada do tema do cisne (Tchaikovsky, 1876; domínio público). Não é gravação de terceiros.
- `tanks.wav`, passos por piso e demais sons: sintetizados em `tools/audio.py`.

## Música e vozes
- Trilha (art/audio/mus_*.wav): sintetizada por tools/musica.py (numpy/scipy), sem amostras de terceiros.
- Vozes (art/audio/vo/*.wav): geradas por tools/vozes.py com espeak-ng e filtros; substituíveis por gravações (ver manifest.json).
