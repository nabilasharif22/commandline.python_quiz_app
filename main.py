from getpass import getpass

from auth import AuthManager
from quiz import QuizEngine
from utils import project_path


def prompt_menu_choice(prompt: str, valid_choices: set[str]) -> str:
    while True:
        choice = input(prompt).strip()
        if choice in valid_choices:
            return choice
        print("Invalid input. Please try again.")


def authenticate_user() -> str | None:
    auth_manager = AuthManager(project_path("users.dat"))

    while True:
        print("\n1) Create a new account")
        print("2) Log in")
        print("3) Exit")
        selection = prompt_menu_choice("Select an option: ", {"1", "2", "3"})

        if selection == "1":
            username = input("Choose a username: ").strip()
            password = getpass("Choose a password: ")
            success, message = auth_manager.register_user(username, password)
            print(message)
            continue

        if selection == "2":
            username = input("Username: ").strip()
            password = getpass("Password: ")
            success, message = auth_manager.login_user(username, password)
            print(message)
            if success:
                return username
            continue

        return None


def prompt_category(engine: QuizEngine) -> str | None:
    questions = engine.load_questions()
    categories = engine.available_categories(questions)

    if not categories:
        print("No categories available.")
        return None

    print("\nAvailable categories:")
    for index, category in enumerate(categories, start=1):
        print(f"{index}) {category}")

    valid_choices = {str(index) for index in range(1, len(categories) + 1)}
    selected = prompt_menu_choice("Select category number: ", valid_choices)
    return categories[int(selected) - 1]


def prompt_question_count() -> int:
    print("\nHow many questions?")
    print("1) 5")
    print("2) 10")
    print("3) 15")
    mapping = {"1": 5, "2": 10, "3": 15}
    selected = prompt_menu_choice("Select an option: ", set(mapping.keys()))
    return mapping[selected]


def prompt_difficulty() -> str:
    print("\nSelect difficulty:")
    print("1) easy")
    print("2) medium")
    print("3) hard")
    print("4) random")
    mapping = {"1": "easy", "2": "medium", "3": "hard", "4": "random"}
    selected = prompt_menu_choice("Select an option: ", set(mapping.keys()))
    return mapping[selected]


def main() -> None:
    print("Welcome to the Python Quiz App!")
    print("Practice Python questions, track your scores, and improve over time.")

    username = authenticate_user()
    if username is None:
        print("Goodbye!")
        return

    quiz_engine = QuizEngine(username)

    while True:
        category = prompt_category(quiz_engine)
        if category is None:
            print("Goodbye!")
            return

        question_count = prompt_question_count()
        difficulty = prompt_difficulty()

        quiz_engine.run_quiz(category, question_count, difficulty)

        next_action = prompt_menu_choice("\n1) Take another quiz\n2) Exit\nSelect an option: ", {"1", "2"})
        if next_action == "2":
            print("Goodbye!")
            return


if __name__ == "__main__":
    main()
