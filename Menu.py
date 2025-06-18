import requests


#este es el GET que nos trae todos los productos.
url = "http://localhost:5000/productos"
respuesta = requests.get(url)
print(respuesta.json())