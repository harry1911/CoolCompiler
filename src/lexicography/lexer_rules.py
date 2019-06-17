# module: lexer_rules.py
# This module just contains the lexing rules


import re
from .ply import lex
from .ply.lex import TOKEN
from general import errors

# RESERVED WORDS
keywords = {
        'INHERITS' : '[iI][nN][hH][eE][rR][iI][tT][sS]$',
        'ISVOID' : '[iI][sS][vV][oO][iI][dD]$',
        'CLASS' : '[cC][lL][aA][sS][sS]$',
        'WHILE' : '[wW][hH][iI][lL][eE]$',
        'FALSE' : '[f][aA][lL][sS][eE]$',
        'LOOP' : '[lL][oO][oO][pP]$',
        'POOL' : '[pP][oO][oO][lL]$',
        'THEN' : '[tT][hH][eE][nN]$',
        'CASE' : '[cC][aA][sS][eE]$',
        'ESAC' : '[eE][sS][aA][cC]',
        'ELSE' : '[eE][lL][sS][eE]$',
        'TRUE' : '[t][rR][uU][eE]$',
        'LET' : '[lL][eE][tT]$',
        'NEW' : '[nN][eE][wW]$',
        'NOT' : '[nN][oO][tT]$',
        'FI' : '[fF][iI]$',
        'IF' : '[iI][fF]$',
        'IN' : '[iI][nN]$',
        'OF' : '[oO][fF]$'
}

# DECLARE THE TOKENS
tokens = ('INTEGER', 'STRING', 'IDENTIFIER', 'TYPE', 'PLUS', 'MINUS', 'STAR', 'DIV', 'LESSEQUAL', 'ASSIGN', \
        'ARROW', 'LESS', 'EQUAL', 'OBRACKET', 'CBRACKET', 'OCURLY', 'CCURLY', 'DOT', 'COLON', 'COMMA', \
        'SEMICOLON', 'COMPLEMENT', 'AT') +  tuple(keywords.keys())

