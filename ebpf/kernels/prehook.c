/* This function is used to patch in before a function in runtime
 prehook getting the same arguments as the original function

 to compile run:
 $ clang -target mips64r6 -c kernels/prehook.c -E -o kernels/prehook.S
 $ clang -I./ -O2 -target mips64r6 -c kernels/prehook.S -x assembler-with-cpp -o prehook.o 
*/
#include "mips_asm.h"

// $4 - $11, $a0 - $a7
// $2 - $3, $v0 - $v1
LEAF(__pre_hook_function)
	.set noreorder
	.set nomacro

	daddiu $sp,$sp,-88
	sd $ra, 8($sp)
	sd $fp, 0($sp)
	sd $28, 16($sp)

	sd $4, 24($sp)
	sd $5, 32($sp)
	sd $6, 40($sp)
	sd $7, 48($sp)
	sd $8, 56($sp)
	sd $9, 64($sp)
	sd $10, 72($sp)
	sd $11, 80($sp)

	move $fp, $sp

	// placeholder for prehook call
	nop
	nop

	move $sp, $fp

	ld $4, 24($sp)
	ld $5, 32($sp)
	ld $6, 40($sp)
	ld $7, 48($sp)
	ld $8, 56($sp)
	ld $9, 64($sp)
	ld $10, 72($sp)
	ld $11, 80($sp)

	ld $28,16($sp)
	ld $fp, 0($sp)
	ld $ra, 8($sp)
	daddiu $sp,$sp,88

	// placeholder for two original commands
	nop
	nop

	// placeholder for back jump
	nop
	nop


	.set macro
	.set reorder

END(__pre_hook_function)
