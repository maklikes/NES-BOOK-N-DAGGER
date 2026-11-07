# Estudo de arte — pescaria v0.2

## Referências pesquisadas

Foram consultadas capturas de jogos de NES no catálogo público Libretro
Thumbnails. A seleção é uma referência de direção de arte, não um ranking
objetivo dos melhores gráficos do console.

| Jogo | Aspectos observados e aplicados ao estudo |
| --- | --- |
| **Crystalis** | Separação entre chão, vegetação e relevo; caminhos claros; silhueta da personagem destacada do cenário. É a referência principal de perspectiva e leitura. |
| **Willow** | Vegetação agrupada, luz e sombra dentro das copas, arquitetura integrada ao terreno e transições entre superfícies. Referência de densidade e identidade ambiental. |
| **StarTropics** | Personagem e elementos interativos legíveis sobre o mapa; contraste entre água e terreno. Referência para trabalhar a figura por direção. |
| **Kirby’s Adventure** | Cores luminosas, massas grandes legíveis e uso controlado de contraste. Referência de cor; não de perspectiva ou de estrutura de fase. |
| **Little Samson** | Separação de planos e acabamento em silhuetas e superfícies. Referência de acabamento; sua perspectiva lateral não foi transplantada para o jogo. |

Capturas consultadas:

- [Crystalis](https://github.com/libretro-thumbnails/Nintendo_-_Nintendo_Entertainment_System/blob/master/Named_Snaps/Crystalis%20%28USA%29.png)
- [Willow](https://github.com/libretro-thumbnails/Nintendo_-_Nintendo_Entertainment_System/blob/master/Named_Snaps/Willow%20%28USA%29.png)
- [StarTropics](https://github.com/libretro-thumbnails/Nintendo_-_Nintendo_Entertainment_System/blob/master/Named_Snaps/StarTropics%20%28USA%29.png)
- [Kirby’s Adventure](https://github.com/libretro-thumbnails/Nintendo_-_Nintendo_Entertainment_System/blob/master/Named_Snaps/Kirby%27s%20Adventure%20%28USA%29.png)
- [Little Samson](https://github.com/libretro-thumbnails/Nintendo_-_Nintendo_Entertainment_System/blob/master/Named_Snaps/Little%20Samson%20%28USA%29.png)

Os tiles, mapas, sprites e ciclos de caminhada desta ROM são originais.
O estudo usa observações de composição e legibilidade das referências; não
incorpora seus gráficos. As capturas de referência não estão incluídas na ROM.

## Direção escolhida: manhã clara junto ao rio

- **Casa:** piso de madeira clara, paredes brancas, tapete azul, cama e janela
  distintas, lareira em tons quentes claros e pequena estante. O vermelho
  dominante da versão anterior foi retirado do interior.
- **Caminho:** fachada com telhado, porta e janelas, chão arenoso com bordas
  menos regulares, árvores com volumes de luz e sombra, raízes e flores.
- **Riacho:** água azul-ciano mais clara, reflexos curtos sem uma grade contínua,
  margens arenosas, barranco, pedras e vegetação da outra margem.
- **Personagens:** cabelo, rosto, roupa, braços e botas mais separados. O herói
  tem frente, costas e perfil. A esquerda espelha corretamente os tiles do
  perfil direito. O ciclo lateral inclui passada, posição neutra e passada
  oposta; ele deixa de caminhar sempre olhando para a câmera.
- **Pesca:** pose de perfil com braços voltados à vara. O ponto continua usando
  brilho contrastante e a mesma posição/atividade da versão funcional.

## Construção gráfica

O estudo mantém mapper 0 / NROM e usa 8 KiB de **CHR RAM** em vez de um único
conjunto global de CHR ROM. Isso dá uma tabela de fundo própria de 4 KiB para
cada área e uma tabela de sprites de 4 KiB compartilhada. As tabelas de fundo
são descomprimidas ao trocar de tela, com renderização desligada.

Cada tile tem 8×8 pixels e duas bitplanes. Os atributos escolhem uma única
subpaleta em cada região de 16×16. As árvores, os caminhos e os móveis foram
compostos levando essas regiões em conta, inclusive transições de paleta.

A cabeça do herói usa uma subpaleta de sprites e o torso/pernas usam outra:
isso permite distinguir cabelo/pele e roupa sem adicionar camadas de sprites.
Cada personagem continua com seis sprites 8×8. O perfil esquerdo combina flip
horizontal com inversão das colunas do metasprite, mantendo a silhueta correta.

### Uso de tiles

| Área | Tiles próprios de cenário | Posições reservadas para fonte/branco | Limite da tabela |
| --- | --- | --- | --- |
| Cabana | 118 | 46 | 256 |
| Caminho | 130 | 46 | 256 |
| Riacho | 96 | 46 | 256 |

Tiles idênticos são compartilhados. A tabela comum de sprites ocupa 4 KiB;
as primeiras 90 posições comportam personagens, poses, brilho e vara.
Os arquivos `.chr`, `.nam` e `.pkb` são gerados por `assets.py` em `build/`.

## Como comparar

- [Cenários lado a lado](comparacao-cenarios.png): capturas reais das duas ROMs
  no mesmo emulador, ampliadas com vizinho mais próximo, sem suavização.
- [Movimento lado a lado](comparacao-movimento.gif): a mesma sequência de
  controles nas duas ROMs. O GIF recorta a área do mundo e exibe quadros
  amostrados com duração maior para facilitar a inspeção; não mede o FPS da ROM.

O objetivo é avaliar o conjunto dentro do jogo: luminosidade, leitura das
superfícies, silhuetas e movimento. A versão não estabelece sozinha um padrão
artístico aprovado; esse padrão depende da comparação e do feedback do usuário.