class CoolLex:
    def __init__(self):
        self.tokens = tokens
        self.keywords = keywords
        self.lexer = None
        self.error_list = []

    # Build the lexer
    def build(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)
        self.lexer.line_start = -1

    def input(self, input_code):
        if self.lexer is None:
            raise Exception("You need to build the lexer first!!")
        
        self.lexer.input(input_code)

    def token(self):
        if self.lexer is None:
            raise Exception("You need to build the lexer first!!")

        return self.lexer.token()

    # Test it output
    def test(self, input_code):
        self.input(input_code)

        while True:
            tok = self.token()
            if not tok: 
                break
            print(tok)

    # DECLARE THE STATES
    @property
    def states(self):
        return (
                ('string', 'exclusive'),
                ('comment1', 'exclusive'),
                ('comment2', 'exclusive'),        
               )

    # RULES SPECIFICATION FOR INITIAL STATE
    @TOKEN('[0-9]+')
    def t_INTEGER(self, token):
        token.lexpos = (token.lexpos - self.lexer.line_start)
        return token

    @TOKEN('[a-z_][a-zA-Z0-9_]*')
    def t_IDENTIFIER(self, token):
        token.lexpos = (token.lexpos - self.lexer.line_start)
        token.type = 'IDENTIFIER'
        for key, exp in keywords.items():
            c_exp = re.compile(exp)
            if c_exp.match(token.value):
                token.type = key
                break
        return token

    @TOKEN('[A-Z][a-zA-Z0-9_]*')
    def t_TYPE(self, token):
        token.lexpos = (token.lexpos - self.lexer.line_start)
        token.type = 'TYPE'
        for key, exp in keywords.items():
            c_exp = re.compile(exp)
            if c_exp.match(token.value):
                token.type = key
                break
        return token

    # Define a rule so we can track line numbers
    def t_newline(self, token):
        '[\n]+'
        token.lexer.lineno += len(token.value)
        self.lexer.line_start = token.lexpos

    # A string containing ignored characters
    t_ignore = '[ \t\r\f\v]'

    # EOF handling rule
    def t_eof(self, token):
        return None

    # Error handling rule
    def t_string_error(self, token):
        token.lexpos = (token.lexpos - self.lexer.line_start)
        errors.throw_error(errors.LexicographicError(text=f'Illegal character {token.value}', line=token.lineno, column=token.lexpos))

    # Rules for changing lexical state
    @TOKEN(r'\-\-')
    def t_start_comment1(self, token): # Enter comment1 state
        token.lexer.push_state('comment1')

    @TOKEN(r"\(\*")
    def t_start_comment2(self, token): # Enter comment2 state
        token.lexer.push_state('comment2')

    @TOKEN(r'\"')
    def t_start_string(self, token):
        token.lexer.push_state('string')
        token.lexer.string_buf = ''
        token.lexer.string_buf_len = 1024
        token.lexer.string_lineno = token.lineno
        token.lexer.string_lexpos = (token.lexpos - self.lexer.line_start)
        
        token.lexer.string_hasnull = False
        token.lexer.backslashEscaped = False

    # RULES SPECIFICATION FOR COMMENT1 STATE
    # COMMENT1: any characters between '--' and the next newline(or EOF, if there is not next newline)

    @TOKEN("[\n]")
    def t_comment1_end(self, token):
        token.lexer.lineno += 1
        self.lexer.line_start = token.lexpos
        token.lexer.pop_state()

    t_comment1_ignore = '' 

    def t_comment1_error(self, token):
        token.lexer.skip(1)

    # EOF handling rule
    def t_comment1_eof(self, token):
        token.lexer.pop_state()    
        return None


    # RULES SPECIFICATION FOR COMMENT2 STATE
    # COMMENT2: any  characters enclosing by (* ... *). May be nested.

    @TOKEN(r"\(\*")
    def t_comment2_nested(self, token): # Enter comment2 state
        token.lexer.push_state('comment2')

    @TOKEN(r'\*\)')
    def t_comment2_end(self, token):
        token.lexer.pop_state()

    @TOKEN('[\n]')  
    def t_comment2_newline(self, token):
        token.lexer.lineno += 1
        self.lexer.line_start = token.lexpos

    t_comment2_ignore = '' 

    def t_comment2_error(self, token):
        token.lexer.skip(1)

    def t_comment2_eof(self, token):
        errors.throw_error(errors.LexicographicError(text="Comment (* ... *) can't end with EOF.", line=token.lineno, column=token.lexpos))


    # RULES SPECIFICATION FOR STRING STATE
    @TOKEN(r'\"')
    def t_string_end(self, token):
        if not token.lexer.backslashEscaped:
            token.value = token.lexer.string_buf
            token.type = 'STRING'
            token.lineno = token.lexer.string_lineno
            token.lexpos = token.lexer.string_lexpos
            if len(token.lexer.string_buf) > 1024:
                errors.throw_error(errors.LexicographicError(text="Strings may be at most 1024 characters long.", line=token.lineno, column=token.lexpos))        
            token.lexer.pop_state()
            return token
        else:
            token.lexer.string_buf += '"'
            token.lexer.backslashEscaped = False

    @TOKEN('[\n]')  
    def t_string_newline(self, token):
        token.lexer.lineno += 1
        if not token.lexer.backslashEscaped:
            errors.throw_error(errors.LexicographicError(text='String \'\\n\' not scaped.', line=token.lineno, column=token.lexpos))
        else:
            token.lexer.backslashEscaped = False
            token.lexer.string_buf += '\n'

    @TOKEN(r'[^\n"]')
    def t_string_whatever(self, token):
        if token.lexer.backslashEscaped:
            if token.value == 'b':
                token.lexer.string_buf += '\b'
            elif token.value == 't':
                token.lexer.string_buf += '\t'
            elif token.value == 'n':
                token.lexer.string_buf += '\n'
            elif token.value == 'f':
                token.lexer.string_buf += '\f'
            elif token.value == '\\':
                token.lexer.string_buf += '\\'
            else:
                token.lexer.string_buf += token.value
            token.lexer.backslashEscaped = False
        else:
            if token.value != '\\':
                token.lexer.string_buf += token.value
            else:
                token.lexer.backslashEscaped = True        

    def t_string_eof(self, token):
        errors.throw_error(errors.LexicographicError(text="String can't end with EOF.", line=token.lineno, column=token.lexpos))

    t_string_ignore = ''

    def t_error(self, token):
        """
        Error Handling and Reporting Rule.
        """
        token.lexpos = (token.lexpos - self.lexer.line_start)
        errors.throw_error(errors.LexicographicError(text=f'Illegal character {token.value}', line=token.lineno, column=token.lexpos))

    @TOKEN('[<][=]')
    def t_LESSEQUAL(self, token):
        token.lexpos = (token.lexpos - self.lexer.line_start)
        return token

    @TOKEN('[<][-]')
    def t_ASSIGN(self, token):
        token.lexpos = (token.lexpos - self.lexer.line_start)
        return token

    @TOKEN('[=][>]')
    def t_ARROW(self, token):
        token.lexpos = (token.lexpos - self.lexer.line_start)
        return token
    
    @TOKEN('[+]')
    def t_PLUS(self, token):
        token.lexpos = (token.lexpos - self.lexer.line_start)
        return token
    
    @TOKEN('[-]')
    def t_MINUS(self, token):
        token.lexpos = (token.lexpos - self.lexer.line_start)
        return token
    
    @TOKEN('[*]')
    def t_STAR(self, token):
        token.lexpos = (token.lexpos - self.lexer.line_start)
        return token
    
    @TOKEN('[/]')
    def t_DIV(self, token):
        token.lexpos = (token.lexpos - self.lexer.line_start)
        return token

    @TOKEN('[<]')
    def t_LESS(self, token):
        token.lexpos = (token.lexpos - self.lexer.line_start)
        return token

    @TOKEN('[=]')
    def t_EQUAL(self, token):
        token.lexpos = (token.lexpos - self.lexer.line_start)
        return token

    @TOKEN('[(]')
    def t_OBRACKET(self, token):
        token.lexpos = (token.lexpos - self.lexer.line_start)
        return token

    @TOKEN('[)]')
    def t_CBRACKET(self, token):
        token.lexpos = (token.lexpos - self.lexer.line_start)
        return token

    @TOKEN('[{]')
    def t_OCURLY(self, token):
        token.lexpos = (token.lexpos - self.lexer.line_start)
        return token

    @TOKEN('[}]')
    def t_CCURLY(self, token):
        token.lexpos = (token.lexpos - self.lexer.line_start)
        return token

    @TOKEN('[.]')
    def t_DOT(self, token):
        token.lexpos = (token.lexpos - self.lexer.line_start)
        return token

    @TOKEN('[:]')
    def t_COLON(self, token):
        token.lexpos = (token.lexpos - self.lexer.line_start)
        return token

    @TOKEN('[,]')
    def t_COMMA(self, token):
        token.lexpos = (token.lexpos - self.lexer.line_start)
        return token

    @TOKEN('[;]')
    def t_SEMICOLON(self, token):
        token.lexpos = (token.lexpos - self.lexer.line_start)
        return token

    @TOKEN('[~]')
    def t_COMPLEMENT(self, token):
        token.lexpos = (token.lexpos - self.lexer.line_start)
        return token

    @TOKEN('[@]')
    def t_AT(self, token):
        token.lexpos = (token.lexpos - self.lexer.line_start)
        return token
