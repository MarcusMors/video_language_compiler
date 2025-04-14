import enum
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from enums.enums import *

# Configuración de logging
DEBUG = True

class Lexer:
    def __init__(self, input_text: str):
        self.input = input_text
        self.pos = 0
        self.line = 1
        self.column = 1
        self.errors: List[str] = []
    
    def _peek_char(self, lookahead: int = 0) -> Optional[str]:
        pos = self.pos + lookahead
        return self.input[pos] if pos < len(self.input) else None
    
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
      