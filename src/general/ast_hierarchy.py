# ===============================================================
# =======================AST=HIERARCHY===========================
# ===============================================================
class AstNode:
    def __init__(self, line=0, column=0):
        self.line = line
        self.column = column

    @property
    def classname(self):
        return self.__class__.__name__

    def to_readable(self):
        return self.classname

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return str(self.to_readable())

class ProgramNode(AstNode):
    def __init__(self, class_list):
        super().__init__()
        self.class_list = class_list

    def to_tuple(self):
        return tuple([('class_name', self.classname),
            ('class_list', self.class_list)])

    def to_readable(self):
        return "{}(class_list={})".format(self.classname, self.class_list)

class ClassNode(AstNode):
    def __init__(self, name, parent, attribute_list, method_list, line, column):
        super().__init__(line, column)
        self.name = name
        self.parent = parent
        self.attribute_list = attribute_list
        self.method_list = method_list

    def to_tuple(self):
        return tuple([('class_name', self.classname),
            ('name', self.name),
            ('parent', self.parent),
            ('attribute_list', self.attribute_list),
            ('method_list', self.method_list)])

    def to_readable(self):
        return "{}(name='{}', parent={}, attribute_list={}, method_list={})".format(self.classname, self.name, self.parent,
                                                self.attribute_list, self.method_list)

class FormalParameterNode(AstNode):
    # no estoy seguro si hereda de FeatureNode
    def __init__(self, name: str, type_parameter: str, line, column):
        super().__init__(line, column)
        self.name = name
        self.type_parameter = type_parameter # should be a string

    def to_tuple(self):
        return tuple([('class_name', self.classname),
            ('name', self.name),
            ('type_parameter', self.type_parameter)])

    def to_readable(self):
        return "{}(name='{}', type_parameter={})".format(self.classname, self.name, self.type_parameter)


##### Feature #####
class FeatureNode(AstNode):
    def __init__(self, line, column):
        super().__init__(line, column)

class FeatureAttributeNode(FeatureNode):
    def __init__(self, name, type_attribute, expression, line, column):
        super().__init__(line, column)
        self.name = name
        self.type_attribute = type_attribute
        self.expression = expression

    def to_tuple(self):
        return tuple([('class_name', self.classname),
            ('name', self.name),
            ('type_attribute', self.type_attribute),
            ('expression', self.expression)])

    def to_readable(self):
        return "{}(name='{}', type_attribute={}, expression={})".format(self.classname, self.name, self.type_attribute, 
                                                                      self.expression)

class FeatureMethodNode(FeatureNode):
    def __init__(self, name, formal_parameter_list, return_type_method, expression, line, column):
        super().__init__(line, column)
        self.name = name
        self.formal_parameter_list = formal_parameter_list
        self.return_type_method = return_type_method
        self.expression = expression

    def to_tuple(self):
        return tuple([('class_name', self.classname),
            ('name', self.name),
            ('formal_parameter_list', self.formal_parameter_list),
            ('return_type_method', self.return_type_method),
            ('expression', self.expression)])

    def to_readable(self):
        return "{}(name='{}', formal_parameter_list={}, return_type_method={}, expression={})".format(self.classname, 
                    self.name, self.formal_parameter_list, self.return_type_method, self.expression)


##### Util #####
class UtilNode(AstNode):
    def __init__(self, line, column):
        super().__init__(line, column)

class DeclarationNode(UtilNode):
    def __init__(self, name, _type, expression, line, column):
        super().__init__(line, column)
        self.name = name
        self._type = _type
        self.expression = expression

    def to_tuple(self):
        return tuple([('class_name', self.classname),
            ('name', self.name),
            ('type', self._type),
            ('expression', self.expression)])

    def to_readable(self):
        return "{}(name='{}', type={}, expression={})".format(self.classname, self.name, self._type, self.expression)

class BranchNode(UtilNode):
    def __init__(self, name, type_branch, expression, line, column):
        super().__init__(line, column)
        self.name = name
        self.type_branch = type_branch
        self.expression = expression

    def to_tuple(self):
        return tuple([('class_name', self.classname),
            ('name', self.name),
            ('type_branch', self.type_branch),
            ('expression', self.expression)])

    def to_readable(self):
        return "{}(name='{}', type_branch={}, expression={})".format(self.classname, self.name, self.type_branch,
                                                                     self.expression)


##### Expressions #####
class ExpressionNode(AstNode):
    def __init__(self, line, column):
        super().__init__(line, column)

