# Aventureiro — reconstrução estática v1

[Ver a prancha ampliada](prancha-aventureiro-16x24.png)

[Baixar o pacote completo](../../../downloads/aventureiro-estatico-16x24-v1.zip)

Para baixar, abra o arquivo no GitHub e use **Download raw file** (seta para
baixo). A prancha também pode ser aberta em tamanho original e salva pelo navegador.

## Conteúdo

- `frente.png`, `costas.png`, `perfil.png`: imagens RGBA reais de **16×24 pixels**,
  com fundo transparente, sem interpolação.
- `prancha-aventureiro-16x24.png`: apresentação ampliada com as três vistas.
- `frente.chr`, `costas.chr`, `perfil.chr`: oito tiles NES 8×8 por vista,
  128 bytes cada. São recursos gráficos, não ROMs executáveis.
- `sprites.json`: pixels de origem, posições dos oito sprites e subpaletas.
- `build.py`: construtor e verificador usado no ambiente; usa Pillow e a prévia
  Wavebeam instalada com FCEUX em `/workspace/nes-tools/emulator`.
- `validacao.txt`: dimensões, exportação/decodificação CHR idênticas e contagem
  máxima de sprites por linha para o personagem isolado.

## Composição

As três vistas ocupam seis posições de 8×8 (duas colunas e três linhas).
Duas sobreposições na faixa central acrescentam pele/colar. Assim são oito
sprites de hardware por pose, no máximo quatro sobre uma linha do personagem
isolado. Cada sprite usa três cores visíveis mais transparência.

A prévia usa as cores da paleta Wavebeam para os índices NES $07, $27, $37,
$11 e $17. O RGB percebido depende da paleta de emulação e do sinal de vídeo.
A fonte conceitual é a proposta 2 — Aventureiro escolhida pelo usuário; esta
é sua primeira adaptação ao tamanho nativo, ainda para aprovação visual.

Não há animação nem teste de integração desta versão na ROM. Nenhuma ROM foi
alterada por esta entrega. O sprite isolado não comprova o orçamento total de
sprites do cenário final, que precisará ser conferido na integração.
