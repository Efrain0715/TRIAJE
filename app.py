from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# Función para conectar a la base de datos
def conectar_bd():
    return sqlite3.connect('data_triaje.db')

# Crear la tabla `sintomas` si no existe
def inicializar_bd():
    conn = conectar_bd()
    cursor = conn.cursor()

    # Crear la tabla `sintomas` si no existe
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sintomas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        descripcion TEXT,
        nivel_triage INTEGER NOT NULL CHECK (nivel_triage BETWEEN 1 AND 3)
    );
    """)


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pacientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        edad INTEGER NOT NULL,
        nivel_urgencia INTEGER NOT NULL CHECK (nivel_urgencia BETWEEN 1 AND 3),
        fecha_ingreso TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Verificar si la tabla está vacía e insertar datos iniciales
    cursor.execute("SELECT COUNT(*) FROM sintomas")
    if cursor.fetchone()[0] == 0:
        sintomas = [
            # Nivel 1 - Emergencias
            ('Dolor en el pecho agudo', 'Síntoma asociado a problemas cardíacos graves', 1),
            ('Dificultad para respirar severa', 'Indica problemas pulmonares o cardíacos graves', 1),
            ('Hemorragia incontrolable', 'Pérdida de sangre significativa', 1),
            ('Convulsiones recurrentes', 'Episodios de actividad eléctrica anormal en el cerebro', 1),
            ('Paro cardíaco', 'Fallo completo del corazón para bombear sangre', 1),
            ('Pérdida de conciencia', 'Estado de inconsciencia repentina', 1),
            ('Quemaduras graves', 'Afectación de capas profundas de la piel', 1),
            ('Lesión traumática en la cabeza', 'Impacto severo que afecta funciones cerebrales', 1),
            ('Dolor abdominal intenso', 'Asociado a apendicitis o perforación', 1),
            ('Infarto', 'Bloqueo en el flujo sanguíneo al corazón', 1),
            ('Fractura expuesta', 'Fractura en la que el hueso perfora la piel', 1),
            ('Trauma torácico', 'Lesión en la cavidad torácica por impacto', 1),
            ('Lesión ocular severa', 'Pérdida significativa de visión o daño estructural', 1),
            ('Ahogamiento', 'Falta de oxígeno debido a inmersión en agua', 1),
            ('Envenenamiento grave', 'Ingestión de sustancias tóxicas en altas dosis', 1),
            ('Electrocución', 'Paso de corriente eléctrica por el cuerpo', 1),
            ('Embolia pulmonar', 'Bloqueo de una arteria en los pulmones', 1),
            ('Anemia severa', 'Pérdida significativa de glóbulos rojos', 1),
            ('Trombosis severa', 'Coágulo de sangre que bloquea el flujo en una vena importante', 1),
            ('Hemorragia cerebral', 'Sangrado dentro del cerebro por ruptura de un vaso sanguíneo', 1),
            ('Asfixia', 'Obstrucción completa de las vías respiratorias', 1),
            ('Sepsis grave', 'Respuesta del cuerpo a una infección que pone en riesgo la vida', 1),
            ('Choque hipovolémico', 'Pérdida severa de líquidos o sangre', 1),
            ('Descompensación diabética', 'Elevación severa de glucosa con daño sistémico', 1),
            
            
            # Completa 25 más para nivel 1...
            
            # Nivel 2 - Urgentes
            ('Fiebre persistente', 'Temperatura corporal superior a 39°C durante días', 2),
            ('Vómitos frecuentes', 'Pueden indicar deshidratación', 2),
            ('Dolor abdominal moderado', 'Relacionado a infecciones o inflamaciones leves', 2),
            ('Fractura simple', 'Ruptura ósea sin complicaciones graves', 2),
            ('Infección urinaria', 'Dolor al orinar y fiebre leve', 2),
            ('Dolor lumbar persistente', 'Posible hernia discal o infección renal', 2),
            ('Tos con sangre', 'Signo de infección o daño pulmonar', 2),
            ('Mareos severos', 'Relacionado a presión arterial baja o anemia', 2),
            ('Crisis hipertensiva', 'Presión arterial elevada con síntomas graves', 2),
            ('Dolor en la espalda media', 'Relacionado a cálculos renales', 2),
            ('Pérdida parcial de visión', 'Obstrucción visual por migrañas o presión ocular', 2),
            ('Infección respiratoria severa', 'Bronquitis aguda con fiebre y malestar general', 2),
            ('Laceraciones profundas', 'Cortes que requieren suturas', 2),
            
            # Completa 37 más para nivel 2...
            
            # Nivel 3 - No Urgentes
            ('Dolor de cabeza leve', 'Molestia no severa, posiblemente relacionada al estrés', 3),
            ('Tos seca persistente', 'Síntoma común en infecciones respiratorias', 3),
            ('Congestión nasal', 'Asociado a resfriados comunes', 3),
            ('Dolor muscular leve', 'Relacionado a sobreesfuerzo físico', 3),
            ('Molestia en los ojos', 'Por exposición prolongada a pantallas', 3),
            ('Dolor de garganta leve', 'Relacionado a infecciones leves', 3),
            ('Erupción cutánea', 'Irritación superficial de la piel', 3),
            ('Dolor en las articulaciones', 'Relacionado a artritis leve o fatiga', 3),
            ('Cansancio generalizado', 'Posible fatiga por falta de sueño', 3),
            ('Picazón en la piel', 'Relacionado a alergias leves', 3),
            ('Manchas en la piel', 'Cambios de coloración por envejecimiento o alergias', 3),
            ('Dolor en el cuello', 'Tensión muscular por postura', 3),
            # Completa 38 más para nivel 3...
        ]

        cursor.executemany(
            "INSERT INTO sintomas (nombre, descripcion, nivel_triage) VALUES (?, ?, ?)",
            sintomas
        )

    conn.commit()
    conn.close()

# Ruta para evaluar pacientes con encadenamiento hacia adelante
@app.route('/evaluar_paciente', methods=['GET', 'POST'])
def evaluar_paciente():
    if request.method == 'POST':
        nombre = request.form['nombre']
        edad = request.form['edad']
        respuestas = request.form.getlist('respuestas')

        nivel_urgencia = None
        if 'nivel_1' in respuestas:
            nivel_urgencia = 1
        elif 'nivel_2' in respuestas:
            nivel_urgencia = 2
        elif 'nivel_3' in respuestas:
            nivel_urgencia = 3

        if nivel_urgencia:
            try:
                conn = conectar_bd()
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO pacientes (nombre, edad, nivel_urgencia)
                    VALUES (?, ?, ?)
                """, (nombre, edad, nivel_urgencia))
                conn.commit()
                conn.close()
                return redirect('/pacientes')
            except sqlite3.Error as e:
                print(f"Error al evaluar paciente: {e}")
                return "Hubo un error al evaluar el paciente."

        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sintomas WHERE prioridad = 2 LIMIT 5")
        sintomas = cursor.fetchall()
        conn.close()
        return render_template('evaluar_paciente.html', sintomas=sintomas, nombre=nombre, edad=edad)


    # Primera iteración: mostrar 5 síntomas clave
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sintomas WHERE prioridad = 1 LIMIT 5")
    sintomas = cursor.fetchall()
    conn.close()
    return render_template('evaluar_paciente.html', sintomas=sintomas)

