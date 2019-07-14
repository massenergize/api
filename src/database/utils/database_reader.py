"""
This is a factory dedicated to reading objects in the Massenergize Database
"""
#TODO: pre-load all models and their fields with those that are one to one and 
# those that are many to many

class DatabaseReader:
  def __init__(self, model, filter_args,required_fields=[], prefetch=False, 
    preselect=False, ):
    self.model = model
    self.args = args