class DynamicDispatchNode(ExpressionNode):
    def __init__(self, instance, method, arguments, line, column):
        super().__init__(line, column)
        self.instance = instance
        self.method = method
        self.arguments = arguments

    def to_tuple(self):
        return tuple([('class_name', self.classname),
            ('instance', self.instance),
            ('method', self.method),
            ('arguments', self.arguments)])

    def to_readable(self):
        return "{}(instance={}, method={}, arguments={})".format(self.classname, self.instance, self.method,
                                                                 self.arguments)

class StaticDispatchNode(ExpressionNode):
    def __init__(self, instance, type_dispatch, method, arguments, line, column):
        super().__init__(line, column)
        self.instance = instance
        self.type_dispatch = type_dispatch
        self.method = method
        self.arguments = arguments

    def to_tuple(self):
        return tuple([('class_name', self.classname),
            ('instance', self.instance),
            ('type_dispatch', self.type_dispatch),
            ('method', self.method),
            ('arguments', self.arguments)])

    def to_readable(self):
        return "{}(instance={}, type_dispatch={}, method={}, arguments={})".format(self.classname, self.instance, 
                self.type_dispatch, self.method, self.arguments)


##### Object #####
class ObjectNode(ExpressionNode):
    def __init__(self, name, line, column):
        super().__init__(line, column)
        self.name = name

    def to_tuple(self):
        return tuple([('class_name', self.classname),
            ('name', self.name)])

    def to_readable(self):
        return "{}(name='{}')".format(self.classname, self.name)

class SelfNode(ObjectNode):
    def __init__(self, line, column):
        super().__init__("self", line, column)

    def to_tuple(self):
        return tuple([('class_name', self.classname)])

    def to_readable(self):
        return "{}".format(self.classname)


##### Atomic #####
class AtomicExpressionNode(ExpressionNode):
    def __init__(self, line, column):
        super().__init__(line, column)

### Constant ###
class ConstantNode(AtomicExpressionNode):
    def __init__(self, line, column):
        super().__init__(line, column)

class IntegerNode(ConstantNode):
    def __init__(self, int_token, line, column):
        super().__init__(line, column)
        self.int_token = int_token

    def to_tuple(self):
        return tuple([('class_name', self.classname),
            ('int_token', self.int_token)])

    def to_readable(self):
        return "{}(int_token={})".format(self.classname, self.int_token)

class StringNode(ConstantNode):
    def __init__(self, str_token, line, column):
        super().__init__(line, column)
        self.str_token = str_token

    def to_tuple(self):
        return tuple([('class_name', self.classname),
            ('str_token', self.str_token)])

    def to_readable(self):
        return "{}(str_token={})".format(self.classname, self.str_token)

class BooleanNode(ConstantNode):
    def __init__(self, bool_token, line, column):
        super().__init__(line, column)
        self.bool_token = bool_token

    def to_tuple(self):
        return tuple([('class_name', self.classname),
            ('bool_token', self.bool_token)])

    def to_readable(self):
        return "{}(bool_token={})".format(self.classname, self.bool_token)

class TrueNode(BooleanNode):
    def __init__(self, line, column):
        super().__init__('true', line, column)

class FalseNode(BooleanNode):
    def __init__(self, line, column):
        super().__init__('false', line, column)

### End_Constant ###
class AssignNode(AtomicExpressionNode):
    def __init__(self, instance, expression, line, column):
        super().__init__(line, column)
        self.instance = instance
        self.expression = expression

    def to_tuple(self):
        return tuple([('class_name', self.classname),
            ('instance', self.instance),
            ('expression', self.expression)])

    def to_readable(self):
        return "{}(instance={}, expression={})".format(self.classname, self.instance, self.expression)

class BlockNode(AtomicExpressionNode):
    def __init__(self, expression_list, line, column):
        super().__init__(line, column)
        self.expression_list = expression_list
    
    def to_tuple(self):
        return tuple([('class_name', self.classname),
            ('expression_list', self.expression_list)])

    def to_readable(self):
        return "{}(expression_list={})".format(self.classname, self.expression_list)

class LetInNode(AtomicExpressionNode):
    def __init__(self, declaration_list, expression, line, column):
        super().__init__(line, column)
        self.declaration_list = declaration_list # list<DeclarationNode>
        self.expression = expression

    def to_tuple(self):
        return tuple([('class_name', self.classname),
            ('declaration_list', self.declaration_list),
            ('expression', self.expression)])

    def to_readable(self):
        return "{}(declaration_list={}, expression={})".format(self.classname, self.declaration_list, 
                                                               self.expression)

