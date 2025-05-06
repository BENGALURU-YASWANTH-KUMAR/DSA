# 🎓 DSA StudyBot - Your Interactive DSA Learning Assistant

A comprehensive learning platform that helps you master Data Structures and Algorithms (DSA) through interactive features like quizzes, progress tracking, smart scheduling, and an AI-powered doubt-solving chatbot.

## 📖 Table of Contents

1. [What is DSA StudyBot?](#what-is-dsa-studybot)
2. [Features](#features)
3. [Installation Guide](#installation-guide)
4. [How to Use](#how-to-use)
5. [Project Structure](#project-structure)
6. [Topics Covered](#topics-covered)
7. [Contributing](#contributing)

## 🤔 What is DSA StudyBot?

DSA StudyBot is your personal learning assistant that makes learning Data Structures and Algorithms fun and interactive. Whether you're preparing for coding interviews or learning DSA for academic purposes, this tool helps you:

- Take topic-wise quizzes
- Track your learning progress
- Schedule your study sessions
- Get instant help on DSA concepts

## ⭐ Features

### 1. User Account System

- **Easy Registration:** Create your account with email
- **Secure Login:** Password-protected personal space
- **Data Privacy:** Your progress is saved securely

### 2. Interactive Quiz System

- **Multiple Topics:** Arrays, Linked Lists, Trees, Graphs, and more
- **Instant Feedback:** Know immediately if your answer is correct
- **Helpful Hints:** Get hints when stuck
- **Detailed Explanations:** Learn from your mistakes

### 3. Progress Tracking System

```
📈 Your Progress
└── Daily tracking
└── Topic-wise analytics
└── Visual progress charts
└── Performance history
```

### 4. Smart Study Scheduler

- **Flexible Scheduling:** Add study tasks with date and time
- **Email Reminders:** Never miss a study session
- **Task Management:** Easy to add/modify/delete tasks

### 5. AI-Powered DSA Chatbot

- Get instant explanations for DSA concepts
- View code examples and implementations
- Understand time and space complexity
- Learn best practices and avoid common mistakes

## 🚀 Installation Guide

1. **Prerequisites:**

   ```bash
   # Make sure you have Python 3.x installed
   python --version

   # Create a virtual environment
   python -m venv venv

   # Activate virtual environment
   # On Windows:
   venv\\Scripts\\activate
   # On Unix/MacOS:
   source venv/bin/activate
   ```

2. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Start the Application:**
   ```bash
   streamlit run main.py
   ```

## 💡 How to Use

### 1. Getting Started

1. Open the application in your browser
2. Click "Signup" to create a new account
3. Log in with your credentials

### 2. Taking Quizzes

```
📚 Quiz Flow
└── Select a DSA topic
└── Answer multiple-choice questions
└── Get instant feedback
└── View explanations
└── Track your score
```

### 3. Tracking Progress

1. Navigate to "Track Progress"
2. View your performance graphs
3. Analyze topic-wise improvement
4. Check daily statistics

### 4. Study Scheduling

1. Go to "Smart Study Scheduler"
2. Add new study tasks
3. Set date and time
4. Receive email reminders

### 5. Using the DSA Chatbot

1. Click "Ask DSA Doubt"
2. Type your question
3. Get detailed explanations with:
   - Code examples
   - Complexity analysis
   - Best practices
   - Common pitfalls

## 📁 Project Structure

```
DSA-StudyBot/
├── main.py              # Main application
├── requirements.txt     # Dependencies
├── README.md           # Documentation
├── auth/               # User authentication
│   └── users.json      # User data
├── data/               # Study materials
│   ├── dsa_questions.json    # Quiz questions
│   └── study_schedule.json   # Schedule data
├── progress/           # User progress
│   └── user_progress.json    # Progress tracking
└── schedules/          # Study schedules
    └── user_schedule.json    # User schedules
```

## 📚 Topics Covered

### Data Structures

1. Arrays
2. Linked Lists
3. Stacks
4. Queues
5. Trees
6. Binary Search Trees
7. Graphs
8. Dynamic Programming

### For Each Topic We Cover

- Basic concepts
- Common operations
- Time complexity
- Space complexity
- Real-world applications
- Practice problems
- Common mistakes to avoid

## 🔧 Configuration

### Email Setup (for reminders)

1. Open main.py
2. Configure email settings:
   ```python
   email_settings = {
       "smtp_server": "smtp.gmail.com",
       "port": 465,
       "sender_email": "your-email@gmail.com"
   }
   ```

### Adding New Questions

1. Navigate to data/dsa_questions.json
2. Follow the format:
   ```json
   {
     "topic": [
       {
         "question": "Your question",
         "options": ["Option1", "Option2", "Option3", "Option4"],
         "answer": "Correct option",
         "hint": "Helpful hint",
         "explanation": "Detailed explanation"
       }
     ]
   }
   ```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

### Areas for Contribution

- Adding new DSA topics
- Improving explanations
- Adding more quiz questions
- Enhancing UI/UX
- Bug fixes and optimizations

## 📞 Support

Need help? Contact us:

- Open an issue on GitHub
- Email: support@dsastudybot.com

## 📄 License

This project is open-source under the MIT License.

---

Made with ❤️ for DSA learners
