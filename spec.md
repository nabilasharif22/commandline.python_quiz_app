# Python Quiz App Spec

## Behavior Description

This app is a command-line Python quiz app  command-line Python quiz app with a local login system that reads questions from a JSON file, quizzes users, tracks scores and performance statistics securely (in a non-human-readable format), allows users to provide feedback on questions to influence future quiz selections, and saves results. Its can also provide useful hints about the answers if the user wants it during the quiz.

# Login / Registration:
1. The app starts from command line, and the user is greeted 
with a welcome message. Include brief description of the app.
This where the user is prompted to either create an account or log in
using existing credentials. 

2. - If "Create a new account" is chosen:
            - field where user chooses a username
            - field where User enters a password
            - Password is securely stored (hashed)
            - if account creation is successful, say so, and then prompt
            the user to go to the log in page.
   - If "Log in" is chosen/ user is in thr log in page.
            - field where user enters username 
            - field where user enters password
            - Credentials are validated against stored data

# Quiz Startup
3. After login, the user should be prompted to:
    - First select category for questions
    - Then select number of questions. Give them options: e.g., 5, 10, 15.
    - Then select difficulty level. Give them options: easy, medium, hard, random.

# Question Selection
7. Questions should be loaded from a JSON file, filtered by difficulty.
9. Questions are weighted based on wether user "liked" or "disliked":
   - Questions previously liked are more likely to appear on the next quiz.
   - Questions disliked are less likely to appear on the next quiz.
10. A random set of questions is selected if the user has no feedback history.

# Quiz Execution
11. For each question:
   - The question is displayed
   - Input method depends on question type:
     - for multiple choice: user selects option: eg. A, B, C, D
     - for true/false: user types true/false or t/f
     - for short answers: user types answer. capitalization shouldn't matter
   After answering:
   - The app immediadely shows:
     - Correct/incorrect
     - Correct answer (if wrong)
     - Promted to give feedback.
    Click enter for next question

# Feedback

13. After each question, get feedback:
   - "Did you like this question? (y/n)"
   - Feedback is stored and question gets a score.
   - For this, discretion on a good strategy for scoring the questions
        and using the score to choose to display question.
    - Questions have a default score if its a brand new question for the user.

# Scoring
14. At the end of the quiz:
   - Total score out of total questions is displayed
   - Percentage score is calculated
   - Option to check additional stats:
     - average percentage correct per category


# Saving Results
15. User results are saved securely:
   - All scores and stats  are stored in an encoded/encrypted format and file is not human-readable
# Exit
16. After quiz user is given the option to:
   - Take another quiz
        - Quizes after the first quiz should also incorporate user feedback.
   - Exit


## File structure
│
├── main.py              # Entry point, handles flow control, error handling
├── auth.py              # Handles login and registration logic
├── quiz.py              # Handles quiz logic, scoring, feedback
├── questions.json       # Initial question bank to be modified later
├── users.dat            # Securely stores user login info
├── scores.dat           # Securely stores user score history. 
                            Tracks performance  and other useful statistics over time for user.
├── feedback.dat         # Tracks feedback for each question
├── utils.py             # Helper functions (hashing, encoding, calculate stats, display)
└── SPEC.md              # Project specification for AI

## Error handling:
Add to this as you see fit
- if the JSON file is missing
    - "No JSON files to pull questions"
- If the user enters invalid input
    - Depending on the question type, prompt user for correct input type.
- If not score history for a category to display for stats
    - "Take more quizes in this category for stats"
- If question has no feedback
    - use the default score

## Data Format
Use these until app is working as intended.
 eg. Question Bank for questions.json

```json
{
  "questions": [
    {
      "question": "What keyword is used to define a function in Python?",
      "type": "multiple_choice",
      "options": ["func", "define", "def", "function"],
      "answer": "def",
      "category": "Python Basics",
      "difficulty": "easy"
    },
    {
      "question": "A list in Python is immutable.",
      "type": "true_false",
      "answer": "false",
      "category": "Data Structures",
      "difficulty": "easy"
    },
    {
      "question": "What built-in function returns the number of items in a list?",
      "type": "short_answer",
      "answer": "len",
      "category": "Python Basics",
      "difficulty": "easy"
    },
    {
      "question": "What does OOP stand for?",
      "type": "short_answer",
      "answer": "object oriented programming",
      "category": "Concepts",
      "difficulty": "medium"
    },
    {
      "question": "Which data structure uses FIFO?",
      "type": "multiple_choice",
      "options": ["Stack", "Queue", "Tree", "Graph"],
      "answer": "Queue",
      "category": "Data Structures",
      "difficulty": "medium"
    }
  ]
}

