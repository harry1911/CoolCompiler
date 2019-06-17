
from general import ast_hierarchy as ast_cool
from general import cil_hierarchy as cilH


class Node:
    def __init__(self,name,classTag,parent=None):
        self.name = name
        self.parent = parent           #the string name of the parent
        self.methods = []              #list of CILMethod
        self.attributes = []           #list of CILAttribute
        self.childs = []               #list of Node
        self.initializers = []          #list of ast_cool.FeatureAttributeNode
        self.classTag = classTag
        
    def contains(self,nodeName):
        if self.name == nodeName:
            return self
        for child in self.childs:
            searched = child.contains(nodeName)
            if searched != None:
                return searched
        return None
    
    def paint(self):
        if self.parent != None:
            print('I am ' + str(self.name) + ' son of ' + str(self.parent))
        else:
            print("I am " + (str)(self.name))
        for attr in self.attributes:
            attr.paint()
        for meth in self.methods:
            meth.paint()
        for child in self.childs:
            child.paint()
            

class InheritanceTree:
    def __init__(self):
        self.subtrees = []  #list of type Node
        
    def add_basic_types(self):
        #-----------adding Object type----------
        objectType = Node("Object",0)
        objectType.methods.append(cilH.CILMethod("abort","f1",0))
        objectType.methods.append(cilH.CILMethod("type_name","f2",1))        
        objectType.methods.append(cilH.CILMethod("copy","f3",2))
        #print('object added',len(objectType.methods))
        self.subtrees.append(objectType)
        #-----------adding IO type----------
        objectType2 = Node("IO",1,"Object")
        objectType2.methods.append(cilH.CILMethod("out_string","f4",0))
        objectType2.methods.append(cilH.CILMethod("out_int","f5",1))        
        objectType2.methods.append(cilH.CILMethod("in_string","f6",2))
        objectType2.methods.append(cilH.CILMethod("in_int","f7",3))     
        #print('IO added',len(objectType2.methods))  
        self.subtrees[0].childs.append(objectType2)
        #-----------adding Int type----------
        objectType4 = Node("Int",2,"Object")
        self.subtrees[0].childs.append(objectType4)
        #print('int added',len(objectType4.methods))
         #-----------adding String type----------
        objectType3 = Node("String",3,"Object")
        objectType3.methods.append(cilH.CILMethod("length","f8",0))
        objectType3.methods.append(cilH.CILMethod("concat","f9",1))        
        objectType3.methods.append(cilH.CILMethod("substr","f10",2))
        #print('string added',len(objectType3.methods))
        self.subtrees[0].childs.append(objectType3)
        #-----------adding Bool type----------
        objectType5 = Node("Bool",4,"Object")
        self.subtrees[0].childs.append(objectType5)
        #print('bool added',len(objectType5.methods))
   
    def add(self,node):  #node has type Node
        if len(self.subtrees) == 0: #is empty
            self.subtrees.append(node)
            return
        
        myNode = self.contains(node.name)
        if myNode != None:  #someone inserted me
            myNode.methods = node.methods
            myNode.attributes = node.attributes
            myNode.initializers = node.initializers
            myNode.classTag = node.classTag
            parent = self.contains(node.parent)
            myNode.parent = parent.name
            if parent != None:
                parent.childs.append(myNode)
                self.subtrees.remove(myNode)
            else:
                parent = Node(node.parent,-1)
                parent.childs.append(myNode)
                self.subtrees.append(parent)
            return           
    
        parent = self.contains(node.parent)
        if parent != None:  #my parent exist
            parent.childs.append(node)
            return

        parent = Node(node.parent,-1)
        myNode = Node(node.name,node.classTag,node.parent)
        myNode.methods = node.methods
        myNode.attributes = node.attributes
        myNode.initializers = node.initializers
        parent.childs.append(myNode)
        self.subtrees.append(parent)

        
    def contains(self, nodeName):
        for node in self.subtrees:
            searched = node.contains(nodeName) 
            if searched != None:
                return searched
        return None
        
    def paint(self):
        for tree in self.subtrees:
            tree.paint()
  