"""
Definition of the different Massenergize Error Types
"""
from _main_.utils.massenergize_response import MassenergizeResponse

class MassEnergizeAPIError(MassenergizeResponse):
  def __init__(self, msg="unknown_error", status=400):
    self.msg = msg
    self.status = status
    super().__init__(error=msg, status=200)

  def __str__(self):
    return self.msg

class NotAuthorizedError(MassEnergizeAPIError):
  def __init__(self):
    super().__init__("permission_denied", 403)



class InvalidResourceError(MassEnergizeAPIError):
  def __init__(self):
    super().__init__("invalid_resource", 404)


class ServerError(MassEnergizeAPIError):
  def __init__(self):
    super().__init__("server_error", 500)


class CustomMassenergizeError(MassEnergizeAPIError):
  def __init__(self, err_msg):
    super().__init__(str(err_msg), 200)
