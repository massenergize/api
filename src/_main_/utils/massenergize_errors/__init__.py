"""
Definition of the different Massenergize Error Types
"""
from _main_.utils.massenergize_response import MassenergizeResponse

class MassEnergizeAPIError(MassenergizeResponse):
  def __init__(self, msg="UNKNOWN ERROR", status=400):
    self.msg = msg
    self.status = status
    super().__init__(error=msg, status=200)

  def __str__(self):
    return f"Error: {self.msg}, Status: {self.status}"


class ResourceNotFoundError(MassEnergizeAPIError):
  def __init__(self):
    super().__init__("RESOURCE NOT FOUND ERROR", 400)


class NotAuthorizedError(MassEnergizeAPIError):
  def __init__(self):
    super().__init__("NOT AUTHORIZED TO ACCESS THIS RESOURCE", 403)



class InvalidResourceError(MassEnergizeAPIError):
  def __init__(self):
    super().__init__("INVALID RESOURCE", 404)


class ServerError(MassEnergizeAPIError):
  def __init__(self):
    super().__init__("SERVER ERROR", 500)


class CustomMassenergizeError(MassEnergizeAPIError):
  def __init__(self, err_msg):
    super().__init__(str(err_msg), 200)
