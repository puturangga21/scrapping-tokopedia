from pymongo import MongoClient
import datetime

MONGO_URI = 'mongodb+srv://puturangga21:abcd@cluster.67v0swb.mongodb.net/'
DATABASE_NAME = 'test_db'
COLLECTION_NAME = 'test_collection'

try:
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]
    print("Berhasil terkoneksi ke MongoDB.")

    test_document = {
        "message": "Hello from Python!",
        "timestamp": datetime.datetime.now()
    }

    result = collection.insert_one(test_document)
    print(f"Dokumen berhasil disisipkan dengan ID: {result.inserted_id}")

except Exception as e:
    print(f"Gagal terkoneksi atau menyisipkan dokumen: {e}")
finally:
    if 'client' in locals() and client:
        client.close() # Penting untuk menutup koneksi