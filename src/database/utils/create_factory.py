"""
This is a factory class dedicated to creating new instances of objects in 
the Massenergize Database
"""

CREATE_ERROR_MSG = "An error occurred during creation.  Please check your \
    information and try again"

class CreateFactory:
  def __init__(self, model, args, direct_fields=None, foreign_key_fields=None,
    many_to_many_fields=None, required_fields=[], field_arg_pairs=None):
    self.model = model
    self.args = args
    self.required_fields = required_fields
    self.field_arg_pairs = field_arg_pairs

    # self.direct_fields =  direct_fields
    # self.foreign_key_fields = foreign_key_fields
    # self.many_to_many_fields = many_to_many_fields



  def verify_required_fields(self):
    errors = []
    for f in self.required_fields:
      if f not in self.args:
        errors.append(f"You are missing a required field: {f}")
    return errors    

  def create(self):
    #if code gets here we have everything we need
    errors = self.verify_required_fields()
    if errors:
      return {"success": False, "errors":errors, "object": None}

    print(self.model._meta)
    return {"success": False, "errors": None, "object": None}
    # try:
    #   new_action = self.model.objects.create()
    #   for f in self.direct_fields:

    #     new_action.title = args["title"]
    #   new_action.save()
    #   return {"success": True, "object":new_action, "errors":None}
    # except Exception as e:
    #   return {"success": False, "errors": [CREATE_ERROR_MSG, str(e)]}
