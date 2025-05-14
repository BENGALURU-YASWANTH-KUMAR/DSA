import os
from dotenv import load_dotenv
import pyrebase
import firebase_admin
from firebase_admin import auth as admin_auth, credentials

# Load environment variables
load_dotenv()

# Firebase Configuration
config = {
    "apiKey": os.getenv("FIREBASE_API_KEY"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN"),
    "projectId": os.getenv("FIREBASE_PROJECT_ID"),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID"),
    "appId": os.getenv("FIREBASE_APP_ID"),
    "measurementId": os.getenv("FIREBASE_MEASUREMENT_ID"),
    "databaseURL": "",  # Add if using Realtime Database
    "persistence": True,  # Enable local persistence
    "serviceAccount": "auth/serviceAccountKey.json",  # Path to service account key
}

# Initialize Pyrebase
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()

# Initialize Firebase Admin SDK if not already initialized
cred = credentials.Certificate("auth/serviceAccountKey.json")
if not firebase_admin._apps:
    firebase_admin.initialize_app(
        cred, {"storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET")}
    )
