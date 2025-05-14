import streamlit as st
import json
import random
import smtplib
import os
import hashlib
from datetime import date, datetime, timedelta
import matplotlib.pyplot as plt
from email.message import EmailMessage
from dsa_assistant import DSAAssistant
from auth.firebase_auth import FirebaseAuthHandler
import sys

# Folder setup
os.makedirs("data", exist_ok=True)
os.makedirs("progress", exist_ok=True)
os.makedirs("schedules", exist_ok=True)
os.makedirs("auth", exist_ok=True)

USER_FILE = "auth/users.json"

# Initialize the DSA Assistant
dsa_assistant = DSAAssistant()


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def load_users():
    if not os.path.exists(USER_FILE):
        return {}
    with open(USER_FILE, "r") as f:
        return json.load(f)


def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=2)


def initialize_session_state():
    """Initialize or update session state variables"""
    if "auth_state" not in st.session_state:
        st.session_state.auth_state = {
            "logged_in": False,
            "user": None,
            "loading": False,
            "error": None,
            "success": None,
        }

    # Check persisted auth state
    if not st.session_state.auth_state["logged_in"]:
        result = FirebaseAuthHandler.check_auth_state()
        if result["success"] and result.get("authenticated"):
            st.session_state.auth_state.update(
                {"logged_in": True, "user": result["user"]}
            )


def show_auth_status():
    """Display authentication status messages"""
    if st.session_state.auth_state.get("loading"):
        with st.spinner("Processing..."):
            st.empty()
    if st.session_state.auth_state.get("error"):
        st.error(st.session_state.auth_state["error"])
        st.session_state.auth_state["error"] = None
    if st.session_state.auth_state.get("success"):
        st.success(st.session_state.auth_state["success"])
        st.session_state.auth_state["success"] = None


def handle_auth_action(action, **kwargs):
    """Handle authentication actions with proper state management"""
    st.session_state.auth_state["loading"] = True
    st.session_state.auth_state["error"] = None  # Clear previous error
    st.session_state.auth_state["success"] = None # Clear previous success message

    result = {} # Initialize result to ensure it's always defined

    if action == "login":
        result = FirebaseAuthHandler.sign_in(kwargs["email"], kwargs["password"])
    elif action == "signup":
        result = FirebaseAuthHandler.sign_up(
            kwargs["username"],
            kwargs["email"],
            kwargs["password"],
            kwargs["confirm_password"],
        )
    elif action == "google":
        if "credential" in kwargs and kwargs["credential"]:
            result = FirebaseAuthHandler.sign_in_with_google(kwargs["credential"])
        else:
            result = {"success": False, "error": "Google ID Token was not provided or is empty."}
    elif action == "signout":
        result = FirebaseAuthHandler.sign_out()
    elif action == "reset_password":
        result = FirebaseAuthHandler.reset_password(kwargs["email"])
    # else: # Optional: handle unknown actions
    #     result = {"success": False, "error": f"Unknown authentication action: {action}"}


    st.session_state.auth_state["loading"] = False

    if result.get("success"):
        st.session_state.auth_state["success"] = result.get("message")
        if action in ["login", "signup", "google"] and "user" in result:
            st.session_state.auth_state.update(
                {"logged_in": True, "user": result["user"]}
            )
            current_user = result["user"]
            if action == "signup":
                signup_form_username = kwargs.get("username")
                if signup_form_username:
                    st.session_state.username = signup_form_username
                elif current_user.get("displayName"):
                    st.session_state.username = current_user.get("displayName")
                else:
                    st.session_state.username = current_user.get("email") # Fallback to email
            elif action == "login" or action == "google":
                if current_user.get("displayName"):
                    st.session_state.username = current_user.get("displayName")
                else:
                    st.session_state.username = current_user.get("email") # Fallback to email

        elif action == "signout": # Explicitly handle signout state update
            st.session_state.auth_state.update(
                {"logged_in": False, "user": None}
            )
            if "username" in st.session_state:
                del st.session_state.username
            # Clear other session state variables related to user/quiz
            keys_to_clear = ["quiz_index", "quiz_topic", "quiz_submitted", "shuffled_questions", "selected_option", "correct_count", "show_hint"]
            for key in keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]
        # For "reset_password", logged_in state doesn't change, only success/error message.
    else:
        # Ensure error is always a string, provide a default if not present in result
        st.session_state.auth_state["error"] = result.get("error", "An unexpected authentication error occurred.")

    # Always rerun to reflect changes in UI (e.g., show messages, update login status)
    st.rerun()
    # The 'return result' is effectively removed as st.rerun() stops execution.


