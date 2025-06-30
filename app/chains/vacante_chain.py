from rag_utils import buscar_contexto_pinecone

def buscar_vacantes_chain(client, historial):
    """Cadena para buscar vacantes: pregunta detalles, busca contexto en Pinecone y responde con el LLM."""
    pregunta = "¿Qué tipo de trabajo buscas? (puedes especificar ciudad, sueldo, modalidad, etc.)"
    print("Bot:", pregunta)
    historial.append({"role": "assistant", "content": pregunta})
    user_input = input("Tú: ")
    historial.append({"role": "user", "content": user_input})
    print("[RAG] Buscando contexto ...")
    contexto = buscar_contexto_pinecone(user_input, k=3)
    prompt_contexto = f"Contexto relevante de vacantes:\n{contexto}\n\n" if contexto else ""
    prompt_final = prompt_contexto + user_input
    mensajes = historial[:-1] + [{"role": "user", "content": prompt_final}]
    respuesta = client.client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=mensajes
    )
    mensaje = respuesta.choices[0].message.content
    print("Bot:", mensaje)
    historial.append({"role": "assistant", "content": mensaje})
