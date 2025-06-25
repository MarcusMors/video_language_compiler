import enum
import sys
from dataclasses import dataclass
from email.policy import default
from typing import Dict, List, Optional, Tuple

from enums.enums import KEYWORDS, Token, TokenType, compound_ops, symbols

# from scanner import Scanner

# Configuración de logging
DEBUG = True


class Lexer:
    def __init__(self, input_text: str):
        self.input = input_text
        self.pos = 0
        self.line = 1
        self.column = 1
        self.errors: List[str] = []
        # self.scanner = Scanner(input_text)

    def _peek_char(self, lookahead: int = 0) -> Optional[str]:
        pos = self.pos + lookahead
        return self.input[pos] if pos < len(self.input) else None

    def _get_char(self) -> Optional[str]:
        if self.pos >= len(self.input):
            return None

        char = self.input[self.pos]
        self.pos += 1

        if char == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1

        return char

    def _skip_whitespace(self):
        while (c := self._peek_char()) and c in {" ", "\t", "\n", "\r"}:
            self._get_char()

    def _read_identifier(self) -> str:
        identifier = []
        while (c := self._peek_char()) and (c.isalnum() or c == "_"):
            identifier.append(self._get_char())
        return "".join(identifier)

    def _read_number(self) -> Tuple[TokenType, str]:
        number = []
        is_float = False
        has_error = False

        while (c := self._peek_char()) and (c.isdigit() or c == "."):
            if c == ".":
                if is_float or len(number) == 0:
                    # if is_float or not number:
                    has_error = True
                is_float = True
            number.append(self._get_char())

        num_str = "".join(number)
        if has_error:
            self.errors.append(f"Invalid numeric format at {self.line}:{self.column}")
            return (TokenType.ERROR, num_str)

        return (TokenType.FLOAT_LITERAL if is_float else TokenType.INT_LITERAL, num_str)

    def _read_string(self) -> str:
        self._get_char()  # Consume opening "
        string = []

        while (c := self._peek_char()) and c != '"':
            if c == "\\":  # problem here, it detects // as double divide
                self._get_char()  # Consume backslash
                escape = self._get_char()
                if escape == "n":
                    string.append("\n")
                elif escape == "t":
                    string.append("\t")
                else:
                    string.append(escape)
            else:
                string.append(self._get_char())

        if self._peek_char() == '"':
            self._get_char()
        else:
            self.errors.append(f"Unclosed string literal at {self.line}:{self.column}")

        return "".join(string)

    def get_token(self) -> Token:
        self._skip_whitespace()
        c = self._peek_char()

        if not c:
            return Token(TokenType.EOF, "", self.line, self.column)

        start_line = self.line
        start_col = self.column

        # Manejo de debug output
        if c == "@":
            self._get_char()
            raw_msg = []
            while (next_char := self._peek_char()) and next_char != "\n":
                raw_msg.append(self._get_char())
            debug_msg = "".join(raw_msg)
            debug_msg = debug_msg.strip()  # para asegurar no trailing antes o después

            print(f"DEBUG OUTPUT [{start_line}:{start_col}]: {debug_msg}")
            return Token(TokenType.DEBUG_OUTPUT, debug_msg, start_line, start_col)

        # Identificadores y palabras clave
        if c.isalpha() or c == "_":
            identifier = self._read_identifier()
            token_type = KEYWORDS.get(identifier, TokenType.IDENTIFIER)
            return Token(token_type, identifier, start_line, start_col)

        # Números int o float
        if c.isdigit():
            token_type, value = self._read_number()
            return Token(token_type, value, start_line, start_col)

        # Strings
        if c == '"':
            value = self._read_string()
            return Token(TokenType.STRING_LITERAL, value, start_line, start_col)

        if c in {"<", ">", "+", "!", "="}:
            two_char = c + (self._peek_char(1) or "")
            if two_char in compound_ops:
                self._get_char()
                self._get_char()
                return Token(compound_ops[two_char], two_char, start_line, start_col)

        if c in symbols:
            self._get_char()
            return Token(symbols[c], c, start_line, start_col)

        # Carácter no reconocido
        self.errors.append(f"Invalid character '{c}' at {start_line}:{start_col}")
        self._get_char()
        return Token(TokenType.ERROR, c, start_line, start_col)


def main():
    if len(sys.argv) != 2:
        print(f"{sys.argv=}")
        print("Usage: python scanner.py <input_file>")
        sys.exit(1)

    with open(sys.argv[1], "r", encoding="utf-8") as f:
        input_text = f.read()

    lexer = Lexer(input_text)
    print("INFO SCAN - Start scanning...")

    while True:
        token = lexer.get_token()
        if token.type == TokenType.EOF:
            print(f"DEBUG SCAN - EOF found at ({token.line}:{token.column})")
            break
        if token.type == TokenType.ERROR:
            print(f"ERROR SCAN - {token.value} at {token.line}:{token.column}")
            continue
        if DEBUG and token.type != TokenType.DEBUG_OUTPUT:
            print(
                f"DEBUG SCAN - {token.type.name:15} [ {token.value} ] at ({token.line}:{token.column})"
            )

    if lexer.errors:
        print(f"\nINFO SCAN - Completed with {len(lexer.errors)} errors")
        for error in lexer.errors:
            print(f"  {error}")
    else:
        print("\nINFO SCAN - Completed with 0 errors")


if __name__ == "__main__":
    main()
