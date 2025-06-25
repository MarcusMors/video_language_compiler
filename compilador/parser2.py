# parse_tree.py

"""
Fase 1: Construcción y visualización del árbol de análisis sintáctico (parse tree).
- Imprime en terminal cada paso de MATCH / EXPAND / RULE con formato tabulado.
- Muestra EPSILON (ε) cuando la producción la contiene.
- Al final genera `parsetree.png` con la estructura completa.
"""

import sys
from collections import deque
from enums import TokenType
from lexer2 import Lexer
from grammar_def2 import PARSING_TABLE, EPSILON, START_SYMBOL
from graphviz import Digraph


class ParseNode:
    """Nodo del parse tree: puede ser un terminal (TokenType) o un no-terminal (str)."""
    def __init__(self, symbol, token=None):
        self.symbol = symbol      # TokenType o nombre del no-terminal
        self.token  = token       # Token emparejado si es terminal
        self.children = []        # Hijos ParseNode

    def __repr__(self):
        return f"ParseNode({self.symbol}, children={len(self.children)})"

class TableDrivenParser:
    """Parser LL(1) con salida paso a paso legible y tabulada."""
    def __init__(self, src: str):
        # Inicializa el lexer y lista de tokens
        self.lexer  = Lexer(src)
        self.tokens = self.lexer.tokenize()
        self.pos    = 0
        self.current= self.tokens[0]

    def advance(self):
        """Avanza al siguiente token en la lista."""
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current = self.tokens[self.pos]

    def parse(self, verbose: bool = True) -> ParseNode:
        """
        Construye el parse tree:
          - Si verbose=True, muestra:
              [MATCH] <línea,columna>  Terminal esperado … Token actual …
              [EXPAND] <no-terminal>    Lookahead …
              [RULE]   Regla elegida (incluye ε)
        """
        root  = ParseNode(START_SYMBOL)
        stack = deque([root])

        if verbose:
            print("=== Inicio del parser LL(1) paso a paso ===\n")

        while stack:
            node = stack.pop()
            sym  = node.symbol

            # ——— Caso terminal ———
            if isinstance(sym, TokenType):
                if verbose:
                    print(f"[MATCH]    Línea {self.current.line:>3}, Col {self.current.column:>3}  "
                          f"Terminal esperado: {sym.name:<15}  "
                          f"Token actual: {self.current.type.name:<15} ('{self.current.value}')")
                if sym == self.current.type:
                    node.token = self.current
                    self.advance()
                else:
                    ln, col = self.current.line, self.current.column
                    raise SyntaxError(
                        f"Error sintáctico en línea {ln}, columna {col}: "
                        f"se esperaba '{sym.name}', vino '{self.current.type.name}'"
                    )
                continue

            # ——— Caso no-terminal ———
            if verbose:
                print(f"[EXPAND]   No-terminal: {sym:<15}  Lookahead: {self.current.type.name:<15} ('{self.current.value}')")
            row = PARSING_TABLE.get(sym)
            if row is None:
                raise SyntaxError(f"No existe fila LL(1) para el no-terminal: {sym}")

            prod = row.get(self.current.type)
            if prod is None:
                esperados = ', '.join(
                    (t.name if isinstance(t, TokenType) else t)
                    for t in row.keys()
                )
                ln, col = self.current.line, self.current.column
                raise SyntaxError(
                    f"Error sintáctico en línea {ln}, columna {col}: "
                    f"token inesperado '{self.current.type.name}'. Se esperaba uno de: {esperados}"
                )

            # Formatear la parte derecha mostrando ε
            rhs = []
            for p in prod:
                if p == EPSILON:
                    rhs.append('ε')
                else:
                    rhs.append(p.name if isinstance(p, TokenType) else p)

            if verbose:
                print(f"[RULE]     {sym:<15} -> {' '.join(rhs)}\n")

            # Crear nodos hijos (omitimos EPSILON en el árbol)
            node.children = [ParseNode(p) for p in prod if p != EPSILON]
            # Apilar en orden inverso
            for child in reversed(node.children):
                stack.append(child)

        if verbose:
            print("=== Fin del parser paso a paso ===\n")
        return root

def visualize_parse_tree(root: ParseNode, outname: str = 'parsetree'):
    """
    Dibuja con Graphviz el parse tree completo y guarda `outname.png`.
    Cada nodo muestra el símbolo; las hojas también el valor del token.
    """
    dot = Digraph('ParseTree', format='png')
    def visit(n: ParseNode, parent_id=None):
        uid   = str(id(n))
        label = str(n.symbol)
        if n.token:
            label += f"\n{n.token.value}"
        
        # Node styling based on symbol type
        style = 'filled'
        fillcolor = "#f4ecd8"  # default color
        penwidth = '1.0'  # default border width
        
        # Control flow and loop styling
        if isinstance(n.symbol, TokenType):
            if n.symbol in (TokenType.IF, TokenType.ELSE):
                fillcolor = "#82c7a5"  # Control flow color
            elif n.symbol == TokenType.WHILE:
                fillcolor = "#d9a6ff"  # Loop color
                penwidth = '2.0'  # Bold border for loops
        
        dot.node(uid, label, style=style, fillcolor=fillcolor, penwidth=penwidth)
        
        if parent_id:
            dot.edge(parent_id, uid)
        for ch in n.children:
            visit(ch, uid)

    visit(root)
    
    # dot.attr(bgcolor='#f4ecd8') #light sepia
    dot.attr(bgcolor='#7d540d') #dark yellow
    
    dot.render(outname, cleanup=True)
    print(f"Parse tree visualizado en {outname}.png")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python parse_tree.py <archivo_fuente>")
        sys.exit(1)

    src = open(sys.argv[1], encoding='utf-8').read()

    # 0) Análisis léxico previo
    lexer = Lexer(src)
    _ = lexer.tokenize()
    if lexer.errors:
        print("Errores léxicos detectados, abortando parser:")
        for e in lexer.errors:
            print("  -", e)
        sys.exit(1)

    # 1) Parse LL(1) paso a paso
    parser = TableDrivenParser(src)
    try:
        pt_root = parser.parse(verbose=True)
    except Exception as e:
        print(e)
        sys.exit(1)

    # 2) Visualizar árbol generado
    visualize_parse_tree(pt_root)
    print("Análisis sintáctico completado sin errores.")
