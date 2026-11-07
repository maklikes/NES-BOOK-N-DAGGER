CA65 ?= ca65
LD65 ?= ld65
ROM = ../../downloads/primeira-pescaria-arte-v0.2.nes
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
	$(LD65) -C nes.cfg -m build/river.map -Ln build/river.lbl -o $@ build/main.o
