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

from parser import Parser, print_ast

from lexer import Lexer

with open("tests/ejemplo1.vid") as f:
    lexer = Lexer(f.read())
    parser = Parser(lexer)
    ast = parser.parse()

    if parser.errors:
        print("Errors found:")
        for error in parser.errors:
            print(error)
    else:
        print("\nAbstract Syntax Tree:")
        print_ast(ast)
