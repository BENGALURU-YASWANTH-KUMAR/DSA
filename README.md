# 📚 DSA StudyBot + Smart Tracker

A smart learning assistant that helps students master Data Structures and Algorithms (DSA) through interactive quizzes, progress tracking, smart scheduling, and an AI-powered doubt-solving chatbot.

## 🌟 Features

### 1. User Authentication System
- Secure signup and login functionality
- Email-based account management
- Password hashing for security

### 2. Interactive DSA Quizzes
- Topic-wise quizzes
- Randomized questions
- Helpful hints and detailed explanations
- Immediate feedback on answers
- Progress tracking for each topic

### 3. Progress Tracking 📈
- Visual representation of learning progress
- Topic-wise progress charts
- Daily tracking system
- Historical performance data

### 4. Smart Study Scheduler 📅
- Create and manage study tasks
- Date and time-based scheduling
- Email reminders for scheduled tasks
- Easy task management (add/delete)

### 5. AI-Powered DSA Chatbot 🤖
- Get instant explanations for DSA concepts
- Built-in knowledge base for common DSA topics
- Code examples and implementations
- Time and space complexity analysis
- Best practices and common pitfalls

## 🛠️ Technical Stack

- **Language:** Python 3.x
- **Framework:** Streamlit
- **Libraries:**
  - `streamlit` - Web interface
  - `matplotlib` - Progress visualization
  - `json` - Data storage
  - `hashlib` - Password encryption
  - `smtplib` - Email notifications
  - `datetime` - Schedule management

## 📂 Project Structure

```
DSA-StudyBot/
├── main.py              # Main application file
├── requirements.txt     # Project dependencies
├── auth/               # Authentication data
│   └── users.json
├── data/               # Quiz questions and study material
│   └── dsa_questions.json
├── progress/           # User progress data
│   └── user_progress.json
└── schedules/          # Study schedules
    └── user_schedule.json
```

## 🚀 Getting Started

1. **Setup Environment:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application:**
   ```bash
   streamlit run main.py
   ```

3. **Create an Account:**
   - Sign up with your email
   - Login to access features

## 💡 How to Use

### 1. Taking Quizzes
- Select "Take Quiz" from the menu
- Choose a DSA topic
- Answer questions and get instant feedback
- View explanations and hints

### 2. Track Your Progress
- Visit "Track Progress" section
- View topic-wise progress charts
- Monitor daily improvements
- Analyze learning patterns

### 3. Schedule Study Sessions
- Go to "Smart Study Scheduler"
- Add new study tasks with date and time
- Get email reminders
- Manage your study calendar

### 4. Use the DSA Chatbot
- Select "Ask DSA Doubt"
- Type your DSA-related question
- Get detailed explanations with:
  - Code examples
  - Time/space complexity analysis
  - Common pitfalls
  - Best practices

## 📊 Features in Detail

### Quiz System
- Multiple choice questions
- Hint system for difficult questions
- Detailed explanations for each answer
- Progress saving after each quiz

### Progress Tracking
- Daily progress monitoring
- Topic-wise success rate
- Visual progress charts
- Performance analytics

### Smart Scheduler
- Email reminders for study sessions
- Flexible scheduling system
- Task priority management
- Easy task modification

### DSA Chatbot
Supports explanations for topics like:
- Dynamic Programming
- Memoization
- Other DSA concepts
- Includes practical examples and implementations

## 🔒 Security Features

- Secure password hashing
- Protected user data
- Email verification system
- Session management

## 📧 Email Notifications

The system sends email alerts for:
- Study session reminders
- New task confirmations
- Important updates
- Schedule changes

## 🤝 Contributing

Feel free to contribute to this project by:
1. Forking the repository
2. Creating your feature branch
3. Committing your changes
4. Opening a pull request

## 📝 License

This project is open source and available under the MIT License.

## 📞 Support

For any questions or support, please contact the development team or open an issue in the repository.

---
Created with ❤️ for DSA learners
