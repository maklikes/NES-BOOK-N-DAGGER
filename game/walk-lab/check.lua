local out=assert(os.getenv('NES_WALK_OUTPUT'))
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
check(v(0)==120 and v(1)==104 and v(6)==0 and v(0x201)==30,'Initial front official idle at center')
local names={
 'REPOUSO_DIREITO','PASSO_1_DIREITO','PASSO_2_DIREITO','PASSO_3_DIREITO','PASSO_4_DIREITO',
 'REPOUSO_FRENTE','PASSO_1_FRENTE','PASSO_2_FRENTE','PASSO_3_FRENTE','PASSO_4_FRENTE',
 'REPOUSO_COSTAS','PASSO_1_COSTAS','PASSO_2_COSTAS','PASSO_3_COSTAS','PASSO_4_COSTAS'}
for i,name in ipairs(names)do
 local f=assert(io.open('/workspace/NES-BOOK-N-DAGGER/art/characters/official-walk-v1/'..name..'.chr','rb'));local data=f:read('*all');f:close()
 check(ppu.readbyterange(0x1000+(i-1)*96,96)==data,'CHR identical to supplied '..name)
end
check(ppu.readbyte(0x3f11)==0x0f and ppu.readbyte(0x3f12)==0x27 and ppu.readbyte(0x3f13)==0x37,'Official head subpalette')
check(ppu.readbyte(0x3f15)==0x0f and ppu.readbyte(0x3f16)==0x12 and ppu.readbyte(0x3f17)==0x37,'Official torso subpalette')
check(ppu.readbyte(0x3f19)==0x0f and ppu.readbyte(0x3f1a)==0x17,'Official leg subpalette')
check(v(0x202)==0 and v(0x206)==0 and v(0x20a)==1 and v(0x20e)==1 and v(0x212)==2 and v(0x216)==2,'Six OAM entries use exact assigned subpalettes')
for i=6,63 do assert(v(0x200+i*4)==255,'Unused OAM entry visible')end
check(true,'All unused OAM entries hidden')
capture('neutral')
local base=0;local worst=0
memory.registerexec(memory.readword(0xfffa),function()base=debugger.getcyclescount()end)
memory.registerwrite(0x2007,function()local d=debugger.getcyclescount()-base;if d>worst then worst=d end end)
local poses={};local x=v(0)
for i=1,32 do step(1,{right=true});poses[v(0x201)]=true end
step(2)
check(v(0)==x+32 and v(1)==104 and v(6)==2,'Right advances exactly one pixel per frame')
check(poses[6] and poses[12] and poses[18] and poses[24],'All four approved walk phases reached')
check(v(0x201)==0 and v(7)==0,'Release restores exact idle and resets cadence')
step(32,{left=true});step(2)
check(v(0)==x and v(6)==3 and v(0x202)==0x40 and v(0x203)==v(0)+8 and v(0x207)==v(0),'Left movement with horizontal flip and swapped tile columns')
local verticalposes={}
for i=1,32 do step(1,{up=true});verticalposes[v(0x201)]=true end
step(2)
check(v(1)==72 and v(6)==1 and v(0x201)==60,'Up moves north and returns to back idle')
check(verticalposes[66] and verticalposes[72] and verticalposes[78] and verticalposes[84],'All four supplied back walk phases reached')
verticalposes={}
for i=1,32 do step(1,{down=true});verticalposes[v(0x201)]=true end
step(2)
check(v(1)==104 and v(6)==0 and v(0x201)==30,'Down moves south and returns to front idle')
check(verticalposes[36] and verticalposes[42] and verticalposes[48] and verticalposes[54],'All four supplied front walk phases reached')
step(20,{up=true,down=true});step(2);check(v(0)==120 and v(1)==104 and v(0x201)==30,'Opposite vertical directions cancel')
step(20,{right=true,left=true});step(2);check(v(0)==120 and v(0x201)==30,'Opposite directions cancel')
step(60,{A=true});step(2);check(v(8)==1 and ppu.readbyte(0x3f05)==0x1a,'A held changes floor once')
capture('grass')
-- Pause while walking: the displayed frame and position must be frozen.
step(12,{right=true});step(2,{start=true,right=true})
local paused_x=v(0);local paused_tick=v(7);local paused_tile=v(0x201)
step(30,{left=true,start=true});step(2)
check(v(5)==1 and v(0)==paused_x and v(7)==paused_tick and v(0x201)==paused_tile and paused_tile~=0,'Pause freezes active walk pose and position')
check(ppu.readbyte(0x207d)==string.byte('P'),'Pause indicator P visible')
tap('select');check(v(0)==120 and v(1)==104 and v(0x201)==30 and v(5)==1,'Select centers and restores idle during pause')
tap('start');check(v(5)==0,'Start unpauses')
tap('B');check(v(9)==1 and ppu.readbyte(0x207b)==string.byte('L'),'B enables slow mode with L indicator')
x=v(0);step(32,{right=true});step(2);check(v(0)==x+16 and v(0x201)==0,'Slow mode halves movement; release returns to idle')
-- Explicitly measure complete phase lengths after input has settled.
tap('B');tap('select');step(3,{right=true})
local counts={}
for i=1,32 do step(1,{right=true});local t=v(0x201);counts[t]=(counts[t] or 0)+1 end
step(2)
check(counts[6]==8 and counts[12]==8 and counts[18]==8 and counts[24]==8,'Each normal-speed walk phase lasts eight frames')
tap('select');step(300,{right=true});step(2);check(v(0)==216 and v(0x201)==0,'Right boundary stops at idle')
step(300,{left=true});step(2);check(v(0)==24 and v(0x201)==0,'Left boundary stops at idle')
step(300,{up=true});step(2);check(v(1)==56 and v(0x201)==60,'Top boundary stops at back idle')
step(300,{down=true});step(2);check(v(1)==160 and v(0x201)==30,'Bottom boundary stops at front idle')
tap('select');step(16,{up=true,right=true});step(2)
check(v(0)==136 and v(1)==88 and v(6)==1,'Diagonal advances each axis one pixel per frame, vertical facing priority')
step(20,{up=true,down=true,right=true,left=true});step(2)
check(v(0)==136 and v(1)==88 and v(0x201)==60,'All opposite directions cancel without animation')
local count=0
for y=0,239 do
 local line=0
 for i=0,63 do local sy=v(0x200+i*4);if sy<239 and y>=sy+1 and y<sy+9 then line=line+1 end end
 if line>count then count=line end
end
check(count==2,'At most two hardware sprites per scanline')
check(worst>0 and worst<2200,'PPU writes complete within VBlank: '..worst..' cycles')
memory.registerwrite(0x2007,nil);memory.registerexec(memory.readword(0xfffa),nil)
emu.softreset();step(240);check(v(0)==120 and v(6)==0 and v(0x201)==30 and v(8)==0 and v(9)==0 and v(5)==0,'Reset clears options and restores official idle')
report:write('TOTAL '..n..' checks passed\n');report:close();emu.exit()
