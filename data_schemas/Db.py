from data_schemas.LinkedList import LinkedList
from data_schemas.Systems import Systems
from data_schemas.System import System
from data_schemas.DronesSystems import DronesSystems
from data_schemas.Messages import Messages
from data_schemas.Instruction import Instruction
from data_schemas.ProcessedData import ProcessedData
from data_schemas.Rows import Rows
from data_schemas.InstDrones import InstDrones

import xml.etree.ElementTree as ET

class Db:
  def __init__(self, filename) -> None:
    self.filename = filename
    self.drones = LinkedList()
    self.systems = LinkedList()
    self.messages = LinkedList()
    self.processed_data = LinkedList()

  def process_file(self):
    tree = ET.parse(self.filename)
    root = tree.getroot()

    # Guardamos los datos de listaDrones
    lista_drones = root.find("listaDrones")
    
    for dron in lista_drones.findall("dron"):
      self.drones.append(dron.text)

    # Guardamos los datos de listaSistemasDrones
    lista_systemas_drones = root.find("listaSistemasDrones")

    for sistema_drones in lista_systemas_drones.findall("sistemaDrones"):
      systems_to_save = Systems(sistema_drones.get("nombre"))

      # self.systems.append(Systems(sistema_drones.get("nombre")))

      for contenido in sistema_drones.find("contenido"):
        drones_systems_to_save = DronesSystems(contenido.find("dron").text)

        for altura in contenido.find("alturas").findall("altura"):
          drones_systems_to_save.add_system(System(altura.get("valor"), altura.text))

        systems_to_save.add_drones_systems(drones_systems_to_save)
      
      self.systems.append(systems_to_save)
    
    # Guardamos los datos de listaMensajes
    lista_mensajes = root.find("listaMensajes")
    for mensaje in lista_mensajes.findall("Mensaje"):
      message_to_save = Messages(mensaje.get("nombre"), mensaje.find("sistemaDrones"))

      for instruccion in mensaje.find("instrucciones").findall("instrucciones"):
        message_to_save.set_instruction(Instruction(instruccion.get("dron"), instruccion.text))

      self.messages.append(message_to_save)

    # Procesamos los datos
    counter = 1
    while True:
      message_elem = self.messages.get_elem_by_position(counter)

      if message_elem:
        process_data_to_save = ProcessedData(message_elem.data.name)
        drones_status = LinkedList()

        # Inicializar posiciones para cada dron
        dron_counter = 1
        while True:
          if self.drones.get_elem_by_position(dron_counter):
            drones_status(Instruction(self.drones.get_elem_by_position(dron_counter).data, 0))
          else:
            break
        
        def check_if_all_inst_are_executed():
          are_all_executed = True
          instructions_counter = 1
          while True:
            inst = message_elem.data.instructions.get_elem_by_position(instructions_counter)
            
            if inst:
              if inst.data.status != "executed":
                are_all_executed = False
                break
            else:
              break
          instructions_counter += 1
          
          return are_all_executed
      
        def get_curr_inst_by_drone(drone):
          ret_inst = None
          instructions_counter = 1
          while True:
            inst = message_elem.data.instructions.get_elem_by_position(instructions_counter)
            
            if inst:
              if inst.data.drone == drone and inst.data.status != "executed":
                ret_inst = inst.data
                break
            else:
              break
          instructions_counter += 1
          
          return ret_inst

        instructions_counter = 1
        executing_inst_setted = False

        # Seleccionar la instrucción que toca como "ejecutandose" o "executing"
        while True:
          inst = message_elem.data.instructions.get_elem_by_position(instructions_counter)
          
          if inst:
            if inst.data.status == "not_exected" and executing_inst_setted == False:
              inst.data.status = "executing"
              executing_inst_setted = True
          else:
            break
        
        time_counter = 1
        drones_status_counter = 1
        time_counter_changed = False
        row_to_save = Rows()
        while True:
          dr_sts = drones_status.get_elem_by_position(drones_status_counter)
          inst_drones_to_save = None

          if time_counter_changed:
            row_to_save = Rows()
            time_counter_changed = False
          
          if dr_sts:
            curr_inst = get_curr_inst_by_drone(dr_sts.data.drone)

            if curr_inst:
              if curr_inst.move_num > dr_sts.move_num:
                dr_sts.data.move_num += 1
                inst_drones_to_save = InstDrones(dr_sts.data.drone, "Subir")
              elif curr_inst.move_num < dr_sts.move_num:
                dr_sts.data.move_num -= 1
                inst_drones_to_save = InstDrones(dr_sts.data.drone, "Bajar")
              else:
                if curr_inst.status == "executing" and curr_inst.drone == dr_sts.data.drone:
                  inst_drones_to_save = InstDrones(dr_sts.data.drone, "Emitir Luz")
                  process_data_to_save.final_message = process_data_to_save.final_message + self.get_text_by_drones_system_drone_and_height(message_elem.data.drones_system, curr_inst.drone, curr_inst.move_num)
                else:
                  inst_drones_to_save = InstDrones(dr_sts.data.drone, "Esperar")

            row_to_save.add_instdrones(inst_drones_to_save)
          else:
            process_data_to_save.add_row(row_to_save.set_time(time_counter))
            drones_status_counter = 1
            time_counter += 1
            time_counter_changed = True

          drones_status_counter += 1
          if check_if_all_inst_are_executed():
            break

        self.processed_data.append(process_data_to_save)
      else:
        break
        
      counter += 1

  def get_text_by_drones_system_drone_and_height(self, drones_systems, drone, height):
    founded_text = None
    
    systems_counter = 1
    while True:
      if self.systems.get_elem_by_position(systems_counter):
        
        if self.systems.get_elem_by_position(systems_counter).data.name == drones_systems:

          drones_systems_counter = 1
          while True:
            if self.systems.get_elem_by_position(systems_counter).data.drones_systems.get_elem_by_position(drones_systems_counter):
              if self.systems.get_elem_by_position(systems_counter).data.drones_systems.get_elem_by_position(drones_systems_counter).data.drone == drone:
                system_counter = 1

                while True:
                  if self.systems.get_elem_by_position(systems_counter).data.drones_systems.get_elem_by_position(drones_systems_counter).data.system.get_elem_by_position(system_counter):
                    if self.systems.get_elem_by_position(systems_counter).data.drones_systems.get_elem_by_position(drones_systems_counter).data.system.get_elem_by_position(system_counter).data.height == height:
                      founded_text = self.systems.get_elem_by_position(systems_counter).data.drones_systems.get_elem_by_position(drones_systems_counter).data.system.get_elem_by_position(system_counter).data.text
                      break
                  else:
                    break

                  system_counter += 1
            else:
              break
            drones_systems_counter += 1
      else:
        break

      systems_counter += 1

    return founded_text

      

  """
  def generate_output_xml(self):
    root = ET.Element("respuesta")
    lista_mensajes = ET.SubElement(root, "listaMensajes")

    counter = 1
    while True:
      message_elem = self.messages.get_elem_by_position(counter)

      if message_elem:
        mensaje = ET.SubElement(lista_mensajes, "mensaje", nombre=message_elem.data.name)
      else:
        break
  """