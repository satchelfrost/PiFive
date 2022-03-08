        .option pic
        .text
        .align  1
        .globl square
        .type   square, @function
square: 
        addi sp, sp, -24
        sd ra, 16(sp)
        sd fp, 8(sp)
        addi fp, sp, 24
        sd a0, -24(fp)
        ld a0, -24(fp)
        mul a0, a0, a0
        ld ra, 16(sp)
        ld fp, 8(sp)
        addi sp, sp, 24
        ret
        .size   square, .-square
        .align  1
        .globl  cube
        .type   cube, @function
cube:   
        addi sp, sp, -24
        sd ra, 16(sp)
        sd fp, 8(sp)
        addi fp, sp, 24
        sd a0, -24(fp)
        ld a0, -24(fp)
        call square
        mv a4, a0
        ld a5, -24(fp)
        mul a0, a4, a5
        ld ra, 16(sp)
        ld fp, 8(sp)
        addi sp, sp, 24
        ret
        .size   cube, .-cube
        .section        .rodata
        .align  3
.LC0:   
        .string "4 cubed is %d\n"
        .text
        .align  1
        .globl main
        .type   main, @function
main:
        addi sp, sp, -16
        sd ra, 8(sp)
        sd fp, 0(sp)
        addi fp, sp, 16
        li a0, 4
        call cube
        mv a1, a0
        lla a0, .LC0
        call printf
        li a5, 0
        mv a0, a5
        ld ra, 8(sp)
        ld fp, 0(sp)
        addi sp, sp, 16
        ret
        .size   main, .-main
        .ident  "GCC: (GNU) 10.2.0"
        .section .note.GNU-stack,"",@progbits
