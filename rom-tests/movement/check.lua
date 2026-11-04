local out=assert(os.getenv('NES_ROOM_OUTPUT'))
local f=assert(io.open(out..'/validation.txt','w'))
local input={}
local passed=0
emu.speedmode('normal')
emu.registerbefore(function() joypad.set(1,input) end)
local function step(n,pad)
 input=pad or {}
 for i=1,n do emu.frameadvance() end
end
local function check(ok,label)
 assert(ok,label)
 passed=passed+1;f:write('PASS '..label..'\n');f:flush()
end
local function capture(name)
 local image=assert(io.open(out..'/'..name..'.gd','wb'))
 image:write(gui.gdscreenshot());image:close()
end
step(240)
check(memory.readbyte(0)==40 and memory.readbyte(1)==128,'Initial position')
check(memory.readbyte(0x201)==0 and memory.readbyte(0x205)==1,'Character OAM tiles')
check(ppu.readbyte(0x2210)==132,'Desk tile in nametable')
capture('room')
local keys={'A','B','select','start','up','down','left','right'}
local masks={128,64,32,16,8,4,2,1}
local hud={0x2363,0x2365,0x2368,0x236c,0x236f,0x2372,0x2375,0x2378}
for i,key in ipairs(keys) do
 step(2,{[key]=true})
 check(memory.readbyte(2)==masks[i],key..' controller bit')
 check(ppu.readbyte(hud[i])==string.byte('1'),key..' HUD pressed')
 step(2)
 check(memory.readbyte(2)==0 and ppu.readbyte(hud[i])==string.byte('0'),key..' release')
end
-- Start in the sequence left the movement paused; unpause explicitly.
check(memory.readbyte(5)==1,'Start toggled pause')
step(2,{start=true});step(2)
check(memory.readbyte(5)==0,'Start unpauses')
step(2,{select=true});step(2)
step(90,{right=true});step(2)
check(memory.readbyte(0)==96,'Desk blocks horizontal motion')
step(50,{down=true});step(2)
check(memory.readbyte(1)==168,'Bottom room bound')
step(300,{right=true});step(2)
check(memory.readbyte(0)==216,'Right room bound and path around desk')
step(300,{up=true});step(2)
check(memory.readbyte(1)==80,'Top room bound')
step(300,{left=true});step(2)
check(memory.readbyte(0)==24,'Left room bound')
local x=memory.readbyte(0);local y=memory.readbyte(1)
step(20,{up=true,down=true,left=true,right=true});step(2)
check(memory.readbyte(0)==x and memory.readbyte(1)==y,'Opposite directions cancel')
step(2,{start=true});step(30,{right=true,start=true});step(2)
check(memory.readbyte(5)==1 and memory.readbyte(0)==x,'Holding Start toggles once and freezes movement')
step(2,{select=true});step(2)
check(memory.readbyte(0)==40 and memory.readbyte(1)==128,'Select resets while paused')
step(2,{start=true});step(2)
step(30,{A=true});check(memory.readbyte(0x202)==1,'A sprite palette');capture('button-a');step(2)
step(2,{B=true});check(memory.readbyte(0x202)==2,'B sprite palette');step(2)
step(2,{A=true,B=true});check(memory.readbyte(0x202)==1,'A takes precedence over B');step(2)
check(memory.readbyte(0x202)==0,'Default sprite palette restored')
-- Measure all live PPU writes after the NMI entry; they must fit VBlank.
local vector=memory.readword(0xfffa)
local base=0
local worst=0
memory.registerexec(vector,function() base=debugger.getcyclescount() end)
memory.registerwrite(0x2007,function()
 local delta=debugger.getcyclescount()-base
 if delta>worst then worst=delta end
end)
step(60,{right=true,down=true,A=true,B=true})
memory.registerexec(vector,nil);memory.registerwrite(0x2007,nil)
check(worst>0 and worst<2200,'PPU writes fit NTSC VBlank: '..worst..' CPU cycles')
step(2);emu.softreset();step(240)
check(memory.readbyte(0)==40 and memory.readbyte(1)==128 and memory.readbyte(5)==0,'Reset reinitializes scene')
capture('reset')
f:write('TOTAL '..passed..' checks passed\n');f:close()
emu.exit()
