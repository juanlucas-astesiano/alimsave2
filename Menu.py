import requests


#este es el GET que nos trae todos los productos.
'''
url = "http://localhost:5000/productos"
respuesta = requests.get(url)
print(respuesta.json())
'''
BASE_URL = "http://localhost:5000"

def mostrar_respuesta(response):
    print(f"\nCódigo de estado: {response.status_code}")
    try:
        print(response.json())
    except ValueError:
        print("⚠️ La respuesta no es JSON:")
        print(response.text)

def listar_productos():
    response = requests.get(f"{BASE_URL}/productos")
    mostrar_respuesta(response)

def registrar_usuario():
    nombre = input("Nombre del usuario: ")
    tipo = input("Tipo de usuario (vendedor o comprador): ").lower()
    data = {"nombre": nombre, "tipo": tipo}
    response = requests.post(f"{BASE_URL}/registrar_usuario", json=data)
    mostrar_respuesta(response)

def login_usuario():
    nombre = input("Nombre del usuario: ")
    data = {"nombre": nombre}
    response = requests.post(f"{BASE_URL}/login_usuario", json=data)
    mostrar_respuesta(response)

def crear_producto():
    nombre = input("Nombre del producto: ")
    precio = float(input("Precio del producto: "))
    cantidad = int(input("Cantidad: "))
    vencimiento = input("Fecha de vencimiento (YYYY-MM-DD): ")
    vendedor_id = int(input("ID del vendedor (debe estar registrado como 'vendedor'): "))

    data = {
        "nombre": nombre,
        "precio": precio,
        "cantidad": cantidad,
        "vencimiento": vencimiento,
        "vendedor_id": vendedor_id
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

def comprar_producto():
    producto_id = input("ID del producto a comprar: ")
    cantidad = int(input("Cantidad a comprar: "))
    comprador_id = int(input("ID del comprador (debe estar registrado como 'comprador'): "))

    data = {
        "cantidad": cantidad,
        "comprador_id": comprador_id
    }

    response = requests.post(f"{BASE_URL}/comprar/{producto_id}", json=data)
    mostrar_respuesta(response)

def generar_csv():
    response = requests.get(f"{BASE_URL}/generar_csv")
    mostrar_respuesta(response)

def menu():
    while True:
        print("\n--- MENÚ DE ALIMSAVE ---")
        print("1. Listar productos")
        print("2. Registrar usuario")
        print("3. Login usuario")
        print("4. Crear producto")
        print("5. Actualizar producto")
        print("6. Eliminar producto")
        print("7. Comprar producto")
        print("8. Generar CSV de ventas")
        print("9. Salir")
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            listar_productos()
        elif opcion == "2":
            registrar_usuario()
        elif opcion == "3":
            login_usuario()
        elif opcion == "4":
            crear_producto()
        elif opcion == "5":
            actualizar_producto()
        elif opcion == "6":
            eliminar_producto()
        elif opcion == "7":
            comprar_producto()
        elif opcion == "8":
            generar_csv()
        elif opcion == "9":
            print("👋 Saliendo del sistema.")
            break
        else:
            print("Opción inválida. Intente de nuevo.")

if __name__ == "__main__":
    menu()