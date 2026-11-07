.setcpu "6502"
.macpack longbranch
xpos=$00
ypos=$01
room_id=$02
buttons=$03
previous=$04
pressed=$05
paused=$06
mode=$07
fish_count=$08
stored_lo=$09
stored_hi=$0a
quest_done=$0b
fishing=$0c
fish_lo=$0d
fish_hi=$0e
spot_index=$0f
spot_lo=$10
spot_hi=$11
random=$12
sim_frame=$13
anim_frame=$14
message=$15
notice_timer=$16
npc_talk=$17
facing=$18
walk_frame=$19
text_dirty=$20
hud_dirty=$21
load_pending=$22
scene_loading=$23
frame_ready=$24
water_dirty=$25
water_phase=$26
music_step=$27
music_timer=$28
sfx_timer=$29
sfx_period=$2a
sfx_volume=$2b
music_started=$2c
fx=$30
fy=$31
ptr=$32
candidate_x=$34
candidate_y=$35
temp=$36
oam_index=$37
nptr=$38
nrow=$3a
sprite_base=$3b
sprite_x=$3c
sprite_y=$3d
sprite_pal=$3e
hundreds=$40
tens=$41
units=$42
num_lo=$43
num_hi=$44
sprite_flip=$45
hero_flag=$46
is_moving=$47
pack_count=$48
pack_value=$49

.segment "HEADER"
.byte $4e,$45,$53,$1a,2,0,0,0
.res 8,0
.segment "CODE"
reset:
 sei
 cld
 ldx #$ff
 txs
 inx
 stx $2000
 stx $2001
 stx $4010
 stx $4015
 lda #$40
 sta $4017
 bit $2002
@wait:
 bit $2002
 bpl @wait
 lda #0
 ldx #0
@ram:
 sta $000,x
 sta $100,x
 sta $300,x
 sta $400,x
 sta $500,x
 sta $600,x
 sta $700,x
 inx
 bne @ram
 lda #$ff
@oam:
 sta $200,x
 inx
 bne @oam
@wait2:
 bit $2002
 bpl @wait2
 lda #112
 sta xpos
 lda #128
 sta ypos
 lda #$a7
 sta random
 lda #$c0
 sta spot_lo
 lda #3
 sta spot_hi             ; initial point lasts 960 simulated frames
 lda #1
 sta mode
 lda #0
 sta message
 lda #3
 sta text_dirty
 ; Load common sprite patterns into CHR RAM at $1000.
 lda #$10
 sta $2006
 lda #0
 sta $2006
 lda #<sprite_patterns
 sta ptr
 lda #>sprite_patterns
 sta ptr+1
 jsr unpack_patterns
 jsr copy_room
 jsr format_hud
 jsr build_oam
 lda #$0f
 sta $4015
 lda #$7f
 sta $4001
 sta $4005
 lda #$ff
 sta $4008
 lda #$30
 sta $400c
 lda #0
 sta $2003
 lda #2
 sta $4014
 bit $2002
 lda #0
 sta $2005
 sta $2005
 lda #$88
 sta $2000
 lda #$1e
 sta $2001

main_loop:
 lda frame_ready
 beq main_loop
 lda #0
 sta frame_ready
 jsr read_pad
 lda pressed
 and #$10
 beq @pause_done
 lda paused
 eor #1
 sta paused
@pause_done:
 lda paused
 bne @draw
 lda mode
 beq @world
 lda pressed
 and #$c0
 beq @draw
 lda #0
 sta mode
 jsr world_message
 jmp @draw
@world:
 inc sim_frame
 jsr random_next
 lda buttons
 and #$0f
 beq @action
 lda fishing
 beq @move
 jsr stop_fishing
@move:
 jsr move_player
 jsr exits
 jmp @timers
@action:
 lda pressed
 and #$40
 beq @a
 lda fishing
 beq @timers
 jsr stop_fishing
 jmp @timers
@a:
 lda pressed
 and #$80
 beq @timers
 lda fishing
 beq @interact
 jsr stop_fishing
 jmp @timers
@interact:
 jsr interact
@timers:
 lda mode
 bne @draw
 jsr world_timers
@draw:
 lda load_pending
 beq @sprites
 jsr change_scene
@sprites:
 jsr build_oam
 jmp main_loop

read_pad:
 lda buttons
 sta previous
 lda #1
 sta $4016
 lda #0
 sta $4016
 sta buttons
 ldx #8
