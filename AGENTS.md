# Personagem principal

A especificação oficial e imutável fornecida pelo usuário está em
`art/characters/main-official-v1/spec.py`; consulte também o README dessa pasta.
Use suas matrizes e índices de subpaleta exatos para o personagem principal.
Não gere conceitos aproximados nem retome os modelos experimentais anteriores.
As poses estáticas têm 16×24 pixels e usam seis sprites 8×8 sem overlays,
dois sprites por scanline, com subpaletas distintas para cabeça, tronco e pernas.
Não altere essas matrizes, cores ou arquitetura sem nova orientação do usuário.
As ROMs antigas são histórico; sua existência não substitui essa especificação.

A caminhada oficial agora vem das matrizes fornecidas pelo usuário em
`art/characters/official-walk-v1/matrizes.json`, com a correção expressa de
Y=10 em PASSO_1_COSTAS e PASSO_3_COSTAS. Não redesenhar nem substituir seus
quadros por animações locais. As caminhadas main-walk-side-v1/v2 produzidas
aqui foram rejeitadas pelo usuário e são apenas histórico, apesar de descrições
antigas de aprovação. Os quadros externos incluem oscilação de um pixel;
não aplicar a regra antiga de cabeça fixa a eles. Os repousos permanecem
idênticos à especificação estática. A integração atual está em game/walk-lab.

O exercício didático independente em `game/tutorial-garden` usa o personagem
16×16 e os cenários desenhados pelo usuário nos arquivos Pixelorama em sua
pasta `source`. Não substituir esses desenhos pelo personagem oficial 16×24,
nem redesenhar ou quantizar seus pixels sem solicitação. A animação permanece
frontal em qualquer direção. Este exercício não redefine a arte do jogo principal.
