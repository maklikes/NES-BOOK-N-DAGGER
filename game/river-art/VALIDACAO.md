# Pescaria — estudo de arte v0.2

## Escopo

Redesenho da cabana, fachada, caminho, margem, água e personagens. A pesca,
capacidade, ritmos, missão, armazenamento e diálogos são os da v0.1 aprovada.
Há pequenos ajustes de colisão para a nova fachada e a cerca visível no caminho.

O herói tem frente, costas, perfil direito e perfil esquerdo espelhado. Os ciclos
laterais alternam passada, neutro e passada oposta; os braços do perfil também
mudam. Poses paradas preservam a direção. A pesca usa uma pose lateral própria.
Mãe e orc têm desenhos distintos e piscam fora dos diálogos.

## Formato e carregamento

NROM-256, mapper 0, iNES 1.0, 32 KiB PRG ROM e 8 KiB CHR RAM. O arquivo tem
**32.784 bytes**: 16 de cabeçalho e 32.768 de programa/dados. O byte CHR ROM do
cabeçalho é zero, indicando gráficos em RAM. Continua sendo uma ROM nativa de
NES, sem expansão gráfica ou de áudio.

Fundos e sprites são armazenados comprimidos em PRG e enviados à PPU enquanto
a renderização está desligada. A tabela de sprites é carregada no boot. Cada
mudança de área transfere 4.096 bytes de fundo, 32 bytes de paleta e 1.024 bytes
de nametable/atributos: **5.152 escritas**. Pode haver um breve escurecimento
durante a troca de tela. A música agora é atualizada pelo NMI, inclusive durante
o carregamento dos gráficos, mantendo as mesmas notas do tema anterior.

Os atributos continuam selecionando uma subpaleta por região 16×16. Cada tile
é 8×8, com quatro índices. Cada sprite usa três cores visíveis e transparência.
A cabeça e o corpo do herói usam subpaletas distintas em linhas de tiles
diferentes, sem camadas adicionais de sprites para acrescentar cores.

## Verificações

O relatório completo está em `resultado-fceux.txt`. A suíte preserva o percurso
funcional da v0.1 e acrescenta verificações de arte/integração:

- Comparação byte a byte entre as tabelas CHR geradas e a RAM da PPU, para
  cada um dos três fundos e para a tabela comum de sprites.
- Perfil direito, espelhamento esquerdo com troca das colunas, costas e frente.
- Dois passos laterais distintos e pose neutra.
- Paleta da cabeça diferente da paleta do torso/pernas.
- Contagem de sprites por linha enquanto a renderização está habilitada.
  O RAM de OAM ainda não inicializado no boot não participa da contagem.
- Cópias completas dos gráficos/paletas/mapas, orçamento das atualizações em
  VBlank e toda a missão de pesca, pausa, entrega, armazenamento e reset.

`validate_art.py` verifica formato, descompressão dos dados, limites de tabelas,
integridade da fonte entre bancos, quadros de animação distintos e paletas.

## Repetir

```sh
export PATH=/workspace/nes-tools/cc65/bin:$PATH
make -C game/river-art
python3 game/river-art/validate_art.py
python3 game/river-art/run_check.py
```

`NES_CAPTURE=0` pula apenas as capturas demoradas. O runner exige um relatório
completo e encerra o emulador em erro/timeout. Resultados locais ficam em
`/workspace/artifacts/river-art`.

## Comparação

As PNGs e o GIF são feitos de frames reais executados pelo FCEUX. O GIF usa
`motion.lua` com a mesma sequência de controles nas duas ROMs, sem escrever
posição ou estado na RAM. O recorte exclui a interface inferior do emulador;
os quadros são ampliados sem suavização e exibidos mais lentamente para inspeção.
Não é uma medição da cadência real de apresentação, que deve ser avaliada jogando.

## Limites

Alvo NTSC, sem salvamento permanente, combate ou sistemas novos. Ainda precisa
do teste do usuário no MesenCE e no NES/flashcart físico. A limitação conhecida
de precisão fina de VBlank do FCEUX não é usada como recurso gráfico.
O estudo é uma proposta de padrão artístico, ainda sujeita à aprovação visual.
