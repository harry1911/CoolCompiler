

class Type:
    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent # str representing the name of the parent class
        self.attribute_dict = {}
        self.method_dict = {}

    def get_attribute(self, name: str, enviroment=None):
        '''
        return type: Attribute class or None if don't exists
        '''
        attr = self.attribute_dict.get(name)
        if attr is not None or enviroment is None:
            return attr
        parent_type = enviroment.get_type(self.parent)
        if parent_type is not None:
            return parent_type.get_attribute(name, enviroment)
        return None

    def get_method(self, name: str, enviroment=None):
        '''
        return type: Method class or None if don't exists
        '''
        method = self.method_dict.get(name)
        if method is not None or enviroment is None:
            return method
        parent_type = enviroment.get_type(self.parent)
        if parent_type is not None:
            return parent_type.get_method(name, enviroment)
        return None

    def get_attribute_type(self, name: str, enviroment):
        attr = self.get_attribute(name, enviroment)
        if attr is None:
            return None
        if attr._type == 'SELF_TYPE':
            return Type(attr._type, self.name)
        else:
            _type = enviroment.get_type(attr._type)
            # _type is guaranted be not None in the type_builder
            return _type

    def define_attribute(self, name: str, _type: str, line: int, column: int):
        '''
        :return type: bool
        '''
        if not name in self.attribute_dict.keys():
            self.attribute_dict[name] = Attribute(name, _type, line, column)
            return True
        else:
            return False

    def define_method(self, name: str, return_type: str, argument_list, argument_types, line: int, column: int):
        '''
        :param return_type: Type
        :return type: bool
        '''
        if not name in self.method_dict.keys() and len(argument_list) == len(argument_types):
            attribute_list = [Attribute(argument_list[i], argument_types[i], line, column) for i in range(len(argument_list))]
            self.method_dict[name] = Method(name, return_type, attribute_list, line, column)
            return True
        else:
            return False

class Attribute:
    def __init__(self, name: str, _type: str, line: int, column: int):
        self.name = name
        self._type = _type
        self.line = line
        self.column = column

class Method:
    def __init__(self, name: str, return_type: str, attribute_list, line: int, column: int):
        '''
        :param attribute_list: list of Attributes
        '''
        self.name = name
        self.return_type = return_type
        self.attribute_list = attribute_list
        self.line = line
        self.column = column
