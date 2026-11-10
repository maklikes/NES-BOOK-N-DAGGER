local out=assert(os.getenv('NES_GARDEN_OUTPUT'))
local input={};local n=0;local report=assert(io.open(out..'/validation.txt','w'))
emu.speedmode('maximum');emu.registerbefore(function()joypad.set(1,input)end)
local f=assert(io.open('/workspace/NES-BOOK-N-DAGGER/game/tutorial-garden/build/collision.bin','rb'));local cells=f:read('*all');f:close()
local f=assert(io.open('/workspace/NES-BOOK-N-DAGGER/game/tutorial-garden/build/graphics.chr','rb'));local graphics=f:read('*all');f:close()
local function v(a)return memory.readbyte(a)end
local function safe()
 local x,y=v(0),v(1)
 assert(x>=16 and x<=224 and y>=48 and y<=192,'Outside field: '..x..','..y)
 for _,p in ipairs({{x,y},{x+15,y},{x,y+15},{x+15,y+15}})do
  local c=math.floor(p[2]/16)*16+math.floor(p[1]/16)
  assert(string.byte(cells,c+1)==0,'Player overlaps bush at '..x..','..y)
 end
end
local function step(frames,pad)
 input=pad or {}
 for i=1,frames do emu.frameadvance();if v(0)>=16 then safe()end end
end
local function tap(k)step(2,{[k]=true});step(2)end
local function check(ok,text)assert(ok,text);n=n+1;report:write('PASS '..text..'\n');report:flush()end
local function capture(name)
 emu.speedmode('normal');step(180)
 local f=assert(io.open(out..'/'..name..'.gd','wb'));f:write(gui.gdscreenshot());f:close();emu.speedmode('maximum')
end
step(240)
check(v(0)==32 and v(1)==64 and v(7)==0,'Start position and user idle frame')
check(ppu.readbyterange(0,8192)==graphics,'Both CHR tables exactly match imported user artwork and font')
check(ppu.readbyte(0x3f01)==0x0a and ppu.readbyte(0x3f02)==0x1a and ppu.readbyte(0x3f03)==0x2a,'Three exact background color indices')
check(ppu.readbyte(0x3f11)==0x0f and ppu.readbyte(0x3f12)==0x12 and ppu.readbyte(0x3f13)==0x37,'Single exact character subpalette')
for i=0,3 do assert(v(0x201+4*i)==i and v(0x202+4*i)==0)end
for i=4,63 do assert(v(0x200+4*i)==255)end
check(true,'Only four unflipped OAM sprites, remaining entries hidden')
-- Compare each map cell's four background tile references.
for my=2,13 do
 for mx=0,15 do
  local base=string.byte(cells,my*16+mx+1)==1 and 132 or 128
  for ty=0,1 do for tx=0,1 do
   assert(ppu.readbyte(0x2000+(my*2+ty)*32+mx*2+tx)==base+ty*2+tx,'Map tile mismatch')
  end end
 end
