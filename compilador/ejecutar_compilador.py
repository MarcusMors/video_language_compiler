#!/usr/bin/env python3
# ejecutar_compilador.py

"""
Pipeline completo del compilador:
  1) Análisis léxico    → lexer2.py
  2) Análisis sintáctico → parse_tree.py
  3) Análisis semántico  → ast_semantic.py

Si alguna fase falla (returncode != 0), se detiene y no sigue a la siguiente.
"""

import sys
import subprocess

def main():
    if len(sys.argv) != 2:
        print("Uso: python ejecutar_compilador.py <archivo_fuente>")
        sys.exit(1)

    fuente = sys.argv[1]
    fases = [
        ("análisis léxico",      [sys.executable, "lexer2.py",       fuente]),
        ("análisis sintáctico",  [sys.executable, "parser2.py",   fuente]),
        ("análisis semántico",   [sys.executable, "ast_semantic.py", fuente]),
    ]

    for nombre, cmd in fases:
        print(f"\n=== Iniciando {nombre} ===")
        resultado = subprocess.run(cmd)
        if resultado.returncode != 0:
            print(f"\n*** El {nombre} ha fallado (código {resultado.returncode}). Abortando. ***")
            sys.exit(resultado.returncode)
        else:
            print(f"--- {nombre.capitalize()} completado sin errores. ---")

    print("\n=== ¡Compilación completada con éxito! ===")

if __name__ == "__main__":
    main()
