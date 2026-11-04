CA65 ?= ca65
LD65 ?= ld65
ROM = ../../downloads/espelho-v0.1.nes
.PHONY: all
all: $(ROM)
build/assets.stamp: assets.py
	mkdir -p build
	python3 assets.py
	touch $@
build/main.o: main.s build/assets.stamp
	$(CA65) -g -o $@ main.s
$(ROM): build/main.o nes.cfg
	mkdir -p ../../downloads
	$(LD65) -C nes.cfg -m build/room.map -Ln build/room.lbl -o $@ build/main.o
