import time
import subprocess
import pymongo
from pymongo import MongoClient

MONGO_IMAGE = "mongo:latest"
MONGO_CONTAINER_NAME = "mongo-container"
MONGO_PORT = "27017"
MONGO_DB = "mydb"
MONGO_COLLECTION = "test_collection"

def run_mongo():
    """Avvia il container Docker di MongoDB."""
    print("[*] Starting MongoDB in Docker...")
    subprocess.run([
        "docker", "run", "-d", "--name", MONGO_CONTAINER_NAME,
        "-p", f"{MONGO_PORT}:27017", MONGO_IMAGE
    ])
    print("[✔] MongoDB started!")
    time.sleep(10)  # Attendi l'avvio di MongoDB

def create_collection():
    """Crea una raccolta di esempio nel database MongoDB."""
    print("[*] Creating collection in MongoDB...")
    try:
        # Connessione a MongoDB
        client = MongoClient(f"mongodb://localhost:{MONGO_PORT}/")
        db = client[MONGO_DB]
        collection = db[MONGO_COLLECTION]

        # Inserisci un documento di esempio
        collection.insert_one({
            "_id": "user-123",
            "username": "john_doe",
            "agents": [
                {
                    "agent_id": "agent-456",
                    "config": {
                        "model": "gemma2",
                        "memory": "chroma",
                        "features": ["retrieval", "chat"]
                    },
                    "created_at": "2025-03-12T10:00:00"
                }
            ]
        })

        print("[✔] Collection 'test_collection' created and data inserted!")
        client.close()

    except Exception as e:
        print(f"Error creating collection: {e}")

def check_mongo():
    """Verifica che il database MongoDB sia attivo e accessibile."""
    print("[*] Checking MongoDB connection...")
    try:
        client = MongoClient(f"mongodb://localhost:{MONGO_PORT}/")
        client.admin.command('ping')
        print("[✔] MongoDB is accessible!")
        client.close()

    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")

if __name__ == "__main__":
    run_mongo()
    check_mongo()
    create_collection()
    print("\n🎉 MongoDB setup completed! Now you can connect to the database.\n")
