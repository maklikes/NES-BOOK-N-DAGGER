# A Adaga e o Livro — primeiro teste de ROM

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
