# Copyright (C) 2025 José Enrique Vilca Campana
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

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
