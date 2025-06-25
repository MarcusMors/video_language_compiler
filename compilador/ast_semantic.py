# ast_semantic.py
"""
Fase 2: Construcción del AST, chequeo semántico y visualización
Versión **sin soporte para @extraer_audio**

• Eliminado `TokenType.VIDEO_EXTRAER_AUDIO` del conjunto `VIDEO_FUNC_TOKENS`.
• VideoFuncCall.infer_type devuelve siempre "video".
"""

import sys
from parser2 import TableDrivenParser
from enums import TokenType
from graphviz import Digraph

# ─────────────────── Nodos AST ───────────────────
class ASTNode:                                         
    """Nodo base abstracto"""
    pass


class Program(ASTNode):
    def __init__(self, statements):
        self.statements = statements

    def check_semantic(self, st):
        errors = []
        for stmt in self.statements:
            try:
                if hasattr(stmt, "check_semantic"):
                    stmt.check_semantic(st)
            except Exception as exc:
                errors.append(str(exc))
                if isinstance(stmt, VarDecl):
                    st[stmt.name] = stmt.var_type  # evitar cascada
        if errors:
            raise Exception("\n".join(errors))


class VarDecl(ASTNode):
    def __init__(self, var_type, name, init, line, col):
        self.var_type = var_type
        self.name = name
        self.init = init
        self.line = line
        self.col = col

    def check_semantic(self, st):
        if self.init:
            et = self.init.infer_type(st)
            if not (self.var_type in ("video", "audio") and et == "string") and et != self.var_type:
                raise TypeError(
                    f"Error semántico en línea {self.line}, columna {self.col}: "
                    f"no se puede asignar '{et}' a variable '{self.name}' de tipo '{self.var_type}'"
                )
        st[self.name] = self.var_type


class Assignment(ASTNode):
    def __init__(self, name, expr, line, col):
        self.name = name
        self.expr = expr
        self.line = line
        self.col = col

    def check_semantic(self, st):
        if self.name not in st:
            raise NameError(
                f"Error semántico en línea {self.line}, columna {self.col}: variable no declarada '{self.name}'"
            )
        et = self.expr.infer_type(st)
        if et != st[self.name]:
            raise TypeError(
                f"Error semántico en línea {self.line}, columna {self.col}: "
                f"no se puede asignar '{et}' a variable '{self.name}' de tipo '{st[self.name]}'"
            )


class ExportStmt(ASTNode):
    def __init__(self, name, out_file, line, col):
        self.name = name
        self.out_file = out_file
        self.line = line
        self.col = col

    def check_semantic(self, st):
        if self.name not in st:
            raise NameError(
                f"Error semántico en línea {self.line}, columna {self.col}: variable no declarada '{self.name}'"
            )


class BinaryOp(ASTNode):
    def __init__(self, op, left, right, line, col):
        self.op = op
        self.left = left
        self.right = right
        self.line = line
        self.col = col

    def infer_type(self, st):
        lt = self.left.infer_type(st)
        rt = self.right.infer_type(st)
        if lt != rt or lt not in {"int", "float"}:
            raise TypeError(
                f"Error semántico en línea {self.line}, columna {self.col}: "
                f"operación '{self.op}' no válida entre '{lt}' y '{rt}'"
            )
        return lt


class Literal(ASTNode):
    def __init__(self, value, lit_type):
        self.value = value
        self.lit_type = lit_type

    def infer_type(self, st):
        return self.lit_type


class Identifier(ASTNode):
    def __init__(self, name):
        self.name = name

    def infer_type(self, st):
        return st.get(self.name, "unknown")


class VideoFuncCall(ASTNode):
    """Nodo para cualquier @función de vídeo (sin @extraer_audio)."""
    def __init__(self, func_token, args, line, col):
        self.func = func_token.value
        self.args = args
        self.line = line
        self.col = col

    def infer_type(self, st):
        return "video"


class IfStmt(ASTNode):
    def __init__(self, condition, then_block, else_block, line, col):
        self.condition = condition
        self.then_block = then_block
        self.else_block = else_block
        self.line = line
        self.col = col
    
    def check_semantic(self, st):
        # Check that condition is boolean
        cond_type = self.condition.infer_type(st)
        if cond_type not in {"bool", "int"}:  # Allow int for flexibility
            raise TypeError(
                f"Error semántico en línea {self.line}, columna {self.col}: "
                f"la condición debe ser de tipo 'bool' o 'int', no '{cond_type}'"
            )
        # Check both blocks with their own scope
        then_st = st.copy()
        self.then_block.check_semantic(then_st)
        if self.else_block:
            else_st = st.copy()
            self.else_block.check_semantic(else_st)


