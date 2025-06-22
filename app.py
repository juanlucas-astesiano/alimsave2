from flask import Flask, request, jsonify
import sqlite3
import pandas as pd
import requests
import matplotlib.pyplot as plt


app = Flask(__name__)

# Inicialización de la base de datos
def crear_base_datos():
    conn = sqlite3.connect('alimsave2.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            tipo TEXT NOT NULL
        )
    ''')

    # Tabla de productos con categoría y código de barras
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            vencimiento TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            precio REAL NOT NULL,
            vendedor_id INTEGER,
            categoria TEXT,
            codigo_barras TEXT,
            FOREIGN KEY (vendedor_id) REFERENCES usuarios(id)
        )
    ''')

    # Tabla de ventas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producto_id INTEGER,
            comprador_id INTEGER,
            cantidad INTEGER,
            precio_total REAL,
            FOREIGN KEY (producto_id) REFERENCES productos(id),
            FOREIGN KEY (comprador_id) REFERENCES usuarios(id)
        )
    ''')

    conn.commit()
    conn.close()

crear_base_datos()

@app.route('/')
def home():
    return '''
    <h2>Bienvenido a la API de AlimSave</h2>
    <ul>
        <li><b>POST</b> /registrar_usuario</li>
        <li><b>POST</b> /login_usuario</li>
        <li><b>POST</b> /producto</li>
        <li><b>GET</b> /productos</li>
        <li><b>PUT</b> /producto/&lt;id&gt;</li>
        <li><b>DELETE</b> /producto/&lt;id&gt;</li>
        <li><b>POST</b> /comprar/&lt;id&gt;</li>
        <li><b>GET</b> /generar_csv</li>
    </ul>
    '''

@app.route('/registrar_usuario', methods=['POST'])
def registrar_usuario():
    data = request.get_json()
    nombre = data.get('nombre')
    tipo = data.get('tipo')
    if not nombre or not tipo:
        return jsonify({'error': 'Datos incompletos'}), 400

    conn = sqlite3.connect('alimsave2.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO usuarios (nombre, tipo) VALUES (?, ?)", (nombre, tipo))
    usuario_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return jsonify({'mensaje': 'Usuario registrado', 'usuario_id': usuario_id})

@app.route('/login_usuario', methods=['POST'])
def login_usuario():
    data = request.get_json()
    nombre = data.get('nombre')

    conn = sqlite3.connect('alimsave2.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, tipo FROM usuarios WHERE nombre = ?", (nombre,))
    usuario = cursor.fetchone()
    conn.close()

    if usuario:
        return jsonify({'mensaje': 'Login exitoso', 'usuario_id': usuario[0], 'tipo': usuario[1]})
    else:
        return jsonify({'error': 'Usuario no encontrado'}), 404

@app.route('/producto', methods=['POST'])
def cargar_producto():
    data = request.get_json()
    campos = ['nombre', 'vencimiento', 'cantidad', 'precio', 'vendedor_id']
    if not all(c in data for c in campos):
        return jsonify({'error': 'Datos incompletos'}), 400

    conn = sqlite3.connect('alimsave2.db')
    cursor = conn.cursor()
    cursor.execute("SELECT tipo FROM usuarios WHERE id = ?", (data['vendedor_id'],))
    vendedor = cursor.fetchone()
    if not vendedor or vendedor[0] != 'vendedor':
        return jsonify({'error': 'Solo los vendedores pueden cargar productos'}), 403

    # 🔍 Consultar OpenFoodFacts
    producto_nombre = data['nombre'].lower().replace(" ", "+")
    try:
        response = requests.get(
            f'https://world.openfoodfacts.org/cgi/search.pl?search_terms={producto_nombre}&search_simple=1&json=1'
        )
        response.raise_for_status()
        resultados = response.json().get('products', [])
        if resultados:
            producto_info = resultados[0]
            categoria = producto_info.get('categories', 'Desconocido')
            codigo_barras = producto_info.get('code', 'N/A')
        else:
            categoria = 'No encontrada'
            codigo_barras = 'N/A'
    except Exception as e:
        categoria = 'Error al consultar'
        codigo_barras = 'N/A'

    # 📝 Insertar producto
    cursor.execute('''
    INSERT INTO productos (
        nombre, vencimiento, cantidad, precio, vendedor_id, categoria, codigo_barras
    ) VALUES (?, ?, ?, ?, ?, ?, ?)
