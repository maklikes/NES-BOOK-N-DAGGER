# Primeira pescaria — v0.1

## Escopo implementado

- Cabana, caminho e riacho conectados por passagens físicas no mapa.
- Pedido inicial da mãe: dois peixes para o jantar.
- Dois locais alternados para um ponto de pesca ativo, com marca animada.
- Pesca automática iniciada com A, interrompida por B, direcional, mudança
  do ponto ou bolsa cheia. Sem minigame, turnos ou cenas separadas.
- Capturas espaçadas entre aproximadamente 4 e 7 segundos em NTSC.
- Primeiro ponto dura 960 quadros simulados; os seguintes duram 1.024–1.279.
  O relógio do ponto só anda no riacho, fora de diálogos e da pausa.
- Bolsa de seis peixes; entrega de dois uma vez, mantendo os excedentes.
- Cesto persistente durante a sessão, capacidade 999; excesso fica na bolsa.
- Continuação livre da atividade após entregar o jantar.
- Orc pescador com duas falas curtas, placa e objetos examináveis na cabana.
- Animação de caminhada, vara/linha, água e marca do ponto de pesca.
- Trilha original de 64 passos, aproximadamente 25,6 segundos por ciclo em
  NTSC, com pulso, segundo pulso e baixo triangular; efeitos curtos no ruído.

## Arquitetura NES

Mapper 0, NROM-256, iNES 1.0, 32 KiB PRG ROM e 8 KiB CHR ROM, 40.976 bytes.
Sem BIOS, cartucho especial, expansão de áudio, DPCM, bateria ou assets externos.
`assets.py` cria tiles, sprites, mapas, colisões, texto e as tabelas da música.
O sequenciador em `main.s` escreve diretamente na APU. NEXXT e FamiStudio não
foram usados nesta primeira implementação; não há projeto nativo desses editores.

Lógica, leitura de controles, áudio e preparação de OAM rodam no laço principal.
NMI faz DMA e atualizações PPU pequenas, com ponteiro separado dos temporários
da lógica. Trocas de tela esperam um NMI que desliga a renderização, copiam
1.024 bytes e reativam a imagem no NMI seguinte. Pausa congela a simulação,
mas não a trilha. Um P no topo indica a pausa.

Colisão usa os pés da personagem, consultando quatro pontos em mapas de
colisão alinhados a páginas de 256 bytes. Troncos, água, móveis, paredes e pés
de NPCs têm limites físicos. Elementos ilustrativos de copa não são obstáculos
por inteiro. A velocidade diagonal não é normalizada nesta versão.

## Verificações funcionais

`check.lua` percorre as três telas usando controles, sem escrever estados de
missão, peixes ou armazenamento na RAM. `resultado-fceux.txt` contém a execução.

Foram exercitados:

- Pedido inicial, A mantido sem repetir diálogo, direções opostas e Select.
- Mãe sem peixes suficientes e cesto vazio, sem retirar ou criar recursos.
- Transições cabana/caminho/riacho e as duas falas do pescador.
- Tentativa de pesca fora de alcance e colisão com a água.
- Lançamento, captura automática, pausa, indicador P e música durante pausa.
- B e direcional interrompendo a atividade.
- Mudança do ponto durante uma tentativa, sem perda de peixes coletados.
- Localização da marca, bolsa cheia e impossibilidade de ultrapassar seis.
- Variação de paleta da água.
- Retorno, entrega exata de dois peixes, A mantido sem entregar repetidamente.
- Missão já concluída preservando os peixes de novas viagens.
- Depósito, HUD, ausência de duplicação e acumulação em outra viagem.
- Retomada da pesca após a tarefa e persistência entre telas.
- Progressão da melodia e efeitos chegando aos registradores da APU.
- Orçamento das escritas PPU e oito cópias completas de tela.
- Reset limpando todos os dados da sessão e reabrindo o pedido inicial.

A transferência de telas é feita com renderização desligada e não é comparada
ao orçamento de VBlank. As atualizações incrementais são comparadas com um
limite conservador de 2.200 ciclos de CPU NTSC a partir da entrada do NMI.
Este teste não prova a precisão de todas as bordas de PPU, que têm uma limitação
conhecida no FCEUX, nem substitui teste no hardware.

## Áudio

Além dos hooks da APU na sequência funcional, uma captura de sinal foi feita
com som habilitado no FCEUX e o driver de saída para disco do SDL. A gravação
PCM apresentou sinal variável, não silencioso, sem atingir os extremos de
clipping de 16 bits. Métricas estão em `audio-validacao.txt`.

O parâmetro antigo `--soundrecord` do frontend não iniciou um WAV; por isso a
prova usou a saída SDL. Essa captura comprova sinal de áudio, não latência de
um dispositivo físico, sincronismo perfeito de reprodução ou qualidade musical
subjetiva. A apreciação e o balanço da trilha ainda precisam de feedback humano.

## Reproduzir

Na raiz do repositório, no ambiente preparado:

```sh
export PATH=/workspace/nes-tools/cc65/bin:$PATH
make -C game/first-river
python3 game/first-river/run_check.py
```

O runner escreve relatório, log e capturas GD em `/workspace/artifacts/first-river`.
Ele verifica conclusão e encerra o grupo de processos em erro/timeout.
`NES_CAPTURE=0` pula apenas as capturas demoradas, mantendo as asserções.
Capturas PNG incluídas são da ROM real executada no FCEUX.

Para uma prova curta de áudio, `audio-probe.lua` avança 600 quadros e fecha
o emulador. O wrapper headless padrão usa som desligado; captura de áudio
requer executá-lo com som habilitado e um backend SDL adequado.

## Limites e próximos testes do usuário

Alvo NTSC. Novo recorte não testado ainda no MesenCE do usuário nem em hardware.
Não há salvamento permanente: Reset ou desligar apaga a sessão. A capacidade
999 e a proteção de excesso estão no código; a sequência funcional percorre
depósitos comuns, não centenas de viagens até o limite.

O ritmo, a duração percebida, o conforto da pesca, as cores e a música precisam
ser avaliados jogando. Não foi medida uma duração humana de 5–10 minutos.
Não há combate, XP, classes, economia, outras skills ou mapa maior neste recorte.
