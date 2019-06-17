.text

# Some methods for
_dispatch_abort:
	la $a0 _dispatch_msg_
	li $v0 4
	syscall
	li $v0 10
	syscall 

_case_abort:
	la $a0 _cabort_msg_
	li $v0 4
	syscall
	li $v0 10
	syscall 

_case_abort2:
	la $a0 _cabort_msg2_
	li $v0 4
	syscall
	li $v0 10
	syscall 

_divide_by_0:
	la $a0 _div_by_zero_
	li $v0 4
	syscall
	li $v0 10
	syscall 
	
_ss_abort1:
	la	$a0 _sabort_msg1
	b	_ss_abort
_ss_abort2:
	la	$a0 _sabort_msg2
	b	_ss_abort
_ss_abort3:
	la	$a0 _sabort_msg3
	b	_ss_abort
_ss_abort4:
	la	$a0 _sabort_msg4
_ss_abort:
	li	$v0 4
	syscall
	la	$a0 _sabort_msg
	li	$v0 4
	syscall
	li	$v0 10		# exit
	syscall

# Objs in $t1 and $t2
# True in $a0, False in $a1
# Moves the result of the equality test to $a0
equality_test:
    beq $t1 $t2 _eq_true
    beq	$t1 $zero _eq_false         # $t2 can't also be void   
	beq $t2 $zero _eq_false         # $t1 can't also be void
    lw	$v0 obj_tag($t1)        	# get tags
    lw	$v1 obj_tag($t2)
    bne	$v1 $v0 _eq_false       	# compare tags
    li	$a2 int_tag		            # load int tag
    beq	$v1 $a2 _eq_int	            # Integers
    li	$a2 bool_tag	            # load bool tag
    beq	$v1 $a2 _eq_int	            # Booleans
    li	$a2 string_tag             # load string tag
    bne	$v1 $a2 _eq_false           # Not a primitive type
_eq_str: # handle strings
    lw	$v0, str_size($t1)	    # get string size objs
    lw	$v1, str_size($t2)
    lw	$v0, int_slot($v0)	    # get string sizes
    lw	$v1, int_slot($v1)
    bne	$v1 $v0 _eq_false
    beqz	$v1 _eq_true		# 0 length strings are equal
    addiu	$t1 str_field		    # Point to start of string
    addiu	$t2 str_field
    move	$t0 $v0		        # Keep string length as counter
_eq_l1:
    lbu	$v0,0($t1)	            # get char
    addiu	$t1 1
    lbu	$v1,0($t2)
    addiu	$t2 1
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
# OUTPUT: $a0 the reference to the new object
Object.copy:
	lw $a0 4($sp)
    lw $t0 obj_size($a0)		# get size of object to copy (offset 4 for object size)
	blez $t0 _objcopy_error		# check for invalid size
    #sll $t0 $t0 2
	move $t1 $a0                # save the reference in $t1
    move $a0 $t0                # the size to allocate
    move $t2 $ra                # save return address
    jal _MemMgr_Alloc
    move $ra $t2                # restore return address
    # $t1 --> obj source, $a0 --> obj destiny
    add $t0 $t0 $a0  #end index
	move $a1 $a0 #preserve $a0
_obj_copy_loop:
    lw $v0 0($t1)               # copy from source
    #sw $v0 0($a0)                # paste to destiny
    sw $v0 0($a1)                # paste to destiny
    #addiu $a0 4
	addiu $a1 4
    addiu $t1 4
    #bne $a0 $t0 _obj_copy_loop
    bne $a1 $t0 _obj_copy_loop	
	addiu $sp $sp 4
    jr $ra
_objcopy_error:
	la	$a0 _objcopy_msg		# show error message
	li	$v0 4
	syscall
	li	$v0 10				# exit
	syscall

_MemMgr_Alloc:
	blt $sp $gp _stack_overflow_error
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
_stack_overflow_error:
	la	$a0 _stack_overflow_msg		# show error message
	li	$v0 4
	syscall
	li	$v0 10				# exit
	syscall

