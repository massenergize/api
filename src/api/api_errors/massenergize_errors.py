class MassEnergizeAPIError(Error):
  def __init__(self, msg="UNKNOWN ERROR"):
    self.msg = ""

  def __str__(self) -> str:
    f"Error: {self.msg}"


class ResourceNotFound(MassEnergizeAPIError):
  def __init__(self):
    super().__init__("RESOURCE NOT FOUND ERROR")

  
