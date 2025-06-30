def responder_dudas_chain(client, historial, encabezado=None):
    """Cadena para responder dudas sobre el puesto."""
    if encabezado:
        print(f"\n--- {encabezado} ---")
    pregunta = "¿Sobre qué puesto tienes dudas? (puedes preguntar por sueldo estimado o habilidades necesarias)"
    print("Bot (Dudas):", pregunta)
    historial.append({"role": "assistant", "content": pregunta})
    user_input = input("Tú: ")
    # Cadena de pensamiento + salida estructurada JSON
    cot_prompt = (
        user_input +
        " Primero, razona paso a paso y escribe tu razonamiento bajo el encabezado 'Razonamiento:'. "
        "Después, da una respuesta final clara bajo el encabezado 'Conclusión:'. "
        "Finalmente, responde en formato JSON con los campos: razonamiento, conclusion, rango_sueldo (min, max, moneda), ciudad, puesto. "
        "Ejemplo de salida JSON: {\"razonamiento\": \"...\", \"conclusion\": \"...\", \"rango_sueldo\": {\"min\": 15000, \"max\": 22000, \"moneda\": \"MXN\"}, \"ciudad\": \"Guadalajara\", \"puesto\": \"Analista de datos junior\"}"
    )
    historial.append({"role": "user", "content": cot_prompt})
    import json
    respuesta = client.client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=historial
    )
    mensaje = respuesta.choices[0].message.content
    # Intentar extraer JSON de la respuesta
    json_data = None
    try:
        start = mensaje.find('{')
        end = mensaje.rfind('}') + 1
        if start != -1 and end != -1:
            json_str = mensaje[start:end]
            json_data = json.loads(json_str)
    except Exception:
        pass
    # Mostrar solo la parte antes del bloque JSON o cualquier encabezado relacionado
    import re
    # Busca el inicio de cualquier encabezado de bloque JSON
    patrones = [r'\*\*Respuesta en formato JSON:?\*\*', r'Respuesta en formato JSON:?', r'```json', r'```\s*{', r'\n{']
    corte = len(mensaje)
    for patron in patrones:
        m = re.search(patron, mensaje, re.IGNORECASE)
        if m:
            corte = min(corte, m.start())
    texto_sin_json = mensaje[:corte].rstrip()
    if texto_sin_json:
        print("Bot (Dudas):", texto_sin_json)
    if json_data:
        # Guardar la salida estructurada en un archivo .json (append)
        import os
        output_dir = "salidas_estructuradas"
        os.makedirs(output_dir, exist_ok=True)
        from datetime import datetime
        filename = f"duda_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
    historial.append({"role": "assistant", "content": mensaje})

def tips_postulacion_chain(client, historial, encabezado=None):
    """Cadena para dar tips de postulación."""
    if encabezado:
        print(f"\n--- {encabezado} ---")
    pregunta = "¿Te gustaría recibir tips para entrevistas o simulación de preguntas?"
    print("Bot (Tips):", pregunta)
    historial.append({"role": "assistant", "content": pregunta})
    user_input = input("Tú: ")
    historial.append({"role": "user", "content": user_input})
    respuesta = client.client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=historial
    )
    mensaje = respuesta.choices[0].message.content
    print("Bot (Tips):", mensaje)
    historial.append({"role": "assistant", "content": mensaje})

def combinacion_cadenas(client, historial):
    """Ejemplo de combinación de cadenas: buscar vacantes y luego dar tips de postulación."""
    buscar_vacantes_chain(client, historial)
    tips_postulacion_chain(client, historial)

import threading
def cadenas_paralelas(client, historial):
    """Ejecuta dudas y tips en paralelo y muestra ambos resultados claramente."""
    import copy
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


from llm_client import LLMClient
import os
from dotenv import load_dotenv

# --- INICIO: Integración RAG ---
from rag_utils import buscar_contexto_pinecone
# --- FIN: Integración RAG ---


