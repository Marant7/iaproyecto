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
