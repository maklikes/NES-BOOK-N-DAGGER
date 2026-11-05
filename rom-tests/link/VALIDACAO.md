# Passagem, antecâmara e vínculo — v0.1

## Comportamento

O puzzle do espelho é preservado. Após a coleta, examinar o armário abre uma
confirmação de entrada. A antecâmara é uma segunda nametable de uma tela, com
porta de retorno à esquerda e porta selada à direita.

B no mundo abre o inventário quando os objetos foram coletados. A usa o objeto
selecionado, Cima/Baixo escolhem e B cancela. B continua fechando diálogos.
Start pausa também o uso de objetos. Select reposiciona na sala atual e fecha
a interface; não apaga inventário, puzzle, vínculo ou conclusão.

## Estados e regras

- Quarto: estados de espelho/gaveta/porta/coleta 0..4, iguais ao teste anterior.
- Vínculo 0: oculto. A adaga não pode cortá-lo.
- Vínculo 1: revelado pelo livro. O livro não abre a porta por si só.
- Vínculo 2: cortado pela adaga. O fio some e a porta fica transitável.
- Conclusão: examinar a porta liberada apresenta o final deste teste.

O livro revela em qualquer posição da antecâmara, sem consumo de recursos.
A adaga só corta em x >= 160, 104 <= y < 152. Fora do alcance há feedback e
nenhuma alteração do vínculo. O teste não exige precisão de um único pixel.
Usar os objetos no quarto não afeta o vínculo da outra sala.
Revelar repetidamente não duplica efeitos; cortar ou revelar depois do corte
não reconstrói o vínculo. Trocar de sala preserva os estados.

## Renderização e transições

- NROM-128, iNES 1.0, 16 KiB PRG, 8 KiB CHR, 24.592 bytes.
- Mesma personagem e colisão da mesa no quarto, sem mesa invisível na antecâmara.
- A porta selada tem colisão própria; ela é removida depois do corte.
- Cada troca de sala desliga a renderização e transfere 1.024 bytes da nametable.
  Essa cópia ocorre com renderização desligada, não é tratada como trabalho que
  precisa caber no VBlank. A renderização volta no NMI seguinte.
- Atualizações incrementais da porta/fio, inventário e texto são limitadas a um
  trabalho por quadro. O fio termina antes dos tiles da porta para não apagá-la.
- Cópias de tela restauram o estado visual da sala: armário vazio, fio revelado
  ou porta aberta, conforme o progresso. Pode haver alguns quadros de atualização.

## Testes

`check.lua` contém a regressão do puzzle aprovado e a sequência nova, com entradas
de controle reais emuladas, sem escrever estados na RAM do programa. O relatório
da execução está em `resultado-fceux.txt` e as capturas PNG são do FCEUX.

Foram verificados, entre outros:

- Tentativas fora de ordem no puzzle original, interação, colisões, pausa e reset.
- Inventário e cancelamento da confirmação de passagem.
- Entrada na segunda sala com os objetos e porta inicialmente bloqueada.
- Adaga antes de revelar, livro no quarto, revelação e repetição do livro.
- Adaga fora de alcance e uso durante pausa, sem avanço indevido.
- Atualização visual do fio, sem sobrescrever os tiles da porta.
- Ida e volta com vínculo revelado e depois cortado, preservando o progresso.
- Remoção da colisão da porta, conclusão e impossibilidade de recriar o vínculo.
- Quatro transferências de tela com exatamente 1.024 escritas cada.
- Medição das escritas incrementais em relação à entrada do NMI. A transferência
  de tela inteira foi identificada pelo PC de `load_scene` e excluída desse limite.

No relatório, os limites de VBlank são comparados com 2.200 ciclos de CPU NTSC.
A precisão fina das bordas da PPU continua sujeita à limitação conhecida do
FCEUX; não são usados efeitos de raster nesta ROM.

## Repetir no ambiente preparado

No diretório raiz do repositório, com ca65/ld65 no PATH:

```sh
make -C rom-tests/link
python3 rom-tests/link/run_check.py
```

O runner lê o endereço de `load_scene` no arquivo de labels da compilação atual
e executa o script no wrapper headless instalado em `/workspace/nes-tools/emulator`.
Resultados locais: `/workspace/artifacts/rom-link`. Para confirmar sucesso,
exige o relatório completo, além da saída normal do emulador.

## Limites

Sem inimigos, combate, áudio, terceira sala ou salvamento. Ainda não validada
nesta execução no Windows/MesenCE, NES físico, EverDrive ou Phantom System.
As figuras são gráficos técnicos provisórios, não a direção de arte final.
