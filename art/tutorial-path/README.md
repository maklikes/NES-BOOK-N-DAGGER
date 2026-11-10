# Caminho de terra — prévia das peças do usuário

[Abrir prancha](prancha-caminho.png).

Montagem de conferência, sem modificar os pixels das três peças recebidas.
A grama e o personagem vêm do exercício anterior em `game/tutorial-garden`.
Não houve integração nem alteração de ROM nesta entrega.

- `source/`: os três projetos `.pxo` originais.
- `borda-esquerda.png`, `centro.png`, `borda-direita.png`: PNGs nativos 16×16.
- Os três `.chr`: quatro tiles 8×8 por peça, 64 bytes, em ordem por linha.
- `pecas.png`: as três peças numa faixa de 48×16.
- `caminho-montado.png`: composição de 128×128 sem personagem.
- `caminho-com-personagem.png`: mesma composição com o personagem para escala.
- `prancha-caminho.png`: peças em 8×, montagem em 4× e montagem em 1×.
- `validation.json`: cores, hashes dos originais e resultado da exportação.

A escala 1× depende de o visualizador abrir a prancha em tamanho original.
As prévias usam os RGBA dos arquivos, sem simular CRT ou paleta de emulador.

## Regras conferidas

Cada arquivo contém uma camada visível, um quadro 16×16, sem efeitos,
com opacidade integral. As três cores opacas são exatamente:

- Verde: #00A800 → índice NES $1A.
- Terra: #8B4400 → índice NES $17.
- Terra clara: #B87018 → índice NES $27.

Subpaleta de caminho proposta: fundo compartilhado $0F, $1A, $17, $27.
A grama pura conserva sua subpaleta de três verdes. As peças estão alinhadas
a blocos 16×16, permitindo atribuir a paleta correspondente a cada região.
As duas subpaletas compartilham o mesmo fundo, $0F; nenhuma dessas peças usa
o pixel de índice 0. Não foram aplicadas recoloração ou quantização.

Cada CHR foi decodificado e comparado ao PNG nativo: os pixels são idênticos.
Esse teste valida a representação técnica, não constitui aprovação artística.

## Montagem

O trecho usa borda esquerda, centro e borda direita, repetidos verticalmente.
As peças ocupam 48 pixels de largura, incluindo as porções verdes das bordas;
a largura da terra varia conforme os recortes desenhados pelo usuário.
O centro pode ser repetido horizontalmente para ampliar o caminho.

As bordas se distinguem da grama pura porque usam um verde e dois marrons.
As marcas claras sobre as áreas verdes foram preservadas como desenhadas.
O padrão se repete a cada 16 pixels; futuras variantes podem quebrar a
repetição sem alterar as peças atuais. Curvas e terminações não estão incluídas.

Executar `python3 art/tutorial-path/build.py` com Python e Pillow para refazer
a exportação e a prancha. O script lê apenas os dados e pixels dos projetos.