# INPUT: $a0 <-- the int value to initialize the Int object
# OUTPUT: $a0 <-- the reference to the Int object
Int_init:
	sw $ra 0($sp)		# push $ra
	addiu $sp $sp -4
	sw $a0 0($sp)
	addiu $sp $sp -4	# push $a0 the int value to initialize the object
    li $t0 int_tag
    sll $t0 $t0 3           # *8
    add $t0 $t0 $s0
    lw $a0 0($t0)       # load the Int protop]type addr
    sw $a0 0($sp)
	addiu $sp $sp -4	# push $a0
    jal Object.copy		# $a0 contains the reference of the Int object
	addiu $sp $sp 4
	lw $a1 0($sp)		# pop $a1 ($a1 contains the input)
	addiu $sp $sp 4
	lw $ra 0($sp)		# restore $ra
	sw $a1 int_slot($a0)
	jr $ra

# 	INPUT: $a0 <-- addr of the first char of the string
#	OUTPUT: $t6 the real size of the string (withot "\0")
calcStrLen:
	la $a1 __e1_  #getting the real length
    lb $a1 0($a1)
    move $t2 $zero
_len_loop:
    lb $t1 0($a0)
    addiu $a0 $a0 1
    addiu $t2 1
    bne $t1 $a1 _len_loop
    sub $a0 $a0 $t2	# $a0 <-- addr of the first char of the string
	move $t6 $t2    
	addiu $t6 -1	# $t6 contains the len of the string (in bytes)
	jr $ra
	
	
# 	INPUT: $a0 <-- addr of the first char of the string
#          $t6 <- length of the string
#	OUTPUT: $a0 the new string object
String_init:
# Compute the length
	sw $a0 0($sp)
	addiu $sp $sp -4	# save the string address    
#now fix length to be multipl of 4
	li $t1 4
	addiu $t6 1 #Porque hay que almacenar el '\0' tambien 
	div $t6 $t1
	mfhi $t2
	bne $t2 $zero make4k
	b continue
make4k:
	sub $t1 $t1 $t2
	addu $a0 $t6 $t1	
	b good
# Fill the string prototype	
continue:
	move $a0 $t6
good:
	addiu $t6 -1 #para restaurar la longitud real del string
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
	move $a0 $t6
	jal Int_init
	move $a1 $a0
	addiu $sp $sp 4
	lw $ra 0($sp)		# restore return address
	addiu $sp $sp 4
	lw $a0 0($sp)		# restore the prototype address
	sw $a1 str_size($a0)	# set the string size
	addiu $sp $sp 4
	lw $a1 0($sp)		# restore the string address
	addi $t0 $a0 str_field
	beqz $t6 ended 
_copy_loop:
	lb $t1 0($a1)
	sb $t1 0($t0)
	addi $a1 1
	addi $t0 1
	addiu $t6 $t6 -1
	bnez $t6 _copy_loop
ended:
	la $t1 __e1_
	lb $t1 0($t1)
	sb $t1 0($t0)
	jr $ra

#   INPUT:	$a0 <-- points to a string prototype
.globl	IO.out_string
IO.out_string:
	lw $a1 4($sp)
	lw $a0 8($sp)				# $a0 <- lo que se quiere imprimir
	addiu	$a0 $a0 str_field	# Adjust to beginning of str
	li	$v0 4					# print_str
	syscall
	move $a0 $a1        # return the self type
	addiu $sp $sp 8     # pop two params from the stack
	jr $ra

# 	INPUT: $a0 <-- points to an Integer prototype
.globl	IO.out_int
IO.out_int:
	lw $a1 4($sp)
	lw $a0 8($sp)
	lw	$a0 int_slot($a0)	# Fetch int
	li	$v0 1		# print_int
	syscall
	move $a0 $a1
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
    move $t2 $ra
	jal _MemMgr_Alloc
    move $ra $t2
	move $s3 $a0			# Prototype address
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
	move $t4 $t1
