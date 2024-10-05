from flask import Flask, request, render_template
import ply.lex as lex
import ply.yacc as yacc

app = Flask(__name__)

# Definición de tokens
tokens = (
    'ID',
    'NUM',
    'PUNTOYCOMA',
    'PARIZQ',
    'PARDER',
    'SUMA',
    'REST',
    'MULT',
    'DIV',
    'IGUAL'
)

# Palabras reservadas
reserved = {
    'programa': 'PR',
    'int': 'PR',
    'float': 'PR',
    'read': 'PR',
    'printf': 'PR',
    'return': 'PR',
}


tokens = tokens + tuple(reserved.values())

# Expresiones regulares para los tokens
t_NUM = r'\d+'
t_PUNTOYCOMA = r'\;'
t_PARIZQ = r'\('
t_PARDER = r'\)'
t_SUMA = r'\+'
t_REST = r'-'
t_MULT = r'\*'
t_DIV = r'/'
t_IGUAL = r'='

# Ignorar espacios en blanco y tabulaciones
t_ignore = ' \t'


def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'ID')  # Verifica si es una palabra reservada
    return t

# Función para manejar errores (ignorar caracteres no reconocidos)
def t_error(t):
    print(f"Token no reconocido: {t.value[0]}")
    t.lexer.skip(1)

# Función para iniciar el análisis léxico
def iniciar_lexico(texto):
    lexer = lex.lex()
    lexer.input(texto)

    tokens = []
    line_number = 1  

    for tok in lexer:
        line_number = tok.lineno
        tipo = None

        if tok.type == "PR":
            tipo = "Palabra Reservada"
        elif tok.type == "ID":
            tipo = "Identificador"
        elif tok.type == "NUM":
            tipo = "Número"
        elif tok.type in {'SUMA', 'REST', 'MULT', 'DIV', 'IGUAL', 'PUNTOYCOMA', 'PARIZQ', 'PARDER'}:
            tipo = "Símbolo"
        else:
            tipo = "Desconocido"

        tokens.append({
            'linea': line_number,
            'token': tok.value,
            'PR': 'X' if tipo == 'Palabra Reservada' else '',
            'ID': 'X' if tipo == 'Identificador' else '',
            'Numero': 'X' if tipo == 'Número' else '',
            'Simbolo': 'X' if tipo == 'Símbolo' else '',
            'tipo': tipo
        })

    return tokens

# Definición de la gramática para el análisis sintáctico
def p_programa(p):
    '''programa : PR ID PARIZQ PARDER bloque
                | PR ID PARIZQ PARDER PUNTOYCOMA bloque'''

def p_bloque(p):
    '''bloque : declaraciones bloque
              | expresion bloque
              | empty'''

def p_declaraciones(p):
    '''declaraciones : PR tipo ID PUNTOYCOMA
                     | PR tipo ID IGUAL expresion PUNTOYCOMA'''

def p_tipo(p):
    '''tipo : PR'''

def p_expresion(p):
    '''expresion : ID IGUAL expresion
                 | termino SUMA termino
                 | termino REST termino
                 | termino MULT termino
                 | termino DIV termino'''

def p_termino(p):
    '''termino : NUM
               | ID'''

def p_empty(p):
    'empty :'
    pass

def p_error(p):
    if p:
        if p.type == 'PARIZQ':
            error_msg = "Falta ')' para el símbolo '('"
        elif p.type == 'PUNTOYCOMA':
            error_msg = "Falta ';' en la expresión"
        else:
            error_msg = f"Error de sintaxis en token: {p.value}"
        print(error_msg)
        return ("incorrecto", error_msg)
    else:
        print("Error de sintaxis en entrada vacía")
        return ("incorrecto", "Error en entrada vacía")

# parser
parser = yacc.yacc()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        text = request.form['text']
        
        # Análisis Léxico
        tokens = iniciar_lexico(text)
        
        # Análisis Sintáctico
        sintactico = []
        errores = []
        linea_actual = 1
        for line in text.splitlines():
            result = parser.parse(line)
            if result and result[0] == 'correcto':
                sintactico.append(f"Línea {linea_actual}: Estructura correcta")
            else:
                # Solo se muestra un error por línea si hay errores
                error_msg = result[1] if result else "Estructura incorrecta"
                sintactico.append(f"Línea {linea_actual}: {error_msg}")
                # Guardar el primer error encontrado por línea
                if not errores or errores[-1][0] != linea_actual:
                    errores.append((linea_actual, error_msg))
            linea_actual += 1
        
        # Contador de Tokens
        contador = {
            'Palabras Reservadas': sum(1 for t in tokens if t['PR']),
            'Identificadores': sum(1 for t in tokens if t['ID']),
            'Numeros': sum(1 for t in tokens if t['Numero']),
            'Simbolos': sum(1 for t in tokens if t['Simbolo']),
        }

        return render_template('index3.html', tokens=tokens, sintactico=sintactico, contador=contador, errores=errores, text=text)
    
    return render_template('index3.html', tokens=None, sintactico=None, contador=None, errores=None, text=None)

if __name__ == '_main_':
    app.run(debug=True)