#!/usr/bin/env python3
# ejecutar_compilador.py

"""
Pipeline completo del compilador:
  1) Análisis léxico    → lexer2.py
  2) Análisis sintáctico → parser2.py
  3) Análisis semántico  → ast_semantic.py
  4) Traducción a Python → translator.py

Si alguna fase falla (returncode != 0), se detiene y no sigue a la siguiente.
El código Python generado se guarda en 'output.py' por defecto.
"""

import sys
import subprocess
import os

def main():
    if len(sys.argv) != 2:
        print("Uso: python ejecutar_compilador.py <archivo_fuente>")
        sys.exit(1)

    fuente = sys.argv[1]
    output_file = "output.py"  # Archivo de salida por defecto
    
    fases = [
        ("análisis léxico",      [sys.executable, "lexer2.py",       fuente]),
        ("análisis sintáctico",  [sys.executable, "parser2.py",      fuente]),
        ("análisis semántico",   [sys.executable, "ast_semantic.py", fuente]),
        ("traducción a Python",  [sys.executable, "translator.py",    fuente, output_file]),
    ]

    # Asegurarse de que el archivo de salida no exista antes de empezar
    if os.path.exists(output_file):
        os.remove(output_file)

    for nombre, cmd in fases:
        print(f"\n=== Iniciando {nombre} ===")
        resultado = subprocess.run(cmd)
        if resultado.returncode != 0:
            print(f"\n*** El {nombre} ha fallado (código {resultado.returncode}). Abortando. ***")
            sys.exit(resultado.returncode)
        else:
            print(f"--- {nombre.capitalize()} completado sin errores. ---")

    if os.path.exists(output_file):
        print(f"\n=== ¡Compilación completada con éxito! ===")
        print(f"Código Python generado en: {output_file}")
    else:
        print("\n*** Error: No se generó el archivo de salida ***")
        sys.exit(1)

if __name__ == "__main__":
    main()
