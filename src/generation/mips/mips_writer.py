from general import cil_hierarchy as cil
from general import  visitor
import os

basedir = os.path.abspath(os.path.dirname(__file__))

OBJECT_SIZE = 4
OBJECT_TAG = 0
OBJECT_DISPATCH = 8
OBJECT_FIRST_ATTR = 12
INT_PROTOTYPE = 16
BOOL_PROTOTYPE = 32

class MIPSWriterVisitor():
    def __init__(self,ast_cil,name_of_file):
        self.output = []        # the list of MIPS insructions
        self.params_list = []   # the list of params to call a function
        self.localsDict = {}    # varName ------> offset In Frame Pointer
        self.astCil = ast_cil
        self.numRets = 0
        self.numBranch = 0 
        self.name_of_file = name_of_file


    def generate_Mips(self):
        self.startFile()
        self.copyFrom('data.asm') 
        for str_type in self.astCil.dotTYPES.types: #foreach key in types generate its data string
            self.emit('_{0}:  .asciiz "{0}"'.format(str_type),0)

        self.copyFrom('text.asm')
        #make code for build in runtime all tables     
        self.emit('initialize:',0)   
        self.push('$ra')
        self.emit('move $s7 $gp')
        self.emit('li $a1 10000000')
        self.emit('add $s7 $s7 $a1')
        # self.emit('li $s7 1000000')
        # self.emit('addu $s7 $s7 $gp')
        self.createTableS1()
        self.createTableS0()
        self.createHierarchyTable()
        self.pop('$ra')
        self.emit('jr $ra')
        self.visit(self.astCil)
        #setup entry point
        self.addEntry()
        self.closeFile()

    def startFile(self):
        writer = open('{0}'.format(self.name_of_file),'w')
        writer.close()
        self.writer = open('{0}'.format(self.name_of_file),'a')         

    def emit(self, msg,spaces = 4):
        s = ''
        for _ in range(spaces):
            s += ' ' 
        self.writer.write(s + msg + '\n')

    def closeFile(self):
        self.writer.close()

    def copyFrom(self, address):
        reader = open(basedir + '/' + address, mode = 'r')
        text = reader.read()
        self.writer.write(text)
        self.writer.write('\n')
        reader.close()

    def push(self, value):
        self.emit('sw ' + str(value) + ' 0($sp)')
        self.emit('addiu $sp $sp -4')
    
    def pop(self, destiny):
        self.emit('lw ' + str(destiny) + ' 4($sp)')
        self.emit('addiu $sp $sp 4')

    def createHierarchyTable(self):
        self.emit('#----Creating hierarchy table----',0)
        self.emit('li $a0 {0}'.format(len(self.astCil.typesHierarchy)*4))          # $a0 <-- len(table)
        self.emit('jal _MemMgr_Alloc')  # allocate n bytes. The reference is in $a0
        self.emit('move $s4 $a0')

        for i in range(len(self.astCil.typesHierarchy)):
            # self.emit('move $s4 $a0')
            self.emit('li $a1 {0}'.format(self.astCil.typesHierarchy[i]))
            self.emit('sw $a1 {0}($s4)'.format(4*i))
        self.emit('#----Created hierarchy table----',0)

    # Emits the MIPS code to create an string object in memory and store its reference in $a0
    # s: the string to allocate
    #(OK)
    def create_string(self, s):
        size = len(s) + 17  #porque el len de python no incluye el fin de linea
        if size % 4 != 0:
            size += (4-(size % 4))
        self.emit('#----Creating a String object----',0)
        self.push('$ra')
        self.emit('li $a0 {0}'.format(size))     # $a0 <-- size (size is 'class tag' + 'object size' + 'dispatch' + 'Int ptr')
        self.emit('jal _MemMgr_Alloc')  # allocate size bytes. The reference is in $a0
        self.pop('$ra')
        self.emit('li $a1 3')      # the calss tag
        self.emit('sw $a1 {0}($a0)'.format(OBJECT_TAG))      # set class tag in 3
        self.emit('li $a1 {0}'.format(size))   # the object size
        self.emit('sw $a1 {0}($a0)'.format(OBJECT_SIZE))      # set the object size
        self.emit('sw $s2 {0}($a0)'.format(OBJECT_DISPATCH))  # set the object dispatch
        self.push('$a0')
        self.createInt(len(s))
        # self.push('$ra')
        # self.emit(f'li $a0 {len(s)}')
        # self.emit('jal Int_init')
        # self.pop('$ra')
        self.emit('move $a1 $a0') #save in $a1 reference to INT.length
        self.pop('$a0')
        self.emit('sw $a1 {0}($a0)'.format(OBJECT_FIRST_ATTR))

        pos = OBJECT_FIRST_ATTR + 4
        for char in s:
            self.emit('li $a1 {0}'.format(ord(char)))
            self.emit('sb $a1 {0}($a0)'.format(pos))
            pos += 1
        self.emit('li $a1 0') #para que ponga el fin de linea
        self.emit('sb $a1 {0}($a0)'.format(pos))
        #finaly in $a0 stay the reference to the begining of the created object
        self.emit('#----Created String object----',0)

    #To be called before initialize the table in $s1 (TAG_CLASS ---> str(name_of_class))
    def createTableS1(self):
        size = 4 * len(self.astCil.dotTYPES.types)        
        self.emit('#----TABLE S1----',0)
        self.emit('li $a0 {0}'.format(size))
        self.emit('jal _MemMgr_Alloc')
        self.emit('move $s1 $a0')

        for typeId in self.astCil.dotTYPES.types.values():
            tag = 4 * typeId.num_id
            self.emit('la $a1 _{0}'.format(typeId.name))
            self.emit('sw $a1 {0}($s1)'.format(tag))
            self.emit('move $a1 $zero')

    #(OK) To initialize the table in $s0 (TAG_CLASS ---> (PROTOTYPE,BUILDER))
    def createTableS0(self):
        size = 8 * len(self.astCil.dotTYPES.types)

        self.emit('#----TABLE S0----',0)
        self.emit('li $a0 {0}'.format(size))    #allocate space
        self.emit('jal _MemMgr_Alloc')
        self.emit('move $s0 $a0')
        
        self.copyFrom('fixedCodeOfTableS0.asm')   #add predefined prototypes

        self.emit('#----automatic code for TABLE S0----',0)
        for typeObj in self.astCil.dotTYPES.types.values():     #add others prototypes
            if typeObj.num_id < 5:
                continue
            else:
                size = (4*len(typeObj.attributes) + 12)
                self.emit('li $a0 {0}'.format(size))
                self.emit('jal _MemMgr_Alloc')
                self.emit('sw $a0 {0}($s0)'.format(8*typeObj.num_id))
                self.emit('li $a1 {0}   # the class tag'.format(typeObj.num_id))
                self.emit('sw $a1 {0}($a0)'.format(OBJECT_TAG))
                self.emit('li $a1 {0}'.format(size))
                self.emit('sw $a1 {0}($a0)'.format(OBJECT_SIZE))
                #code for dispatch pointer
                self.emit('move $a1 $a0')                
                self.emit('li $a0 {0}'.format(4*len(typeObj.methods)))
                self.emit('jal _MemMgr_Alloc')
                self.emit('sw $a0 {0}($a1)'.format(OBJECT_DISPATCH)) #now in $a0 is dispatch pointer and in $a1 is the pointer to prototype
                for meth in typeObj.methods.values():
                    self.emit('la $t4 {0}'.format(meth.func))
                    self.emit('sw $t4 {0}($a0)'.format(4*meth.offset))
                    self.emit('move $t4 $zero')
        self.emit('#----TABLE S0 ctors----',0)
        for typeObj in self.astCil.dotTYPES.types.values():   #add builders methods labels
            if typeObj.num_id < 5:
                continue
            else:
                self.emit('la $t4 {0}.ctor'.format(typeObj.name))
                self.emit('sw $t4 {0}($s0)'.format((8*typeObj.num_id)+4))
                self.emit('move $t4 $zero')
        self.emit('#----TABLE S0 builded----',0)
        
    #(OK)
    def createInt(self,IntValue): #return in $a0 the Int object
        self.emit('#----Creating an Int object----',0)
        self.push('$ra')
        self.emit('lw $a0 {0}($s0)'.format(INT_PROTOTYPE))
        # self.emit('lw $a0 0($a0) #ver si es 2!!!!!!!!!!!!!!!!!!!!') #new
        self.push('$a0')
        self.emit('jal Object.copy')
        self.emit('li $a1 {0}'.format(IntValue))
        self.emit('sw $a1 {0}($a0)'.format(OBJECT_FIRST_ATTR))
        self.pop('$ra')
        self.emit('#----Created Int object----',0)

    def createBool(self,BoolValue):
        self.push('$ra')
        self.emit('lw $a0 {0}($s0)'.format(BOOL_PROTOTYPE))
        self.push('$a0')
        self.emit('jal Object.copy')
        self.emit('li $a1 {0}'.format(BoolValue))
        self.emit('sw $a1 {0}($a0)'.format(OBJECT_FIRST_ATTR))
        self.pop('$ra')

    #(OK)
    def addEntry(self):
        self.emit('.globl main',0)
        self.emit('main:',0)
        self.emit('jal initialize')
        self.emit('lw $a0 {0}($s0)'.format(self.astCil.dotTYPES.types['Main'].num_id*8)) #$a0 <- direccion del prototipo
        self.push('$a0')
        self.emit('jal Object.copy')
        self.push('$a0') #parameter for Ctor
        self.emit('jal Main.ctor')
        self.push('$a0')
        self.emit('jal Main.main')
        self.emit('la $a0 _term_msg')
        self.emit('li $v0 4')
        self.emit('syscall')
        self.emit('li $v0 10')
        self.emit('syscall')

