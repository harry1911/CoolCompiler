# NEXT REGISTERS CAN'T NEVER BE MODIFIED!!!!!!
	# --$s0-- contains Class Tag <-----> (Prototype,  Builder)
	# --$s1-- contains Class Tag <-----> Type Name (str)
	# --$s4-- contains Class Tag <-----> Parent Class Tag
	# --$s7-- contains the Heap Limit

.data

# =================================================================================

__m1_:	.asciiz "  Exception "
__m2_:	.asciiz " Execution aborted\n"
__e0_:	.asciiz "  [Interrupt] "
__e1_:	.asciiz	""
__e2_:	.asciiz	""
__e3_:	.asciiz	""
__e4_:	.asciiz	"  [Unaligned address in inst/data fetch] "
__e5_:	.asciiz	"  [Unaligned address in store] "
__e6_:	.asciiz	"  [Bad address in text read] "
__e7_:	.asciiz	"  [Bad address in data/stack read] "
__e8_:	.asciiz	"  [Error in syscall] "
__e9_:	.asciiz	"  [Breakpoint/Division by 0] "
__e10_:	.asciiz	"  [Reserved instruction] "
__e11_:	.asciiz	""
__e12_:	.asciiz	"  [Arithmetic overflow] "
__e13_:	.asciiz	"  [Inexact floating point result] "
__e14_:	.asciiz	"  [Invalid floating point result] "
__e15_:	.asciiz	"  [Divide by 0] "
__e16_:	.asciiz	"  [Floating point overflow] "
__e17_:	.asciiz	"  [Floating point underflow] "
__excp:	.word __e0_,__e1_,__e2_,__e3_,__e4_,__e5_,__e6_,__e7_,__e8_,__e9_
	.word __e10_,__e11_,__e12_,__e13_,__e14_,__e15_,__e16_,__e17_
s1:	.word 0
s2:	.word 0


# =================================================================================


_abort_msg:	.asciiz "Abort called from class "
_colon_msg:	.asciiz ":"
_dispatch_msg_:  .asciiz ": Dispatch to void.\n"
_cabort_msg_:	.asciiz "No match in case statement for Class "
_cabort_msg2_:   .asciiz "Match on void in case statement.\n"
_nl:		    .asciiz "\n"
_term_msg:	    .asciiz "COOL program successfully executed\n"
_sabort_msg1:	.asciiz	"Index to substr is negative\n"
_sabort_msg2:	.asciiz	"Index to substr is too big\n"
_sabort_msg3:	.asciiz	"Length to substr too long\n"
_sabort_msg4:	.asciiz	"Length to substr is negative\n"
_sabort_msg:	.asciiz "Execution aborted.\n"
_objcopy_msg:	.asciiz "Object.copy: Invalid object size.\n"
_gc_abort_msg:	.asciiz "GC bug!\n"
_div_by_zero_:	.asciiz "Divided by zero\n"

# Exception Handler Message:
_uncaught_msg1: .asciiz "Uncaught Exception of Class "
_uncaught_msg2: .asciiz " thrown. COOL program aborted.\n"
_exception_handler:	.word	__exception

# Stack overflow handler message:
_stack_overflow_msg: .asciiz " Stack overflow detected, COOL program aborted\n"

# Define some constants

obj_eyecatch=-4	    # Unique id to verify any object
obj_tag=0
obj_size=4
obj_disp=8
obj_attr=12
int_slot=12
bool_slot=12
str_size=12	        # This is a pointer to an Int object!!!
str_field=16	    # The beginning of the ascii sequence
str_maxsize=1026	# the maximum string length
int_tag = 2
string_tag = 3
bool_tag = 4


.text

# Some methods for
_dispatch_msg:
	la $a0 _dispatch_msg_
	li $v0 4
	syscall
	li $v0 10
	syscall 

_cabort_msg:
	la $a0 _cabort_msg_
	li $v0 4
	syscall
	li $v0 10
	syscall 

_cabort_msg2:
	la $a0 _cabort_msg2_
	li $v0 4
	syscall
	li $v0 10
	syscall 

_div_by_zero:
	la $a0 _div_by_zero_
	li $v0 4
	syscall
	li $v0 10
	syscall 

# Objs in $t1 and $t2
# True in $a0, False in $a1
# Moves the result of the equality test to $a0
equality_test:
    beq $t1 $t1 _eq_true
    beq	$t1 $zero _eq_false         # $t2 can't also be void   
	beq $t2 $zero _eq_false         # $t1 can't also be void
    lw	$v0 obj_tag($t1)        	# get tags
    lw	$v1 obj_tag($t2)
    bne	$v1 $v0 _eq_false       	# compare tags
    lw	$a2 _int_tag	            # load int tag
    beq	$v1 $a2 _eq_int	            # Integers
    lw	$a2 _bool_tag	            # load bool tag
    beq	$v1 $a2 _eq_int	            # Booleans
    lw	$a2 _string_tag             # load string tag
    bne	$v1 $a2 _eq_false           # Not a primitive type
