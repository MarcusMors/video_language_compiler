import enum
from dataclasses import dataclass


class TokenType(enum.Enum):
    # Palabras clave
    MAIN = "main"
    IF = "if"
    ELSE = "else"
    WHILE = "while"
    TRUE = "True"
    FALSE = "False"
    NOT = "not"
    AND = "and"
    OR = "or"

    # Tipos
    STRING_TYPE = "string"
    FLOAT_TYPE = "float"
    INT_TYPE = "int"
    VIDEO_TYPE = "video"
    BOOL_TYPE = "bool"

    # Operadores y símbolos
    ASSIGN = "="
    PLUS = "+"
    MINUS = "-"
    MULT = "*"
    DIV = "/"
    MOD = "%"
    CONCAT = "++"
    EQ = "=="
    NEQ = "!="
    LT = "<"
    GT = ">"
    LE = "<="
    GE = ">="
    LPAREN = "("
    RPAREN = ")"
    LBRACE = "{"
    RBRACE = "}"
    LBRACKET = "["
    RBRACKET = "]"
    COMMA = ","
    DOT = "."
    SEMICOLON = ";"
    COLON = ":"
    DEBUG_OUTPUT = "@"

    # Literales e identificadores
    IDENTIFIER = "IDENTIFIER"
    INT_LITERAL = "INT_LITERAL"
    FLOAT_LITERAL = "FLOAT_LITERAL"
    STRING_LITERAL = "STRING_LITERAL"
    BOOL_LITERAL = "BOOL_LITERAL"
    LIST_LITERAL = "LIST_LITERAL"

    # Especiales
    EOF = "EOF"
    ERROR = "ERROR"


# Operadores y símbolos individuales
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


KEYWORDS = {
    "main": TokenType.MAIN,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "while": TokenType.WHILE,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
    "not": TokenType.NOT,
    "and": TokenType.AND,
    "or": TokenType.OR,
    "string": TokenType.STRING_TYPE,
    "float": TokenType.FLOAT_TYPE,
    "int": TokenType.INT_TYPE,
    "video": TokenType.VIDEO_TYPE,
    "bool": TokenType.BOOL_TYPE,
}

# Operadores compuestos
compound_ops = {
    "<=": TokenType.LE,
    ">=": TokenType.GE,
    "++": TokenType.CONCAT,
    "==": TokenType.EQ,
    "!=": TokenType.NEQ,
}


@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int

class SyntaxErrorType(enum.Enum):
    MISSING_SEMICOLON = "Missing ';' at end of statement"
    MISSING_COLON = "Missing ':' in declaration"
    MISSING_ASSIGN = "Missing '=' in assignment"
    UNCLOSED_BRACE = "Unclosed '{' block"
    UNCLOSED_PAREN = "Unclosed '(' in expression"
    UNCLOSED_BRACKET = "Unclosed '[' in array access"
    TYPE_MISMATCH = "Type mismatch in expression"
    UNDECLARED_VARIABLE = "Undeclared variable"
    DUPLICATE_DECLARATION = "Duplicate variable declaration"
    INVALID_OPERATION = "Invalid operation for type"
    UNEXPECTED_TOKEN = "Unexpected token"
    INVALID_CONCAT_OPERATOR = "Use '++' for video concatenation"
    INVALID_ARRAY_ACCESS = "Array access on non-array type"
    INVALID_IDENTIFIER = "Identifier cannot start with underscore"

class SemanticErrorType(enum.Enum):
    ARRAY_SIZE_MISMATCH = "Array literal size doesn't match declaration"
    ARRAY_TYPE_MISMATCH = "Array element type doesn't match declaration"
    INVALID_ARRAY_DECLARATION = "Invalid array declaration syntax"