#now make it mult of 4
	li $t3 4 #making 4kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk
	div $t1 $t3
	mfhi $t2
	bne $t2 $zero make4k2
	b continue2
make4k2:
	sub $t3 $t3 $t2  #$make4k
	addu $t1 $t1 $t3
	addu $gp $gp $t3 #fixing $gp
continue2:
	
	# #$gp points just after the null byte
	# lb	$v0 0($a0)			# is first byte '\0'?
	# bnez $v0 _instr_noteof
	# # we read nothing. Return '\n' (we don't have '\0'!!!)
	# li	$v0 10					# load '\n' into $v0
	# sb	$v0 -1($gp)
	# sb	$zero 0($gp)			# terminate
	# addiu	$gp $gp 1

_instr_noteof:
	# Fill the prototype
	li $a1 string_tag
	sw $a1 obj_tag($s3)     # set class tag 
	addiu $a1 $t1 16        
	sw $a1 obj_size($s3)    # set object size
	sw $s2 obj_disp($s3)    # set dispatch
	addiu $t4 $t4 -2        # the actual size of the string
	move $a0 $t4
	sw $ra 0($sp)
	addiu $sp $sp -4	# save return address
	jal Int_init
	sw $a0 str_size($s3)
	addiu $sp $sp 4
	lw $ra 0($sp)       # restore return addr
    move $a0 $s3
	addiu $sp $sp 4
	jr $ra				# return

#   INPUT:	$a0 object who's class name is desired
#	OUTPUT:	$a0 reference to class name string object
	.globl	Object.type_name
Object.type_name:
	lw $a0 4($sp)   #Object.type_name
	lw $a0 0($a0)	# load class tag
	li $t0 4
	mul $a0 $a0 $t0
	addu $a0 $a0 $s1
	sw $ra 0($sp)
	addiu $sp $sp -4	# save return address
	lw $a0 0($a0)
	jal calcStrLen
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
	lw $a0 4($sp)   #Object.type_name
	move $s5 $a0
	li	$v0 4
	la	$a0 _abort_msg
	syscall			# print_str

	
	lw $a0 0($s5)	# load class tag
	li $t0 4
	mul $a0 $a0 $t0
	addu $a0 $a0 $s1
	lw $a0 0($a0)

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
	#lw $a0 int_slot($a0)
	addiu $sp $sp 4
	jr $ra	# Return

String.concat:
	lw $t0 4($sp) 				# str obj 1
	lw $t1 8($sp) 				# str obj 2

	sw $t0 0($sp)
	addiu $sp $sp -4	# save t0
	
	sw $t1 0($sp)
	addiu $sp $sp -4	# save t1
	
	lw $v0 str_size($t0)
	lw $v0 int_slot($v0)		# str 1 size
	lw $v1 str_size($t1)
	lw $v1 int_slot($v1)		# str 2 size
	
	addu $t6 $v0 $v1			#len final
	
#now fix length to be multipl of 4
	li $t3 4
	addiu $t6 1 #Porque hay que almacenar el '\0' tambien 
	div $t6 $t3
	mfhi $t2
	bne $t2 $zero make4k3
	b continue3
make4k3:
	sub $t3 $t3 $t2
	addu $a0 $t6 $t3	
	b good2
# Fill the string prototype	
continue3:
	move $a0 $t6