def auth_ui():
    st.sidebar.markdown(
        """
    <style>
        .auth-container { 
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .auth-header {
            text-align: center;
            margin-bottom: 20px;
        }
        .divider {
            text-align: center;
            margin: 15px 0;
        }
        .google-btn {
            background-color: #fff;
            color: #757575;
            border: 1px solid #ddd;
            padding: 10px;
            border-radius: 5px;
            width: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-bottom: 15px;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )

    initialize_session_state()
    show_auth_status()

    with st.sidebar:
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)

        if not st.session_state.auth_state["logged_in"]:
            action = st.radio(
                "",
                ["Login", "Sign Up", "Sign in with Phone"],
                horizontal=True,
                key="auth_action",
            )

            if action == "Sign Up":
                st.markdown("### Create Account")
                username = st.text_input("Username", key="signup_username")
                email = st.text_input("Email", key="signup_email")
                password = st.text_input(
                    "Password", type="password", key="signup_password"
                )
                confirm_pass = st.text_input(
                    "Confirm Password", type="password", key="signup_confirm"
                )

                st.markdown(
                    """
                <small>Password must contain:
                - At least 8 characters
                - One uppercase letter
                - One lowercase letter
                - One number
                </small>
                """,
                    unsafe_allow_html=True,
                )

                if st.button("Create Account", use_container_width=True):
                    handle_auth_action(
                        "signup",
                        username=username,
                        email=email,
                        password=password,
                        confirm_password=confirm_pass,
                    )

            elif action == "Sign in with Phone":
                st.markdown("### Sign in with Phone Number")
                phone_number = st.text_input(
                    "Phone Number (e.g., +11234567890)", key="phone_signin_number"
                )

                if (
                    "otp_sent_to_phone" not in st.session_state
                ):  # Initialize if not present
                    st.session_state.otp_sent_to_phone = None
                if "current_phone_for_otp" not in st.session_state:
                    st.session_state.current_phone_for_otp = ""

                if st.button(
                    "Send OTP", key="phone_send_otp", use_container_width=True
                ):
                    if not phone_number:
                        st.warning("Please enter a phone number.")
                    else:
                        st.info(
                            "This is a placeholder for sending OTP. Firebase Phone Authentication typically requires client-side SDKs (like reCAPTCHA verifier) to initiate OTP sending. This button simulates the start of that process."
                        )
                        st.session_state.otp_sent_to_phone = True
                        st.session_state.current_phone_for_otp = phone_number
                        st.experimental_rerun()  # Rerun to show OTP field

                if (
                    st.session_state.otp_sent_to_phone
                    and st.session_state.current_phone_for_otp == phone_number
                ):
                    verification_code = st.text_input(
                        "Enter OTP received on "
                        + st.session_state.current_phone_for_otp,
                        key="phone_otp_code",
                    )
                    if st.button(
                        "Verify OTP & Sign In",
                        key="phone_verify_otp",
                        use_container_width=True,
                    ):
                        if not verification_code:
                            st.warning("Please enter the OTP.")
                        else:
                            result = FirebaseAuthHandler.sign_in_with_phone(
                                st.session_state.current_phone_for_otp,
                                "dummy_verification_id",  # This ID comes from the OTP sending step in a real Firebase flow
                                verification_code,
                            )
                            if result["success"]:
                                st.session_state.auth_state.update(
                                    {"logged_in": True, "user": result["user"]}
                                )
                                firebase_user_obj = result["user"]
                                if firebase_user_obj and isinstance(
                                    firebase_user_obj, dict
                                ):
                                    email_from_user = firebase_user_obj.get("email")
                                    if not email_from_user and firebase_user_obj.get(
                                        "providerData"
                                    ):
                                        for provider in firebase_user_obj.get(
                                            "providerData"
                                        ):
                                            if provider.get("email"):
                                                email_from_user = provider.get("email")
                                                break
                                    st.session_state.email = (
                                        email_from_user
                                        if email_from_user
                                        else st.session_state.current_phone_for_otp
                                    )
                                else:
                                    st.session_state.email = (
                                        st.session_state.current_phone_for_otp
                                    )
                                st.success(result["message"])
                                st.session_state.otp_sent_to_phone = None
                                st.session_state.current_phone_for_otp = ""
                                st.experimental_rerun()
                            else:
                                st.error(result["error"])
                elif (
                    st.session_state.current_phone_for_otp != phone_number
                    and st.session_state.otp_sent_to_phone
                ):
                    # Reset if phone number changed after OTP was "sent"
                    st.session_state.otp_sent_to_phone = None
                    st.session_state.current_phone_for_otp = ""

            elif action == "Login":  # Changed from else to elif
                st.markdown("### Welcome Back!")
                # Google Sign-In Section
                st.markdown("**Sign in with Google**")
                google_id_token = st.text_input("Paste Google ID Token here", key="google_id_token_input", help="For testing backend logic. Obtain this token from a client-side Google Sign-In flow.")
                
                col1_google, col2_google = st.columns([1, 4])
                with col1_google:
                    st.image(
                        "https://img.icons8.com/color/48/000000/google-logo.png",
                        width=30,
                    )
                with col2_google:
                    if st.button("Continue with Google", use_container_width=True, key="google_signin_button"):
                        if google_id_token:
                            handle_auth_action("google", credential=google_id_token)
                        else:
                            st.warning("Please paste the Google ID Token above to sign in with Google.")
                        st.info(
                            "Note: For a full user experience, a client-side Google Sign-In (e.g., JavaScript) is needed to obtain the ID token automatically. "
                            "Also, ensure `YOUR_GOOGLE_WEB_CLIENT_ID` is configured in `auth/firebase_auth.py` for the `sign_in_with_google` method to function correctly with actual tokens."
                        )

                st.markdown('<div class="divider">or</div>', unsafe_allow_html=True)

                email = st.text_input("Email", key="login_email")
                password = st.text_input(
                    "Password", type="password", key="login_password"
                )

                col1, col2 = st.columns([1, 1])
                with col1:
                    st.checkbox("Remember me")
                with col2:
                    if st.button("Forgot Password?"):
                        forgot_email = st.text_input("Enter your email")
                        if forgot_email and st.button("Send Reset Link"):
                            handle_auth_action("reset_password", email=forgot_email)

                if st.button("Sign In", use_container_width=True):
                    handle_auth_action("login", email=email, password=password)

        else:
            # User is logged in
            user = st.session_state.auth_state["user"]
            if user:
                st.markdown(f"""
                ### 👋 Welcome!
                You're signed in as **{user.get("displayName", user["email"])}**
                """)
                if st.button("Sign Out", use_container_width=True):
                    handle_auth_action("signout")

        st.markdown("</div>", unsafe_allow_html=True)


def load_questions():
    with open("data/dsa_questions.json", "r") as f:
        return json.load(f)


def get_user_progress_file():
    return f"progress/{st.session_state['username']}_progress.json"


def load_progress():
    path = get_user_progress_file()
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                content = f.read().strip()
                if not content:
                    return {}
                return json.loads(content)
        except json.JSONDecodeError:
            return {}
    return {}


def save_progress(topic, increment=1):
    today = str(date.today())
    progress = load_progress()

    if today not in progress:
        progress[today] = {}
    if topic not in progress[today]:
        progress[today][topic] = 0
    progress[today][topic] += increment

    with open(get_user_progress_file(), "w") as f:
        json.dump(progress, f, indent=2)


def get_user_schedule_file():
    return f"schedules/{st.session_state['username']}_schedule.json"


def load_schedule():
    path = get_user_schedule_file()
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}


def save_schedule(schedule):
    path = get_user_schedule_file()
    with open(path, "w") as f:
        json.dump(schedule, f, indent=2)


def send_email_alert(subject, message, to_email=None):
    try:
        from_email = "ai.smart.study.bot@gmail.com"
        password = ""
        if to_email is None:
            to_email = st.session_state.get("email")

        msg = EmailMessage()
        msg.set_content(message)
        msg["Subject"] = subject
        msg["From"] = from_email
        msg["To"] = to_email

        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(from_email, password)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        st.error(f"❌ Email alert failed: {e}")


def quiz_interface(topic, questions):
    st.subheader(f"\U0001f9e0 Quiz on {topic}")

    # Show learning resources section
    with st.expander("📚 Learning Resources", expanded=True):
        if "youtube_tutorials" in questions:
            st.markdown("### 📺 Recommended Tutorials")
            for tutorial in questions["youtube_tutorials"]:
                st.markdown(f"""
                - [{tutorial["title"]}]({tutorial["url"]})
                  - Creator: {tutorial["creator"]}
                  - Duration: {tutorial["duration"]}
                """)

        if "practice_links" in questions:
            st.markdown("### 💻 Practice Problems")
            for problem in questions["practice_links"]:
                st.markdown(f"""
                - [{problem["title"]}]({problem["url"]})
                  - Platform: {problem["platform"]}
                  - Difficulty: {problem["difficulty"]}
                """)

    if (
        "quiz_index" not in st.session_state
        or st.session_state.get("quiz_topic") != topic
        or "shuffled_questions" not in st.session_state  # Ensure initialization if missing
    ):
        st.session_state.quiz_index = 0
        st.session_state.quiz_topic = topic
        st.session_state.quiz_submitted = False
        # Assuming 'questions' param is the list of questions for the topic
        st.session_state.shuffled_questions = random.sample(
            questions, len(questions)
        )
        st.session_state.selected_option = None
        st.session_state.correct_count = 0
        st.session_state.show_hint = False

    idx = st.session_state.quiz_index
    if idx >= len(st.session_state.shuffled_questions):
        st.success("\U0001f389 Quiz completed!")
        score = st.session_state.correct_count
        total = len(st.session_state.shuffled_questions)
        st.info(f"✅ Score: {score} out of {total} ({(score / total * 100):.1f}%)")

        # Show recommended next steps based on score
        if score / total < 0.6:
            st.warning(
                "📝 Recommendation: Review the concepts and watch the tutorial videos before trying again."
            )
        elif score / total < 0.8:
            st.info(
                "👍 Good job! Practice more problems to improve your understanding."
            )
        else:
            st.success("🌟 Excellent! You're ready to tackle more advanced topics!")

        save_progress(topic, st.session_state.correct_count)
        return

    q = st.session_state.shuffled_questions[idx]

    # Show current question with progress indicator
    st.progress((idx + 1) / len(st.session_state.shuffled_questions))
    st.markdown(
        f"**Question {idx + 1} of {len(st.session_state.shuffled_questions)}:** {q['question']}"
    )

    if not st.session_state.show_hint and "hint" in q:
        if st.button("\U0001f4a1 Show Hint"):
            st.session_state.show_hint = True
            st.rerun()
    elif "hint" in q:
        st.info(f"\U0001f4a1 **Hint:** {q['hint']}")

    st.session_state.selected_option = st.radio(
        "Choose your answer:", q["options"], index=None, key=f"radio_{idx}"
    )

    col1, col2 = st.columns([1, 5])
    with col1:
        submit = st.button("Submit")

    if submit and not st.session_state.quiz_submitted:
        if st.session_state.selected_option is None:
            st.warning("Please select an option before submitting.")
        else:
            st.session_state.quiz_submitted = True
            if st.session_state.selected_option == q["answer"]:
                st.success("✅ Correct!")
                st.session_state.correct_count += 1
            else:
                st.error("❌ Incorrect.")

            # Show explanation and video solution if available
            if "explanation" in q:
                st.markdown(f"\U0001f9e0 **Explanation:** {q['explanation']}")
            if "video_solution" in q:
                st.markdown(f"📺 [Watch Video Solution]({q['video_solution']})")

    if st.session_state.quiz_submitted:
        btn_label = (
            "Submit Quiz"
            if idx == len(st.session_state.shuffled_questions) - 1
            else "Next Question"
        )
        if st.button(btn_label):
            st.session_state.quiz_index += 1
            st.session_state.quiz_submitted = False
            st.session_state.selected_option = None
            st.session_state.show_hint = False
            st.rerun()


def show_progress():
    st.subheader("\U0001f4ca Your DSA Progress")
    progress = load_progress()

    # Top level metrics
    if progress:
        col1, col2, col3 = st.columns(3)
        total_questions = sum(sum(day.values()) for day in progress.values())
        topics_covered = len(
            {topic for day in progress.values() for topic in day.keys()}
        )
        current_streak = calculate_streak(progress)

        with col1:
            st.metric("Total Questions Solved", total_questions)
        with col2:
            st.metric("Topics Covered", topics_covered)
        with col3:
            st.metric("Current Streak", f"{current_streak} days")

        # Progress visualization
        st.markdown("### 📈 Progress Over Time")
        tab1, tab2 = st.tabs(["Topic-wise Progress", "Daily Activity"])

        with tab1:
            dates = list(progress.keys())
            topics = set()
            for daily in progress.values():
                topics.update(daily.keys())

            topics = sorted(topics)
            topic_data = {t: [] for t in topics}

            for d in dates:
                for t in topics:
                    topic_data[t].append(progress[d].get(t, 0))

            fig, ax = plt.subplots(figsize=(10, 5))
            for t in topics:
                ax.plot(dates, topic_data[t], marker="o", label=t)
            ax.set_xlabel("Date")
            ax.set_ylabel("Questions Solved")
            ax.set_title("Topic-wise Progress")
            ax.legend()
            plt.xticks(rotation=45)
            st.pyplot(fig)

        with tab2:
            daily_totals = [sum(day.values()) for day in progress.values()]
            fig2, ax2 = plt.subplots(figsize=(10, 5))
            ax2.bar(dates, daily_totals)
            ax2.set_xlabel("Date")
            ax2.set_ylabel("Questions Solved")
            ax2.set_title("Daily Activity")
            plt.xticks(rotation=45)
            st.pyplot(fig2)

        # Topic breakdown
        st.markdown("### 📊 Topic Breakdown")
        topic_totals = {}
        for day in progress.values():
            for topic, count in day.items():
                topic_totals[topic] = topic_totals.get(topic, 0) + count

        fig3, ax3 = plt.subplots(figsize=(8, 8))
        ax3.pie(topic_totals.values(), labels=topic_totals.keys(), autopct="%1.1f%%")
        ax3.set_title("Distribution of Questions by Topic")
        st.pyplot(fig3)

        # Recent activity
        st.markdown("### 🎯 Recent Activity")
        recent_dates = sorted(progress.keys(), reverse=True)[:5]
        for date in recent_dates:
            with st.expander(f"Activity on {date}"):
                for topic, count in progress[date].items():
                    st.write(f"- {topic}: {count} questions completed")

        # Study recommendations
        st.markdown("### 💡 Recommendations")
        if topic_totals:
            least_practiced = min(topic_totals.items(), key=lambda x: x[1])[0]
            st.info(
                f"Focus more on **{least_practiced}** as it's your least practiced topic."
            )

            # Load recommended resources for the topic
            with open("data/dsa_questions.json", "r") as f:
                questions = json.load(f)
            if least_practiced in questions:
                st.markdown("**Recommended Resources:**")
                topic_data = questions[least_practiced]
                if "youtube_tutorials" in topic_data:
                    for tutorial in topic_data["youtube_tutorials"]:
                        st.markdown(
                            f"- 📺 [{tutorial['title']}]({tutorial['url']}) by {tutorial['creator']}"
                        )
    else:
        st.info(
            "No progress recorded yet. Start solving problems to track your progress! 🚀"
        )
        st.markdown("""
        ### 🎯 Getting Started
        1. Choose a topic from the Practice Quiz section
        2. Complete the quizzes to track your progress
        3. Follow your study schedule
        4. Use the AI chatbot for help when stuck
        """)


def calculate_streak(progress):
    """Calculate the current learning streak in days"""
    if not progress:
        return 0

    dates = sorted(progress.keys(), reverse=True)
    if not dates:
        return 0

    streak = 0
    current_date = datetime.strptime(dates[0], "%Y-%m-%d").date()

    for date_str in dates:
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
        if current_date - date == timedelta(days=streak):
            streak += 1
        else:
            break

    return streak


def show_scheduler():
    st.subheader("\U0001f4c5 Smart Study Scheduler")

    # Load recommended study path
    with open("data/study_schedule.json", "r") as f:
        study_data = json.load(f)

    # Show recommended learning path
    with st.expander("📚 Recommended Learning Path", expanded=True):
        st.write("Follow this structured path to master DSA:")
        for week in study_data[0]["recommended_path"]:
            st.markdown(f"""
            ### Week {week["week"]}
            """)
            for topic in week["topics"]:
                st.markdown(f"""
                **{topic["name"]}** (~{topic["estimated_hours"]} hours)
                - Subtopics: {", ".join(topic["subtopics"])}
                """)
                if "resources" in topic:
                    st.markdown("📺 **Recommended Videos:**")
                    for resource in topic["resources"]:
                        st.markdown(
                            f"- [{resource['title']}]({resource['url']}) by {resource['creator']}"
                        )

    # Show study tips
    with st.expander("💡 Study Tips", expanded=True):
        st.markdown("### Tips for Effective Learning")
        for tip in study_data[0]["tips"]:
            st.markdown(f"- {tip}")
        st.info(
            f"🎯 Recommended: {study_data[0]['recommended_daily_hours']} hours daily, {study_data[0]['recommended_weekly_hours']} hours weekly"
        )

    # Existing scheduler functionality
    schedule = load_schedule()
    st.markdown("---")
    st.markdown("### 📝 Schedule Your Study Sessions")

    task = st.text_input("Enter a new task")
    study_date = st.date_input("Select study date", value=date.today())
    study_time = st.time_input("Time to study")

    if st.button("Add Task"):
        task_entry = {
            "task": task,
            "date": str(study_date),
            "time": str(study_time),
            "reminded": False,
        }
        schedule.setdefault("tasks", []).append(task_entry)
        save_schedule(schedule)
        st.success(f"Task added: {task} on {study_date} at {study_time}")
        send_email_alert(
            "\U0001f4da Study Reminder Added",
            f"New task: {task} on {study_date} at {study_time}",
        )

    tasks = schedule.get("tasks", [])
    tasks.sort(key=lambda x: (x["date"], x["time"]))

    today = str(date.today())
    current_time = datetime.now().strftime("%H:%M:%S")

    if tasks:
        st.write("### \U0001f4c4 Your Scheduled Tasks")
        for i, t in enumerate(tasks):
            col1, col2 = st.columns([6, 1])
            with col1:
                st.write(f"**{t['task']}** on `{t['date']}` at `{t['time']}`")
            with col2:
                if st.button("🗑️", key=f"delete_{i}"):
                    tasks.pop(i)
                    schedule["tasks"] = tasks
                    save_schedule(schedule)
                    st.success("Task deleted.")
                    st.rerun()

            if (
                t.get("date") == today
                and not t.get("reminded", False)
                and current_time >= t["time"]
            ):
                st.info(f"⏰ Reminder: {t['task']} scheduled for {t['time']}")
                send_email_alert(
                    "📌 Study Reminder",
                    f"Reminder: {t['task']} is scheduled today at {t['time']}",
                )
                t["reminded"] = True
                save_schedule(schedule)


def load_study_schedule():
    with open("data/study_schedule.json", "r") as f:
        return json.load(f)


def ask_dsa_questions():
    st.header("Ask DSA Questions")
    st.write("Need help with DSA concepts? Ask your questions here!")

    user_question = st.text_area("Your DSA Question:")

    if st.button("Get Answer"):
        if user_question:
            with st.spinner("Generating response..."):
                response = dsa_assistant.generate_dsa_response(user_question)
                st.markdown("### Answer:")
                st.write(response)
        else:
            st.warning("Please enter a question first!")


def view_history():
    st.header("Previous Questions & Answers")
    history = dsa_assistant.get_qa_history()

    for qa in history:
        st.subheader(
            f"Question (asked on {qa['timestamp'].strftime('%Y-%m-%d %H:%M')})"
        )
        st.write(qa["question"])
        st.markdown("**Answer:**")
        st.write(qa["answer"])
        st.divider()


def display_menu():
    print("\nDSA Study Bot - Menu")
    print("1. Sign Up")
    print("2. Sign In")
    print("3. Sign Out")
    print("4. Reset Password")
    print("5. Start Study Session")
    print("6. Exit")


def handle_auth():
    while True:
        display_menu()
        choice = input("\nEnter your choice (1-6): ")

        if choice == "1":  # Sign Up
            email = input("Enter email: ")
            password = input("Enter password: ")
            result = FirebaseAuthHandler.sign_up(email, password)
            if result["success"]:
                print("Successfully signed up!")
            else:
                print(f"Error signing up: {result['error']}")

        elif choice == "2":  # Sign In
            email = input("Enter email: ")
            password = input("Enter password: ")
            result = FirebaseAuthHandler.sign_in(email, password)
            if result["success"]:
                print("Successfully signed in!")
                return True
            else:
                print(f"Error signing in: {result['error']}")

        elif choice == "3":  # Sign Out
            result = FirebaseAuthHandler.sign_out()
            if result["success"]:
                print("Successfully signed out!")
            else:
                print(f"Error signing out: {result['error']}")

        elif choice == "4":  # Reset Password
            email = input("Enter email: ")
            result = FirebaseAuthHandler.reset_password(email)
            if result["success"]:
                print("Password reset email sent!")
            else:
                print(f"Error sending reset email: {result['error']}")

        elif choice == "5":  # Start Study Session
            user = FirebaseAuthHandler.get_current_user()
            if user:
                print("Starting study session...")
                # Add your study session logic here
            else:
                print("Please sign in first!")

        elif choice == "6":  # Exit
            print("Goodbye!")
            sys.exit()

        else:
            print("Invalid choice. Please try again.")


def main():
    print("Welcome to DSA Study Bot!")
    handle_auth()


if __name__ == "__main__":
    st.set_page_config(page_title="DSA Study Bot", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")
    
    auth_ui() # Handles sidebar authentication and initializes session state

    # Access logged_in state from auth_state, which should be managed by auth_ui
    if st.session_state.get("auth_state", {}).get("logged_in"):
        # Main content area
        st.title("🤖 DSA Study Bot")

        # Navigation in the sidebar (if not already part of auth_ui or if more items are needed)
        page = st.sidebar.selectbox(
            "Navigation",
            [
                "Practice DSA",
                "Progress Tracker",
                "Study Schedule",
                "Ask Questions",
                "History",
            ],
            key="main_navigation_selectbox" # Unique key for the selectbox
        )

        if page == "Practice DSA":
            st.header("Practice DSA")
            try:
                # Ensure the path to dsa_questions.json is correct relative to main.py
                # If main.py is in DSA-StudyBot and data is a subfolder, 'data/dsa_questions.json' is correct.
                with open("data/dsa_questions.json", "r") as f:
                    questions_data = json.load(f)
                topic = st.selectbox("Select Topic", list(questions_data.keys()), key="dsa_topic_selectbox")
                if topic:
                    # Assuming quiz_interface is defined in this file (main.py)
                    quiz_interface(topic, questions_data[topic]) 
            except FileNotFoundError:
                st.error("Error: The questions database (data/dsa_questions.json) was not found. Please ensure it exists.")
            except json.JSONDecodeError:
                st.error("Error: Could not decode the questions database. Please check the format of data/dsa_questions.json.")
            except Exception as e:
                st.error(f"An unexpected error occurred while loading DSA practice questions: {e}")

        elif page == "Progress Tracker":
            # Assuming show_progress is defined in this file (main.py)
            show_progress()

        elif page == "Study Schedule":
            # Assuming show_scheduler is defined in this file (main.py)
            show_scheduler()

        elif page == "Ask Questions":
            # Assuming ask_dsa_questions is defined in this file (main.py)
            ask_dsa_questions()

        elif page == "History":
            # Assuming view_history is defined in this file (main.py)
            view_history()
    else:
        # This content is shown in the main area if the user is not logged in.
        # auth_ui handles the sidebar for login/signup.
        st.title("🤖 Welcome to DSA Study Bot")
        st.info("Please use the sidebar to Login or Sign Up to access the features.")
