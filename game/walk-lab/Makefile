CA65 ?= ca65
LD65 ?= ld65
ROM = ../../downloads/laboratorio-caminhada-externa-v0.1.nes
.PHONY: all
all: $(ROM)
build/assets.stamp: assets.py ../../art/characters/official-walk-v1/matrizes.json ../../art/characters/official-walk-v1/build.py ../../art/characters/main-official-v1/spec.py ../../game/first-river/assets.py
	mkdir -p build
	python3 ../../art/characters/official-walk-v1/build.py
	python3 assets.py
	touch $@
build/main.o: main.s build/assets.stamp
	$(CA65) -g -o $@ main.s
$(ROM): build/main.o nes.cfg
	mkdir -p ../../downloads
	$(LD65) -C nes.cfg -Ln build/lab.lbl -o $@ build/main.o
