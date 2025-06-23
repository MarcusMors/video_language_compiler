# parser2.py

from collections import deque
from enums import TokenType
from lexer2 import Lexer
from grammar_def2 import PARSING_TABLE, EPSILON, START_SYMBOL

# -------------------------------------------------
# Parse tree node
# -------------------------------------------------
class ParseNode:
    def __init__(self, symbol, token=None):
        self.symbol = symbol      # TokenType or str
        self.token = token        # Token instance if terminal
        self.children = []        # list of ParseNode
    def __repr__(self):
        return f"ParseNode({self.symbol}, children={len(self.children)})"

# -------------------------------------------------
# AST node definitions with semantic methods
# -------------------------------------------------
class ASTNode:
    pass

class Program(ASTNode):
    def __init__(self, statements):
        self.statements = statements  # list of ASTNode

class VarDecl(ASTNode):
    def __init__(self, var_type, name, init_expr, line, col):
        self.var_type = var_type
        self.name = name
        self.init = init_expr
        self.line = line
        self.col = col

    def check_semantic(self, symbol_table):
        # inicialización opcional
        if self.init:
            et = self.init.infer_type(symbol_table)
            if et != self.var_type:
                raise TypeError(
                    f"Error semántico en línea {self.line}, columna {self.col}: "
                    f"no se puede asignar '{et}' a variable '{self.name}' de tipo '{self.var_type}'"
                )
        # registrar variable
        symbol_table[self.name] = self.var_type

class Assignment(ASTNode):
    def __init__(self, name, expr, line, col):
        self.name = name
        self.expr = expr
        self.line = line
        self.col = col

    def check_semantic(self, symbol_table):
        if self.name not in symbol_table:
            raise NameError(
                f"Error semántico en línea {self.line}, columna {self.col}: "
                f"variable no declarada '{self.name}'"
            )
        et = self.expr.infer_type(symbol_table)
        if et != symbol_table[self.name]:
            raise TypeError(
                f"Error semántico en línea {self.line}, columna {self.col}: "
                f"no se puede asignar '{et}' a variable '{self.name}' de tipo '{symbol_table[self.name]}'"
            )

class BinaryOp(ASTNode):
    def __init__(self, op, left, right, line, col):
        self.op = op
        self.left = left
        self.right = right
        self.line = line
        self.col = col

    def infer_type(self, symbol_table):
        lt = self.left.infer_type(symbol_table)
        rt = self.right.infer_type(symbol_table)
        if lt != rt or lt not in {'int','float'}:
            raise TypeError(
                f"Error semántico en línea {self.line}, columna {self.col}: "
                f"operación '{self.op}' no válida entre '{lt}' y '{rt}'"
            )
        return lt

class Literal(ASTNode):
    def __init__(self, value, lit_type):
        self.value = value
        self.lit_type = lit_type
    def infer_type(self, symbol_table):
        return self.lit_type

class Identifier(ASTNode):
    def __init__(self, name):
        self.name = name
    def infer_type(self, symbol_table):
        return symbol_table.get(self.name, 'unknown')

# -------------------------------------------------
# Parser table-driven LL(1)
# -------------------------------------------------
class TableDrivenParser:
    def __init__(self, source_code: str):
        self.lexer = Lexer(source_code)
        self.tokens = self.lexer.tokenize()
        self.pos = 0
        self.current = self.tokens[0]

    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current = self.tokens[self.pos]

    def parse(self) -> ParseNode:
        root = ParseNode(START_SYMBOL)
        stack = deque([root])
        while stack:
            node = stack.pop()
            sym = node.symbol
            if isinstance(sym, TokenType):
                if sym == self.current.type:
                    node.token = self.current
                    self.advance()
                else:
                    ln, col = self.current.line, self.current.column
                    raise SyntaxError(
                        f"Error sintáctico en línea {ln}, columna {col}: "
                        f"Se esperaba '{sym.name}', pero vino '{self.current.type.name}'"
                    )
                continue
            row = PARSING_TABLE.get(sym)
            if row is None:
                raise SyntaxError(f"No terminal desconocido: {sym}")
            prod = row.get(self.current.type)
            if prod is None:
                expected = ', '.join(sorted(t.name for t in row.keys()))
                ln, col = self.current.line, self.current.column
                raise SyntaxError(
                    f"Error sintáctico en línea {ln}, columna {col}: "
                    f"token inesperado '{self.current.type.name}'. "
                    f"Se esperaba uno de: {expected}"
                )
            children = [ParseNode(p) for p in prod if p != EPSILON]
            node.children = children
            for child in reversed(children):
                stack.append(child)
        return root

