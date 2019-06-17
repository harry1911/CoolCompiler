# TODO: es muy importante especificar la distincion de que una expression
# puede dar como resultado:
#   - un valor entero en memoria.
#   - una referencia a un objeto.
# Por tanto assign puede guardar en la direccion de memoria apuntada por
# destiny tanto un numero entero como una referencia a un objeto. 

# TODO: int(), str() significan tipos de python que se pasan en el node de CIL
#       para la generacion de codigo MIPS.

# TODO: expressiones que retornan un valor entero en lugar de una referencia:
#   - Aritmeticas
#   - TypeOf
#   - CILLessThan
#   - CILLessThanEq
#   - CILEqual
#   - CILVar

# TODO: - CILConditional: puede recibir los dos valores sin necesidad de restarlos

from general import visitor


class CILNode:
    pass

class CIL_Program(CILNode):
    def __init__(self):
        self.dotTYPES = None    # .TYPES section
        self.dotCODE = []     # .CODE section
        
##################################### .TYPES definitions ################################

class DotTYPES(CILNode):
    def __init__(self):
        self.types = {}     # { str(name) : CILType }
        self.map = {}       # { int(num_id) : str(name) }

    def add_type(self, _type):
        self.types[_type.name] = _type
        self.map[_type.num_id] = _type.name

    def get_type_by_name(self, name):
        return self.types.get(name)

    def get_type_by_id(self, num_id):
        return self.get_type_by_name(self.map.get(num_id))   

class CILType(CILNode):
    def __init__(self, name, num_id):
        self.name = name        # str(name)
        self.num_id = num_id    # int(tag_class)
        self.attributes = {}    # { str(name) : CILAttribute }
        self.methods = {}       # { str(name) : CILMethod }

class CILAttribute(CILNode):
    def __init__(self, name, offset):
        self.name = name        # str(name)
        self.offset = offset    # int(offset)

    def paint(self):
        print('        ',self.name)

class CILMethod(CILNode):
    def __init__(self, name, func, offset):
        self.name = name            # str(meth_name)
        self.func = func            # str(fun_name)
        self.offset = offset        # int(offset)

#########################################################################################
##################################### .CODE definitions #################################

# class DotCode(CILNode):
#     def __init__(self):
#         self.functions = {}    # { str(name) : CILFunction }

class CILFunction(CILNode):
    def __init__(self, name, params, localvars, statements):
        self.name = name                # str(name)
        self.params = params            # list(CILArgument)
        self.localvars = localvars      # list(CILLocalvar)
        self.statements = statements    # list(CILStatement)

class CILArgument(CILNode):    # to use to receive an arg in a func
    '''
    Se usa en la declaracion de una funcion para 
    recibir los argumentos.
    '''
    def __init__(self, name, local_value):
        self.name = name    # str(name)
        self.local_value = local_value # object of type CILLocalvar, represent a reference to the argument object in memory

class CILLocalvar(CILNode):
    '''
    Define una variable local con nombre name y 
    valor value.
    '''
    def __init__(self, name, value):
        self.name = name    # str(name)
        self.value = value  # int(value)
        # value is necessary because sometimes I need to create a local
        # variable with a specific default value. So the semantic of this
        # in MIPS code generation is:
        # 1- local_ptr = allocate memory for local_name
        # 2- store in local_ptr the 32-bit number representation of value

class CILStatement(CILNode):
    pass

class CILAssignment(CILStatement):
    '''
    Asigna al lugar de memoria a donde apunta la 
    variable local destiny el resultado de computar
    expr. Este resultado se puede interpretar tanto
    como una referencia o como un numero.
    '''
    def __init__(self, destiny, expr):
        self.destiny = destiny      # left part of assignation, object of type CILLocalvar
        self.expr = expr            # right part of assignation, object of type CILExpression

class CILExpression(CILNode):
    pass

class CILAritmeticNode(CILExpression):
    '''
    Retorna el valor entero resultado de computar (left op rigth).
    '''
    def __init__(self, left, right):
        self.left = left    # object of type CILLocalvar: an int value in memory
        self.right = right  # object of type CILLocalvar: an int value in memory

class CILPLus(CILAritmeticNode):
    def __init__(self, left, right):
        super().__init__(left, right)      

class CILMinus(CILAritmeticNode):
    def __init__(self, left, right):
        super().__init__(left, right)

class CILMult(CILAritmeticNode):
    def __init__(self, left, right):
        super().__init__(left, right)

class CILDiv(CILAritmeticNode):
    def __init__(self, left, right):
        super().__init__(left, right)

# class CILConstructor(CILExpression):
#     '''
#     Representa una invocacion dinamica de la funcion
#     constructora del tipo con id = type_id. Retorna 
#     la direccion de memoria donde se encuentra la 
#     instancia que se le paso como argumento. Esta
#     direccion no cambia.    
#     '''
#     def __init__(self, type_id):
#         self.type_id = type_id     # the id of a type: object of type CILLocalvar: an int value in memory

