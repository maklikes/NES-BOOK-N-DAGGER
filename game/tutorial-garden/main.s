.setcpu "6502"
xpos=$00
ypos=$01
buttons=$02
previous=$03
pressed=$04
paused=$05
anim_tick=$06
anim_frame=$07
moving=$08
slow=$09
clock=$0a
base_tile=$0b
ptr=$0e
try_x=$10
try_y=$11
point_x=$12
point_y=$13
cell_index=$14

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
@first:
 bit $2002
 bpl @first
 lda #0
 ldx #0
@clear:
 sta $000,x
 inx
 bne @clear
 lda #$ff
@oam:
 sta $200,x
 inx
 bne @oam
@second:
 bit $2002
 bpl @second
 jsr center
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
 lda #<screen
 sta ptr
 lda #>screen
 sta ptr+1
 lda #$20
 sta $2006
 lda #0
 sta $2006
 ldx #4
 ldy #0
@screen:
 lda (ptr),y
 sta $2007
 iny
 bne @screen
 inc ptr+1
 dex
 bne @screen
 jsr draw_hero
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
idle:
 jmp idle

center:
 lda #32
 sta xpos
 lda #64
 sta ypos
stop_animation:
 lda #0
 sta anim_tick
 sta anim_frame
 sta moving
 rts

nmi:
 pha
 txa
 pha
 tya
 pha
 ; Upload the previously prepared frame first, while VBlank is guaranteed.
 ; Movement and collision calculations follow without further PPU writes.
 lda #0
 sta $2003
 lda #2
 sta $4014
 bit $2002
 lda #$20
 sta $2006
 lda #$5c
 sta $2006
 lda slow
 beq @slow_blank
 lda #'L'
 bne @slow_write
@slow_blank:
 lda #0
@slow_write:
 sta $2007
 lda #$20
 sta $2006
 lda #$5e
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
 inc clock
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
 and #$10
 beq @select
 lda paused
 eor #1
 sta paused
@select:
 lda pressed
 and #$20
 beq @paused
 jsr center
@paused:
 lda paused
 bne @draw
 lda pressed
 and #$40
 beq @directions
 lda slow
 eor #1
 sta slow
@directions:
 lda buttons
 and #3
 cmp #1
 beq @speed
 cmp #2
 beq @speed
 lda buttons
 and #12
 cmp #4
 beq @speed
 cmp #8
 beq @speed
 jsr stop_animation
 jmp @draw
@speed:
 lda slow
 beq @move
 lda clock
 and #1
 bne @draw
@move:
 jsr move_hero
@draw:
 jsr draw_hero
 pla
 tay
 pla
 tax
 pla
 rti
irq:
 rti

move_hero:
 lda #0
 sta moving
 lda xpos
 sta try_x
 lda ypos
 sta try_y
 lda buttons
 and #3
 cmp #1
 bne @left
 lda xpos
 cmp #224
 bcs @vertical
 inc try_x
 jmp @test_x
@left:
 cmp #2
 bne @vertical
 lda xpos
 cmp #16
 beq @vertical
 dec try_x
@test_x:
 jsr position_blocked
 bcs @restore_x
 lda try_x
 sta xpos
 inc moving
@restore_x:
 lda xpos
 sta try_x
@vertical:
 lda buttons
 and #12
 cmp #4
 bne @up
 lda ypos
 cmp #192
 bcs @animate
 inc try_y
 jmp @test_y
@up:
 cmp #8
 bne @animate
 lda ypos
 cmp #48
 beq @animate
 dec try_y
@test_y:
 jsr position_blocked
 bcs @animate
 lda try_y
 sta ypos
 inc moving
@animate:
 lda moving
 bne @walk
 jmp stop_animation
@walk:
 inc anim_tick
 lda anim_tick
 cmp #11
 bcc @return
 lda #1
 sta anim_tick
 inc anim_frame
 lda anim_frame
 and #3
 sta anim_frame
@return:
 rts

; Check the four corners of the prospective full 16x16 player rectangle.
; Carry set means at least one overlapping metatile is blocked.
position_blocked:
 lda try_x
 sta point_x
 lda try_y
 sta point_y
 jsr point_blocked
 bcs @return
 lda try_x
 clc
 adc #15
 sta point_x
 jsr point_blocked
 bcs @return
 lda try_y
 clc
 adc #15
 sta point_y
 jsr point_blocked
 bcs @return
 lda try_x
 sta point_x
 jsr point_blocked
@return:
 rts
point_blocked:
 lda point_y
 and #$f0
 sta cell_index
 lda point_x
 lsr a
 lsr a
 lsr a
 lsr a
 ora cell_index
 tax
 lda collision_map,x
 beq @clear
 sec
 rts
@clear:
 clc
 rts

draw_hero:
 lda anim_frame
 asl a
 asl a
 sta base_tile
 ldx #0
 ldy #0
@part:
 lda ypos
 clc
 adc ys,y
 sec
 sbc #1
 sta $200,x
 tya
 clc
 adc base_tile
 sta $201,x
 lda #0
 sta $202,x
 lda xs,y
 clc
 adc xpos
 sta $203,x
 inx
 inx
 inx
 inx
 iny
 cpy #4
 bne @part
 rts
palettes:
 .byte $0f,$0a,$1a,$2a, $0f,$30,$10,$20, $0f,$0a,$1a,$2a, $0f,$0a,$1a,$2a
 .byte $0f,$0f,$12,$37, $0f,$0f,$12,$37, $0f,$0f,$12,$37, $0f,$0f,$12,$37
xs: .byte 0,8,0,8
ys: .byte 0,0,8,8
screen: .incbin "build/screen.nam"
collision_map: .incbin "build/collision.bin"
.segment "VECTORS"
.word nmi,reset,irq
.segment "CHR"
.incbin "build/graphics.chr"
