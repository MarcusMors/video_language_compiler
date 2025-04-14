import enum
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

# Configuración de logging (puedes personalizar los niveles)
DEBUG = True

class TokenType(enum.Enum):
    # Palabras clave
    MAIN = 'main'
    IF = 'if'
    ELSE = 'else'
    WHILE = 'while'
    TRUE = 'True'
    FALSE = 'False'
    NOT = 'not'
    AND = 'and'
    OR = 'or'
    
    # Tipos
    STRING_TYPE = 'string'
    FLOAT_TYPE = 'float'
    INT_TYPE = 'int'
    VIDEO_TYPE = 'video'
    BOOL_TYPE = 'bool'
    
    # Operadores y símbolos
    ASSIGN = '='
    PLUS = '+'
    MINUS = '-'
    MULT = '*'
    DIV = '/'
    MOD = '%'
    CONCAT = '++'
    EQ = '=='
    NEQ = '!='
    LT = '<'
    GT = '>'
    LE = '<='
    GE = '>='
    LPAREN = '('
    RPAREN = ')'
    LBRACE = '{'
    RBRACE = '}'
    LBRACKET = '['
    RBRACKET = ']'
    COMMA = ','
    DOT = '.'
    SEMICOLON = ';'
    COLON = ':'
    
    # Literales e identificadores
    IDENTIFIER = 'IDENTIFIER'
    INT_LITERAL = 'INT_LITERAL'
    FLOAT_LITERAL = 'FLOAT_LITERAL'
    STRING_LITERAL = 'STRING_LITERAL'
    
    # Especiales
    COMMENT = 'COMMENT'
    EOF = 'EOF'
    ERROR = 'ERROR'
    
    # ... (otros tokens)
    DEBUG_OUTPUT = '@'  # Nuevo token especial

@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int

