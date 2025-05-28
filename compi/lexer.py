
import sys
from typing import List, Optional, Tuple
from enums import (
    Token,
    TokenType,
    KEYWORDS,
    symbols,
    compound_ops,
    SyntaxErrorType
)

DEBUG = True
MAX_ERRORS = 20


class Lexer:
    def __init__(self, source: str) -> None:
        self.src = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.errors: List[str] = []

    # ---------- helpers ----------
    def _peek(self, k: int = 0) -> Optional[str]:
        idx = self.pos + k
        return self.src[idx] if idx < len(self.src) else None

    def _advance(self) -> Optional[str]:
        if self.pos >= len(self.src):
            return None
        ch = self.src[self.pos]
        self.pos += 1
        if ch == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return ch
    
    def tokenize(self) -> List[Token]:
        tokens = []
        while True:
            tok = self.get_token()
            tokens.append(tok)
            if tok.type == TokenType.EOF:
                break
        return tokens
    
    def _error(self, msg: str) -> None:
        self.errors.append(f"{msg} -> {self.line}:{self.column}")
        if len(self.errors) >= MAX_ERRORS:
            raise RuntimeError("Too many lexical errors – aborted")

    # ---------- skip spaces + // comments ----------
    def _skip_blanks_comments(self) -> None:
        while True:
            while (c := self._peek()) and c in " \t\r\n":
                self._advance()
            if self._peek() == "/" and self._peek(1) == "/":
                while (c := self._peek()) and c != "\n":
                    self._advance()
                continue
            break

    # ---------- readers ----------
    def _read_identifier(self) -> Tuple[TokenType, str]:
        buf = []
        starts_with_underscore = self._peek() == "_"
        while (c := self._peek()) and (c.isalnum() or c == "_"):
            buf.append(self._advance())
        lex = "".join(buf)
        if starts_with_underscore and lex != "_":
            self._error(SyntaxErrorType.INVALID_IDENTIFIER.value)
            return TokenType.ERROR, lex
        return KEYWORDS.get(lex, TokenType.IDENTIFIER), lex

    def _read_number(self) -> Tuple[TokenType, str]:
        buf = []
        is_float = False
        while (c := self._peek()) and (c.isdigit() or c == "."):
            if c == ".":
                if is_float:
                    break
                is_float = True
            buf.append(self._advance())

        # exponente
        if (c := self._peek()) and c in "eE":
            is_float = True
            buf.append(self._advance())
            if (c2 := self._peek()) and c2 in "+-":
                buf.append(self._advance())
            if not (self._peek() and self._peek().isdigit()):
                self._error(SyntaxErrorType.INVALID_EXPONENT_FORMAT.value)
            while (c3 := self._peek()) and c3.isdigit():
                buf.append(self._advance())

        lex = "".join(buf)

        # identificador pegado a número
        if (nxt := self._peek()) and (nxt.isalpha() or nxt == "_"):
            self._error(SyntaxErrorType.INVALID_IDENTIFIER_DIGIT.value)

        if lex.count(".") > 1 or lex.endswith("."):
            self._error(SyntaxErrorType.INVALID_NUMERIC_FORMAT.value)

        return (TokenType.FLOAT_LITERAL if is_float else TokenType.INT_LITERAL), lex

    def _read_string(self) -> str:
        self._advance()  # consume opening "
        buf = []
        while True:
            c = self._peek()
            if c is None or c == "\n":
                self._error(SyntaxErrorType.UNCLOSED_STRING.value)
                break
            if c == '"':
                self._advance()
                break
            if c == "\\":
                self._advance()
                buf.append({"n": "\n", "t": "\t"}.get(self._peek(), self._peek() or ""))
                self._advance()
            else:
                buf.append(self._advance())
        return "".join(buf)

    # ---------- public ----------
    def get_token(self) -> Token:
        self._skip_blanks_comments()
        start_line, start_col = self.line, self.column
        c = self._peek()

        if c is None:
            return Token(TokenType.EOF, "", start_line, start_col)

        if c == "@":
            
            self._advance()
            return Token(TokenType.DEBUG_OUTPUT, "@", start_line, start_col)
            #self._advance()
            #txt = []
            #while (n := self._peek()) and n != "\n":
            #    txt.append(self._advance())
            #return Token(TokenType.DEBUG_OUTPUT, "".join(txt).strip(), start_line, start_col)

        if c.isalpha() or c == "_":
            t, lex = self._read_identifier()
            return Token(t, lex, start_line, start_col)

        if c.isdigit():
            t, lex = self._read_number()
            return Token(t, lex, start_line, start_col)

        if c == '"':
            lex = self._read_string()
            return Token(TokenType.STRING_LITERAL, lex, start_line, start_col)

        two = (c or "") + (self._peek(1) or "")
        if two in compound_ops:
            self._advance(); self._advance()
            return Token(compound_ops[two], two, start_line, start_col)

        if c in symbols:
            self._advance()
            return Token(symbols[c], c, start_line, start_col)
        
        
        # illegal char
        self._advance()
        self._error(f"Lexical error: illegal character '{c}'")
        return Token(TokenType.ERROR, c, start_line, start_col)


# ---------- CLI driver ----------
def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python lexer.py <source_file>")
        sys.exit(1)

    with open(sys.argv[1], encoding="utf-8") as f:
        src = f.read()

    lex = Lexer(src)
    if DEBUG:
        print("--- TOKENS ---")
    while True:
        tok = lex.get_token()
        if tok.type == TokenType.EOF:
            if DEBUG:
                print("EOF")
            break
        if DEBUG and tok.type != TokenType.DEBUG_OUTPUT:
            print(tok)

    print("\n--- LEXICAL ERRORS ---")
    if lex.errors:
        for e in lex.errors:
            print("  " + e)
    else:
        print("No lexical errors.")


if __name__ == "__main__":
    main()