class CILStaticCall(CILExpression):
    '''
    Representa una invocacion dinamica de la funcion
    func_name. Retorna la direccion de memoria donde 
    se encuentra el valor de retorno de la funcion.
    '''
    def __init__(self, func_name):
        self.func_name = func_name  # str(func_name): represent a function name in .code 
        
class CILDinamicCall(CILExpression):
    '''
    Representa una invocacion dinamica de el metodo
    con offset meth_offset en el tipo de var.
    Retorna la direccion de memoria donde se encuentra el
    valor de retorno del metodo.
    '''
    def __init__(self, var, meth_offset):
        self.var = var                  # object of type CILLocalvar, represent a reference to an object in memory
        self.meth_offset = meth_offset  # the method offset: int(meth_offset)

class CILBinaryOperator(CILExpression):
    def __init__(self, oper1, oper2):
        self.oper1 = oper1      # first operand
        self.oper2 = oper2      # second operand
        
class CILUnaryOperator(CILExpression):
    def __init__(self, operand):
        self.operand = operand  # operand

class CILGetAttr(CILBinaryOperator):
    '''
    Retorna la direccion de memoria donde se encuentra el
    atributo, o sea la direccion de memoria a la cual hace 
    referencia el campo del atributo en el espacio de 
    memoria del tipo.
    '''
    def __init__(self, var, attr_offset):
        super().__init__(var, attr_offset)
        # var: object of type CILLocalvar, represent a reference to an object in memory
        # attr_offset: the attribute offset: int(attr_offset)

class CILLessThan(CILBinaryOperator):
    '''
    Retorna el valor int 0 o 1, o sea si es false o true.
    '''
    def __init__(self, left, right):
        super().__init__(left, right)
        # object of type CILLocalvar: an int value in memory
        # object of type CILLocalvar: an int value in memory

class CILLessThanEq(CILBinaryOperator):
    '''
    Retorna el valor int 0 o 1, o sea si es false o true.
    '''
    def __init__(self, left, right):
        super().__init__(left, right)
        # object of type CILLocalvar: an int value in memory
        # object of type CILLocalvar: an int value in memory

class CILEqual(CILBinaryOperator):
    '''
    Chequea si los objetos tienen el mismo tipo
    basico y el mismo contenido. Retorna un valor
    entero 0 o 1.
    '''
    def __init__(self, left, right):
        super().__init__(left, right)
        # object of type CILLocalvar: a reference to an object in memory
        # object of type CILLocalvar: a reference to an object in memory

class CILGetIndex(CILUnaryOperator):
    '''
    Retorna el valor entero que se encuentra en esa 
    posicion del array que representa la jerarquia de
    clases.
    '''
    def __init__(self, index):
        super().__init__(index)
        # index: object of type CILLocalvar: an int value in memory
        
class CILAllocate(CILUnaryOperator):
    '''
    Retorna la direccion de memoria donde se encuentra el
    espacio de memoria reservado.
    '''
    def __init__(self, type_id):
        super().__init__(type_id)
        # type_id: the id of a type: object of type CILLocalvar: an int value in memory

class CILTypeOf(CILUnaryOperator):
    '''
    Retorna el valor int que representa el tag_class de var.
    '''
    def __init__(self, var):
        super().__init__(var)
        # var: object of type CILLocalvar, represent a reference to an object in memory

class CILSetAttr(CILStatement):
    '''
    Iguala el pointer del atributo con offset att_offset
    en el tipo de var al valor en la direccion de memoria de source. 
    '''
    def __init__(self, var, attr_offset, source):
        self.var = var                      # object of type CILLocalvar, represent a reference to an object in memory
        self.attr_offset = attr_offset      # the attribute offset: int(attr_offset)
        self.source = source                # object of type CILLocalvar, represent a reference to an object in memory 
                                            #                              or it can be an int value in memory 
        # ex: SETATTR var attr source ===> var.attr = source    
        
class CILCondition(CILStatement):
    def __init__(self, var, label):
        self.var = var      # object of type CILLocalvar: an int value in memory
        self.label = label  # the name of the label: str(label)

class CILReturn(CILStatement):
    def __init__(self, value = None):
        self.value = value      # (object of type CILLocalvar, representing a reference to an object in memory
                                # or an int in memory) or nothing

class CILLabel(CILStatement):
    def __init__(self, label):
        self.label = label      # the name of the label: str(label)

class CILGoTo(CILStatement):
    def __init__(self, label):
        self.label = label      # the name of the label: str(label)

class CILParam(CILStatement):    # to use to pass an arg to a func
    def __init__(self, var):
        self.var = var      # object of type CILLocalvar, represent a reference to an object in memory

