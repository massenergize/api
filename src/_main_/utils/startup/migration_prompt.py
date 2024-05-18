import os, sys, json
from pathlib import Path


def ask_user_to_proceed():
    current_run_file_path = Path('.') / '.massenergize'/ 'current_run_info.json'
    current_run_info = {}
    if current_run_file_path.exists():
        current_run_info = load_json(current_run_file_path)
    else:
        print("Could not tell which environment you want to target.")
        os.exit(1)

    while True:
        user_input = input(f"\033[91mDo you want to proceed running Django migration for {current_run_info.get('django_env')} environment? (yes/no): \033[0m").strip().lower()
        if user_input in ['yes', 'no', 'y', 'n', '']:
            return user_input in ['yes', 'y']
        else:
            print("Please enter 'yes' or 'no'.")

def load_json(path):
    """
    Loads the json file in the given path.

    Precondition:
    path: is a string of a valid json path.
    """
    with open(path) as file:
        return json.load(file)
    return {}

def main():
    if ask_user_to_proceed():
        print("Alright, migration ready to commence...")
    else:
        print("Database migration aborted.")
        sys.exit(1)


if __name__ == "__main__":
    main()
