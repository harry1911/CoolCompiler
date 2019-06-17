import itertools as itl

from .type import Type, Attribute
from general import errors
from .scope import Scope
from .rmq_lca import LCA


class Enviroment:
    def __init__(self, parent=None):
        # object context
        self.locals = dict() # dict of Attributes { str : Attribute }
        self.parent = parent # enviroment
        self.children = []  # list of enviroments

        if parent is None:
            # method context
            self.inheritance_graph = None
            self.lca_structure = None
            self.types_list = [] # stores a list of Type
            self.types_dict = {} # stores a dictionary of { str : int } --> { name : index in types_list}
            self.add_basic_types()
        else:
            # method context
            self.inheritance_graph = parent.inheritance_graph
            self.lca_structure = parent.lca_structure
            self.types_list = parent.types_list
            self.types_dict = parent.types_dict
            parent.children.append(self)

    def add_basic_types(self):
        # Object
        object_type = Type(name="Object")
        object_type.define_method(name="abort",return_type="Object",argument_list=[],argument_types=[], line=0, column=0)
        object_type.define_method(name="type_name",return_type="String",argument_list=[],argument_types=[], line=0, column=0)
        object_type.define_method(name="copy",return_type="SELF_TYPE",argument_list=[],argument_types=[], line=0, column=0)    
        # IO
        io_type =Type(name="IO", parent=object_type.name)
        io_type.define_method(name="out_string",return_type="SELF_TYPE",argument_list=["arg"],argument_types=["String"], line=0, column=0)
        io_type.define_method(name="out_int",return_type="SELF_TYPE",argument_list=["arg"],argument_types=["Int"], line=0, column=0)
        io_type.define_method(name="in_string",return_type="String",argument_list=[],argument_types=[], line=0, column=0)
        io_type.define_method(name="in_int",return_type="Int",argument_list=[],argument_types=[], line=0, column=0)
        # Int
        int_type = Type(name="Int", parent=object_type.name)
        int_type.define_attribute("_val", "Int", line=0, column=0)
        # String
        string_type = Type(name="String", parent=object_type.name)
        string_type.define_attribute("_val", "Int", line=0, column=0)
        string_type.define_attribute("_str", "String", line=0, column=0)
        string_type.define_method(name="length", return_type="Int", argument_list=[], argument_types=[], line=0, column=0)
        string_type.define_method(name="concat", return_type="String", argument_list=["arg"], argument_types=["String"], line=0, column=0)
        string_type.define_method(name="substr", return_type="String", argument_list=["arg1", "arg2"], argument_types=["Int", "Int"], line=0, column=0)
        # Bool
        bool_type = Type(name="Bool", parent=object_type.name)
        bool_type.define_attribute("_val", "Bool", line=0, column=0)

        # Adding basic types
        self.types_list.extend([object_type, io_type, int_type, string_type, bool_type])
        self.types_dict["Object"] = 0
        self.types_dict["IO"] = 1
        self.types_dict["Int"] = 2
        self.types_dict["String"] = 3
        self.types_dict["Bool"] = 4

    def define_symbol(self, symbol: str, _type: str, line: int, column: int):
        vinfo = Attribute(symbol, _type, line, column)
        self.locals[symbol] = vinfo
        return vinfo

    def create_child_enviroment(self):
        child_enviroment = Enviroment(self)
        return child_enviroment

    def create_type(self, name: str, parent: str):
        '''
        :return type: Type or None if a problem occurs
        :param name: type name
        '''
        if not name in self.types_dict.keys():
            _type = Type(name, parent)
            self.types_dict[name] = len(self.types_list)
            self.types_list.append(_type)
            return _type
        else:
            return None

    def get_type(self, type_name):
        '''
        :return type: Type or None if not exists
        '''
        index = self.types_dict.get(type_name) 
        if index is not None:
            return self.types_list[index]
        return None

    def is_defined(self, symbol):
        '''
        :return type: bool
        '''
        return self.get_symbol_type(symbol) is not None

    def get_symbol_type(self, symbol):
        '''
        :param name: symbol
        :return type: Type or None if don't exists
        '''
        current = self
        while current is not None:
            _type = current.get_local_symbol_type(symbol)
            if _type is not None:
                return _type
            current = current.parent
        return None

    def is_local(self, symbol):
        '''
        :return type: bool
        '''
        return self.get_local_symbol_type(symbol) is not None

    def get_local_symbol_type(self, symbol):
        '''
        returns Type symbol for self scope
        or None if not exists
        '''
        attr = self.locals.get(symbol)
        if attr is not None:
            _type = attr._type
            if attr._type[:9] == 'SELF_TYPE':
                _type = attr._type[9:]
                # I change the next line of code
                return Type('SELF_TYPE', _type)
                
            index = self.types_dict.get(_type)
            if index is not None:
                return self.types_list[index]
            # the type is not defined which is a semantic error, this
            # method returns None in the case that the attribute is not
            # previously defined and when the type of the attribute is 
            # missing
        return None

    # semantic methods
    def build_types_graph(self):
        '''
        directed graph
        '''
        graph = [[] for i in range(len(self.types_list))]

        for _type in self.types_list[1:]:
            u = self.types_dict[_type.parent]
            v = self.types_dict[_type.name]
            graph[u].append(v)
        self.inheritance_graph = graph
        self.lca_structure = LCA(graph)

    def __lca(self, typeA, typeB):
        a = self.types_dict[typeA.name] # typeA.name
        b = self.types_dict[typeB.name] # typeB.name
        lca_index = self.lca_structure.query(a,b)
        return self.types_list[lca_index]

    def _lca(self, typeA, typeB):
        if typeA.name == 'SELF_TYPE':
            if typeB.name == 'SELF_TYPE':
                if typeA.parent == typeB.parent:
                    return typeA
                else:
                    # should not occur in Cool
                    pass
            else:
                c_type = self.get_type(typeA.parent)
                return self.__lca(c_type, typeB)
        else:
            if typeB.name == 'SELF_TYPE':
                c_type = self.get_type(typeB.parent)
                return self.__lca(typeA, c_type)
            else:
                return self.__lca(typeA, typeB)
                
    def lca(self, type_list):
        assert len(type_list) > 0, "In enviroment in lca method type_list must contanis at least one type"

        lca_type = type_list[0]        
        for _type in type_list[1:]:
            lca_type = self._lca(lca_type, _type)
        
        return lca_type

    def _conforms(self, first_type, second_type):
        return self._lca(first_type, second_type) == second_type

    def conforms(self, first_type, second_type):
        if first_type.name == 'SELF_TYPE':
            if second_type.name == 'SELF_TYPE':
                return first_type.parent == second_type.parent
            else:
                c_type = self.get_type(first_type.parent)
                return self._conforms(c_type, second_type)
        else:
            if second_type.name == 'SELF_TYPE':
                return False
            else:
                return self._conforms(first_type, second_type)

    def detect_cycles(self):
        #self.build_types_graph()
        self.visited = [False]*len(self.types_list)
        for u in range(len(self.types_list)):
            if not self.visited[u]:
                if self.dfs_cycles(u):
                    errors.throw_error(errors.SemanticError(text="The inheritance graph contains cycles.", line=0, column=0))
                    return 0
        return 1

    def dfs_cycles(self, u):
        self.visited[u] = True
        for v in self.inheritance_graph[u]:
            if self.visited[v]:
                return True
            if self.dfs_cycles(v):
                return True
        return False

    def check_main(self):
        _type = self.get_type("Main")
        if _type is not None: # checking if there is the program has a class Main 
            method = _type.get_method("main") # the method main is not inherited because enviroment is None
            if method is None: # checking if the a class Main has a method named main
                errors.throw_error(errors.SemanticError(text="Main class must have a method main.", line=0, column=0))
                return 0
            if len(method.attribute_list) > 0: # checking if the method main takes no formal parameters
                errors.throw_error(errors.SemanticError(text="Method main must not take formal parameters.", line=0, column=0))
                return 0
            return 1
        else:
            errors.throw_error(errors.SemanticError(text="Program must have a class Main.", line=0, column=0))
            return 0
    
    def check_inheritance_features(self):
        self.visited = [False]*len(self.types_list)
        my_scope = Scope()

        return self.dfs_inheritance_features(0, my_scope)

    def dfs_inheritance_features(self, u, inherited_scope):
        # scope represent the scope inherited for the current type
        self.visited[u] = True
        valid = 1
        # take the current type
        _type = self.types_list[u]
        # check my attributes and methods first
        for attr, attr_obj in _type.attribute_dict.items():
            if inherited_scope.isdefined_attr(attr):
                valid = 0
                errors.throw_error(errors.SemanticError(text=f"In class '{_type.name}' attribute '{attr}' is redefined.", line=attr_obj.line, column=attr_obj.column))
            else:
                inherited_scope.define_attr(attr, _type.attribute_dict[attr]._type, attr_obj.line, attr_obj.column)

        # setting inherited attributes to the type
        for attr, (attr_type, attr_line, attr_column) in inherited_scope.attribute_dict.items():
            _type.define_attribute(attr, attr_type, attr_line, attr_column) # working on error

        for meth in _type.method_dict.values():
            arg_list = [attr._type for attr in meth.attribute_list]
            arg_list.append(meth.return_type)
            if inherited_scope.isdefined_meth(meth.name):
                arg_def_method = inherited_scope.get_method(meth.name)
                if len(arg_def_method) != len(arg_list):
                    valid = 0
                    errors.throw_error(errors.SemanticError(text=f"In class '{_type.name}' method '{meth.name}' is redefined with a different number of arguments.", line=meth.line, column=meth.column))
                else:
                    if arg_def_method[len(arg_def_method)-1] != arg_list[len(arg_list)-1]:
                        valid = 0
                        errors.throw_error(errors.SemanticError(text=f"In class '{_type.name}' method '{meth.name}' is redefined with a different return type.", line=meth.line, column=meth.column))
                    
                    for i in range(len(arg_list)-1):
                        if arg_def_method[i] != arg_list[i]:
                            valid = 0
                            errors.throw_error(errors.SemanticError(text=f"In class '{_type.name}' method '{meth.name}' is redefined with argument at position {i} with different type.", line=meth.line, column=meth.column))
            else:
                inherited_scope.define_meth(meth.name, arg_list)
        
        for v in self.inheritance_graph[u]:
            if not self.visited[v]:
                valid &= self.dfs_inheritance_features(v, Scope(inherited_scope))
        
        return valid
