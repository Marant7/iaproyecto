
# --- INICIO: Adaptación de main.py a Gradio ---
import gradio as gr
from llm_client import LLMClient
from rag_utils import buscar_contexto_pinecone
from dotenv import load_dotenv
import os
import json
import re
from datetime import datetime

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
client = LLMClient(api_key=api_key)

system_prompt = (
    "Eres un asistente experto en empleos. Ayudas a buscar vacantes, filtras por ciudad, sueldo y modalidad (remoto/presencial), "
    "respondes dudas sobre puestos (como sueldo estimado y habilidades necesarias), das tips de postulación, preparas para entrevistas y puedes hacer preguntas simuladas. "
    "Guía al usuario con preguntas claras y ofrece ayuda proactiva."
)
saludo_inicial = "¡Hola! ¿En qué puedo ayudarte hoy? Puedes preguntarme por vacantes, dudas sobre puestos, tips de postulación, o pedir una combinación o respuesta paralela."

def gradio_chain(user_input, history, tipo):
    # history: [[user, bot], ...]
    # Convertir history a historial tipo OpenAI
    historial = [
        {"role": "system", "content": system_prompt},
        {"role": "assistant", "content": saludo_inicial}
    ]
    for par in history:
        if len(par) == 2:
            historial.append({"role": "user", "content": par[0]})
            historial.append({"role": "assistant", "content": par[1]})
    # Si es el primer mensaje, mostrar saludo
    if len(history) == 0:
        return saludo_inicial

    if tipo == "Vacante":
        contexto = buscar_contexto_pinecone(user_input, k=3)
        prompt_contexto = f"Contexto relevante de vacantes:\n{contexto}\n\n" if contexto else ""
        prompt_final = prompt_contexto + user_input
        mensajes = historial + [{"role": "user", "content": prompt_final}]
        respuesta = client.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=mensajes
        )
        mensaje = respuesta.choices[0].message.content
        return mensaje
    elif tipo == "Duda":
        # Recuperar contexto RAG igual que en Vacante
        contexto = buscar_contexto_pinecone(user_input, k=3)
        prompt_contexto = f"Contexto relevante de vacantes:\n{contexto}\n\n" if contexto else ""
        cot_prompt = (
            prompt_contexto + user_input +
            " Primero, razona paso a paso y escribe tu razonamiento bajo el encabezado 'Razonamiento:'. "
            "Después, da una respuesta final clara bajo el encabezado 'Conclusión:'. "
            "Finalmente, responde en formato JSON con los campos: razonamiento, conclusion, rango_sueldo (min, max, moneda), ciudad, puesto. "
        )
        mensajes = historial + [{"role": "user", "content": cot_prompt}]
        respuesta = client.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=mensajes
        )
        mensaje = respuesta.choices[0].message.content
        # Intentar extraer JSON y guardar
        json_data = None
        try:
            start = mensaje.find('{')
            end = mensaje.rfind('}') + 1
            if start != -1 and end != -1:
                json_str = mensaje[start:end]
                json_data = json.loads(json_str)
        except Exception:
            pass
        if json_data:
            output_dir = "salidas_estructuradas"
            os.makedirs(output_dir, exist_ok=True)
            filename = f"duda_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = os.path.join(output_dir, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
        return mensaje
    elif tipo == "Tip":
        prompt = "Dame tips para entrevistas o simulación de preguntas sobre: " + user_input
        mensajes = historial + [{"role": "user", "content": prompt}]
        respuesta = client.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=mensajes
        )
        mensaje = respuesta.choices[0].message.content
        return mensaje
    elif tipo == "Combinación":
        # Buscar vacante y luego tips
        r1 = gradio_chain(user_input, history, "Vacante")
        r2 = gradio_chain(user_input, history, "Tip")
        return f"[Vacante]\n{r1}\n\n[Tips]\n{r2}"
    elif tipo == "Paralelo":
        # Ejecutar dudas y tips en paralelo (simulado)
        r1 = gradio_chain(user_input, history, "Duda")
        r2 = gradio_chain(user_input, history, "Tip")
        return f"[Duda]\n{r1}\n\n[Tips]\n{r2}"
    else:
        mensajes = historial + [{"role": "user", "content": user_input}]
        respuesta = client.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=mensajes
        )
        mensaje = respuesta.choices[0].message.content
        return mensaje

with gr.Blocks() as demo:
    gr.Markdown("# Chatbot de Empleos")
    tipo = gr.Radio(["Vacante", "Duda", "Tip", "Combinación", "Paralelo"], label="Tipo de consulta", value="Vacante")
    chatbox = gr.Chatbot(label="Conversación", type='messages')
    input_box = gr.Textbox(label="Tu mensaje")
    send_btn = gr.Button("Enviar")


    def responder_gradio(user_input, chat_history, tipo):
        # chat_history: lista de pares [usuario, bot]
        respuesta = gradio_chain(user_input, chat_history, tipo)
        # Convertir historial a formato OpenAI messages para gr.Chatbot (role/content)
        new_history = []
        for par in chat_history:
            if len(par) == 2:
                new_history.append({"role": "user", "content": par[0]})
                new_history.append({"role": "assistant", "content": par[1]})
        new_history.append({"role": "user", "content": user_input})
        new_history.append({"role": "assistant", "content": respuesta})
        # Para gr.Chatbot type='messages', solo se pasan los mensajes (no system)
        messages_for_gradio = [m for m in new_history if m["role"] in ("user", "assistant")]
        return "", messages_for_gradio, tipo

    send_btn.click(
        responder_gradio,
        inputs=[input_box, chatbox, tipo],
        outputs=[input_box, chatbox, tipo]
    )

demo.launch(share=True)
