"""Controlador: rutas de Flask (Blueprint). No calcula, llama al modelo y servicio."""

import os
import io
import zipfile
from datetime import date

from flask import Blueprint, render_template, send_file, abort, url_for

from models.datos import cargar_clientes, cargar_polizas
from models.polizas import (
    FECHA_CORTE,
    DIAS_AVISO,
    estado_poliza,
    calcular_resultados,
    contar_por_estado,
    primas_por_aseguradora,
    buscar_inconsistencias,
    buscar_por_numero,
)
from services.generador_aviso import generar_aviso_poliza

polizas_bp = Blueprint("polizas", __name__)


@polizas_bp.route("/")
def tablero():
    """Ruta principal: muestra el tablero con contadores, primas, inconsistencias y tabla."""
    resultados = calcular_resultados(FECHA_CORTE)
    contadores = contar_por_estado(resultados)
    primas = primas_por_aseguradora(resultados)
    inconsistencias = buscar_inconsistencias(resultados)

    return render_template(
        "tablero.html",
        contadores=contadores,
        primas=primas,
        inconsistencias=inconsistencias,
        resultados=resultados,
    )


@polizas_bp.route("/aviso/<numero>")
def aviso(numero):
    """Devuelve el aviso de renovación en PDF para la póliza dada.

    Devuelve 404 si la póliza no existe o está vigente.
    """
    resultados = calcular_resultados(FECHA_CORTE)
    poliza = buscar_por_numero(numero, resultados)

    if poliza is None:
        abort(404)

    if poliza["estado"] == "Vigente":
        abort(404)

    clientes_df = cargar_clientes()
    cliente = None
    if poliza.get("cedula"):
        fila = clientes_df[clientes_df["Cedula"] == poliza["cedula"]]
        if not fila.empty:
            cliente = fila.iloc[0].to_dict()

    pdf_bytes = generar_aviso_poliza(poliza, cliente)

    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"aviso_{numero}.pdf",
    )


@polizas_bp.route("/descargar-avisos")
def descargar_avisos():
    """Descarga un .zip con los avisos de todas las pólizas por vencer y vencidas."""
    resultados = calcular_resultados(FECHA_CORTE)
    clientes_df = cargar_clientes()

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for r in resultados:
            if r["estado"] in ("Por vencer", "Vencida"):
                cedula = r.get("cedula")
                cliente = None
                if cedula:
                    fila = clientes_df[clientes_df["Cedula"] == cedula]
                    if not fila.empty:
                        cliente = fila.iloc[0].to_dict()

                pdf_bytes = generar_aviso_poliza(r, cliente)
                zf.writestr(f"aviso_{r['numero']}.pdf", pdf_bytes)

    buffer.seek(0)

    return send_file(
        buffer,
        mimetype="application/zip",
        as_attachment=True,
        download_name="avisos_renovacion.zip",
    )
