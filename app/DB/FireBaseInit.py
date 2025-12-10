from google.cloud import firestore
from pathlib import Path

json_path = Path("/etc/secrets/mymoneytracking.json")

# json_path = Path(__file__).resolve().parent.parent.parent / "mymoneytracking.json"


print("Firebase JSON Path:", json_path)
firebase_db = firestore.Client.from_service_account_json(json_path)
print("Firebase Firestore client initialized.")