from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

username = os.getenv("MONGO_USERNAME")
password = os.getenv("MONGO_PASSWORD")

MONGO_URI = f"mongodb+srv://{username}:{password}@cluster0.7d31h.mongodb.net/test?retryWrites=true&w=majority&appName=Cluster0"

client = MongoClient(MONGO_URI)

db = client["test"]

coleccion = db["chats"]

print("Conectado a MongoDB Atlas con éxito")