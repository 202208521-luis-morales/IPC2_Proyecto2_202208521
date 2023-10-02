from data_schemas.LinkedList import LinkedList

class Rows:
  def __init__(self) -> None:
    self.time = None
    self.instdrones = LinkedList()

  def add_instdrones(self, instdrones):
    self.instdrones.append(instdrones)

  def set_time(self, time):
    self.time = time