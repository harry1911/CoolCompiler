# module: grammar_rules.py
# This module just contains the grammar rules

# Get the token map from the lexer.  This is required.
import re
from general import ast_hierarchy as ast
from general import errors
from .lexer_rules import tokens
from .ply import yacc


class CoolParse:
    def __init__(self, lexer):
        self.tokens = tokens
        self.error_list = []
        self.lexer = lexer
        self.parser = None

    # Build the parser
    def build(self, **kwargs):
        self.parser = yacc.yacc(module=self, **kwargs)

    def parse(self, input_code):
        if self.parser is None:
            raise Exception("You need to build the lexer first!!")

        return self.parser.parse(input_code)

    # precedence rules
    precedence = (
        ('right', 'ASSIGN'),
        ('right', 'NOT'),
        ('nonassoc', 'LESSEQUAL', 'LESS', 'EQUAL'),
        ('left', 'PLUS', 'MINUS'),
        ('left', 'STAR', 'DIV'),
        ('right', 'ISVOID'),
        ('right', 'COMPLEMENT'),
        ('left', 'AT'),
        ('left', 'DOT')
    )

    ###################### Grammar rules ######################

    def p_program(self, parse):
        '''
        program : class SEMICOLON class_list
        '''
        parse[0] = ast.ProgramNode(class_list=[parse[1]]+parse[3])

    def p_class_list(self, parse):
        '''
        class_list : class SEMICOLON class_list
        '''
        parse[0] = [parse[1]] + parse[3]      

    def p_class_list_empty(self, parse):
        '''
        class_list : empty
        '''
        parse[0] = []

    def p_class(self, parse):
        '''
        class : CLASS TYPE inherits OCURLY feature_list CCURLY
        '''
        parse[0] = ast.ClassNode(name=parse[2], parent=parse[3], attribute_list=parse[5][0], method_list=parse[5][1], line=parse.lineno(1), column=parse.lexpos(1))

    def p_class_inherits(self, parse):
        '''
        inherits : INHERITS TYPE
        '''
        parse[0] = parse[2]

    def p_class_inherits_empty(self, parse):
        '''
        inherits : empty
        '''
        parse[0] = "Object"

    def p_feature_list_attribute(self, parse):
        '''
        feature_list : feature_attribute SEMICOLON feature_list
        '''
        parse[0] = [[parse[1]]+parse[3][0], parse[3][1]]

    def p_feature_list_method(self, parse):
        '''
        feature_list : feature_method SEMICOLON feature_list
        '''
        parse[0] = [parse[3][0], [parse[1]]+parse[3][1]]

    def p_feature_list_empty(self, parse):
        '''
        feature_list : empty
        '''
        parse[0] = [[],[]]

    def p_feature_method(self, parse):
        '''
        feature_method : IDENTIFIER OBRACKET formal_params_list CBRACKET COLON TYPE OCURLY expression CCURLY
        '''
        parse[0] = ast.FeatureMethodNode(name=parse[1], formal_parameter_list=parse[3], return_type_method=parse[6], 
                                         expression=parse[8], line=parse.lineno(1), column=parse.lexpos(1))

    def p_feature_attribute_initialized(self, parse):
        '''
        feature_attribute : IDENTIFIER COLON TYPE ASSIGN expression
        '''
        parse[0] = ast.FeatureAttributeNode(name=parse[1], type_attribute=parse[3], expression=parse[5], line=parse.lineno(1), column=parse.lexpos(1))

    def p_feature_attribute(self, parse):
        '''
        feature_attribute : IDENTIFIER COLON TYPE
        '''
        parse[0] = ast.FeatureAttributeNode(name=parse[1], type_attribute=parse[3], expression=None, line=parse.lineno(1), column=parse.lexpos(1))

    def p_formal_params_list(self, parse):
        '''
        formal_params_list : formal more_formal_params_list
        '''
        parse[0] = [parse[1]] + parse[2]

    def p_formal_params_list_empty(self, parse):
        '''
        formal_params_list : empty
        '''
        parse[0] = []

    def p_more_formal_params_list(self, parse):
        '''
        more_formal_params_list : COMMA formal more_formal_params_list
        '''
        parse[0] = [parse[2]] + parse[3]

    def p_more_formal_params_list_empty(self, parse):
        '''
        more_formal_params_list : empty
        '''
        parse[0] = []

    def p_formal(self, parse):
        '''
        formal : IDENTIFIER COLON TYPE
        '''
        parse[0] = ast.FormalParameterNode(name=parse[1], type_parameter=parse[3], line=parse.lineno(1), column=parse.lexpos(1))

    ######## Aux for expressions ########
    def p_expression_list(self, parse):
        '''
        expression_list : expression more_expression_list
        ''' 
        parse[0] = [parse[1]] + parse[2]

    def p_expression_list_empty(self, parse):
        '''
        expression_list : empty
        ''' 
        parse[0] = []

    def p_more_expression_list(self, parse):
        '''
        more_expression_list : COMMA expression more_expression_list
        ''' 
        parse[0] = [parse[2]] + parse[3]

    def p_more_expression_list_empty(self, parse):
        '''
        more_expression_list : empty
        ''' 
        parse[0] = []

    def p_block_expression_list_simple(self, parse):
        '''
        block_expression_list : expression SEMICOLON
        '''
        parse[0] = [parse[1]]

    def p_block_expression_list(self, parse):
        '''
        block_expression_list : expression SEMICOLON block_expression_list
        '''
        parse[0] = [parse[1]] + parse[3]

    def p_let_expressions_simple(self, parse):
        '''
        let_expressions : IDENTIFIER COLON TYPE let_list
        '''
        parse[0] = [ast.DeclarationNode(name=parse[1], _type=parse[3], expression=None, line=parse.lineno(1), column=parse.lexpos(1))] + parse[4]

    def p_let_expressions(self, parse):
        '''
        let_expressions : IDENTIFIER COLON TYPE ASSIGN expression let_list
        '''
        parse[0] = [ast.DeclarationNode(name=parse[1], _type=parse[3], expression=parse[5], line=parse.lineno(1), column=parse.lexpos(1))] + parse[6]

    def p_let_list_simple(self, parse):
        '''
        let_list : COMMA IDENTIFIER COLON TYPE let_list
        '''
        parse[0] = [ast.DeclarationNode(name=parse[2], _type=parse[4], expression=None, line=parse.lineno(2), column=parse.lexpos(2))] + parse[5]

    def p_let_list(self, parse):
        '''
        let_list : COMMA IDENTIFIER COLON TYPE ASSIGN expression let_list
        '''
        parse[0] = [ast.DeclarationNode(name=parse[2], _type=parse[4], expression=parse[6], line=parse.lineno(2), column=parse.lexpos(2))] + parse[7]

    def p_let_list_empty(self, parse):
        '''
        let_list : empty
        '''
        parse[0] = []

    def p_branch_list(self, parse):
        '''
        branch_list : branch branch_list
        '''
        parse[0] = [parse[1]] + parse[2]

    def p_branch_list_simple(self, parse):
        '''
        branch_list : branch
        '''
        parse[0] = [parse[1]]

    def p_branch(self, parse):
        '''
        branch : IDENTIFIER COLON TYPE ARROW expression SEMICOLON
        '''
        parse[0] = ast.BranchNode(name=parse[1], type_branch=parse[3], expression=parse[5], line=parse.lineno(1), column=parse.lexpos(1))

    ################################################################


    def p_expression_object_id(self, parse):
        '''
        expression : IDENTIFIER
        '''
        if parse[1] == 'self':
            parse[0] = ast.SelfNode(line=parse.lineno(1), column=parse.lexpos(1))
        else:
            parse[0] = ast.ObjectNode(name=parse[1], line=parse.lineno(1), column=parse.lexpos(1))

    def p_expression_new(self, parse):
        '''
        expression : NEW TYPE
        '''
        parse[0] = ast.NewObjectNode(new_type=parse[2], line=parse.lineno(1), column=parse.lexpos(1))

    def p_expression_block(self, parse):
        '''
        expression : OCURLY block_expression_list CCURLY
        '''
        parse[0] = ast.BlockNode(expression_list=parse[2], line=parse.lineno(1), column=parse.lexpos(1))

    # Control flow
    def p_expression_if(self, parse):
        '''
        expression : IF expression THEN expression ELSE expression FI
        '''
        parse[0] = ast.IfNode(if_expression=parse[2], then_expression=parse[4], else_expression=parse[6], line=parse.lineno(1), column=parse.lexpos(1))

    def p_expression_while(self, parse):
        '''
        expression : WHILE expression LOOP expression POOL
        '''
        parse[0] = ast.WhileLoopNode(while_expression=parse[2], loop_expression=parse[4], line=parse.lineno(1), column=parse.lexpos(1))

    def p_expression_case(self, parse):
        '''
        expression : CASE expression OF branch_list ESAC
        '''
        parse[0] = ast.CaseNode(case_expression=parse[2], branch_list=parse[4], line=parse.lineno(1), column=parse.lexpos(1))

    # Methods Dispatchs
    def p_expression_dynamic_dispatch(self, parse):
        '''
        expression : expression DOT IDENTIFIER OBRACKET expression_list CBRACKET
        '''
        parse[0] = ast.DynamicDispatchNode(instance=parse[1], method=parse[3], arguments=parse[5], line=parse.lineno(2), column=parse.lexpos(2))

    def p_expression_static_dispatch(self, parse):
        '''
        expression : expression AT TYPE DOT IDENTIFIER OBRACKET expression_list CBRACKET
        '''
        parse[0] = ast.StaticDispatchNode(instance=parse[1], type_dispatch=parse[3], method=parse[5], 
                                          arguments=parse[7], line=parse.lineno(4), column=parse.lexpos(4))

    def p_expression_self_dispatch(self, parse):
        '''
        expression : IDENTIFIER OBRACKET expression_list CBRACKET
        '''
        parse[0] = ast.DynamicDispatchNode(instance=ast.SelfNode(line=parse.lineno(1), column=parse.lexpos(1)), method=parse[1], arguments=parse[3], line=parse.lineno(1), column=parse.lexpos(1))

    # Let expressions
    def p_expression_let(self, parse):
        '''
        expression : LET let_expressions IN expression
        '''
        parse[0] = ast.LetInNode(declaration_list=parse[2], expression=parse[4], line=parse.lineno(1), column=parse.lexpos(1))

    # Atomic Expressions
    def p_expression_integer_constant(self, parse):
        '''
        expression : INTEGER
        '''
        parse[0] = ast.IntegerNode(int_token=parse[1], line=parse.lineno(1), column=parse.lexpos(1))

    def p_expression_string_constant(self, parse):
        '''
        expression : STRING
        '''
        parse[0] = ast.StringNode(str_token=parse[1], line=parse.lineno(1), column=parse.lexpos(1))

    def p_expression_BOOLEAN_true_constant(self, parse):
        '''
        expression : TRUE
        '''
        parse[0] = ast.TrueNode(line=parse.lineno(1), column=parse.lexpos(1))

    def p_expression_BOOLEAN_false_constant(self, parse):
        '''
        expression : FALSE
        '''
        parse[0] = ast.FalseNode(line=parse.lineno(1), column=parse.lexpos(1))

    def p_expression_assign(self, parse):
        '''
        expression : IDENTIFIER ASSIGN expression
        '''
        parse[0] = ast.AssignNode(instance=ast.ObjectNode(name=parse[1], line=parse.lineno(1), column=parse.lexpos(1)), expression=parse[3], line=parse.lineno(1), column=parse.lexpos(1))

    # Binary Operations
    def p_expression_plus(self, parse):
        '''
        expression : expression PLUS expression
        '''
        parse[0] = ast.PlusNode(left_expression=parse[1], right_expression=parse[3], line=parse.lineno(2), column=parse.lexpos(2))

    def p_expression_minus(self, parse):
        '''
        expression : expression MINUS expression
        '''
        parse[0] = ast.MinusNode(left_expression=parse[1], right_expression=parse[3], line=parse.lineno(2), column=parse.lexpos(2))

    def p_expression_star(self, parse):
        '''
        expression : expression STAR expression
        '''
        parse[0] = ast.StarNode(left_expression=parse[1], right_expression=parse[3], line=parse.lineno(2), column=parse.lexpos(2))

    def p_expression_div(self, parse):
        '''
        expression : expression DIV expression
        '''
        parse[0] = ast.DivNode(left_expression=parse[1], right_expression=parse[3], line=parse.lineno(2), column=parse.lexpos(2))

    def p_expression_equal(self, parse):
        '''
        expression : expression EQUAL expression
        '''
        parse[0] = ast.EqualNode(left_expression=parse[1], right_expression=parse[3], line=parse.lineno(2), column=parse.lexpos(2))

    def p_expression_lessthan(self, parse):
        '''
        expression : expression LESS expression
        '''
        parse[0] = ast.LessThanNode(left_expression=parse[1], right_expression=parse[3], line=parse.lineno(2), column=parse.lexpos(2))

    def p_expression_lessequal(self, parse):
        '''
        expression : expression LESSEQUAL expression
        '''
        parse[0] = ast.LessThanOrEqualNode(left_expression=parse[1], right_expression=parse[3], line=parse.lineno(2), column=parse.lexpos(2))

    # Unary operations
    def p_expression_complement(self, parse):
        '''
        expression : COMPLEMENT expression
        '''
        parse[0] = ast.ComplementNode(expression=parse[2], line=parse.lineno(1), column=parse.lexpos(1))

    def p_expression_negation(self, parse):
        '''
        expression : NOT expression
        '''
        parse[0] = ast.NegationNode(expression=parse[2], line=parse.lineno(1), column=parse.lexpos(1))

    def p_expression_isvoid(self, parse):
        '''
        expression : ISVOID expression
        '''
        parse[0] = ast.IsVoidNode(expression=parse[2], line=parse.lineno(1), column=parse.lexpos(1))

    # Parenthesized expression
    def p_expression_parenthesis(self, parse):
        '''
        expression : OBRACKET expression CBRACKET
        '''
        parse[0] = parse[2]

    # Empty production
    def p_empty(self, parse):
        '''
        empty : 
        '''
        pass

    # Error rule
    def p_error(self, parse):
        if parse:
            errors.throw_error(errors.SyntacticError(text=f"Token error '{parse.value}'.", line=parse.lineno, column=parse.lexpos))
        else:
            errors.throw_error(errors.SyntacticError(text='EOF error.'))