@read:
 lda $4016
 lsr a
 rol buttons
 dex
 bne @read
 lda previous
 eor #$ff
 and buttons
 sta pressed
 rts

nmi:
 pha
 txa
 pha
 tya
 pha
 lda scene_loading
 beq @normal
 lda #0
 sta $2001
 jmp @ready
@normal:
 lda #0
 sta $2003
 lda #2
 sta $4014
 bit $2002
 jsr render_job
 lda #$20
 sta $2006
 lda #$5d
 sta $2006
 lda paused
 beq @pause_blank
 lda #'P'
 bne @pause_write
@pause_blank:
 lda #0
@pause_write:
 sta $2007
 lda #0
 sta $2005
 sta $2005
 lda #$88
 sta $2000
 lda #$1e
 sta $2001
@ready:
 jsr update_music
 lda #1
 sta frame_ready
 pla
 tay
 pla
 tax
 pla
 rti
irq:
 rti

random_next:
 lda random
 lsr a
 bcc @store
 eor #$b8
@store:
 sta random
 rts

move_player:
 lda #0
 sta is_moving
 lda xpos
 sta candidate_x
 lda ypos
 sta candidate_y
 lda buttons
 and #3
 cmp #1
 bne @left
 lda xpos
 cmp #240
 bcs @vertical
 inc candidate_x
 lda #2
 sta facing
 jmp @try_x
@left:
 cmp #2
 bne @vertical
 lda xpos
 beq @vertical
 dec candidate_x
 lda #3
 sta facing
@try_x:
 jsr blocked
 bcs @vertical
 lda candidate_x
 sta xpos
 lda #1
 sta is_moving
@vertical:
 lda xpos
 sta candidate_x
 lda buttons
 and #12
 cmp #4
 bne @up
 lda ypos
 cmp #168
 bcs @done
 inc candidate_y
 lda #0
 sta facing
 jmp @try_y
@up:
 cmp #8
 bne @done
 lda ypos
 cmp #40
 beq @done
 dec candidate_y
 lda #1
 sta facing
@try_y:
 jsr blocked
 bcs @done
 lda candidate_y
 sta ypos
 lda #1
 sta is_moving
@done:
 lda is_moving
 beq @still
 inc walk_frame
@still:
 rts

blocked:
 lda candidate_x
 clc
 adc #4
 sta fx
 lda candidate_y
 clc
 adc #16
 sta fy
 jsr solid_point
 bne @yes
 lda candidate_x
 clc
 adc #11
 sta fx
 jsr solid_point
 bne @yes
 lda candidate_y
 clc
 adc #23
 sta fy
 jsr solid_point
 bne @yes
 lda candidate_x
 clc
 adc #4
 sta fx
 jsr solid_point
 bne @yes
 clc
 rts
@yes:
 sec
 rts
solid_point:
 ; Collision arrays are page-aligned, one byte per map tile.
 lda fy
 lsr a
 lsr a
 lsr a
 lsr a
 lsr a
 lsr a
 ldx room_id
 clc
 adc solid_high,x
 sta ptr+1
 lda fy
 and #$38
 asl a
 asl a
 sta temp
 lda #0
 sta ptr
 lda fx
 lsr a
 lsr a
 lsr a
 clc
 adc temp
 tay
 lda (ptr),y             ; ptr low must be zero for indexed tile lookup
 rts

exits:
 lda room_id
 bne @path
 lda ypos
 cmp #164
 jcc @done
 lda xpos
 cmp #104
 jcc @done
 cmp #137
 jcs @done
 lda buttons
 and #4
 jeq @done
 lda #1
 sta room_id
 sta load_pending
 lda #112
 sta xpos
 lda #80
 sta ypos
 rts
@path:
 cmp #1
 bne @river
 lda xpos
 cmp #104
 bcc @east
 cmp #137
 bcs @east
 lda ypos
 cmp #65
 bcs @east
 lda buttons
 and #8
 beq @east
 lda #0
 sta room_id
 lda #1
 sta load_pending
 lda #112
 sta xpos
 lda #152
 sta ypos
 rts
@east:
 lda xpos
 cmp #232
 jcc @done
 lda ypos
 cmp #96
 jcc @done
 cmp #145
 jcs @done
 lda buttons
 and #1
 jeq @done
 lda #2
 sta room_id
 lda #1
 sta load_pending
 lda #16
 sta xpos
 lda #112
 sta ypos
 rts
