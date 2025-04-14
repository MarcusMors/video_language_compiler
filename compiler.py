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

from enums.enums import *


class Compiler:
  def __init__(self, t_input_file : str, t_output_file: str, t_verbose:list[str]):
    self.input_file =t_input_file
    self.output_file =t_output_file
    # self.verbose =t_verbose
    # self.
  def compile(self):
    # Lexer is used in the scanner
    # tokens = scanner(input_file)
    # AST = parser(tokens)
    # Elaboration
    
    # scanner(input_files).parser() ????? this sintax is possible i think
    
    # Optimizations
    
    # Inst Selection
    # Inst Scheduling
    # Reg Allocation
    
    
  def FE_Scanner(self,):
    pass
  def FE_Parser(self,):
    pass
  def FE_Elaboration(self,):
    pass
