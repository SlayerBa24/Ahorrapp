import sqlite3
from collections import defaultdict

def comparar_precios():
    conn = sqlite3.connect('productos.db')
    c = conn.cursor()

    # Obtener todos los productos
    c.execute("SELECT nombre, precio, marca, tienda, categoria FROM productos ORDER BY nombre")
    productos = c.fetchall()

    if not productos:
        print("No hay productos en la base de datos. Ejecuta el scraper primero.")
        return

    print("=== COMPARACIÓN DE PRECIOS Y PRODUCTOS ===\n")

    # Agrupar productos por nombre similar (primeras 3 palabras)
    productos_agrupados = defaultdict(list)

    for nombre, precio, marca, tienda, categoria in productos:
        # Limpiar nombre para agrupar (tomar primeras 3 palabras)
        palabras = nombre.lower().split()[:3]
        clave = ' '.join(palabras)

        # Limpiar precio (extraer solo números)
        import re
        precio_texto = re.sub(r'[^\d.,]', '', precio)  # Solo números, puntos y comas
        precio_texto = precio_texto.replace(',', '.')  # Cambiar coma por punto
        try:
            # Tomar el primer número encontrado
            match = re.search(r'\d+(?:\.\d+)?', precio_texto)
            if match:
                precio_float = float(match.group())
            else:
                precio_float = 0
        except (ValueError, AttributeError):
            precio_float = 0

        productos_agrupados[clave].append({
            'nombre_completo': nombre,
            'precio': precio,
            'precio_float': precio_float,
            'marca': marca,
            'tienda': tienda,
            'categoria': categoria
        })

    # Mostrar comparaciones
    productos_comparados = 0
    for clave, items in productos_agrupados.items():
        if len(items) > 1:  # Solo mostrar si hay más de una tienda
            print(f"📦 PRODUCTO: {clave.upper()}")
            print("-" * 60)

            # Ordenar por precio
            items_ordenados = sorted(items, key=lambda x: x['precio_float'])

            for item in items_ordenados:
                precio_display = f"${item['precio_float']:,.0f}" if item['precio_float'] > 0 else item['precio']
                print(f"🏪 {item['tienda']} | 💰 {precio_display} | 🏷️ {item['marca']}")
                print(f"   📝 {item['nombre_completo']}")
                print()

            # Calcular diferencia de precio
            precios_validos = [item['precio_float'] for item in items if item['precio_float'] > 0]
            if len(precios_validos) >= 2:
                precio_min = min(precios_validos)
                precio_max = max(precios_validos)
                diferencia = precio_max - precio_min
                ahorro_porcentaje = (diferencia / precio_max * 100) if precio_max > 0 else 0

                print(f"💸 Ahorro máximo: ${diferencia:,.0f} ({ahorro_porcentaje:.1f}%)")
                print(f"✅ Mejor precio en: {items_ordenados[0]['tienda']}")
            elif len(precios_validos) == 1:
                print(f"💰 Solo un precio válido encontrado: ${precios_validos[0]:,.0f}")
            else:
                print("❌ No se pudieron parsear precios para comparación")
            productos_comparados += 1

            if productos_comparados >= 10:  # Limitar a 10 comparaciones para no saturar
                break

    if productos_comparados == 0:
        print("No se encontraron productos similares en diferentes tiendas para comparar.")
        print("Ejecuta el scraper en más tiendas o categorías.")

    # Estadísticas generales
    print("\n=== ESTADÍSTICAS GENERALES ===")
    c.execute("SELECT tienda, COUNT(*) as total FROM productos GROUP BY tienda")
    stats = c.fetchall()
    for tienda, total in stats:
        print(f"🏪 {tienda}: {total} productos")

    c.execute("SELECT COUNT(DISTINCT nombre) FROM productos")
    productos_unicos = c.fetchone()[0]
    print(f"📦 Total productos únicos: {productos_unicos}")

    conn.close()

if __name__ == "__main__":
    comparar_precios()