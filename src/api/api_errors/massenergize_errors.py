class MassEnergizeAPIError(Error):
  def __init__(self, msg="UNKNOWN ERROR", status=400):
    self.msg = ""
    self.status = status

  def __str__(self) -> str:
    f"Error: {self.msg}"


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
    super().__init__(err_msg, 200)