@river:
 lda xpos
 cmp #9
 jcs @done
 lda ypos
 cmp #96
 jcc @done
 cmp #145
 jcs @done
 lda buttons
 and #2
 jeq @done
 lda #1
 sta room_id
 sta load_pending
 lda #224
 sta xpos
 lda #112
 sta ypos
@done:
 rts

interact:
 lda #3
 sta sfx_timer
 lda #3
 sta sfx_period
 sta sfx_volume
 lda room_id
 beq cabin_interact
 cmp #1
 bne @river
 jmp path_interact
@river:
 jmp start_fishing
cabin_interact:
 lda xpos
 cmp #144
 bcc @basket
 cmp #201
 bcs @basket
 lda ypos
 cmp #64
 bcc @basket
 cmp #121
 bcs @basket
 lda quest_done
 bne @already
 lda fish_count
 cmp #2
 bcc @not_enough
 sec
 sbc #2
 sta fish_count
 lda #1
 sta quest_done
 jsr format_hud
 lda #5
 jmp dialog
@not_enough:
 lda #4
 jmp dialog
@already:
 lda #6
 jmp dialog
@basket:
 lda xpos
 cmp #24
 bcc @home
 cmp #81
 bcs @home
 lda ypos
 cmp #88
 bcc @home
 cmp #145
 bcs @home
 lda fish_count
 beq @empty
 clc
 adc stored_lo
 sta stored_lo
 lda stored_hi
 adc #0
 sta stored_hi
 lda #0
 sta fish_count
 ; Capacity 999: retain any overflow in the bag, never delete resources.
 lda stored_hi
 cmp #3
 bcc @stored
 bne @overflow
 lda stored_lo
 cmp #$e8
 bcc @stored
@overflow:
 sec
 lda stored_lo
 sbc #$e7
 sta fish_count
 lda #$e7
 sta stored_lo
 lda #3
 sta stored_hi
 jsr format_hud
 lda #20
 jmp dialog
@stored:
 jsr format_hud
 lda #7
 jmp dialog
@empty:
 lda #8
 jmp dialog
@home:
 lda #17
 jmp dialog
path_interact:
 lda xpos
 cmp #48
 bcc @sign
 cmp #105
 bcs @sign
 lda ypos
 cmp #80
 bcc @sign
 cmp #145
 bcs @sign
 lda npc_talk
 eor #1
 sta npc_talk
 beq @lore
 lda #14
 jmp dialog
@lore:
 lda #15
 jmp dialog
@sign:
 lda xpos
 cmp #152
 bcc @nothing
 lda ypos
 cmp #72
 bcc @nothing
 cmp #121
 bcs @nothing
 lda #16
 jmp dialog
@nothing:
 lda #18
 jmp notice

start_fishing:
 lda fish_count
 cmp #6
 bcc @space
 lda #10
 jmp notice
@space:
 lda xpos
 cmp #124
 bcc @wrong
 cmp #145
 bcs @wrong
 lda ypos
 clc
 adc #20
 sec
 ldx spot_index
 sbc spot_y,x
 bcs @positive
 eor #$ff
 clc
 adc #1
@positive:
 cmp #13
 bcs @wrong
 lda #1
 sta fishing
 lda #2
 sta facing
 jsr next_capture
 lda #5
 sta sfx_timer
 lda #4
 sta sfx_period
 lda #3
 sta sfx_volume
 lda #12
 jmp show_message
@wrong:
 lda #19
 jmp notice
stop_fishing:
 lda #0
 sta fishing
 lda #9
 jmp notice
next_capture:
 lda random
 cmp #181
 bcc @add
 sec
 sbc #181
@add:
 clc
 adc #240
 sta fish_lo
 lda #0
 adc #0
 sta fish_hi
 rts

world_timers:
 lda notice_timer
 beq @animation
 dec notice_timer
 bne @animation
 jsr world_message
@animation:
 inc anim_frame
 lda room_id
 cmp #2
 bne @done
 lda anim_frame
 and #31
 bne @spot
 lda water_phase
 eor #1
 sta water_phase
 lda #1
 sta water_dirty
@spot:
 lda spot_lo
 bne @spot_dec
 dec spot_hi
@spot_dec:
 dec spot_lo
 lda spot_lo
 ora spot_hi
 bne @capture
 lda spot_index
 eor #1
 sta spot_index
 lda random
 sta spot_lo
 lda #4
 sta spot_hi          ; next location lasts 1024..1279 frames
 lda #0
 sta fishing
 lda #11
 jsr notice
