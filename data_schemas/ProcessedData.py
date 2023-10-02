from data_schemas.LinkedList import LinkedList

class ProcessedData:
  def __init__(self, message_name) -> None:
    self.message_name = message_name
    self.final_message = ""
    self.rows = LinkedList()

  def add_row(self, row):
    self.rows.append(row)