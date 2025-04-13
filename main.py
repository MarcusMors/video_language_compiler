# ---------------------------------------------------------------------------
# scanner.py
# Ejemplo de un analizador léxico (scanner) en Python
# ---------------------------------------------------------------------------


# 1) Definición de categorías léxicas (tokens) y otras constantes


# Palabras clave que reconocerás en tu lenguaje
KEYWORDS = {
    "if", "else", "while", "for",
    "int", "float", "video", "bool", "print",
}


# Operadores. Incluimos algunos de doble carácter: ==, //
OPERATORS = {
    "=", "+", "-", "*", "/", "==", "//"
}


# Separadores y símbolos
SEPARATORS = {
    "(", ")", "{", "}", ";", ",", ":", "[", "]"
}


# Caracteres usados para terminar un string, o para comentarios
STRING_DELIMITER = '"'


# 2) Clase Fuente: implementa getchar() y peekchar()


class Fuente:
    """
    Clase que modela la fuente de caracteres. Mantiene un índice
    que se mueve a medida que se leen caracteres.
    """
    def __init__(self, texto):
        self.texto = texto
        self.pos = 0
        self.longitud = len(texto)


    def getchar(self):
        """
        Retorna el carácter actual y avanza el índice.
        Retorna None si se acabó el texto.
        """
        if self.pos >= self.longitud:
            return None
        c = self.texto[self.pos]
        self.pos += 1
        return c


    def peekchar(self):
        """
        Retorna el carácter actual sin avanzar el índice.
        Retorna None si se acabó el texto.
        """
        if self.pos >= self.longitud:
            return None
        return self.texto[self.pos]




# 3) Clase Token


class Token:
    def __init__(self, tipo, valor, linea, columna):
        self.tipo = tipo       # Ej: KEYWORD, IDENTIFIER, NUMBER, etc.
        self.valor = valor     # Cadena concreta del token
        self.linea = linea     # Número de línea en el archivo
        self.columna = columna # Número de columna en la línea


    def __repr__(self):
        return f"Token({self.tipo}, '{self.valor}', {self.linea}:{self.columna})"




# 4) Clase Scanner


