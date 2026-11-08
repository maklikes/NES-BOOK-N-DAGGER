# Caminhada lateral — proposta v1

- [Prancha de repouso + quatro fases](prancha-caminhada-lateral.png).
- [GIF de caminhada](caminhada-lateral.gif).
- [GIF em velocidade reduzida](caminhada-lateral-lenta.gif).

Somente a caminhada lateral direita, para avaliação antes de produzir ROM.
A pose de repouso é o perfil oficial, idêntico em PNG e CHR.
As quatro fases são matrizes novas: contato A, passagem A, contato B,
passagem B, em ciclo. A cabeça inteira é fixa, sem balanço vertical.
O braço alterna discretamente sua posição na faixa de paleta do tronco.

A prancha mostra as cinco poses em 10× e amostras 1× / 3×.
O GIF mostra a caminhada no lugar, nas escalas 1× / 4× / 5×, sobre verde
e bege. Abra em tamanho original para preservar essas escalas.
O repouso não entra no ciclo contínuo do GIF.

Cadência inicial proposta: oito quadros NTSC por pose, aproximadamente
133 ms. O GIF usa 130 ms por pose devido à resolução de centésimos de
segundo do formato; a versão lenta usa 260 ms. O reprodutor pode afetar
a cadência. Não é uma captura de emulador e não simula CRT.
Ainda não há deslocamento, velocidade de jogo ou contato com o cenário.

## Recursos e conferência

Cada pose é 16×24, seis sprites 8×8 sem overlays, dois por linha.
As três subpaletas e os RGBA são os oficiais, sem alterações.
Y=23 permanece transparente; cabeça Y=0..7 e barra da túnica Y=15
permanecem idênticas ao perfil oficial em todas as fases.

Cada arquivo `.chr` tem seis tiles (96 bytes). Os bitplanes exportados
foram decodificados e comparados aos PNGs: idênticos. O GIF usa uma paleta
comum com as cores oficiais explícitas; os pixels opacos da amostra 1×
também foram comparados às imagens de origem antes da gravação.

`frames.json` contém as matrizes e a ordem do ciclo; `build.py` gera
os arquivos com Pillow e importa a especificação oficial sem modificá-la.
`validacao.txt` registra as verificações dos cinco conjuntos de tiles.

Avaliar: leitura da alternância das pernas, passagem dos pés, movimento do
braço e manutenção da personalidade. Esta proposta não foi aprovada ainda.
Não houve alteração de ROM, frente, costas ou arquivo oficial.
