"""
Business Logic for how communities are managed
"""
from api.api_errors.massenergize_errors import MassEnergizeAPIError

def validate(data) -> bool:
  return True 


def get(id) -> (dict, MassEnergizeAPIError):
  pass 


def create(data) -> (dict, MassEnergizeAPIError):
  #TODO: create community object
  # create pages
  # create graphs
  # send email to admin of community to welcome and set goals
  # notify super admin admin 
  pass


def update(data) -> (dict, MassEnergizeAPIError):
  pass


def delete(data) -> (dict, MassEnergizeAPIError):
  pass

