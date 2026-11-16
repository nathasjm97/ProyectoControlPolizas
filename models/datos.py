"""Capa de acceso a datos: único lugar que abre archivos."""

import os
import pandas as pd
import pdfplumber


# Diccionario que mapea la etiqueta del PDF al nombre del campo interno.
CAMPOS = {
    "Numero de poliza": "numero",
    "Ramo": "ramo",
    "Tomador / Asegurado": "nombre",
    "Cedula": "cedula",
    "Vigencia desde": "desde",
    "Vigencia hasta": "hasta",
    "Prima anual": "prima",
    "Forma de pago": "pago",
    "Suma asegurada": "suma",
    "Asesor": "asesor",
}


def cargar_clientes():
    """Lee data/Maestro_Clientes.xlsx (hoja Clientes) y devuelve un DataFrame.

    La columna Cedula se lee como texto y se le quitan los espacios.
    """
    ruta = os.path.join("data", "Maestro_Clientes.xlsx")
    df = pd.read_excel(ruta, sheet_name="Clientes", dtype={"Cedula": str})
    df["Cedula"] = df["Cedula"].str.strip()
    return df


def _convertir_fecha(texto):
    """Convierte una fecha en formato dd/mm/aaaa a objeto date.

    Devuelve None si el texto está vacío o no se puede convertir.
    """
    if not texto or texto.strip() == "":
        return None
    from datetime import datetime
    try:
        return datetime.strptime(texto.strip(), "%d/%m/%Y").date()
    except ValueError:
        return None


def _convertir_monto(texto):
    """Convierte un monto como 'CRC 228,000.00' a número (float).

    Devuelve None si el texto está vacío.
    """
    if not texto or texto.strip() == "":
        return None
    limpio = texto.strip()
    # Quitar posibles prefijos de moneda y comas de miles
    limpio = limpio.replace("CRC", "").replace(",", "").strip()
    try:
        return float(limpio)
    except ValueError:
        return None


def leer_poliza(ruta_pdf):
    """Abre un PDF con pdfplumber y devuelve un diccionario con sus datos.

    - La primera línea del texto es la aseguradora.
    - Las demás líneas con ':' se buscan en CAMPOS y se guardan.
    - Fechas se convierten con _convertir_fecha.
    - Montos se convierten con _convertir_monto.
    """
    nombre_archivo = os.path.basename(ruta_pdf)

    with pdfplumber.open(ruta_pdf) as pdf:
        pagina = pdf.pages[0]
        texto = pagina.extract_text()

    if not texto:
        return {
            "archivo": nombre_archivo,
            "aseguradora": None,
            "numero": None,
            "ramo": None,
            "nombre": None,
            "cedula": None,
            "desde": None,
            "hasta": None,
            "prima": None,
            "pago": None,
            "suma": None,
            "asesor": None,
        }

    lineas = texto.splitlines()
    aseguradora = lineas[0].strip() if lineas else None

    resultado = {
        "archivo": nombre_archivo,
        "aseguradora": aseguradora,
        "numero": None,
        "ramo": None,
        "nombre": None,
        "cedula": None,
        "desde": None,
        "hasta": None,
        "prima": None,
        "pago": None,
        "suma": None,
        "asesor": None,
    }

    # Recorrer las demás líneas con un bucle
    for linea in lineas[1:]:
        if ":" in linea:
            partes = linea.split(":", 1)
            etiqueta = partes[0].strip()
            valor = partes[1].strip()
            if etiqueta in CAMPOS:
                campo = CAMPOS[etiqueta]
                if campo in ("desde", "hasta"):
                    resultado[campo] = _convertir_fecha(valor)
                elif campo in ("prima", "suma"):
                    resultado[campo] = _convertir_monto(valor)
                else:
                    resultado[campo] = valor

    return resultado


def cargar_polizas():
    """Recorre data/polizas en orden alfabético y devuelve una lista de diccionarios.

    Cada diccionario es el resultado de leer_poliza() para un PDF.
    """
    carpeta = os.path.join("data", "polizas")
    archivos = sorted(os.listdir(carpeta))
    polizas = []
    for archivo in archivos:
        if archivo.lower().endswith(".pdf"):
            ruta = os.path.join(carpeta, archivo)
            polizas.append(leer_poliza(ruta))
    return polizas