end
check(true,'Field faithfully repeats floor and bush metatiles')
capture('cenario')
local startcycle=0;local worst=0
memory.registerexec(memory.readword(0xfffa),function()startcycle=debugger.getcyclescount()end)
memory.registerwrite(0x2007,function()local d=debugger.getcyclescount()-startcycle;if d>worst then worst=d end end)
-- Eight-direction movement, palette and tile bases remain unchanged.
step(32,{right=true});step(2);check(v(0)==64 and v(1)==64,'Right: one pixel per NTSC frame')
step(32,{left=true});step(2);check(v(0)==32,'Left uses the same front-facing artwork')
step(16,{up=true});step(2);check(v(1)==48,'Up reaches top interior boundary')
step(16,{down=true});step(2);check(v(1)==64,'Down returns to starting row')
step(12,{right=true,down=true});step(2);check(v(0)==44 and v(1)==76,'Diagonal moves both axes')
step(20,{right=true,left=true,up=true,down=true});step(2)
check(v(0)==44 and v(1)==76 and v(7)==0,'Opposite directions cancel and reset idle')
tap('select')
step(3,{right=true});local counts={}
for i=1,40 do step(1,{right=true});counts[v(7)]=(counts[v(7)] or 0)+1;assert(v(0x201)==v(7)*4)end
step(2)
check(counts[0]==10 and counts[1]==10 and counts[2]==10 and counts[3]==10,'All four user poses last ten NTSC frames: 6 FPS')
check(v(7)==0 and v(6)==0,'Release restores original frame and resets timer')
-- Four approaches to the horizontal group at x=80..127, y=80..95.
tap('select');step(48,{right=true});step(2);step(32,{down=true});step(2)
check(v(0)==80 and v(1)==64 and v(7)==0,'Bush group blocks approach from above')
step(48,{left=true});step(2);step(48,{down=true});step(2);step(48,{right=true});step(2);step(32,{up=true});step(2)
check(v(0)==80 and v(1)==96,'Bush group blocks approach from below')
step(64,{right=true});step(2);step(16,{up=true});step(2);step(64,{left=true});step(2)
check(v(0)==128 and v(1)==80,'Bush group blocks approach from right')
step(32,{down=true});step(2);step(80,{left=true});step(2);step(32,{up=true});step(2);step(64,{right=true});step(2)
check(v(0)==64 and v(1)==80,'Bush group blocks approach from left')
step(4,{right=true,down=true});step(2)
check(v(0)==64 and v(1)==84,'Character slides along bush when other axis is free')
-- Boundary ring and maximum camera-safe coordinates.
step(300,{left=true});step(2);check(v(0)==16,'Left border blocks movement')
step(300,{up=true});step(2);check(v(1)==48,'Top border blocks movement')
step(300,{right=true});step(2);check(v(0)==224,'Right border blocks movement')
step(300,{down=true});step(2);check(v(1)==192,'Bottom border blocks movement')
step(300,{left=true});step(2);check(v(0)==16 and v(1)==192,'Bottom corridor traversable')
-- Pause must freeze a non-idle frame; Select works while paused.
tap('select');step(14,{right=true});step(2,{start=true,right=true})
local x,y,pose,tick=v(0),v(1),v(7),v(6)
step(30,{start=true,left=true});step(2)
check(v(5)==1 and v(0)==x and v(1)==y and v(7)==pose and v(6)==tick and pose~=0,'Pause freezes active pose and position')
check(ppu.readbyte(0x205e)==string.byte('P'),'Pause indicator visible')
tap('select');check(v(0)==32 and v(1)==64 and v(7)==0 and v(5)==1,'Select resets spawn and idle during pause')
tap('start');check(v(5)==0,'Unpause')
tap('B');check(v(9)==1 and ppu.readbyte(0x205c)==string.byte('L'),'B enables slow mode and indicator')
x=v(0);step(32,{right=true});step(2);check(v(0)==x+16 and v(7)==0,'Slow mode halves motion and returns to idle')
-- Input-free palette stability: no flashing or animation of user grass.
step(120)
check(ppu.readbyte(0x3f01)==0x0a and ppu.readbyte(0x3f02)==0x1a and ppu.readbyte(0x3f03)==0x2a,'Grass palette stays fixed')
local maximum=0
for y=0,239 do
 local line=0
 for i=0,63 do local sy=v(0x200+i*4);if sy<239 and y>=sy+1 and y<sy+9 then line=line+1 end end
 if line>maximum then maximum=line end
end
check(maximum==2,'At most two hardware sprites per scanline')
check(worst>0 and worst<1000,'PPU writes complete early in VBlank: '..worst..' cycles')
memory.registerwrite(0x2007,nil);memory.registerexec(memory.readword(0xfffa),nil)
emu.softreset();step(240)
check(v(0)==32 and v(1)==64 and v(7)==0 and v(9)==0 and v(5)==0,'Reset restores the exercise initial state')
report:write('TOTAL '..n..' checks passed\n');report:close();emu.exit()
