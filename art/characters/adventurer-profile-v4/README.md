# Perfil estático v4 — correções manuais do usuário

[Abrir prancha v3 / v4](prancha-perfil-v4.png).

Transcrição da diretriz enviada pelo usuário: eliminar o pixel que projeta
o nariz e suavizar o topo do cabelo, removendo a mecha elevada. As alterações
se concentram nas primeiras quatro linhas do cabelo e na linha do nariz.
O restante do desenho da v3 foi mantido.

- `perfil.png`: sprite transparente de 16×24 pixels reais.
- `perfil.chr`: dez tiles NES 8×8, 160 bytes.
- `sprites.json`: pixels, posições e subpaletas.
- `build.py`: geração da prancha e validação da exportação.
- `validacao.txt`: resultado da reconstrução dos tiles.

A prancha apresenta ampliação 16× e amostras 1× / 4× em verde. Para preservar
essas escalas, abra em tamanho original. Prévia de cores Wavebeam.

O CHR exportado, decodificado com as subpaletas, reproduz exatamente o PNG.
Mesmo arranjo da v3: dez posições de sprites, no máximo quatro por linha;
três subpaletas e cinco cores no conjunto, respeitando três cores visíveis
mais transparência por sprite de hardware.

Somente o perfil estático foi atualizado. Não há alterações de ROM, frente,
costas ou animação. A aprovação visual e a integração na ROM ficam pendentes.
