# Caminhada oficial externa — matrizes v1

[Prancha das 15 poses](prancha-matrizes.png).

Fonte: matrizes fornecidas pelo usuário a partir do outro ambiente de arte.
`matrizes.json` preserva as 15 poses: repouso + quatro fases para perfil
direito, frente e costas. A única correção aplicada é a expressamente enviada
pelo usuário: Y=10 em PASSO_1_COSTAS e PASSO_3_COSTAS contém
`.KUUUUUUUSUUUUK.`. Nenhum outro pixel foi redesenhado.

Os três repousos são idênticos à especificação estática oficial. As animações
locais anteriores foram rejeitadas pelo usuário e não são utilizadas.

## Exportação

- 16×24 pixels por pose; Y=23 transparente.
- Seis sprites 8×8 sem overlays, dois por scanline.
- Seis tiles lineares T0–T5, 96 bytes de CHR por pose.
- PNGs transparentes com os valores RGBA oficiais, sem suavização.
- Cabeça: índices 0/1/2/3 = transparente/$0F/$27/$37.
- Tronco: transparente/$0F/$12/$37.
- Pernas: transparente/$0F/$17/$0F não usado.

A oscilação vertical já está desenhada nas matrizes. Não deslocar novamente
o metasprite para simular esse movimento. O preto comum às três subpaletas
acomoda as linhas de contorno que atravessam a divisão dos tiles; os outros
símbolos continuam respeitando a subpaleta de cada faixa.

`build.py` valida as 360 linhas e exporta todos os PNGs e CHRs. Cada CHR é
decodificado e comparado ao PNG: resultado idêntico. `validacao.txt` registra
o resultado. `layout.json` descreve a ordem e os endereços usados no laboratório.

| Grupo | Índices de tiles | Endereços PPU |
| --- | --- | --- |
| Perfil direito | $00–$1D | $1000–$11DF |
| Frente | $1E–$3B | $11E0–$13BF |
| Costas | $3C–$59 | $13C0–$159F |

Cada grupo contém repouso, passo 1, passo 2, passo 3 e passo 4.
O perfil esquerdo usa o mesmo grupo lateral com espelhamento OAM e troca das
colunas. A prancha é uma exportação das matrizes, não captura de uma ROM.
