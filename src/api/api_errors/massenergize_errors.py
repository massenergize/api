class MassEnergizeAPIError(Error):
  def __init__(self, msg="UNKNOWN ERROR"):
    self.msg = ""

  def __str__(self) -> str:
    f"Error: {self.msg}"


class ResourceNotFoundError(MassEnergizeAPIError):
  def __init__(self):
    super().__init__("RESOURCE NOT FOUND ERROR")


class NotAuthorizedError(MassEnergizeAPIError):
  def __init__(self):
    super().__init__("NOT AUTHORIZED TO ACCESS THIS RESOURCE")



class InvalidResourceError(MassEnergizeAPIError):
  def __init__(self):
    super().__init__("INVALID RESOURCE")

