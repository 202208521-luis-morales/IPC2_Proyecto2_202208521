from data_schemas.LinkedList import LinkedList

class DronesSystems:
  def __init__(self, drone) -> None:
    self.drone = drone
    self.system = LinkedList()

  def add_system(self, system):
    self.system.append(system)