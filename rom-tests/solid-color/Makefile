CA65 ?= ca65
LD65 ?= ld65
ROM = ../../downloads/tela-azul-v0.1.nes

.PHONY: all
all: $(ROM)

build/main.o: main.s
	mkdir -p build
	$(CA65) -g -o $@ $<

$(ROM): build/main.o nes.cfg
	mkdir -p ../../downloads
	$(LD65) -C nes.cfg -m build/tela-azul.map -Ln build/tela-azul.lbl -o $@ build/main.o
