
from general import visitor, errors
from general import ast_hierarchy as ast
from .type import Type


class TypeBuilderVisitor:
    def __init__(self, enviroment):
        self.enviroment = enviroment
        self.current_type = None # type(current_type) = Type

    @visitor.on('node')
    def visit(self, node):
        pass

    @visitor.when(ast.ProgramNode)
    def visit(self, node):
        for _class in node.class_list:
            self.visit(_class)

    @visitor.when(ast.ClassNode)
    def visit(self, node):
        self.current_type = self.enviroment.get_type(node.name)

        parent_type = self.enviroment.get_type(node.parent)
        if parent_type is None and node.name != "Object":
            errors.throw_error(errors.TypeError(text=f"In class '{self.current_type.name}' parent type '{node.parent}' is missing.", line=node.line, column=node.column))
        if parent_type.name in ['Int', 'String', 'Bool']:
            errors.throw_error(errors.SemanticError(text=f"In class '{self.current_type.name}' it is an error to inherit from basic class '{node.parent}'.", line=node.line, column=node.column))

        for attribute in node.attribute_list:
            self.visit(attribute)

        for method in node.method_list:
            self.visit(method)


    @visitor.when(ast.FeatureAttributeNode)
    def visit(self, node):
        # node.type_attribute can be SELF_TYPE
        if node.type_attribute == 'SELF_TYPE':
            attribute_type = Type('SELF_TYPE', self.current_type.name)
        else:
            attribute_type = self.enviroment.get_type(node.type_attribute)
        if attribute_type is not None:
            if node.name == "self":
                errors.throw_error(errors.SemanticError(text=f"Name attribute can not be self.", line=node.line, column=node.column))
            else:
                ans = self.current_type.define_attribute(node.name, node.type_attribute, node.line, node.column)
                if not ans:
                    errors.throw_error(errors.SemanticError(text=f"In class '{self.current_type.name}' attribute '{node.name}' is defined multiple times.", line=node.line, column=node.column))
        else:
            errors.throw_error(errors.TypeError(text=f"The type '{node.type_attribute}' of attribute '{node.name}' is missing.", line=node.line, column=node.column))


    @visitor.when(ast.FeatureMethodNode)
    def visit(self, node):
        # node.return_type_method can be SELF_TYPE
        if node.return_type_method == 'SELF_TYPE':
            return_type = Type('SELF_TYPE', self.current_type.name)
        else:
            return_type = self.enviroment.get_type(node.return_type_method)
        if return_type is not None:
            # formal_parameter_list
            argument_list = []
            for parameter in node.formal_parameter_list:
                if parameter.name == 'self':
                    errors.throw_error(errors.SemanticError(text=f"In method '{node.name}' it is an error to bind self as a formal parameter.", line=node.line, column=node.column))
                if parameter.name in argument_list:
                    errors.throw_error(errors.SemanticError(text=f"In method '{node.name}' the argument '{parameter.name}' is defined multiple times.", line=node.line, column=node.column))
                argument_list.append(parameter.name)

            argument_types = []
            for parameter in node.formal_parameter_list:
                if parameter.type_parameter == 'SELF_TYPE':
                    errors.throw_error(errors.TypeError(text=f"In method '{node.name}' the type of argument '{parameter.name}' cannot be SELF_TYPE.", line=node.line, column=node.column))
                _type = self.enviroment.get_type(parameter.type_parameter)
                if _type is not None:
                    argument_types.append(parameter.type_parameter)
                else:
                    errors.throw_error(errors.TypeError(text=f"The type of the parameter '{parameter.name}' in method '{node.name}' is missing.", line=node.line, column=node.column))
                    
            ans = self.current_type.define_method(node.name, node.return_type_method, argument_list, argument_types, node.line, node.column)
            if not ans:
                errors.throw_error(errors.SemanticError(text=f"In class '{self.current_type.name}' method '{node.name}' is defined multiple times.", line=node.line, column=node.column))             
        else:
            errors.throw_error(errors.TypeError(text=f"In class '{self.current_type.name}' return type of method '{node.name}' is missing.", line=node.line, column=node.column))

