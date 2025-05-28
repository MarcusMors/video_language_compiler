#!/usr/bin/env python3


import sys
from dataclasses import dataclass, field
from typing import List, Union, Optional
from graphviz import Digraph

from lexer import Lexer
from enums import Token, TokenType
from grammar_def import PARSING_TABLE, START_SYMBOL, EPSILON

# ─── Nodo del arbol de parseo 
class ParseTreeNode:
    id:      int
    label:   str
    token:   Optional[Token] = None
    children: List['ParseTreeNode'] = field(default_factory=list)

# ─── Clase visualizadora 
class ParseTreeVisualizer:
    def __init__(self):
        self.node_counter = 0

    def _new_node(self, label: str, token: Token = None) -> ParseTreeNode:
        self.node_counter += 1
        return ParseTreeNode(id=self.node_counter, label=label, token=token)

    def build_tree(self, tokens: List[Token]) -> ParseTreeNode:
        # EOF
        if not tokens or tokens[-1].type != TokenType.EOF:
            last = tokens[-1] if tokens else None
            tokens.append(Token(TokenType.EOF, "", 
                                last.line if last else 0, 
                                last.column if last else 0))

        pos      = 0
        actual   = tokens[pos]
        # Raíz del árbol
        self.node_counter = 0
        root      = self._new_node(START_SYMBOL)
        # Pilas paralelas
        symbol_stack = [START_SYMBOL]
        node_stack   = [root]

        # Bucle principal
        while symbol_stack:
            sym  = symbol_stack.pop()
            node = node_stack.pop()

            # ── Caso A: TERMINAL ────────────────────
            if isinstance(sym, TokenType):
                if actual.type == sym:
                    leaf = self._new_node(token_repr(actual.type, actual.value), actual)
                    node.children.append(leaf)
                    pos += 1
                    actual = tokens[pos] if pos < len(tokens) else tokens[-1]
                # si no coincide, simplemente descartamos actual
                continue

            # ── Caso B: EPSILON ─────────────────────
            if sym == EPSILON:
                # omitimos nódulo ε
                continue

            # ── Caso C: NO-TERMINAL ─────────────────
            prod = PARSING_TABLE.get(sym, {}).get(actual.type)
            if prod is None:
                # no hay producción → recuperamos descartando token
                pos += 1
                actual = tokens[pos] if pos < len(tokens) else tokens[-1]
                continue

            # Creamos un hijo por cada símbolo de la producción
            children = []
            for s in prod:
                if isinstance(s, TokenType):
                    lab = s.name
                else:
                    lab = str(s)
                child = self._new_node(lab)
                children.append(child)
                node.children.append(child)

            # Apilamos en orden inverso
            for s, child in zip(reversed(prod), reversed(children)):
                if s != EPSILON:
                    symbol_stack.append(s)
                    node_stack.append(child)

        return root

    def print_tree(self, node: ParseTreeNode, indent: int = 0) -> None:
        """Imprime el árbol en consola con indentación."""
        pref = "  " * indent
        print(f"{pref}{node.label}")
        for c in node.children:
            self.print_tree(c, indent + 1)

    def visualize(self, root: ParseTreeNode, filename: str = 'parse_tree'):
        """Genera PNG con Graphviz."""
        dot = Digraph(comment='Parse Tree', format='png')
        self._add_nodes(dot, root)
        dot.render(filename, cleanup=True)
        print(f"Árbol de parseo guardado en {filename}.png")

    def _add_nodes(self, dot: Digraph, node: ParseTreeNode):
        # estilo distinto para hojas (tokens) y nodos internos
        if node.token:
            dot.node(str(node.id), node.label,
                     shape='ellipse', style='filled', color='lightblue2')
        else:
            dot.node(str(node.id), node.label,
                     shape='box', style='filled', color='lightcoral')
        for ch in node.children:
            self._add_nodes(dot, ch)
            dot.edge(str(node.id), str(ch.id))

# ─── Representación de un token en etiqueta de nodo ────────────────────────
def token_repr(tt: TokenType, lex: str) -> str:
    if tt == TokenType.IDENTIFIER:
        return f"ID:{lex}"
    if tt in {TokenType.INT_LITERAL, TokenType.FLOAT_LITERAL,
              TokenType.STRING_LITERAL, TokenType.BOOL_LITERAL}:
        return f"{tt.name}:{lex}"
    return tt.name

# ─── Driver ────────────────────────────────────────────────────────────────
def main():
    if len(sys.argv) != 2:
        print("Uso: python parse_tree.py <archivo.txt>")
        sys.exit(1)

    ruta = sys.argv[1]
    try:
        src = open(ruta, encoding='utf-8').read()
    except FileNotFoundError:
        print(f"Error: no existe '{ruta}'")
        sys.exit(1)

    #lexer
    lexer = Lexer(src)
    tokens = lexer.tokenize()
    if lexer.errors:
        print("✗ Errores léxicos:")
        for e in lexer.errors:
            print("  " + e)
        sys.exit(1)

    #built tree
    visualizer = ParseTreeVisualizer()
    root = visualizer.build_tree(tokens)

    #consola
    print("\n=== Árbol de parseo (indentado) ===")
    visualizer.print_tree(root)

    #png
    visualizer.visualize(root, filename=ruta.split('.')[0] + '_parse_tree')

if __name__ == "__main__":
    main()