class Scanner:
    """
    Clase principal que hace el análisis léxico. Usa un objeto Fuente para
    obtener caracteres mediante getchar() y peekchar().
    """
    def __init__(self, fuente: Fuente):
        self.fuente = fuente
        # Usamos estos contadores para ubicar línea y columna
        self.linea = 1
        self.columna = 1
        self.errores = 0  # Para contabilizar errores léxicos


    def avanzar(self):
        """
        Lee el siguiente carácter de la fuente, actualiza línea y columna.
        """
        c = self.fuente.getchar()
        if c == '\n':
            self.linea += 1
            self.columna = 1
        else:
            self.columna += 1
        return c


    def mirar(self):
        """
        Retorna el siguiente carácter sin consumirlo (sin avanzar).
        """
        return self.fuente.peekchar()


    def reportar_error(self, mensaje):
        print(f"[Error léxico] Línea {self.linea}, Col {self.columna}: {mensaje}")
        self.errores += 1


    def saltar_espacios_blancos(self):
        """
        Avanza mientras el carácter actual sea un espacio, tab o newline.
        """
        c = self.mirar()
        while c is not None and c.isspace():
            self.avanzar()
            c = self.mirar()


    def saltar_comentarios(self):
        """
        Maneja comentarios de una línea (//) o multilinea (/* ... */) si quisieras.
        En este ejemplo usaré tipo Python: '#' para 1 línea,
        y '//' también como 1 línea, para mostrar variedad.
        """
        while True:
            c = self.mirar()
            # Comentario estilo Python
            if c == '#':
                # Consumir hasta fin de línea
                while c is not None and c != '\n':
                    self.avanzar()
                    c = self.mirar()
            # Comentario estilo C++ (una línea)
            elif c == '/':
                # Revisar si el siguiente es '/'
                siguiente = self.fuente.texto[self.fuente.pos+1] if (self.fuente.pos+1) < self.fuente.longitud else None
                if siguiente == '/':
                    # Consumir hasta fin de línea
                    while c is not None and c != '\n':
                        self.avanzar()
                        c = self.mirar()
                else:
                    break  # No es comentario
            else:
                break
            # Consumimos posibles saltos de línea y espacios
            self.saltar_espacios_blancos()


    def gettoken(self):
        """
        Método principal que retorna el siguiente token.
        Llamará a saltar_espacios_blancos y saltar_comentarios antes de tokenizar.
        """
        # 1) Saltar espacios y comentarios
        self.saltar_espacios_blancos()
        self.saltar_comentarios()
        self.saltar_espacios_blancos()


        # 2) Verificar si llegamos al final del archivo
        c = self.mirar()
        if c is None:
            return Token("EOF", "", self.linea, self.columna)


        # 3) Consumimos el primer caracter para analizar
        c = self.avanzar()
        inicio_linea, inicio_columna = self.linea, self.columna


        # 4) Identificadores / Palabras clave (empiezan con letra o '_')
        if c.isalpha() or c == '_':
            lexema = c
            while True:
                nxt = self.mirar()
                if nxt is not None and (nxt.isalnum() or nxt == '_'):
                    lexema += self.avanzar()
                else:
                    break
            # Verificamos si es una palabra clave
            if lexema in KEYWORDS:
                return Token("KEYWORD", lexema, inicio_linea, inicio_columna)
            else:
                return Token("IDENTIFIER", lexema, inicio_linea, inicio_columna)


        # 5) Números (solo enteros en este ejemplo)
        elif c.isdigit():
            lexema = c
            while True:
                nxt = self.mirar()
                if nxt is not None and nxt.isdigit():
                    lexema += self.avanzar()
                else:
                    break
            return Token("NUMBER", lexema, inicio_linea, inicio_columna)


        # 6) Cadenas (Strings) - digamos delimitadas por comillas "
        elif c == STRING_DELIMITER:
            lexema = ""
            # Consumir hasta la siguiente comilla o EOF
            while True:
                nxt = self.mirar()
                if nxt is None:
                    # Se acabó el archivo y no cerramos comillas -> error
                    self.reportar_error("String no cerrado antes de EOF.")
                    return Token("STRING", lexema, inicio_linea, inicio_columna)
                elif nxt == STRING_DELIMITER:
                    # Consumimos la comilla de cierre y salimos
                    self.avanzar()
                    break
                else:
                    lexema += self.avanzar()
            return Token("STRING", lexema, inicio_linea, inicio_columna)


        # 7) Operadores (incluyendo doble carácter como '==', '//')
        #    Observa que ya consumimos el 1er carácter en c. Miremos el siguiente
        #    para ver si forma un operador doble.
        possible_double = c + (self.mirar() or "")
        if possible_double in OPERATORS:
            # Consumimos el segundo carácter
            self.avanzar()
            return Token("OPERATOR", possible_double, inicio_linea, inicio_columna)


        # 7b) Si no era doble, verificamos si c es un operador simple
        if c in OPERATORS:
            return Token("OPERATOR", c, inicio_linea, inicio_columna)


        # 8) Separadores
        if c in SEPARATORS:
            return Token("SEPARATOR", c, inicio_linea, inicio_columna)


        # 9) Si llegamos aquí, es un carácter desconocido
        self.reportar_error(f"Carácter inesperado: '{c}'")
        return Token("UNKNOWN", c, inicio_linea, inicio_columna)




# 5) Función para ejecutar todo el proceso de escaneo de un archivo


def run_scanner(filename):
    """
    Lee el archivo 'filename', crea el scanner y
    va extrayendo tokens hasta encontrar EOF.
    Retorna la lista de tokens generada.
    """
    with open(filename, 'r', encoding='utf-8') as f:
        contenido = f.read()


    fuente = Fuente(contenido)
    scanner = Scanner(fuente)


    tokens = []
    while True:
        tk = scanner.gettoken()
        tokens.append(tk)
        if tk.tipo == "EOF":
            break


    # Podemos imprimir cuántos errores hubo
    print(f"\nSe encontraron {scanner.errores} errores léxicos.\n")
    return tokens




# 6) Prueba rápida cuando se ejecuta este archivo directamente


if __name__ == "__main__":
    # Cambia 'test1.txt' por el nombre de tu archivo de prueba
    nombre_archivo = "test1.txt"
    print(f"Escaneando archivo: {nombre_archivo}")
    resultado = run_scanner(nombre_archivo)
    for token in resultado:
        print(token)
