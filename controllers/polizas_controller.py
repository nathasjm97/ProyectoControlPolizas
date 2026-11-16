"""Controlador: rutas de Flask (Blueprint). No calcula, llama al modelo y servicio."""

import os
import io
import zipfile
from datetime import date
from werkzeug.utils import secure_filename

from flask import Blueprint, render_template, send_file, abort, url_for, request, redirect, flash

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

# Extensiones permitidas para subida
ALLOWED_EXTENSIONS = {"xlsx", "xls"}


def archivo_permitido(nombre_archivo):
    """Devuelve True si el archivo tiene extensión permitida."""
    return "." in nombre_archivo and nombre_archivo.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


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


@polizas_bp.route("/importar-excel", methods=["GET", "POST"])
def importar_excel():
    """Permite subir un nuevo archivo Excel de clientes.

    Guarda el archivo en la carpeta uploads/ (no modifica data/).
    """
    if request.method == "POST":
        if "archivo" not in request.files:
            flash("No se seleccionó ningún archivo.", "error")
            return redirect(request.url)

        archivo = request.files["archivo"]

        if archivo.filename == "":
            flash("No se seleccionó ningún archivo.", "error")
            return redirect(request.url)

        if archivo and archivo_permitido(archivo.filename):
            nombre_seguro = secure_filename(archivo.filename)
            ruta_destino = os.path.join("uploads", nombre_seguro)
            archivo.save(ruta_destino)
            flash(f"Archivo '{nombre_seguro}' subido correctamente a uploads/.", "exito")
            return redirect(url_for("polizas.tablero"))
        else:
            flash("Solo se permiten archivos .xlsx o .xls.", "error")
            return redirect(request.url)

    return render_template("tablero.html", mostrar_importar=True)


@polizas_bp.route("/generar-avisos")
def generar_avisos():
    """Genera los PDFs de aviso para pólizas por vencer y vencidas,
    los guarda en output/avisos/ y muestra la lista de archivos creados."""
    resultados = calcular_resultados(FECHA_CORTE)
    clientes_df = cargar_clientes()

    # Carpeta de salida para los avisos generados
    carpeta_salida = os.path.join("output", "avisos")
    os.makedirs(carpeta_salida, exist_ok=True)

    archivos_generados = []

    for r in resultados:
        if r["estado"] in ("Por vencer", "Vencida"):
            cedula = r.get("cedula")
            cliente = None
            if cedula:
                fila = clientes_df[clientes_df["Cedula"] == cedula]
                if not fila.empty:
                    cliente = fila.iloc[0].to_dict()

            pdf_bytes = generar_aviso_poliza(r, cliente)
            nombre_archivo = f"aviso_{r['numero']}.pdf"
            ruta_archivo = os.path.join(carpeta_salida, nombre_archivo)

            with open(ruta_archivo, "wb") as f:
                f.write(pdf_bytes)

            archivos_generados.append({
                "numero": r["numero"],
                "nombre_archivo": nombre_archivo,
                "estado": r["estado"],
                "aseguradora": r["aseguradora"],
                "cliente": r["nombre"],
            })

    return render_template(
        "avisos_generados.html",
        archivos=archivos_generados,
    )