@capture:
 lda fishing
 beq @done
 lda fish_lo
 bne @fish_dec
 dec fish_hi
@fish_dec:
 dec fish_lo
 lda fish_lo
 ora fish_hi
 bne @done
 lda fish_count
 cmp #6
 bcs @full
 inc fish_count
 jsr format_hud
 lda #10
 sta sfx_timer
 lda #2
 sta sfx_period
 lda #5
 sta sfx_volume
 lda fish_count
 cmp #6
 bcs @full
 jsr next_capture
 lda #13
 jmp notice
@full:
 lda #0
 sta fishing
 lda #10
 jmp notice
@done:
 rts

dialog:
 ldx #1
 stx mode
 ldx #0
 stx notice_timer
 jmp show_message
notice:
 ldx #180
 stx notice_timer
show_message:
 sta message
 lda #3
 sta text_dirty
 rts
world_message:
 lda fishing
 beq @room
 lda #12
 jmp show_message
@room:
 lda room_id
 clc
 adc #1
 jmp show_message

change_scene:
 lda #1
 sta scene_loading
 lda #0
 sta frame_ready
@wait_nmi:
 lda frame_ready
 beq @wait_nmi
 lda #0
 sta frame_ready
 sta load_pending
 sta fishing
 sta notice_timer
 sta water_dirty
 jsr copy_room
 jsr format_hud
 jsr world_message
 jsr build_oam
 lda #0
 sta scene_loading
 rts
copy_room:
 ; All scene uploads run with rendering disabled, including CHR RAM.
 bit $2002
 lda #0
 sta $2006
 sta $2006
 ldx room_id
 lda bg_low,x
 sta ptr
 lda bg_high,x
 sta ptr+1
 jsr unpack_patterns
 ; Room-specific background palettes; common sprite palettes.
 lda #$3f
 sta $2006
 lda #0
 sta $2006
 ldx room_id
 lda palette_low,x
 sta ptr
 lda palette_high,x
 sta ptr+1
 ldy #0
@palette:
 lda (ptr),y
 sta $2007
 iny
 cpy #32
 bne @palette
 bit $2002
 lda #$20
 sta $2006
 lda #0
 sta $2006
 ldx room_id
 lda room_low,x
 sta ptr
 lda room_high,x
 sta ptr+1
 ldx #4
 ldy #0
@copy:
 lda (ptr),y
 sta $2007
 iny
 bne @copy
 inc ptr+1
 dex
 bne @copy
 rts

format_hud:
 lda #0
 sta hud_dirty
 ldx #31
@blank:
 lda #' '
 sta $300,x
 dex
 bpl @blank
 ldx #0
@label:
 lda hud_label,x
 sta $300,x
 inx
 cpx #32
 bne @label
 lda fish_count
 clc
 adc #'0'
 sta $309
 lda stored_lo
 sta num_lo
 lda stored_hi
 sta num_hi
 lda #0
 sta hundreds
 sta tens
@hundred:
 lda num_hi
 bne @sub100
 lda num_lo
 cmp #100
 bcc @ten
@sub100:
 sec
 lda num_lo
 sbc #100
 sta num_lo
 lda num_hi
 sbc #0
 sta num_hi
 inc hundreds
 jmp @hundred
@ten:
 lda num_lo
 cmp #10
 bcc @digits
 sec
 sbc #10
 sta num_lo
 inc tens
 jmp @ten
@digits:
 lda hundreds
 clc
 adc #'0'
 sta $314
 lda tens
 clc
 adc #'0'
 sta $315
 lda num_lo
 clc
 adc #'0'
 sta $316
 lda quest_done
 beq @done
 lda #'2'
 sta $31b
@done:
 lda #1
 sta hud_dirty
 rts

render_job:
 lda hud_dirty
 beq @water
 lda #0
 sta hud_dirty
 lda #$20
 sta $2006
 lda #$60
 sta $2006
 ldx #0
@hud:
 lda $300,x
 sta $2007
 inx
 cpx #32
 bne @hud
 rts
@water:
 lda water_dirty
 beq @text
 lda #0
 sta water_dirty
 lda #$3f
 sta $2006
 lda #$0d
 sta $2006
 ldx water_phase
 lda water_a,x
 sta $2007
 lda water_b,x
 sta $2007
 rts