class CILString(CILUnaryOperator):
    '''
    Retorna la direccion de memoria donde se encuentra el
    objeto string inicializado.
    '''
    def __init__(self, text=''):
        super().__init__(text)  # str(value)

class CILVar(CILUnaryOperator):   # to represent a declared var ej: LOCAL a, LOCAL b
    '''
    Expression que retorna el valor almacenado en el
    local_var.
    '''
    def __init__(self, local_var):
        super().__init__(local_var)


def get_formatter():

    class PrintVisitor(object):
        @visitor.on('node')
        def visit(self, node):
            pass

        @visitor.when(CIL_Program)
        def visit(self, node):
            dottypes = '\n'.join(self.visit(t) for t in node.dotTYPES.types.values())
            # dotdata = '\n'.join(self.visit(t) for t in node.dotdata)
            dotcode = '\n'.join(self.visit(t) for t in node.dotCODE)

            return f'.TYPES\n{dottypes}\n\n.CODE\n{dotcode}'

        @visitor.when(CILType)
        def visit(self, node):
            attributes = '\n\t'.join(f'attribute {x.name}: {x.offset}' for x in node.attributes.values())
            methods = '\n\t'.join(f'method {x.name}: {x.offset} {x.func}' for x in node.methods.values())

            return f'type {node.name} id {node.num_id} {{\n\t{attributes}\n\n\t{methods}\n}}'

        @visitor.when(CILFunction)
        def visit(self, node):
            params = '\n\t'.join(self.visit(x) for x in node.params)
            localvars = '\n\t'.join(self.visit(x) for x in node.localvars)
            instructions = '\n\t'.join(self.visit(x) for x in node.statements)

            return f'function {node.name} {{\n\t{params}\n\n\t{localvars}\n\n\t{instructions}\n}}'

        @visitor.when(CILArgument)
        def visit(self, node):
            return f'ARG {node.name}: {node.local_value.name}'

        @visitor.when(CILLocalvar)
        def visit(self, node):
            return f'LOCAL {node.name} : {node.value}'

        @visitor.when(CILAssignment)
        def visit(self, node):
            return f'{node.destiny.name} = {self.visit(node.expr)}'

        @visitor.when(CILPLus)
        def visit(self, node):
            return f'{node.left.name} + {node.right.name}'

        @visitor.when(CILMinus)
        def visit(self, node):
            return f'{node.left.name} - {node.right.name}'

        @visitor.when(CILMult)
        def visit(self, node):
            return f'{node.left.name} * {node.right.name}'

        @visitor.when(CILDiv)
        def visit(self, node):
            return f'{node.left.name} / {node.right.name}'

        # @visitor.when(CILConstructor)
        # def visit(self, node):
        #     return f'CTOR {node.type_id.name}'

        @visitor.when(CILStaticCall)
        def visit(self, node):
            return f'CALL {node.func_name}'

        @visitor.when(CILDinamicCall)
        def visit(self, node):
            return f'VCALL {node.var.name} {node.meth_offset}'

        @visitor.when(CILGetAttr)
        def visit(self, node):
            return f'GETATTR {node.oper1.name} {node.oper2}'

        @visitor.when(CILLessThan)
        def visit(self, node):
            return f'{node.oper1.name} < {node.oper2.name}'

        @visitor.when(CILLessThanEq)
        def visit(self, node):
            return f'{node.oper1.name} <= {node.oper2.name}'

        @visitor.when(CILEqual)
        def visit(self, node):
            return f'{node.oper1.name} == {node.oper2.name}'

        @visitor.when(CILGetIndex)
        def visit(self, node):
            return f'GETINDEX {node.operand.name}'

        @visitor.when(CILAllocate)
        def visit(self, node):
            return f'ALLOCATE {node.operand.name}'

        @visitor.when(CILTypeOf)
        def visit(self, node):
            return f'TYPEOF {node.operand.name}'

        @visitor.when(CILSetAttr)
        def visit(self, node):
            return f'SETATTR {node.var.name} {node.attr_offset} {node.source.name}'

        @visitor.when(CILCondition)
        def visit(self, node):
            return f'IF {node.var.name} GOTO {node.label}'

        @visitor.when(CILReturn)
        def visit(self, node):
            return f'RETURN {node.value.name if node.value is not None else ""}'

        @visitor.when(CILLabel)
        def visit(self, node):
            return f'LABEL {node.label}'

        @visitor.when(CILGoTo)
        def visit(self, node):
            return f'GOTO {node.label}'

        @visitor.when(CILParam)
        def visit(self, node):
            return f'PARAM {node.var.name}'
        
        @visitor.when(CILString)
        def visit(self, node):
            return f"STRING '{node.operand}'"

        @visitor.when(CILVar)
        def visit(self, node):
            return f'VAR {node.operand.name}'

    printer = PrintVisitor()
    return (lambda ast: printer.visit(ast))