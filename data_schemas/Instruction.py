class Instruction:
  def __init__(self, drone, move_num) -> None:
    self.drone = drone
    self.move_num = move_num
    self.status = "not_exected" # not_executed | executing | executed