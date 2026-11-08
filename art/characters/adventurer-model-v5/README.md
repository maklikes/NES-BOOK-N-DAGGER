# Aventureiro — modelo estático completo v5

[Abrir a prancha](prancha-modelo-v5.png).

Frente e costas propostas a partir do perfil v4 aprovado visualmente pelo
usuário. O perfil v4 foi preservado: PNG e CHR são idênticos aos anteriores.

As novas vistas procuram manter o topo suave do cabelo, a franja irregular,
orelhas discretas, túnica azul, faixa dourada e mãos até a altura do quadril.
A faixa acompanha o mesmo ombro nas vistas de frente e de costas.

Cada sprite ocupa 16×24 pixels reais. A prancha apresenta ampliação 12× e
amostras 1× / 4× sobre verde e bege. Abra em tamanho original para preservar
essas escalas. Cores de prévia Wavebeam, sem simulação de CRT.

## Recursos e verificação

- `frente.png`, `costas.png`, `perfil.png`: RGBA com transparência, 16×24.
- Arquivos `.chr`: dez tiles NES 8×8 por vista, 160 bytes cada.
- `sprites.json`: pixels, posições dos sprites e subpaletas.
- `build.py`: geração e conferência por decodificação do CHR exportado.
- `validacao.txt`: comparação entre os pixels exportados e os PNGs.

Mantém o arranjo do perfil v4: seis tiles de base e quatro sobreposições para
pele nas faixas central e inferior. Dez posições de sprites por vista,
máximo de quatro por linha; três subpaletas e cinco cores no conjunto.
Cada sprite respeita três cores visíveis mais transparência.

Os três arquivos CHR foram decodificados e reproduzem os respectivos PNGs.
O perfil foi comparado byte a byte à v4. Isso valida a representação técnica;
frente e costas ainda aguardam aprovação visual. Não houve atualização
de ROM, animação ou teste de execução nesta entrega.
