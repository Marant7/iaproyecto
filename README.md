# Manual de Usuario: Chatbot de Empleos con RAG, Pinecone y OpenAI

Este manual te guía paso a paso para ejecutar y probar el chatbot de empleos en modo consola, aprovechando la modularidad y las funcionalidades avanzadas del proyecto.

---

## 1. Requisitos previos

- **Python 3.8+** instalado en tu sistema.
- **Dependencias** instaladas (ver sección 3).
- **Claves de API**:
  - Una clave válida de OpenAI (`OPENAI_API_KEY`).
  - Acceso y configuración de Pinecone (si usas RAG).
- **Archivos de datos**: Los archivos de vacantes deben estar cargados en Pinecone.

---

## 2. Estructura del proyecto

```
app/
  main.py                # Script principal (consola)
  chains/                # Lógica modular de cada flujo
    duda_chain.py
    tip_chain.py
    vacante_chain.py
    combinacion_chain.py
    paralelo_chain.py
  llm_client.py          # Cliente para OpenAI
  rag_utils.py           # Utilidades para RAG y Pinecone
.env                     # Variables de entorno (no subir a repositorio)
requirements.txt         # Dependencias
```

---

## 3. Instalación de dependencias

Desde la raíz del proyecto, ejecuta:

```bash
python -m venv .venv
.venv\Scripts\activate  # En Windows
pip install -r requirements.txt
```

---

## 4. Configuración de variables de entorno

Crea un archivo `.env` en la raíz del proyecto con el siguiente contenido:

```
OPENAI_API_KEY=tu_clave_openai
PINECONE_API_KEY=tu_clave_pinecone
PINECONE_ENV=tu_entorno_pinecone
PINECONE_INDEX=nombre_de_tu_indice
```

---

## 5. Ejecución del chatbot en consola

Desde la carpeta `app/`, ejecuta:

```bash
python main.py
```

Verás un mensaje de bienvenida. Puedes interactuar escribiendo preguntas o solicitudes, por ejemplo:

- "Quiero un trabajo de analista de datos en Lima"
- "¿Cuánto gana un programador Python junior?"
- "Dame tips para entrevistas"

El bot detecta automáticamente la intención y ejecuta el flujo adecuado:
- **Vacante**: Busca empleos usando RAG.
- **Duda**: Responde dudas con razonamiento y salida estructurada.
- **Tip**: Da consejos para entrevistas.
- **Combinación**: Vacante + Tip.
- **Paralelo**: Duda + Tip.

---

## 6. Archivos de salida

Las respuestas estructuradas de tipo "Duda" se guardan automáticamente en la carpeta `app/salidas_estructuradas/` en formato JSON.

---

## 7. Consejos para la exposición

- Explica que el código está modularizado: cada flujo está en un archivo diferente bajo `app/chains/`.
- Muestra cómo el bot detecta la intención y ejecuta el flujo adecuado.
- Demuestra la integración RAG (Pinecone + OpenAI) en vacantes y dudas.
- Enseña un ejemplo de archivo JSON generado.
- Si tienes interfaz web (Gradio), puedes mostrarla como extra.

---

## 8. Solución de problemas

- Si ves errores de API Key, revisa tu archivo `.env`.
- Si no aparecen resultados de vacantes, asegúrate de que Pinecone esté correctamente configurado y poblado.
- Si tienes problemas con dependencias, reinstala con `pip install -r requirements.txt`.

---

## 9. Ejemplos de prompts y resultados esperados

A continuación, algunos ejemplos de preguntas y comandos que puedes usar para demostrar cada funcionalidad del bot. Puedes copiar y pegar estos prompts durante tu exposición:

### Buscar vacantes (RAG)
- **Prompt:**
  > Quiero un trabajo de analista de datos en Lima
- **Resultado esperado:**
  > El bot muestra contexto relevante de vacantes y responde con detalles de empleos disponibles.

### Duda sobre puesto (Razonamiento + RAG + JSON)
- **Prompt:**
  > ¿Cuánto gana un programador Python junior?
- **Resultado esperado:**
  > El bot muestra un razonamiento bajo el encabezado "Razonamiento:", una conclusión bajo "Conclusión:", y genera un archivo JSON con los campos razonamiento, conclusión, rango_sueldo, ciudad y puesto.

### Tips para entrevistas
- **Prompt:**
  > Dame tips para entrevistas de trabajo
- **Resultado esperado:**
  > El bot responde con consejos prácticos para entrevistas o simulaciones de preguntas.

### Combinación (Vacante + Tip)
- **Prompt:**
  > Busco empleo de desarrollador backend y tips para entrevistas
- **Resultado esperado:**
  > El bot responde primero con vacantes y luego con tips, ambos en la misma respuesta.

### Paralelo (Duda + Tip)
- **Prompt:**
  > ¿Qué habilidades necesito para ser analista de datos? Dame también tips para entrevistas
- **Resultado esperado:**
  > El bot responde con el razonamiento y conclusión de la duda, y en paralelo con tips para entrevistas.

---

## 10. Notas sobre los prompts y el flujo

- Puedes escribir los prompts en lenguaje natural, el bot detecta la intención automáticamente.
- Para dudas, el bot siempre separa el razonamiento y la conclusión, y guarda la respuesta estructurada en JSON.
- Para vacantes y dudas, el bot utiliza RAG (recupera contexto relevante de Pinecone).
- Puedes combinar intenciones en una sola pregunta (por ejemplo, "vacante" y "tip" o "duda" y "tip").
- Si el bot no entiende la intención, responderá de forma general usando el modelo de lenguaje.

---

## 11. Ejemplos de prompts basados en tu base de datos vectorial

Estos ejemplos usan puestos, ciudades y tecnologías reales de tu base de datos. Así garantizas que el bot recupere contexto relevante y la demo sea realista.

### Buscar vacantes (RAG)
- **Prompt:**
  > Quiero un trabajo de Desarrollador Fullstack Node en Chiclayo
- **Prompt:**
  > ¿Hay vacantes de Desarrollador Java Backend en Trujillo?

### Duda sobre puesto (Razonamiento + RAG + JSON)
- **Prompt:**
  > ¿Cuánto gana un Desarrollador Móvil iOS en Perú?
- **Prompt:**
  > ¿Qué habilidades necesito para ser Desarrollador Fullstack Node + Nest + React en Chiclayo?

### Tips para entrevistas
- **Prompt:**
  > Dame tips para entrevistas de Desarrollador Java Backend

### Combinación (Vacante + Tip)
- **Prompt:**
  > Busco empleo de Desarrollador Móvil iOS en Trujillo y tips para entrevistas

### Paralelo (Duda + Tip)
- **Prompt:**
  > ¿Qué sueldo puedo esperar como Desarrollador Fullstack Node en Chiclayo? Dame también tips para entrevistas

**Recomendación:** Usa estos ejemplos en tu exposición para mostrar cómo el bot recupera información real de tu base vectorial y responde de forma precisa y contextualizada.

---

¡Con estos ejemplos y el manual, tienes todo lo necesario para exponer y demostrar tu chatbot de empleos!
