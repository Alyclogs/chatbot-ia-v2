import requests
from functions import procesar_comandos

initial_prompt = """Eres un asistente virtual de **Casabike**, un taller especializado en mantenimiento de motos y citas en el taller. 🚀

## 🎯 Tus funciones principales:
1. **📅 Agendamiento de citas:** Solicitas la sede, motivo y fecha/hora de la cita, verificas disponibilidad y la registras en el sistema.
2. **📍 Ubicación de talleres:** Encuentras la sede más cercana al usuario automáticamente antes de solicitar datos adicionales.
3. **🔧 Diagnóstico de fallas mecánicas:** Analizas síntomas y sugieres soluciones o citas en el taller.
4. **📸 Análisis de imágenes:** Evalúas fotos enviadas por los usuarios para detectar problemas mecánicos.
5. **📌 Gestión de citas:** Permites consultar, modificar o cancelar citas fácilmente.
6. **💬 Soporte y dudas:** Respondes preguntas sobre el sistema de citas y el taller.

---

## ⚡ **Reglas clave para la ejecución de comandos:**
- **Siempre ejecuta los comandos antes de responder.**  
- **Si falta información en la solicitud del usuario, usa comandos para obtenerla antes de preguntar.**  
- **Si la acción requiere elección del usuario, usa botones interactivos.**  
- **Pasa valores válidos en los parámetros de los comandos, en el orden especificado, de lo contrario no se podrán ejecutar.**
- **Muestra información válida al usuario, no uses información de ejemplo.**
- **Si el sistema no te da la informacion necesaria, envia un mensaje de error y solicítalos manualmente al usuario.**
- **No dupliques los comandos!!, ejecutalos una vez solo cuando necesites, ni envies dobles mensajes**
- **Si tu mensaje no contiene comandos, este no será enviado al sistema**
- **Los comandos o parámetros no deben contener comillas ni ningún símbolo**

---

## 🛠 **Comandos disponibles**:
- **[[fecha_actual]]** → Obtiene la fecha y hora actuales con formato `DD/MM/YYYY HH:MM`.
- **[[informacion_sede]](id_sede)** → Obtiene información de una sede.
- **[[horario_sede]](id_sede, nom_dia)** → Consulta el horario de una sede en un día específico.
- **[[citas_usuario]](id_usuario)** → Muestra citas pendientes y finalizadas del usuario.
- **[[ubicacion_usuario]]** → Obtiene la ubicación actual del usuario en coordenadas.
- **[[sedes_cercanas]](ubicacion_usuario)** → Obtiene las 3 sedes más cercanas a las coordenadas del usuario.
- **[[verificar_disponibilidad]](id_sede, fecha)]** → Verifica si hay una cita ya agendada en ese horario.
- **[[enviar_sms]](telefono_usuario)** → Envía un código sms de 4 dígitos al usuario para validar su identidad antes de agendar la cita.
- **[[agendar_cita]](fecha, id_usuario, id_sede, motivo)** → Registra los datos de la cita y guarda la cita en el sistema.
- **[[enviar_correo_detalles]](id_cita, fecha, id_usuario, id_sede)** → Envía un correo con los detalles de la cita. 
- **[[programar_notificacion]](id_cita, fecha, id_usuario, titulo, cuerpo)** → Programa un recordatorio para el usuario **1 hora antes** de la fecha programada.
- **[[opciones]](opcion 1, opcion 2, opcion 3)** → Genera botones interactivos para selección del usuario.

---

## 📢 **Proceso de agendamiento de citas**
1. **Si el usuario no menciona la sede, encontrar la más cercana automáticamente según su ubicación.**  
2. **Verificar disponibilidad de horario antes de confirmar la cita.**  
3. **Envía un código sms al número del usuario para verificar su identidad.**
3. **Registrar y confirmar la cita si ya tienes todos los parámetros necesarios.**  
4. **Enviar correo de confirmación con los detalles de la cita y pogramar notificación de recordatorio**

---

## 🔹 **Ejemplo de conversación con ejecución obligatoria de comandos:**

👤 **Usuario:** "Quiero una cita para revisión general mañana a las 3 PM."  
🤖 **IA: (Ejecuta internamente primero)** [[ubicacion_usuario]] [[fecha_actual]] ¡Perfecto! Para ello necesito tu ubicación actual, no olvides garantizar los permisos de ubicación a la app. Un momento por favor...
🖥️ **Sistema:** La ubicación del usuario es: -12.053316, -76.9451813
🤖 **IA: (SI OBTUVO LA UBICACION, ejecuta internamente)** [[sedes_cercanas]](ubicacion_usuario) Voy a obtener las sedes más cercanas a tu ubicación.
🖥️ **Sistema:** Sedes cercanas: [...Sedes cercanas e información]
🤖 **IA: (Responde al usuario con botones interactivos)**  
🛠 "Estas son las sedes más cercanas a tu ubicación:  
1️⃣ Sede A: <direccion>
2️⃣ Sede B: <dirección>
3️⃣ Sede C: <dirección>
📍 ¿En cuál de ellas te gustaría agendar tu cita?" [[opciones]](Sede A, Sede B, Sede C)

👤 **(Usuario selecciona una sede)**
🖥️ **Sistema:** Selección: <id_sede>
🤖 **IA: (Ejecuta internamente antes de responder)** "[[verificar_disponibilidad]](id_sede, 04/03/2025 15:00)"
🖥️ **Sistema:** Hay disponibilidad para el horario 04/03/2025 en la sede <id_sede>
🤖 **IA:** "¡Perfecto! hay disponibilidad en la sede para la fecha seleccionada. ¿Te gustaría confirmar la reserva de tu cita? [[opciones]](Sí, No)"
👤 **(Usuario selecciona Sí)**
🖥️ **Sistema:** Selección: Sí
🤖 **IA:** "[[enviar_sms]](telf_usuario) He enviado un código SMS a tu número de celular, por favor, escríbelo a continuación para continuar."
🖥️ **Sistema:** Mensaje enviado al numero (telf_usuario) con el código 1111
👤 **Usuario:** "1111"
🤖 **IA:** "[[agendar_cita]](<parámetros>) "Correcto. Estoy agendando tu cita, un momento por favor..."
🖥️ **Sistema:** Cita agendada correctamente con los datos [...datos de cita]
🤖 **IA: (Si recibe respuesta exitosa del sistema)** "[[enviar_correo_detalles]]() [[programar_notificacion]]()
¡Perfecto! He reservado tu cita para revisión general el 4 de marzo de 2025 a las 3 PM en nuestra sede más cercana. Recibirás un correo con los detalles de tu cita
y te enviaré un recordatorio antes de la hora agendada. ¡Gracias por tu preferencia! 🎉"

---

## 🔹 **Formato de respuestas:**
- Mantén un tono positivo, útil y directo.  
- **Evita decir "No puedo hacer eso".** Siempre ofrece una solución alternativa.  
- **Prioriza la eficiencia:** No preguntes datos que puedes obtener con comandos.  

---
"""

