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

import sys
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from sympy import true

from enums.enums import SyntaxErrorType, Token, TokenType

DEBUG = True

# ----------------------------
#  Nodos del AST
# ----------------------------
class ASTNode:
    def print(self, level: int = 0) -> str:
        raise NotImplementedError


@dataclass
class FunctionCallNode(ASTNode):
    func_name: str
    args: List[ASTNode]
    postfix: List[ASTNode]

    def print(self, level: int = 0) -> str:
        args_str = "\n".join(arg.print(level + 2) for arg in self.args)
        postfix_str = "\n".join(p.print(level + 2) for p in self.postfix)
        return (
            f"{'  '*level}FunctionCall: {self.func_name}\n"
            f"{'  '*(level+1)}Arguments:\n{args_str}"
            f"\n{'  '*(level+1)}Postfix:\n{postfix_str}"
        )


@dataclass
class ArrayAccessNode(ASTNode):
    array: ASTNode
    index: ASTNode

    def print(self, level: int = 0) -> str:
        return (
            f"{'  '*level}ArrayAccess:\n"
            f"{self.array.print(level+1)}"
            f"{self.index.print(level+1)}"
        )


@dataclass
class MemberAccessNode(ASTNode):
    object: ASTNode
    member: str

    def print(self, level: int = 0) -> str:
        return f"{'  '*level}MemberAccess: {self.member}\n{self.object.print(level+1)}"


@dataclass
class ConditionalNode(ASTNode):
    condition: ASTNode
    then_block: ASTNode
    else_block: Optional[ASTNode]

    def print(self, level: int = 0) -> str:
        result = f"{'  '*level}If:\n{'  '*(level+1)}Condition:\n{self.condition.print(level+2)}"
        result += f"\n{'  '*(level+1)}Then:\n{self.then_block.print(level+2)}"
        if self.else_block:
            result += f"\n{'  '*(level+1)}Else:\n{self.else_block.print(level+2)}"
        return result + "\n"


@dataclass
class LoopNode(ASTNode):
    condition: ASTNode
    body: ASTNode

    def print(self, level: int = 0) -> str:
        return (
            f"{'  '*level}While:\n{'  '*(level+1)}Condition:\n{self.condition.print(level+2)}"
            f"\n{'  '*(level+1)}Body:\n{self.body.print(level+2)}\n"
        )


@dataclass
class ProgramNode(ASTNode):
    body: "BlockNode"

    def print(self, level: int = 0) -> str:
        return f"Program\n{self.body.print(level+1)}"


@dataclass
class BlockNode(ASTNode):
    statements: List[ASTNode]

    def print(self, level: int = 0) -> str:
        result = " " * level + "Block:\n"
        for stmt in self.statements:
            result += stmt.print(level + 1)
        return result


@dataclass
class DeclarationNode(ASTNode):
    identifier: str
    var_type: str
    value: Optional[ASTNode]

    def print(self, level: int = 0) -> str:
        value_str = (
            f"\n{'  '*(level+1)}Value: {self.value.print(level+2)}"
            if self.value
            else ""
        )
        return f"{'  '*level}Declare {self.identifier}: {self.var_type}{value_str}\n"


@dataclass
class AssignmentNode(ASTNode):
    identifier: str
    value: ASTNode

    def print(self, level: int = 0) -> str:
        return f"{'  '*level}Assign {self.identifier} =\n{self.value.print(level+2)}\n"


@dataclass
class BinaryOpNode(ASTNode):
    left: ASTNode
    op: str
    right: ASTNode

    def print(self, level: int = 0) -> str:
        return (
            f"{'  '*level}BinaryOp ({self.op}):\n"
            f"{self.left.print(level+1)}"
            f"{self.right.print(level+1)}"
        )


@dataclass
class IdentifierNode(ASTNode):
    name: str

    def print(self, level: int = 0) -> str:
        return f"{'  '*level}Identifier: {self.name}\n"


