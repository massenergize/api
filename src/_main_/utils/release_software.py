import json
import datetime
import os,sys
import subprocess
from utils import load_json

def save_release_info(release_info, filename='release_info.json'):
    with open(filename, 'w') as file:
        json.dump(release_info, file, indent=4)

def increment_version(version, release_type):
    major, minor, patch = map(int, version.split('.'))
    
    if release_type == 'major':
        major += 1
        minor = 0
        patch = 0
    elif release_type == 'minor':
        minor += 1
        patch = 0
    elif release_type == 'patch':
        patch += 1
    else:
        sys.exit(1)
    
    return f"{major}.{minor}.{patch}"

def get_github_username():
    try:
        result = subprocess.run(
            ['git', 'config', 'user.name'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        username = result.stdout.strip()
        if username:
            return username
    except Exception as e:
        print(f"Error fetching GitHub username: {e}")
    
    return input("Enter your GitHub username: ").strip()

def main():
    release_info = load_json("release_info.json")
    
    current_version = release_info["version"]
    print(f"Current version: {current_version}")
    
    release_type = input("\033[94mEnter the release type (major, minor, patch): \033[0m").strip().lower()
    if release_type not in ['major', 'minor', 'patch']:
        print("Sorry: invalid release type: must be one of: 'major', 'minor', 'patch'")
        sys.exit(1)
        
    
    new_version = increment_version(current_version, release_type)
    print(f"New version will be: {new_version}")
    
    confirm = input("\033[91mAre you sure you want to proceed? (yes/y): \033[0m").strip().lower()
    if confirm not in ['yes', 'y']:
        print("Release aborted")
        return
    
    github_username = get_github_username()
    
    release_info["version"] = new_version
    release_info["release_date"] = datetime.date.today().isoformat()
    release_info["released_by"] = github_username
    
    save_release_info(release_info)
    
    print("release_info.json has been updated.")
    print(f"New version: {new_version}")
    print(f"Released by: {github_username}")
    print(f"Release date: {release_info['release_date']}")

    try:
        with open('version.txt', 'w') as version_file:
            version_file.write(new_version)
    except:
        print("Could not write to version.txt")

def welcome_message():
    ascii_art = """\033[92m
##########################################################################################################
#    ____  ________    _________   _____ ______  __________  __  _____  ______    _   ______  __________ #
#   / __ \/ ____/ /   / ____/   | / ___// ____/ / ____/ __ \/  |/  /  |/  /   |  / | / / __ \/ ____/ __ \#
#  / /_/ / __/ / /   / __/ / /| | \__ \/ __/   / /   / / / / /|_/ / /|_/ / /| | /  |/ / / / / __/ / /_/ /#
# / _, _/ /___/ /___/ /___/ ___ |___/ / /___  / /___/ /_/ / /  / / /  / / ___ |/ /|  / /_/ / /___/ _, _/ #
#/_/ |_/_____/_____/_____/_/  |_/____/_____/  \____/\____/_/  /_/_/  /_/_/  |_/_/ |_/_____/_____/_/ |_|  #
##########################################################################################################                     

Howdy, Namaste, Mabuhay, Welcome, Bienvenue, Akwaaba!
\033[0m"""

    warning = """\033[96m
---------------------------------------------------------------------
ABOUT TO RELEASE ?
---------------------------------------------------------------------
1. Make sure you tested
2. Make sure you have release notes
3. Have you given the right stakeholders the headsup?
4. Head to AWS and trigger a deployment in the pipeline when done.
     \033[0m"""
    
    print(ascii_art)
    print(warning)

if __name__ == "__main__":
    welcome_message()
    main()
