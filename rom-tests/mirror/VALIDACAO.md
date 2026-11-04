# Interação e puzzle do espelho — v0.1

## Escopo

Derivado da sala de controles aprovada. Movimento, mesa, paredes e pausa foram
mantidos. O armário cresceu para 48×48 pixels e tem colisão própria. A/B deixam
de testar cores e passam a examinar/voltar. Não há áudio ou outra sala.

## Estados do puzzle

0. Nada descoberto: porta e gaveta bloqueadas.
1. Espelho examinado: a diferença do puxador foi percebida.
2. Gaveta examinada após a pista: o fecho foi solto.
3. Porta aberta: livro e adaga visíveis no compartimento.
4. Objetos recolhidos: compartimento vazio e inventário registrado no topo.

A mudança 3→4 exige uma nova interação no mundo. A inspeção não teletransporta
a personagem. A personagem deve alcançar o armário; nada acontece à distância.
Examinar a mesa ou tentar interagir longe gera resposta sem alterar o puzzle.

## Interface

Modo 0: exploração. Modo 1: menu de inspeção do armário. Modo 2: leitura.
Menus e leituras param o movimento; o tempo de leitura é livre. Start pausa;
Select reposiciona e fecha a interface, preservando descobertas e inventário.
Reset da ROM limpa o progresso. Não há persistência em bateria.

Cada mensagem ocupa três linhas de 32 tiles, com margem de duas colunas,
nos endereços de nametable $2320, $2340 e $2360. O script de assets rejeita
linhas que ultrapassem o espaço reservado. As letras usam uma fonte bitmap
própria; esta versão não implementa acentos.

Atualizações de texto, armário e inventário são enfileiradas: no máximo um
trabalho de fundo por quadro, além dos sprites e do indicador de pausa.
As transições visuais podem levar alguns quadros para completar.

## Validação automatizada

O script `check.lua` exercita o jogo com controles emulados, sem escrever estados
do puzzle na RAM. Foram verificados:

- Interação fora de alcance e inspeção da mesa.
- Colisão com mesa, limites da sala e armário.
- Aproximação do armário por caminho livre.
- Pausa, tecla Start mantida e reposicionamento.
- Menu bloqueando movimento e cancelamento sem progresso.
- Porta antes da pista, gaveta antes da pista, porta antes de soltar o fecho.
- Descoberta do reflexo, fecho, abertura e coleta em interações separadas.
- A mantido sem acionar várias etapas e inspeções repetidas sem duplicações.
- Nametable atualizada para armário aberto e depois vazio.
- Inventário com os dois itens e preservação ao usar Select durante a pausa.
- Reset limpando inventário e progresso e restaurando o armário fechado.
- Orçamento das escritas PPU durante as transições.

O resultado e a medida de ciclos da compilação final estão em
`resultado-fceux.txt`. Capturas do FCEUX são incluídas como evidência de execução,
não como imagens conceituais geradas.

## Repetir

```sh
export PATH=/workspace/nes-tools/cc65/bin:$PATH
make -C /workspace/NES-BOOK-N-DAGGER/rom-tests/mirror
mkdir -p /workspace/artifacts/rom-mirror
NES_MIRROR_OUTPUT=/workspace/artifacts/rom-mirror \
  timeout 90s /workspace/nes-tools/emulator/bin/fceux-headless --no-config 1 \
  --loadlua /workspace/NES-BOOK-N-DAGGER/rom-tests/mirror/check.lua \
  /workspace/NES-BOOK-N-DAGGER/downloads/espelho-v0.1.nes
```

O teste escreve relatório e capturas GD no diretório indicado. Uma asserção
interrompe o script e pode deixar a janela do emulador aberta até o timeout;
sucesso requer `TOTAL 39 checks passed`, não apenas saída do processo.

## Limitações

NROM-128, NTSC, 16 KiB PRG + 8 KiB CHR. A compatibilidade física e o novo fluxo
no MesenCE do usuário ainda precisam de teste. Não altera as ROMs anteriores.
O orçamento observado em emulação não prova precisão de todas as bordas de
VBlank; permanece a limitação conhecida do FCEUX. Não há efeitos de raster.
