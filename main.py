import streamlit as st
import json
import random
import smtplib
import os
import hashlib
from datetime import date, datetime, timedelta
import matplotlib.pyplot as plt
from email.message import EmailMessage

# Folder setup
os.makedirs("data", exist_ok=True)
os.makedirs("progress", exist_ok=True)
os.makedirs("schedules", exist_ok=True)
os.makedirs("auth", exist_ok=True)

USER_FILE = "auth/users.json"


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


def auth_ui():
    st.sidebar.subheader("\U0001f510 Login or Signup")
    users = load_users()
    action = st.sidebar.radio("Choose Action", ["Login", "Signup"])

    if action == "Signup":
        new_user = st.sidebar.text_input("Create Username")
        new_email = st.sidebar.text_input("Your Email")
        new_pass = st.sidebar.text_input("Create Password", type="password")
        if st.sidebar.button("Signup"):
            if new_user in users:
                st.sidebar.warning("Username already exists!")
            else:
                users[new_user] = {
                    "password": hash_password(new_pass),
                    "email": new_email,
                }
                save_users(users)
                st.sidebar.success("Signup successful! Please login.")
                st.rerun()

    elif action == "Login":
        user = st.sidebar.text_input("Username")
        passwd = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Login"):
            if user in users and users[user]["password"] == hash_password(passwd):
                st.session_state.logged_in = True
                st.session_state.username = user
                st.session_state.email = users[user]["email"]
                st.success(f"Welcome, {user}!")
                st.rerun()
            else:
                st.sidebar.error("Invalid credentials")


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
    ):
        st.session_state.quiz_index = 0
        st.session_state.quiz_topic = topic
        st.session_state.quiz_submitted = False
        st.session_state.shuffled_questions = random.sample(
            questions["questions"], len(questions["questions"])
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


def get_dsa_explanation(topic):
    """Get explanation for common DSA topics"""
    explanations = {
        "memoization": {
            "title": "Memoization in Dynamic Programming (DP)",
            "explanation": """
Memoization is an optimization technique in Dynamic Programming where we store the results of expensive function calls and return the cached result when the same inputs occur again. It's a way to make your program more efficient by trading space for time.

**Key Concepts:**
1. Cache storage of computed results
2. Top-down approach (recursive with storage)
3. Avoid redundant calculations

**Example Implementation:**
```python
def fibonacci(n, memo={}):
    # Base case
    if n in memo:
        return memo[n]
    if n <= 1:
        return n
        
    # Store result in memo before returning
    memo[n] = fibonacci(n-1, memo) + fibonacci(n-2, memo)
    return memo[n]
```

**Common Pitfalls to Avoid:**
1. Using mutable default arguments (like empty dict) in Python
2. Not clearing the memo between different problem instances
3. Using memoization when tabulation might be more appropriate

**Time and Space Complexity:**
- Time: O(n) - each subproblem solved once
- Space: O(n) - storing results in memo dictionary

**Real-world Applications:**
1. Path-finding algorithms
2. String matching (like edit distance)
3. Resource optimization problems
4. Game theory calculations
5. Dynamic programming problems in competitive programming
""",
        },
        "dynamic programming": {
            "title": "Dynamic Programming (DP)",
            "explanation": """
Dynamic Programming is a method for solving complex problems by breaking them down into simpler subproblems. It is applicable when subproblems share subsubproblems.

**Key Concepts:**
1. Optimal substructure
2. Overlapping subproblems
3. State transitions

**Two Main Approaches:**
1. Top-down (Memoization)
2. Bottom-up (Tabulation)

**Example Implementation (Fibonacci using tabulation):**
```python
def fibonacci_dp(n):
    if n <= 1:
        return n
    
    # Initialize dp table
    dp = [0] * (n + 1)
    dp[1] = 1
    
    # Fill dp table
    for i in range(2, n + 1):
        dp[i] = dp[i-1] + dp[i-2]
    
    return dp[n]
```

**Common Pitfalls:**
1. Not identifying optimal substructure
2. Missing base cases
3. Incorrect state transitions
4. Using DP when greedy would suffice

**Time and Space Analysis:**
- Usually transforms exponential to polynomial time
- Space complexity depends on state storage needed

**When to Use:**
1. Optimization problems
2. Counting problems
3. Problems with overlapping subproblems
""",
        },
    }

    # Handle variations in topic names
    topic = topic.lower().strip()
    if "memo" in topic and "dp" in topic:
        return explanations["memoization"]
    elif "dynamic" in topic or "dp" in topic:
        return explanations["dynamic programming"]
    return None


def show_chatbot():
    st.subheader("🤖 DSA Doubt-Resolving Chatbot")

    user_question = st.text_area(
        "💬 Ask your DSA doubt (e.g., What is memoization in DP?)"
    )

    if st.button("Ask Chatbot"):
        if not user_question.strip():
            st.warning("Please type a valid question.")
            return

        # Try to find a matching explanation
        explanation = get_dsa_explanation(user_question)

        if explanation:
            st.success("✅ Here's your explanation:")
            st.markdown(f"# {explanation['title']}")
            st.markdown(explanation["explanation"])
        else:
            st.info("I can help you understand these DSA topics:")
            st.markdown("""
            - Memoization in Dynamic Programming
            - Dynamic Programming (DP) concepts
            
            Please ask about one of these topics, and I'll provide a detailed explanation with examples!
            """)

    # Show sample questions
    with st.expander("🔍 Sample Questions"):
        st.markdown("""
        Try asking:
        - What is memoization in DP?
        - Explain Dynamic Programming
        - How does memoization work?
        - What are the benefits of DP?
        """)


def main():
    st.set_page_config(page_title="DSA StudyBot", page_icon="📚", layout="wide")
    st.title("📚 AI DSA StudyBot + Smart Tracker")

    # Authentication
    if "username" not in st.session_state:
        auth_ui()
        return

    # Sidebar navigation
    st.sidebar.title(f"Welcome, {st.session_state['username']}! 👋")
    page = st.sidebar.radio(
        "Navigate",
        [
            "Study Path",
            "Practice Quiz",
            "Progress Tracker",
            "Study Scheduler",
            "Ask DSA Doubt",
        ],
    )

    if page == "Study Path":
        st.header("🗺️ Your DSA Learning Journey")

        # Load study path
        with open("data/study_schedule.json", "r") as f:
            study_data = json.load(f)

        # Progress tracking
        progress = load_progress()
        today = str(date.today())
        today_progress = progress.get(today, {})

        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("📚 Learning Path")
            for week in study_data[0]["recommended_path"]:
                with st.expander(
                    f"Week {week['week']}: {week['topics'][0]['name']}",
                    expanded=week["week"] == 1,
                ):
                    for topic in week["topics"]:
                        st.markdown(f"""
                        ### {topic["name"]}
                        **Estimated Time:** {topic["estimated_hours"]} hours
                        
                        **Topics covered:**
                        {", ".join(topic["subtopics"])}
                        
                        **Learning Resources:**
                        """)
                        for resource in topic.get("resources", []):
                            st.markdown(
                                f"- 📺 [{resource['title']}]({resource['url']}) by {resource['creator']}"
                            )

        with col2:
            st.subheader("📊 Today's Progress")
            if today_progress:
                for topic, count in today_progress.items():
                    st.metric(topic, f"{count} questions completed")
            else:
                st.info("No progress recorded today. Start learning! 🚀")

            st.markdown("---")
            st.markdown("### 💡 Study Tips")
            for tip in study_data[0]["tips"]:
                st.markdown(f"- {tip}")

    elif page == "Practice Quiz":
        st.header("🎯 Practice Quiz")
        questions = load_questions()
        topic = st.selectbox("Select Topic", list(questions.keys()))
        if topic:
            quiz_interface(topic, questions[topic])

    elif page == "Progress Tracker":
        show_progress()

    elif page == "Study Scheduler":
        show_scheduler()

    else:  # Ask DSA Doubt
        show_chatbot()

    # Logout button
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()


if __name__ == "__main__":
    main()
