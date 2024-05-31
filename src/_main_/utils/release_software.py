import json
import datetime
import os
import subprocess
from _main_.utils.utils import load_json

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
        raise ValueError("Invalid release type")
    
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
    
    release_type = input("Enter the release type (major, minor, patch): ").strip().lower()
    if release_type not in ['major', 'minor', 'patch']:
        print("Invalid release type")
        return
    
    new_version = increment_version(current_version, release_type)
    print(f"New version will be: {new_version}")
    
    confirm = input("Are you sure you want to proceed? (yes/y): ").strip().lower()
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
    print(new_version) # we use this in the `make release`` command

if __name__ == "__main__":
    main()
