"""Capa de reglas del negocio: estados, primas, inconsistencias y búsquedas."""

from datetime import date
from collections import defaultdict

from models.datos import cargar_clientes, cargar_polizas

# Constantes de negocio según AGENTS.md
FECHA_CORTE = date(2026, 11, 2)
DIAS_AVISO = 30


def estado_poliza(hasta, fecha_corte=FECHA_CORTE):
    """Devuelve el estado de una póliza según su fecha de vigencia hasta.

    - Vencida: hasta < fecha_corte
    - Por vencer: 0 <= días hasta vencer <= DIAS_AVISO
    - Vigente: más de DIAS_AVISO días
    - Sin fecha: si hasta es None
    """
    if hasta is None:
        return "Sin fecha"

    dias = (hasta - fecha_corte).days

    if dias < 0:
        return "Vencida"
    elif 0 <= dias <= DIAS_AVISO:
        return "Por vencer"
    else:
        return "Vigente"


def calcular_resultados(fecha_corte=FECHA_CORTE):
    """Cruza cada póliza con el maestro por cédula y devuelve una lista de
    diccionarios ordenada de menos a más días para vencer (lo urgente primero).

    Cada diccionario incluye los datos de la póliza, el correo del cliente,
    si está en el maestro, los días hasta vencer y el estado.
    """
    clientes_df = cargar_clientes()
    polizas = cargar_polizas()

    # Índice de clientes por cédula para buscar rápido
    clientes_por_cedula = {}
    for _, fila in clientes_df.iterrows():
        cedula = fila["Cedula"]
        clientes_por_cedula[cedula] = fila.to_dict()

    resultados = []
    for poliza in polizas:
        cedula = poliza.get("cedula")

        # Buscar cliente en el maestro por cédula
        cliente = clientes_por_cedula.get(cedula)
        en_maestro = cliente is not None
        correo = cliente.get("Correo") if cliente else None

        hasta = poliza.get("hasta")
        dias_hasta_vencer = None
        if hasta is not None:
            dias_hasta_vencer = (hasta - fecha_corte).days

        estado = estado_poliza(hasta, fecha_corte)

        resultados.append({
            "archivo": poliza.get("archivo"),
            "aseguradora": poliza.get("aseguradora"),
            "numero": poliza.get("numero"),
            "ramo": poliza.get("ramo"),
            "nombre": poliza.get("nombre"),
            "cedula": cedula,
            "desde": poliza.get("desde"),
            "hasta": hasta,
            "prima": poliza.get("prima"),
            "pago": poliza.get("pago"),
            "suma": poliza.get("suma"),
            "asesor": poliza.get("asesor"),
            "correo": correo,
            "en_maestro": en_maestro,
            "dias_hasta_vencer": dias_hasta_vencer,
            "estado": estado,
        })

    # Ordenar de menos a más días (lo urgente primero)
    # Las vencidas tienen días negativos, van primero
    resultados.sort(key=lambda r: (r["dias_hasta_vencer"] is None, r["dias_hasta_vencer"] if r["dias_hasta_vencer"] is not None else 999999))

    return resultados


def contar_por_estado(resultados):
    """Devuelve un diccionario con cuántas pólizas hay de cada estado."""
    conteo = defaultdict(int)
    for r in resultados:
        conteo[r["estado"]] += 1
    return dict(conteo)


def primas_por_aseguradora(resultados):
    """Devuelve un diccionario aseguradora -> suma de primas de pólizas no
    vencidas, ordenado de mayor a menor suma."""
    sumas = defaultdict(float)
    for r in resultados:
        if r["estado"] != "Vencida" and r["prima"] is not None:
            sumas[r["aseguradora"]] += r["prima"]

    # Ordenar de mayor a menor
    ordenado = dict(sorted(sumas.items(), key=lambda item: item[1], reverse=True))
    return ordenado


def buscar_inconsistencias(resultados):
    """Devuelve una lista de textos con los 3 tipos de inconsistencia:
    1. Cliente del maestro sin ninguna póliza.
    2. Póliza cuya cédula no está en el maestro.
    3. Póliza sin prima o con fecha ilegible.
    """
    inconsistencias = []

    # Cargar clientes y pólizas para cruzar
    clientes_df = cargar_clientes()
    polizas = cargar_polizas()

    # Índice de cédulas que tienen póliza
    cedulas_con_poliza = set()
    for p in polizas:
        if p.get("cedula"):
            cedulas_con_poliza.add(p["cedula"])

    # 1. Clientes del maestro sin ninguna póliza
    for _, fila in clientes_df.iterrows():
        cedula = fila["Cedula"]
        if cedula not in cedulas_con_poliza:
            nombre = fila.get("Nombre", fila.get("nombre", "Sin nombre"))
            inconsistencias.append(
                f"Cliente {cedula} ({nombre}) no tiene ninguna póliza"
            )

    # Índice de cédulas del maestro para validar pólizas
    cedulas_maestro = set(clientes_df["Cedula"].astype(str).str.strip())

    # 2 y 3. Revisar cada póliza
    for r in resultados:
        cedula = r["cedula"]
        numero = r["numero"]
        prima = r["prima"]
        hasta = r["hasta"]

        # 2. Póliza cuya cédula no está en el maestro
        if cedula and cedula not in cedulas_maestro:
            inconsistencias.append(
                f"Póliza {numero} con cédula {cedula} no está registrada en el maestro"
            )

        # 3. Póliza sin prima o con fecha ilegible
        if prima is None or hasta is None:
            inconsistencias.append(
                f"Póliza {numero} sin prima o con fecha ilegible"
            )

    return inconsistencias


def buscar_por_numero(numero, resultados=None):
    """Busca una póliza por su número en la lista de resultados."""
    if resultados is None:
        resultados = calcular_resultados()
    for r in resultados:
        if r["numero"] == numero:
            return r
    return None
