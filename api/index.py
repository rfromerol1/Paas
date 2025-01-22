from flask import Flask, request, jsonify 
from flask_cors import CORS
from api.openai_client import get_or_create_thread, send_message, run_thread, get_response, list_messages, delete_message
import json

app = Flask(__name__)
#CORS(app)
@app.route('/')
def home():
    return 'Hello, World!'

@app.route('/about')
def about():
    return 'About'

  # Permite CORS para todas las rutas

# Inicializa la variable global `thread_id`
thread_id = None

# Función para leer el ID del hilo desde un archivo
def read_thread_id():
    try:
        with open('thread_id.json', 'r') as f:
            data = json.load(f)
            return data.get('thread_id')
    except FileNotFoundError:
        return None

# Función para escribir el ID del hilo en un archivo
def write_thread_id(thread_id):
    with open('thread_id.json', 'w') as f:
        json.dump({'thread_id': thread_id}, f)

# Función para eliminar todos los mensajes de un hilo
def delete_old_messages(thread_id):
    messages_page = list_messages(thread_id)
    messages = messages_page.data if hasattr(messages_page, 'data') else []
    for message in messages:
        if message.role != 'user':  # Solo elimina mensajes que no son del usuario
            delete_message(thread_id, message.id)

# Inicializa la variable global `thread_id` al inicio
thread_id = read_thread_id()
print(f"Initialized thread_id: {thread_id}")  # Verifica la inicialización

@app.route('/api/ask', methods=['POST'])
def ask_question():
    global thread_id
    request_data = request.json
    question = request_data.get('question')
    
    if not question:
        return jsonify({"response": ["No question provided"]})

    try:
        if thread_id is None:
            thread_id = get_or_create_thread()
            write_thread_id(thread_id)  # Guarda el nuevo ID del hilo
            print("Thread created:", thread_id)
        
        # Elimina los mensajes viejos
        delete_old_messages(thread_id)
        
        send_message(thread_id, question)
        print("Message sent to thread ID:", thread_id)

        run = run_thread(thread_id)
        print("Run created:", run)

        run_result = get_response(thread_id, run.id)
        print("Run result:", run_result)

        messages_page = list_messages(thread_id)
        messages = messages_page.data if hasattr(messages_page, 'data') else []
        print("Messages retrieved:", messages)

        # Extraer el último mensaje del asistente
        response_content = None
        for message in reversed(messages):
            if message.role == 'assistant':
                # Extrae el texto del mensaje
                if message.content:
                    response_content = [content_block.text.value for content_block in message.content if content_block.type == 'text']
                break
        
        if response_content is None:
            return jsonify({"response": ["No response from the assistant"]})

        return jsonify({"response": response_content})
    
    except Exception as e:
        print(f"Error in /api/ask: {e}")
        return jsonify({"response": ["An error occurred"]})