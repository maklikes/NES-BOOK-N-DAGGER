local out=assert(os.getenv('NES_GARDEN_OUTPUT'))
emu.registerbefore(function()joypad.set(1,{})end)
emu.speedmode('normal')
-- Allow transient emulator speed/status messages to disappear.
for i=1,480 do emu.frameadvance()end
local f=assert(io.open(out..'/cenario-clean.gd','wb'))
f:write(gui.gdscreenshot());f:close()
emu.exit()
