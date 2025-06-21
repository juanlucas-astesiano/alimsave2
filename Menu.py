import requests
import pandas as pd



#este es el GET que nos trae todos los productos.
'''
url = "http://localhost:5000/productos"
respuesta = requests.get(url)
print(respuesta.json())
'''
BASE_URL = "http://localhost:5000"

usuario_actual = {
    "id": None,
    "nombre": None,
    "tipo": None
}

def mostrar_respuesta(response):
    print(f"\nCódigo de estado: {response.status_code}")
    try:
        print(response.json())
    except ValueError:
        print("⚠️ La respuesta no es JSON:")
        print(response.text)

def registrar_usuario():
    nombre = input("Nombre del usuario: ")
    tipo = input("Tipo de usuario (vendedor o comprador): ").lower()
    data = {"nombre": nombre, "tipo": tipo}
    response = requests.post(f"{BASE_URL}/registrar_usuario", json=data)
    if response.status_code == 200:
        resultado = response.json()
        usuario_actual["id"] = resultado["usuario_id"]
        usuario_actual["nombre"] = nombre
        usuario_actual["tipo"] = tipo
        print(f"✅ Registrado como {tipo} con ID {usuario_actual['id']}")
        return True
    else:
        mostrar_respuesta(response)
        return False

def login_usuario():
    nombre = input("Nombre del usuario: ")
    data = {"nombre": nombre}
    response = requests.post(f"{BASE_URL}/login_usuario", json=data)
    if response.status_code == 200:
        resultado = response.json()
        usuario_actual["id"] = resultado["usuario_id"]
        usuario_actual["nombre"] = nombre
        usuario_actual["tipo"] = resultado["tipo"]
        print(f"🔓 Login exitoso como {usuario_actual['tipo']} (ID: {usuario_actual['id']})")
        return True
    else:
        mostrar_respuesta(response)
        return False

# Funciones para compradores
def listar_productos():
    response = requests.get(f"{BASE_URL}/productos")
    print(f"\nCódigo de estado: {response.status_code}")

    try:
        data = response.json()

        # Asegurarse de que recibimos una lista (sin 'get' porque data ya es la lista)
        if isinstance(data, list):
            productos = data
        elif isinstance(data, dict):
            productos = data.get("productos", [])
        else:
            productos = []

        if not productos:
            print("⚠️ No hay productos disponibles.")
            return

        import pandas as pd
        df = pd.DataFrame(productos)

        # Eliminar columnas que no quieras mostrar
        columnas_a_mostrar = ["id", "nombre", "precio", "cantidad", "vencimiento", "codigo_barras"]
        df = df[columnas_a_mostrar]

        print("\n📦 Lista de productos:")
        print(df.to_string(index=False))  # Sin índice numérico a la izquierda

    except ValueError:
        print("⚠️ La respuesta no es JSON:")
        print(response.text)


def comprar_producto():
    producto_id = input("ID del producto a comprar: ")
    cantidad = int(input("Cantidad a comprar: "))

    data = {
        "cantidad": cantidad,
        "comprador_id": usuario_actual["id"]
    }

    response = requests.post(f"{BASE_URL}/comprar/{producto_id}", json=data)
    mostrar_respuesta(response)

# Funciones para vendedores
def crear_producto():
    nombre = input("Nombre del producto: ")
    precio = float(input("Precio del producto: "))
    cantidad = int(input("Cantidad: "))
    vencimiento = input("Fecha de vencimiento (YYYY-MM-DD): ")

    data = {
        "nombre": nombre,
        "precio": precio,
        "cantidad": cantidad,
        "vencimiento": vencimiento,
        "vendedor_id": usuario_actual["id"]
    }

    response = requests.post(f"{BASE_URL}/producto", json=data)
    mostrar_respuesta(response)

def actualizar_producto():
    producto_id = input("ID del producto a actualizar: ")
    cantidad = int(input("Nueva cantidad: "))
    precio = float(input("Nuevo precio: "))

    data = {
        "cantidad": cantidad,
        "precio": precio
    }

    response = requests.put(f"{BASE_URL}/producto/{producto_id}", json=data)
    mostrar_respuesta(response)

def eliminar_producto():
    producto_id = input("ID del producto a eliminar: ")
    response = requests.delete(f"{BASE_URL}/producto/{producto_id}")
    mostrar_respuesta(response)

def generar_csv():
    response = requests.get(f"{BASE_URL}/generar_csv")
    mostrar_respuesta(response)

# Menús por tipo de usuario
def menu_comprador():
    while True:
        print(f"\n🛒 Menú del Comprador ({usuario_actual['nombre']})")
        print("1. Listar productos")
        print("2. Comprar producto")
        print("3. Cerrar sesión")
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            listar_productos()
        elif opcion == "2":
            comprar_producto()
        elif opcion == "3":
            print("🔒 Cerrando sesión...")
            return
        else:
            print("Opción inválida.")

def menu_vendedor():
    while True:
        print(f"\n📦 Menú del Vendedor ({usuario_actual['nombre']})")
        print("1. Crear producto")
        print("2. Actualizar producto")
        print("3. Eliminar producto")
        print("4. Generar CSV de ventas")
        print("5. Cerrar sesión")
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            crear_producto()
        elif opcion == "2":
            actualizar_producto()
        elif opcion == "3":
            eliminar_producto()
        elif opcion == "4":
            generar_csv()
        elif opcion == "5":
            print("🔒 Cerrando sesión...")
            return
        else:
            print("Opción inválida.")

# Menú de inicio
def menu_inicio():
    while True:
        print("\n🔐 Bienvenido a AlimSave")
        print("1. Registrarse")
        print("2. Iniciar sesión")
        print("0. Salir del programa")
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            if registrar_usuario():
                break
        elif opcion == "2":
            if login_usuario():
                break
        elif opcion == "0":
            print("👋 Hasta pronto.")
            exit()
        else:
            print("Opción inválida.")

# Control general del flujo
def main():
    while True:
        menu_inicio()

        if usuario_actual["tipo"] == "comprador":
            menu_comprador()
        elif usuario_actual["tipo"] == "vendedor":
            menu_vendedor()
        else:
            print("⚠️ Tipo de usuario no reconocido.")

        # Resetear sesión
        usuario_actual["id"] = None
        usuario_actual["nombre"] = None
        usuario_actual["tipo"] = None

if __name__ == "__main__":
    main()