class Lexer:
    def __init__(self, input_text: str):
        self.input = input_text
        self.pos = 0
        self.line = 1
        self.column = 1
        self.errors: List[str] = []
    
    def _peek_char(self) -> Optional[str]:
        if self.pos >= len(self.input):
            return None
        return self.input[self.pos]
    
    def _get_char(self) -> Optional[str]:
        if self.pos >= len(self.input):
            return None
        char = self.input[self.pos]
        self.pos += 1
        
        if char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
            
        return char
    
    def _skip_whitespace(self):
        while (c := self._peek_char()) and c in {' ', '\t', '\n', '\r'}:
            self._get_char()
    
    def _read_identifier(self) -> str:
        identifier = []
        while (c := self._peek_char()) and (c.isalnum() or c == '_'):
            identifier.append(self._get_char())
        return ''.join(identifier)
    
    def _read_number(self) -> Tuple[TokenType, str]:
        number = []
        is_float = False
        
        while (c := self._peek_char()) and (c.isdigit() or c == '.'):
            if c == '.':
                if is_float:
                    self.errors.append(f"Invalid number format at {self.line}:{self.column}")
                    break
                is_float = True
            number.append(self._get_char())
        
        num_str = ''.join(number)
        if is_float:
            return (TokenType.FLOAT_LITERAL, num_str)
        return (TokenType.INT_LITERAL, num_str)
    
    def _read_string(self) -> str:
        self._get_char()  # Consume opening "
        string = []
        
        while (c := self._peek_char()) and c != '"':
            if c == '\\':
                self._get_char()  # Consume backslash
                escape = self._get_char()
                if escape == 'n':
                    string.append('\n')
                else:
                    string.append(escape)
            else:
                string.append(self._get_char())
        
        if self._peek_char() == '"':
            self._get_char()
        else:
            self.errors.append(f"Unclosed string literal at {self.line}:{self.column}")
        
        return ''.join(string)
    
    def _read_comment(self):
        while (c := self._peek_char()) and c != '\n':
            self._get_char()
        self._get_char()  # Consume newline
    
    def get_token(self) -> Token:
        self._skip_whitespace()
        c = self._peek_char()
        
        if c == '@':
            self._get_char()  # Consumir @
            message = []
            while (next_char := self._peek_char()) and next_char != '\n':
                message.append(self._get_char())
            debug_msg = ''.join(message).strip()
            # Imprimir inmediatamente el mensaje de debug
            print(f"DEBUG OUTPUT [{self.line}:{self.column}]: {debug_msg}")
            return Token(TokenType.DEBUG_OUTPUT, debug_msg, self.line, self.column)
        
        if not c:
            return Token(TokenType.EOF, '', self.line, self.column)
        
        start_line = self.line
        start_col = self.column
        
        # Identificadores y palabras clave
        if c.isalpha() or c == '_':
            identifier = self._read_identifier()
            if identifier in KEYWORDS:
                return Token(KEYWORDS[identifier], identifier, start_line, start_col)
            return Token(TokenType.IDENTIFIER, identifier, start_line, start_col)
        
        # Números
        if c.isdigit():
            token_type, value = self._read_number()
            return Token(token_type, value, start_line, start_col)
        
        # Strings
        if c == '"':
            value = self._read_string()
            return Token(TokenType.STRING_LITERAL, value, start_line, start_col)
        
        # Comentarios
        if c == '/':
            self._get_char()
            if self._peek_char() == '/':
                self._read_comment()
                return self.get_token()  # Skip comment and get next token
            else:
                return Token(TokenType.DIV, '/', start_line, start_col)
        
        # Operadores de múltiples caracteres
        if c == '=':
            self._get_char()
            if self._peek_char() == '=':
                self._get_char()
                return Token(TokenType.EQ, '==', start_line, start_col)
            return Token(TokenType.ASSIGN, '=', start_line, start_col)
        
        if c == '!':
            self._get_char()
            if self._peek_char() == '=':
                self._get_char()
                return Token(TokenType.NEQ, '!=', start_line, start_col)
            self.errors.append(f"Unexpected character '!' at {start_line}:{start_col}")
            return Token(TokenType.ERROR, '!', start_line, start_col)
        
        # Resto de operadores y símbolos
        symbols = {
            '+': TokenType.PLUS,
            '-': TokenType.MINUS,
            '*': TokenType.MULT,
            '%': TokenType.MOD,
            '(': TokenType.LPAREN,
            ')': TokenType.RPAREN,
            '{': TokenType.LBRACE,
            '}': TokenType.RBRACE,
            '[': TokenType.LBRACKET,
            ']': TokenType.RBRACKET,
            ',': TokenType.COMMA,
            '.': TokenType.DOT,
            ';': TokenType.SEMICOLON,
            ':': TokenType.COLON,
            '<': TokenType.LT,
            '>': TokenType.GT,
            '@': TokenType.DEBUG_OUTPUT,
        }
        
        if c in symbols:
            self._get_char()
            # Manejar operadores de dos caracteres
            if c == '+' and self._peek_char() == '+':
                self._get_char()
                return Token(TokenType.CONCAT, '++', start_line, start_col)
            if c == '<' and self._peek_char() == '=':
                self._get_char()
                return Token(TokenType.LE, '<=', start_line, start_col)
            if c == '>' and self._peek_char() == '=':
                self._get_char()
                return Token(TokenType.GE, '>=', start_line, start_col)
            return Token(symbols[c], c, start_line, start_col)
        
        # Carácter no reconocido
        self.errors.append(f"Invalid character '{c}' at {start_line}:{start_col}")
        self._get_char()  # Saltar carácter inválido
        return Token(TokenType.ERROR, c, start_line, start_col)

KEYWORDS = {
    'main': TokenType.MAIN,
    'if': TokenType.IF,
    'else': TokenType.ELSE,
    'while': TokenType.WHILE,
    'True': TokenType.TRUE,
    'False': TokenType.FALSE,
    'not': TokenType.NOT,
    'and': TokenType.AND,
    'or': TokenType.OR,
    'string': TokenType.STRING_TYPE,
    'float': TokenType.FLOAT_TYPE,
    'int': TokenType.INT_TYPE,
    'video': TokenType.VIDEO_TYPE,
    'bool': TokenType.BOOL_TYPE,
}

def main():
    if len(sys.argv) < 2:
        print("Usage: python scanner.py <input_file>")
        return
    
    with open(sys.argv[1], 'r') as f:
        input_text = f.read()
    
    lexer = Lexer(input_text)
    print(f"INFO SCAN - Start scanning...")
    
    while True:
        token = lexer.get_token()
        if token.type == TokenType.EOF:
            print(f"DEBUG SCAN - EOP [ $ ] found at ({token.line}:{token.column})")
            break
        if token.type == TokenType.ERROR:
            print(f"ERROR SCAN - {token.value} at {token.line}:{token.column}")
            continue
        if DEBUG and token.type != TokenType.COMMENT:
            print(f"DEBUG SCAN - {token.type.name} [ {token.value} ] found at ({token.line}:{token.column})")
    
    if lexer.errors:
        print(f"INFO SCAN - Completed with {len(lexer.errors)} errors")
        for error in lexer.errors:
            print(f"ERROR: {error}")
    else:
        print(f"INFO SCAN - Completed with 0 errors")

if __name__ == "__main__":
    main()