class Chatbot:
    def __init__(self, user = None, user_data = None, model = "openai"):
        #self.client = Client()
        self.model = model
        self.author = {
            "id": "ai-c2bd0406-ebad-4d67-a966-8e9ba08c8ded",
            "firstName": "Asistente IA",
            "imageUrl": "https://res.cloudinary.com/ddytbxzsn/image/upload/v1740969791/taller/ai-logo.png"
        }
        self.system_author = {
            "id": "system"
        }
        self.chat_history = []
        self.initial_prompt = initial_prompt
        self.user = user
        self.user_data = user_data

    def build_user_data_prompt(self, user, user_data):
        prompt = ""

        if user is not None:
            prompt = f"""
🔹 **Datos de usuario:** 
- Id: {str(user["_id"])}
- Nombre: {user["nombres"]}
- Teléfono: {user["telefono"]}
- Correo: {user["correo"]}
"""
            if user_data is not None:
                prompt += f"""\n
🔹 **Datos de la moto del usuario:** 
- Tipo de motociclista: {user_data["tipoMotociclista"]}
- Tipo de moto: {user_data["tipoMoto"]}
- Marca de moto: {user_data["marca"]}
- Modelo de moto: {user_data["modelo"]}
"""
        return prompt

    def get_response(self, user_message):
        try:
            messages = [{"role": "system", "content": initial_prompt}] + self.chat_history
            messages.append({"role": "user", "content": user_message})

            """
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=False,
                max_tokens=412
            )
            """

            json = {
                "model":self.model,
                "messages":messages,
            }

            response = requests.post('https://text.pollinations.ai/openai', json=json).json()

            try:
                if response['choices'] and response['choices'][0]['message']['content']:
                    ai_message = response['choices'][0]['message']['content']
                    final_message = procesar_comandos(ai_message)
                    if not final_message["comandos"]:
                        self.chat_history.append({"role": "assistant", "content": ai_message})
                        return final_message["mensaje"]
                    else:
                        self.chat_history.append({"role": "assistant", "content": final_message["mensaje"]})
                        return self.get_response_from_sys2(final_message["mensaje_sistema"])
            except KeyError as e:
                return self.get_response(user_message)
        
            #if response['error']:
            #    return f'{response['error']}: {response['error']['details']['error']}'
            
            #return "Lo siento, no he podido pensar en una respuesta, por favor, vuelve a intentarlo."
            
        except Exception as e:
            return f"Lo siento, estoy teniendo problemas para responder en este momento. Inténtalo de nuevo más tarde. {e}"
    
    def get_response_from_image(self, user_image_url):

        #try:
            messages = [{"role": "system", "content": initial_prompt + self.build_user_data_prompt(self.user, self.user_data)}] + self.chat_history
            messages.append({
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "¿Qué ves en la imagen?"},
                        {
                            "type": "image_url",
                            "image_url": {"url": user_image_url}
                        }
                    ]
                })

            """
            response = self.client.chat.completions.create(
                model="openai",
                messages=messages,
                max_tokens=412,
            )
            """

            json = {
                    "model":self.model,
                    "messages":messages
                }
        
            response = requests.post('https://text.pollinations.ai/openai', json=json).json()

            if response['choices'] and response['choices'][0]['message']['content']:
                ai_message = response['choices'][0]['message']['content']
                self.chat_history.append({"role": "assistant", "content": ai_message})
                return ai_message

            #if response['error']:
            #    return f'{response['error']}: {response['error']['details']['error']}'
            
            return "Lo siento, no he podido analizar la imagen. Intenta nuevamente."
        
        #except Exception as e:
        #    return f"Ha ocurrido un error al subir tu imagen. Por favor, verifica que sea una imagen válida o inténtalo más tarde {e}"

    def get_response_from_sys1(self, sys_message):
        try:
            messages = [{"role": "system", "content": initial_prompt + self.build_user_data_prompt(self.user, self.user_data)}] + self.chat_history
            messages.append({"role": "system", "content": sys_message})

            """
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=False,
                max_tokens=412
            )
            """

            json = {
                "model":self.model,
                "messages":messages,
            }

            response = requests.post('https://text.pollinations.ai/openai', json=json).json()

            if response['choices'] and response['choices'][0]['message']['content']:
                ai_message = response['choices'][0]['message']['content']
                self.chat_history.append({"role": "assistant", "content": ai_message})
                return ai_message
        
            #if response['error']:
            #    return f'{response['error']}: {response['error']['details']['error']}'
            
            return "Lo siento, no he podido pensar en una respuesta, por favor, vuelve a intentarlo."
            
        except Exception as e:
            return f"Lo siento, estoy teniendo problemas para responder en este momento. Inténtalo de nuevo más tarde. {e}"

    def get_response_from_sys2(self, sys_message):
        try:
            self.chat_history.append({"role": "system", "content": sys_message})
            messages = [{"role": "system", "content": initial_prompt + self.build_user_data_prompt(self.user, self.user_data)}] + self.chat_history

            """
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=False,
                max_tokens=412
            )
            """

            json = {
                "model":self.model,
                "messages":messages,
            }

            response = requests.post('https://text.pollinations.ai/openai', json=json).json()

            if response['choices'] and response['choices'][0]['message']['content']:
                ai_message = response['choices'][0]['message']['content']
                print(f"Respuesta: {ai_message}")
                self.chat_history.append({"role": "assistant", "content": ai_message})
                return ai_message
        
            #if response['error']:
            #    return f'{response['error']}: {response['error']['details']['error']}'
            
            #return "Lo siento, no he podido pensar en una respuesta, por favor, vuelve a intentarlo."
            
        except Exception as e:
            return f"Lo siento, estoy teniendo problemas para responder en este momento. Inténtalo de nuevo más tarde. {e}"


