"""Capa de servicio: genera el aviso de renovación en PDF con fpdf2."""

from fpdf import FPDF


def generar_aviso_poliza(poliza, cliente):
    """Crea el aviso de renovación en formato A4 vertical y lo devuelve en bytes.

    Args:
        poliza: diccionario con los datos de la póliza.
        cliente: diccionario o serie con los datos del cliente (incluye nombre y correo).

    Returns:
        bytes: contenido del PDF generado.
    """
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Título
    pdf.set_font("Arial", "B", 16)
    pdf.set_text_color(174, 24, 0)  # rojo #AE1800
    pdf.cell(0, 10, "Aviso de Renovación de Póliza", ln=True, align="C")
    pdf.ln(10)

    # Aseguradora
    pdf.set_font("Arial", "", 12)
    pdf.set_text_color(32, 30, 29)  # negro #201E1D
    pdf.cell(0, 8, f"Aseguradora: {poliza.get('aseguradora', 'N/A')}", ln=True)
    pdf.ln(5)

    # Datos de la póliza
    campos = [
        ("Número de póliza", poliza.get("numero", "N/A")),
        ("Ramo", poliza.get("ramo", "N/A")),
        ("Tomador / Asegurado", poliza.get("nombre", cliente.get("Nombre", "N/A") if cliente else "N/A")),
        ("Cédula", poliza.get("cedula", "N/A")),
        ("Vigencia desde", poliza.get("desde", "N/A")),
        ("Vigencia hasta", poliza.get("hasta", "N/A")),
        ("Prima anual", poliza.get("prima", "N/A")),
        ("Forma de pago", poliza.get("pago", "N/A")),
        ("Suma asegurada", poliza.get("suma", "N/A")),
        ("Asesor", poliza.get("asesor", "N/A")),
    ]

    for etiqueta, valor in campos:
        pdf.set_font("Arial", "B", 11)
        pdf.cell(50, 7, f"{etiqueta}:")
        pdf.set_font("Arial", "", 11)
        pdf.cell(0, 7, str(valor), ln=True)

    pdf.ln(10)

    # Pie de página
    pdf.set_font("Arial", "I", 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 7, "Este aviso es un recordatorio de renovación generado automáticamente.", ln=True, align="C")

    # Devolver el PDF como bytes
    return pdf.output(dest="S").encode("latin-1")