class IfNode(AtomicExpressionNode):
    def __init__(self, if_expression, then_expression, else_expression, line, column):
        super().__init__(line, column)
        self.if_expression = if_expression
        self.then_expression = then_expression
        self.else_expression = else_expression

    def to_tuple(self):
        return tuple([('class_name', self.classname),
            ('if_expression', self.if_expression),
            ('then_expression', self.then_expression),
            ('else_expression', self.else_expression)])

    def to_readable(self):
        return "{}(if_expression={}, then_expression={}, else_expression={})".format(self.classname,
                    self.if_expression, self.then_expression, self.else_expression)

class WhileLoopNode(AtomicExpressionNode):
    def __init__(self, while_expression, loop_expression, line, column):
        super().__init__(line, column)
        self.while_expression = while_expression
        self.loop_expression = loop_expression

    def to_tuple(self):
        return tuple([('class_name', self.classname),
            ('while_expression', self.while_expression),
            ('loop_expression', self.loop_expression)])

    def to_readable(self):
        return "{}(while_expression={}, loop_expression={})".format(self.classname, self.while_expression, 
                                                                    self.loop_expression)

class CaseNode(AtomicExpressionNode):
    def __init__(self, case_expression, branch_list, line, column):
        super().__init__(line, column)
        self.case_expression = case_expression
        self.branch_list = branch_list

    def to_tuple(self):
        return tuple([('class_name', self.classname),
            ('case_expression', self.case_expression),
            ('branch_list', self.branch_list)])

    def to_readable(self):
        return "{}(case_expression={}, branch_list={})".format(self.classname, self.case_expression, self.branch_list)

class NewObjectNode(AtomicExpressionNode):
    def __init__(self, new_type, line, column):
        super().__init__(line, column)
        self.new_type = new_type

    def to_tuple(self):
        return tuple([('class_name', self.classname),
            ('new_type', self.new_type)])

    def to_readable(self):
        return "{}(new_type={})".format(self.classname, self.new_type)


##### Binary Operators #####
class BinaryOperatorNode(ExpressionNode):
    def __init__(self, left_expression, symbol, right_expression, line, column):
        super().__init__(line, column)
        self.left_expression = left_expression
        self.symbol = symbol
        self.right_expression = right_expression

    def to_tuple(self):
        return tuple([('class_name', self.classname),
            ('left_expression', self.left_expression),
            ('right_expression', self.right_expression)])

    def to_readable(self):
        return "{}(left_expression={}, right_expression={})".format(self.classname, self.left_expression, 
                                                                    self.right_expression)

class PlusNode(BinaryOperatorNode):
    def __init__(self, left_expression, right_expression, line, column):
        super().__init__(left_expression, '+', right_expression, line, column)

class MinusNode(BinaryOperatorNode):
    def __init__(self, left_expression, right_expression, line, column):
        super().__init__(left_expression, '-', right_expression, line, column)

class StarNode(BinaryOperatorNode):
    def __init__(self, left_expression, right_expression, line, column):
        super().__init__(left_expression, '*', right_expression, line, column)  

class DivNode(BinaryOperatorNode):
    def __init__(self, left_expression, right_expression, line, column):
        super().__init__(left_expression, '/', right_expression, line, column)

### Comparison Operators ###
class ComparisonNode(BinaryOperatorNode):
    def __init__(self, left_expression, symbol, right_expression, line, column):
        super().__init__(left_expression, symbol, right_expression, line, column)      

class EqualNode(ComparisonNode):
    def __init__(self, left_expression, right_expression, line, column):
        super().__init__(left_expression, '=', right_expression, line, column)

class LessThanNode(ComparisonNode):
    def __init__(self, left_expression, right_expression, line, column):
        super().__init__(left_expression, '<', right_expression, line, column)  

class LessThanOrEqualNode(ComparisonNode):
    def __init__(self, left_expression, right_expression, line, column):
        super().__init__(left_expression, '<=', right_expression, line, column)

##### Unary Operators #####
class UnaryOperatorNode(ExpressionNode):
    def __init__(self, expression, symbol, line, column):
        super().__init__(line, column)
        self.expression = expression
        self.symbol = symbol

    def to_tuple(self):
        return tuple([('class_name', self.classname),
            ('expression', self.expression)])

    def to_readable(self):
        return "{}(expression={})".format(self.classname, self.expression)

class ComplementNode(UnaryOperatorNode):
    '~'
    def __init__(self, expression, line, column):
        super().__init__(expression, '~', line, column)

class NegationNode(UnaryOperatorNode):
    'NOT'
    def __init__(self, expression, line, column):
        super().__init__(expression, 'NOT', line, column)

class IsVoidNode(UnaryOperatorNode):
    def __init__(self, expression, line, column):
        super().__init__(expression, 'ISVOID', line, column)