@text:
 lda text_dirty
 beq @done
 dec text_dirty
 ldx text_dirty
 lda #$23
 sta $2006
 lda dialog_rows,x
 sta $2006
 ldx message
 lda message_low,x
 sta nptr
 lda message_high,x
 sta nptr+1
 ldx text_dirty
 beq @draw
@offset:
 clc
 lda nptr
 adc #32
 sta nptr
 bcc @next
 inc nptr+1
@next:
 dex
 bne @offset
@draw:
 ldy #0
@char:
 lda (nptr),y
 sta $2007
 iny
 cpy #32
 bne @char
@done:
 rts

build_oam:
 lda #$ff
 ldx #0
@hide:
 sta $200,x
 inx
 inx
 inx
 inx
 bne @hide
 lda #0
 sta oam_index
 sta sprite_pal
 sta sprite_flip
 lda #1
 sta hero_flag
 ldx facing
 lda hero_bases,x
 sta sprite_base
 cpx #3
 bne @pose
 lda #$40
 sta sprite_flip
@pose:
 lda fishing
 beq @walk
 lda #54
 sta sprite_base
 lda #0
 sta sprite_flip
 jmp @hero
@walk:
 lda buttons
 and #15
 beq @hero
 lda is_moving
 beq @hero
 lda paused
 ora mode
 bne @hero
 lda walk_frame
 lsr a
 lsr a
 lsr a
 and #3
 tax
 lda walk_offsets,x
 clc
 adc sprite_base
 sta sprite_base
@hero:
 lda xpos
 sta sprite_x
 lda ypos
 sta sprite_y
 jsr actor
 lda #0
 sta hero_flag
 sta sprite_flip
 lda room_id
 beq @mother
 cmp #1
 beq @orc
 jmp @river
@mother:
 lda #60
 sta sprite_base
 lda mode
 bne @mother_open
 lda anim_frame
 and #127
 cmp #124
 bcc @mother_open
 lda #66
 sta sprite_base
@mother_open:
 lda #2
 sta sprite_pal
 lda #176
 sta sprite_x
 lda #88
 sta sprite_y
 jsr actor
 rts
@orc:
 lda #72
 sta sprite_base
 lda mode
 bne @orc_open
 lda anim_frame
 and #127
 cmp #124
 bcc @orc_open
 lda #78
 sta sprite_base
@orc_open:
 lda #3
 sta sprite_pal
 lda #72
 sta sprite_x
 lda #104
 sta sprite_y
 jsr actor
 rts
@river:
 ldx oam_index
 lda #160
 sta sprite_x
 ldy spot_index
 lda spot_y,y
 sec
 sbc #1
 sta $200,x
 sta $204,x
 lda anim_frame
 and #16
 beq @spot1
 lda #86
 bne @spot_tile
@spot1:
 lda #84
@spot_tile:
 sta $201,x
 clc
 adc #1
 sta $205,x
 lda #0
 sta $202,x
 sta $206,x
 lda #160
 sta $203,x
 lda #168
 sta $207,x
 lda fishing
 beq @done
 lda ypos
 clc
 adc #11
 sta $208,x
 clc
 adc #8
 sta $20c,x
 lda #88
 sta $209,x
 lda #89
 sta $20d,x
 lda #0
 sta $20a,x
 sta $20e,x
 lda xpos
 clc
 adc #10
 sta $20b,x
 clc
 adc #8
 sta $20f,x
@done:
 rts
actor:
 ldx oam_index
 ldy #0
@part:
 lda sprite_y
 clc
 adc y_offsets,y
 sec
 sbc #1
 sta $200,x
 tya
 clc
 adc sprite_base
 sta $201,x
 lda hero_flag
 beq @npc_palette
 lda hero_palettes,y
 ora sprite_flip
 jmp @palette_ready
@npc_palette:
 lda sprite_pal
@palette_ready:
 sta $202,x
 lda sprite_flip
 beq @normal_x
 lda x_offsets_flip,y
 jmp @add_x
@normal_x:
 lda x_offsets,y
@add_x:
 clc
 adc sprite_x
 sta $203,x
 jmp @next_part
@next_part:
 inx
 inx
 inx
 inx
 iny
 cpy #6
 bne @part
 stx oam_index
 rts

update_music:
 lda music_timer
 beq @note
 dec music_timer
 jmp @effects
