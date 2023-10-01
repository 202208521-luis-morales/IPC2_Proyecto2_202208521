from data_schemas.LinkedList import LinkedList

class Db:
  def __init__(self) -> None:
    self.systems = LinkedList()
    self.instructions = LinkedList()