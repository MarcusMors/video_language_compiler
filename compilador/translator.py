# translator.py
"""
Traductor del AST a código Python usando moviepy.
Este módulo toma el AST generado por ast_semantic.py y lo convierte
en código Python ejecutable que usa la biblioteca moviepy para
manipulación de video.
"""

import sys
from ast_semantic import (
    Program, VarDecl, Assignment, ExportStmt, 
    BinaryOp, Literal, Identifier, VideoFuncCall,
    IfStmt, WhileStmt
)

class Translator:
    def __init__(self):
        self.output = []
        self.indent_level = 0
        self.symbol_table = {}  # Add symbol table to track variable types
        
    def indent(self):
        self.indent_level += 1
        
    def dedent(self):
        self.indent_level -= 1
        
    def write(self, line):
        self.output.append("    " * self.indent_level + line)
        
    def translate(self, ast):
        # Escribir imports necesarios
        self.write("from moviepy.editor import *")
        self.write("from moviepy.video.fx.all import *")
        self.write("from moviepy.audio.fx.all import *")
        self.write("")
        
        # Traducir el programa
        if isinstance(ast, Program):
            for stmt in ast.statements:
                self.translate_statement(stmt)
                
        return "\n".join(self.output)
    
    def translate_statement(self, stmt):
        if isinstance(stmt, VarDecl):
            self.translate_var_decl(stmt)
            # Store variable type in symbol table
            self.symbol_table[stmt.name] = stmt.var_type
        elif isinstance(stmt, Assignment):
            self.translate_assignment(stmt)
        elif isinstance(stmt, ExportStmt):
            self.translate_export(stmt)
        elif isinstance(stmt, IfStmt):
            self.translate_if(stmt)
        elif isinstance(stmt, WhileStmt):
            self.translate_while(stmt)
            
    def translate_var_decl(self, decl):
        init_expr = self.translate_expr(decl.init) if decl.init else "None"
        
        # Manejar tipos especiales
        if decl.var_type == "video":
            self.write(f"{decl.name} = VideoFileClip({init_expr})")
        elif decl.var_type == "audio":
            self.write(f"{decl.name} = AudioFileClip({init_expr})")
        else:
            self.write(f"{decl.name} = {init_expr}")
            
    def translate_assignment(self, assign):
        expr = self.translate_expr(assign.expr)
        self.write(f"{assign.name} = {expr}")
        
    def translate_export(self, export):
        # Asegurarse de que el nombre del archivo tenga comillas
        out_file = export.out_file.strip('"')  # Remover comillas existentes
        # Check variable type in symbol table
        var_type = self.symbol_table.get(export.name)
        if var_type == "audio":
            self.write(f'{export.name}.write_audiofile("{out_file}")')
        else:
            self.write(f'{export.name}.write_videofile("{out_file}")')
        
    def translate_if(self, if_stmt):
        condition = self.translate_expr(if_stmt.condition)
        self.write(f"if {condition}:")
        self.indent()
        for stmt in if_stmt.then_block:
            self.translate_statement(stmt)
        self.dedent()
        
        if if_stmt.else_block:
            self.write("else:")
            self.indent()
            for stmt in if_stmt.else_block:
                self.translate_statement(stmt)
            self.dedent()
            
    def translate_while(self, while_stmt):
        condition = self.translate_expr(while_stmt.condition)
        self.write(f"while {condition}:")
        self.indent()
        for stmt in while_stmt.body:
            self.translate_statement(stmt)
        self.dedent()
        
    def translate_expr(self, expr):
        if expr is None:
            return "None"
        
        if isinstance(expr, BinaryOp):
            left = self.translate_expr(expr.left)
            right = self.translate_expr(expr.right)
            return f"({left} {expr.op} {right})"
        elif isinstance(expr, Literal):
            # Asegurarse de que los strings tengan comillas correctamente
            if expr.lit_type == "string":
                # Remover cualquier comilla existente y agregar una sola vez
                clean_value = expr.value.strip('"')
                return f'"{clean_value}"'
            return expr.value
        elif isinstance(expr, Identifier):
            return expr.name
        elif isinstance(expr, VideoFuncCall):
            try:
                return self.translate_video_func(expr)
            except Exception as e:
                print(f"Error al traducir función de video: {str(e)}")
                return str(expr)
        return str(expr)
    
    def translate_video_func(self, func):
        # Limpiar y formatear argumentos
        def format_arg(arg):
            if isinstance(arg, str) and (arg.startswith('"') or arg.endswith('"')):
                return f'"{arg.strip('"')}"' # Reiniciar comillas
            return arg

        args = [format_arg(self.translate_expr(arg)) for arg in func.args]
        
        # Mapeo de funciones de video a moviepy con validación de argumentos
        video_funcs = {
            "@resize": lambda args: (
                f".resize(width={args[1]}, height={args[2]})" 
                if len(args) >= 3 
                else ".resize()"
            ),
            "@flip": lambda args: (
                f".fx(vfx.mirror_x)" 
                if len(args) > 0 and "horizontal" in args[0].strip('"') 
                else f".fx(vfx.mirror_y)"
            ),
            "@velocidad": lambda args: (
                f".speedx({args[0]})" 
                if len(args) > 0 
                else ".speedx(1.0)"
            ),
            "@fadein": lambda args: (
                f".fadein({args[0]})" 
                if len(args) > 0 
                else ".fadein(1.0)"
            ),
            "@fadeout": lambda args: (
                f".fadeout({args[0]})" 
                if len(args) > 0 
                else ".fadeout(1.0)"
            ),
            "@silencio": lambda args: ".without_audio()",
            "@quitar_audio": lambda args: ".without_audio()",
            "@agregar_musica": lambda args: (
                f".set_audio(AudioFileClip({args[0]}))" 
                if len(args) > 0 
                else ".set_audio(None)"
            ),
            "@concatenar": lambda args: (
                f".concatenate_videoclips([{args[0]}, {args[1]}])" 
                if len(args) >= 2 
                else ".concatenate_videoclips([])"
            ),
            "@cortar": lambda args: (
                f".subclip({args[0]}, {args[1]})" 
                if len(args) >= 2 
                else ".subclip(0)"
            )
        }
        
        if func.func not in video_funcs:
            raise ValueError(f"Función de video no soportada: {func.func}")
        
        try:
            return video_funcs[func.func](args)
        except Exception as e:
            print(f"Error al traducir función {func.func} con argumentos {args}: {str(e)}")
            return f".{func.func.replace('@', '')}()"

