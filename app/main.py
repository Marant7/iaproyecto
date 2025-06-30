
# Importar cadenas modulares
from chains.duda_chain import responder_dudas_chain
from chains.tip_chain import tips_postulacion_chain
from chains.vacante_chain import buscar_vacantes_chain
from chains.combinacion_chain import combinacion_cadenas
from chains.paralelo_chain import cadenas_paralelas


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
