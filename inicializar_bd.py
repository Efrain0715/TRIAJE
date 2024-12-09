import sqlite3

def inicializar_bd():
    conn = sqlite3.connect('data_triaje.db')
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

    # Verificar si la tabla está vacía e insertar datos iniciales
    cursor.execute("SELECT COUNT(*) FROM sintomas")
    if cursor.fetchone()[0] == 0:
        sintomas = [
            ('Dolor en el pecho', 'Síntoma asociado a problemas cardíacos graves', 1),
            ('Fiebre alta', 'Temperatura corporal superior a 39°C', 2),
            ('Dolor de cabeza leve', 'Molestia no severa, posiblemente relacionada al estrés', 3),
            ('Dificultad para respirar', 'Indica problemas pulmonares o cardíacos graves', 1),
            ('Dolor abdominal moderado', 'Posible inflamación o infección leve', 2),
            ('Tos seca persistente', 'Síntoma común en infecciones respiratorias', 3)
        ]
        cursor.executemany(
            "INSERT INTO sintomas (nombre, descripcion, nivel_triage) VALUES (?, ?, ?)",
            sintomas
        )

    conn.commit()
    conn.close()
    print("Base de datos inicializada correctamente.")

# Ejecutar solo si se llama directamente
if __name__ == '__main__':
    inicializar_bd()
