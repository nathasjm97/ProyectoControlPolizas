"""Script temporal de prueba para models/datos.py"""

from models.datos import cargar_clientes, cargar_polizas, leer_poliza
import os

# 1. Probar cargar_clientes
clientes = cargar_clientes()
print(f"Clientes leídos: {len(clientes)}")
print(clientes.head())
print()

# 2. Probar cargar_polizas
polizas = cargar_polizas()
print(f"Pólizas leídas: {len(polizas)}")
print()

# 3. Mostrar diccionario completo de Poliza_AIS-2026-0001.pdf
ruta = os.path.join("data", "polizas", "Poliza_AIS-2026-0001.pdf")
if os.path.exists(ruta):
    poliza = leer_poliza(ruta)
    print("Diccionario de Poliza_AIS-2026-0001.pdf:")
    for clave, valor in poliza.items():
        print(f"  {clave}: {valor}")
else:
    print(f"No se encontró {ruta}")
