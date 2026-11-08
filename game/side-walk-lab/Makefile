CA65 ?= ca65
LD65 ?= ld65
ROM = ../../downloads/laboratorio-caminhada-oficial-v0.1.nes
.PHONY: all
all: $(ROM)
build/assets.stamp: assets.py $(wildcard ../../art/characters/main-walk-side-v2/*.chr) ../../game/first-river/assets.py
	mkdir -p build
	python3 assets.py
	touch $@
build/main.o: main.s build/assets.stamp
	$(CA65) -g -o $@ main.s
$(ROM): build/main.o nes.cfg
	mkdir -p ../../downloads
	$(LD65) -C nes.cfg -Ln build/lab.lbl -o $@ build/main.o
