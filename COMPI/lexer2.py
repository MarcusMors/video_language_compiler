# lexer2.py

"""
Analizador léxico del lenguaje de edición de video.

Convierte el texto fuente en una secuencia de tokens utilizando las
tablas definidas en `enums.py`. Se reportan errores léxicos
manteniendo información de línea y columna.
"""

import sys
from typing import List, Optional
from enums import TokenType, Token, KEYWORDS, symbols, compound_ops, VIDEO_FUNCS

class Lexer:
    """Clase encargada de recorrer el texto fuente y producir tokens."""

    def __init__(self, text: str) -> None:
        self.text = text
        self.pos = 0            # índice actual en la cadena
        self.line = 1           # línea actual
        self.column = 1         # columna actual
        self.errors: List[str] = []  # lista de mensajes de error

    def _peek(self) -> str:
        return self.text[self.pos] if self.pos < len(self.text) else ''

    def _advance(self) -> str:
        ch = self._peek()
        if ch:
            self.pos += 1
            if ch == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
        return ch

    def _skip_whitespace(self) -> None:
        while (ch := self._peek()) and ch in ' \t\r\n':
            self._advance()

    def _number(self) -> Optional[Token]:
        start, ln, col = self.pos, self.line, self.column
        has_dot = False
        while True:
            ch = self._peek()
            if ch.isdigit():
                self._advance()
            elif ch == '.':
                if has_dot:
                    # Número mal formado como 1.2.3
                    while (c := self._peek()) and (c.isdigit() or c == '.'):
                        self._advance()
                    lex = self.text[start:self.pos]
                    self.errors.append(f"Malformed number '{lex}' at line {ln}, column {col}")
                    return None
                has_dot = True
                self._advance()
            else:
                break

        lex = self.text[start:self.pos]
        # Si empieza con dígito pero sigue con letra: identificador inválido
        if (nxt := self._peek()).isalpha() or nxt == '_':
            while (c := self._peek()) and (c.isalnum() or c == '_'):
                self._advance()
            lex = self.text[start:self.pos]
            self.errors.append(f"Invalid identifier '{lex}' at line {ln}, column {col}")
            return None

        tok_type = TokenType.FLOAT_LITERAL if has_dot else TokenType.INT_LITERAL
        return Token(tok_type, lex, ln, col)

    def _string(self) -> Optional[Token]:
        ln, col = self.line, self.column
        self._advance()  # consume opening "
        start = self.pos
        while True:
            ch = self._peek()
            if not ch:
                self.errors.append(f"Unterminated string at line {ln}, column {col}")
                return None
            if ch == '"':
                self._advance()  # consume closing "
                lex = self.text[start:self.pos]
                return Token(TokenType.STRING_LITERAL, lex, ln, col)
            if ch == '\n':
                self.errors.append(f"Unterminated string at line {ln}, column {col}")
                return None
            self._advance()

    def _identifier(self) -> Token:
        start, ln, col = self.pos, self.line, self.column
        while (ch := self._peek()) and (ch.isalnum() or ch == '_'):
            self._advance()
        lex = self.text[start:self.pos]
        tok_type = KEYWORDS.get(lex, TokenType.IDENTIFIER)
        return Token(tok_type, lex, ln, col)

    def _video_function(self) -> Optional[Token]:
        ln, col = self.line, self.column
        self._advance()  # consume '@'
        if not (self._peek().isalpha() or self._peek() == '_'):
            invalid = '@' + self._peek()
            self.errors.append(f"Invalid character '{invalid}' at line {ln}, column {col}")
            if self._peek():
                self._advance()
            return None
        start = self.pos
        while (ch := self._peek()) and (ch.isalnum() or ch == '_'):
            self._advance()
        lex = '@' + self.text[start:self.pos]
        tok_type = VIDEO_FUNCS.get(lex)
        if tok_type is None:
            self.errors.append(f"Invalid function '{lex}' at line {ln}, column {col}")
            return None
        return Token(tok_type, lex, ln, col)

    def tokenize(self) -> List[Token]:
        tokens: List[Token] = []
        while self.pos < len(self.text):
            self._skip_whitespace()
            if self.pos >= len(self.text):
                break

            ch = self._peek()
            ln, col = self.line, self.column

            # Comentarios
            if ch == '/' and self.text.startswith('//', self.pos):
                while self._peek() and self._peek() != '\n':
                    self._advance()
                continue
            if ch == '/' and self.text.startswith('/*', self.pos):
                self.errors.append(f"Malformed comment at line {ln}, column {col}")
                self._advance(); self._advance()
                while self._peek() and not self.text.startswith('*/', self.pos):
                    self._advance()
                if self.text.startswith('*/', self.pos):
                    self._advance(); self._advance()
                continue

            # Números
            if ch.isdigit():
                tok = self._number()
                if tok:
                    tokens.append(tok)
                continue

            # Cadenas
            if ch == '"':
                tok = self._string()
                if tok:
                    tokens.append(tok)
                continue

            # Identificadores o keywords
            if ch.isalpha() or ch == '_':
                tok = self._identifier()
                tokens.append(tok)
                continue

            # Funciones de video
            if ch == '@':
                tok = self._video_function()
                if tok:
                    tokens.append(tok)
                continue

            # Operadores compuestos
            two = self.text[self.pos:self.pos+2]
            if two in compound_ops:
                self._advance(); self._advance()
                tokens.append(Token(compound_ops[two], two, ln, col))
                continue

            # Símbolos y operadores simples (incluye +, -, *, /, =, <, >, etc.)
            if ch in symbols:
                self._advance()
                tokens.append(Token(symbols[ch], ch, ln, col))
                continue

            # Carácter inválido
            self.errors.append(f"Invalid character '{ch}' at line {ln}, column {col}")
            self._advance()

        tokens.append(Token(TokenType.EOF, '', self.line, self.column))
        return tokens


def main() -> None:
    if len(sys.argv) != 2:
        print("Uso: python lexer2.py <archivo.txt>")
        return
    path = sys.argv[1]
    try:
        src = open(path, encoding='utf-8').read()
    except FileNotFoundError:
        print(f"Error: no existe '{path}'")
        return

    lexer = Lexer(src)
    tokens = lexer.tokenize()
    print("--- TOKENS ---")
    for t in tokens:
        print(t if t.type != TokenType.EOF else "EOF")
    if lexer.errors:
        print("\n--- LEXICAL ERRORS ---")
        for err in lexer.errors:
            print(err)


if __name__ == '__main__':
    main()