##########################################################---- VISITORS ----##########################################################

    @visitor.on('node')
    def visit(self, node):
        pass

    @visitor.when(cil.CIL_Program)#(OK)
    def visit(self, node: cil.CIL_Program):
        for x in node.dotCODE:
            self.visit(x)

    @visitor.when(cil.CILString) #(OK)
    def visit(self, node: cil.CILString):
        self.create_string(node.operand)

    @visitor.when(cil.CILFunction) #(OK)
    def visit(self, node: cil.CILFunction):
        self.emit('{0}:'.format(node.name),0)    # the label for the function entry
        self.push('$ra')                    # save the return address
        self.localsDict.clear()             #clear the current enviroment of vars
        ############ GENERATE CODE FOR FUNCTION #########
        
        #local(i) = sp + 4(i) + 4
        #param(i) = sp + 4*i + (len(locals)*4 + 8)

        argOffset = 8 + (len(node.localvars)*4)
        for i in range(0,len(node.params)):  #  EL PRIMERO ES EL SELF?????????????????????????????????????????????????????????????
            self.localsDict[node.params[i].local_value.name] = argOffset
            argOffset += 4

        argOffset = 4*len(node.localvars)
        for local in node.localvars:
            self.localsDict[local.name] = argOffset
            argOffset -= 4
            self.visit(local)          

        for stat in node.statements:
            self.visit(stat)

        #################################################
        # RESTORE THE VALUES TO PRESERV THE SATCK
        nLocals = len(node.localvars)
        self.emit('addiu $sp $sp {0}'.format(4*nLocals))
        self.pop('$ra')
        nArgs = len(node.params)
        self.emit('addiu $sp $sp {0}'.format(4*nArgs))
        self.emit('jr $ra') # jump to return address

    @visitor.when(cil.CILLocalvar) #(OK)
    def visit(self, node: cil.CILLocalvar):
        self.emit('li $a1 {0}'.format(node.value)) #save its value
        self.push('$a1')
        self.emit('move $a0 $a1') #return its value
   
    @visitor.when(cil.CILAssignment) #(OK)
    def visit(self, node: cil.CILAssignment):
        self.visit(node.expr) #in $a0 is the result of the expression (READY TO RETURN)
        self.emit('#ASSIGN')
        self.emit('sw $a0 {0}($sp)'.format(self.localsDict[node.destiny.name])) 
        
    @visitor.when(cil.CILPLus) #(OK)
    def visit(self, node: cil.CILPLus):
        self.emit('lw $a0 {0}($sp)'.format(self.localsDict[node.left.name])) #a0 <- valor INT
        self.emit('lw $a1 {0}($sp)'.format(self.localsDict[node.right.name])) #a1 <- valor INT
        # self.emit('lw $a0 0($a0)')
        # self.emit('lw $a1 0($a1)')
        self.emit('add $a0 $a0 $a1')        

    @visitor.when(cil.CILMinus) #(OK)
    def visit(self, node: cil.CILMinus):
        self.emit('lw $a0 {0}($sp)'.format(self.localsDict[node.left.name])) #a0 <- valor INT
        self.emit('lw $a1 {0}($sp)'.format(self.localsDict[node.right.name])) #a1 <- valor INT
        # self.emit('addi $a0 {0}'.format(12) #a0 <- direccion del atributo a setear
        # self.emit('addi $a1 {0}'.format(12) #a1 <- direccion del atributo a setear
        # self.emit('lw $a0 0($a0)')
        # self.emit('lw $a1 0($a1)')
        self.emit('sub $a0 $a0 $a1')

    @visitor.when(cil.CILMult) #(OK)
    def visit(self, node: cil.CILMult):
        self.emit('lw $a0 {0}($sp)'.format(self.localsDict[node.left.name])) #a0 <- valor INT
        self.emit('lw $a1 {0}($sp)'.format(self.localsDict[node.right.name])) #a1 <- valor INT
        # self.emit('addi $a0 {0}'.format(12) #a0 <- direccion del atributo a setear
        # self.emit('addi $a1 {0}'.format(12) #a1 <- direccion del atributo a setear
        # self.emit('lw $a0 0($a0)')
        # self.emit('lw $a1 0($a1)')
        self.emit('mul $a0 $a0 $a1')

    @visitor.when(cil.CILDiv) #(OK)
    def visit(self, node: cil.CILDiv):
        self.emit('lw $a0 {0}($sp)'.format(self.localsDict[node.left.name])) #a0 <- valor INT
        self.emit('lw $a1 {0}($sp)'.format(self.localsDict[node.right.name])) #a1 <- valor INT
        # self.emit('addi $a0 {0}'.format(12) #a0 <- direccion del atributo a setear
        # self.emit('addi $a1 {0}'.format(12) #a1 <- direccion del atributo a setear
        # self.emit('lw $a0 0($a0)')
        # self.emit('lw $a1 0($a1)')
        self.emit('div $a0 $a1')
        self.emit('mflo $a0')    

    @visitor.when(cil.CILLessThan) #(OK)
    def visit(self, node: cil.CILLessThan):
        self.emit('lw $a0 {0}($sp)'.format(self.localsDict[node.oper1.name])) #a0 <- valor INT
        self.emit('lw $a1 {0}($sp)'.format(self.localsDict[node.oper2.name])) #a1 <- valor INT
        self.emit('sub $a1 $a0 $a1') #(r < 0) => True, (r >= 0) => False        
        self.numBranch += 1
        self.emit('bgez $a1 false{0}'.format(self.numBranch)) #Branch on Greater Than or Equal to Zero
        self.emit('li $a0 1')
        self.emit('b end{0}'.format(self.numBranch+1))
        self.emit('false{0}:'.format(self.numBranch),0)
        self.emit('move $a0 $zero')
        self.numBranch += 1
        self.emit('end{0}:'.format(self.numBranch),0)

    @visitor.when(cil.CILLessThanEq) #(OK)
    def visit(self, node: cil.CILLessThanEq):
        self.emit('lw $a0 {0}($sp)'.format(self.localsDict[node.oper1.name])) #a0 <- valor INT
        self.emit('lw $a1 {0}($sp)'.format(self.localsDict[node.oper2.name])) #a1 <- valor INT
        self.emit('sub $a1 $a0 $a1') #(r <= 0) => True, (r > 0) => False        
        self.numBranch += 1
        self.emit('blez $a1 false{0}'.format(self.numBranch)) #Branch on Less or Eq to Zero ????????????????????????????????????????????????????????????????????????????????
        self.emit('move $a0 $zero')
        self.emit('b end{0}'.format(self.numBranch+1))
        self.emit('false{0}:'.format(self.numBranch),0)
        self.emit('li $a0 1')
        self.numBranch += 1
        self.emit('end{0}:'.format(self.numBranch),0)

    @visitor.when(cil.CILEqual) #(OK)
    def visit(self, node: cil.CILEqual):
        self.emit('lw $t1 {0}($sp)'.format(self.localsDict[node.oper1.name])) #t1 <- direccion de memoria del left
        self.emit('lw $t2 {0}($sp)'.format(self.localsDict[node.oper2.name])) #t2 <- direccion de memoria del right
        self.emit('li $a0 1')
        self.emit('li $a1 0')
        self.emit('jal equality_test')

    @visitor.when(cil.CILVar) #(OK)
    def visit(self,node: cil.CILVar):
        self.emit('lw $a0 {0}($sp)'.format(self.localsDict[node.operand.name])) #a0 <- valor almacenado en var

    @visitor.when(cil.CILStaticCall) #(OK)
    def visit(self, node: cil.CILStaticCall):
        #ya los parametros fueron pasados y el primero que se paso es self, solo queda llamar a la funcion
        self.emit('move $fp $sp')
        while len(self.params_list) > 0:
            self.emit('lw $a1 {0}($fp)'.format(self.localsDict[self.params_list.pop()])) #$a1 <- reference to the variable
            self.push('$a1')
        self.emit('jal {0}'.format(node.func_name)) # jump and link to the function entry label

    @visitor.when(cil.CILDinamicCall) #(OK)
    def visit(self, node: cil.CILDinamicCall):
        #lo mismo pero buscando en la tabla el entry (metodo con el offset dado) para el tag del objeto al que apunta la variable que me llaman
         #ya los parametros fueron pasados y el primero que se paso es self, solo queda llamar a la funcion

        self.emit('lw $a1 {0}($sp)'.format(self.localsDict[node.var.name]))  #$a1 <- object prototype
        self.emit('lw $a1 {0}($a1)'.format(OBJECT_DISPATCH))  # $a1 <- dispatch pointer del object 
        self.emit('lw $t1 {0}($a1)'.format(4*node.meth_offset))  #$a1 <- la entry

        self.emit('move $fp $sp')
        while len(self.params_list) > 0:
            self.emit('lw $a1 {0}($fp)'.format(self.localsDict[self.params_list.pop()])) #$a1 <- reference to the variable
            self.push('$a1')
        
        self.numRets += 1
        self.emit('la $ra return{0}'.format(self.numRets))
        self.emit('jr $t1')
        self.emit('return{0}:'.format(self.numRets),0)

    @visitor.when(cil.CILGetAttr) #(OK)
    def visit(self, node: cil.CILGetAttr):
        self.emit('#GETATTR')
        self.emit('lw $a0 {0}($sp)'.format(self.localsDict[node.oper1.name])) #a0 <- direccion de memoria del prototipo
        self.emit('addiu $a0 {0}'.format(12+4*node.oper2)) #a0 <- direccion del atributo a setear
        self.emit('lw $a0 0($a0)')

    @visitor.when(cil.CILGetIndex)
    def visit(self, node: cil.CILGetIndex):
        self.emit('lw $a0 {0}($sp)'.format(self.localsDict[node.operand.name])) #a0 <- valor entero tag_class
        self.emit('move $a1 $s4') #puts in $a1 the pointer to the table
        self.emit('sll $a0 $a0 2')
        self.emit('addu $a1 $a1 $a0') #puts in $a1 correcte offset of table 
        self.emit('lw $a0 0($a1)') #save in $a0 the value of the table

    @visitor.when(cil.CILAllocate) #(OK)
    def visit(self, node: cil.CILAllocate):     
        self.emit('#ALLOCATE')
        self.emit('lw $a0 {0}($sp)'.format(self.localsDict[node.operand.name])) #$a0 <- valor INT del TAG
        self.emit('move $s6 $a0')   #guardar el TAG en $s6
        self.emit('sll $a0 $a0 3')
        self.emit('addu $a0 $a0 $s0') # poner en $a0 el offset con respecto a $s0 donde esta la direccion del proto
        self.emit('lw $a0 0($a0)')  
        self.push('$a0')
        self.emit('jal Object.copy')
        #en $a0 esta la copia del prototipo
        # self.emit('li $t0 8')   
        # self.emit('mul $s6 $s6 $t0')   # $s6*=8
        self.emit('sll $s6 $s6 3')
        self.emit('addiu $s6 4')# en $s6 esta el offset correcto para el ctor
        self.emit('addu $s6 $s6 $s0')# en $s6 la direccion del ctor
        self.emit('lw $s6 0($s6)') #NEW
        self.numRets += 1
        self.emit('la $ra return{0}'.format(self.numRets))        
        self.push('$a0')
        self.emit('jr $s6')             # $s6 = direccion del ctor
        self.emit('return{0}:'.format(self.numRets),0)
    
    @visitor.when(cil.CILTypeOf) #(OK)
    def visit(self, node: cil.CILTypeOf):
        self.emit('lw $a0 {0}($sp)'.format(self.localsDict[node.operand.name])) #a0 <- direccion de memoria del prototipo
        self.emit('lw $a0 0($a0)')

    @visitor.when(cil.CILSetAttr)  #(OK)
    def visit(self, node: cil.CILSetAttr):
        self.emit('#SETATTR')
        self.emit('lw $a0 {0}($sp)'.format(self.localsDict[node.var.name])) #a0 <- direccion de memoria del prototipo
        self.emit('addi $a0 {0}'.format(12+4*node.attr_offset)) #a0 <- direccion del atributo a setear
        self.emit('lw $a1 {0}($sp)'.format(self.localsDict[node.source.name])) #PONER EN a1 lo que hay que setear
        self.emit('sw $a1 0($a0)')    
        self.emit('lw $a0 0($a0)')    

    @visitor.when(cil.CILCondition) #(OK)
    def visit(self, node: cil.CILCondition):
        self.emit('lw $a0 {0}($sp)'.format(self.localsDict[node.var.name]))
        self.emit('bne $a0 $zero {0}'.format(node.label)) 

    @visitor.when(cil.CILReturn) #(OK)
    def visit(self, node: cil.CILReturn):
        if node.value != None:
            self.emit('lw $a0 {0}($sp)'.format(self.localsDict[node.value.name]))

    @visitor.when(cil.CILLabel) #(OK)
    def visit(self, node: cil.CILLabel):
        self.emit(node.label + ':',0)

    @visitor.when(cil.CILGoTo) #(OK)
    def visit(self, node: cil.CILGoTo):
        self.emit('b ' + node.label)

    @visitor.when(cil.CILParam) #(OK)
    def visit(self, node: cil.CILParam):
        self.params_list.append(node.var.name)
