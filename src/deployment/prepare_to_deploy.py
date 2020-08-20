from _main_ import settings
import sys, os
from termcolor import colored
import json

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))
CONFIG_PATH = os.path.join(__location__, '../_main_/config/build/deployConfig.json') 
DEPLOY_NOTES = os.path.join(__location__, '../_main_/config/build/deployNotes.txt') 
BUILD_VERSION_PATH = os.path.join(__location__, 'build.json') 

def run():
  args = sys.argv
  deploy_to_prod = False
  deploy_to_dev = True
  is_local = False
  is_deploy = True
  target = 'dev'

  if len(args) > 1:
    deploy_to_prod = "prod" in args[1].lower()
    deploy_to_dev = not deploy_to_prod
    target = "prod" if deploy_to_prod else "dev"

    
  if len(args) > 2:
    is_local = args[2] in ['1', 'true', 'True']
  else:
    is_local = False

  if len(args) > 3:
    is_deploy = args[3] in ['1', 'true', 'True']
  else:
    is_deploy = False

  warning = False
  if settings.DEBUG and deploy_to_prod:
    print(colored("!!! Please set DEBUG=False in _main_/settings.py", 'red'))
    warning = False

  if deploy_to_dev and settings.IS_PROD: 
    return "!!! Please set IS_PROD=False in _main_/settings.py if you want to deploy to DEV", False
  
  elif deploy_to_prod and not settings.IS_PROD:
    return "!!! Please set IS_PROD=True in _main_/settings.py if you want to deploy to PROD", False

  
  generate_config(target, is_local, is_deploy)

  return f"ALL GOOD! - Ready for Launch to {'PROD' if deploy_to_prod else 'DEV'}", True


def get_target_config(target, is_local, is_deploy):
  deploy_notes = load_text_contents(DEPLOY_NOTES)

  if is_deploy:
    print(colored("!!! Please remember to updates deploy notes in _main_/config/build/deployNotes.txt", 'yellow'))

  if target == 'prod':
    return {
      "IS_PROD": True,
      "BUILD_VERSION": generate_new_build_number(target),
      "BUILD_VERSION_NOTES": deploy_notes
    }

  else:
    #assume dev
    return {
      "IS_PROD": False,
      "BUILD_VERSION": generate_new_build_number(target),
      "BUILD_VERSION_NOTES": deploy_notes
    }


def generate_new_build_number(target) -> str:
  old_build_versions = load_json_contents(BUILD_VERSION_PATH)
  build_version_for_target = old_build_versions.get(target)
  parts = [int(k) for k in build_version_for_target.split('.')]
  part1 = parts[0] if len(parts) > 0 else 0
  part2 = parts[1] if len(parts) > 1 else 0
  part3 = parts[2] if len(parts) > 2 else 0

  part3 += 1
  if part3 >=100:
    part2 += 1
    part3 = 0
    if part2 >= 100:
      part1 +=1
      part2 = 0
  
  return f'{part1}.{part2}.{part3}'


def load_json_contents(path) -> dict:
  data = {}
  with open(path) as f:
    data = json.load(f)
  
  return data


def load_text_contents(path) -> str:
  data = {}
  with open(path) as f:
    data = f.read()

  return data


def write_json_contents(path, data) -> bool:
  with open(path, 'w') as f:
    json.dump(data, f, indent=2)
  return True


def generate_config(target, is_local, is_deploy):
  new_config = get_target_config(target, is_local, is_deploy)
  success = write_json_contents(CONFIG_PATH, new_config)

  if is_deploy:
    build_versions = load_json_contents(BUILD_VERSION_PATH)
    build_versions[target] = new_config.get('BUILD_VERSION')
    write_json_contents(BUILD_VERSION_PATH, build_versions)

  if success:
    return (f'Running ON {"PROD" if new_config.get("IS_PROD") else "DEV" }, \
        Local={new_config.get("IS_LOCAL") }', True)
  return ('Updating Config Failed!', False)




if __name__ == "__main__":
  msg, success = run()
  if success:
    print(colored(msg, 'green'))
  else:
    print(colored(msg, 'red'))