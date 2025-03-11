from time import time
import uuid
from connection import coleccion, db
from chatbot import Chatbot
from bson import ObjectId

class Handler:
    def __init__(self, chatbot: Chatbot):
        self.chatbot = chatbot

    def load_chat_history(self, chat_id, user_id):
        chat_key = f'chat_{chat_id}_{user_id}'
        user_chat_history = coleccion.find_one({'_id': chat_key})

        if user_chat_history:
            return user_chat_history
        
        current_user = db["usuarios"].find_one({'_id': ObjectId(user_id)})
        current_user_motorcycle_data = db["datos_motos"].find_one({'idUsuario': ObjectId(user_id)})

        if current_user is not None:
            initial_system_message = self.chatbot.build_user_data_prompt(current_user, current_user_motorcycle_data)

        chat_data = {
            "_id": chat_key,
            "title": "",
            "user_id": user_id,
            "messages": [
                {
                    "author": self.chatbot.system_author,
                    "text": self.chatbot.initial_prompt + '\n' + initial_system_message
                }
                ,{
                    "author": self.chatbot.author,
                    "createdAt": int(time() * 1000),
                    "id": str(uuid.uuid4()),
                    "text": "¡Hola! soy tu asistente virtual, ¿En qué puedo ayudarte hoy?"
                }]
            }
        self.load_ai_messages(chat_data)
        return chat_data

    def get_user_chats(self, user_id):
        return list(coleccion.find({'user_id': user_id}))

    def save_message(self, chat_data, message):
        if not chat_data["title"]:
            chat_data["title"] = self.generate_chat_title(message.get("text") or f"Nuevo chat [{chat_data["_id"]}]")

        chat_data["messages"].append(message)
        self.load_ai_messages(chat_data)
        self.save_chat_history(chat_data)

    def save_chat_history(self, chat_data):
        coleccion.update_one({'_id': chat_data["_id"]}, {"$set": chat_data}, upsert=True)

    def get_user(self, correo, password):
        user = db["usuarios"].find_one({"correo": correo, "contrasena": password})
        return user

    def load_ai_messages(self, chat_data):
        self.chatbot.chat_history.clear()

        for message in chat_data["messages"]:
            role = "assistant" if message["author"]["id"] == self.chatbot.author["id"] else "system" if message["author"]["id"] == self.chatbot.system_author["id"] else "user"
            self.chatbot.chat_history.append({
                "role": role,
                "content": message.get("text") or message.get("uri")
            })

    def generate_chat_title(self, first_message_text):
        return f"{first_message_text[:30]}..."