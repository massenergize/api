from os.path import dirname, abspath, join
import sys, os, semver
THIS_DIR = dirname(__file__)
CODE_DIR = abspath(join(THIS_DIR, '..'))
sys.path.append(CODE_DIR)


from _main_ import settings

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
  deploy_to_canary = False
  deploy_to_dev = True
  is_local = False
  is_deploy = True
  target = 'dev'

  if len(args) > 1:
    run_locally = "local" in args[1].lower()
    deploy_to_prod = "prod" in args[1].lower()
    deploy_to_canary = "canary" in args[1].lower()
    deploy_to_dev = (not deploy_to_prod) and (not deploy_to_canary)
    if deploy_to_prod:
      target = "prod"
    elif deploy_to_canary:
      target = "canary"
    else:
      target = "dev"

  if run_locally or len(args) > 2:
    is_local = args[2] in ['1', 'true', 'True']
  else:
    is_local = False

  if len(args) > 3:
    is_deploy = args[3] in ['1', 'true', 'True']
  else:
    is_deploy = False

  warning = False
  if settings.DEBUG and is_deploy:
    print(colored("!!! Please set DEBUG=False in _main_/settings.py", 'red'))
    warning = False

  if settings.IS_LOCAL:
    print(colored("!!!Warning: IS_LOCAL=True in _main_/settings.py", 'yellow'))
    warning = False
    if is_deploy:
      return "!!! Please set IS_LOCAL=False in _main_/settings.py if you want to deploy to DEV/PROD", False

  if deploy_to_dev and settings.IS_PROD: 
    return "!!! Please set IS_PROD=False in _main_/settings.py if you want to deploy to DEV", False
  
  elif deploy_to_prod and not settings.IS_PROD:
    return "!!! Please set IS_PROD=True in _main_/settings.py if you want to deploy to PROD", False
  
  elif deploy_to_canary and not settings.IS_CANARY:
    return "!!! Please set IS_CANARY=True in _main_/settings.py if you want to deploy to CANARY", False

  if not is_deploy:
    return f"Ready for running API locally", True

  build_version = generate_config(target, is_local, is_deploy)
  update_aws_docker_config(target, build_version)
  
  return f"ALL GOOD! - Ready for Launch v{build_version} to {target.capitalize()}", True


def get_target_config(target, is_local, is_deploy):
  deploy_notes = load_text_contents(DEPLOY_NOTES)

  if is_deploy:
    print(colored("!!! Please remember to updates deploy notes in _main_/config/build/deployNotes.txt", 'yellow'))

  if target == 'prod':
    return {
      "IS_PROD": True,
      "IS_CANARY": False,
      "BUILD_VERSION": generate_new_build_number(target),
      "BUILD_VERSION_NOTES": deploy_notes
    }

  elif target == 'canary':
    return {
      "IS_PROD": False,
      "IS_CANARY": True,
      "BUILD_VERSION": generate_new_build_number(target),
      "BUILD_VERSION_NOTES": deploy_notes
    }

  else:
    #assume dev
    return {
      "IS_PROD": False,
      "IS_CANARY": False,
      "BUILD_VERSION": generate_new_build_number(target),
      "BUILD_VERSION_NOTES": deploy_notes
    }


def generate_new_build_number(target, is_major=False) -> str:
  old_build_versions = load_json_contents(BUILD_VERSION_PATH)
  build_version_for_target = old_build_versions.get(target)
  version =  semver.VersionInfo.parse(build_version_for_target)
  if is_major:
    version =  version.bump_major()
  else:
    version =  version.bump_minor()
  print(version)
  return str(version)

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
  with open(path, 'w+') as f:
    json.dump(data, f, indent=2)
  return True

def write_any_content(path, data):
  f = open(path, "w+")
  f.write(data)
  f.close()


def generate_config(target, is_local, is_deploy):
  new_config = get_target_config(target, is_local, is_deploy)
  success = write_json_contents(CONFIG_PATH, new_config)

  if is_deploy:
    build_versions = load_json_contents(BUILD_VERSION_PATH)
    build_versions[target] = new_config.get('BUILD_VERSION')
    write_json_contents(BUILD_VERSION_PATH, build_versions)

  if success:
    print (f'Running ON {target.capitalize()}, Local={new_config.get("IS_LOCAL") }')

  else:
    print ('Updating Config Failed!')

  return new_config.get("BUILD_VERSION")


def update_aws_docker_config(target, build_version):
  dst_docker_run_aws_file = os.path.join(__location__, '../Dockerrun.aws.json') 
  dst_secure_listener_file = os.path.join(__location__, '../.ebextensions/securelistener-clb.config') 
  dst_elastic_bean_stalk = os.path.join(__location__, '../.elasticbeanstalk/config.yml') 
  dst_docker_compose = os.path.join(__location__, '../docker-compose.yml') 

  dev_version_txt = os.path.join(__location__, '../api_version_dev.txt') 
  prod_version_txt = os.path.join(__location__, '../api_version_prod.txt') 
  canary_version_txt = os.path.join(__location__, '../api_version_canary.txt')

  if target == 'prod':
    src_docker_run_aws_file = os.path.join(__location__, '../deployment/aws/Dockerrun.prod.aws.json') 
    src_secure_listener_file = os.path.join(__location__, '../deployment/aws/prodSecureListener.config') 
    src_elastic_bean_stalk = os.path.join(__location__, '../deployment/aws/prodElasticBeanstalkConfig.yml') 
    src_docker_compose = os.path.join(__location__, '../deployment/aws/docker-compose.prod.yml') 
    write_any_content(prod_version_txt, build_version)
    

  elif target == 'canary':
    src_docker_run_aws_file = os.path.join(__location__, '../deployment/aws/Dockerrun.canary.aws.json') 
    src_secure_listener_file = os.path.join(__location__, '../deployment/aws/canarySecureListener.config') 
    src_elastic_bean_stalk = os.path.join(__location__, '../deployment/aws/canaryElasticBeanstalkConfig.yml') 
    src_docker_compose = os.path.join(__location__, '../deployment/aws/docker-compose.canary.yml') 
    write_any_content(canary_version_txt, build_version)

  else:
    # assume dev
    src_docker_run_aws_file = os.path.join(__location__, '../deployment/aws/Dockerrun.dev.aws.json') 
    src_secure_listener_file = os.path.join(__location__, '../deployment/aws/devSecureListener.config') 
    src_elastic_bean_stalk = os.path.join(__location__, '../deployment/aws/devElasticBeanstalkConfig.yml')
    src_docker_compose = os.path.join(__location__, '../deployment/aws/docker-compose.dev.yml')  
    write_any_content(dev_version_txt, build_version)

  transfer_file_contents(src_docker_run_aws_file, dst_docker_run_aws_file)
  d = load_json_contents(src_docker_run_aws_file)
  d["Image"]["Name"] = f"{d['Image']['Name']}:{build_version}"
  write_json_contents(dst_docker_run_aws_file, d)

  transfer_file_contents(src_secure_listener_file, dst_secure_listener_file)
  transfer_file_contents(src_elastic_bean_stalk, dst_elastic_bean_stalk)
  transfer_file_contents(src_docker_compose, dst_docker_compose)

def transfer_file_contents(src, dst):
  src_content = load_text_contents(src)
  write_any_content(dst, src_content)


if __name__ == "__main__":
  msg, success = run()
  if success:
    print(colored(msg, 'green'))
  else:
    print(colored(msg, 'red'))