def buscar_vacantes_chain(client, historial):
    """Cadena para buscar vacantes: pregunta detalles, busca contexto en Pinecone y responde con el LLM."""
    pregunta = "¿Qué tipo de trabajo buscas? (puedes especificar ciudad, sueldo, modalidad, etc.)"
    print("Bot:", pregunta)
    historial.append({"role": "assistant", "content": pregunta})
    user_input = input("Tú: ")
    historial.append({"role": "user", "content": user_input})

    # --- INICIO: Recuperar contexto RAG ---
    print("[RAG] Buscando contexto ...")
    contexto = buscar_contexto_pinecone(user_input, k=3)
    if contexto:
        prompt_contexto = f"Contexto relevante de vacantes:\n{contexto}\n\n"
    else:
        prompt_contexto = ""
    # --- FIN: Recuperar contexto RAG ---

    # Paso 2: Consultar al LLM con contexto recuperado
    prompt_final = prompt_contexto + user_input
    mensajes = historial[:-1] + [{"role": "user", "content": prompt_final}]
    respuesta = client.client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=mensajes
    )
    mensaje = respuesta.choices[0].message.content
    print("Bot:", mensaje)
    historial.append({"role": "assistant", "content": mensaje})

def main():
    # Cargar variables de entorno desde .env
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Por favor, configura la variable de entorno OPENAI_API_KEY en el archivo .env.")
        return

    client = LLMClient(api_key=api_key)
    print("\nChatbot de Empleos listo para ayudarte. Escribe 'salir' para terminar.\n")
    system_prompt = (
        "Eres un asistente experto en empleos. Ayudas a buscar vacantes, filtras por ciudad, sueldo y modalidad (remoto/presencial), "
        "respondes dudas sobre puestos (como sueldo estimado y habilidades necesarias), das tips de postulación, preparas para entrevistas y puedes hacer preguntas simuladas. "
        "Guía al usuario con preguntas claras y ofrece ayuda proactiva."
    )
    saludo_inicial = "¡Hola! ¿En qué puedo ayudarte hoy? Puedes preguntarme por vacantes, dudas sobre puestos, tips de postulación, o pedir una combinación o respuesta paralela."
    print("Bot:", saludo_inicial)
    historial = [
        {"role": "system", "content": system_prompt},
        {"role": "assistant", "content": saludo_inicial}
    ]


    # Diccionario de funciones ejecutables (runnables)
    def ejecutar_vacante(client, historial):
        print("[Runnable] Ejecutando función de vacantes...")
        buscar_vacantes_chain(client, historial)

    def ejecutar_duda(client, historial):
        print("[Runnable] Ejecutando función de dudas...")
        responder_dudas_chain(client, historial)

    def ejecutar_tip(client, historial):
        print("[Runnable] Ejecutando función de tips...")
        tips_postulacion_chain(client, historial)

    def ejecutar_combinacion(client, historial):
        print("[Runnable] Ejecutando función de combinación...")
        combinacion_cadenas(client, historial)

    def ejecutar_paralelo(client, historial):
        print("[Runnable] Ejecutando función de paralelo...")
        cadenas_paralelas(client, historial)

    runnables = {
        "vacante": ejecutar_vacante,
        "duda": ejecutar_duda,
        "tip": ejecutar_tip,
        "combinacion": ejecutar_combinacion,
        "paralelo": ejecutar_paralelo
    }

    while True:
        user_input = input("Tú: ")
        if user_input.lower() in ["salir", "exit", "quit"]:
            print("¡Hasta luego!")
            break
        # Detección de intenciones múltiples
        texto = user_input.lower()
        tiene_vacante = any(pal in texto for pal in ["vacante", "trabajo", "empleo"])
        tiene_duda = any(pal in texto for pal in ["duda", "sueldo", "habilidad"])
        tiene_tip = any(pal in texto for pal in ["tip", "entrevista", "simulad"])

        historial.append({"role": "user", "content": user_input})

        # Combinación: vacantes y tips
        if tiene_vacante and tiene_tip:
            runnables["combinacion"](client, historial)
        # Paralela: dudas y tips
        elif tiene_duda and tiene_tip:
            runnables["paralelo"](client, historial)
        # Solo vacantes usando runnable
        elif tiene_vacante:
            runnables["vacante"](client, historial)
        # Solo dudas usando runnable
        elif tiene_duda:
            runnables["duda"](client, historial)
        # Solo tips usando runnable
        elif tiene_tip:
            runnables["tip"](client, historial)
        else:
            respuesta = client.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=historial
            )
            mensaje = respuesta.choices[0].message.content
            print("Bot:", mensaje)
            historial.append({"role": "assistant", "content": mensaje})

if __name__ == "__main__":
    main()
