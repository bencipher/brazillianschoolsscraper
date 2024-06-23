import firebase_admin
from firebase_admin import credentials, firestore


class FirebaseService:
    def __init__(self, service_account_key_path):
        self.cred = credentials.Certificate(service_account_key_path)
        self.firebase_admin_app = None
        self.firestore_db = None

    def initialize_app(self):
        if not firebase_admin._apps:
            self.firebase_admin_app = firebase_admin.initialize_app(self.cred)
        if not self.firestore_db:
            self.firestore_db = firestore.client(app=self.firebase_admin_app)

    def get_firestore_client(self):
        if not self.firestore_db:
            self.initialize_app()
        return self.firestore_db
