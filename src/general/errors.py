

class Error:
    def __init__(self, text, line=0, column=0):
        self.text = text
        self.line = line
        self.column = column

    @property
    def classname(self):
        return self.__class__.__name__

    def to_readable(self):
        return f'({self.line},{self.column}) - {self.classname}: {self.text}'

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return str(self.to_readable())

class CompilerError(Error):
    '''
    Se reporta al detectar alguna anomalia con la entrada del compilador.
    '''
    def __init__(self, text):
        super().__init__(text)

class LexicographicError(Error):
    '''
    Errores detectados en el lexer.
    '''
    def __init__(self, text, line=0, column=0):
        super().__init__(text, line, column)

class SyntacticError(Error):
    '''
    Errores detectados en el parser.
    '''
    def __init__(self, text, line=0, column=0):
        super().__init__(text, line, column)

class SemanticError(Error):
    '''
    Se reporta para cualquier error semantico excepto los 
    especificados a continuacion. 
    '''
    def __init__(self, text, line=0, column=0):
        super().__init__(text, line, column)

class NameError(SemanticError):
    '''
    Se reporta cuando un identificado se referencia en un
    ambito en el que no es visible.
    '''
    def __init__(self, text, line=0, column=0):
        super().__init__(text, line, column)

class TypeError(SemanticError):
    '''
    Se reporta al detectar uno de los siguientes errores de
    tipo:
    - Incompatibilidad de tipos entre rvalue y lvalue.
    - Operacion no definida entre objetos de diferentes tipos.
    - Tipo referenciado pero no definido.
    '''
    def __init__(self, text, line=0, column=0):
        super().__init__(text, line, column)

class AttributeError(SemanticError):
    '''
    Se reporta cuando un atributo o método se referencia pero
    no está definido.
    '''
    def __init__(self, text, line=0, column=0):
        super().__init__(text, line, column)


def throw_error(error):
    print(error)
    exit(1)
