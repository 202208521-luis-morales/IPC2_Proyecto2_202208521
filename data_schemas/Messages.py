from data_schemas.LinkedList import LinkedList

class Messages:
  def __init__(self, name, drones_system: str) -> None:
    self.name = name
    self.drones_system = drones_system
    self.instructions = LinkedList()

  def add_instruction(self, instruction):
    self.instructions.append(instruction)