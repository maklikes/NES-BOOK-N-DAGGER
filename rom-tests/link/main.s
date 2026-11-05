.setcpu "6502"
xpos=$00
ypos=$01
buttons=$02
previous=$03
pressed=$04
paused=$05
frames=$06
candidate_x=$07
candidate_y=$08
sprite_palette=$09
ptr=$0a
saved=$0c
mode=$0d
puzzle=$0e
selection=$0f
message=$10
text_dirty=$11
wardrobe_dirty=$12
inventory_dirty=$13
row_index=$14
room_id=$15
load_pending=$16
link_state=$17
link_dirty=$18
completed=$19
.segment "HEADER"
.byte $4e,$45,$53,$1a,1,1,0,0
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
@wait1:
 bit $2002
 bpl @wait1
 lda #0
 ldx #0
@clear:
 sta $000,x
 sta $100,x
 sta $300,x
 sta $400,x
 sta $500,x
 sta $600,x
 sta $700,x
 inx
 bne @clear
 lda #$ff
@oam:
 sta $200,x
 inx
 bne @oam
@wait2:
 bit $2002
 bpl @wait2
 lda #40
 sta xpos
 lda #128
 sta ypos
 ; Palette upload while rendering is disabled.
 lda #$3f
 sta $2006
 lda #0
 sta $2006
 ldx #0
@pal:
 lda palettes,x
 sta $2007
 inx
 cpx #32
 bne @pal
 ; Upload exactly one complete 1-KiB nametable (map and attributes).
 lda #<room
 sta ptr
 lda #>room
 sta ptr+1
 lda #$20
 sta $2006
 lda #0
 sta $2006
 ldx #4
 ldy #0
@map:
 lda (ptr),y
 sta $2007
 iny
 bne @map
 inc ptr+1
 dex
 bne @map
 lda #3
 sta text_dirty
 jsr update_oam
 lda #0
 sta $2003
 lda #2
 sta $4014
 bit $2002
 lda #0
 sta $2005
 sta $2005
 lda #$88                ; NMI, background $0000, 8x8 sprites $1000
 sta $2000
 lda #$1e
 sta $2001
idle:
 jmp idle

nmi:
 pha
 txa
 pha
 tya
 pha
 inc frames
 ; Read the eight serial controller bits: A=$80 ... Right=$01.
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
 and #$10                 ; Start toggles pause on press, not on hold.
 beq @no_pause
 lda paused
 eor #1
 sta paused
@no_pause:
 lda pressed
 and #$20                 ; Select resets position, including while paused.
 beq @no_reset
 lda #40
 sta xpos
 lda #128
 sta ypos
 lda #0
 sta mode
 jsr world_message
@no_reset:
 lda paused
 bne @no_action
 lda mode
 beq @world
 jsr handle_ui
 jmp @no_action
@world:
 lda pressed
 and #$80
 beq @move
 jsr interact
 jmp @no_action
@move:
 lda pressed
 and #$40
 beq @walk
 jsr open_items
 jmp @no_action
@walk:
 jsr move_player
@no_action:
 lda load_pending
 beq @normal_frame
 jsr load_scene
 jmp nmi_end
@normal_frame:
 jsr update_oam
 lda #0
 sta $2003
 lda #2
 sta $4014
 ; At most one bounded background update job per VBlank.
 bit $2002
 jsr render_job
 ; Pause indicator next to the title (P while paused, blank otherwise).
 lda #$20
 sta $2006
 lda #$7d
 sta $2006
 lda paused
 beq @blank
 lda #'P'
 bne @pause_write
@blank:
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
nmi_end:
 pla
 tay
 pla
 tax
 pla
 rti
irq:
 rti

move_player:
 ; Opposite directions cancel. Movement is 1 pixel/frame with axis separation.
 lda xpos
 sta candidate_x
 lda ypos
 sta candidate_y
 lda buttons
 and #3
 cmp #1
 bne @left
 lda xpos
 cmp #216
 bcs @x_done
 inc candidate_x
 jmp @try_x
@left:
 cmp #2
 bne @x_done
 lda xpos
 cmp #24
 beq @x_done
 dec candidate_x
@try_x:
 jsr collides
 bcs @x_done
 lda candidate_x
 sta xpos
