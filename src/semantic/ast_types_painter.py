
from general import visitor
from general import ast_hierarchy as ast


class Painter:
    def string_type(self, _type):
        if _type.name == 'SELF_TYPE':
            return _type.name + ':' + _type.parent
        else:
            return _type.name

    @visitor.on('node')
    def visit(self, node, tabs):
        pass

    @visitor.when(ast.ProgramNode)
    def visit(self, node, tabs):
        _str = 'Program' + '\n'
        for _class in node.class_list:
            _str += '\n' + self.visit(_class, tabs+1)
        return _str

    @visitor.when(ast.ClassNode)
    def visit(self, node, tabs):
        _str = '\t' * tabs + '\__' + '<class> ' + node.name + ' <parent> ' + node.parent + '\n'       
        for _attr in node.attribute_list:
            _str += '\n' + self.visit(_attr, tabs+1)

        for _meth in node.method_list:
            _str += '\n' + self.visit(_meth, tabs+1)        
        return _str

    @visitor.when(ast.FeatureAttributeNode)
    def visit(self, node, tabs):
        if node.expression is None:
            _str = '\t' * tabs + '\__' + '<id> : <type>'
            _str += '\n' + '\t' * (tabs+1) + '\__' + 'computed_type: ' + self.string_type(node.computed_type)
            _str += '\n' + '\t' * (tabs+1) + '\__' + 'id: ' + node.name
            _str += '\n' + '\t' * (tabs+1) + '\__' + 'type: ' + node.type_attribute
        else:
            _str = '\t' * tabs + '\__' + '<id> : <type> <- <expr>'
            _str += '\n' + '\t' * (tabs+1) + '\__' + 'computed_type: ' + self.string_type(node.computed_type)
            _str += '\n' + '\t' * (tabs+1) + '\__' + 'id: ' + node.name
            _str += '\n' + '\t' * (tabs+1) + '\__' + 'type: ' + node.type_attribute
            _str += '\n' + self.visit(node.expression, tabs+1)
        return _str

    @visitor.when(ast.FeatureMethodNode)
    def visit(self, node, tabs):
        _str = '\t' * tabs + '\__' + '<id>(<formal_params_list>) : <type> { <expr> }'
        _str += '\n' + '\t' * (tabs+1) + '\__' + 'computed_type: ' + self.string_type(node.computed_type)
        _str += '\n' + '\t' * (tabs+1) + '\__' + 'id: ' + node.name
        _str += '\n' + '\t' * (tabs+1) + '\__' + '<formal_params_list>: '
        for formal_param in node.formal_parameter_list:
            _str += '\n' + self.visit(formal_param, tabs+2)
        _str += '\n' + '\t' * (tabs+1) + '\__' + 'type: ' + node.return_type_method        
        _str += '\n' + self.visit(node.expression, tabs+1)
        return _str

    @visitor.when(ast.FormalParameterNode)
    def visit(self, node, tabs):
        _str = '\t' * tabs + '\__' + '<id> : <type>'
        _str += '\n' + '\t' * (tabs+1) + '\__' + 'id: ' + node.name
        _str += '\n' + '\t' * (tabs+1) + '\__' + 'type: ' + node.type_parameter
        return _str
    
    @visitor.when(ast.IntegerNode)
    def visit(self, node, tabs):
        return '\t' * tabs + '\__' + 'num: ' + str(node.int_token)
    
    @visitor.when(ast.StringNode)
    def visit(self, node, tabs):
        return '\t' * tabs + '\__' + 'str: ' + node.str_token

    @visitor.when(ast.BooleanNode)
    def visit(self, node, tabs):
        return '\t' * tabs + '\__' + 'bool: ' + node.bool_token

    @visitor.when(ast.BinaryOperatorNode)
    def visit(self, node, tabs):
        _str = '\t' * tabs + '\__' + '<expr> ' + node.symbol + ' <expr>'
        _str += '\n' + '\t' * (tabs+1) + '\__' + 'computed_type: ' + self.string_type(node.computed_type)
        _str += '\n' + self.visit(node.left_expression, tabs+1)
        _str += '\n' + self.visit(node.right_expression, tabs+1)
        return _str

    @visitor.when(ast.UnaryOperatorNode)
    def visit(self, node, tabs):
        _str = '\t' * tabs + '\__' + node.symbol + ' <expr>'
        _str += '\n' + '\t' * (tabs+1) + '\__' + 'computed_type: ' + self.string_type(node.computed_type)        
        _str += '\n' + self.visit(node.expression, tabs+1)
        return _str

    @visitor.when(ast.AssignNode)
    def visit(self, node, tabs):
        _str = '\t' * tabs + '\__' + '<var> <- <expr>'
        _str += '\n' + '\t' * (tabs+1) + '\__' + 'computed_type: ' + self.string_type(node.computed_type)
        _str += '\n' + self.visit(node.instance, tabs+1)
        _str += '\n' + self.visit(node.expression, tabs+1)
        return _str

    @visitor.when(ast.BlockNode)
    def visit(self, node, tabs):
        _str = '\t' * tabs + '\__' + '{ <expression_list> }'
        _str += '\n' + '\t' * (tabs+1) + '\__' + 'computed_type: ' + self.string_type(node.computed_type)
        for expr in node.expression_list:
            _str += '\n' + self.visit(expr, tabs+1)
        return _str

    @visitor.when(ast.IfNode)
    def visit(self, node, tabs):
        _str = '\t' * tabs + '\__' + 'if <if_expression> then <then_expression> else <else_expression> fi'
        _str += '\n' + '\t' * (tabs+1) + '\__' + 'computed_type: ' + self.string_type(node.computed_type)        
        _str += '\n' + '\t' * (tabs+1) + '\__' + '<if_expression>\n' + self.visit(node.if_expression, tabs+2)
        _str += '\n' + '\t' * (tabs+1) + '\__' + '<then_expression>\n' + self.visit(node.then_expression, tabs+2)
        _str += '\n' + '\t' * (tabs+1) + '\__' + '<else_expression>\n' + self.visit(node.else_expression, tabs+2)
        return _str
    
    @visitor.when(ast.WhileLoopNode)
    def visit(self, node, tabs):
        _str = '\t' * tabs + '\__' + 'while <while_expression> loop <loop_expression> pool'
        _str += '\n' + '\t' * (tabs+1) + '\__' + 'computed_type: ' + self.string_type(node.computed_type)
        _str += '\n' + '\t' * (tabs+1) + '\__' + '<while_expression>\n' + self.visit(node.while_expression, tabs+2)
        _str += '\n' + '\t' * (tabs+1) + '\__' + '<loop_expression>\n' + self.visit(node.loop_expression, tabs+2)
        return _str

    @visitor.when(ast.NewObjectNode)
    def visit(self, node, tabs):
        _str = '\t' * tabs + '\__' + 'new <type>'
        _str += '\n' + '\t' * (tabs+1) + '\__' + 'computed_type: ' + self.string_type(node.computed_type)
        return _str

    @visitor.when(ast.ObjectNode)
    def visit(self, node, tabs):
        _str = '\t' * tabs + '\__' + 'var: ' + node.name
        _str += '\n' + '\t' * (tabs+1) + '\__' + 'computed_type: ' + self.string_type(node.computed_type)
        return _str
        
    @visitor.when(ast.LetInNode)
    def visit(self, node, tabs):
        _str = '\t' * tabs + '\__' + 'let <declaration_list> in <expr>'
        _str += '\n' + '\t' * (tabs+1) + '\__' + 'computed_type: ' + self.string_type(node.computed_type)
        _str += '\n' + '\t' * (tabs+1) + '\__' + '<declaration_list>: '
        for _decl in node.declaration_list:
            _str += '\n' + self.visit(_decl, tabs+2)
        _str += '\n' + self.visit(node.expression, tabs+1)
        return _str

    @visitor.when(ast.CaseNode)
    def visit(self, node, tabs):
        _str = '\t' * tabs + '\__' + 'case <expr> of <branch_list> esac'
        _str += '\n' + '\t' * (tabs+1) + '\__' + 'computed_type: ' + self.string_type(node.computed_type)
        _str += '\n' + self.visit(node.case_expression, tabs+1)
        _str += '\n' + '\t' * (tabs+1) + '<branch_list>: '
        for _branch in node.branch_list:
            _str += '\n' + self.visit(_branch, tabs+2)
        return _str

    @visitor.when(ast.DeclarationNode)
    def visit(self, node, tabs):
        if node.expression is None:
            _str = '\t' * tabs + '\__' + '<id> : <type>'
            _str += '\n' + '\t' * (tabs+1) + '\__' + 'id: ' + node.name
            _str += '\n' + '\t' * (tabs+1) + '\__' + 'type: ' + node._type
        else:
            _str = '\t' * tabs + '\__' + '<id> : <type> <- <expr>'
            _str += '\n' + '\t' * (tabs+1) + '\__' + 'id: ' + node.name
            _str += '\n' + '\t' * (tabs+1) + '\__' + 'type: ' + node._type
            _str += '\n' + self.visit(node.expression, tabs+1)
        return _str
    
    @visitor.when(ast.BranchNode)
    def visit(self, node, tabs):
        _str = '\t' * tabs + '\__' + '<id> : <type> => <expr>'
        _str += '\n' + '\t' * (tabs+1) + '\__' + 'id: ' + node.name
        _str += '\n' + '\t' * (tabs+1) + '\__' + 'type: ' + node.type_branch
        _str += '\n' + self.visit(node.expression, tabs+1)
        return _str

    @visitor.when(ast.DynamicDispatchNode)
    def visit(self, node, tabs):
        _str = '\t' * tabs + '\__' + '<expr>.<id>( <expression_list> )'
        _str += '\n' + '\t' * (tabs+1) + '\__' + 'computed_type: ' + self.string_type(node.computed_type)
        _str += '\n' + self.visit(node.instance, tabs+1)
        _str += '\n' + '\t' * (tabs+1) + '\__' + 'id: ' + node.method
        _str += '\n' + '\t' * (tabs+1) + '<expression_list>: '
        for expr in node.arguments:
            _str += '\n' + self.visit(expr, tabs+2)
        return _str
        
    @visitor.when(ast.StaticDispatchNode)
    def visit(self, node, tabs):
        _str = '\t' * tabs + '\__' + '<expr>@<type>.<id>( <expression_list> )'
        _str += '\n' + '\t' * (tabs+1) + '\__' + 'computed_type: ' + self.string_type(node.computed_type)
        _str += '\n' + self.visit(node.instance, tabs+1)
        _str += '\n' + '\t' * (tabs+1) + '\__' + 'type: ' + node.type_dispatch
        _str += '\n' + '\t' * (tabs+1) + '\__' + 'id: ' + node.method
        _str += '\n' + '\t' * (tabs+1) + '<expression_list>: '
        for expr in node.arguments:
            _str += '\n' + self.visit(expr, tabs+2)
        return _str