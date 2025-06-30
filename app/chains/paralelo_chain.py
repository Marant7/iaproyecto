from .duda_chain import responder_dudas_chain
from .tip_chain import tips_postulacion_chain
import threading
import copy

def cadenas_paralelas(client, historial):
    """Ejecuta dudas y tips en paralelo y muestra ambos resultados claramente."""
    resultados = {}
    def run_dudas():
        h = copy.deepcopy(historial)
        import io, sys
        buffer = io.StringIO()
        sys_stdout = sys.stdout
        sys.stdout = buffer
        responder_dudas_chain(client, h, encabezado="Resultado Dudas")
        sys.stdout = sys_stdout
        resultados['dudas'] = buffer.getvalue()

    def run_tips():
        h = copy.deepcopy(historial)
        import io, sys
        buffer = io.StringIO()
        sys_stdout = sys.stdout
        sys.stdout = buffer
        tips_postulacion_chain(client, h, encabezado="Resultado Tips")
        sys.stdout = sys_stdout
        resultados['tips'] = buffer.getvalue()

    t1 = threading.Thread(target=run_dudas)
    t2 = threading.Thread(target=run_tips)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    print("\n=== Resultados Paralelos ===")
    print(resultados['dudas'])
    print(resultados['tips'])
