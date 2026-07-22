/* GENERATED-FROM: memory_map.json@<md5> — DO NOT HAND-EDIT */
/* PRJ-001 (Argus) — Ibex RV32I, 4KB SRAM, APB peripherals */

MEMORY
{
    SRAM (rwx)  : ORIGIN = 0x00000000, LENGTH = 4096
}

ENTRY(_start)

SECTIONS
{
    . = 0x00000000;

    .text : {
        *(.text._start)
        *(.text*)
    } > SRAM

    .rodata : {
        *(.rodata*)
    } > SRAM

    .data : {
        *(.data*)
    } > SRAM

    .bss : {
        _bss_start = .;
        *(.bss*)
        *(COMMON)
        _bss_end = .;
    } > SRAM

    _stack_top = ORIGIN(SRAM) + LENGTH(SRAM);
}
