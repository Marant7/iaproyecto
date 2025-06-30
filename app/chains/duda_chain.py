from rag_utils import buscar_contexto_pinecone
import json
import os
from datetime import datetime
import re

def responder_dudas_chain(client, historial, encabezado=None):
    """Cadena para responder dudas sobre el puesto, con RAG."""
    if encabezado:
        print(f"\n--- {encabezado} ---")
    pregunta = "¿Sobre qué puesto tienes dudas? (puedes preguntar por sueldo estimado o habilidades necesarias)"
    print("Bot (Dudas):", pregunta)
    historial.append({"role": "assistant", "content": pregunta})
    user_input = input("Tú: ")
    print("[RAG] Buscando contexto ...")
    contexto = buscar_contexto_pinecone(user_input, k=3)
    prompt_contexto = f"Contexto relevante de vacantes:\n{contexto}\n\n" if contexto else ""
    cot_prompt = (
        prompt_contexto + user_input +
        " Primero, razona paso a paso y escribe tu razonamiento bajo el encabezado 'Razonamiento:'. "
        "Después, da una respuesta final clara bajo el encabezado 'Conclusión:'. "
        "Finalmente, responde en formato JSON con los campos: razonamiento, conclusion, rango_sueldo (min, max, moneda), ciudad, puesto. "
        "Ejemplo de salida JSON: {\"razonamiento\": \"...\", \"conclusion\": \"...\", \"rango_sueldo\": {\"min\": 15000, \"max\": 22000, \"moneda\": \"MXN\"}, \"ciudad\": \"Guadalajara\", \"puesto\": \"Analista de datos junior\"}"
    )
    historial.append({"role": "user", "content": cot_prompt})
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
        output_dir = "salidas_estructuradas"
        os.makedirs(output_dir, exist_ok=True)
        filename = f"duda_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
    historial.append({"role": "assistant", "content": mensaje})