# -------------------------------------------------
# Build AST from parse tree
# -------------------------------------------------
def build_ast(node: ParseNode) -> Program:
    block = node.children[1]            # MAIN Block EOF
    stmt_list = block.children[1]      # StmtList
    statements = collect_statements(stmt_list)
    return Program(statements)

def collect_statements(stmt_list_node: ParseNode):
    if not stmt_list_node.children:
        return []
    stmt = build_statement(stmt_list_node.children[0])
    rest = collect_statements(stmt_list_node.children[1])
    return ([stmt] if stmt else []) + rest

def build_statement(stmt_node: ParseNode):
    child = stmt_node.children[0]
    if child.symbol == 'VarDecl':
        # VarDecl → Type COLON IDENT VarInitOpt
        name_token = child.children[2].token
        ln, col = name_token.line, name_token.column
        return VarDecl(
            child.children[0].children[0].symbol.name.replace('_TYPE','').lower(),
            name_token.value,
            build_expr(child.children[3].children[-1]) if child.children[3].children else None,
            ln, col
        )
    if child.symbol == 'Assignment':
        # Assignment → IDENT ASSIGN Expr
        name_token = child.children[0].token
        ln, col = name_token.line, name_token.column
        return Assignment(
            name_token.value,
            build_expr(child.children[2]),
            ln, col
        )
    return None

def build_expr(node: ParseNode):
    if node.symbol in ('AddOp','MulOp') and len(node.children)==3:
        op_token = node.children[1].token
        ln, col = op_token.line, op_token.column
        return BinaryOp(
            op_token.value,
            build_expr(node.children[0]),
            build_expr(node.children[2]),
            ln, col
        )
    if isinstance(node.symbol, TokenType):
        tok = node.token
        if node.symbol == TokenType.INT_LITERAL:
            return Literal(tok.value, 'int')
        if node.symbol == TokenType.FLOAT_LITERAL:
            return Literal(tok.value, 'float')
        if node.symbol == TokenType.STRING_LITERAL:
            return Literal(tok.value, 'string')
        if node.symbol == TokenType.IDENTIFIER:
            return Identifier(tok.value)
    for c in node.children:
        ast = build_expr(c)
        if ast:
            return ast
    return None

# -------------------------------------------------
# Analyzer: parse, AST, semantic (collect all errors)
# -------------------------------------------------
class Analyzer:
    def __init__(self, source):
        self.source = source

    def run(self):
        try:
            pt = TableDrivenParser(self.source).parse()
            ast = build_ast(pt)
        except Exception as e:
            print(e)
            return
        errors = []
        symbol_table = {}
        for stmt in ast.statements:
            try:
                stmt.check_semantic(symbol_table)
            except Exception as e:
                errors.append(str(e))
                if isinstance(stmt, VarDecl):
                    symbol_table[stmt.name] = stmt.var_type
        if errors:
            for err in errors:
                print(err)
            return
        print('Análisis exitoso con AST')

# -------------------------------------------------
# Main
# -------------------------------------------------
if __name__ == '__main__':
    import sys
    src = open(sys.argv[1], encoding='utf-8').read()
    Analyzer(src).run()
