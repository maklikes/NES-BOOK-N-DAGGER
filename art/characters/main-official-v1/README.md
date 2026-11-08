# Personagem principal — especificação oficial imutável

[Abrir a prancha oficial](prancha-oficial.png).

`spec.py` contém as matrizes FRONT, PROFILE e BACK e os valores RGBA fornecidos
pelo usuário, transcritos sem redesenho. Esta é a fonte oficial para futuras
integrações, substituindo os estudos visuais anteriores como referência do
personagem. Nenhuma ROM ou animação foi atualizada nesta entrega.

## Composição obrigatória

- 16×24 pixels por vista.
- Seis sprites 8×8 sem overlays: T0/T1, T2/T3, T4/T5.
- Posições relativas: (0,0), (8,0), (0,8), (8,8), (0,16), (8,16).
- Dois sprites por scanline; três subpaletas de sprite.
- Topo em Y=0; botas até Y=22; Y=23 transparente.
- Fechamentos do queixo e da túnica em Y=7 e Y=15, respectivamente.

| Região | Subpaleta | Índices 0, 1, 2, 3 |
| --- | --- | --- |
| T0/T1 — cabeça | 0 | transparência, $0F, $27, $37 |
| T2/T3 — tronco | 1 | transparência, $0F, $12, $37 |
| T4/T5 — pernas | 2 | transparência, $0F, $17, $0F não usado |

As alocações explícitas por tile foram seguidas: H usa $27; B usa $17.
A menção alternativa a $18 para H não foi aplicada. A alternativa de compartilhar
a subpaleta 0 nas pernas não preservaria $17 e, portanto, não foi aplicada.

Os PNGs usam exatamente os RGBA informados. O 2C02 recebe índices de cor,
não valores RGB; a aparência no console depende do sinal e da televisão.
Isso não autoriza substituir os índices ou corrigir as matrizes.

## Arquivos

- `spec.py`: matrizes e cores oficiais, sem modificações artísticas.
- `frente.png`, `perfil.png`, `costas.png`: RGBA transparente 16×24.
- `frente.chr`, `perfil.chr`, `costas.chr`: seis tiles cada, 96 bytes.
- `sprites.json`: matrizes, cores, índices e composição dos sprites.
- `sprite-subpalettes.pal`: 12 bytes, três grupos de quatro entradas;
  entrada transparente preenchida com $0F. Não é uma paleta RGB de emulador.
  Ao carregar a PPU, respeitar o espelhamento das entradas de fundo/transparência.
- `prancha-oficial.png`: vistas 12× e amostras 1× / 4× sobre dois fundos.
- `build.py`: geração determinística e verificação dos bitplanes exportados.
- `validacao.txt`: resultados da exportação e reconstrução.

Executar `python3 art/characters/main-official-v1/build.py` com Pillow instalado.
As três vistas foram reconstruídas do CHR e comparadas aos PNGs: idênticas.
As dimensões, símbolos por subpaleta, alinhamentos e consumo por linha foram
verificados. Não foi realizado teste de execução desta versão na ROM.