@note:
 lda #23
 sta music_timer
 ldx music_step
 lda melody_low,x
 ora melody_high,x
 beq @rest
 lda #$b5
 sta $4000
 lda melody_low,x
 sta $4002
 lda melody_high,x
 ora #8
 sta $4003
 jmp @harmony
@rest:
 lda #$b0
 sta $4000
@harmony:
 lda #$72
 sta $4004
 lda harmony_low,x
 sta $4006
 lda harmony_high,x
 ora #8
 sta $4007
 lda #$ff
 sta $4008
 lda bass_low,x
 sta $400a
 lda bass_high,x
 ora #8
 sta $400b
 inc music_step
 lda music_step
 and #63
 sta music_step
@effects:
 lda sfx_timer
 beq @silence
 dec sfx_timer
 lda #$30
 ora sfx_volume
 sta $400c
 lda sfx_period
 sta $400e
 lda #8
 sta $400f
 rts
@silence:
 lda #$30
 sta $400c
 rts

; Compact PackBits decoder. Pointer belongs to main logic, not NMI.
get_packed_byte:
 ldy #0
 lda (ptr),y
 inc ptr
 bne @done
 inc ptr+1
@done:
 cmp #0                 ; Return Z/N for the data byte, not pointer INC.
 rts
unpack_patterns:
 jsr get_packed_byte
 beq @done
 bmi @literal
 sta pack_count
 jsr get_packed_byte
 sta pack_value
@repeat:
 lda pack_value
 sta $2007
 dec pack_count
 bne @repeat
 jmp unpack_patterns
@literal:
 and #$7f
 sta pack_count
@copy:
 jsr get_packed_byte
 sta $2007
 dec pack_count
 bne @copy
 jmp unpack_patterns
@done:
 rts
bg_low: .byte <bg0,<bg1,<bg2
bg_high: .byte >bg0,>bg1,>bg2
bg0: .incbin "build/background0.pkb"
bg1: .incbin "build/background1.pkb"
bg2: .incbin "build/background2.pkb"
sprite_patterns: .incbin "build/sprites.pkb"

palettes0:
 .byte $0f,$30,$20,$10, $0f,$37,$27,$17
 .byte $0f,$12,$22,$32, $0f,$21,$31,$30
 .byte $0f,$07,$37,$27, $0f,$07,$12,$37
 .byte $0f,$07,$37,$24, $0f,$09,$2a,$17
palettes1:
 .byte $0f,$30,$20,$10, $0f,$27,$17,$1a
 .byte $0f,$1a,$2a,$0a, $0f,$16,$26,$06
 .byte $0f,$07,$37,$27, $0f,$07,$12,$37
 .byte $0f,$07,$37,$24, $0f,$09,$2a,$17
palettes2:
 .byte $0f,$30,$20,$10, $0f,$27,$17,$1a
 .byte $0f,$1a,$2a,$0a, $0f,$21,$31,$11
 .byte $0f,$07,$37,$27, $0f,$07,$12,$37
 .byte $0f,$07,$37,$24, $0f,$09,$2a,$17
palette_low: .byte <palettes0,<palettes1,<palettes2
palette_high: .byte >palettes0,>palettes1,>palettes2
water_a: .byte $21,$2c
water_b: .byte $31,$3c
hero_bases: .byte 0,18,36,36
walk_offsets: .byte 6,0,12,0
hero_palettes: .byte 0,0,1,1,1,1
x_offsets_flip: .byte 8,0,8,0,8,0
spot_y: .byte 104,160
x_offsets: .byte 0,8,0,8,0,8
y_offsets: .byte 0,0,8,8,16,16
dialog_rows: .byte $20,$40,$60
.include "build/hud.inc"
room_low: .byte <room0,<room1,<room2
room_high: .byte >room0,>room1,>room2
solid_high: .byte >solid0,>solid1,>solid2
message_low:
.repeat 21,I
 .byte <(messages+I*96)
.endrepeat
message_high:
.repeat 21,I
 .byte >(messages+I*96)
.endrepeat
messages: .incbin "build/messages.bin"
.include "build/music.inc"
room0: .incbin "build/room0.nam"
room1: .incbin "build/room1.nam"
room2: .incbin "build/room2.nam"
.align 256
solid0: .incbin "build/solid0.bin"
solid1: .incbin "build/solid1.bin"
solid2: .incbin "build/solid2.bin"
.segment "VECTORS"
.word nmi,reset,irq
