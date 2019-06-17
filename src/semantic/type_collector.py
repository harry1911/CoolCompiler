
from general import visitor, errors
from general import ast_hierarchy as ast
from .enviroment import Enviroment


class TypeCollectorVisitor:
    def __init__(self):
        self.enviroment = None
        self.basic_classes = ["Object", "IO", "Int", "String", "Bool"]

    @visitor.on('node')
    def visit(self, node):
        pass

    @visitor.when(ast.ProgramNode)
    def visit(self, node):
        self.enviroment = Enviroment()

        for _class in node.class_list:
            self.visit(_class)

    @visitor.when(ast.ClassNode)
    def visit(self, node):
        ans = self.enviroment.create_type(node.name, node.parent)
        if ans is None:
            errors.throw_error(errors.SemanticError(text=f"Class '{node.name}' may not be redefined", line=node.line, column=node.column))
            
