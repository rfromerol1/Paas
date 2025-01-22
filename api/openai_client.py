from openai import OpenAI
import time
import json

# Inicializa el cliente con la clave API
client = OpenAI(api_key="")

# Carga los embeddings desde el archivo JSON
def load_embeddings():
    try:
        with open('C:/Users/usuario/Desktop/Heinsontech/CHAT-IA/embeddings.json', 'r') as f:
            embeddings = json.load(f)
        return embeddings
    except FileNotFoundError:
        print("El archivo de embeddings no se encuentra.")
        return {}

# Crea el asistente solo una vez con instrucciones más detalladas
assistant = client.beta.assistants.create(
    name="Experto SAP",
    instructions=(
        "Eres un experto en SAP Business One. Responde preguntas del sistema a clientes de manera precisa y detallada, "
        "utilizando tu conocimiento profundo de la plataforma. Asegúrate de explicar las funcionalidades de SAP Business One, "
        "responder dudas relacionadas con su implementación, uso y optimización, y proporcionar recomendaciones prácticas "
        "para mejorar la experiencia de los usuarios del sistema."
    ),
    model="gpt-3.5-turbo-0125"
)

def read_thread_id():
    try:
        with open('thread_id.json', 'r') as f:
            data = json.load(f)
            return data.get('thread_id')
    except FileNotFoundError:
        return None

def write_thread_id(thread_id):
    with open('thread_id.json', 'w') as f:
        json.dump({'thread_id': thread_id}, f)

def get_or_create_thread():
    thread_id = read_thread_id()
    if thread_id:
        try:
            # Verificar si el hilo aún existe
            client.beta.threads.retrieve(thread_id)
            return thread_id
        except Exception:
            # El hilo no existe, crea uno nuevo
            return create_thread()
    else:
        return create_thread()

def create_thread():
    try:
        thread = client.beta.threads.create()
        thread_id = thread.id
        write_thread_id(thread_id)  # Guarda el nuevo ID del hilo
        return thread_id
    except Exception as e:
        print(f"Error creating thread: {e}")
        raise

def send_message(thread_id, content):
    try:
        embeddings = load_embeddings()  # Cargar los embeddings
        # Incluir el recordatorio del rol de experto y los embeddings como contexto en el mensaje
        context = f"Eres un experto en SAP Business One. Responde con precisión y detalle sobre el sistema. {content}"
        # Envía el mensaje con el contexto de su rol
        message = client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=context  # Incluir el contexto con el recordatorio del rol
        )
        return message
    except Exception as e:
        print(f"Error sending message: {e}")
        raise

def run_thread(thread_id):
    try:
        run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant.id
        )
        return run
    except Exception as e:
        print(f"Error running thread: {e}")
        raise

def delete_message(thread_id, message_id):
    try:
        client.beta.threads.messages.delete(
            thread_id=thread_id,
            message_id=message_id
        )
    except Exception as e:
        print(f"Error deleting message: {e}")
        raise

def get_response(thread_id, run_id):
    try:
        while True:
            run_result = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run_id
            )
            if run_result.status == 'completed':
                return run_result
            time.sleep(1)  # Check every second
    except Exception as e:
        print(f"Error retrieving response: {e}")
        raise

def list_messages(thread_id):
    try:
        messages = client.beta.threads.messages.list(
            thread_id=thread_id
        )
        return messages
    except Exception as e:
        print(f"Error listing messages: {e}")
        raise
