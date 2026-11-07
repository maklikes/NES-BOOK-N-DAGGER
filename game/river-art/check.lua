local out=assert(os.getenv('NES_RIVER_OUTPUT'))
local report=assert(io.open(out..'/validation.txt','w'))
local input={};local total=0
emu.speedmode('maximum')
emu.registerbefore(function() joypad.set(1,input) end)
local max_scanline=0
local rendering=false
memory.registerwrite(0x2001,function(address,size,value)rendering=math.floor(value/16)%2==1 end)
emu.registerafter(function()
 if not rendering then return end
 local diff={}
 for i=0,63 do
  local y=memory.readbyte(0x200+i*4)
  if y<239 then
   diff[y+1]=(diff[y+1] or 0)+1
   diff[math.min(240,y+9)]=(diff[math.min(240,y+9)] or 0)-1
  end
 end
 local count=0
 for y=0,239 do count=count+(diff[y] or 0);if count>max_scanline then max_scanline=count end end
end)
local function v(a)return memory.readbyte(a)end
local function word(a)return v(a)+v(a+1)*256 end
local function step(n,pad)input=pad or {};for i=1,n do emu.frameadvance() end end
local function tap(key)step(2,{[key]=true});step(14)end
local function check(ok,label)
 if not ok then report:write('STATE room='..v(2)..' x='..v(0)..' y='..v(1)..' fish='..v(8)..' mode='..v(7)..' fishing='..v(12)..' spot='..v(15)..'\n');report:flush() end
 assert(ok,label);total=total+1;report:write('PASS '..label..'\n');report:flush()
end
local function capture(name)
 if os.getenv('NES_CAPTURE')=='0' then return end
 emu.speedmode('normal');step(240)
 local f=assert(io.open(out..'/'..name..'.gd','wb'));f:write(gui.gdscreenshot());f:close()
 emu.speedmode('maximum')
end
local function move_x(x)
 for i=1,400 do
  local d=x-v(0);if math.abs(d)<=1 then step(2);return end
  step(1,d>0 and {right=true} or {left=true})
 end
 check(false,'Reach x='..x)
end
local function move_y(y)
 for i=1,400 do
  local d=y-v(1);if math.abs(d)<=1 then step(2);return end
  step(1,d>0 and {down=true} or {up=true})
 end
 check(false,'Reach y='..y)
end
local function exit_to(room,key)
 for i=1,400 do
  if v(2)==room and v(0x23)==0 and v(0x22)==0 then step(20);return end
  step(1,{[key]=true})
 end
 check(false,'Transition to room '..room)
end
local function to_river()
 if v(2)==0 then move_x(112);exit_to(1,'down') end
 if v(2)==1 then move_y(120);exit_to(2,'right') end
end
local function to_cabin()
 if v(2)==2 then move_y(112);exit_to(1,'left') end
 if v(2)==1 then move_x(112);exit_to(0,'up') end
end
local function point()
 move_x(136);move_y(v(15)==0 and 80 or 136)
end
local function fish_until(n)
 for i=1,10000 do
  if v(8)>=n then step(2);return end
  if v(12)==0 then point();tap('A') else step(1) end
 end
 check(false,'Collect '..n..' fish')
end
local function compare_chr(scene)
 local file=assert(io.open('/workspace/NES-BOOK-N-DAGGER/game/river-art/build/background'..scene..'.chr','rb'))
 local expected=file:read('*all');file:close()
 check(ppu.readbyterange(0,4096)==expected,'CHR RAM exactly matches background '..scene)
