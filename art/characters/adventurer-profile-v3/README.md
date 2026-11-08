# Perfil estático — reconstrução v3

[Abrir a prancha](prancha-perfil-v3.png): conceito à esquerda; sprite real
de 16×24 pixels à direita, ampliado 16× sem suavização. Abaixo, amostras
1× e 4× sobre verde. Abra em tamanho original para preservar essas escalas.

Somente o perfil direito foi reconstruído. Frente, costas, caminhada e ROMs
permanecem como estavam. Esta proposta aguarda avaliação visual.

O desenho parte das proporções do conceito escolhido: cabeça e rosto com
profundidade, ombro e peito mais largos que a cintura, braço separado da
túnica e mão visível. O cabelo acompanha a referência, com mecha superior e
contorno da nuca recuado em relação à massa da cabeça.

## Arquivos

- `perfil.png`: RGBA 16×24 pixels, fundo transparente.
- `perfil.chr`: dez tiles 8×8, 160 bytes; recurso gráfico, não executável.
- `sprites.json`: pixels e composição dos sprites de hardware.
- `build.py`: gera a prancha e confere a exportação CHR.
- `validacao.txt`: resultado da comparação entre PNG e CHR decodificado.
- `conceito-referencia.png`: imagem conceitual anterior, preservada como referência.

Os seis tiles de base usam as três subpaletas anteriores; quatro tiles de
sobreposição acrescentam pele nas faixas central e inferior. A mão desce até
a faixa inferior, exigindo duas posições de sobreposição adicionais em relação
à v1/v2. São dez posições de sprites, no máximo quatro por linha. Alguns tiles
de sobreposição são transparentes; este é um arranjo simples, sem otimização.
Cada sprite usa até três cores e transparência; o conjunto mantém os cinco
índices NES anteriores. Prévia RGB Wavebeam, sem simulação de CRT.

A reconstrução do CHR exportado é idêntica ao PNG. Isso verifica o formato
técnico do desenho; a qualidade visual ainda precisa ser aprovada. Não houve
teste em execução ou alteração de ROM nesta entrega.
