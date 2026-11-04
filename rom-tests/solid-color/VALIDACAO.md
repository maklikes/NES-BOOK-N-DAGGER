# Validação — tela azul v0.1

## Ambiente restaurado

Após a publicação do ambiente, foram localizados e executados ca65 e ld65
(cc65, commit `555282497c3ecf8b313d87d5973093af19c35bd5`). O FCEUX 2.6.5 e
o wrapper de display virtual também foram restaurados e executados.
Não foi necessário reaplicar o rascunho ou publicar outra configuração.

## Compilação e formato

- Montagem e link concluídos sem erros.
- Cabeçalho iNES 1.0 conferido byte a byte: mapper 0, 1 banco PRG, 1 banco CHR.
- Tamanho: 24.592 bytes (16 de cabeçalho + 16.384 PRG + 8.192 CHR).
- Vetor Reset: `$C000`; NMI/IRQ: `$C046`.
- Banco CHR vazio e vetores dentro da área PRG conferidos.
- SHA-256: `3d966c8d185104fcd800998168aff48e6c1a17e319d614bc69ff4979390feca3`.

## Execução no FCEUX

Modo NTSC, núcleo NewPPU, captura após 240 avanços de quadro em cada etapa:

| Verificação | Inicialização | Após soft reset |
| --- | --- | --- |
| Cor universal PPU `$3F00` | `$01` | `$01` |
| CPU em JMP estável para si mesma | PASS | PASS |
| Captura 256 × 240 | PASS | PASS |
| Pixels de uma única cor | 61.440 | 61.440 |
| RGB na paleta do emulador | `(36, 24, 142)` | `(36, 24, 142)` |

As duas capturas foram comparadas pixel a pixel e são idênticas.
O RGB acima é a interpretação da paleta deste FCEUX, não uma exigência para
outros emuladores ou televisores.

![Captura real do FCEUX: tela azul](tela-azul.png)

O script Lua usado para capturar as etapas e conferir CPU/PPU está em
[`check.lua`](check.lua). No ambiente preparado:

```sh
mkdir -p /workspace/artifacts/rom-solid-color
NES_SOLID_OUTPUT=/workspace/artifacts/rom-solid-color \
  /workspace/nes-tools/emulator/bin/fceux-headless --no-config 1 \
  --loadlua /workspace/NES-BOOK-N-DAGGER/rom-tests/solid-color/check.lua \
  /workspace/NES-BOOK-N-DAGGER/downloads/tela-azul-v0.1.nes
```

As capturas `.gd` produzidas pelo FCEUX contêm um cabeçalho de 11 bytes e
pixels ARGB de 256 × 240. A análise local desses pixels confirmou uma única
cor azul e igualdade entre as etapas. Os logs locais estão em
`/workspace/artifacts/rom-solid-color`.

## Limites do teste

Não há gameplay, leitura de controles, música ou salvamento. Não houve teste
em Windows, EverDrive, NES físico ou Phantom System nesta execução.
A ROM não depende de efeitos de borda de VBlank, cuja precisão fina tem
uma limitação conhecida no FCEUX instalado.

O passo seguinte é o usuário baixar o `.nes` no GitHub e abrir em seu emulador.
