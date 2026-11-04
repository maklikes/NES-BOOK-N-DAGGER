; Native NES smoke test: a solid blue backdrop, without rendering or sound.
; NROM-128 / iNES 1.0: 16 KiB PRG ROM + 8 KiB CHR ROM, mapper 0.
.setcpu "6502"

PPUCTRL   = $2000
PPUMASK   = $2001
PPUSTATUS = $2002
PPUADDR   = $2006
PPUDATA   = $2007

.segment "HEADER"
.byte $4E, $45, $53, $1A
.byte 1, 1                    ; PRG and CHR banks
.byte 0, 0                    ; Mapper 0, horizontal mirroring, no battery
.res 8, 0

.segment "CODE"
.proc reset
    sei
    cld
    ldx #$FF
    txs
    inx                       ; X = 0
    stx PPUCTRL               ; Disable NMI
    stx PPUMASK               ; Disable background and sprite rendering
    stx $4010                 ; Disable DMC IRQ
    stx $4015                 ; Disable audio channels
    lda #$40
    sta $4017                 ; Inhibit APU frame IRQ

    ; Wait through two VBlanks before configuring the PPU.
    bit PPUSTATUS
@first_vblank:
    bit PPUSTATUS
    bpl @first_vblank
@second_vblank:
    bit PPUSTATUS
    bpl @second_vblank

    ; Initialize all palette entries, including universal backdrop $3F00.
    bit PPUSTATUS             ; Reset the PPU address latch
    lda #$3F
    sta PPUADDR
    lda #$00
    sta PPUADDR
    ldx #32
    lda #$01                  ; NES blue; exact RGB varies with palette/display
@palette:
    sta PPUDATA
    dex
    bne @palette

    ; With rendering off, park the address outside palette RAM so the PPU
    ; displays universal backdrop $3F00 instead of an addressed palette entry.
    lda #$00
    sta PPUADDR
    sta PPUADDR
.export idle
idle:
    jmp idle
.endproc

.proc interrupt
    rti
.endproc

.segment "VECTORS"
.word interrupt, reset, interrupt

.segment "CHR"
.res $2000, 0                 ; Valid blank CHR bank; no graphics needed
