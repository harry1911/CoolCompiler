from general import visitor
from general import cil_hierarchy as ast_cil
from general import ast_hierarchy as ast_cool
from .context import Defaults
from . import inheritanceTree as inhTree


class TypesCollector:
    def __init__(self,astCool,typesDict):
        self.astCool = astCool #the ProgramNode of ASTCool (the root)
        self.astCil = ast_cil.CIL_Program()   #the CIL_ProgramNode of ASTCil (the root)
        self.astCil.dotTYPES = ast_cil.DotTYPES()
        self.strEnv = ""
        self.inhTree = inhTree.InheritanceTree()
        self.inhTree.add_basic_types()
        self.counter = 11
        self.typesDict = typesDict
 
    def getTypes(self):      #to start generating AST_Cil

        self.visit(self.astCool)    #to build inheritance tree
        queue = [self.inhTree.subtrees[0]]  #solve inheritance
        defaults = []          #una lista de context.defaults

        while len(queue) > 0:
            element = queue.pop(0)            
            defaults.append(Defaults(element.name, element.initializers))
                        
            actualType = ast_cil.CILType(element.name,element.classTag)

            if self.astCil.dotTYPES.types.__contains__(element.parent):
                parent = self.astCil.dotTYPES.types[element.parent]
                parentInitializers = self.inhTree.contains(element.parent).initializers
            else:
                parent = None
            nInheritedAttrs = 0
            nInheritedMeth = 0

            if parent != None: #para todos menos Object
                defaults[-1].defaults.extend(parentInitializers.__iter__()) #add initializers inheriteds
                nInheritedAttrs = len(parent.attributes)
                nInheritedMeth = len(parent.methods)

                for attr in parent.attributes.values(): #VER cuando se heredan  los atributos el nombre no es exactamente el mismo 
                    actualType.attributes[attr.name] = ast_cil.CILAttribute(attr.name, attr.offset)

                for meth in parent.methods.values():
                    actualType.methods[meth.name] = ast_cil.CILMethod(meth.name, meth.func, meth.offset)

            for attrOffset in range(len(element.attributes)):
                attr = element.attributes[attrOffset]
                actualType.attributes[attr.name] = ast_cil.CILAttribute(attr.name, attrOffset + nInheritedAttrs)
            
            numOfRed = 0
            for methOffset in range(len(element.methods)):
                meth = element.methods[methOffset]
                redefined = self.redefinesMethod(parent,meth.name)
                if not redefined: #no es una redefinicion
                    actualType.methods[meth.name] = ast_cil.CILMethod(meth.name, actualType.name + '.' + meth.name, methOffset + nInheritedMeth - numOfRed)
                else:
                    numOfRed += 1
                    actualType.methods[meth.name].func = actualType.name + '.' + meth.name
            
            self.astCil.dotTYPES.types[actualType.name] = actualType
            self.astCil.dotTYPES.map[actualType.num_id] = actualType.name
            
            for child in element.childs:
                queue.append(child)

        for _def in defaults:
            _def.defaults.sort(key=lambda x: self.astCil.dotTYPES.types[_def.class_name].attributes[x.name].offset)

        return { _def.class_name:_def for _def in defaults }


    def redefinesMethod(self,parent,method):
        if parent == None:
            return False
        for child_meth in parent.methods:
            if child_meth == method:
                return True
        return False
    
    @visitor.on('node')
    def visit(self, node):
        pass
    
    @visitor.when(ast_cool.ProgramNode)
    def visit(self, node):
        for classDef in node.class_list:
            self.visit(classDef)
            
    @visitor.when(ast_cool.ClassNode)
    def visit(self, node):

        actualType = inhTree.Node(node.name,self.typesDict[node.name])

        for attr in node.attribute_list:
            actualType.attributes.append(ast_cil.CILAttribute(attr.name,-1))
            actualType.initializers.append(attr) #featureAttributeNode

        for meth in node.method_list:
            actualType.methods.append(ast_cil.CILMethod(meth.name , "f" ,-1))
            # actualType.methods.append(ast_cil.CILMethod(meth.name , "f" + str(self.counter),-1))
            # #obtener el orden desde aqui y hacer que se respete
            # self.counter += 1            
        
        if node.parent == None:  #OJO-------------asumimos que si el padre es object se pone None y que est de tipo string
            actualType.parent = "Object"
        else:
            actualType.parent = node.parent
        
        self.inhTree.add(actualType)