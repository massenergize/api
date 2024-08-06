from _main_.utils.massenergize_errors import CustomMassenergizeError
from _main_.utils.common import parse_bool, parse_date, parse_list, parse_int, parse_string, parse_location, is_value, parse_str_list, parse_dict
from _main_.utils.massenergize_logger import log


class Validator:

  def __init__(self):
    self.fields = {}
    self.one_of = {}
    self.rename_fields = set()


  def expect(self, field_name, field_type=str, is_required=False, options={}):
    self.fields[field_name] = {
      "type": field_type,
      "is_required": is_required,
      "options": options
    }
    return self

  def expect_one_of(self, lst):
    for (field_name, field_type) in lst:
      self.fields[field_name] = {
        "type": field_type,
        "is_required": False
      }
    return self

  def add(self, field_name, field_type=str, is_required=False):
    return self.expect(field_name, field_type, is_required)

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

  def verify(self, args, strict=False):
    try:
      #first rename all fields that need renaming
      for (old_name, new_name) in self.rename_fields:
        val = args.pop(old_name, None)
        if val:
          args[new_name] = val

      # when in strict mode remove all unexpected fields
      if strict:
        tmp_args = args.copy()
        for f in args:
          if f not in self.fields:
            del tmp_args[f]
        args = tmp_args

      # cleanup and verify all contents of the args and return it
      for field_name, field_info in self.fields.items():
        field_type = field_info["type"]
        field_is_required = field_info["is_required"]

        if field_is_required and field_name not in args:
          raise Exception(f"You are Missing a Required Input: {self._common_name(field_name)}")
        
        if field_name in args:
          if field_type == str:
            val = parse_string(args[field_name])
            options = field_info.get("options", {})
            min_length = options.get("min_length", None)
            max_length = options.get("max_length", None)
            if min_length and len(val) < min_length:
              raise Exception(f"{field_name} must have at least {min_length} characters")
            if max_length and len(val) > max_length:
              raise Exception(f"{field_name} must have at most {max_length} characters")
            args[field_name] = val
            
          elif field_type == int:
            check = args.pop(field_name)
            if is_value(check):     # protect against "undefined", "NULL", "None"
              args[field_name] = parse_int(check)
          elif field_type == bool:
            args[field_name] = parse_bool(args[field_name])
          elif field_type == list:
            args[field_name] = parse_list(args[field_name])
          elif field_type == 'str_list':
            check = args.pop(field_name)
            if is_value(check):     # protect against "undefined" or "NULL"
              args[field_name] = parse_str_list(check)
          elif field_type == 'date':
            args[field_name] = parse_date(args[field_name])
          elif field_type == 'location':
            parse_location(args)
          elif field_type == 'file':
            args[field_name] = args.get(field_name, None) or None

          elif field_type == dict:
            args[field_name] = parse_dict(args[field_name])
        else:
          if field_type == 'location':
            parse_location(args)
          elif field_type == 'file':
            args[field_name] =  args.get(field_name, None) or None

      # now clear the dictionary
      self.fields = {}
      self.rename_fields = set()

      return args, None

    except Exception as e:
      # now clear the  dictionary
      self.fields = {}
      self.rename_fields = set()

      log.exception(e)
      return None, CustomMassenergizeError(e)
