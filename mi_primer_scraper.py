from playwright.sync_api import sync_playwright
import time

def extraer_precios():
    print("Iniciando el bot...")
    
    with sync_playwright() as p:
        # 1. Abrimos el navegador (headless=False nos permite verlo)
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # 2. Vamos a la sección de despensa del Líder
        url = "https://www.lider.cl/supermercado/category/Despensa/_/N-1"
        print(f"Navegando a: {url}")
        page.goto(url)

        # 3. Esperamos unos segundos para que la página cargue visualmente
        print("Esperando 5 segundos a que carguen los productos...")
        time.sleep(5) 
        
        # 4. Hacemos un poco de scroll hacia abajo como un humano
        page.mouse.wheel(0, 1000)
        time.sleep(2)

        print("¡Navegación exitosa! Ahora cerraremos el navegador.")
        
        # 5. Cerramos todo
        browser.close()

if __name__ == "__main__":
    extraer_precios()