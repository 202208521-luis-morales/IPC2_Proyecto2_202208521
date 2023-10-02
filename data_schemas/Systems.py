from data_schemas.LinkedList import LinkedList

class Systems:
  def __init__(self, name) -> None:
    self.name = name
    self.drones_systems = LinkedList()

  def add_drones_systems(self, drones_systems):
    self.drones_systems.append(drones_systems)