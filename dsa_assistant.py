import os
import json
import time 
import google.generativeai as genai
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
from google.api_core import retry

# Initialize Firebase
cred = credentials.Certificate(
    os.path.join(os.path.dirname(__file__), "auth", "serviceAccountKey.json")
)

# Only initialize if not already initialized
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
db = firestore.client()

# Initialize Gemini API with proper configuration
GEMINI_API_KEY = "AIzaSyDppc4tVLE5hFZjPs9Aqo9r5_904PvMasQ"
genai.configure(api_key=GEMINI_API_KEY)

# Load DSA concepts for enhancing responses
with open(os.path.join(os.path.dirname(__file__), "data", "dsa_questions.json"), "r") as f:
    DSA_CONCEPTS = json.load(f)


class DSAAssistant:
    def __init__(self):
        self.model = genai.GenerativeModel("gemini-1.5-pro-latest")
        self.history_collection = db.collection("qa_history")

    def generate_dsa_response(self, question):
        try:
            response = self.model.generate_content(question)
            answer = response.text

            # Store the Q&A in Firebase
            self.history_collection.add(
                {"question": question, "answer": answer, "timestamp": datetime.now()}
            )

            return answer
        except Exception as e:
            return f"Error generating response: {str(e)}"

    def get_qa_history(self):
        try:
            docs = (
                self.history_collection.order_by(
                    "timestamp", direction=firestore.Query.DESCENDING
                )
                .limit(10)
                .get()
            )
            return [
                {
                    "question": doc.get("question"),
                    "answer": doc.get("answer"),
                    "timestamp": doc.get("timestamp"),
                }
                for doc in docs
            ]
        except Exception as e:
            return []


# Example usage:
if __name__ == "__main__":
    dsa_assistant = DSAAssistant()

    # Example question
    question = "Explain the time complexity of quicksort algorithm"
    response = dsa_assistant.generate_dsa_response(question)
    print(f"Q: {question}\nA: {response}")
