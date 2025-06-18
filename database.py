import sqlite3

def crear_base_datos():
    try:
        conn = sqlite3.connect('alimsave.db')
        cursor = conn.cursor()

        # Crear tabla usuarios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                tipo TEXT NOT NULL
            )
        ''')

        # Crear tabla productos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                vencimiento TEXT NOT NULL,
                cantidad INTEGER NOT NULL,
                precio REAL NOT NULL,
                vendedor_id INTEGER NOT NULL,
                FOREIGN KEY (vendedor_id) REFERENCES usuarios(id)
            )
        ''')

        # Crear tabla ventas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                producto_id INTEGER NOT NULL,
                comprador_id INTEGER NOT NULL,
                cantidad INTEGER NOT NULL,
                precio_total REAL NOT NULL,
                FOREIGN KEY (producto_id) REFERENCES productos(id),
                FOREIGN KEY (comprador_id) REFERENCES usuarios(id)
            )
        ''')

        conn.commit()
        conn.close()
        print("Base de datos creada correctamente.")
    except Exception as e:
        print(f"Error creando la base de datos: {e}")
