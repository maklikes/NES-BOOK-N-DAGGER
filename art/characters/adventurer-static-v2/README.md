# Aventureiro — ajustes estáticos v2

[Abrir prancha comparativa](prancha-aventureiro-v2-comparacao.png).
Linha superior: v1 usada no laboratório de caminhada. Linha inferior: revisão.
Cada vista tem uma ampliação 8× e uma amostra em 1× sobre verde.
As amostras 1× dependem de o visualizador não redimensionar a prancha.

Revisão baseada no teste do usuário no Phantom System com EverDrive e CRT de
14 polegadas: nariz menor, frente do tronco mais reta, orelhas frontais curtas
e simétricas, cabelo mais compacto atrás e pequenas mechas no topo.
Roupa, paleta e dimensões foram mantidas.

## Arquivos técnicos

- `frente.png`, `costas.png`, `perfil.png`: RGBA 16×24 com transparência.
- `sprites.json`: pixels e composição em sprites de hardware.
- `frente.chr`, `costas.chr`, `perfil.chr`: oito tiles NES por vista, 128 bytes.
- `build.py`: gera as imagens, exporta CHR e confere a reconstrução dos tiles.
- `validacao.txt`: resultados da verificação dos sprites estáticos.

Os três conjuntos CHR foram decodificados e comparados aos PNGs: idênticos.
Mantêm oito sprites por vista, máximo de quatro por linha e três subpaletas;
cada sprite usa até três cores e transparência. Cores NES $07, $27, $37,
$11 e $17; prévia RGB Wavebeam.

Esta prancha técnica contém os pixels reais; a imagem conceitual gerada à parte
serve somente de referência visual. A revisão v2 ainda aguarda aprovação.
Não foram modificadas ROMs nem animações, e estes novos sprites não foram
testados em execução.

## Registro do teste em hardware da v1

O usuário relatou execução de `aventureiro-caminhada-v0.1.nes` e
`primeira-pescaria-arte-v0.2.nes` no Phantom System, via EverDrive, em uma CRT
de 14 polegadas. A leitura visual foi considerada mais agradável que no Mesen,
com ressalvas sobre a silhueta do personagem. É uma observação desse conjunto
de equipamento; não equivale a validar esta revisão v2 ou todos os consoles.
