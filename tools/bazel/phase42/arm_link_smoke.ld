ENTRY(_phase42_smoke_entry)

MEMORY
{
    FLASH (rx) : ORIGIN = 0x08000000, LENGTH = 1024K
    RAM (rwx) : ORIGIN = 0x20000000, LENGTH = 128K
}

SECTIONS
{
    .text :
    {
        KEEP(*(.text._phase42_smoke_entry))
        *(.text .text.*)
        *(.rodata .rodata.*)
    } > FLASH

    .ARM.extab :
    {
        *(.ARM.extab* .gnu.linkonce.armextab.*)
    } > FLASH

    .ARM.exidx :
    {
        *(.ARM.exidx* .gnu.linkonce.armexidx.*)
    } > FLASH

    .data :
    {
        *(.data .data.*)
    } > RAM AT > FLASH

    .bss (NOLOAD) :
    {
        *(.bss .bss.*)
        *(COMMON)
    } > RAM

    /DISCARD/ :
    {
        *(.comment)
    }
}
