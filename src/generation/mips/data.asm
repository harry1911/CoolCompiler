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
_dispatch_msg_:  .asciiz "Exception: Dispatch to void.\n"
_cabort_msg_:	.asciiz "Exception: No match in case statement.\n"
_cabort_msg2_:   .asciiz "Exception: Match on void in case statement.\n"
_nl:		    .asciiz "\n"
_term_msg:	    .asciiz "COOL program successfully executed\n"
_sabort_msg1:	.asciiz	"Exception: Index to substr is negative\n"
_sabort_msg2:	.asciiz	"Exception: Index to substr is too big\n"
_sabort_msg3:	.asciiz	"Exception: Length to substr too long\n"
_sabort_msg4:	.asciiz	"Exception: Length to substr is negative\n"
_sabort_msg:	.asciiz "Execution aborted.\n"
_objcopy_msg:	.asciiz "Object.copy: Invalid object size.\n"
_gc_abort_msg:	.asciiz "GC bug!\n"
_div_by_zero_:	.asciiz "Exception: Division by zero.\n"

# Exception Handler Message:
_uncaught_msg1: .asciiz "Uncaught Exception of Class "
_uncaught_msg2: .asciiz " thrown. COOL program aborted.\n"
_heap_overflow_msg: .asciiz "Exception: Heap overflow\n"

# Stack overflow handler message:
_stack_overflow_msg: .asciiz " Stack overflow detected, COOL program aborted.\n"

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

# #################################################################################################
