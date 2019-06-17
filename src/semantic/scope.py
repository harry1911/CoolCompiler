

class Scope:
    def __init__(self, scope=None):
        if scope is not None:
            self.attribute_dict = scope.attribute_dict.copy()
            self.method_dict = {key:lista.copy() for key,lista in scope.method_dict.items()}
        else:
            # self.attribute_list = [] # str list
            self.attribute_dict = {} # { str : (str,int,int) } represents the attr_name and the (attr_type, attr_line, attr_column) 
            self.method_dict = {} # { str : list<str> }

    def isdefined_attr(self, name: str):
        '''
        return True or False
        '''
        return self.attribute_dict.get(name) is not None

    def isdefined_meth(self, name: str):
        '''
        return True or False
        '''
        return self.method_dict.get(name) is not None

    def get_method(self, name: str):
        return self.method_dict.get(name)

    def define_attr(self, name: str, _type: str, line: int, column: int):
        if not self.isdefined_attr(name):
            self.attribute_dict[name] = (_type, line, column)

    def define_meth(self, name: str, args):
        '''
        :param args: represents a list with the type
        names of the arguments of this method, the last
        type name is the return type name.
        '''
        if not self.isdefined_meth(name):
            self.method_dict[name] = args
