import os
import json
import time
import google.generativeai as genai
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

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
with open(
    os.path.join(os.path.dirname(__file__), "data", "dsa_questions.json"), "r"
) as f:
    DSA_CONCEPTS = json.load(f)


class DSAAssistant:
    def __init__(self):
        self.model = genai.GenerativeModel("gemini-pro")
        self.history_collection = db.collection("qa_history")
        self.max_retries = 3
        self.retry_delay = 5  # seconds

    def find_relevant_concept(self, question):
        """Find relevant DSA concept from our database"""
        question_lower = question.lower()

        # Check for direct topic matches
        for topic, content in DSA_CONCEPTS.items():
            if isinstance(content, dict) and "description" in content:
                if any(word in question_lower for word in topic.lower().split()):
                    return content
            elif isinstance(content, list) and len(content) > 0:
                # Handle array of questions
                for q in content:
                    if isinstance(q, dict) and "question" in q:
                        if any(
                            word in question_lower
                            for word in q["question"].lower().split()
                        ):
                            return q
        return None

    def enhance_question(self, question):
        """Enhance the question with context and structure"""
        concept = self.find_relevant_concept(question)

        enhanced_prompt = f"""
        You are a DSA Expert providing clear, comprehensive answers about Data Structures and Algorithms.
        
        Question: {question}
        
        Please provide a well-structured answer that includes all of the following sections:

        1. 📚 Basic Definition and Intuitive Explanation:
           - Simple, clear definition
           - Real-world analogy or example
           - Core concept intuition
        
        2. 🔑 Key Concepts and Working:
           - Main principles
           - How it works step by step
           - Important properties or characteristics
        
        3. ⚡ Complexity Analysis:
           - Time complexity (best, average, worst cases)
           - Space complexity
           - Why these complexities occur
        
        4. 💡 Common Use Cases:
           - Practical applications
           - When to use this concept
           - Real-world examples
        
        5. 📝 Implementation Example:
           - Clean, readable code example in Python
           - Key implementation details
           - Common variations
        
        6. ⚠️ Common Pitfalls and Tips:
           - Common mistakes to avoid
           - Best practices
           - Optimization techniques
        
        7. 🔍 Related Concepts:
           - Related DS/Algo concepts
           - Comparisons with alternatives
           - When to use one over another
        
        {f"Additional context from our curriculum: {concept['explanation'] if 'explanation' in concept else concept.get('description', '')}" if concept else ""}
        
        Format the response in a clear, structured manner using markdown.
        """
        return enhanced_prompt

    def format_error_response(self, error):
        """Format error messages in a user-friendly way"""
        if "429" in str(error):  # Rate limit error
            return (
                "I'm experiencing high traffic at the moment. Please try again in a few minutes. "
                "In the meantime, you can explore our structured DSA content in the Practice DSA section."
            )
        elif "quota" in str(error).lower():
            return (
                "We've reached our API limit for the moment. Please try again later. "
                "You can also check out our pre-loaded DSA questions and tutorials in the Practice section."
            )
        else:
            return (
                "I'm having trouble processing your question right now. "
                "Please try rephrasing it or check our practice materials for similar topics."
            )

    def generate_dsa_response(self, question):
        """Generate a comprehensive DSA response with retries and error handling"""
        enhanced_question = self.enhance_question(question)

        for attempt in range(self.max_retries):
            try:
                generation_config = {
                    "temperature": 0.7,
                    "top_p": 0.8,
                    "top_k": 40,
                    "max_output_tokens": 2048,
                }

                safety_settings = [
                    {
                        "category": "HARM_CATEGORY_HARASSMENT",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
                    },
                    {
                        "category": "HARM_CATEGORY_HATE_SPEECH",
                        "threshold": "BLOCK_MEDIUM_AND_ABOVE",
                    },
                ]

                response = self.model.generate_content(
                    enhanced_question,
                    generation_config=generation_config,
                    safety_settings=safety_settings,
                )

                if response.text:
                    # Store successful Q&A in Firebase
                    self.history_collection.add(
                        {
                            "question": question,
                            "enhanced_question": enhanced_question,
                            "answer": response.text,
                            "timestamp": datetime.now(),
                            "attempts": attempt + 1,
                        }
                    )
                    return response.text

            except Exception as e:
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (attempt + 1))  # Exponential backoff
                    continue
                return self.format_error_response(e)

        return self.format_error_response("Maximum retries exceeded")

    def get_qa_history(self):
        """Get recent Q&A history"""
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
        except Exception:
            # Log error if needed, but return empty list for user-facing error handling
            return []


# Example usage:
if __name__ == "__main__":
    dsa_assistant = DSAAssistant()

    # Example question
    question = "Explain the time complexity of quicksort algorithm"
    response = dsa_assistant.generate_dsa_response(question)
    print(f"Q: {question}\nA: {response}")
