# Python Quiz App

Command-line quiz app with local login, secure credential storage, weighted question selection based on feedback, hints, and secure score tracking.

## Run

```bash
python3 main.py
```

## Files

- `main.py`: flow control and user interaction
- `auth.py`: registration and login
- `quiz.py`: question delivery, scoring, feedback, stats
- `utils.py`: hashing, secure file encode/decode, helpers
- `questions.json`: question bank
- `users.dat`, `scores.dat`, `feedback.dat`: secure encoded storage
