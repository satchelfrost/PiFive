	.file	"example.c"
	.option nopic
	.text
	.align	1
	.globl	square
	.type	square, @function
square:
	addi	sp,sp,-32
	sd	s0,24(sp)
	addi	s0,sp,32
	sd	a0,-24(s0)
	ld	a5,-24(s0)
	mul	a5,a5,a5
	mv	a0,a5
	ld	s0,24(sp)
	addi	sp,sp,32
	jr	ra
	.size	square, .-square
	.align	1
	.globl	cube
	.type	cube, @function
cube:
	addi	sp,sp,-32
	sd	ra,24(sp)
	sd	s0,16(sp)
	addi	s0,sp,32
	sd	a0,-24(s0)
	ld	a0,-24(s0)
	call	square
	mv	a4,a0
	ld	a5,-24(s0)
	mul	a5,a4,a5
	mv	a0,a5
	ld	ra,24(sp)
	ld	s0,16(sp)
	addi	sp,sp,32
	jr	ra
	.size	cube, .-cube
	.section	.rodata
	.align	3
.LC0:
	.string	"%d\n"
	.text
	.align	1
	.globl	main
	.type	main, @function
main:
	addi	sp,sp,-32
	sd	ra,24(sp)
	sd	s0,16(sp)
	addi	s0,sp,32
	li	a0,3
	call	cube
	sd	a0,-24(s0)
	ld	a1,-24(s0)
	lui	a5,%hi(.LC0)
	addi	a0,a5,%lo(.LC0)
	call	printf
	li	a5,0
	mv	a0,a5
	ld	ra,24(sp)
	ld	s0,16(sp)
	addi	sp,sp,32
	jr	ra
	.size	main, .-main
	.ident	"GCC: (crosstool-NG 1.24.0.385_9e10cb6) 11.1.0"
	.section	.note.GNU-stack,"",@progbits