_eq_str: # handle strings
    lw	$v0, str_size($t1)	    # get string size objs
    lw	$v1, str_size($t2)
    lw	$v0, int_slot($v0)	    # get string sizes
    lw	$v1, int_slot($v1)
    bne	$v1 $v0 _eq_false
    beqz	$v1 _eq_true		# 0 length strings are equal
    add	$t1 str_field		    # Point to start of string
    add	$t2 str_field
    move	$t0 $v0		        # Keep string length as counter
_eq_l1:
    lbu	$v0,0($t1)	            # get char
    add	$t1 1
    lbu	$v1,0($t2)
    add	$t2 1
    bne	$v1 $v0 _eq_false
    addiu $t0 $t0 -1	        # Decrement counter
    bnez $t0 _eq_l1
    b _eq_true		        # end of strings		
_eq_int:	                    # handles booleans and ints
    lw $v0,int_slot($t1)	    # load values
    lw $v1,int_slot($t2)
    bne	$v1 $v0 _eq_false
_eq_true:
	jr $ra		        # return true
 _eq_false:
	move $a0 $a1		# move false into accumulator
	jr $ra

# Emits the MIPS code to copy an object.
# INPUT: $a0 the reference to the object to be copied
# OTPUT: $a0 the reference to the new object
Object.copy:
	lw $a0 4($sp)
    lw $t0 obj_size($a0)		# get size of object to copy (offset 4 for object size)
	blez $t0 _objcopy_error		# check for invalid size
	move $t1 $a0                # save the reference in $t1
    move $a0 $t0                # the size to allocate
    move $t2 $ra                # save return address
    jal _MemMgr_Alloc
    move $ra $t2                # restore return address
    # $t1 --> obj source, $a0 --> obj destiny
_obj_copy_loop:
    lw $v0 0($t1)               # copy from source
    sw $v0 0(a0)                # paste to destiny
    addiu $a0 4
    addiu $t1 4
    bne $a0 $t0 _obj_copy_loop
	addiu $sp $sp 4
    jr $ra
_objcopy_error:
	la	$a0 _objcopy_msg		# show error message
	li	$v0 4
	syscall
	li	$v0 10				# exit
	syscall

_MemMgr_Alloc:
    add	$gp $gp $a0
    blt	$gp $s7 _MemMgr_Alloc_end
    la	$a0 _heap_overflow_msg		# show error message
	li	$v0 4
	syscall
	li	$v0 10				# exit
	syscall
_MemMgr_Alloc_end:
    sub $a0 $gp $a0
    jr $ra

# INPUT: $a0 <-- the int value to initialize the Int object
# OUTPUT: $a0 <-- the reference to the Int object
Int_init:
	sw $ra 0($sp)		# push $ra
	addiu $sp $sp -4
	sw $a0 0(sp)
	addiu $sp $sp -4	# push $a0
    lw $a0 int_tag($s0)
    jal Object.copy		 # $a0 contains the reference of the Int object
	addiu $sp $sp 4
	lw $a1 0($sp)		# pop $a1 ($a1 contains the input)
	addiu $sp $sp 4
	lw $ra 0($sp)		# restore $ra
	sw $a1 int_slot($a0)
	jr $ra

# 	INPUT: $a0 <-- addr of the first char of the string
#	OUTPUT: $a0 the new string object
String_init:
# Compute the length
	sw $a0 0($sp)
	addiu $sp $sp -4	# save the string address
    la $a1 __e1_
    lb $a1 0($a1)
    move $t2 $zero
_len_loop:
    lb $t1 0($a0)
    addiu $a0 $a0 1
    addiu $t2 1
    bne $t1 $a1 _len_loop
    move $a0 $t2	# $a0 contains the len of the string (in bytes)
# Fill the string prototype
	addi $a0 $a0 16		# the size of the string prototype
	sw $a0 0($sp)
	addiu $sp $sp -4	# save the length
	sw $ra 0($sp)
	addiu $sp $sp -4	# save return address
	jal _MemMgr_Alloc
	addiu $sp $sp 4
	lw $ra 0($sp)		# restore return address
	li $a1 string_tag
	sw $a1 obj_tag($a0)		# set the class tag
	addiu $sp $sp 4
	lw $t0 0($sp)			# pop: $t0 <-- size of the string prototype
	sw $t0 obj_size($a0)	# set the object size
	sw $s2 obj_disp($a0)	# set the dispatch
	
	sw $a0 0($sp)
	addiu $sp $sp -4	# save the pointer
	sw $ra 0($sp)
	addiu $sp $sp -4	# save return address
	addiu $t2 -1
	move $a0 $t2
	jal Int_init
	move $a1 $a0
	addiu $sp $sp 4
	lw $ra 0($sp)		# restore return address
	addiu $sp $sp 4
	lw $a0 0($sp)		# restore the prototype address
	sw $a1 str_size($a0)	# set the string size
	addiu $sp $sp 4
	lw $a1 0($sp)		# restore the string address
	addi $t2 1
	addi $t0 $a0 str_field
