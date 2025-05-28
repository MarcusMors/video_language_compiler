import enum
from dataclasses import dataclass

class TokenType(enum.Enum):
    # ---------- Palabras clave ----------
    MAIN   = enum.auto()
    IF     = enum.auto()
    ELSE   = enum.auto()
    WHILE  = enum.auto()

    # ---------- Operadores lógicos ----------
    NOT  = enum.auto()
    AND  = enum.auto()
    OR   = enum.auto()

    # ---------- Tipos ----------
    STRING_TYPE = enum.auto()
    FLOAT_TYPE  = enum.auto()
    INT_TYPE    = enum.auto()
    VIDEO_TYPE  = enum.auto()
    BOOL_TYPE   = enum.auto()

    # ---------- Operadores y símbolos ----------
    ASSIGN = enum.auto()    # =
    PLUS   = enum.auto()    # +
    MINUS  = enum.auto()    # -
    MULT   = enum.auto()    # *
    DIV    = enum.auto()    # /
    MOD    = enum.auto()    # %
    CONCAT = enum.auto()    # ++
    EQ     = enum.auto()    # ==
    NEQ    = enum.auto()    # !=
    LT     = enum.auto()    # <
    GT     = enum.auto()    # >
    LE     = enum.auto()    # <=
    GE     = enum.auto()    # >=
    LPAREN   = enum.auto()  # (
    RPAREN   = enum.auto()  # )
    LBRACE   = enum.auto()  # {
    RBRACE   = enum.auto()  # }
    LBRACKET = enum.auto()  # [
    RBRACKET = enum.auto()  # ]
    COMMA    = enum.auto()  # ,
    DOT      = enum.auto()  # .
    SEMICOLON= enum.auto()  # ;
    COLON    = enum.auto()  # :
    DEBUG_OUTPUT = enum.auto()  # @

    # ---------- Literales e identificadores ----------
    IDENTIFIER     = enum.auto()
    INT_LITERAL    = enum.auto()
    FLOAT_LITERAL  = enum.auto()
    STRING_LITERAL = enum.auto()
    BOOL_LITERAL   = enum.auto()
    LIST_LITERAL   = enum.auto()

    # ---------- Especiales ----------
    EOF   = enum.auto()
    ERROR = enum.auto()

# Tablas auxiliares
symbols = {
    "=": TokenType.ASSIGN,
    "+": TokenType.PLUS,
    "-": TokenType.MINUS,
    "*": TokenType.MULT,
    "/": TokenType.DIV,
    "%": TokenType.MOD,
    "(": TokenType.LPAREN,
    ")": TokenType.RPAREN,
    "{": TokenType.LBRACE,
    "}": TokenType.RBRACE,
    "[": TokenType.LBRACKET,
    "]": TokenType.RBRACKET,
    ",": TokenType.COMMA,
    ".": TokenType.DOT,
    ";": TokenType.SEMICOLON,
    ":": TokenType.COLON,
    "<": TokenType.LT,
    ">": TokenType.GT,
}
compound_ops = {
    "<=": TokenType.LE,
    ">=": TokenType.GE,
    "++": TokenType.CONCAT,
    "==": TokenType.EQ,
    "!=": TokenType.NEQ,
}
KEYWORDS = {
    "main":  TokenType.MAIN,
    "if":    TokenType.IF,
    "else":  TokenType.ELSE,
    "while": TokenType.WHILE,
    "not":   TokenType.NOT,
    "and":   TokenType.AND,
    "or":    TokenType.OR,
    "string": TokenType.STRING_TYPE,
    "float":  TokenType.FLOAT_TYPE,
    "int":    TokenType.INT_TYPE,
    "video":  TokenType.VIDEO_TYPE,
    "bool":   TokenType.BOOL_TYPE,
    "true":   TokenType.BOOL_LITERAL,
    "false":  TokenType.BOOL_LITERAL,
}

@dataclass
class Token:
    type:   TokenType
    value:  str
    line:   int
    column: int

    def __str__(self) -> str:
        return f"{self.type.name:15} [ {self.value} ] -> {self.line}:{self.column}"
 #   

class SyntaxErrorType(enum.Enum):
    MISSING_SEMICOLON      = "Missing ';' at end of statement"
    MISSING_COLON          = "Missing ':' in declaration"
    MISSING_ASSIGN         = "Missing '=' in assignment"
    UNCLOSED_BRACE         = "Unclosed '{' block"
    UNCLOSED_PAREN         = "Unclosed '(' in expression"
    UNCLOSED_BRACKET       = "Unclosed '[' in array access"
    UNCLOSED_STRING         = "Unclosed string literal" 
    TYPE_MISMATCH          = "Type mismatch in expression"
    UNDECLARED_VARIABLE    = "Undeclared variable"
    DUPLICATE_DECLARATION  = "Duplicate variable declaration"
    INVALID_OPERATION      = "Invalid operation for type"
    UNEXPECTED_TOKEN       = "Unexpected token"
    INVALID_CONCAT_OPERATOR= "Use '++' for video concatenation"
    INVALID_ARRAY_ACCESS   = "Array access on non-array type"
    INVALID_IDENTIFIER     = "Identifier cannot start with underscore"
    INVALID_IDENTIFIER_DIGIT = "Identifier cannot start with digit"
    INVALID_NUMERIC_FORMAT = "Invalid numeric format"
    INVALID_EXPONENT_FORMAT= "Invalid exponent format"