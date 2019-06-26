"""
This file contains utility functions that come in handy for processing and 
retrieving data
"""
import json

def json_loader(file):
  """
  Returns json data given a valid filepath.  Returns {} if error occurs
  """
  try:
    with open(file) as myfile:
      data = myfile.read()
    return json.loads(data)
  except Exception as e:
    print(e) #TODO: remove this
    return {}

