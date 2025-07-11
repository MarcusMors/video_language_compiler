import enum
from dataclasses import dataclass

"""
Definición de tokens del lenguaje de edición de video.
Este módulo centraliza todas las enumeraciones y tablas de mapeo
utilizadas por el lexer para convertir los lexemas de la entrada en
tipos de token.
"""


class TokenType(enum.Enum):
    # --- Palabras clave del lenguaje ---
    MAIN = enum.auto()
    IF = enum.auto()
    ELSE = enum.auto()
    WHILE = enum.auto()
    EXPORT = enum.auto()
    AS = enum.auto()

    # — Tipos de datos —
    INT_TYPE = enum.auto()
    FLOAT_TYPE = enum.auto()
    STRING_TYPE = enum.auto()
    VIDEO_TYPE = enum.auto()
    AUDIO_TYPE = enum.auto()

    # — Literales e identificadores —
    INT_LITERAL = enum.auto()
    FLOAT_LITERAL = enum.auto()
    STRING_LITERAL = enum.auto()
    IDENTIFIER = enum.auto()

    # — Operadores lógicos —
    NOT = enum.auto()
    AND = enum.auto()
    OR = enum.auto()

    # — Operadores aritméticos —
    ASSIGN = enum.auto()  # '='
    PLUS = enum.auto()  # '+'
    MINUS = enum.auto()  # '-'
    MULT = enum.auto()  # '*'
    DIV = enum.auto()  # '/'

    # — Comparaciones —
    EQ = enum.auto()  # '=='
    NEQ = enum.auto()  # '!='
    LT = enum.auto()  # '<'
    GT = enum.auto()  # '>'
    LE = enum.auto()  # '<='
    GE = enum.auto()  # '>='

    # — Símbolos —
    LPAREN = enum.auto()
    RPAREN = enum.auto()
    LBRACE = enum.auto()
    RBRACE = enum.auto()
    LBRACKET = enum.auto()
    RBRACKET = enum.auto()
    COMMA = enum.auto()
    SEMICOLON = enum.auto()
    COLON = enum.auto()

    VIDEO_RESIZE = enum.auto()
    # — Funciones especiales de video —
    VIDEO_FLIP = enum.auto()
    VIDEO_VELOCIDAD = enum.auto()
    VIDEO_FADEIN = enum.auto()
    VIDEO_FADEOUT = enum.auto()
    VIDEO_SILENCIO = enum.auto()
    VIDEO_QUITAR_AUDIO = enum.auto()
    VIDEO_AGREGAR_MUSICA = enum.auto()
    VIDEO_CONCATENAR = enum.auto()
    VIDEO_CORTAR = enum.auto()

    # — Especiales —
    EOF = enum.auto()
    ERROR = enum.auto()


# Mapeo de lexema a TokenType
LEXEME_TO_TOKEN: dict[str, TokenType] = {
    # keywords
    "main": TokenType.MAIN,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "while": TokenType.WHILE,
    "exportar": TokenType.EXPORT,
    "como": TokenType.AS,
    # tipos
    "int": TokenType.INT_TYPE,
    "float": TokenType.FLOAT_TYPE,
    "string": TokenType.STRING_TYPE,
    "video": TokenType.VIDEO_TYPE,
    "audio": TokenType.AUDIO_TYPE,
    # literales lógicos
    "not": TokenType.NOT,
    "and": TokenType.AND,
    "or": TokenType.OR,
    # operadores compuestos
    "==": TokenType.EQ,
    "!=": TokenType.NEQ,
    "<=": TokenType.LE,
    ">=": TokenType.GE,
    # operadores simples y símbolos
    "=": TokenType.ASSIGN,
    "+": TokenType.PLUS,
    "-": TokenType.MINUS,
    "*": TokenType.MULT,
    "/": TokenType.DIV,
    "<": TokenType.LT,
    ">": TokenType.GT,
    ":": TokenType.COLON,
    ",": TokenType.COMMA,
    "{": TokenType.LBRACE,
    "}": TokenType.RBRACE,
    "[": TokenType.LBRACKET,
    "]": TokenType.RBRACKET,
    "(": TokenType.LPAREN,
    ")": TokenType.RPAREN,
    ";": TokenType.SEMICOLON,
    # funciones @
    "@resize": TokenType.VIDEO_RESIZE,
    "@flip": TokenType.VIDEO_FLIP,
    "@velocidad": TokenType.VIDEO_VELOCIDAD,
    "@fadein": TokenType.VIDEO_FADEIN,
    "@fadeout": TokenType.VIDEO_FADEOUT,
    "@silencio": TokenType.VIDEO_SILENCIO,
    "@quitar_audio": TokenType.VIDEO_QUITAR_AUDIO,
    "@agregar_musica": TokenType.VIDEO_AGREGAR_MUSICA,
    "@concatenar": TokenType.VIDEO_CONCATENAR,
    "@cortar": TokenType.VIDEO_CORTAR,
}


# Representación de un token
@dataclass(frozen=True)
class Token:
    type: TokenType
    value: str
    line: int
    column: int

    def __str__(self):
        return f"{self.type.name:20} [ {self.value} ] -> {self.line}:{self.column}"


# Tablas auxiliares for lexer speed
KEYWORDS = {k: v for k, v in LEXEME_TO_TOKEN.items() if k.isalpha()}
compound_ops = {
    k: v
    for k, v in LEXEME_TO_TOKEN.items()
    if len(k) == 2 and not k.isalpha() and not k.startswith("@")
}
symbols = {k: v for k, v in LEXEME_TO_TOKEN.items() if len(k) == 1 and not k.isalnum()}
VIDEO_FUNCS = {k: v for k, v in LEXEME_TO_TOKEN.items() if k.startswith("@")}
