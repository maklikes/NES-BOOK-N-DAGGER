local out=assert(os.getenv('NES_HERO_OUTPUT'))
local input={};local n=0;local report=assert(io.open(out..'/validation.txt','w'))
emu.speedmode('maximum');emu.registerbefore(function()joypad.set(1,input)end)
local function step(frames,pad)input=pad or {};for i=1,frames do emu.frameadvance()end end
local function tap(k)step(2,{[k]=true});step(2)end
local function v(a)return memory.readbyte(a)end
local function check(ok,text)assert(ok,text);n=n+1;report:write('PASS '..text..'\n');report:flush()end
local function capture(name)
 emu.speedmode('normal');step(180)
 local f=assert(io.open(out..'/'..name..'.gd','wb'));f:write(gui.gdscreenshot());f:close();emu.speedmode('maximum')
end
step(240)
check(v(0)==120 and v(1)==104 and v(6)==0,'Initial position and front idle')
for i,name in ipairs({'frente','costas','perfil'})do
 local f=assert(io.open('/workspace/NES-BOOK-N-DAGGER/art/characters/adventurer-static-v1/'..name..'.chr','rb'));local data=f:read('*all');f:close()
 check(ppu.readbyterange(0x1000+(i-1)*640,128)==data,'Idle CHR exactly equals static '..name)
end
check(v(0x201)==0 and v(0x202)==0 and v(0x20a)==1 and v(0x212)==2 and v(0x21a)==0,'Base and overlay palettes match static model')
capture('neutral')
local base=0;local worst=0
memory.registerexec(memory.readword(0xfffa),function()base=debugger.getcyclescount()end)
memory.registerwrite(0x2007,function()local d=debugger.getcyclescount()-base;if d>worst then worst=d end end)
local poses={};local x=v(0)
for i=1,32 do step(1,{right=true});poses[v(0x201)]=true end
step(2) -- Allow the last injected input frame to finish.
check(v(0)==x+32 and v(6)==2,'Right movement, profile and normal speed x='..v(0)..' expected='..(x+32)..' facing='..v(6)..' buttons='..v(2))
check(poses[88] and poses[96] and poses[104] and poses[112],'Four distinct right walk phases')
step(2);check(v(0x201)==80,'Release returns to exact profile idle')
step(32,{left=true});step(2)
check(v(0)==x and v(6)==3 and v(0x202)==0x40 and v(0x203)==v(0)+8 and v(0x207)==v(0),'Left flip swaps tile columns')
step(16,{up=true});step(2);check(v(1)==88 and v(6)==1 and v(0x201)==40,'North/back pose')
step(16,{down=true});step(2);check(v(1)==104 and v(6)==0 and v(0x201)==0,'South/front pose')
step(20,{left=true,right=true,up=true,down=true});step(2);check(v(0)==120 and v(1)==104,'Opposite directions cancel')
step(60,{A=true});step(2);check(v(8)==1 and ppu.readbyte(0x3f05)==0x1a,'A held switches background once')
capture('grass')
step(2,{start=true});step(30,{right=true,start=true});step(2)
check(v(5)==1 and v(0)==120 and ppu.readbyte(0x207d)==string.byte('P'),'Start hold pauses once with visible P')
tap('select');check(v(0)==120 and v(1)==104 and v(5)==1,'Select centers during pause')
tap('start');check(v(5)==0,'Unpause')
tap('B');check(v(9)==1 and ppu.readbyte(0x207b)==string.byte('L'),'B enables slow mode')
x=v(0);step(32,{right=true});step(2);check(v(0)==x+16,'Slow mode halves movement and animation together')
tap('B');tap('select');step(300,{right=true});step(2);check(v(0)==216 and v(0x201)==80,'Right limit stops at idle')
step(300,{left=true});step(2);check(v(0)==24,'Left limit')
step(300,{up=true});step(2);check(v(1)==56,'Top limit')
step(300,{down=true});step(2);check(v(1)==160,'Bottom limit')
local count=0
for y=0,239 do
 local line=0
 for i=0,63 do local sy=v(0x200+i*4);if sy<239 and y>=sy+1 and y<sy+9 then line=line+1 end end
 if line>count then count=line end
end
check(count==4,'Metasprite needs at most four sprites per scanline')
check(worst<2200 and worst>0,'PPU writes fit VBlank: '..worst..' cycles')
memory.registerwrite(0x2007,nil);memory.registerexec(memory.readword(0xfffa),nil)
emu.softreset();step(240);check(v(0)==120 and v(1)==104 and v(8)==0 and v(9)==0 and v(5)==0,'Reset clears test options')
report:write('TOTAL '..n..' checks passed\n');report:close();emu.exit()
