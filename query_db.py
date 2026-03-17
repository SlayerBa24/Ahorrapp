import sqlite3

conn = sqlite3.connect('productos.db')
c = conn.cursor()

# Total productos
c.execute('SELECT COUNT(*) FROM productos')
total = c.fetchone()[0]
print(f'Total de productos en la base de datos: {total}')

# Primeros 10 productos
c.execute('SELECT tienda, categoria, nombre, precio, marca FROM productos LIMIT 10')
rows = c.fetchall()

if rows:
    print('\nPrimeros 10 productos:')
    print('Tienda | Categoria | Nombre | Precio | Marca')
    print('-' * 100)
    for row in rows:
        print(' | '.join(str(x) for x in row))

conn.close()