@x_done:
 lda xpos
 sta candidate_x
 lda buttons
 and #$0c
 cmp #4
 bne @up
 lda ypos
 cmp #168
 bcs @done
 inc candidate_y
 jmp @try_y
@up:
 cmp #8
 bne @done
 lda ypos
 cmp #80
 beq @done
 dec candidate_y
@try_y:
 jsr collides
 bcs @done
 lda candidate_y
 sta ypos
@done:
 rts

collides:
 lda room_id
 beq @bedroom
 jmp corridor_collision
@bedroom:
 ; 16x24 character vs desk [112,160) x [128,152).
 lda candidate_x
 cmp #160
 bcs @free
 clc
 adc #16
 cmp #113
 bcc @free
 lda candidate_y
 cmp #152
 bcs @free
 clc
 adc #24
 cmp #129
 bcc @free
 sec
 rts
@free:
 ; The wardrobe occupies x=[184,232), y=[56,104).
 lda candidate_x
 cmp #232
 bcs @clear
 clc
 adc #16
 cmp #185
 bcc @clear
 lda candidate_y
 cmp #104
 bcs @clear
 sec
 rts
@clear:
 clc
 rts

update_oam:
 ; Six 8x8 sprites, only two per scanline. Hide all unused OAM entries.
 ldx #0
 ldy #0
@part:
 lda ypos
 clc
 adc y_offsets,y
 sec
 sbc #1
 sta $200,x
 tya
 sta $201,x
 lda sprite_palette
 sta $202,x
 lda xpos
 clc
 adc x_offsets,y
 sta $203,x
 inx
 inx
 inx
 inx
 iny
 cpy #6
 bne @part
 rts

 ; World interaction only occurs on a new A press.
interact:
 lda room_id
 beq @bedroom
 jmp corridor_interact
@bedroom:
 lda xpos
 cmp #176
 bcc @table
 lda ypos
 cmp #112
 bcs @table
 lda puzzle
 cmp #3
 beq @collect
 cmp #4
 beq @empty
 lda #1
 sta mode
 lda #0
 sta selection
 lda #1
 jmp show_message
@collect:
 lda #4
 sta puzzle
 lda #6
 sta wardrobe_dirty
 lda #1
 sta inventory_dirty
 lda #11
 jmp dialog
@empty:
 lda #4
 sta mode
 lda #15
 jmp show_message
@table:
 lda xpos
 cmp #80
 bcc @far
 cmp #177
 bcs @far
 lda ypos
 cmp #104
 bcc @far
 lda #5
 jmp dialog
@far:
 lda #4
 jmp dialog

dialog:
 ldx #2
 stx mode
show_message:
 sta message
 lda #3
 sta text_dirty
 rts

handle_ui:
 lda mode
 cmp #3
 bne @not_items
 jmp handle_items
@not_items:
 cmp #4
 bne @not_passage
 jmp handle_passage
@not_passage:
 lda mode
 cmp #2
 beq @dialog
 lda pressed
 and #$40
 bne @close
 lda pressed
 and #$08
 beq @down
 lda selection
 beq @choose
 dec selection
 jmp @refresh
@down:
 lda pressed
 and #$04
 beq @choose
 lda selection
 cmp #2
 beq @choose
 inc selection
@refresh:
 lda selection
 clc
 adc #1
 jsr show_message
@choose:
 lda pressed
 and #$80
 beq @done
 lda selection
 beq @mirror
 cmp #1
 beq @drawer
 ; Door: a latch must have been found and released first.
 lda puzzle
 cmp #2
 bcc @locked
 lda #3
 sta puzzle
 lda #6
 sta wardrobe_dirty
 lda #10
 jmp dialog
@locked:
 lda #9
 jmp dialog
@mirror:
 lda puzzle
 bne @known
 lda #1
 sta puzzle
 lda #6
 jmp dialog
@known:
 lda #12
 jmp dialog
@drawer:
 lda puzzle
 beq @stuck
 cmp #2
 bcs @loose
 lda #2
 sta puzzle
 lda #8
 jmp dialog
@stuck:
 lda #7
 jmp dialog
@loose:
 lda #13
 jmp dialog
@dialog:
 lda pressed
 and #$c0
 beq @done
@close:
 lda #0
 sta mode
 jmp world_message
@done:
 rts

render_job:
 lda room_id
 beq @bedroom
 lda link_dirty
 beq @items_hud
 jmp render_link
