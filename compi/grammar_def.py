# grammar_def.py
from enums import TokenType

EPSILON: str = 'ε'
START_SYMBOL: str = 'Program'

PARSING_TABLE = {
    'Program': {
        TokenType.MAIN: ['MainDecl', 'Block', TokenType.EOF]
    },
    'MainDecl': {
        TokenType.MAIN: [TokenType.MAIN, TokenType.COLON, TokenType.LPAREN, TokenType.RPAREN]
    },
    'Block': {
        TokenType.LBRACE: [TokenType.LBRACE, 'StmtList', TokenType.RBRACE]
    },
    'StmtList': {
        TokenType.IDENTIFIER: ['Stmt', 'StmtList'],
        TokenType.IF: ['Stmt', 'StmtList'],
        TokenType.WHILE: ['Stmt', 'StmtList'],
        TokenType.DEBUG_OUTPUT: ['Stmt', 'StmtList'],
        TokenType.RBRACE: [EPSILON]
    },
    'Stmt': {
        TokenType.IDENTIFIER: [TokenType.IDENTIFIER, 'StmtSuffix'],
        TokenType.IF: ['Conditional'],
        TokenType.WHILE: ['Loop'],
        TokenType.DEBUG_OUTPUT: ['DebugStmt']
    },
    'StmtSuffix': {
        TokenType.COLON: [TokenType.COLON, 'Type', 'VarInit', TokenType.SEMICOLON],
        TokenType.ASSIGN: [TokenType.ASSIGN, 'Expr', TokenType.SEMICOLON]
    },
    'VarInit': {
        TokenType.ASSIGN: [TokenType.ASSIGN, 'Expr'],
        TokenType.SEMICOLON: [EPSILON]
    },
    'Type': {
        TokenType.INT_TYPE: [TokenType.INT_TYPE],
        TokenType.FLOAT_TYPE: [TokenType.FLOAT_TYPE],
        TokenType.STRING_TYPE: [TokenType.STRING_TYPE],
        TokenType.VIDEO_TYPE: [TokenType.VIDEO_TYPE],
        TokenType.BOOL_TYPE: [TokenType.BOOL_TYPE]
    },
    'Conditional': {
        TokenType.IF: [TokenType.IF, TokenType.LPAREN, 'Expr', TokenType.RPAREN, 'Block', 'ElseClause']
    },
    'ElseClause': {
        TokenType.ELSE: [TokenType.ELSE, 'Block'],
        TokenType.RBRACE: [EPSILON],
        TokenType.IDENTIFIER: [EPSILON],
        TokenType.IF: [EPSILON],
        TokenType.WHILE: [EPSILON],
        TokenType.DEBUG_OUTPUT: [EPSILON]
    },
    'Loop': {
        TokenType.WHILE: [TokenType.WHILE, TokenType.LPAREN, 'Expr', TokenType.RPAREN, 'Block']
    },
    'DebugStmt': {
        TokenType.DEBUG_OUTPUT: [TokenType.DEBUG_OUTPUT, 'Expr', TokenType.SEMICOLON]
    },

    # Expresiones
    'Expr': {
        TokenType.NOT: ['LogicalOr'],
        TokenType.LPAREN: ['LogicalOr'],
        TokenType.INT_LITERAL: ['LogicalOr'],
        TokenType.FLOAT_LITERAL: ['LogicalOr'],
        TokenType.STRING_LITERAL: ['LogicalOr'],
        TokenType.BOOL_LITERAL: ['LogicalOr'],
        TokenType.IDENTIFIER: ['LogicalOr']
    },
    'LogicalOr': {
        TokenType.NOT: ['LogicalAnd', 'OrTail'],
        TokenType.LPAREN: ['LogicalAnd', 'OrTail'],
        TokenType.INT_LITERAL: ['LogicalAnd', 'OrTail'],
        TokenType.FLOAT_LITERAL: ['LogicalAnd', 'OrTail'],
        TokenType.STRING_LITERAL: ['LogicalAnd', 'OrTail'],
        TokenType.BOOL_LITERAL: ['LogicalAnd', 'OrTail'],
        TokenType.IDENTIFIER: ['LogicalAnd', 'OrTail']
    },
    'OrTail': {
        TokenType.OR: [TokenType.OR, 'LogicalAnd', 'OrTail'],
        TokenType.SEMICOLON: [EPSILON],
        TokenType.RPAREN: [EPSILON],
        TokenType.RBRACE: [EPSILON]
    },
    'LogicalAnd': {
        TokenType.NOT: ['Equality', 'AndTail'],
        TokenType.LPAREN: ['Equality', 'AndTail'],
        TokenType.INT_LITERAL: ['Equality', 'AndTail'],
        TokenType.FLOAT_LITERAL: ['Equality', 'AndTail'],
        TokenType.STRING_LITERAL: ['Equality', 'AndTail'],
        TokenType.BOOL_LITERAL: ['Equality', 'AndTail'],
        TokenType.IDENTIFIER: ['Equality', 'AndTail']
    },
    'AndTail': {
        TokenType.AND: [TokenType.AND, 'Equality', 'AndTail'],
        TokenType.OR: [EPSILON],
        TokenType.SEMICOLON: [EPSILON],
        TokenType.RPAREN: [EPSILON],
        TokenType.RBRACE: [EPSILON]
    },
    'Equality': {
        TokenType.NOT: ['Relational', 'EqTail'],
        TokenType.LPAREN: ['Relational', 'EqTail'],
        TokenType.INT_LITERAL: ['Relational', 'EqTail'],
        TokenType.FLOAT_LITERAL: ['Relational', 'EqTail'],
        TokenType.STRING_LITERAL: ['Relational', 'EqTail'],
        TokenType.BOOL_LITERAL: ['Relational', 'EqTail'],
        TokenType.IDENTIFIER: ['Relational', 'EqTail']
    },
    'EqTail': {
        TokenType.EQ: [TokenType.EQ, 'Relational', 'EqTail'],
        TokenType.NEQ: [TokenType.NEQ, 'Relational', 'EqTail'],
        TokenType.AND: [EPSILON],
        TokenType.OR: [EPSILON],
        TokenType.SEMICOLON: [EPSILON],
        TokenType.RPAREN: [EPSILON],
        TokenType.RBRACE: [EPSILON]
    },
    'Relational': {
        TokenType.NOT: ['Additive', 'RelTail'],
        TokenType.LPAREN: ['Additive', 'RelTail'],
        TokenType.INT_LITERAL: ['Additive', 'RelTail'],
        TokenType.FLOAT_LITERAL: ['Additive', 'RelTail'],
        TokenType.STRING_LITERAL: ['Additive', 'RelTail'],
        TokenType.BOOL_LITERAL: ['Additive', 'RelTail'],
        TokenType.IDENTIFIER: ['Additive', 'RelTail']
    },
    'RelTail': {
        TokenType.LT: [TokenType.LT, 'Additive', 'RelTail'],
        TokenType.GT: [TokenType.GT, 'Additive', 'RelTail'],
        TokenType.LE: [TokenType.LE, 'Additive', 'RelTail'],
        TokenType.GE: [TokenType.GE, 'Additive', 'RelTail'],
        TokenType.EQ: [EPSILON],
        TokenType.NEQ: [EPSILON],
        TokenType.AND: [EPSILON],
        TokenType.OR: [EPSILON],
        TokenType.SEMICOLON: [EPSILON],
        TokenType.RPAREN: [EPSILON],
        TokenType.RBRACE: [EPSILON]
    },
    'Additive': {
        TokenType.NOT: ['Multiplicative', 'AddTail'],
        TokenType.LPAREN: ['Multiplicative', 'AddTail'],
        TokenType.INT_LITERAL: ['Multiplicative', 'AddTail'],
        TokenType.FLOAT_LITERAL: ['Multiplicative', 'AddTail'],
        TokenType.STRING_LITERAL: ['Multiplicative', 'AddTail'],
        TokenType.BOOL_LITERAL: ['Multiplicative', 'AddTail'],
        TokenType.IDENTIFIER: ['Multiplicative', 'AddTail']
    },
    'AddTail': {
        TokenType.PLUS: [TokenType.PLUS, 'Multiplicative', 'AddTail'],
        TokenType.MINUS: [TokenType.MINUS, 'Multiplicative', 'AddTail'],
        TokenType.CONCAT: [TokenType.CONCAT, 'Multiplicative', 'AddTail'],
        TokenType.MULT: [EPSILON],
        TokenType.DIV: [EPSILON],
        TokenType.MOD: [EPSILON],
        TokenType.EQ: [EPSILON],
        TokenType.NEQ: [EPSILON],
        TokenType.LT: [EPSILON],
        TokenType.GT: [EPSILON],
        TokenType.LE: [EPSILON],
        TokenType.GE: [EPSILON],
        TokenType.AND: [EPSILON],
        TokenType.OR: [EPSILON],
        TokenType.SEMICOLON: [EPSILON],
        TokenType.RPAREN: [EPSILON],
        TokenType.RBRACE: [EPSILON]
    },
    'Multiplicative': {
        TokenType.NOT: ['Unary', 'MulTail'],
        TokenType.LPAREN: ['Unary', 'MulTail'],
        TokenType.INT_LITERAL: ['Unary', 'MulTail'],
        TokenType.FLOAT_LITERAL: ['Unary', 'MulTail'],
        TokenType.STRING_LITERAL: ['Unary', 'MulTail'],
        TokenType.BOOL_LITERAL: ['Unary', 'MulTail'],
        TokenType.IDENTIFIER: ['Unary', 'MulTail']
    },
    'MulTail': {
        TokenType.MULT: [TokenType.MULT, 'Unary', 'MulTail'],
        TokenType.DIV: [TokenType.DIV, 'Unary', 'MulTail'],
        TokenType.MOD: [TokenType.MOD, 'Unary', 'MulTail'],
        TokenType.PLUS: [EPSILON],
        TokenType.MINUS: [EPSILON],
        TokenType.CONCAT: [EPSILON],
        TokenType.EQ: [EPSILON],
        TokenType.NEQ: [EPSILON],
        TokenType.LT: [EPSILON],
        TokenType.GT: [EPSILON],
        TokenType.LE: [EPSILON],
        TokenType.GE: [EPSILON],
        TokenType.AND: [EPSILON],
        TokenType.OR: [EPSILON],
        TokenType.SEMICOLON: [EPSILON],
        TokenType.RPAREN: [EPSILON],
        TokenType.RBRACE: [EPSILON]
    },
    'Unary': {
        TokenType.NOT: [TokenType.NOT, 'Unary'],
        TokenType.MINUS: [TokenType.MINUS, 'Unary'],
        TokenType.LPAREN: ['Primary'],
        TokenType.INT_LITERAL: ['Primary'],
        TokenType.FLOAT_LITERAL: ['Primary'],
        TokenType.STRING_LITERAL: ['Primary'],
        TokenType.BOOL_LITERAL: ['Primary'],
        TokenType.IDENTIFIER: ['Primary']
    },
    'Primary': {
        TokenType.INT_LITERAL: [TokenType.INT_LITERAL],
        TokenType.FLOAT_LITERAL: [TokenType.FLOAT_LITERAL],
        TokenType.STRING_LITERAL: [TokenType.STRING_LITERAL],
        TokenType.BOOL_LITERAL: [TokenType.BOOL_LITERAL],
        TokenType.IDENTIFIER: [TokenType.IDENTIFIER],
        TokenType.LPAREN: [TokenType.LPAREN, 'Expr', TokenType.RPAREN]
    }
}
