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

from enums.enums import SemanticErrorType, SyntaxErrorType, Token, TokenType

DEBUG = True


# ----------------------------
#  Nodos del AST
# ----------------------------
class ASTNode:
    def print(self, level: int = 0) -> str:
        raise NotImplementedError


@dataclass
class ListLiteralNode(ASTNode):
    elements: List[ASTNode]

    def print(self, level: int = 0) -> str:
        elements_str = "\n".join([elem.print(level + 1) for elem in self.elements])
        return f"{'  '*level}ListLiteral:\n{elements_str}"


@dataclass
class ArrayTypeNode(ASTNode):
    base_type: str
    dimensions: List[Optional[int]]  # None = dimensión dinámica

    def print(self, level: int = 0) -> str:
        dims = "".join(f"[{dim if dim else ''}]" for dim in self.dimensions)
        return f"{'  '*level}ArrayType: {self.base_type}{dims}"


@dataclass
class ArrayLiteralNode(ASTNode):
    elements: List[ASTNode]
    inferred_type: Optional[str] = None


@dataclass
class FunctionCallNode(ASTNode):
    function: ASTNode  # MemberAccessNode o IdentifierNode
    arguments: List[ASTNode]
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
        # self.current_token : Token = None
        self.errors = []
        self.symbol_table = {}
        self.advance()

    def validate_array_assignment(
        self, identifier: str, array_type: ArrayTypeNode, literal: ListLiteralNode
    ):
        # Verificar tamaño si es array estático
        if array_type.dimensions and array_type.dimensions[0] is not None:
            expected_size = array_type.dimensions[0]
            if len(literal.elements) != expected_size:
                self.log_error(
                    SemanticErrorType.ARRAY_SIZE_MISMATCH,
                    f"Array '{identifier}' expects {expected_size} elements, got {len(literal.elements)}",
                )

        # Verificar tipos de elementos
        for element in literal.elements:
            if not self.type_matches(element, array_type.base_type):
                self.log_error(
                    SemanticErrorType.ARRAY_TYPE_MISMATCH,
                    f"Array '{identifier}' expects {array_type.base_type}, found {self.get_type(element)}",
                )

    def parse_array_declaration(self, identifier: str):
        # Analizar dimensiones
        dims = []
        while self.current_token.type == TokenType.LBRACKET:
            self.advance()
            if self.current_token.type == TokenType.INT_LITERAL:
                dims.append(int(self.current_token.value))
                self.advance()
            else:
                dims.append(None)  # Dimensión dinámica
            self.expect(TokenType.RBRACKET, SyntaxErrorType.UNCLOSED_BRACKET)

        # Registrar declaración
        self.array_declarations[identifier] = (current_type, dims)

    def validate_array_literal(self, identifier: str, literal: ArrayLiteralNode):
        declared_type, declared_dims = self.array_declarations.get(
            identifier, (None, None)
        )

        # Verificar tipo
        for element in literal.elements:
            if not self.type_check(element, declared_type):
                self.log_error(
                    SemanticErrorType.ARRAY_TYPE_MISMATCH,
                    f"Expected {declared_type}, got {element.inferred_type}",
                )

        # Verificar tamaño si es array estático
        if None not in declared_dims:
            expected_size = reduce(lambda x, y: x * y, declared_dims)
            if len(literal.elements) != expected_size:
                self.log_error(
                    SemanticErrorType.ARRAY_SIZE_MISMATCH,
                    f"Expected {expected_size} elements, got {len(literal.elements)}",
                )

    def type_check(self, node: ASTNode, expected_type: str) -> bool:
        if isinstance(node, LiteralNode):
            return node.literal_type == expected_type
        elif isinstance(node, IdentifierNode):
            var_type, _ = self.array_declarations.get(node.name, (None, None))
            return var_type == expected_type
        return False

    def parse_function_call(self, func: ASTNode) -> ASTNode:
        self.advance()  # Consume (
        args = self.parse_arguments()
        self.expect(TokenType.RPAREN, SyntaxErrorType.UNCLOSED_PAREN)
        return FunctionCallNode(func, args)

    def parse_member_access(self, obj: ASTNode) -> ASTNode:
        self.advance()  # Consume .
        member = self.current_token.value
        self.expect(TokenType.IDENTIFIER, SyntaxErrorType.UNEXPECTED_TOKEN)
        return MemberAccessNode(obj, member)

    def parse_arguments(self) -> List[ASTNode]:
        args = []
        if self.current_token.type == TokenType.RPAREN:
            return args

        args.append(self.parse_expression())
        while self.current_token.type == TokenType.COMMA:
            self.advance()
            args.append(self.parse_expression())

        return args

    def parse_list_literal(self) -> ListLiteralNode:
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

    def parse_postfix(self, primary: ASTNode) -> ASTNode:
        current_node = primary
        while True:
            if self.current_token.type == TokenType.DOT:
                current_node = self.parse_member_access(current_node)
            elif self.current_token.type == TokenType.LBRACKET:
                current_node = self.parse_array_access(current_node)
            elif self.current_token.type == TokenType.LPAREN:
                current_node = self.parse_function_call(current_node)
            else:
                break
        return current_node

    # def parse_type(self) -> str:
    #     type_token = self.current_token
    #     if type_token.type not in {
    #         TokenType.VIDEO_TYPE,
    #         TokenType.STRING_TYPE,
    #         TokenType.INT_TYPE,
    #         TokenType.FLOAT_TYPE,
    #         TokenType.BOOL_TYPE,
    #     }:
    #         self.log_error(SyntaxErrorType.INVALID_OPERATION, "valid type")
    #         self.synchronize()
    #         return "unknown"

    #     self.advance()
    #     array_dims = []
    #     while self.current_token.type == TokenType.LBRACKET:
    #         self.advance()
    #         if not self.current_token.type == TokenType.INT_LITERAL:
    #             self.log_error(
    #                 SyntaxErrorType.INVALID_OPERATION, "integer literal for array size"
    #             )
    #         array_dims.append(self.current_token.value)
    #         self.advance()
    #         if not self.expect(TokenType.RBRACKET, SyntaxErrorType.UNCLOSED_BRACKET):
    #             self.synchronize()

    #     return f"{type_token.value}{''.join(f'[{dim}]' for dim in array_dims)}"

    def parse_type(self) -> ArrayTypeNode:
        base_type = self.current_token.value
        self.advance()

        dimensions = []
        while self.current_token.type == TokenType.LBRACKET:
            self.advance()  # Consume [
            dimensions.append(
                int(self.current_token.value)
                if self.current_token.type == TokenType.INT_LITERAL
                else None
            )
            self.advance()  # Consume tamaño o ]
            self.expect(TokenType.RBRACKET, SyntaxErrorType.UNCLOSED_BRACKET)

        return ArrayTypeNode(base_type, dimensions)

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

    def log_error(self, error_type: SemanticErrorType, context: str = ""):
        msg = f"{error_type.value} at line {self.current_token.line}"
        if context:
            msg += f" ({context})"
        self.errors.append(msg)
        print(f"SEMANTIC ERROR: {msg}")

    def synchronize(self):
        sync_tokens = {
            TokenType.SEMICOLON,
            TokenType.RBRACE,
            TokenType.LBRACE,
            TokenType.EOF,
            TokenType.IF,
            TokenType.WHILE,
        }

        skip_tokens = {
            TokenType.SEMICOLON,
            TokenType.RBRACE,
            TokenType.LBRACE,
            TokenType.EOF,
        }
        while self.current_token and self.current_token.type not in skip_tokens:
            self.advance()

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
        if self.current_token.type == TokenType.LBRACKET:
            return self.parse_list_literal()
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

    def validate_array_declaration(
        self, identifier: str, array_type: ArrayTypeNode, literal: ListLiteralNode
    ):
        # Verificar cantidad de dimensiones
        if len(array_type.dimensions) != 1:
            self.log_error(
                SemanticErrorType.INVALID_ARRAY_DECLARATION,
                f"Expected 1D array, got {len(array_type.dimensions)}D",
            )

        # Verificar tamaño si es array estático
        declared_size = array_type.dimensions[0]
        if declared_size is not None and len(literal.elements) != declared_size:
            self.log_error(
                SemanticErrorType.ARRAY_SIZE_MISMATCH,
                f"Declared size {declared_size}, got {len(literal.elements)}",
            )

        # Verificar tipos de elementos
        for element in literal.elements:
            if not self.check_type(element, array_type.base_type):
                self.log_error(
                    SemanticErrorType.ARRAY_TYPE_MISMATCH,
                    f"Expected {array_type.base_type}, got {element.inferred_type}",
                )


# ----------------------------
#  Ejemplo de Uso
# ----------------------------


def main():
    from lexer import Lexer, TokenType  # Asumiendo el lexer anterior

    try:
        with open("tests/direct_debug_comment.vid", "r", encoding="utf-8") as f:
            # with open("tests/direct_debug_comment_good.vid", "r", encoding="utf-8") as f:
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