class WhileStmt(ASTNode):
    def __init__(self, condition, body, line, col):
        self.condition = condition
        self.body = body
        self.line = line
        self.col = col
    
    def check_semantic(self, st):
        # Check that condition is boolean
        cond_type = self.condition.infer_type(st)
        if cond_type not in {"bool", "int"}:  # Allow int for flexibility
            raise TypeError(
                f"Error semántico en línea {self.line}, columna {self.col}: "
                f"la condición debe ser de tipo 'bool' o 'int', no '{cond_type}'"
            )
        # Check body with its own scope
        body_st = st.copy()
        self.body.check_semantic(body_st)


# ─────────────────── Construcción del AST ───────────────────
def build_ast(pt_root):
    block = pt_root.children[1]        # MAIN Block EOF
    stmtlist = block.children[1]       # lista de sentencias
    return Program(_collect_statements(stmtlist))


def _collect_statements(node):
    if not node.children:
        return []
    first = _build_statement(node.children[0])
    rest = _collect_statements(node.children[1])
    return ([first] if first else []) + rest


def _build_statement(node):
    prod = node.children[0]

    if prod.symbol == "VarDecl":
        ident_tok = prod.children[2].token
        init_expr = build_expr(prod.children[3].children[-1]) if prod.children[3].children else None
        vtype = prod.children[0].children[0].symbol.name.replace("_TYPE", "").lower()
        return VarDecl(vtype, ident_tok.value, init_expr, ident_tok.line, ident_tok.column)

    if prod.symbol == "Assignment":
        ident_tok = prod.children[0].token
        expr = build_expr(prod.children[2])
        return Assignment(ident_tok.value, expr, ident_tok.line, ident_tok.column)

    if prod.symbol == "ExportStmt":
        exp_tok = prod.children[0].token
        name_tok = prod.children[1].token
        out_tok = prod.children[3].token
        return ExportStmt(name_tok.value, out_tok.value, exp_tok.line, exp_tok.column)

    if prod.symbol == "IfStmt":
        if_tok = prod.children[0].token  # 'if' token
        condition = build_expr(prod.children[2])  # Expression between parentheses
        then_block = build_ast(prod.children[4])  # Block after condition
        # Check for optional else block
        else_block = None
        if len(prod.children) > 5 and prod.children[5].children:  # Has ElseOpt with content
            else_block = build_ast(prod.children[5].children[1])  # Block after 'else'
        return IfStmt(condition, then_block, else_block, if_tok.line, if_tok.column)

    if prod.symbol == "WhileStmt":
        while_tok = prod.children[0].token  # 'while' token
        condition = build_expr(prod.children[2])  # Expression between parentheses
        body = build_ast(prod.children[4])  # Block after condition
        return WhileStmt(condition, body, while_tok.line, while_tok.column)

    return None


# ─────────────────── Expresiones ───────────────────
VIDEO_FUNC_TOKENS = {
    TokenType.VIDEO_RESIZE,
    TokenType.VIDEO_FLIP,
    TokenType.VIDEO_VELOCIDAD,
    TokenType.VIDEO_FADEIN,
    TokenType.VIDEO_FADEOUT,
    TokenType.VIDEO_SILENCIO,
    TokenType.VIDEO_QUITAR_AUDIO,
    TokenType.VIDEO_AGREGAR_MUSICA,
    TokenType.VIDEO_CONCATENAR,
    TokenType.VIDEO_CORTAR,
}


def build_expr(node):
    if node.symbol == "FunctionCall":
        return _build_function_call(node)

    tokens = _flatten_tokens(node)
    if any(tok.type in VIDEO_FUNC_TOKENS for tok in tokens):
        fc = _find_function_call(node)
        if fc:
            return _build_function_call(fc)

    return _shunting_yard(tokens)


def _find_function_call(node):
    if node.symbol == "FunctionCall":
        return node
    for ch in node.children:
        res = _find_function_call(ch)
        if res:
            return res
    return None


def _flatten_tokens(node):
    out = []
    if hasattr(node, "token") and node.token:
        out.append(node.token)
    for ch in node.children:
        out.extend(_flatten_tokens(ch))
    return out


