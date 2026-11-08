# Laboratório — caminhada externa v0.1

[Baixar a ROM](../../downloads/laboratorio-caminhada-externa-v0.1.nes).
Abra o arquivo no GitHub, clique em **Download raw file**, copie o `.nes`
para o cartão do EverDrive e abra pelo menu. Preferir NTSC no Mesen.

Usa exatamente as 15 matrizes recebidas do usuário, com as duas correções
expressas em Y=10 das costas. Substitui, neste novo laboratório, a animação
lateral local rejeitada. Não altera as ROMs antigas ou a pescaria.

## Controles

| NES | Tecla configurada no Mesen do usuário | Ação |
| --- | --- | --- |
| Direcional | W A S D | Mover nos quatro sentidos |
| A | K | Alternar fundo claro / verde |
| B | J | Alternar câmera lenta, indicador L |
| Start | I | Congelar posição e quadro atual, indicador P |
| Select | U | Centralizar e restaurar repouso de frente |

O personagem começa parado, de frente. Soltar o direcional ou atingir uma
borda retorna ao repouso da direção atual. Select funciona durante a pausa.
Trocar fundo e velocidade requer despausar. O teste é silencioso.

Movimento normal: um pixel por quadro em cada eixo. Diagonais são permitidas,
com prioridade da direção vertical para a aparência; não há normalização
da velocidade diagonal. Direções opostas se cancelam por eixo.
Oito quadros NTSC por fase; quatro fases por ciclo, aproximadamente 0,53 s.
Câmera lenta reduz deslocamento e animação pela metade.

O perfil esquerdo é espelhado, inclusive a faixa da túnica. A oscilação de
cabeça/tronco está contida nos quadros enviados; não há deslocamento extra
do corpo. As seis posições de sprites permanecem fixas em relação a X/Y.

## Estrutura

- Assembly 6502, ca65/ld65, mapper 0 / NROM-128.
- 16 KiB PRG + 8 KiB CHR ROM, arquivo iNES de 24.592 bytes.
- Pattern table de sprites em $1000; seis sprites por pose, dois por scanline.
- 90 tiles de personagem: lateral $00–$1D, frente $1E–$3B, costas $3C–$59.
- Três subpaletas oficiais; nenhum overlay ou recoloração da arte.
- Dados copiados dos CHRs gerados de `art/characters/official-walk-v1`.

`make -C game/walk-lab` com cc65 no PATH valida/exporta as matrizes e gera
a ROM. Requer Python e Pillow para a exportação gráfica. `check.lua` e
`run_check.py` verificam o programa no FCEUX instalado neste ambiente.

## Validação

Passaram **48 verificações no FCEUX 2.6.5**: todos os 15 CHRs presentes na
PPU iguais aos exportados; subpaletas; seis sprites e entradas OAM restantes
ocultas; quatro direções; fases de frente e costas; repousos; espelhamento;
pausa; câmera lenta; cadência; bordas; diagonais; cancelamento de direções;
reset e dois sprites por scanline. Última escrita PPU medida até 1.483 ciclos
após a entrada na NMI, dentro do VBlank NTSC. Relatório em `validation.txt`.

O teste no EverDrive / CRT desta ROM ainda depende do retorno do usuário.
Avaliar fidelidade à animação aprovada, alternância das pernas, oscilação,
transições, velocidade de avanço e contraste nos dois fundos.
