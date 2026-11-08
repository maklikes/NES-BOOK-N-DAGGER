-- Diagnostic recording: actual controller input, no RAM changes.
local out=assert(os.getenv('NES_MOTION_OUTPUT'))
local input={}
emu.registerbefore(function()joypad.set(1,input)end)
emu.speedmode('maximum')
local function step(n,pad)input=pad or {};for i=1,n do emu.frameadvance()end end
step(240);step(2,{A=true});step(180)
local index=0
for _,key in ipairs({'right','left','up','down'})do
 for frame=1,16 do
  step(2,{[key]=true})
  local f=assert(io.open(out..'/'..string.format('%03d',index)..'.gd','wb'));f:write(gui.gdscreenshot());f:close();index=index+1
 end
 step(2)
 local f=assert(io.open(out..'/'..string.format('%03d',index)..'.gd','wb'));f:write(gui.gdscreenshot());f:close();index=index+1
end
emu.exit()