@items_hud:
 jmp @inventory
@bedroom:
 lda wardrobe_dirty
 beq @inventory
 dec wardrobe_dirty
 lda wardrobe_dirty
 sta row_index
 ; Update one six-tile row of the wardrobe per frame.
 tax
 lda wardrobe_high,x
 sta $2006
 lda wardrobe_low,x
 sta $2006
 lda #<wardrobe_maps
 sta ptr
 lda #>wardrobe_maps
 sta ptr+1
 lda puzzle
 cmp #4
 beq @empty
 lda #36
 bne @add_state
@empty:
 lda #72
@add_state:
 clc
 adc ptr
 sta ptr
 bcc @row
 inc ptr+1
@row:
 ldx row_index
 beq @draw_wardrobe
@offset:
 clc
 lda ptr
 adc #6
 sta ptr
 bcc @next
 inc ptr+1
@next:
 dex
 bne @offset
@draw_wardrobe:
 ldy #0
@tiles:
 lda (ptr),y
 sta $2007
 iny
 cpy #6
 bne @tiles
 rts
@inventory:
 lda inventory_dirty
 beq @text
 lda #0
 sta inventory_dirty
 lda #$20
 sta $2006
 lda #$65
 sta $2006
 ldx #0
@item:
 lda inventory_text,x
 sta $2007
 inx
 cpx #21
 bne @item
 rts
@text:
 lda text_dirty
 beq @done
 dec text_dirty
 lda text_dirty
 sta row_index
 ; Three 32-character rows at $2320, $2340 and $2360.
 tax
 lda #$23
 sta $2006
 lda dialog_rows,x
 sta $2006
 ldx message
 lda message_low,x
 sta ptr
 lda message_high,x
 sta ptr+1
 ldx row_index
 beq @draw
@offset_text:
 clc
 lda ptr
 adc #32
 sta ptr
 bcc @next_text
 inc ptr+1
@next_text:
 dex
 bne @offset_text
@draw:
 ldy #0
@char:
 lda (ptr),y
 sta $2007
 iny
 cpy #32
 bne @char
@done:
 rts

world_message:
 lda room_id
 beq @bedroom
 lda #16
 bne @show
@bedroom:
 lda #0
@show:
 jmp show_message

handle_passage:
 lda pressed
 and #$40
 beq @enter
 lda #0
 sta mode
 jmp world_message
@enter:
 lda pressed
 and #$80
 beq @done
 lda #1
 sta room_id
 sta load_pending
 lda #40
 sta xpos
 lda #128
 sta ypos
@done:
 rts

open_items:
 lda puzzle
 cmp #4
 beq @have
 lda #19
 jmp dialog
@have:
 lda #3
 sta mode
 lda #0
 sta selection
 lda #17
 jmp show_message

handle_items:
 lda pressed
 and #$40
 beq @select
 lda #0
 sta mode
 jmp world_message
@select:
 lda pressed
 and #$08
 beq @down
 lda #0
 sta selection
 lda #17
 jsr show_message
@down:
 lda pressed
 and #$04
 beq @use
 lda #1
 sta selection
 lda #18
 jsr show_message
@use:
 lda pressed
 and #$80
 beq @done
 lda room_id
 bne @corridor
 lda #20
 jmp dialog
@corridor:
 lda selection
 bne @dagger
 lda link_state
 beq @reveal
 cmp #2
 beq @finished
 lda #22
 jmp dialog
@reveal:
 lda #1
 sta link_state
 lda #7
 sta link_dirty
 lda #21
 jmp dialog
@dagger:
 lda link_state
 beq @hidden
 cmp #2
 beq @finished
 lda xpos
 cmp #160
 bcc @far
 lda ypos
 cmp #104
 bcc @far
 cmp #152
 bcs @far
 lda #2
 sta link_state
 lda #7
 sta link_dirty
 lda #25
 jmp dialog
@hidden:
 lda #23
 jmp dialog
@far:
 lda #24
 jmp dialog
@finished:
 lda #29
 jmp dialog
@done:
 rts

corridor_interact:
 lda xpos
 cmp #49
 bcs @gate
 lda ypos
 cmp #112
 bcc @nothing
 cmp #152
 bcs @nothing
 lda #0
 sta room_id
 lda #1
 sta load_pending
 lda #200
 sta xpos
 lda #112
 sta ypos
 rts
