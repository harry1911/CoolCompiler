
from general import visitor
from general import ast_hierarchy as ast_cool
from general import cil_hierarchy as ast_cil
from .dataTypesCollector import TypesCollector
from .context import Scope, ObjecContext, Defaults
from collections import OrderedDict



class CilGeneratorVisitor:
    def __init__(self, astCool, enviroment):
        self.astCool= astCool
        self.cilProgram = None
        self.types_dict = enviroment.types_dict
        self.objectContext = ObjecContext(enviroment.types_list[1:])
        self.current_type = None # type(current_type) = Type
        self.context = Scope()
        self.num_labels = 0
        self.defaults = {}      # { str(class_name) : Defaults }

    def generate_code(self):
        collector = TypesCollector(self.astCool, self.types_dict)
        self.defaults = collector.getTypes()
        self.cilProgram = collector.astCil # types added
        self.visit(self.astCool, self.context) # build Data and Code seccions
        return self.cilProgram

    def add_constructor(self, type_defaults, context):
        child_context = context.create_child()
        child_context.self = child_context.define_local()

        function_name = type_defaults.class_name + '.ctor'
        argument_list = [ast_cil.CILArgument('self', child_context.self)]

        # localvars = [child_context.self]
        localvars = []        
        code = []
        for feature_attr in type_defaults.defaults:
            attr_offset = self.cilProgram.dotTYPES.types[self.current_type.name].attributes.get(feature_attr.name).offset
            if feature_attr.type_attribute in ['Int','Bool']:
                local_var = child_context.define_local()
                localvars.append(local_var)
                local_tag = child_context.define_local(self.types_dict[feature_attr.type_attribute])
                localvars.append(local_tag)

                cil_allocate = ast_cil.CILAllocate(local_tag)
                cil_assign1 = ast_cil.CILAssignment(local_var, cil_allocate)
                code.append(cil_assign1)
                cil_setattr1 = ast_cil.CILSetAttr(child_context.self, attr_offset, local_var)
                code.append(cil_setattr1)
            elif feature_attr.type_attribute == 'String':
                local_var = child_context.define_local()
                localvars.append(local_var)
                cil_str = ast_cil.CILString()
                cil_assign2 = ast_cil.CILAssignment(local_var, cil_str)
                code.append(cil_assign2)
                cil_setattr2 = ast_cil.CILSetAttr(child_context.self, attr_offset, local_var)
                code.append(cil_setattr2)
        
        for feature_attr in type_defaults.defaults:
            if feature_attr.expression is not None:
                attr_offset = self.cilProgram.dotTYPES.types[self.current_type.name].attributes.get(feature_attr.name).offset
                self.visit(feature_attr.expression, child_context)
                localvars += feature_attr.expression.locals
                code += feature_attr.expression.code
                cil_setattr3 = ast_cil.CILSetAttr(child_context.self, attr_offset, feature_attr.expression.value)
                code.append(cil_setattr3)

        code.append(ast_cil.CILReturn(child_context.self))        
        cil_func = ast_cil.CILFunction(function_name, argument_list, localvars, code)
        self.cilProgram.dotCODE.append(cil_func)
                    
    @visitor.on('node')
    def visit(self, node, context):
        pass
    
    @visitor.when(ast_cool.ProgramNode)
    def visit(self, node, context):
        for _class in node.class_list:
            child_context = context.create_child()
            self.visit(_class, child_context)

    @visitor.when(ast_cool.ClassNode)
    def visit(self, node, context):
        self.current_type = self.objectContext.get_type(node.name)

        self.add_constructor(self.defaults[node.name], context)

        for method in node.method_list:
            self.visit(method, context)
            self.cilProgram.dotCODE.append(method.code)
            
    @visitor.when(ast_cool.FeatureMethodNode)
    def visit(self, node, context):
        child_context = context.create_child()
        child_context.self = child_context.define_local()

        function_name = self.current_type.name + '.' + node.name

        # localvars = [child_context.self]
        localvars = []
        argument_list = [ast_cil.CILArgument('self', child_context.self)]
        for param in node.formal_parameter_list:
            local_arg = child_context.define_local()
            # localvars.append(local_arg)
            argument = ast_cil.CILArgument(param.name, local_arg)
            argument_list.append(argument)
            child_context.define_variable(param.name, param.type_parameter, local_arg)
        
        self.visit(node.expression, child_context)
        
        local_value = node.expression.value
        localvars += node.expression.locals
        code = node.expression.code
        code.append(ast_cil.CILReturn(local_value))
        
        cil_func = ast_cil.CILFunction(function_name, argument_list, localvars, code)

        node.value = local_value
        node.locals = localvars
        node.code = cil_func

    # [Assign]
    @visitor.when(ast_cool.AssignNode)
    def visit(self, node, context):
        self.visit(node.expression, context)
        localvars = node.expression.locals
        code = node.expression.code

        vinfo = context.find_variable(node.instance.name)

        if vinfo is None:
            # check if this variable is an attr
            attr = self.cilProgram.dotTYPES.types[self.current_type.name].attributes.get(node.instance.name)
            if attr is None:
                # throw an error because var is not defined(this shouldn't happend)
                raise Exception('Attr is not defined.')

            cil_setattr = ast_cil.CILSetAttr(context.self, attr.offset, node.expression.value)
            code.append(cil_setattr)
        else:
            cil_assign = ast_cil.CILAssignment(vinfo.cil_name, ast_cil.CILVar(node.expression.value))
            code.append(cil_assign)
            
        node.value = node.expression.value
        node.locals = localvars
        node.code = code

    # [Self]
    @visitor.when(ast_cool.SelfNode)
    def visit(self, node, context):
        node.value = context.self
        node.locals = []
        node.code = []

    # [Var - Identifier]
    @visitor.when(ast_cool.ObjectNode)
    def visit(self, node, context):
        localvars = []
        code = []

        vinfo = context.find_variable(node.name)

        if vinfo is None:
            # check if this variable is an attr
            attr = self.cilProgram.dotTYPES.types[self.current_type.name].attributes.get(node.name)
            if attr is None:
                # throw an error because var is not defined(this shouldn't happend)
                pass

            local_value = context.define_local()
            localvars.append(local_value)

            cil_getattr = ast_cil.CILGetAttr(context.self, attr.offset)
            cil_assign = ast_cil.CILAssignment(local_value, cil_getattr)
            code.append(cil_assign)
        else:
            local_value = vinfo.cil_name

        node.value = local_value
        node.locals = localvars
        node.code = code

    # [True]
    @visitor.when(ast_cool.TrueNode) 
    def visit(self, node, context):
        local_bool_content = context.define_local(1)
        local_bool_tag = context.define_local(self.types_dict['Bool'])
        local_value = context.define_local()

        cil_allocate = ast_cil.CILAllocate(local_bool_tag)
        cil_assign = ast_cil.CILAssignment(local_value, cil_allocate)
        cil_setattr = ast_cil.CILSetAttr(local_value, 0, local_bool_content)
        
        node.value = local_value
        node.locals = [local_value, local_bool_content, local_bool_tag]
        node.code = [cil_assign, cil_setattr]

    # [False]
    @visitor.when(ast_cool.FalseNode) 
    def visit(self, node, context):
        local_bool_tag = context.define_local(self.types_dict['Bool'])
        local_value = context.define_local()

        cil_allocate = ast_cil.CILAllocate(local_bool_tag)
        cil_assign = ast_cil.CILAssignment(local_value, cil_allocate)
        
        node.value = local_value
        node.locals = [local_value, local_bool_tag]
        node.code = [cil_assign]

    # [Int]
    @visitor.when(ast_cool.IntegerNode)
    def visit(self, node, context):
        local_int_content = context.define_local(int(node.int_token))
        local_int_tag = context.define_local(self.types_dict['Int'])
        local_value = context.define_local()

        cil_allocate = ast_cil.CILAllocate(local_int_tag)
        cil_assign = ast_cil.CILAssignment(local_value, cil_allocate)
        cil_setattr = ast_cil.CILSetAttr(local_value, 0, local_int_content)
        
        node.value = local_value
        node.locals = [local_value, local_int_content, local_int_tag]
        node.code = [cil_assign, cil_setattr]

    # [String]
    @visitor.when(ast_cool.StringNode) 
    def visit(self, node, context):
        local_value = context.define_local()

        cil_str = ast_cil.CILString(node.str_token)
        cil_assign = ast_cil.CILAssignment(local_value, cil_str)
        
        node.value = local_value
        node.locals = [local_value]
        node.code = [cil_assign]

    # [New]
    @visitor.when(ast_cool.NewObjectNode) 
    def visit(self, node, context):
        localvars = []
        code = []

        local_instance = context.define_local()
        localvars.append(local_instance)

        # TODO: code added
        if node.new_type == 'String':
            cil_str = ast_cil.CILString()
            cil_assign3 = ast_cil.CILAssignment(local_instance, cil_str)
            code.append(cil_assign3)

            node.value = local_instance
            node.locals = localvars
            node.code = code

            return

        if node.new_type == 'SELF_TYPE':
            local_tag = context.define_local()
            localvars.append(local_tag)
            cil_typeof = ast_cil.CILTypeOf(context.self)
            cil_assign1 = ast_cil.CILAssignment(local_tag, cil_typeof)
            code.append(cil_assign1)
        else:
            local_tag = context.define_local(self.types_dict[node.new_type])
            localvars.append(local_tag)

        cil_allocate = ast_cil.CILAllocate(local_tag)
        cil_assign2 = ast_cil.CILAssignment(local_instance, cil_allocate)
        code.append(cil_assign2)

        # local_value = context.define_local()
        # localvars.append(local_value)

        # cil_self_param = ast_cil.CILParam(local_instance)
        # code.append(cil_self_param)
        # cil_ctor = ast_cil.CILConstructor(local_tag)
        # cil_assign3 = ast_cil.CILAssignment(local_instance, cil_ctor)
        # code.append(cil_assign3)

        node.value = local_instance
        node.locals = localvars
        node.code = code

    # [DynamicDispatch]
    @visitor.when(ast_cool.DynamicDispatchNode)
    def visit(self, node, context):
        localvars = []
        code = []

        params = []
        for arg_expr in node.arguments:
            self.visit(arg_expr, context)
            localvars += arg_expr.locals
            code += arg_expr.code
            params.append(ast_cil.CILParam(arg_expr.value))

        self.visit(node.instance, context)
        localvars += node.instance.locals
        code += node.instance.code

        self.num_labels += 1
        cil_dispatchnotvoid_label = ast_cil.CILLabel('DISPATCH_NOT_VOID' + str(self.num_labels))

        cil_cond = ast_cil.CILCondition(node.instance.value, cil_dispatchnotvoid_label.label)
        code.append(cil_cond)

        cil_goto1 = ast_cil.CILGoTo('_dispatch_abort') # DISPATCH_ON_VOID
        code.append(cil_goto1)
        
        code.append(cil_dispatchnotvoid_label) # DISPATCH_NOT_VOID

        param_instance = ast_cil.CILParam(node.instance.value)
        
        # take the method offset
        type_name = node.instance.computed_type.name
        if type_name == 'SELF_TYPE':
            type_name = node.instance.computed_type.parent
        meth_offset = self.cilProgram.dotTYPES.types[type_name].methods.get(node.method).offset

        # check order of parameters
        code.append(param_instance)
        for _param in params:
            code.append(_param)

        local_value = context.define_local()
        localvars.append(local_value)

        cil_dcall = ast_cil.CILDinamicCall(node.instance.value, meth_offset)
        cil_assign = ast_cil.CILAssignment(local_value, cil_dcall)
        code.append(cil_assign)

        node.value = local_value
        node.locals = localvars
        node.code = code

    # [StaticDispatch]
    @visitor.when(ast_cool.StaticDispatchNode)
    def visit(self, node, context):
        localvars = []
        code = []

        params = []
        for arg_expr in node.arguments:
            self.visit(arg_expr, context)
            localvars += arg_expr.locals
            code += arg_expr.code
            params.append(ast_cil.CILParam(arg_expr.value))

        self.visit(node.instance, context)
        localvars += node.instance.locals
        code += node.instance.code

        self.num_labels += 1
        cil_dispatchnotvoid_label = ast_cil.CILLabel('DISPATCH_NOT_VOID' + str(self.num_labels))

        cil_cond = ast_cil.CILCondition(node.instance.value, cil_dispatchnotvoid_label.label)
        code.append(cil_cond)

        cil_goto1 = ast_cil.CILGoTo('_dispatch_abort') # DISPATCH_ON_VOID
        code.append(cil_goto1)
        
        code.append(cil_dispatchnotvoid_label) # DISPATCH_NOT_VOID
        
        param_instance = ast_cil.CILParam(node.instance.value)
        
        # take the method function
        func_name = self.cilProgram.dotTYPES.types[node.type_dispatch].methods.get(node.method).func

        # check order of parameters
        code.append(param_instance)
        for _param in params:
            code.append(_param)

        local_value = context.define_local()
        localvars.append(local_value)

        cil_scall = ast_cil.CILStaticCall(func_name)
        cil_assign = ast_cil.CILAssignment(local_value, cil_scall)
        code.append(cil_assign)

        node.value = local_value
        node.locals = localvars
        node.code = code

    # [If-True]
    # [If-False]
    @visitor.when(ast_cool.IfNode)
    def visit(self, node, context):
        self.visit(node.if_expression, context)
        localvars = node.if_expression.locals
        code = node.if_expression.code

        local_value = context.define_local()
        localvars.append(local_value)

        self.num_labels += 1
        cil_then_label = ast_cil.CILLabel('THEN' + str(self.num_labels))
        self.num_labels += 1
        cil_end_label = ast_cil.CILLabel('END' + str(self.num_labels))

        local_if_value = context.define_local()
        localvars.append(local_if_value)

        cil_getattr = ast_cil.CILGetAttr(node.if_expression.value, 0)
        cil_assign1 = ast_cil.CILAssignment(local_if_value, cil_getattr)
        code.append(cil_assign1)

        cil_condition = ast_cil.CILCondition(local_if_value, cil_then_label.label)
        code.append(cil_condition)

        self.visit(node.else_expression, context)
        localvars += node.else_expression.locals
        code += node.else_expression.code
        cil_assign2 = ast_cil.CILAssignment(local_value, ast_cil.CILVar(node.else_expression.value))
        code.append(cil_assign2)

        cil_goto = ast_cil.CILGoTo(cil_end_label.label)
        code.append(cil_goto)

        code.append(cil_then_label) # THEN        
        self.visit(node.then_expression, context)
        localvars += node.then_expression.locals
        code += node.then_expression.code
        cil_assign3 = ast_cil.CILAssignment(local_value, ast_cil.CILVar(node.then_expression.value))
        code.append(cil_assign3)

        code.append(cil_end_label) # END

        node.value = local_value
        node.locals = localvars
        node.code = code
    
    # [Sequence]    
    @visitor.when(ast_cool.BlockNode)
    def visit(self, node, context):
        local_value = None
        code = []
        localvars = []

        for expr in node.expression_list:
            self.visit(expr, context)
            local_value = expr.value
            code += expr.code
            localvars += expr.locals
            
        node.value = local_value
        node.locals = localvars
        node.code = code

    # [Let]    
    @visitor.when(ast_cool.LetInNode)
    def visit(self, node, context):
        localvars = []
        code = []

        current_context = context
        for _decl in node.declaration_list:
            local_decl = current_context.define_local()
            localvars.append(local_decl)

            if _decl.expression is None:
                if _decl._type == 'String':
                    cil_str = ast_cil.CILString()
                    cil_assign1 = ast_cil.CILAssignment(local_decl, cil_str)
                    code.append(cil_assign1)
                elif _decl._type in ['Int','Bool']:
                    local_tag = current_context.define_local(self.types_dict[_decl._type])
                    localvars.append(local_tag)
                    cil_allocate = ast_cil.CILAllocate(local_tag)
                    cil_assign2 = ast_cil.CILAssignment(local_decl, cil_allocate)
                    code.append(cil_assign2)
            else:
                self.visit(_decl.expression, current_context)
                localvars += _decl.expression.locals
                code += _decl.expression.code

                cil_assign3 = ast_cil.CILAssignment(local_decl, ast_cil.CILVar(_decl.expression.value))
                code.append(cil_assign3)
            
            new_child_context = current_context.create_child()
            new_child_context.define_variable(_decl.name, _decl._type, local_decl)
            current_context = new_child_context

        self.visit(node.expression, current_context)
        localvars += node.expression.locals
        code += node.expression.code

        node.value = node.expression.value
        node.locals = localvars
        node.code = code

    # [Case]
    @visitor.when(ast_cool.CaseNode)
    def visit(self, node, context):
        self.visit(node.case_expression, context)
        localvars = node.case_expression.locals
        code = node.case_expression.code

        self.num_labels += 1
        cil_caseonvoid_label = ast_cil.CILLabel('CASE_ON_VOID' + str(self.num_labels))
        self.num_labels += 1
        cil_taketag_label = ast_cil.CILLabel('TAKE_TAG' + str(self.num_labels))
        self.num_labels += 1
        cil_while_label = ast_cil.CILLabel('WHILE' + str(self.num_labels))
        self.num_labels += 1
        cil_casenobranch_label = ast_cil.CILLabel('CASE_NO_BRANCH' + str(self.num_labels))
        self.num_labels += 1
        cil_takeparenttag_label = ast_cil.CILLabel('TAKE_PARENT_TAG' + str(self.num_labels))
        self.num_labels += 1
        cil_end_label = ast_cil.CILLabel('END' + str(self.num_labels))

        cil_condition1 = ast_cil.CILCondition(node.case_expression.value, cil_taketag_label.label)
        code.append(cil_condition1)

        code.append(cil_caseonvoid_label) # CASE_ON_VOID _case_abort2
        cil_goto1 = ast_cil.CILGoTo('_case_abort2')
        code.append(cil_goto1)
        
        # cil_goto1 = ast_cil.CILGoTo(cil_end_label.label)
        # code.append(cil_goto1)

        code.append(cil_taketag_label) # TAKE_TAG
        local_instance_tag = context.define_local()
        localvars.append(local_instance_tag)

        cil_typeof = ast_cil.CILTypeOf(node.case_expression.value)
        cil_assign1 = ast_cil.CILAssignment(local_instance_tag, cil_typeof)
        code.append(cil_assign1)

        local_value = context.define_local()
        localvars.append(local_value)

        code.append(cil_while_label) # WHILE

        for _branch in node.branch_list:
            local_branch_tag = context.define_local(self.types_dict[_branch.type_branch])
            localvars.append(local_branch_tag)
            local_diff = context.define_local()
            localvars.append(local_diff)

            cil_minus = ast_cil.CILMinus(local_instance_tag, local_branch_tag)
            cil_assign2 = ast_cil.CILAssignment(local_diff, cil_minus)
            code.append(cil_assign2)

            self.num_labels += 1
            cil_typenotmatch_label = ast_cil.CILLabel('TYPE_NOT_MATCH' + str(self.num_labels))

            cil_condition = ast_cil.CILCondition(local_diff, cil_typenotmatch_label.label)
            code.append(cil_condition)

            child_context = context.create_child()
            child_context.define_variable(_branch.name, _branch.type_branch, node.case_expression.value)

            self.visit(_branch.expression, child_context)
            localvars += _branch.expression.locals
            code += _branch.expression.code

            cil_assign3 = ast_cil.CILAssignment(local_value, ast_cil.CILVar(_branch.expression.value))
            code.append(cil_assign3)

            cil_goto = ast_cil.CILGoTo(cil_end_label.label)
            code.append(cil_goto)

            code.append(cil_typenotmatch_label) # TYPE_NOT_MATCH

        cil_condition2 = ast_cil.CILCondition(local_instance_tag, cil_takeparenttag_label.label)
        code.append(cil_condition2)

        code.append(cil_casenobranch_label) # CASE_NO_BRANCH _case_abort
        cil_goto2 = ast_cil.CILGoTo('_case_abort')
        code.append(cil_goto2)
        
        # cil_goto2 = ast_cil.CILGoTo(cil_end_label.label)
        # code.append(cil_goto2)

        code.append(cil_takeparenttag_label) # TAKE_PARENT_TAG

        cil_parent = ast_cil.CILGetIndex(local_instance_tag)
        cil_assign4 = ast_cil.CILAssignment(local_instance_tag, cil_parent)
        code.append(cil_assign4)

        cil_goto3 = ast_cil.CILGoTo(cil_while_label.label)
        code.append(cil_goto3)

        code.append(cil_end_label) # END

        node.value = local_value
        node.locals = localvars
        node.code = code

    # [Loop-True]
    # [Loop-False]
    @visitor.when(ast_cool.WhileLoopNode)
    def visit(self, node, context):
        localvars = []
        code = []

        self.num_labels += 1
        cil_while_label = ast_cil.CILLabel('WHILE' + str(self.num_labels))
        self.num_labels += 1
        cil_loop_label = ast_cil.CILLabel('LOOP' + str(self.num_labels))
        self.num_labels += 1
        cil_pool_label = ast_cil.CILLabel('POOL' + str(self.num_labels))

        local_while_value = context.define_local()
        localvars.append(local_while_value)

        code.append(cil_while_label) # WHILE
        
        self.visit(node.while_expression, context)
        localvars += node.while_expression.locals
        code += node.while_expression.code

        cil_getattr = ast_cil.CILGetAttr(node.while_expression.value, 0)
        cil_assign = ast_cil.CILAssignment(local_while_value, cil_getattr)
        code.append(cil_assign)

        cil_condition = ast_cil.CILCondition(local_while_value, cil_loop_label.label)
        code.append(cil_condition)
        
        cil_goto1 = ast_cil.CILGoTo(cil_pool_label.label)
        code.append(cil_goto1)

        code.append(cil_loop_label) # LOOP
        self.visit(node.loop_expression, context)
        localvars += node.loop_expression.locals
        code += node.loop_expression.code

        cil_goto2 = ast_cil.CILGoTo(cil_while_label.label)
        code.append(cil_goto2)

        code.append(cil_pool_label) # POOL
        # return void
        local_value = context.define_local()
        localvars.append(local_value)

        node.value = local_value
        node.locals = localvars
        node.code = code

    # [IsVoid-True]
    # [IsVoid-False]
    @visitor.when(ast_cool.IsVoidNode)
    def visit(self, node, context):
        self.visit(node.expression, context)
        code = node.expression.code
        localvars = node.expression.locals

        self.num_labels += 1
        cil_false_label = ast_cil.CILLabel('FALSE' + str(self.num_labels))
        self.num_labels += 1
        cil_end_label = ast_cil.CILLabel('END' + str(self.num_labels))

        local_value = context.define_local()
        localvars.append(local_value)
        local_bool_tag = context.define_local(self.types_dict['Bool'])
        localvars.append(local_bool_tag)
        cil_allocate = ast_cil.CILAllocate(local_bool_tag)
        cil_assign = ast_cil.CILAssignment(local_value, cil_allocate)
        code.append(cil_assign)

        cil_condition = ast_cil.CILCondition(node.expression.value, cil_false_label.label)
        code.append(cil_condition)

        # TRUE
        local_true_content = context.define_local(1)
        localvars.append(local_true_content)
        cil_setattr_true = ast_cil.CILSetAttr(local_value, 0, local_true_content)
        code.append(cil_setattr_true)

        cil_goto = ast_cil.CILGoTo(cil_end_label.label)
        code.append(cil_goto)

        code.append(cil_false_label) # FALSE
        local_false_content = context.define_local(0)
        localvars.append(local_false_content)
        cil_setattr_false = ast_cil.CILSetAttr(local_value, 0, local_false_content)
        code.append(cil_setattr_false)

        code.append(cil_end_label) #END

        node.value = local_value
        node.locals = localvars
        node.code = code

    # [Not]
    @visitor.when(ast_cool.ComplementNode)
    def visit(self, node, context):
        self.visit(node.expression, context)
        code = node.expression.code
        localvars = node.expression.locals

        local_cero = context.define_local(0)
        localvars.append(local_cero)   

        local_int_content = context.define_local()
        localvars.append(local_int_content)

        cil_getattr = ast_cil.CILGetAttr(node.expression.value, 0) 
        cil_assign1 = ast_cil.CILAssignment(local_int_content, cil_getattr)
        code.append(cil_assign1)

        local_int_value = context.define_local()
        localvars.append(local_int_value)

        cil_neg = ast_cil.CILMinus(local_cero, local_int_content)
        cil_assign2 = ast_cil.CILAssignment(local_int_value, cil_neg)
        code.append(cil_assign2)

        local_value = context.define_local()
        localvars.append(local_value)
        local_int_tag = context.define_local(self.types_dict['Int'])
        localvars.append(local_int_tag)

        cil_allocate = ast_cil.CILAllocate(local_int_tag)
        cil_assign3 = ast_cil.CILAssignment(local_value, cil_allocate)
        cil_setattr = ast_cil.CILSetAttr(local_value, 0, local_int_value)
        code += [cil_assign3, cil_setattr]

        node.value = local_value
        node.locals = localvars
        node.code = code

    # [Comp]
    @visitor.when(ast_cool.LessThanOrEqualNode)
    def visit(self, node, context):
        self.visit(node.left_expression, context)
        code = node.left_expression.code
        localvars = node.left_expression.locals

        self.visit(node.right_expression, context)
        code += node.right_expression.code
        localvars += node.right_expression.locals

        local_int_left = context.define_local()
        localvars.append(local_int_left)        
        cil_getattr1 = ast_cil.CILGetAttr(node.left_expression.value, 0) 
        cil_assign1 = ast_cil.CILAssignment(local_int_left, cil_getattr1)
        code.append(cil_assign1)

        local_int_right = context.define_local()
        localvars.append(local_int_right)
        cil_getattr2 = ast_cil.CILGetAttr(node.right_expression.value, 0) 
        cil_assign2 = ast_cil.CILAssignment(local_int_right, cil_getattr2)
        code.append(cil_assign2)

        local_bool_content = context.define_local()
        localvars.append(local_bool_content)

        cil_lesseq = ast_cil.CILLessThanEq(local_int_left, local_int_right)
        cil_assign3 = ast_cil.CILAssignment(local_bool_content, cil_lesseq)
        code.append(cil_assign3)

        local_value = context.define_local()
        localvars.append(local_value)
        local_bool_tag = context.define_local(self.types_dict['Bool'])
        localvars.append(local_bool_tag)

        cil_allocate = ast_cil.CILAllocate(local_bool_tag)
        cil_assign4 = ast_cil.CILAssignment(local_value, cil_allocate)
        cil_setattr = ast_cil.CILSetAttr(local_value, 0, local_bool_content)
        code += [cil_assign4, cil_setattr]

        node.value = local_value
        node.locals = localvars
        node.code = code

    @visitor.when(ast_cool.LessThanNode)
    def visit(self, node, context):
        self.visit(node.left_expression, context)
        code = node.left_expression.code
        localvars = node.left_expression.locals

        self.visit(node.right_expression, context)
        code += node.right_expression.code
        localvars += node.right_expression.locals

        local_int_left = context.define_local()
        localvars.append(local_int_left)        
        cil_getattr1 = ast_cil.CILGetAttr(node.left_expression.value, 0) 
        cil_assign1 = ast_cil.CILAssignment(local_int_left, cil_getattr1)
        code.append(cil_assign1)

        local_int_right = context.define_local()
        localvars.append(local_int_right)
        cil_getattr2 = ast_cil.CILGetAttr(node.right_expression.value, 0) 
        cil_assign2 = ast_cil.CILAssignment(local_int_right, cil_getattr2)
        code.append(cil_assign2)

        local_bool_content = context.define_local()
        localvars.append(local_bool_content)

        cil_less = ast_cil.CILLessThan(local_int_left, local_int_right)
        cil_assign3 = ast_cil.CILAssignment(local_bool_content, cil_less)
        code.append(cil_assign3)

        local_value = context.define_local()
        localvars.append(local_value)
        local_bool_tag = context.define_local(self.types_dict['Bool'])
        localvars.append(local_bool_tag)

        cil_allocate = ast_cil.CILAllocate(local_bool_tag)
        cil_assign4 = ast_cil.CILAssignment(local_value, cil_allocate)
        cil_setattr = ast_cil.CILSetAttr(local_value, 0, local_bool_content)
        code += [cil_assign4, cil_setattr]

        node.value = local_value
        node.locals = localvars
        node.code = code

    # [Neg]
    @visitor.when(ast_cool.NegationNode)
    def visit(self, node, context):
        self.visit(node.expression, context)
        code = node.expression.code
        localvars = node.expression.locals

        local_one = context.define_local(1)
        localvars.append(local_one)   

        local_bool_content = context.define_local()
        localvars.append(local_bool_content)

        cil_getattr = ast_cil.CILGetAttr(node.expression.value, 0) 
        cil_assign1 = ast_cil.CILAssignment(local_bool_content, cil_getattr)
        code.append(cil_assign1)

        local_bool_value = context.define_local()
        localvars.append(local_bool_value)

        cil_neg = ast_cil.CILMinus(local_one, local_bool_content)
        cil_assign2 = ast_cil.CILAssignment(local_bool_value, cil_neg)
        code.append(cil_assign2)

        local_value = context.define_local()
        localvars.append(local_value)
        local_bool_tag = context.define_local(self.types_dict['Bool'])
        localvars.append(local_bool_tag)

        cil_allocate = ast_cil.CILAllocate(local_bool_tag)
        cil_assign3 = ast_cil.CILAssignment(local_value, cil_allocate)
        cil_setattr = ast_cil.CILSetAttr(local_value, 0, local_bool_value)
        code += [cil_assign3, cil_setattr]

        node.value = local_value
        node.locals = localvars
        node.code = code

    # [Arith]
    @visitor.when(ast_cool.PlusNode)
    def visit(self, node, context):
        self.visit(node.left_expression, context)
        code = node.left_expression.code
        localvars = node.left_expression.locals

        self.visit(node.right_expression, context)
        code += node.right_expression.code
        localvars += node.right_expression.locals

        local_int_left = context.define_local()
        localvars.append(local_int_left)        
        cil_getattr1 = ast_cil.CILGetAttr(node.left_expression.value, 0) 
        cil_assign1 = ast_cil.CILAssignment(local_int_left, cil_getattr1)
        code.append(cil_assign1)

        local_int_right = context.define_local()
        localvars.append(local_int_right)
        cil_getattr2 = ast_cil.CILGetAttr(node.right_expression.value, 0) 
        cil_assign2 = ast_cil.CILAssignment(local_int_right, cil_getattr2)
        code.append(cil_assign2)

        local_int_content = context.define_local()
        localvars.append(local_int_content)

        cil_plus = ast_cil.CILPLus(local_int_left, local_int_right)
        cil_assign3 = ast_cil.CILAssignment(local_int_content, cil_plus)
        code.append(cil_assign3)

        local_value = context.define_local()
        localvars.append(local_value)
        local_int_tag = context.define_local(self.types_dict['Int'])
        localvars.append(local_int_tag)

        cil_allocate = ast_cil.CILAllocate(local_int_tag)
        cil_assign4 = ast_cil.CILAssignment(local_value, cil_allocate)
        cil_setattr = ast_cil.CILSetAttr(local_value, 0, local_int_content)
        code += [cil_assign4, cil_setattr]   

        node.value = local_value
        node.locals = localvars
        node.code = code
    
    @visitor.when(ast_cool.MinusNode)
    def visit(self, node, context):
        self.visit(node.left_expression, context)
        code = node.left_expression.code
        localvars = node.left_expression.locals

        self.visit(node.right_expression, context)
        code += node.right_expression.code
        localvars += node.right_expression.locals

        local_int_left = context.define_local()
        localvars.append(local_int_left)        
        cil_getattr1 = ast_cil.CILGetAttr(node.left_expression.value, 0) 
        cil_assign1 = ast_cil.CILAssignment(local_int_left, cil_getattr1)
        code.append(cil_assign1)

        local_int_right = context.define_local()
        localvars.append(local_int_right)
        cil_getattr2 = ast_cil.CILGetAttr(node.right_expression.value, 0) 
        cil_assign2 = ast_cil.CILAssignment(local_int_right, cil_getattr2)
        code.append(cil_assign2)

        local_int_content = context.define_local()
        localvars.append(local_int_content)

        cil_minus = ast_cil.CILMinus(local_int_left, local_int_right)
        cil_assign3 = ast_cil.CILAssignment(local_int_content, cil_minus)
        code.append(cil_assign3)

        local_value = context.define_local()
        localvars.append(local_value)
        local_int_tag = context.define_local(self.types_dict['Int'])
        localvars.append(local_int_tag)

        cil_allocate = ast_cil.CILAllocate(local_int_tag)
        cil_assign4 = ast_cil.CILAssignment(local_value, cil_allocate)
        cil_setattr = ast_cil.CILSetAttr(local_value, 0, local_int_content)
        code += [cil_assign4, cil_setattr]   

        node.value = local_value
        node.locals = localvars
        node.code = code

    @visitor.when(ast_cool.StarNode)
    def visit(self, node, context):
        self.visit(node.left_expression, context)
        code = node.left_expression.code
        localvars = node.left_expression.locals

        self.visit(node.right_expression, context)
        code += node.right_expression.code
        localvars += node.right_expression.locals

        local_int_left = context.define_local()
        localvars.append(local_int_left)        
        cil_getattr1 = ast_cil.CILGetAttr(node.left_expression.value, 0) 
        cil_assign1 = ast_cil.CILAssignment(local_int_left, cil_getattr1)
        code.append(cil_assign1)

        local_int_right = context.define_local()
        localvars.append(local_int_right)
        cil_getattr2 = ast_cil.CILGetAttr(node.right_expression.value, 0) 
        cil_assign2 = ast_cil.CILAssignment(local_int_right, cil_getattr2)
        code.append(cil_assign2)

        local_int_content = context.define_local()
        localvars.append(local_int_content)

        cil_mult = ast_cil.CILMult(local_int_left, local_int_right)
        cil_assign3 = ast_cil.CILAssignment(local_int_content, cil_mult)
        code.append(cil_assign3)

        local_value = context.define_local()
        localvars.append(local_value)
        local_int_tag = context.define_local(self.types_dict['Int'])
        localvars.append(local_int_tag)

        cil_allocate = ast_cil.CILAllocate(local_int_tag)
        cil_assign4 = ast_cil.CILAssignment(local_value, cil_allocate)
        cil_setattr = ast_cil.CILSetAttr(local_value, 0, local_int_content)
        code += [cil_assign4, cil_setattr]   

        node.value = local_value
        node.locals = localvars
        node.code = code
    
    @visitor.when(ast_cool.DivNode)
    def visit(self, node, context):
        self.visit(node.left_expression, context)
        code = node.left_expression.code
        localvars = node.left_expression.locals

        self.visit(node.right_expression, context)
        code += node.right_expression.code
        localvars += node.right_expression.locals

        local_int_left = context.define_local()
        localvars.append(local_int_left)        
        cil_getattr1 = ast_cil.CILGetAttr(node.left_expression.value, 0) 
        cil_assign1 = ast_cil.CILAssignment(local_int_left, cil_getattr1)
        code.append(cil_assign1)

        local_int_right = context.define_local()
        localvars.append(local_int_right)
        cil_getattr2 = ast_cil.CILGetAttr(node.right_expression.value, 0) 
        cil_assign2 = ast_cil.CILAssignment(local_int_right, cil_getattr2)
        code.append(cil_assign2)

        self.num_labels += 1
        cil_notnone_label = ast_cil.CILLabel('NOT_NONE' + str(self.num_labels))
        self.num_labels += 1
        cil_divisionby0_label = ast_cil.CILLabel('DIVISION_BY_0' + str(self.num_labels))

        cil_condition = ast_cil.CILCondition(local_int_right, cil_notnone_label.label)
        code.append(cil_condition)

        code.append(cil_divisionby0_label) # DIVISION_BY_0
        cil_goto = ast_cil.CILGoTo('_divide_by_0')
        code.append(cil_goto)

        code.append(cil_notnone_label) # NOT_NONE

        local_int_content = context.define_local()
        localvars.append(local_int_content)

        cil_div = ast_cil.CILDiv(local_int_left, local_int_right)
        cil_assign3 = ast_cil.CILAssignment(local_int_content, cil_div)
        code.append(cil_assign3)

        local_value = context.define_local()
        localvars.append(local_value)
        local_int_tag = context.define_local(self.types_dict['Int'])
        localvars.append(local_int_tag)
        
        cil_allocate = ast_cil.CILAllocate(local_int_tag)
        cil_assign4 = ast_cil.CILAssignment(local_value, cil_allocate)
        cil_setattr = ast_cil.CILSetAttr(local_value, 0, local_int_content)
        code += [cil_assign4, cil_setattr]   

        node.value = local_value
        node.locals = localvars
        node.code = code
    
    # [Equal]
    @visitor.when(ast_cool.EqualNode) 
    def visit(self, node, context):
        self.visit(node.left_expression, context)
        code = node.left_expression.code
        localvars = node.left_expression.locals

        self.visit(node.right_expression, context)
        code += node.right_expression.code
        localvars += node.right_expression.locals

        local_value = context.define_local()
        localvars.append(local_value)
        local_bool_tag = context.define_local(self.types_dict['Bool'])
        localvars.append(local_bool_tag)

        cil_allocate = ast_cil.CILAllocate(local_bool_tag)
        cil_assign1 = ast_cil.CILAssignment(local_value, cil_allocate)
        code.append(cil_assign1)

        local_bool_content = context.define_local()
        localvars.append(local_bool_content)
        cil_eq = ast_cil.CILEqual(node.left_expression.value, node.right_expression.value)
        cil_assign3 = ast_cil.CILAssignment(local_bool_content, cil_eq)
        cil_setattr_bool = ast_cil.CILSetAttr(local_value, 0, local_bool_content)
        code += [cil_assign3, cil_setattr_bool]

        node.value = local_value
        node.locals = localvars
        node.code = code