# Ruta para listar los síntomas
@app.route('/sintomas')
def listar_sintomas():
    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sintomas")
    sintomas = cursor.fetchall()
    conn.close()
    return render_template('sintomas.html', sintomas=sintomas)

# Ruta para agregar un nuevo síntoma
@app.route('/nuevo_sintoma', methods=['GET', 'POST'])
def nuevo_sintoma():
    if request.method == 'POST':
        # Obtener datos del formulario
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        nivel_triage = request.form['nivel_triage']

        # Insertar en la base de datos
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO sintomas (nombre, descripcion, nivel_triage) VALUES (?, ?, ?)",
            (nombre, descripcion, nivel_triage)
        )
        conn.commit()
        conn.close()

        # Redirigir a la lista de síntomas
        return redirect('/sintomas')

    return render_template('nuevo_sintoma.html')

# Ruta para ingresar pacientes
@app.route('/ingresar_paciente', methods=['GET', 'POST'])
def ingresar_paciente():
    if request.method == 'POST':
        # Obtener los datos del formulario
        nombre = request.form['nombre']
        edad = request.form['edad']
        sintomas_seleccionados = request.form.getlist('sintomas')

        # Determinación del nivel de urgencia
        if any(s == '1' for s in sintomas_seleccionados):
            nivel_urgencia = 1
        elif any(s == '2' for s in sintomas_seleccionados):
            nivel_urgencia = 2
        else:
            nivel_urgencia = 3

        # Guardar el paciente en la base de datos
        try:
            conn = conectar_bd()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO pacientes (nombre, edad, nivel_urgencia)
                VALUES (?, ?, ?)
            """, (nombre, edad, nivel_urgencia))
            conn.commit()
            conn.close()
            return redirect('/pacientes')
        except sqlite3.Error as e:
            print(f"Error al registrar el paciente: {e}")
            return "Hubo un error al registrar el paciente."

    # Obtener la lista de síntomas de la base de datos
    try:
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sintomas")
        sintomas = cursor.fetchall()
        conn.close()
    except sqlite3.Error as e:
        print(f"Error al cargar los síntomas: {e}")
        sintomas = []

    return render_template('ingresar_paciente.html', sintomas=sintomas)


# Ruta para listar los pacientes
@app.route('/pacientes')
def listar_pacientes():
    try:
        conn = conectar_bd()
        cursor = conn.cursor()

        # Obtener pacientes por nivel de urgencia
        cursor.execute("SELECT * FROM pacientes WHERE nivel_urgencia = 1 ORDER BY fecha_ingreso DESC")
        pacientes_nivel_1 = cursor.fetchall()

        cursor.execute("SELECT * FROM pacientes WHERE nivel_urgencia = 2 ORDER BY fecha_ingreso DESC")
        pacientes_nivel_2 = cursor.fetchall()

        cursor.execute("SELECT * FROM pacientes WHERE nivel_urgencia = 3 ORDER BY fecha_ingreso DESC")
        pacientes_nivel_3 = cursor.fetchall()

        conn.close()

        return render_template('pacientes.html', 
                               pacientes_nivel_1=pacientes_nivel_1,
                               pacientes_nivel_2=pacientes_nivel_2,
                               pacientes_nivel_3=pacientes_nivel_3)
    except sqlite3.Error as e:
        print(f"Error al listar pacientes: {e}")
        return "Hubo un error al obtener la lista de pacientes."

def agregar_sintomas_faltantes():
    conn = conectar_bd()
    cursor = conn.cursor()

    sintomas_faltantes = [
        ('Diarrea', 'Evacuaciones líquidas frecuentes, puede indicar deshidratación', 2),
        ('Dolor de cabeza intenso', 'Puede estar relacionado con migrañas o problemas neurológicos graves', 1)
    ]

    for sintoma in sintomas_faltantes:
        cursor.execute("""
            INSERT OR IGNORE INTO sintomas (nombre, descripcion, nivel_triage)
            VALUES (?, ?, ?)
        """, sintoma)
        print(f"Sintoma agregado: {sintoma[0]}")

    conn.commit()
    conn.close()

@app.route('/agregar_sintoma', methods=['GET', 'POST'])
def agregar_sintoma():
    if request.method == 'POST':
        # Obtener datos del formulario
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        nivel_triage = request.form['nivel_triage']

        # Insertar en la base de datos
        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO sintomas (nombre, descripcion, nivel_triage)
            VALUES (?, ?, ?)
        """, (nombre, descripcion, nivel_triage))
        conn.commit()
        conn.close()

        return redirect('/sintomas')

    return render_template('agregar_sintomas.html')


# Ruta para la página de inicio
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    inicializar_bd()  # Asegura que la base de datos esté lista
    agregar_sintomas_faltantes()
    app.run(debug=True)