''', (
    data['nombre'],
    data['vencimiento'],
    data['cantidad'],
    data['precio'],
    data['vendedor_id'],
    categoria,
    codigo_barras
))
    conn.commit()
    conn.close()

    return jsonify({
        'mensaje': 'Producto cargado',
        'categoria': categoria,
        'codigo_barras': codigo_barras
    })

@app.route('/productos', methods=['GET'])
def listar_productos():
    conn = sqlite3.connect('alimsave2.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()
    conn.close()

    lista = [{
        'id': p[0],
        'nombre': p[1],
        'vencimiento': p[2],
        'cantidad': p[3],
        'precio': p[4],
        'vendedor_id': p[5],
        'categoria': p[6],
        'codigo_barras': p[7]
    } for p in productos]

    return jsonify(lista)

@app.route('/producto/<int:id>', methods=['PUT'])
def actualizar_producto(id):
    data = request.get_json()
    conn = sqlite3.connect('alimsave2.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE productos SET cantidad = ?, precio = ? WHERE id = ?",
                   (data.get('cantidad'), data.get('precio'), id))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'Producto actualizado'})

@app.route('/producto/<int:id>', methods=['DELETE'])
def eliminar_producto(id):
    conn = sqlite3.connect('alimsave2.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM productos WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'Producto eliminado'})

@app.route('/comprar', methods=['POST'])
def comprar():
    data = request.get_json()
    producto_id = data.get("producto_id")
    comprador_id = data.get("comprador_id")
    cantidad = data.get("cantidad")

    conn = sqlite3.connect('alimsave2.db')
    cursor = conn.cursor()

    cursor.execute("SELECT cantidad, precio FROM productos WHERE id = ?", (producto_id,))
    producto = cursor.fetchone()

    if not producto or producto[0] < cantidad:
        conn.close()
        return jsonify({'error': 'Stock insuficiente o producto no encontrado'}), 400

    nuevo_stock = producto[0] - cantidad
    precio_total = cantidad * producto[1]

    cursor.execute("UPDATE productos SET cantidad = ? WHERE id = ?", (nuevo_stock, producto_id))
    cursor.execute("INSERT INTO ventas (producto_id, comprador_id, cantidad, precio_total) VALUES (?, ?, ?, ?)",
                   (producto_id, comprador_id, cantidad, precio_total))

    conn.commit()
    conn.close()

    return jsonify({'mensaje': 'Compra realizada'}), 200


@app.route('/generar_csv', methods=['GET'])
def generar_csv():
    conn = sqlite3.connect('alimsave2.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT productos.nombre, ventas.cantidad, ventas.precio_total
        FROM ventas
        JOIN productos ON ventas.producto_id = productos.id
    ''')
    data = cursor.fetchall()
    conn.close()
    df = pd.DataFrame(data, columns=['producto', 'cantidad', 'precio_total'])
    df.to_csv('datos_ventas.csv', index=False)
    return jsonify({'mensaje': 'Archivo CSV generado'})



@app.route('/grafico_categorias/<int:vendedor_id>', methods=['GET'])
def grafico_categorias_por_vendedor(vendedor_id):
    try:
        conn = sqlite3.connect('alimsave2.db')

        query = """
            SELECT p.categoria, SUM(v.precio_total) AS total_categoria
            FROM ventas v
            JOIN productos p ON v.producto_id = p.id
            WHERE p.vendedor_id = ?
            GROUP BY p.categoria
        """
        df = pd.read_sql_query(query, conn, params=(vendedor_id,))
        conn.close()

        if df.empty:
            return jsonify({"mensaje": "NO TENES VENTAS REALIZADAS"}), 404

        # Mostrar para diagnosticar (podés comentar luego)
        print(df)

        def dividir_texto_en_n_lineas(texto, n=3):
            longitud = len(texto)
            if longitud <= n:
                return texto
            tamaño_linea = (longitud + n - 1) // n
            lineas = [texto[i*tamaño_linea:(i+1)*tamaño_linea] for i in range(n)]
            return '\n'.join(lineas)

        df['categoria'] = df['categoria'].apply(lambda x: dividir_texto_en_n_lineas(x, 3))

        plt.figure(figsize=(10, max(4, len(df) * 0.8)))
        plt.barh(df['categoria'], df['total_categoria'], color='skyblue')
        for i, (valor, categoria) in enumerate(zip(df['total_categoria'], df['categoria'])):
            plt.text(valor + max(df['total_categoria'])*0.01, i, f"${valor:.2f}", va='center', fontsize=9)
        plt.title(f'Ventas por Categoría del Vendedor {vendedor_id}')
        plt.xlabel('Monto Total Vendido ($)')
        plt.ylabel('Categoría')
        plt.tight_layout(pad=3.0)
        plt.subplots_adjust(left=0.3)

        archivo_salida = f"grafico_categorias_vendedor_{vendedor_id}.png"
        plt.savefig(archivo_salida)
        plt.close()

        return jsonify({
            "mensaje": "✅ Gráfico generado exitosamente",
            "archivo": archivo_salida
        })

    except Exception as e:
        print(f"❌ Error en el endpoint gráfico: {e}")
        return jsonify({"error": "Ocurrió un error al generar el gráfico"}), 500




if __name__ == '__main__':
    app.run(debug=True)
