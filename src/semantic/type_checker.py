
from general import visitor, errors
from general import ast_hierarchy as ast
from .type import Type

# SELF_TYPE: is represented by a normal type with name SELF_TYPE and the parent is the class

class TypeCheckerVisitor:
    def __init__(self):
        self.current_type = None # type(current_type) = Type

    @visitor.on('node')
    def visit(self, node, enviroment):
        pass

    # [Program]
    @visitor.when(ast.ProgramNode)
    def visit(self, node, enviroment):
        '''
        In this method is where we start the visitor over
        the ast, checking all classes and last the main class
        and it's main method.
        '''
        # build the types_graph
        enviroment.build_types_graph()
        # check if Program has a clas Main with a local method main
        enviroment.check_main()
        # check if are not cycles in the inheritance graph
        enviroment.detect_cycles()
        # check inheritance features and build LCA preprocessing
        enviroment.check_inheritance_features()

        # check if classes are ok
        for _class in node.class_list:
            child_enviroment = enviroment.create_child_enviroment()
            self.visit(_class, child_enviroment)

    # [Class]
    @visitor.when(ast.ClassNode)
    def visit(self, node, enviroment):
        self.current_type = enviroment.get_type(node.name)

        # adding to the current enviroment all the class attributes
        for _, attr in self.current_type.attribute_dict.items():
            if attr._type == 'SELF_TYPE':
                enviroment.define_symbol(attr.name, 'SELF_TYPE'+node.name, attr.line, attr.column)
            else:
                enviroment.define_symbol(attr.name, attr._type, attr.line, attr.column)

        for _attr in node.attribute_list:
            self.visit(_attr, enviroment)

        for _meth in node.method_list:
            self.visit(_meth, enviroment)

    # [Self]
    # [Var - Identifier]
    @visitor.when(ast.ObjectNode)
    def visit(self, node, enviroment):
        node_type = enviroment.get_symbol_type(node.name)
        if node_type is None:
            errors.throw_error(errors.NameError(text=f"Variable '{node.name}' is not defined.", line=node.line, column=node.column))
        node.computed_type = node_type
    
    # [ASSIGN]
    @visitor.when(ast.AssignNode)
    def visit(self, node, enviroment):
        if node.instance.name == 'self':
            errors.throw_error(errors.SemanticError(text=f"It is an error to assign to self.", line=node.line, column=node.column))

        self.visit(node.instance, enviroment)
        self.visit(node.expression, enviroment)
         
        if not enviroment.conforms(node.expression.computed_type, node.instance.computed_type):
            errors.throw_error(errors.TypeError(text=f"In assign expression type does not conforms with variable '{node.instance.name}' declared type.", line=node.line, column=node.column))

        node.computed_type = node.expression.computed_type
        
    # [True]
    @visitor.when(ast.TrueNode)
    def visit(self, node, enviroment):
        node.computed_type = enviroment.get_type("Bool")

    # [False]
    @visitor.when(ast.FalseNode)
    def visit(self, node, enviroment):
        node.computed_type = enviroment.get_type("Bool")

    # [Int]
    @visitor.when(ast.IntegerNode)
    def visit(self, node, enviroment):
        node.computed_type = enviroment.get_type("Int")

    # [String]
    @visitor.when(ast.StringNode)
    def visit(self, node, enviroment):
        node.computed_type = enviroment.get_type("String")

    # [New]
    @visitor.when(ast.NewObjectNode)
    def visit(self, node, enviroment):
        if node.new_type == 'SELF_TYPE':
            node.computed_type = Type('SELF_TYPE', self.current_type.name)
        else:
            _type = enviroment.get_type(node.new_type)
            if _type is None:
                errors.throw_error(errors.TypeError(text=f"In new expression type '{node.new_type}' does not exists.", line=node.line, column=node.column))
            node.computed_type = _type

    # [DynamicDispatch]
    @visitor.when(ast.DynamicDispatchNode)
    def visit(self, node, enviroment):
        self.visit(node.instance, enviroment)

        for _expr in node.arguments:
            self.visit(_expr, enviroment)

        instance_type = node.instance.computed_type if node.instance.computed_type.name != 'SELF_TYPE' else enviroment.get_type(node.instance.computed_type.parent)
        meth = instance_type.get_method(node.method, enviroment) # enviroment is used to search for inherited methods
        
        if meth is None:
            errors.throw_error(errors.AttributeError(text=f"Class '{instance_type.name}' does not contain a method named '{node.method}'.", line=node.line, column=node.column))

        # check if the number of arguments is correct
        if len(node.arguments) != len(meth.attribute_list):
            errors.throw_error(errors.SemanticError(text=f"Dynamic dispatch does not match with the signature of method '{node.method}'.", line=node.line, column=node.column))

        # check if each arg type conforms with the formal parameter type in the method signautre
        for i in range(len(node.arguments)):
            if not enviroment.conforms(node.arguments[i].computed_type, enviroment.get_type(meth.attribute_list[i]._type)):
                errors.throw_error(errors.TypeError(text=f"In dynamic dispatch of method '{node.method}' the type of the argument at index {i} does not conforms with the type of the formal parameter in the method signature.", line=node.line, column=node.column))

        # The return type of a method always exits, its garanty in the type_builder
        if meth.return_type == 'SELF_TYPE':
            node.computed_type = node.instance.computed_type
        else:
            node.computed_type = enviroment.get_type(meth.return_type)

    # [StaticDispatch]
    @visitor.when(ast.StaticDispatchNode)
    def visit(self, node, enviroment):
        self.visit(node.instance, enviroment)

        for _expr in node.arguments:
            self.visit(_expr, enviroment)

        if node.type_dispatch == 'SELF_TYPE':
            errors.throw_error(errors.SemanticError(text=f"Static dispatch specified type cannot be 'SELF_TYPE'.", line=node.line, column=node.column))

        type_dispatch = enviroment.get_type(node.type_dispatch)
        if type_dispatch is None:
            errors.throw_error(errors.TypeError(text=f"Type '{node.type_dispatch}' specified in static dispatch of method '{node.method}' is not defined.", line=node.line, column=node.column))

        if not enviroment.conforms(node.instance.computed_type, type_dispatch):
            errors.throw_error(errors.TypeError(text=f"In static dispatch the instance static type does not conforms with the specified type.", line=node.line, column=node.column))

        meth = type_dispatch.get_method(node.method, enviroment) # enviroment is used to search for inherited methods
        
        if meth is None:
            errors.throw_error(errors.AttributeError(text=f"Class '{type_dispatch.name}' does not contain a method named '{node.method}'.", line=node.line, column=node.column))

        # check if the number of arguments is correct
        if len(node.arguments) != len(meth.attribute_list):
            errors.throw_error(errors.SemanticError(text=f"Static dispatch does not match with the signature of method '{node.method}'.", line=node.line, column=node.column))


        # check if each arg type conforms with the formal parameter type in the method signautre
        for i in range(len(node.arguments)):
            if not enviroment.conforms(node.arguments[i].computed_type, enviroment.get_type(meth.attribute_list[i]._type)):
                errors.throw_error(errors.TypeError(text=f"In static dispatch of method '{node.method}' the type of the argument at index {i} does not conforms with the type of the formal parameter in the method signature.", line=node.line, column=node.column))

        # The return type of a method always exits, its garanty in the type_builder
        if meth.return_type == 'SELF_TYPE':
            node.computed_type = node.instance.computed_type
        else:
            node.computed_type = enviroment.get_type(meth.return_type)
        
    # [If]
    @visitor.when(ast.IfNode)
    def visit(self, node, enviroment):
        self.visit(node.if_expression, enviroment)
        self.visit(node.then_expression, enviroment)
        self.visit(node.else_expression, enviroment)

        if node.if_expression.computed_type.name != "Bool":
            errors.throw_error(errors.TypeError(text=f"If expression type must be 'Bool'.", line=node.line, column=node.column))

        node.computed_type = enviroment.lca([node.then_expression.computed_type, node.else_expression.computed_type])

    # [Sequence]
    @visitor.when(ast.BlockNode)
    def visit(self, node, enviroment):
        for _expr in node.expression_list:
            self.visit(_expr, enviroment)

        node.computed_type = node.expression_list[-1].computed_type
    
    # [Let-Init]
    # [Let-No-Init]
    @visitor.when(ast.LetInNode)
    def visit(self, node, enviroment):
        current_enviroment = enviroment 
        for _decl in node.declaration_list:
            if _decl.name == 'self':
                errors.throw_error(errors.SemanticError(text=f"It is an error to bind self in a let expression.", line=_decl.line, column=_decl.column))                
            if _decl._type == 'SELF_TYPE':
                _type = Type('SELF_TYPE', self.current_type.name)
            else:
                _type = current_enviroment.get_type(_decl._type)
                if _type is None:
                    errors.throw_error(errors.TypeError(text=f"Type '{_decl._type}' declared for variable '{_decl.name}' is not defined.", line=_decl.line, column=_decl.column))
            
            # check if _decl has an init expression
            if _decl.expression is not None:
                self.visit(_decl.expression, current_enviroment)

                if not enviroment.conforms(_decl.expression.computed_type, _type):
                    errors.throw_error(errors.TypeError(text=f"Type of initialization expression for variable '{_decl.name}' does not conform with its declared type '{_decl._type}'.", line=_decl.line, column=_decl.column))

            new_child_enviroment = current_enviroment.create_child_enviroment()
            if _type.name == 'SELF_TYPE':
                new_child_enviroment.define_symbol(_decl.name, 'SELF_TYPE'+_type.parent, _decl.line, _decl.column)
            else:
                new_child_enviroment.define_symbol(_decl.name, _type.name, _decl.line, _decl.column)
            
            current_enviroment = new_child_enviroment

        self.visit(node.expression, current_enviroment)
        node.computed_type = node.expression.computed_type

    # [Case]
    @visitor.when(ast.CaseNode)
    def visit(self, node, enviroment):
        self.visit(node.case_expression, enviroment)

        variable_types = []
        for _branch in node.branch_list:
            if _branch.name == 'self':
                errors.throw_error(errors.SemanticError(text=f"It is an error to bind self in a case expression.", line=_branch.line, column=_branch.column))
            if _branch.type_branch == 'SELF_TYPE':
                errors.throw_error(errors.SemanticError(text=f"Branch declared type cannot be 'SELF_TYPE'.", line=_branch.line, column=_branch.column))
            _type = enviroment.get_type(_branch.type_branch)
            if _type is None:
                errors.throw_error(errors.TypeError(text=f"Type '{_branch.type_branch}' declared for variable '{_branch.name}' is not defined.", line=_branch.line, column=_branch.column))
            if _type in variable_types:
                errors.throw_error(errors.SemanticError(text=f"In case expression all types declared type must be different.", line=node.line, column=node.column))
            variable_types.append(_type)

        static_types = []
        for _branch in node.branch_list:
            child_enviroment = enviroment.create_child_enviroment()
            child_enviroment.define_symbol(_branch.name, _branch.type_branch, _branch.line, _branch.column)
            self.visit(_branch.expression, child_enviroment)
            _branch.computed_type = _branch.expression.computed_type # in a BranchNode computed_type means the computed type of its expression
            static_types.append(_branch.computed_type)

        node.computed_type = enviroment.lca(static_types)

    # [Loop]
    @visitor.when(ast.WhileLoopNode)
    def visit(self, node, enviroment):
        self.visit(node.while_expression, enviroment)
        self.visit(node.loop_expression, enviroment)

        if node.while_expression.computed_type.name != "Bool":
            errors.throw_error(errors.TypeError(text=f"The predicate of a loop must have type 'Bool'.", line=node.line, column=node.column))

        node.computed_type = enviroment.get_type("Object")

    # [Isvoid]
    @visitor.when(ast.IsVoidNode)
    def visit(self, node, enviroment):
        self.visit(node.expression, enviroment)

        node.computed_type = enviroment.get_type("Bool")

    # [Not]
    @visitor.when(ast.NegationNode)
    def visit(self, node, enviroment):
        self.visit(node.expression, enviroment)

        if node.expression.computed_type.name != "Bool":
            errors.throw_error(errors.TypeError(text=f"The expression for unary operation 'Not' must have type 'Bool'.", line=node.line, column=node.column))

        node.computed_type = enviroment.get_type("Bool")

    # [Compare]
    @visitor.when(ast.ComparisonNode)
    def visit(self, node, enviroment):
        self.visit(node.left_expression, enviroment)
        self.visit(node.right_expression, enviroment)

        if node.left_expression.computed_type.name != 'Int' or node.right_expression.computed_type.name != 'Int':
            errors.throw_error(errors.TypeError(text=f"In compare operation type of letf and right expressions must be 'Int'.", line=node.line, column=node.column))

        node.computed_type = enviroment.get_type("Bool")

    # [Neg]
    @visitor.when(ast.ComplementNode)
    def visit(self, node, enviroment):
        self.visit(node.expression, enviroment)

        if node.expression.computed_type.name != "Int":
            errors.throw_error(errors.TypeError(text=f"The expression for unary operation 'Neg' must have type 'Int'.", line=node.line, column=node.column))

        node.computed_type = enviroment.get_type("Int")
    
    # [Arith]
    @visitor.when(ast.BinaryOperatorNode)
    def visit(self, node, enviroment):
        self.visit(node.left_expression, enviroment)
        self.visit(node.right_expression, enviroment)

        if node.left_expression.computed_type.name != 'Int' or node.right_expression.computed_type.name != 'Int':
            errors.throw_error(errors.TypeError(text=f"In arithmetic operation type of letf and right expressions must be 'Int'.", line=node.line, column=node.column))

        node.computed_type = enviroment.get_type("Int")

    # [Equal]
    @visitor.when(ast.EqualNode)
    def visit(self, node, enviroment):
        self.visit(node.left_expression, enviroment)
        self.visit(node.right_expression, enviroment)

        basic_types = ['Int', 'String', 'Bool']

        if node.left_expression.computed_type.name in basic_types \
            or node.right_expression.computed_type.name in basic_types:
            
            if node.left_expression.computed_type.name != node.right_expression.computed_type.name:
                errors.throw_error(errors.TypeError(text=f"In an equal operation, both expressions must have the same basic type.", line=node.line, column=node.column))
        
        node.computed_type = enviroment.get_type('Bool')

    # [Attr-Init]
    # [Attr-No-Init]
    @visitor.when(ast.FeatureAttributeNode)
    def visit(self, node, enviroment):
        # [Attr-No-Init]
        node.computed_type = enviroment.get_symbol_type(node.name)

        # check if attribute has an initialization expression
        if node.expression is not None:
           # [Attr-Init]    
            child_enviroment = enviroment.create_child_enviroment()
            child_enviroment.define_symbol('self', 'SELF_TYPE'+self.current_type.name, 0, 0)
            
            self.visit(node.expression, child_enviroment)
            
            if not enviroment.conforms(node.expression.computed_type, node.computed_type):
                errors.throw_error(errors.TypeError(text=f"Initialization expression type for attribute '{node.name}' does not conforms with its declared type.", line=node.line, column=node.column))

            node.computed_type = node.expression.computed_type

    # [Method]
    @visitor.when(ast.FeatureMethodNode)
    def visit(self, node, enviroment):
        child_enviroment = enviroment.create_child_enviroment()
        child_enviroment.define_symbol('self', 'SELF_TYPE'+self.current_type.name, 0, 0)

        for formal_param in node.formal_parameter_list:
            child_enviroment.define_symbol(formal_param.name, formal_param.type_parameter, formal_param.line, formal_param.column)

        self.visit(node.expression, child_enviroment)
        
        if node.return_type_method == 'SELF_TYPE':
            _type = Type('SELF_TYPE', self.current_type.name)
        else:
            # type_builder guarantee that _type exists
            _type = enviroment.get_type(node.return_type_method)

        if not enviroment.conforms(node.expression.computed_type, _type):
            errors.throw_error(errors.TypeError(text=f"Body expression type for method '{node.name}' does not conforms with its return type.", line=node.line, column=node.column))

        node.computed_type = node.expression.computed_type