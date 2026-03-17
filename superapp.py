import requests
import json

def extraer_productos_supermercado():
    # 1. Reemplaza esta URL por la que encontraste en la pestaña Network (F12)
    url_api = "https://api.ejemplo-supermercado.cl/v1/catalog/search?category=despensa"
    
    # 2. Los "Headers" son vitales. Le dicen al supermercado que eres un navegador real y no un robot.
    # Copia el "User-Agent" exacto desde las herramientas de desarrollador.
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }

    try:
        # 3. Hacemos la petición a la página
        respuesta = requests.get(url_api, headers=headers)
        
        # Verificamos que la petición fue exitosa (Código 200)
        if respuesta.status_code == 200:
            datos = respuesta.json()
            
            # 4. Navegamos por el JSON para sacar lo que nos importa
            # Nota: La estructura (datos['products']) cambiará dependiendo del supermercado
            productos = datos.get('products', []) 
            
            for producto in productos:
                nombre = producto.get('name')
                precio_normal = producto.get('price')
                precio_oferta = producto.get('discount_price')
                sku = producto.get('sku')
                
                print(f"[{sku}] {nombre} - Normal: ${precio_normal} | Oferta: ${precio_oferta}")
                
                # Aquí es donde luego guardarías los datos en tu base de datos (Supabase/Firebase)
                
        else:
            print(f"Error al conectar: Código {respuesta.status_code}")
            
    except Exception as e:
        print(f"Ocurrió un error: {e}")

# Ejecutamos la función
extraer_productos_supermercado()