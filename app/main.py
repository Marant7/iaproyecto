def responder_dudas_chain(client, historial, encabezado=None):
    """Cadena para responder dudas sobre el puesto."""
    if encabezado:
        print(f"\n--- {encabezado} ---")
    pregunta = "¿Sobre qué puesto tienes dudas? (puedes preguntar por sueldo estimado o habilidades necesarias)"
    print("Bot (Dudas):", pregunta)
    historial.append({"role": "assistant", "content": pregunta})
    user_input = input("Tú: ")
    historial.append({"role": "user", "content": user_input})
    respuesta = client.client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=historial
    )
    mensaje = respuesta.choices[0].message.content
    print("Bot (Dudas):", mensaje)
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
    resultados = {}
    def run_dudas():
        h = historial.copy()
        import io, sys
        buffer = io.StringIO()
        sys_stdout = sys.stdout
        sys.stdout = buffer
        responder_dudas_chain(client, h, encabezado="Resultado Dudas")
        sys.stdout = sys_stdout
        resultados['dudas'] = buffer.getvalue()

    def run_tips():
        h = historial.copy()
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

def buscar_vacantes_chain(client, historial):
    """Cadena para buscar vacantes: pregunta detalles y responde con el LLM."""
    # Paso 1: Preguntar tipo de trabajo
    pregunta = "¿Qué tipo de trabajo buscas? (puedes especificar ciudad, sueldo, modalidad, etc.)"
    print("Bot:", pregunta)
    historial.append({"role": "assistant", "content": pregunta})
    user_input = input("Tú: ")
    historial.append({"role": "user", "content": user_input})
    # Paso 2: Consultar al LLM
    respuesta = client.client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=historial
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
            combinacion_cadenas(client, historial)
        # Paralela: dudas y tips
        elif tiene_duda and tiene_tip:
            cadenas_paralelas(client, historial)
        # Solo vacantes
        elif tiene_vacante:
            buscar_vacantes_chain(client, historial)
        # Solo dudas
        elif tiene_duda:
            responder_dudas_chain(client, historial)
        # Solo tips
        elif tiene_tip:
            tips_postulacion_chain(client, historial)
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