_copy_loop:
	lb $t1 0($a1)
	sb $t1 0($t2)
	addi $a1 1
	addi $t0 1
	addiu $t2 $t2 -1
	bnez $t2 _copy_loop
	jr $ra

#   INPUT:	$a0 <-- points to a string prototype
.globl	IO.out_string
IO.out_string:
	lw $a0 8($sp)
	addiu	$a0 $a0 str_field	# Adjust to beginning of str
	li	$v0 4					# print_str
	syscall
	addiu $sp $sp 8
	jr $ra

# 	INPUT: $a0 <-- points to an Integer prototype
.globl	IO.out_int
IO.out_int:
	lw $a0 8($sp)
	lw	$a0 int_slot($a0)	# Fetch int
	li	$v0 1		# print_int
	syscall
	addiu $sp $sp 8
	jr	$ra

#	Returns an integer object read from the terminal in $a0
	.globl	IO.in_int
IO.in_int:
	li $v0, 5		# read int
	syscall
	move $a0 $v0
	sw $ra 0($sp)
	addiu $sp $sp -4	# save return address
    jal Int_init
	addiu $sp $sp 4
	lw $ra 0($sp)		# restore return address
	addiu $sp $sp 4
	jr $ra

#	Returns a string object read from the terminal, removing the '\n'
#	OUTPUT:	$a0 the read string object
	.globl	IO.in_string
IO.in_string:
	li $a0 1042				# Prototype size + string max size
	jal _MemMgr_Alloc
	move $t0 $a0			# Prototype address
	addi $a0 16				# $a0 points to the begining of the string
	li	$a1 str_maxsize		# largest string to read
	li	$v0, 8				# read string
	syscall
	move $gp $a0
	move $t1 $zero			# keep counter in $t1 (length)
_instr_find_end:
	lb	$v0 0($gp)
	addiu $gp $gp 1
	addiu $t1 $t1 1
	bnez $v0 _instr_find_end
	# $gp points just after the null byte
	lb	$v0 0($a0)			# is first byte '\0'?
	bnez $v0 _instr_noteof
	# we read nothing. Return '\n' (we don't have '\0'!!!)
	li	$v0 10					# load '\n' into $v0
	sb	$v0 -1($gp)
	sb	$zero 0($gp)			# terminate
	addiu	$gp $gp 1
_instr_noteof:
	# Fill the prototype
	li $a1 string_tag
	sw $a1 obj_tag($t0)
	move $a1 $t1
	addiu $a1 $t1 16
	sw $a1 obj_size($t0)
	sw $s2 obj_disp($t0)
	addiu $t1 $t1 -1
	move $a0 $t1
	sw $ra 0($sp)
	addiu $sp $sp -4	# save return address
	jal Int_init
	sw $a0 str_size($t0)
	addiu $sp $sp 4
	lw $ra 0($sp)
	addiu $sp $sp 4
	jr $ra				# return

#   INPUT:	$a0 object who's class name is desired
#	OUTPUT:	$a0 reference to class name string object
	.globl	Object.type_name
Object.type_name:
	lw $a0 4($sp)
	lw $a0 0($a0)	# load class tag
	li $t0 4
	mul $a0 $a0 $t0
	addu $a0 $a0 $s1
	sw $ra 0($sp)
	addiu $sp $sp -4	# save return address
	jal String_init
	addiu $sp $sp 4
	lw $ra 0($sp)		# restore $ra
	addiu $sp $sp 4
	jr $ra
	
#	The abort method for the object class (usually inherited by
#	all other classes)
#   INPUT:	$a0 contains the object on which abort() was dispatched.
	.globl	Object.abort
Object.abort:
	move $s5 $a0
	li	$v0 4
	la	$a0 _abort_msg
	syscall			# print_str
	move $t1 $s1
	lw	$v0 obj_tag($s5)	# Get object tag
	sll	$v0 $v0 2	# *4
	addu	$t1 $t1 $v0
	lw	$t1 0($t1)	# Load class name string.
	li	$v0 4		# print_str
	syscall
	la	$a0 _nl
	li	$v0 4
	syscall			# print new line
	li	$v0 10
	syscall			# Exit

#	INPUT:	$a0 the string object
#	OUTPUT:	$a0 the int object which is the size of the string
	.globl	String.length
String.length:
	lw $a0 4($sp)
	lw	$a0 str_size($a0)	# fetch attr
	lw $a0 int_slot($a0)
	addiu $sp $sp 4
	jr $ra	# Return



# #################################################################################################
