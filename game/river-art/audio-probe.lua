-- Ten seconds of native NES APU audio captured by the emulator recorder.
emu.speedmode('normal')
for i=1,600 do emu.frameadvance() end
emu.exit()
