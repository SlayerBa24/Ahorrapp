from playwright.sync_api import sync_playwright
import time
import sqlite3

def hacer_scraping_real():
    print("Iniciando nuestro navegador fantasma...")
    
    # Lista de tiendas a scrapear (una visita por tienda)
    categorias = [
        {'tienda': 'Lider', 'categoria': 'Despensa', 'url': 'https://www.lider.cl/supermercado/category/Despensa/_/N-1'},
        {'tienda': 'Santa Isabel', 'categoria': 'Home', 'url': 'https://www.santaisabel.cl'},
        {'tienda': 'Acuenta', 'categoria': 'Home', 'url': 'https://www.acuenta.cl'},
    ]
    
    # Conectar a la base de datos
    conn = sqlite3.connect('productos.db')
    cursor = conn.cursor()
    
    # Crear tabla si no existe
    cursor.execute('''CREATE TABLE IF NOT EXISTS productos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        precio TEXT,
        marca TEXT,
        tienda TEXT,
        categoria TEXT,
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Agregar columnas si no existen (por compatibilidad)
    try:
        cursor.execute("ALTER TABLE productos ADD COLUMN tienda TEXT")
    except sqlite3.OperationalError:
        pass  # Ya existe
    try:
        cursor.execute("ALTER TABLE productos ADD COLUMN categoria TEXT")
    except sqlite3.OperationalError:
        pass  # Ya existe
    
    with sync_playwright() as p:
        # headless=False hace que el navegador sea visible para nosotros
        browser = p.chromium.launch(headless=False)
        
        for categoria in categorias:
            print(f"\n--- SCRAPEANDO {categoria['tienda']} - CATEGORÍA: {categoria['categoria']} ---")
            
            page = browser.new_page()
            url = categoria['url']
            print(f"Entrando a Líder: {url}")
            page.goto(url)

            # La magia de Playwright: Le decimos que espere hasta que el sitio 
            # deje de cargar cosas en segundo plano (load)
            print("Esperando a que el JavaScript cargue los productos (como lo haría un humano)...")
            page.wait_for_load_state('load')
            time.sleep(3) # Pausa humana extra

            # Hacemos scroll hacia abajo para que se carguen las imágenes
            print("Haciendo scroll múltiple para cargar más productos...")
            for i in range(5):  # 5 scrolls para cargar más productos
                page.mouse.wheel(0, 1500)
                time.sleep(1)  # Pausa entre scrolls
                print(f"Scroll {i+1} completado")

            print("\n--- ¡BUSCANDO PRODUCTOS! ---")
            
            # Buscamos las cajas de los productos. 
            productos = page.locator("li[class*='product'], div[class*='product-item'], div[class*='product-card'], div[class*='ProductCard'], div[data-testid*='product']").all()
            
            if len(productos) == 0:
                print("Ups, parece que Líder cambió el nombre de sus cajas en el código. ¡Tendremos que inspeccionar la página con F12!")
            else:
                print(f"¡Se encontraron {len(productos)} productos!\n")
                
                productos_guardados = 0
                # Recorremos cada producto que encontró
                for producto in productos:  # Procesar TODOS los productos encontrados (sin límite)
                    texto = producto.inner_text()
                    
                    # Separamos el texto en partes
                    parts = [line.strip() for line in texto.split('\n') if line.strip()]
                    
                    # EL ARREGLO ESTÁ AQUÍ:
                    # Si la caja tiene menos de 5 líneas de texto, es un "fantasma". Lo saltamos.
                    if len(parts) < 5:
                        continue 

                    texto_limpio = " | ".join(parts)
                    
                    # Parsear los datos (Según la estructura que viste en consola)
                    nombre = parts[0]
                    
                    # Extraer precio más limpiamente
                    precio_texto = parts[2] if len(parts) > 2 else ""
                    import re
                    # Buscar patrón de precio chileno: $ seguido de números con puntos
                    match = re.search(r'\$[\d.,]+', precio_texto)
                    if match:
                        precio = match.group()
                    else:
                        precio = precio_texto
                    
                    # A veces la marca está en la posición 5, pero si no hay, dejamos en blanco
                    marca = parts[5] if len(parts) > 5 else "Sin marca" 
                    
                    # Guardar en la base de datos
                    cursor.execute("INSERT INTO productos (nombre, precio, marca, tienda, categoria) VALUES (?, ?, ?, ?, ?)", (nombre, precio, marca, categoria['tienda'], categoria['categoria']))
                    productos_guardados += 1
                    
                    # Imprimir bonito para nosotros
                    print(f"🛒 Producto: {nombre}")
                    print(f"🏷️  Marca: {marca}")
                    print(f"💰 Precio: {precio}")
                    print("-" * 50)

                print(f"\n¡Se guardaron {productos_guardados} productos de {categoria['tienda']} - {categoria['categoria']} en la base de datos!")
            
            page.close()  # Cerrar la página después de cada categoría
        
        print("\n¡Trabajo terminado! Cerrando el navegador...")
        time.sleep(2)
        browser.close()
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    hacer_scraping_real()