@gate:
 cmp #192
 bcc @nothing
 lda ypos
 cmp #104
 bcc @nothing
 cmp #152
 bcs @nothing
 lda link_state
 cmp #2
 beq @complete
 lda #26
 jmp dialog
@complete:
 lda #1
 sta completed
 lda #27
 jmp dialog
@nothing:
 lda #28
 jmp dialog

corridor_collision:
 lda link_state
 cmp #2
 beq @free
 lda candidate_x
 clc
 adc #16
 cmp #209
 bcc @free
 lda candidate_y
 cmp #152
 bcs @free
 clc
 adc #24
 cmp #105
 bcc @free
 sec
 rts
@free:
 clc
 rts

load_scene:
 ; Rendering is disabled for this whole upload. Not a VBlank-only transfer.
 lda #0
 sta $2001
 sta load_pending
 sta mode
 sta wardrobe_dirty
 sta link_dirty
 lda #<room
 sta ptr
 lda #>room
 sta ptr+1
 lda room_id
 beq @bedroom
 lda #<room2
 sta ptr
 lda #>room2
 sta ptr+1
 lda #7
 sta link_dirty
 jmp @upload
@bedroom:
 lda puzzle
 cmp #3
 bcc @upload
 lda #6
 sta wardrobe_dirty
@upload:
 bit $2002
 lda #$20
 sta $2006
 lda #0
 sta $2006
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
 lda puzzle
 cmp #4
 bne @text
 lda #1
 sta inventory_dirty
@text:
 jsr world_message
 rts

render_link:
 dec link_dirty
 lda link_dirty
 bne @gate_row
 ; Last job updates the horizontal tether, x=20..25, y=16.
 lda #$22
 sta $2006
 lda #$14
 sta $2006
 lda #129
 ldx link_state
 cpx #1
 bne @rope
 lda #136
@rope:
 ldx #6
@draw_rope:
 sta $2007
 dex
 bne @draw_rope
 ; Return without overwriting the gate: jobs are ordered gate first, rope last.
 rts
@gate_row:
 sec
 sbc #1
 sta row_index
 tax
 lda gate_high,x
 sta $2006
 lda gate_low,x
 sta $2006
 lda #<gate_maps
 sta ptr
 lda #>gate_maps
 sta ptr+1
 lda link_state
 cmp #2
 bne @offset
 clc
 lda ptr
 adc #18
 sta ptr
 bcc @offset
 inc ptr+1
@offset:
 ldx row_index
 beq @draw
@add:
 clc
 lda ptr
 adc #3
 sta ptr
 bcc @next
 inc ptr+1
@next:
 dex
 bne @add
@draw:
 ldy #0
@tile:
 lda (ptr),y
 sta $2007
 iny
 cpy #3
 bne @tile
 rts

gate_low: .byte $ba,$da,$fa,$1a,$3a,$5a
gate_high: .byte $21,$21,$21,$22,$22,$22

wardrobe_low: .byte $f7,$17,$37,$57,$77,$97
wardrobe_high: .byte $20,$21,$21,$21,$21,$21
dialog_rows: .byte $20,$40,$60
inventory_text: .byte "LIVRO: SIM ADAGA: SIM  "
message_low:
.repeat 30,I
 .byte <(messages+I*96)
.endrepeat
message_high:
.repeat 30,I
 .byte >(messages+I*96)
.endrepeat
messages: .incbin "build/messages.bin"
wardrobe_maps: .incbin "build/wardrobe.bin"

palettes:
 ; Text, wall/floor, wood/desk, spare. Universal background is $0f.
 .byte $0f,$30,$10,$00, $0f,$07,$17,$27
 .byte $0f,$08,$18,$28, $0f,$02,$12,$22
 ; Sprite palettes: burgundy, pale/violet for A, gold for B, spare.
 .byte $0f,$00,$37,$16, $0f,$00,$37,$24
 .byte $0f,$00,$37,$28, $0f,$00,$37,$16
x_offsets: .byte 0,8,0,8,0,8
y_offsets: .byte 0,0,8,8,16,16
room: .incbin "build/room.nam"
room2: .incbin "build/room2.nam"
gate_maps: .incbin "build/gate.bin"
.segment "VECTORS"
.word nmi,reset,irq
.segment "CHR"
.incbin "build/graphics.chr"
