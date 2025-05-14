import streamlit as st
# from auth.firebase_auth import FirebaseAuthHandler # No longer directly needed here
from main import (
    quiz_interface,
    show_progress,
    show_scheduler,
    ask_dsa_questions,
    view_history,
    auth_ui as main_auth_sidebar_component, # Import the enhanced auth_ui
)
import json

# Page config
st.set_page_config(page_title="DSA Study Bot", page_icon="🤖", layout="wide")


def main():
    main_auth_sidebar_component()  # Call the unified auth UI component from main.py

    # Access logged_in state from auth_state managed by main.py
    if st.session_state.get("auth_state", {}).get("logged_in"):
        # Main content
        st.title("🤖 DSA Study Bot")

        # Navigation
        page = st.sidebar.selectbox(
            "Navigation",
            [
                "Practice DSA",
                "Progress Tracker",
                "Study Schedule",
                "Ask Questions",
                "History",
            ],
        )

        if page == "Practice DSA":
            st.header("Practice DSA")
            try:
                with open("data/dsa_questions.json", "r") as f:
                    questions = json.load(f)
                topic = st.selectbox("Select Topic", list(questions.keys()))
                if topic:
                    quiz_interface(topic, questions[topic])
            except FileNotFoundError:
                st.error("Questions database not found!")

        elif page == "Progress Tracker":
            show_progress()

        elif page == "Study Schedule":
            show_scheduler()

        elif page == "Ask Questions":
            ask_dsa_questions()

        elif page == "History":
            view_history()
    else:
        st.title("🤖 Welcome to DSA Study Bot")
        st.info("Please use the sidebar to Login or Sign Up to access the features.")


if __name__ == "__main__":
    main()
