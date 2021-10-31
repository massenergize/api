
import requests 
import json


def send_slack_message(webhook, body):
  r = requests.post(url = webhook, data = json.dumps(body)) 
  return r

