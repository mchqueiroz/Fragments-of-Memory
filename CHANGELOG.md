# Changelog

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/). A seção de cada versão vira
o texto da Release no GitHub.

## [1.0.0] - 2026-10-31

Primeira versão completa.

### História
- 28 cenas jogáveis em quatro atos, duas linhas do tempo (1993 para trás, 1991 para frente) e quatro finais.
- Créditos no final; o save é apagado e o jogo volta ao título.

### Jogo
- Diário com memória que se apaga e se reescreve, quadro de evidências, confiança de Irina, Boris e Sergei,
  furtividade com volta ao último ponto seguro.
- Teclado, mouse e controle.

### Opções
- Qualidade gráfica (Baixa, Média, Alta), tela cheia (F11), sincronia vertical.
- Volumes separados: geral, música, efeitos, vozes.
- Sensibilidade, eixo Y invertido, balanço da câmera desligável, campo de visão, legendas grandes.

### Técnico
- Na Alta, 60 fps em GPU integrada em quase todas as cenas (pior quadro medido: 20 ms).
- Save atômico e tolerante a arquivo antigo ou corrompido.
- Auditoria automática de posições: nenhum objeto flutuando ou atravessando outro.
- CI: a cada push um robô joga a história inteira; tags `v*` geram os executáveis de Linux e Windows.
