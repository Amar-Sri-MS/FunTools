/* This function is used to patch in around a function in runtime
 prehook getting the same arguments as the original function

 posthook is getting prehook 64 bit return value as an argument

 to compile run:
 $ clang -target mips64r6 -c kernels/fullhook.c -E -o kernels/fullhook.S
 $ clang -I./ -O2 -target mips64r6 -c kernels/fullhook.S -x assembler-with-cpp -o fullhook.o 
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

	daddiu $sp,$sp,-32
	sd $ra, 8($sp)
  sd $v0, 0($sp)

	lui	$1, 0 // %highest(posthook)
	daddiu	$1, $1, 0 //%higher(posthook)
	dsll	$1, $1, 16
	daddiu	$1, $1, 0 // %hi(posthook)
	dsll	$1, $1, 16
	daddiu	$ra, $1, 0 // %lo(posthook)

	// placeholder for two original commands
	nop
	nop

	// placeholder for back jump
	nop
	nop

	.set macro
	.set reorder

END(__pre_hook_function)

LEAF(__post_hook_function)
	.set noreorder
	.set nomacro

	ld $4, 0($sp)

	// Save v0 and v1
	sd $2, 16($sp)
	sd $3, 24($sp)

	sd $fp, 0($sp)
	move $fp, $sp

	// placeholder for posthook call
	nop
	nop

	move $sp, $fp
	ld $fp, 0($sp)

	// Restore v0 and v1
	ld $2, 16($sp)
	ld $3, 24($sp)

	ld $ra, 8($sp)
	daddiu $sp,$sp,32
	jr $ra

	.set macro
	.set reorder

END(__post_hook_function)
