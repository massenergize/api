from _main_.utils.massenergize_errors import CustomMassenergizeError
from _main_.utils.common import parse_bool, parse_date, parse_list, parse_int, parse_string, parse_location

class Validator:

  def __init__(self):
    self.fields = []

  def add(self, field_name, field_type=str, is_required=True):
    self.fields.append({
      "name": field_name,
      "type": field_type,
      "is_required": is_required
    })
    return self

  def expect(self, field_name, field_type=str, is_required=True):
    self.fields.append({
      "name": field_name,
      "type": field_type,
      "is_required": is_required
    })
    return self



  def _common_name(self, s):
    return (' '.join(s.split('_'))).title()

  def verify(self, args):
    for field in self.fields:
      field_name = field["name"]
      field_type = field["type"]
      field_is_required = field["is_required"]

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
