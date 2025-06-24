# lexer2.py

"""
Analizador léxico para el mini-lenguaje de edición de video/audio.

Convierte el texto fuente en tokens, detecta errores léxicos
y, al finalizar, informa del resultado.
"""

import sys
from typing import List, Optional

from enums import (
    TokenType,    # enum de tipos de token
    Token,        # clase Token(tipo, valor, línea, columna)
    KEYWORDS,     # mapeo de palabras reservadas a TokenType
    symbols,      # mapeo de símbolos simples a TokenType
    compound_ops, # mapeo de operadores de dos caracteres a TokenType
    VIDEO_FUNCS   # mapeo de nombres @función a TokenType
)

class Lexer:
    """Recorre el texto y genera la lista de tokens, acumulando errores."""

    def __init__(self, text: str) -> None:
        # Texto fuente completo
        self.text = text
        # Posición actual en la cadena
        self.pos = 0
        # Contadores de línea y columna para mensajes
        self.line = 1
        self.column = 1
        # Lista de errores léxicos (mensajes)
        self.errors: List[str] = []

    def _peek(self) -> str:
        """Devuelve el carácter en self.pos (o cadena vacía si EOF)."""
        return self.text[self.pos] if self.pos < len(self.text) else ''

    def _advance(self) -> str:
        """
        Avanza una posición:
         - Actualiza línea/columna si ve '\n'.
         - Devuelve el carácter consumido.
        """
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
        """Saltar espacios, tabs y saltos de línea."""
        while (ch := self._peek()) and ch in ' \t\r\n':
            self._advance()

    def _number(self) -> Optional[Token]:
        """
        Reconoce un literal numérico (int o float).
        Maneja un único punto decimal y reporta números mal formados.
        """
        start_pos, ln, col = self.pos, self.line, self.column
        has_dot = False

        # Consumir dígitos y, a lo más, un punto
        while True:
            ch = self._peek()
            if ch.isdigit():
                self._advance()
            elif ch == '.':
                if has_dot:
                    # Mal formado: más de un punto
                    while (c := self._peek()) and (c.isdigit() or c == '.'):
                        self._advance()
                    lex = self.text[start_pos:self.pos]
                    self.errors.append(f"Malformed number '{lex}' at line {ln}, column {col}")
                    return None
                has_dot = True
                self._advance()
            else:
                break

        lex = self.text[start_pos:self.pos]
        # Si tras el número viene letra/_ → identificador inválido
        if (nxt := self._peek()).isalpha() or nxt == '_':
            while (c := self._peek()) and (c.isalnum() or c == '_'):
                self._advance()
            lex = self.text[start_pos:self.pos]
            self.errors.append(f"Invalid identifier '{lex}' at line {ln}, column {col}")
            return None

        tok_type = TokenType.FLOAT_LITERAL if has_dot else TokenType.INT_LITERAL
        return Token(tok_type, lex, ln, col)

    def _string(self) -> Optional[Token]:
        """
        Reconoce literales de cadena encerradas en dobles comillas.
        Reporta si faltan las comillas de cierre.
        """
        ln, col = self.line, self.column
        # Consume la comilla de apertura
        self._advance()
        start = self.pos

        while True:
            ch = self._peek()
            if not ch:
                self.errors.append(f"Unterminated string at line {ln}, column {col}")
                return None
            if ch == '"':
                # Cierre encontrado
                self._advance()
                lex = self.text[start:self.pos]
                return Token(TokenType.STRING_LITERAL, lex, ln, col)
            if ch == '\n':
                # String no puede contener salto de línea
                self.errors.append(f"Unterminated string at line {ln}, column {col}")
                return None
            self._advance()

    def _identifier(self) -> Token:
        """
        Reconoce identificadores y palabras reservadas.
        Un identificador: letra/_ seguido de letras/dígitos/_.
        """
        start, ln, col = self.pos, self.line, self.column
        while (ch := self._peek()) and (ch.isalnum() or ch == '_'):
            self._advance()
        lex = self.text[start:self.pos]
        # Si coincide con palabra reservada, le asigna otro TokenType
        tok_type = KEYWORDS.get(lex, TokenType.IDENTIFIER)
        return Token(tok_type, lex, ln, col)

    def _video_function(self) -> Optional[Token]:
        """
        Reconoce funciones de video/audio prefijadas con @.
        Ej.: @resize, @flip, etc. Mapea a TokenType.VIDEO_RESIZE…
        """
        ln, col = self.line, self.column
        # Consumir la '@'
        self._advance()
        # Debe seguir una letra o '_'
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
        """
        Recorre todo el texto fuente y genera la lista de tokens.
        - Detecta y acumula errores léxicos en self.errors.
        - Al final, añade un token EOF.
        """
        tokens: List[Token] = []
        while self.pos < len(self.text):
            self._skip_whitespace()
            if self.pos >= len(self.text):
                break

            ch = self._peek()
            ln, col = self.line, self.column

            # 1) Comentarios // …
            if ch == '/' and self.text.startswith('//', self.pos):
                while self._peek() and self._peek() != '\n':
                    self._advance()
                continue

            # 2) Comentarios mal formados /* … */
            if ch == '/' and self.text.startswith('/*', self.pos):
                self.errors.append(f"Malformed comment at line {ln}, column {col}")
                # saltar '/*'
                self._advance(); self._advance()
                # hasta '*/' o EOF
                while self._peek() and not self.text.startswith('*/', self.pos):
                    self._advance()
                if self.text.startswith('*/', self.pos):
                    self._advance(); self._advance()
                continue

            # 3) Literales numéricas
            if ch.isdigit():
                tok = self._number()
                if tok:
                    tokens.append(tok)
                continue

            # 4) Literales de cadena
            if ch == '"':
                tok = self._string()
                if tok:
                    tokens.append(tok)
                continue

            # 5) Identificadores o keywords
            if ch.isalpha() or ch == '_':
                tok = self._identifier()
                tokens.append(tok)
                continue

            # 6) Funciones de video/audio con '@'
            if ch == '@':
                tok = self._video_function()
                if tok:
                    tokens.append(tok)
                continue

            # 7) Operadores de dos caracteres (==, !=, <=, >=, &&, ||, etc.)
            two = self.text[self.pos:self.pos+2]
            if two in compound_ops:
                self._advance(); self._advance()
                tokens.append(Token(compound_ops[two], two, ln, col))
                continue

            # 8) Símbolos simples (p.ej. ; , ( ) { } + - * / < > = : …)
            if ch in symbols:
                self._advance()
                tokens.append(Token(symbols[ch], ch, ln, col))
                continue

            # 9) Carácter inválido
            self.errors.append(f"Invalid character '{ch}' at line {ln}, column {col}")
            self._advance()

        # Añadir token EOF al final
        tokens.append(Token(TokenType.EOF, '', self.line, self.column))
        return tokens


def main() -> None:
    """Punto de entrada cuando se ejecuta 'python lexer2.py archivo'."""
    if len(sys.argv) != 2:
        print("Uso: python lexer2.py <archivo.txt>")
        sys.exit(1)

    path = sys.argv[1]
    try:
        src = open(path, encoding='utf-8').read()
    except FileNotFoundError:
        print(f"Error: no existe '{path}'")
        sys.exit(1)

    lexer = Lexer(src)
    tokens = lexer.tokenize()

    # Mostrar todos los tokens (incluye EOF)
    print("--- TOKENS ---")
    for t in tokens:
        if t.type != TokenType.EOF:
            print(t)
    print("EOF")

    # Informar resultado del análisis léxico
    if lexer.errors:
        print("\n--- ERRORES LÉXICOS ---")
        for err in lexer.errors:
            print(err)
        sys.exit(1)
    else:
        print("\nAnálisis léxico completado sin errores")
        sys.exit(0)


if __name__ == '__main__':
    main()