@dataclass
class LiteralNode(ASTNode):
    value: Any
    literal_type: str

    def print(self, level: int = 0) -> str:
        return f"{'  '*level}Literal ({self.literal_type}): {self.value}\n"


# ----------------------------
#  Parser LL(1)
# ----------------------------
class Parser:
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = None
        self.errors = []
        self.symbol_table = {}
        self.advance()

    def parse_function_call(self, identifier: ASTNode) -> ASTNode:
        self.advance()  # Consume (
        args = self.parse_arguments()
        if not self.expect(TokenType.RPAREN, SyntaxErrorType.UNCLOSED_PAREN):
            self.synchronize()

        postfix = []
        while self.current_token.type in {TokenType.DOT, TokenType.LBRACKET}:
            if self.current_token.type == TokenType.DOT:
                postfix.append(self.parse_member_access())
            else:
                postfix.append(self.parse_array_access(IdentifierNode(identifier.name)))

        return FunctionCallNode(identifier.name, args, postfix)

    def parse_member_access(self) -> MemberAccessNode:
        self.advance()  # Consume .
        member = self.current_token.value
        if not self.expect(TokenType.IDENTIFIER, SyntaxErrorType.UNEXPECTED_TOKEN):
            self.synchronize()
            return MemberAccessNode(None, "error")
        return MemberAccessNode(None, member)

    def parse_arguments(self) -> List[ASTNode]:
        args = []
        if self.current_token.type == TokenType.RPAREN:
            return args

        args.append(self.parse_expression())
        while self.current_token.type == TokenType.COMMA:
            self.advance()
            args.append(self.parse_expression())

        return args

    def parse_list_literal(self) -> ASTNode:
        self.advance()  # Consume [
        elements = []

        if self.current_token.type != TokenType.RBRACKET:
            elements.append(self.parse_expression())
            while self.current_token.type == TokenType.COMMA:
                self.advance()
                elements.append(self.parse_expression())

        if not self.expect(TokenType.RBRACKET, SyntaxErrorType.UNCLOSED_BRACKET):
            self.synchronize()

        return ListLiteralNode(elements)

    def parse_postfix(self, identifier: ASTNode) -> ASTNode:
        current_node = identifier
        while self.current_token.type in {TokenType.DOT, TokenType.LBRACKET}:
            if self.current_token.type == TokenType.DOT:
                self.advance()  # Consume .
                member = self.current_token.value
                self.expect(TokenType.IDENTIFIER, SyntaxErrorType.UNEXPECTED_TOKEN)
                current_node = MemberAccessNode(current_node, member)
            elif self.current_token.type == TokenType.LBRACKET:
                current_node = self.parse_array_access(current_node)
        return current_node

    def parse_type(self) -> str:
        type_token = self.current_token
        if type_token.type not in {
            TokenType.VIDEO_TYPE,
            TokenType.STRING_TYPE,
            TokenType.INT_TYPE,
            TokenType.FLOAT_TYPE,
            TokenType.BOOL_TYPE,
        }:
            self.log_error(SyntaxErrorType.INVALID_OPERATION, "valid type")
            self.synchronize()
            return "unknown"

        self.advance()
        array_dims = []
        while self.current_token.type == TokenType.LBRACKET:
            self.advance()
            if not self.current_token.type == TokenType.INT_LITERAL:
                self.log_error(
                    SyntaxErrorType.INVALID_OPERATION, "integer literal for array size"
                )
            array_dims.append(self.current_token.value)
            self.advance()
            if not self.expect(TokenType.RBRACKET, SyntaxErrorType.UNCLOSED_BRACKET):
                self.synchronize()

        return f"{type_token.value}{''.join(f'[{dim}]' for dim in array_dims)}"

    def parse_literal(self) -> ASTNode:
        if self.current_token.type == TokenType.LBRACKET:
            return self.parse_list_literal()

        token = self.current_token
        self.advance()
        return LiteralNode(token.value, token.type.name.replace("_LITERAL", "").lower())

    def parse_conditional(self) -> Optional[ASTNode]:
        if not self.expect(TokenType.IF, SyntaxErrorType.UNEXPECTED_TOKEN):
            return None

        self.expect(TokenType.LPAREN, SyntaxErrorType.UNCLOSED_PAREN)
        condition = self.parse_expression()
        self.expect(TokenType.RPAREN, SyntaxErrorType.UNCLOSED_PAREN)
        self.expect(TokenType.LBRACE, SyntaxErrorType.UNCLOSED_BRACE)
        then_block = self.parse_block()
        self.expect(TokenType.RBRACE, SyntaxErrorType.UNCLOSED_BRACE)

        else_block = None
        if self.current_token.type == TokenType.ELSE:
            self.advance()
            self.expect(TokenType.LBRACE, SyntaxErrorType.UNCLOSED_BRACE)
            else_block = self.parse_block()
            self.expect(TokenType.RBRACE, SyntaxErrorType.UNCLOSED_BRACE)

        return ConditionalNode(condition, then_block, else_block)

    def parse_loop(self) -> Optional[ASTNode]:
        if not self.expect(TokenType.WHILE, SyntaxErrorType.UNEXPECTED_TOKEN):
            return None

        self.expect(TokenType.LPAREN, SyntaxErrorType.UNCLOSED_PAREN)
        condition = self.parse_expression()
        self.expect(TokenType.RPAREN, SyntaxErrorType.UNCLOSED_PAREN)
        self.expect(TokenType.LBRACE, SyntaxErrorType.UNCLOSED_BRACE)
        body = self.parse_block()
        self.expect(TokenType.RBRACE, SyntaxErrorType.UNCLOSED_BRACE)

        return LoopNode(condition, body)

    def parse_array_access(self, identifier: ASTNode) -> ASTNode:
        self.advance()  # Consume [
        index = self.parse_expression()
        if not self.expect(TokenType.RBRACKET, SyntaxErrorType.UNCLOSED_BRACKET):
            self.synchronize()
        return ArrayAccessNode(identifier, index)

    def advance(self):
        self.current_token = self.lexer.get_token()

    def log_error(self, error_type: SyntaxErrorType, expected: str = None):
        msg = f"Syntax Error [{self.current_token.line}:{self.current_token.column}]: {error_type.value}"
        if expected:
            msg += f". Expected: {expected}"
        self.errors.append(msg)
        print(f"ERROR: {msg}")

    def synchronize(self):
        sync_tokens = {
            TokenType.SEMICOLON,
            TokenType.RBRACE,
            TokenType.LBRACE,
            TokenType.EOF,
            TokenType.IF,
            TokenType.WHILE,
        }

        while self.current_token.type not in sync_tokens:
            if DEBUG:
                print(f"Synchronizing... Skipping {self.current_token}")
            self.advance()

        if self.current_token.type == TokenType.SEMICOLON:
            self.advance()

    def expect(self, token_type: TokenType, error_type: SyntaxErrorType, advance=True):
        if self.current_token.type == token_type:
            if advance:
                self.advance()
            return True
        self.log_error(error_type, token_type.name)
        self.synchronize()
        return False

    def parse(self) -> ProgramNode:
        if not self.expect(TokenType.MAIN, SyntaxErrorType.UNEXPECTED_TOKEN):
            return None

        self.expect(TokenType.COLON, SyntaxErrorType.MISSING_COLON)
        self.expect(TokenType.LPAREN, SyntaxErrorType.UNCLOSED_PAREN)
        self.expect(TokenType.RPAREN, SyntaxErrorType.UNCLOSED_PAREN)

        if not self.expect(TokenType.LBRACE, SyntaxErrorType.UNCLOSED_BRACE):
            return None

        block = self.parse_block()

        if not self.expect(TokenType.RBRACE, SyntaxErrorType.UNCLOSED_BRACE):
            return None

        return ProgramNode(block)

    def parse_block(self) -> BlockNode:
        statements = []
        while self.current_token.type not in {TokenType.RBRACE, TokenType.EOF}:
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        return BlockNode(statements)

    def parse_expression_statement(self) -> Optional[ASTNode]:
        expr = self.parse_expression()
        if not self.expect(TokenType.SEMICOLON, SyntaxErrorType.MISSING_SEMICOLON):
            self.synchronize()
        return expr

    def parse_statement(self) -> Optional[ASTNode]:
        try:
            if self.current_token.type == TokenType.IF:
                return self.parse_conditional()
            elif self.current_token.type == TokenType.WHILE:
                return self.parse_loop()
            elif self.current_token.type == TokenType.IDENTIFIER:
                return self.parse_declaration_or_assignment()
            else:
                return self.parse_expression_statement()
        except Exception as e:
            self.log_error(SyntaxErrorType.UNEXPECTED_TOKEN)
            self.synchronize()
            return None

    def parse_declaration_or_assignment(self) -> ASTNode:
        identifier = self.current_token.value
        self.advance()

        if self.current_token.type == TokenType.COLON:
            return self.parse_declaration(identifier)
        elif self.current_token.type == TokenType.ASSIGN:
            return self.parse_assignment(identifier)
        else:
            self.log_error(SyntaxErrorType.UNEXPECTED_TOKEN, "':' or '='")
            return None

    def parse_declaration(self, identifier: str) -> DeclarationNode:
        self.advance()  # Consume colon

        var_type = self.parse_type()
        value = None

        if self.current_token.type == TokenType.ASSIGN:
            self.advance()
            value = self.parse_expression()

        if not self.expect(TokenType.SEMICOLON, SyntaxErrorType.MISSING_SEMICOLON):
            self.synchronize()

        if identifier in self.symbol_table:
            self.log_error(SyntaxErrorType.DUPLICATE_DECLARATION)
        else:
            self.symbol_table[identifier] = var_type

        return DeclarationNode(identifier, var_type, value)

    def parse_assignment(self, identifier: str) -> AssignmentNode:
        self.advance()  # Consume '='
        value = self.parse_expression()

        if not self.expect(TokenType.SEMICOLON, SyntaxErrorType.MISSING_SEMICOLON):
            self.synchronize()

        if identifier not in self.symbol_table:
            self.log_error(SyntaxErrorType.UNDECLARED_VARIABLE)

        return AssignmentNode(identifier, value)

    def parse_expression(self) -> ASTNode:
        return self.parse_assignment_expression()

    def parse_assignment_expression(self) -> ASTNode:
        left = self.parse_logical_or()

        if self.current_token.type == TokenType.ASSIGN:
            self.advance()
            value = self.parse_assignment_expression()
            return BinaryOpNode(left, "=", value)

        return left

    def parse_logical_or(self) -> ASTNode:
        left = self.parse_logical_and()

        while self.current_token.type == TokenType.OR:
            self.advance()
            right = self.parse_logical_and()
            left = BinaryOpNode(left, "or", right)

        return left

    def parse_logical_and(self) -> ASTNode:
        left = self.parse_equality()

        while self.current_token.type == TokenType.AND:
            self.advance()
            right = self.parse_equality()
            left = BinaryOpNode(left, "and", right)

        return left

    def parse_equality(self) -> ASTNode:
        left = self.parse_relational()

        while self.current_token.type in {TokenType.EQ, TokenType.NEQ}:
            op = self.current_token.value
            self.advance()
            right = self.parse_relational()
            left = BinaryOpNode(left, op, right)

        return left

    def parse_relational(self) -> ASTNode:
        left = self.parse_additive()

        while self.current_token.type in {
            TokenType.LT,
            TokenType.GT,
            TokenType.LE,
            TokenType.GE,
        }:
            op = self.current_token.value
            self.advance()
            right = self.parse_additive()
            left = BinaryOpNode(left, op, right)

        return left

    def parse_additive(self) -> ASTNode:
        left = self.parse_multiplicative()

        while self.current_token.type in {TokenType.PLUS, TokenType.MINUS}:
            op = self.current_token.value
            self.advance()
            right = self.parse_multiplicative()
            left = BinaryOpNode(left, op, right)

        return left

    def parse_multiplicative(self) -> ASTNode:
        left = self.parse_concat()

        while self.current_token.type in {TokenType.MULT, TokenType.DIV, TokenType.MOD}:
            op = self.current_token.value
            self.advance()
            right = self.parse_concat()
            left = BinaryOpNode(left, op, right)

        return left

    def parse_concat(self) -> ASTNode:
        left = self.parse_unary()

        while self.current_token.type == TokenType.CONCAT:
            self.advance()
            right = self.parse_unary()
            left = BinaryOpNode(left, "++", right)

        return left

    def parse_unary(self) -> ASTNode:
        if self.current_token.type in {
            TokenType.NOT,
            TokenType.MINUS,
            TokenType.CONCAT,
        }:
            op = self.current_token.value
            self.advance()
            expr = self.parse_primary()
            return BinaryOpNode(None, op, expr)
        return self.parse_primary()

    def parse_array_access(self, identifier: ASTNode) -> ASTNode:
        self.advance()  # Consume [
        index = self.parse_expression()
        if not self.expect(TokenType.RBRACKET, SyntaxErrorType.UNCLOSED_BRACKET):
            self.synchronize()
        return ArrayAccessNode(identifier, index)

    def parse_primary(self) -> ASTNode:
        if self.current_token.type == TokenType.IDENTIFIER:
            identifier = self.parse_identifier()
            # Manejar acceso a array
            if self.current_token.type == TokenType.LBRACKET:
                return self.parse_array_access(identifier)
            return identifier
        elif self.current_token.type == TokenType.IDENTIFIER:
            return self.parse_identifier()
        elif self.current_token.type in {
            TokenType.INT_LITERAL,
            TokenType.FLOAT_LITERAL,
            TokenType.STRING_LITERAL,
        }:
            return self.parse_literal()
        else:
            self.log_error(SyntaxErrorType.UNEXPECTED_TOKEN)
            return LiteralNode(None, "error")

    def parse_identifier(self) -> ASTNode:
        identifier = self.current_token.value
        if identifier not in self.symbol_table:
            self.log_error(SyntaxErrorType.UNDECLARED_VARIABLE)
        node = IdentifierNode(identifier)
        self.advance()
        return node

    def parse_literal(self) -> ASTNode:
        token = self.current_token
        self.advance()
        return LiteralNode(token.value, token.type.name.replace("_LITERAL", "").lower())

    def parse_type(self) -> str:
        type_token = self.current_token
        if type_token.type not in {
            TokenType.VIDEO_TYPE,
            TokenType.STRING_TYPE,
            TokenType.INT_TYPE,
            TokenType.FLOAT_TYPE,
            TokenType.BOOL_TYPE,
        }:
            self.log_error(SyntaxErrorType.INVALID_OPERATION, "valid type")
            return "unknown"

        self.advance()
        return type_token.value


# ----------------------------
#  Ejemplo de Uso
# ----------------------------


def main():
    from lexer import Lexer, TokenType  # Asumiendo el lexer anterior

    try:
        # with open("tests/direct_debug_comment.vid", "r", encoding="utf-8") as f:
        with open("tests/direct_debug_comment_good.vid", "r", encoding="utf-8") as f:
            code = f.read()

        print("Analizando archivo direct_debug_comment.vid...\n")
        lexer = Lexer(code)
        parser = Parser(lexer)
        ast = parser.parse()

        print("\nResultado del análisis sintáctico:")
        if ast:
            print(ast.print())

        if parser.errors:
            print(f"\nSe encontraron {len(parser.errors)} errores:")
            for error in parser.errors:
                print(f"• {error}")
        else:
            print("\nAnálisis completado sin errores sintácticos")

    except FileNotFoundError:
        print("Error: Archivo 'direct_debug_comment.vid' no encontrado")
        sys.exit(1)
    except Exception as e:
        print(f"Error inesperado: {str(e)}")
        sys.exit(2)


if __name__ == "__main__":
    main()
