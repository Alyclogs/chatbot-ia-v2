from datetime import datetime
from time import time
import uuid
from flask import Flask, request, jsonify
from chatbot import Chatbot
from flask_cors import CORS
from handler import Handler

app = Flask(__name__)
CORS(app)

chatbot = Chatbot()
handler = Handler(chatbot)

@app.route("/send-message", methods=["POST"])
def send_message():
    username = request.args.get("username")
    password = request.args.get("password")

    user = handler.get_user(username, password)
    if user is None:
        return jsonify({"error": "Credenciales incorrectas"}), 401

    data = request.get_json()
    chat_id = request.args.get("chat_id") 
    message = data.get("message")
    ia_author = chatbot.author

    chat_data = handler.load_chat_history(chat_id, str(user["_id"]))

    response = chatbot.get_response(message["text"])
    handler.save_message(chat_data, message)

    ia_message = {
        "author": ia_author,
        "createdAt": int(time() * 1000),
        "id": f"m-{str(uuid.uuid4())}",
        "text": response
    }
    handler.save_message(chat_data, ia_message)
    return jsonify({ "response": response })

@app.route("/send-image", methods=["POST"])
def send_image():
    username = request.args.get("username")
    password = request.args.get("password")

    user = handler.get_user(username, password)
    if user is None:
        return jsonify({"error": "Credenciales incorrectas"}), 401

    data = request.get_json()
    chat_id = request.args.get("chat_id") 
    message = data.get("message")
    ia_author = chatbot.author

    chat_data = handler.load_chat_history(chat_id, str(user["_id"]))

    response = chatbot.get_response_from_image(message["uri"])
    handler.save_message(chat_data, message)

    ia_message = {
        "author": ia_author,
        "createdAt": int(time() * 1000),
        "id": f"m-{str(uuid.uuid4())}",
        "text": response
    }
    handler.save_message(chat_data, ia_message)
    return jsonify({ "response": response })

@app.route("/send-sys-message", methods=["POST"])
def send_system_message():
    username = request.args.get("username")
    password = request.args.get("password")

    user = handler.get_user(username, password)
    if user is None:
        return jsonify({"error": "Credenciales incorrectas"}), 401

    data = request.get_json()
    chat_id = request.args.get("chat_id") 
    message = data.get("message")
    system_author = chatbot.system_author

    chat_data = handler.load_chat_history(chat_id, str(user["_id"]))
    response = chatbot.get_response_from_sys1(message["text"])
    handler.save_message(chat_data, message)

    system_message = {
        "author": system_author,
        "text": response
    }
    handler.save_message(chat_data, system_message)
    return jsonify({ "response": response })

@app.route("/chats", methods=["GET"])
def get_user_chats():
    username = request.args.get("username")
    password = request.args.get("password")

    user = handler.get_user(username, password)
    if user is None:
        return jsonify({"error": "Credenciales incorrectas"}), 401

    chats = handler.get_user_chats(str(user["_id"]))
    return jsonify(chats)

@app.route("/messages", methods=["GET"])
def get_messages():
    username = request.args.get("username")
    password = request.args.get("password")
    chat_id = request.args.get("chat_id")

    user = handler.get_user(username, password)
    if user is None:
        return jsonify({"error": "Credenciales incorrectas"}), 401

    chat_data = handler.load_chat_history(chat_id, str(user["_id"]))
    return jsonify(chat_data)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)