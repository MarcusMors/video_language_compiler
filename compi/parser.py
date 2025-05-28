# parser.py - Versión final corregida
# ----------------------------------------------------------------
from typing import List, Dict, Set
from dataclasses import dataclass
from enums import Token, TokenType, KEYWORDS, symbols, compound_ops
from grammar_def import PARSING_TABLE, START_SYMBOL, EPSILON

def _build_symbol_map() -> Dict[TokenType, str]:
    m: Dict[TokenType, str] = {}
    for lex, tt in symbols.items():
        m[tt] = lex
    for lex, tt in compound_ops.items():
        m[tt] = lex
    for lex, tt in KEYWORDS.items():
        if tt not in m:
            m[tt] = lex
    m[TokenType.DEBUG_OUTPUT] = "@"
    return m

TOKEN_SIMBOLO = _build_symbol_map()

def token_repr(tt: TokenType, lexema: str = "") -> str:
    base = TOKEN_SIMBOLO.get(tt)
    if base:
        return f"{tt.name} '{base}'"
    if lexema and tt in {
        TokenType.IDENTIFIER,
        TokenType.INT_LITERAL, TokenType.FLOAT_LITERAL,
        TokenType.STRING_LITERAL, TokenType.BOOL_LITERAL
    }:
        return f"{tt.name} («{lexema}»)"
    return tt.name

@dataclass
class ErrorSintactico:
    linea: int
    columna: int
    esperados: List[TokenType]
    encontrado: Token

    def __str__(self) -> str:
        esp = ", ".join(token_repr(t) for t in self.esperados)
        enc = token_repr(self.encontrado.type, self.encontrado.value)
        return f"Error en {self.linea}:{self.columna} → Esperaba {esp}, encontré {enc}"

class ParserLL1:
    def __init__(self, tokens: List[Token]) -> None:
        self.tokens = tokens
        self.pos = 0
        self.actual = tokens[0] if tokens else Token(TokenType.EOF, "", 0, 0)
        self.pila = [TokenType.EOF, START_SYMBOL]
        self.errores: List[ErrorSintactico] = []
        self.braces = 0
        self.max_errores = 20
        self.en_main_decl = False

    def _avanzar(self) -> None:
        if self.actual.type == TokenType.LBRACE:
            self.braces += 1
        elif self.actual.type == TokenType.RBRACE:
            self.braces -= 1
        self.pos += 1
        self.actual = self.tokens[self.pos] if self.pos < len(self.tokens) else \
                     Token(TokenType.EOF, "", self.actual.line, self.actual.column + 1)

    def _recuperar_error(self, sync_tokens: Set[TokenType]) -> None:
        while (self.actual.type not in sync_tokens and 
               self.pos < len(self.tokens) and 
               len(self.errores) < self.max_errores):
            self._avanzar()

    def _manejar_main_alternativo(self) -> bool:
        """Maneja la sintaxis main() como alternativa especial"""
        if (self.en_main_decl and 
            self.actual.type == TokenType.LPAREN and
            len(self.pila) > 0 and self.pila[-1] == TokenType.COLON):
            
            # Saltar los tokens de main() y continuar
            self._avanzar()  # Saltar '('
            while self.actual.type not in [TokenType.RPAREN, TokenType.EOF]:
                self._avanzar()
            if self.actual.type == TokenType.RPAREN:
                self._avanzar()  # Saltar ')'
            
            # Reconstruir la pila correctamente para lo que sigue
            self.pila = [s for s in self.pila if s != TokenType.COLON]
            if self.actual.type == TokenType.LBRACE:
                self.pila.extend(reversed([TokenType.RBRACE, 'Block', TokenType.LBRACE]))
            return True
        return False

    def _registrar_error(self, esperados: List[TokenType]) -> None:
        if len(self.errores) >= self.max_errores:
            return
            
        # Manejar main() como caso especial primero
        if self._manejar_main_alternativo():
            return
            
        # Filtrar tokens irrelevantes para mensajes de error
        esperados_filtrados = [
            tt for tt in esperados 
            if tt not in [TokenType.EOF, TokenType.RBRACE, TokenType.SEMICOLON, TokenType.LPAREN]
        ]
        
        if not esperados_filtrados:
            return
            
        if not any(e.linea == self.actual.line and abs(e.columna - self.actual.column) <= 2 
                  for e in self.errores):
            self.errores.append(ErrorSintactico(
                self.actual.line,
                self.actual.column,
                esperados_filtrados,
                self.actual
            ))

    def parse(self) -> bool:
        sync_global = {TokenType.SEMICOLON, TokenType.RBRACE, TokenType.EOF, TokenType.LBRACE}
        
        while self.pila and len(self.errores) < self.max_errores:
            cima = self.pila.pop()

            if isinstance(cima, TokenType):
                if self.actual.type == cima:
                    self._avanzar()
                else:
                    self._registrar_error([cima])
                    self._recuperar_error(sync_global)
                    continue

            elif cima == EPSILON:
                continue

            else:
                if cima == 'MainDecl':
                    self.en_main_decl = True
                    
                producciones = PARSING_TABLE.get(cima, {})
                produccion = producciones.get(self.actual.type)
                
                if produccion is None:
                    esperados = list(producciones.keys())
                    self._registrar_error(esperados)
                    
                    sync_local = sync_global.copy()
                    if cima in ['Stmt', 'StmtList']:
                        sync_local.update({TokenType.RBRACE, TokenType.SEMICOLON})
                    elif cima == 'MainDecl':
                        sync_local.add(TokenType.LBRACE)
                    
                    self._recuperar_error(sync_local)
                    continue
                
                for simbolo in reversed(produccion):
                    if simbolo != EPSILON:
                        self.pila.append(simbolo)
                
                if cima == 'MainDecl':
                    self.en_main_decl = False

        if self.braces > 0 and len(self.errores) < self.max_errores:
            self.errores.append(ErrorSintactico(
                self.actual.line, self.actual.column,
                [TokenType.RBRACE],
                Token(TokenType.EOF, "", self.actual.line, self.actual.column)
            ))

        return not self.errores

    def imprimir_errores(self) -> None:
        if not self.errores:
            print("\n✓ Análisis sintáctico correcto")
            return
            
        print(f"\n✗ Errores sintácticos encontrados ({len(self.errores)}):")
        for i, error in enumerate(self.errores, 1):
            print(f"{i}. {error}")
        
        if len(self.errores) >= self.max_errores:
            print(f"\n⚠ Se alcanzó el límite máximo de {self.max_errores} errores")

def analizar_archivo(ruta: str) -> None:
    from lexer import Lexer
    
    try:
        with open(ruta, encoding='utf-8') as f:
            codigo = f.read()
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{ruta}'")
        return

    lexer = Lexer(codigo)
    tokens = lexer.tokenize()
    
    if lexer.errors:
        print("\n--- ERRORES LÉXICOS ---")
        for error in lexer.errors[:10]:
            print(f"  {error}")
        if len(lexer.errors) > 10:
            print(f"  ... ({len(lexer.errors) - 10} errores más)")

    parser = ParserLL1(tokens)
    parser.parse()
    parser.imprimir_errores()

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Uso: python parser.py <archivo.txt>")
        sys.exit(1)
    
    analizar_archivo(sys.argv[1])