def main():
    if len(sys.argv) != 3:
        print("Uso: python translator.py <archivo_fuente> <archivo_salida>")
        sys.exit(1)

    source = sys.argv[1]
    output_file = sys.argv[2]
    
    try:
        # Importar y usar el parser
        from ast_semantic import TableDrivenParser, build_ast
        
        # Parsear el archivo fuente
        with open(source, encoding="utf-8") as f:
            source_code = f.read()
            
        parser = TableDrivenParser(source_code)
        parse_tree = parser.parse()
        
        # Construir el AST
        ast = build_ast(parse_tree)
        
        # Traducir a Python
        translator = Translator()
        python_code = translator.translate(ast)
        
        # Escribir el código Python generado
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(python_code)
            
        print(f"Código Python generado en {output_file}")
        
    except FileNotFoundError:
        print(f"Error: No se pudo encontrar el archivo {source}")
        sys.exit(1)
    except Exception as e:
        print(f"Error durante la traducción: {str(e)}")
        # Crear un archivo de salida incluso si hay error, con un mensaje de error como comentario
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(f"# Error durante la traducción: {str(e)}\n")
                f.write("# El código generado puede estar incompleto\n\n")
                f.write("print('Error: El código no se pudo generar correctamente')\n")
        except:
            pass
        sys.exit(1)

if __name__ == "__main__":
    main()