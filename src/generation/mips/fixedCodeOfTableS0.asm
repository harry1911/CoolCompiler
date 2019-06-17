
    #----------------------------Object prototype
    li $a0 12
    jal _MemMgr_Alloc           # allocate 12 bytes for a Object prototype
    sw $a0 0($s0)
    move $a1 $zero              # the calss tag
    sw $a1 0($a0)               # set class tag in 0
    li $a1 12
    sw $a1 4($a0)               # set the object size to 12
    #### Dispatch Pointer
    move $a1 $a0                #save address of prototype in $a1
    li $a0 12                   #prepare $a0
    jal _MemMgr_Alloc           # allocate 12 bytes for a Object virtual methods
    sw $a0 8($a1)               #save dispatch pointer address in prototype
    la $a2 Object.abort         #save at $a2 abort method address
    sw $a2 0($a0)                #build virtual method table
    la $a2 Object.type_name
    sw $a2 4($a0) 
    la $a2 Object.copy
    sw $a2 8($a0)
    #------------------CODE TO ADD ITS CTOR
    la $a1 Object.ctor
    sw $a1 4($s0)

    #----------------------------IO prototype
    li $a0 12
    jal _MemMgr_Alloc           # allocate 16 bytes for a IO prototype
    sw $a0 8($s0)
    li $a1 1                    # the calss tag
    sw $a1 0($a0)               # set class tag in 2
    li $a1 12                   # the object size (4*num_of_attrs)
    sw $a1 4($a0)               # set the object size
    
    #### Dispatch Pointer
    move $a1 $a0                #save address of prototype in $a1
    li $a0 28                   #prepare $a0
    jal _MemMgr_Alloc           # allocate 12 bytes for a Object virtual methods
    sw $a0 8($a1)               #save dispatch pointer address in prototype
    la $a2 Object.abort         #save at $a2 abort method address
    sw $a2 0($a0)                #build virtual method table
    la $a2 Object.type_name
    sw $a2 4($a0) 
    la $a2 Object.copy
    sw $a2 8($a0) 
    la $a2 IO.out_string
    sw $a2 12($a0)
    la $a2 IO.out_int
    sw $a2 16($a0)
    la $a2 IO.in_string
    sw $a2 20($a0)
    la $a2 IO.in_int
    sw $a2 24($a0)
    #------------------CODE TO ADD ITS CTOR
    la $a1 IO.ctor
    sw $a1 12($s0)

    #----------------------------Int prototype
    li $a0 16
    jal _MemMgr_Alloc           # allocate 16 bytes for a Int prototype
    sw $a0 16($s0)
    li $a1 2                    # the calss tag
    sw $a1 0($a0)               # set class tag in 2
    li $a1 16                    # the object size (4*num_of_attrs)
    sw $a1 4($a0)               # set the object size

    ### Attr 1
    move $a1 $zero              # Value of Int is 0 by defauld
    sw $a1 12($a0)

    #### Dispatch Pointer
    move $a1 $a0                #save address of prototype in $a1
    li $a0 12                   #prepare $a0
    jal _MemMgr_Alloc           # allocate 12 bytes for a Object virtual methods
    sw $a0 8($a1)               #save dispatch pointer address in prototype
    la $a2 Object.abort         #save at $a2 abort method address
    sw $a2 0($a0)                #build virtual method table
    la $a2 Object.type_name
    sw $a2 4($a0) 
    la $a2 Object.copy
    sw $a2 8($a0)        
    #------------------CODE TO ADD ITS CTOR
    la $a1 Int.ctor
    sw $a1 20($s0)

   
    #----------------------------Bool prototype
    li $a0 16
    jal _MemMgr_Alloc           # allocate 16 bytes for a Bool prototype
    sw $a0 32($s0)
    li $a1 4                    # the calss tag
    sw $a1 0($a0)               # set class tag in 4
    li $a1 16                    # the object size (4*num_of_attrs)
    sw $a1 4($a0)               # set the object size
    
    #### Attr 1
    move $a1 $zero              # Value of Bool is 0 by defauld
    sw $a1 12($a0)
    
    #### Dispatch Pointer
    move $a1 $a0                #save address of prototype in $a1
    li $a0 12                   #prepare $a0
    jal _MemMgr_Alloc           # allocate 12 bytes for a Object virtual methods
    sw $a0 8($a1)               #save dispatch pointer address in prototype
    la $a2 Object.abort         #save at $a2 abort method address
    sw $a2 0($a0)                #build virtual method table
    la $a2 Object.type_name
    sw $a2 4($a0) 
    la $a2 Object.copy
    sw $a2 8($a0) 
    #------------------CODE TO ADD ITS CTOR
    la $a1 Bool.ctor
    sw $a1 36($s0)

    #---------------------------Virtual table of methods of string
    li $a0 24                   #prepare $a0
    jal _MemMgr_Alloc           #allocate 12 bytes for a Object virtual methods
    move $s2 $a0                #save dispatch pointer address in $s2
    la $a2 Object.abort         #save at $a2 abort method address
    sw $a2 0($a0)               #build virtual method table
    la $a2 Object.type_name
    sw $a2 4($a0) 
    la $a2 Object.copy
    sw $a2 8($a0) 
    la $a2 String.length
    sw $a2 12($a0) 
    la $a2 String.concat
    sw $a2 16($a0) 
    la $a2 String.substr
    sw $a2 20($a0)

    #----------------------------String prototype
    li $a0 20
    jal _MemMgr_Alloc           # allocate 20 bytes for a IO prototype
    sw $a0 24($s0)
    li $a1 3                    # the calss tag
    sw $a1 0($a0)               # set class tag in 2
    li $a1 20                   # the object size (4*num_of_attrs)
    sw $a1 4($a0)               # set the object size
    
    #### Dispatch Pointer
    sw $s2 8($a0)
    #------------------CODE TO ADD ITS CTOR
    la $a1 String.ctor
    sw $a1 28($s0)

# #################################################################################################
