import itertools as itt
from collections import OrderedDict
from general.cil_hierarchy import CILLocalvar


class Defaults:
    def __init__(self, class_name, feature_attributes):
        self.class_name = class_name
        self.defaults = feature_attributes # list(ast_hierarchy.FeatureAttributeNode)

class ObjecContext:
    def __init__(self, types):
        self.types = {_type.name:_type for _type in types} #  { str(name) : Type() }

    def get_type(self, type_name):
        return self.types.get(type_name)

class VariableInfo:
    def __init__(self, name, vtype, cil_name):
        self.name = name
        self.type = vtype
        self.cil_name = cil_name # it is an object CILLocalvar

class Scope:
    def __init__(self, parent=None):
        self.locals = []
        self.parent = parent
        self.children = []
        self.local_vars = {} if parent is None else parent.local_vars # { str(name) : CILLocalvar }
        self.self = None if parent is None else parent.self # it is an object CILLocalvar: represent the location in memory of the self object
        self.index = 0 if parent is None else len(parent)

    def __len__(self):
        return len(self.locals)

    def create_child(self):
        child = Scope(self)
        self.children.append(child)
        return child

    def define_variable(self, vname, vtype, cilname):
        info = VariableInfo(vname, vtype, cilname)
        self.locals.append(info)
        return info

    def define_local(self, value=0):
        local_var = CILLocalvar('local' + str(len(self.local_vars)+1), value)
        self.local_vars[local_var.name] = local_var
        return local_var

    def find_local(self, local_name):
        self.local_vars.get(local_name)

    def find_variable(self, vname, index=None):
        locals = self.locals if index is None else itt.islice(self.locals, index)
        try:
            return next(x for x in locals if x.name == vname)
        except StopIteration:
            return self.parent.find_variable(vname, self.index) if self.parent else None

    def is_defined(self, vname):
        return self.find_variable(vname) is not None

    def is_local(self, vname):
        return any(True for x in self.locals if x.name == vname)