end
step(240)
check(v(2)==0 and v(7)==1 and v(8)==0 and word(9)==0 and v(11)==0,'Start in cabin with mother request and empty inventory')
step(60,{A=true});step(14)
check(v(7)==0 and v(0)==112,'Holding A dismisses only one dialogue')
local sf=assert(io.open('/workspace/NES-BOOK-N-DAGGER/game/river-art/build/sprites.chr','rb'));local sprite_data=sf:read('*all');sf:close()
check(ppu.readbyterange(0x1000,4096)==sprite_data,'Common sprite patterns loaded exactly into CHR RAM')
compare_chr(0);capture('cabin')
local nmi_base=0;local worst=0;local load_writes=0;local audio_notes=0;local noise_periods={}
memory.registerexec(memory.readword(0xfffa),function()nmi_base=debugger.getcyclescount()end)
memory.registerwrite(0x2007,function()
 if v(0x23)==1 then load_writes=load_writes+1
 else local d=debugger.getcyclescount()-nmi_base;if d>worst then worst=d end end
end)
memory.registerwrite(0x4002,function()audio_notes=audio_notes+1 end)
memory.registerwrite(0x400e,function(address,size,value)noise_periods[value]=true end)
local stride={}
for i=1,32 do step(1,{right=true});stride[v(0x201)]=true end
step(2)
check(stride[36] and stride[42] and stride[48],'Side walk cycles through both strides and neutral pose')
check(v(0x18)==2 and v(0x201)==36,'Right-facing profile is used while idle')
check(v(0x202)==0 and v(0x20a)==1,'Head and torso use distinct sprite palettes')
step(32,{left=true});step(2)
check(v(0x18)==3 and v(0x202)==0x40 and v(0x203)==v(0)+8 and v(0x207)==v(0),'Left profile mirrors pixels and swaps tile columns')
step(8,{up=true});step(2)
check(v(0x18)==1 and v(0x201)==18,'Moving north uses back-facing sprite')
step(8,{down=true});step(2)
check(v(0x18)==0 and v(0x201)==0,'Moving south uses front-facing sprite')
step(40,{left=true,right=true,up=true,down=true});step(2)
check(v(0)==112 and v(1)==128,'Opposite directions cancel')
tap('select');check(v(0)==112 and v(1)==128,'Select has no gameplay action')
move_x(160);move_y(96);tap('A')
check(v(7)==1 and v(0x15)==4 and v(8)==0 and v(11)==0,'Mother does not consume insufficient fish')
tap('B');move_x(48);tap('A')
check(v(7)==1 and v(0x15)==8 and word(9)==0,'Empty basket feedback');tap('B')
move_x(112);exit_to(1,'down')
check(v(2)==1 and v(8)==0,'Cabin exit leads to path')
move_y(120);move_x(80);tap('A')
check(v(7)==1 and v(0x15)==14,'Talk to orc fisherman');tap('B');tap('A')
check(v(0x15)==15,'Short second conversation suggests world history');tap('B')
compare_chr(1);capture('path')
exit_to(2,'right')
check(v(2)==2,'Path exit leads to river')
tap('A');check(v(12)==0 and v(0x15)==19,'Cannot fish far from active point')
step(300,{right=true});step(2)
check(v(0)<=140 and v(0)>=136,'River water blocks walking')
point();tap('A')
check(v(12)==1 and word(13)>=200 and word(13)<=420,'Cast begins timed automatic fishing')
local music=v(0x27)
step(2,{start=true});step(30,{start=true});step(2)
check(v(6)==1 and ppu.readbyte(0x205d)==string.byte('P'),'Holding Start pauses once with visible indicator')
local timer=word(13);local spot_timer=word(16);local count=v(8)
step(300)
check(word(13)==timer and word(16)==spot_timer and v(8)==count,'Pause freezes captures and point movement')
check(v(0x27)~=music,'Music continues while paused')
tap('start');check(v(6)==0,'Unpause')
tap('B');check(v(12)==0,'B interrupts fishing')
tap('A');step(2,{left=true});step(2)
check(v(12)==0,'Directional input interrupts fishing')
point();tap('A');compare_chr(2);capture('fishing')
fish_until(2)
check(v(8)==2,'Two automatic captures without repeating A')
tap('B');local before=v(8)
-- Place the next cast near the end of the spot lifetime.
point();local oldspot=v(15)
for i=1,1500 do if word(16)<=32 then break end;step(1)end
check(word(16)<=32,'Point has a finite lifetime')
tap('A');check(v(12)==1,'Cast before point moves')
step(60)
check(v(15)~=oldspot and v(12)==0 and v(8)==before,'Point relocation interrupts line without losing fish')
check(v(0x218)==(v(15)==0 and 103 or 159),'Marker follows active location')
point();tap('A');fish_until(6)
check(v(8)==6 and v(12)==0,'Six fish fill the bag and stop collection')
tap('A');step(300)
check(v(8)==6 and v(12)==0,'Full bag cannot overfill')
local seen={}
for i=1,100 do step(1);seen[ppu.readbyte(0x3f0d)]=true end
check(seen[0x21] and seen[0x2c],'Water animation changes palette')
capture('full-bag')
to_cabin();check(v(2)==0 and v(8)==6,'Return trip preserves fish')
move_x(160);move_y(96);step(60,{A=true});step(14)
check(v(7)==1 and v(11)==1 and v(8)==4 and v(0x15)==5,'Dinner consumes exactly two fish, once')
tap('B');tap('A');check(v(8)==4 and v(11)==1 and v(0x15)==6,'Completed dinner cannot consume fish again');tap('B')
move_y(136);move_x(48);tap('A')
check(v(8)==0 and word(9)==4 and v(0x15)==7,'Basket stores every remaining fish')
check(ppu.readbyte(0x2069)==string.byte('0') and ppu.readbyte(0x2076)==string.byte('4') and ppu.readbyte(0x207b)==string.byte('2'),'HUD shows inventory, storage and completed dinner')
capture('dinner');tap('B');tap('A')
check(v(8)==0 and word(9)==4,'Repeated basket interaction does not duplicate fish');tap('B')
to_river();check(v(11)==1 and word(9)==4,'World progress persists through both transitions')
point();tap('A');fish_until(2);tap('B')
check(v(8)==2,'Can continue fishing after quest completion')
to_cabin();move_x(160);move_y(96);tap('A')
check(v(8)==2 and v(11)==1,'Mother still preserves surplus after another trip');tap('B')
move_y(136);move_x(48);tap('A')
check(word(9)==6 and v(8)==0,'Storage accumulates across repeated fishing trips');tap('B')
check(audio_notes>10,'Melody advances on native APU')
check(noise_periods[2] and noise_periods[3] and noise_periods[4],'Catch, interaction and casting effects reach native noise channel')
check(max_scanline<=8,'Sprite count stays within eight per scanline: '..max_scanline)
check(worst>0 and worst<2200,'PPU incremental writes fit VBlank: '..worst..' cycles')
check(load_writes==8*(4096+32+1024),'Scene transfers upload full CHR, palette and nametable with rendering disabled: '..load_writes)
memory.registerexec(memory.readword(0xfffa),nil);memory.registerwrite(0x2007,nil);memory.registerwrite(0x4002,nil);memory.registerwrite(0x400e,nil)
emu.softreset();step(240)
check(v(2)==0 and v(8)==0 and word(9)==0 and v(11)==0 and v(7)==1,'Reset starts a new session without saved progress')
report:write('TOTAL '..total..' checks passed\n');report:close();emu.exit()
