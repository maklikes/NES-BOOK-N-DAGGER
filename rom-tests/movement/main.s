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
@no_reset:
 lda paused
 bne @no_move
 jsr move_player
@no_move:
 lda #0
 sta sprite_palette
 lda buttons
 and #$40
 beq @not_b
 lda #2
 sta sprite_palette
@not_b:
 lda buttons
 and #$80
 beq @not_a
 lda #1
 sta sprite_palette
@not_a:
 jsr update_oam
 lda #0
 sta $2003
 lda #2
 sta $4014
 ; One numeric indicator below each button label.
 bit $2002
 ldx #0
@hud:
 lda #$23
 sta $2006
 lda hud_addresses,x
 sta $2006
 lda buttons
 and masks,x
 beq @released
 lda #'1'
 bne @write
@released:
 lda #'0'
@write:
 sta $2007
 inx
 cpx #8
 bne @hud
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

palettes:
 ; Text, wall/floor, wood/desk, spare. Universal background is $0f.
 .byte $0f,$30,$10,$00, $0f,$07,$17,$27
 .byte $0f,$08,$18,$28, $0f,$02,$12,$22
 ; Sprite palettes: burgundy, pale/violet for A, gold for B, spare.
 .byte $0f,$00,$37,$16, $0f,$00,$37,$24
 .byte $0f,$00,$37,$28, $0f,$00,$37,$16
masks: .byte $80,$40,$20,$10,$08,$04,$02,$01
hud_addresses: .byte $63,$65,$68,$6c,$6f,$72,$75,$78
x_offsets: .byte 0,8,0,8,0,8
y_offsets: .byte 0,0,8,8,16,16
room: .incbin "build/room.nam"
.segment "VECTORS"
.word nmi,reset,irq
.segment "CHR"
.incbin "build/graphics.chr"