def _extract_exprs(node):
    if node.symbol == "Expr":
        return [node]
    acc = []
    for ch in node.children:
        acc.extend(_extract_exprs(ch))
    return acc


def _build_function_call(fc_node):
    func_tok = fc_node.children[0].token
    args_pt = fc_node.children[2]
    arg_asts = [build_expr(e) for e in _extract_exprs(args_pt)]
    return VideoFuncCall(func_tok, arg_asts, func_tok.line, func_tok.column)


# Algoritmo shunting-yard (operadores normales)
def _shunting_yard(tokens):
    if not tokens:
        return None

    output, ops = [], []
    prec = {
        TokenType.MULT: 3, TokenType.DIV: 3,
        TokenType.PLUS: 2, TokenType.MINUS: 2,
        TokenType.LT: 1,  TokenType.LE: 1,
        TokenType.GT: 1,  TokenType.GE: 1,
        TokenType.EQ: 1,  TokenType.NEQ: 1,
        TokenType.AND: 0, TokenType.OR: 0,
    }
    binops = set(prec)

    def pop():
        op = ops.pop()
        r, l = output.pop(), output.pop()
        output.append(BinaryOp(op.value, l, r, op.line, op.column))

    for tok in tokens:
        if tok.type == TokenType.INT_LITERAL:
            output.append(Literal(tok.value, "int"))
        elif tok.type == TokenType.FLOAT_LITERAL:
            output.append(Literal(tok.value, "float"))
        elif tok.type == TokenType.STRING_LITERAL:
            output.append(Literal(tok.value, "string"))
        elif tok.type == TokenType.IDENTIFIER:
            output.append(Identifier(tok.value))
        elif tok.type == TokenType.LPAREN:
            ops.append(tok)
        elif tok.type == TokenType.RPAREN:
            while ops and ops[-1].type != TokenType.LPAREN:
                pop()
            if ops:
                ops.pop()
        elif tok.type in binops:
            while ops and ops[-1].type in binops and prec[ops[-1].type] >= prec[tok.type]:
                pop()
            ops.append(tok)

    while ops:
        pop()

    return output[-1] if output else None


# ─────────────────── Visualización ───────────────────
def visualize_ast(ast, fname="ast"):
    dot = Digraph("AST", format="png")

    def walk(n, parent=None):
        uid = str(id(n))
        label = n.__class__.__name__
        if isinstance(n, VarDecl):
            label += f"\\n{n.name}:{n.var_type}"
        elif isinstance(n, Identifier):
            label += f"\\n{n.name}"
        elif isinstance(n, Literal):
            label += f"\\n{n.value}"
        elif isinstance(n, BinaryOp):
            label += f"\\n{n.op}"
        elif isinstance(n, VideoFuncCall):
            label += f"\\n{n.func}"
        dot.node(uid, label)
        if parent:
            dot.edge(parent, uid)

        children = []
        if isinstance(n, Program):
            children = n.statements
        elif isinstance(n, VarDecl) and n.init:
            children = [n.init]
        elif isinstance(n, Assignment):
            children = [n.expr]
        elif isinstance(n, BinaryOp):
            children = [n.left, n.right]
        elif isinstance(n, VideoFuncCall):
            children = n.args
        elif isinstance(n, IfStmt):
            children = [n.condition, n.then_block]
            if n.else_block:
                children.append(n.else_block)
        elif isinstance(n, WhileStmt):
            children = [n.condition, n.body]

        for ch in children:
            walk(ch, uid)

    walk(ast)
    dot.render(fname, cleanup=True)
    print(f"AST visualizado en {fname}.png")


# ─────────────────── Main ───────────────────
def main():
    if len(sys.argv) != 2:
        print("Uso: python ast_semantic.py <archivo_fuente>")
        sys.exit(1)

    source = open(sys.argv[1], encoding="utf-8").read()
    parser = TableDrivenParser(source)

    try:
        pt = parser.parse(verbose=False)
    except Exception as e:
        print(e)
        sys.exit(1)

    ast = build_ast(pt)
    st = {}
    try:
        ast.check_semantic(st)
    except Exception as e:
        print("\n--- ERRORES SEMÁNTICOS ---")
        for err in str(e).split("\n"):
            print("  -", err)
        sys.exit(1)

    print("Análisis semántico OK. Generando AST…")
    visualize_ast(ast)


if __name__ == "__main__":
    main()
