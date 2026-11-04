# A Adaga e o Livro — testes técnicos de NES

## Novo: interação e puzzle do espelho

ROM: [`downloads/espelho-v0.1.nes`](downloads/espelho-v0.1.nes).
Abra o arquivo e use **Download raw file**, depois **File → Open** no MesenCE.

![Puzzle no FCEUX](rom-tests/mirror/espelho.png)

- Direcionais: movimentar a personagem; perto do armário, A abre a inspeção.
- No menu do armário: Cima/Baixo escolhem o objeto, A examina e B cancela.
- Durante uma leitura: A ou B fecham o texto. Segurar A não avança várias etapas.
- Start: pausa/despausa. Select: reposiciona sem apagar o progresso do puzzle.
- No seu mapeamento: **K = A/examinar**, **J = B/voltar**, W/S navegam no menu.
- A e B agora são interação/voltar; não mudam mais a cor da roupa nesta ROM.

Explore o espelho, a gaveta e a porta. As respostas dependem das descobertas.
Abrir o compartimento mostra os objetos; recolhê-los exige uma nova interação.
O topo da tela registra os objetos coletados. Select preserva o progresso;
**Reset do emulador começa uma nova tentativa**, sem inventário ou descobertas.

Esta versão termina na coleta do livro e da adaga. Não há uso de poderes,
passagem para outra sala, combate, áudio ou salvamento permanente ainda.
A fonte atual usa texto em português sem acentos. A arte continua provisória.

Código e verificação: [`rom-tests/mirror`](rom-tests/mirror).
Compilação: `make -C rom-tests/mirror`, com ca65/ld65 no PATH.

## Novo: sala com personagem e controles

ROM: [`downloads/sala-controles-v0.1.nes`](downloads/sala-controles-v0.1.nes).
Abra o arquivo no GitHub e clique em **Download raw file** para baixar.
No MesenCE, use **File → Open** e selecione o `.nes`.

![Sala real capturada no FCEUX](rom-tests/movement/sala.png)

| Controle | Resposta esperada |
| --- | --- |
| Direcionais | Movem o personagem nas quatro direções. Paredes e mesa bloqueiam o movimento. |
| A, segurado | Muda a cor do casaco para violeta. |
| B, segurado | Muda a cor do casaco para dourado. A tem prioridade se ambos estiverem pressionados. |
| Select | Reposiciona o personagem no ponto inicial, inclusive durante a pausa. |
| Start | Alterna pausa. Segurar não alterna repetidamente. Um P aparece no topo. |

As legendas **A B SEL STA UP DN LT RT** mostram `1` quando cada botão está
pressionado e `0` quando está solto. Durante a pausa, o movimento para, mas
os indicadores e as mudanças de cor continuam funcionando.

Esta sala é um ensaio de movimentação livre nas quatro direções; não fecha
a perspectiva do jogo definitivo. Não há áudio, combate, puzzles, troca de
salas ou salvamento. Os gráficos foram desenhados para este teste, com tiles
e sprites nativos do NES; não são a arte final do jogo.

- Mapper 0, 16 KiB PRG + 8 KiB CHR, 24.592 bytes, alvo NTSC.
- 43 verificações automatizadas passaram no FCEUX 2.6.5.
- Código e validação: [`rom-tests/movement`](rom-tests/movement).
- Ainda não validada no MesenCE do usuário, NES físico ou Phantom System.

Compilar no ambiente preparado:

```sh
export PATH=/workspace/nes-tools/cc65/bin:$PATH
make -C rom-tests/movement
```

## Anterior: tela azul

Este repositório contém um teste técnico nativo de NES. Ainda não é o piloto
do jogo e não contém os cenários, personagens ou mecânicas planejados.

## Baixar e executar no Windows

1. Abra a pasta [`downloads`](downloads) nesta branch.
2. Abra **tela-azul-v0.1.nes** e clique em **Download raw file** (seta para baixo).
3. No seu emulador de NES para Windows, use **File → Open / Arquivo → Abrir**
   e selecione o arquivo `.nes` baixado.
4. O resultado esperado é **uma tela inteira azul sólida**, sem texto, animação,
   som ou resposta aos botões. Após alguns quadros de inicialização, a cor fica
   estável. A tonalidade pode variar entre paletas, emuladores e televisores.
5. Reinicie a ROM pelo comando Reset: a tela deve voltar a ficar azul.

Se conseguir abrir, informe o nome/versão do emulador e se a tela ficou azul.
Este teste confirma o caminho compilação → GitHub → Windows → emulação.
Não valida ainda gameplay, leitura de controles, áudio ou hardware real.

## Formato

- Arquivo `.nes` com cabeçalho iNES 1.0.
- Mapper 0 (NROM-128), 16 KiB de PRG ROM e 8 KiB de CHR ROM.
- Tamanho total: **24.592 bytes**.
- Sem BIOS, dependências externas, salvamento ou dados de jogos comerciais.
- O programa mantém a renderização desligada e configura a cor universal de
  fundo da PPU como `$01`. Isso é saída nativa de vídeo do NES.
- Alvo inicial: NES NTSC. Não utiliza efeitos com temporização fina de PPU.

## Compilar

Requer `ca65`, `ld65` (cc65) e Make. No ambiente preparado:

```sh
export PATH=/workspace/nes-tools/cc65/bin:$PATH
make -C rom-tests/solid-color
```

O código está em [`rom-tests/solid-color`](rom-tests/solid-color).
O checksum do binário está em [`downloads/SHA256SUMS.txt`](downloads/SHA256SUMS.txt).

No PowerShell do Windows, para conferir o checksum:

```powershell
Get-FileHash .\tela-azul-v0.1.nes -Algorithm SHA256
```

## Validação

O resultado do teste em FCEUX e a inspeção do binário serão registrados em
[`rom-tests/solid-color/VALIDACAO.md`](rom-tests/solid-color/VALIDACAO.md).
