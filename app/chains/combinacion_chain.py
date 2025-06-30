from .vacante_chain import buscar_vacantes_chain
from .tip_chain import tips_postulacion_chain

def combinacion_cadenas(client, historial):
    """Ejemplo de combinación de cadenas: buscar vacantes y luego dar tips de postulación."""
    buscar_vacantes_chain(client, historial)
    tips_postulacion_chain(client, historial)
