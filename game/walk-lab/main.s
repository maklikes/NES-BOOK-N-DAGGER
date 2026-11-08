.setcpu "6502"
xpos=$00
ypos=$01
buttons=$02
previous=$03
pressed=$04
paused=$05
facing=$06
walk_tick=$07
bg=$08
slow=$09
clock=$0a
moving=$0b
base_tile=$0c
flip=$0d
ptr=$0e
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
 lda #120
 sta xpos
 lda #104
 sta ypos
 lda #0
 sta walk_tick
 sta moving
 lda #0
 sta facing
 rts
nmi:
 pha
 txa
 pha
 tya
 pha
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
 and #$80
 beq @speed
 lda bg
 eor #1
 sta bg
@speed:
 lda pressed
 and #$40
 beq @move
 lda slow
 eor #1
 sta slow
@move:
 lda buttons
 and #3
 cmp #1
 beq @speed_gate
 cmp #2
 beq @speed_gate
 lda buttons
 and #12
 cmp #4
 beq @speed_gate
 cmp #8
 beq @speed_gate
 lda #0
 sta moving
 sta walk_tick
@speed_gate:
 lda slow
 beq @full_speed
 lda clock
 and #1
 bne @draw
@full_speed:
 jsr move_hero
@draw:
 jsr draw_hero
 lda #0
 sta $2003
 lda #2
 sta $4014
 bit $2002
 lda #$3f
 sta $2006
 lda #5
 sta $2006
 lda bg
 beq @sand
 ldx #3
 bne @bg_colors
@sand:
 ldx #0
@bg_colors:
 lda floors,x
 sta $2007
 inx
 lda floors,x
 sta $2007
 inx
 lda floors,x
 sta $2007
 lda #$20
 sta $2006
 lda #$7b
 sta $2006
 lda slow
 beq @speed_blank
 lda #'L'
 bne @write_slow
@speed_blank:
 lda #0
@write_slow:
 sta $2007
 lda #$20
 sta $2006
 lda #$7d
 sta $2006
 lda paused
 beq @pause_blank
 lda #'P'
 bne @write_pause
@pause_blank:
 lda #0
@write_pause:
 sta $2007
 lda #0
 sta $2005
 sta $2005
 lda #$88
 sta $2000
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
 lda buttons
 and #3
 cmp #1
 bne @left
 lda #2
 sta facing
 lda xpos
 cmp #216
 bcs @vertical
 inc xpos
 inc moving
 jmp @vertical
@left:
 cmp #2
 bne @vertical
 lda #3
 sta facing
 lda xpos
 cmp #24
 beq @vertical
 dec xpos
 inc moving
@vertical:
 lda buttons
 and #12
 cmp #4
 bne @up
 lda #0
 sta facing
 lda ypos
 cmp #160
 bcs @done
 inc ypos
 inc moving
 jmp @done
@up:
 cmp #8
 bne @done
 lda #1
 sta facing
 lda ypos
 cmp #56
 beq @done
 dec ypos
 inc moving
@done:
 lda moving
 beq @idle
 inc walk_tick
 rts
@idle:
 lda #0
 sta walk_tick
 rts

draw_hero:
 ldx facing
 lda direction_bases,x
 sta base_tile
 lda #0
 sta flip
 cpx #3
 bne @pose
 lda #$40
 sta flip
@pose:
 lda moving
 beq @tiles
 lda walk_tick
 sec
 sbc #1
 and #$18
 lsr a
 lsr a
 lsr a
 tax
 lda walk_bases,x
 clc
 adc base_tile
 sta base_tile
@tiles:
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
 lda attrs,y
 ora flip
 sta $202,x
 lda flip
 beq @normal_x
 lda xs_flipped,y
 jmp @x
@normal_x:
 lda xs,y
@x:
 clc
 adc xpos
 sta $203,x
 inx
 inx
 inx
 inx
 iny
 cpy #6
 bne @part
 rts
palettes:
 .byte $0f,$30,$10,$20,$0f,$37,$27,$17,$0f,$00,$10,$20,$0f,$00,$10,$20
 .byte $0f,$0f,$27,$37,$0f,$0f,$12,$37,$0f,$0f,$17,$0f,$0f,$0f,$0f,$0f
floors: .byte $37,$27,$17,$1a,$2a,$0a
direction_bases: .byte 30,60,0,0
walk_bases: .byte 6,12,18,24
attrs: .byte 0,0,1,1,2,2
xs: .byte 0,8,0,8,0,8
xs_flipped: .byte 8,0,8,0,8,0
ys: .byte 0,0,8,8,16,16
screen: .incbin "build/screen.nam"
.segment "VECTORS"
.word nmi,reset,irq
.segment "CHR"
.incbin "build/graphics.chr"