good2:
	addiu $a0 $a0 16
	addiu $t6 -1 #para restaurar la longitud real del string
	sw $a0 0($sp)
	addiu $sp $sp -4	# save the length
	sw $ra 0($sp)
	addiu $sp $sp -4	# save return address
	jal _MemMgr_Alloc
	addiu $sp $sp 4
	lw $ra 0($sp)		# restore return address
	addiu $sp $sp 4
	lw $t3 0($sp)			# pop: $t3 <-- size of the string prototype
	li $a1 string_tag
	sw $a1 obj_tag($a0)		# set the class tag
	sw $t3 obj_size($a0)	# set the object size
	sw $s2 obj_disp($a0)	# set the dispatch	
	
	sw $a0 0($sp)
	addiu $sp $sp -4	# save the pointer
	sw $ra 0($sp)
	addiu $sp $sp -4	# save return address
	move $a0 $t6
	jal Int_init
	move $a1 $a0
	addiu $sp $sp 4
	lw $ra 0($sp)		# restore return address
	addiu $sp $sp 4
	lw $a0 0($sp)		# restore the prototype address
	sw $a1 str_size($a0)
	addiu $sp $sp 4
	lw $t1 0($sp)		# restore t1 (str2 address)
	addiu $sp $sp 4
	lw $t0 0($sp)		# restore t0 (str2 address)
	lw $v0 str_size($t0)
	lw $v0 int_slot($v0)		# str 1 size
	lw $v1 str_size($t1)
	lw $v1 int_slot($v1)		# str 2 size
	
	addiu $t0 $t0 str_field
	addiu $t1 $t1 str_field
	addiu $a1 $a0 str_field
	
copy_l1:
	beqz $v0 copy_l2
	lb $t2 0($t0)
	sb $t2 0($a1)
	addiu $t0 $t0 1
	addiu $a1 $a1 1
	addiu $v0 $v0 -1
	b copy_l1
copy_l2:
	beqz $v1 final
	lb $t2 0($t1)
	sb $t2 0($a1)
	addiu $t1 $t1 1
	addiu $a1 $a1 1
	addiu $v1 $v1 -1
	b copy_l2
final:
	la $t2 __e1_
	lb $t2 0($t2)
	sb $t2 0($a1)
	addiu $sp $sp 8
	jr $ra

String.substr:
	lw $a1 4($sp) 				# load str orig
	lw $t1 8($sp) 				# index int obj
	lw $t2 12($sp) 				# length int obj
	lw $t0 str_size($a1) 		# length str orig, int obj	
	lw $v0 int_slot($t0) 		# size of orig
	lw $v1 int_slot($t1) 		# index
	bltz $v1 _ss_abort1			# index is smaller than 0
	#beq $v1 $v0 _ss_abort2		# index == size of orig
	bgt $v1 $v0 _ss_abort2		# index > size of orig
	lw $t3 int_slot($t2)		# sublength
	add $t4 $v1 $t3				# index + sublength
	bgt $t4 $v0	_ss_abort3		# substr out of range
	bltz $t3 _ss_abort4			# sublength is smaller than 0
	move $t6 $t3				# set str length for String_init
	addiu $a1 str_field			# pointer to the begining of str array
	addu $a0 $a1 $v1			# pointer to index
	sw $ra 0($sp)
	addiu $sp $sp -4			# save return address
	jal String_init
	addiu $sp $sp 4
	lw $ra 0($sp)				# restore return address
	addiu $sp $sp 12
	jr $ra
	
Object.ctor:
	addiu $sp $sp 4
	jr $ra

Int.ctor:
	sw $zero 12($a0)
	addiu $sp $sp 4
	jr $ra

Bool.ctor:
	sw $zero 12($a0)
	addiu $sp $sp 4
	jr $ra

IO.ctor:
	addiu $sp $sp 4
	jr $ra

String.ctor:  #realmente no hace falta
	lw $a0 8($s0)#!!!!!!!!!!!!!!!!!!@@@
	sw $ra 0($sp)
	addiu $sp $sp -4
	sw $a0 0($sp)
	addiu $sp $sp -4
	jal Object.copy
	sw $zero 12($a0)
	move $a1 $a0 #int $a1 the ref to Int obj
	addiu $sp $sp 4
	lw $ra 0($sp)
	addiu $sp $sp 4
	lw $a0 0($sp)
	sw $a1 12($a0)
	sb $zero 16($a0)
	jr $ra

# #################################################################################################
