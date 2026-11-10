# Kit para o usuário montar seu mapa no Pixelorama

[Baixar o tileset nativo](tileset-exercicio.png): no GitHub, abra o PNG e use
**Download raw file**. Imagem RGBA de **80×16**, cinco peças 16×16 lado a lado:

1. Grama.
2. Arbusto.
3. Borda esquerda do caminho.
4. Centro do caminho.
5. Borda direita do caminho.

Os pixels são cópias exatas dos PNGs exportados dos projetos do usuário.
`tileset.json` registra as fontes, hashes e propriedades propostas de colisão.
As posições de coluna desse manifesto não presumem os IDs internos atribuídos
pelo Pixelorama ao importar o tileset.

## Primeiro mapa

No Pixelorama 1.2.4, criar um projeto **256×192** com fundo transparente,
um quadro e uma camada de tilemap com peças retangulares **16×16**. Isso
resulta em 16 colunas e 12 linhas, correspondentes à área de cenário do
exercício anterior. A interface do programa tem a opção **Add Tilemap Layer**
no menu de tipos de camada (seta junto ao botão de adicionar camada).

Importar o PNG como tileset, sem redimensionar. Usar o modo de colocação
de tiles para montar o mapa, preservando as peças. O ajuste fino dos diálogos
de importação será orientado pela interface apresentada pelo usuário.

O personagem é separado do cenário: não pintá-lo nem incorporá-lo ao mapa.
Escolher sua posição inicial posteriormente, em uma célula livre.
Primeiro trabalhar apenas com as cinco peças e sem rotações/espelhamentos,
para manter a correspondência direta com os recursos já desenhados.

As peças atuais permitem caminhos retos verticais. Curvas, bordas superior
e inferior e terminações precisam de novas peças desenhadas pelo usuário.
O mapa pode começar inteiramente preenchido com grama e depois receber
arbustos e caminhos conforme a organização desejada.

## Entrega e integração futura

Salvar o projeto `.pxo` editável e exportar também um PNG **256×192**,
sem recorte, em escala 100%, sem filtros. O mapa deve estar totalmente
preenchido com as peças. A escolha de rota e posição dos obstáculos é do usuário.

Este kit não altera a ROM. O programa atual monta o cenário no gerador Python;
será necessário adaptar a importação para consumir o mapa montado pelo usuário.
A imagem rasterizada permite identificar as peças por células de 16×16 e
validar a montagem sem depender dos IDs específicos do editor.

Propriedades planejadas: grama e caminho caminháveis; arbusto bloqueado
no quadrado inteiro. Essas propriedades são dados do jogo, não efeitos da
imagem. Grama/arbusto usam uma subpaleta de background e o caminho usa outra,
com a atribuição feita por célula 16×16 durante a conversão para o NES.
