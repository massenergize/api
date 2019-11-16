from _main_.utils.massenergize_errors import CustomMassenergizeError
from _main_.utils.common import parse_bool, parse_date, parse_list, parse_int, parse_string, parse_location

class Validator:

  def __init__(self):
    self.fields = {}
    self.rename_fields = set()


  def expect(self, field_name, field_type=str, is_required=True):
    self.fields[field_name] = {
      "type": field_type,
      "is_required": is_required
    }
    return self

  def expect_all(self, lst):
    for (field_name, field_type, is_required) in lst:
      self.fields[field_name] = {
        "type": field_type,
        "is_required": is_required
      }
    return self

  def rename(self, old_name, new_name):
    self.rename_fields.add((old_name, new_name))
    return self


  def _common_name(self, s):
    return (' '.join(s.split('_'))).title()

  def verify(self, args):
    try:
      #first rename all fields that need renaming
      for (old_name, new_name) in self.rename_fields:
        val = self.fields.pop(old_name, None)
        if val:
          self.fields[new_name] = val

      # cleanup and verify all contents of the args and return it
      for field_name, field_info in self.fields.items():
        field_type = field_info["type"]
        field_is_required = field_info["is_required"]

        if field_is_required and field_name not in args:
          return None, CustomMassenergizeError(f"You are Missing a Required Input: {self._common_name(field_name)}")
        
        if field_name in args:
          if field_type == str:
            args[field_name] = parse_string(args[field_name])
          elif field_type == int:
            args[field_name] = parse_int(args[field_name])
          elif field_type == bool:
            args[field_name] = parse_bool(args[field_name])
          elif field_type == list:
            args[field_name] = parse_list(args[field_name])
          elif field_type == 'date':
            args[field_name] = parse_date(args[field_name])
        else:
          if field_type == 'location':
            args[field_name] = parse_location(args)

      return args, None
      
    except Exception as e:
      print(e)
      return None, CustomMassenergizeError(e)
