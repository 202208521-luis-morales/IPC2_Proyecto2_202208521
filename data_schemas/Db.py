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
import graphviz
import time as time_lib

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

      for contenido in sistema_drones.findall("contenido"):
        drones_systems_to_save = DronesSystems(contenido.find("dron").text)

        for altura in contenido.find("alturas").findall("altura"):
          drones_systems_to_save.add_system(System(altura.get("valor"), altura.text))

        systems_to_save.add_drones_systems(drones_systems_to_save)
      
      self.systems.append(systems_to_save)
    
    # Guardamos los datos de listaMensajes
    lista_mensajes = root.find("listaMensajes")
    for mensaje in lista_mensajes.findall("Mensaje"):
      message_to_save = Messages(mensaje.get("nombre"), mensaje.find("sistemaDrones").text)

      for instruccion in mensaje.find("instrucciones").findall("instruccion"):
        message_to_save.add_instruction(Instruction(instruccion.get("dron"), int(instruccion.text)))

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
            drones_status.append(Instruction(self.drones.get_elem_by_position(dron_counter).data, 0))
          else:
            break
          dron_counter += 1
        
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

        # La primera vez hace que la primera instrucción se esté ejecutando, las siguientes marca como "ejecutada"
        # la que se estaba ejecutando y la siguiente la marca como "ejecutandose y así sucesivamente"
        def go_to_next_inst():
          instructions_counter = 1

          while True:
            inst = message_elem.data.instructions.get_elem_by_position(instructions_counter)

            if inst:
              # Si ya se llegó a ese último elemento y está executing, que lo marque ya como executed
              if message_elem.data.instructions.get_length() == instructions_counter and inst.data.status == "executing":
                inst.data.status = "executed"
              elif inst.data.status == "not_exected":
                # Marcar la anterior como ejecutada
                if instructions_counter > 1:
                  prev_inst = message_elem.data.instructions.get_elem_by_position(instructions_counter - 1)

                  if prev_inst:
                    prev_inst.data.status = "executed"
                inst.data.status = "executing"
                break
            else:
              break
            instructions_counter += 1

        # Ponemos la primera como ejecutándose
        go_to_next_inst()
        
        time_counter = 1
        drones_status_counter = 1
        time_counter_changed = False
        row_to_save = Rows()

        a_ins_was_executed = False
        while True:
          dr_sts = drones_status.get_elem_by_position(drones_status_counter)
          inst_drones_to_save = None

          if time_counter_changed:
            row_to_save = Rows()
            time_counter_changed = False
          
          if dr_sts:
            curr_inst = get_curr_inst_by_drone(dr_sts.data.drone)

            if curr_inst:
              if curr_inst.move_num > dr_sts.data.move_num:
                dr_sts.data.move_num += 1
                inst_drones_to_save = InstDrones(dr_sts.data.drone, "Subir")
              elif curr_inst.move_num < dr_sts.data.move_num:
                dr_sts.data.move_num -= 1
                inst_drones_to_save = InstDrones(dr_sts.data.drone, "Bajar")
              else:
                if curr_inst.status == "executing" and curr_inst.drone == dr_sts.data.drone:
                  inst_drones_to_save = InstDrones(dr_sts.data.drone, "Emitir Luz")
                  process_data_to_save.final_message = process_data_to_save.final_message + self.get_text_by_drones_system_drone_and_height(message_elem.data.drones_system, curr_inst.drone, curr_inst.move_num)
                  
                  # Marcamos que se acaba de ejecutar una instrucción y más adelante la cancelamos
                  a_ins_was_executed = True
                else:
                  inst_drones_to_save = InstDrones(dr_sts.data.drone, "Esperar")
            
            # Consideramos el caso donde no encuentra ninguna instrucción para su dron, por lo cual solo le queda esperar   
            else:
              inst_drones_to_save = InstDrones(dr_sts.data.drone, "Esperar")

            # Marcamos la actual como ejecutada
            # Si ya le dimos la vuelta a todos los drones, procede a marcar la instrucción que se está ejecutando
            # como ejecutada y se ejecuta la siguiente
            if drones_status.get_length() == drones_status_counter and a_ins_was_executed:
              go_to_next_inst()
              # Aquí cancelamos que fue ejecutada una instrucción para así pasar a la siguiente
              a_ins_was_executed = False

            row_to_save.add_instdrones(inst_drones_to_save)
            drones_status_counter += 1
          else:
            row_to_save.set_time(time_counter)
            process_data_to_save.add_row(row_to_save)

            # Al registrar la última fila, chequea si queda otras instrucciones que ejecutar
            # Si ya no hay, sale del ciclo
            if check_if_all_inst_are_executed():
              break

            drones_status_counter = 1
            time_counter += 1
            time_counter_changed = True


        self.processed_data.append(process_data_to_save)
      else:
        break
        
      counter += 1
    
    self.print_data_all()

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
                    if int(self.systems.get_elem_by_position(systems_counter).data.drones_systems.get_elem_by_position(drones_systems_counter).data.system.get_elem_by_position(system_counter).data.height) == height:
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

  def print_drones(self):
    self.drones.print_as_list()

  def add_drone(self, drone_name):
    founded_drone = False

    drone_counter = 1#self.drones.append(drone_name)
    while True:
      drone = self.drones.get_elem_by_position(drone_counter)
      if drone:
        if drone.data == drone_name:
          founded_drone = True
      else:
        break
      drone_counter +=1

    if founded_drone:
      print("# ERROR: El dron ya existe")
    else:
      self.drones.append(drone_name)

  def generate_graph_drones_system(self):
    self.systems.print_as_list(type="system_name")
    drones_system_num = int(input("Elija el número de sistema que desea imprimir: "))

    dot = graphviz.Digraph()
    drones_sys = self.systems.get_elem_by_position(drones_system_num).data
    dot.node("head", drones_sys.name, shape="circle")
    dot.node("height", "Altura (mts)", shape="circle")
    dot.edge("height","head")

    # Agregar nodos de los nombre de los drones junto con su sistema
    data_drones_system_counter = 1
    while True:
      data_drones_system = drones_sys.drones_systems.get_elem_by_position(data_drones_system_counter)

      if data_drones_system:
        dron_name = data_drones_system.data.name
        dot.node(dron_name, dron_name)

        system_counter = 1
        while True:
          system = data_drones_system.data.system.get_elem_by_position(system_counter)

          if system:
            if data_drones_system_counter == 1:
              dot.node(str(system_counter), str(system_counter))
              if system_counter == 1:
                dot.edge(str(system_counter), "height")
              else:
                dot.edge(str(system_counter), str(system_counter - 1))

            dot.node(str(system_counter) + dron_name, system.data.text if system.data.height == system_counter else "-")
            if system_counter == 1:
              dot.edge(str(system_counter) + dron_name, dron_name)
            else:
              dot.edge(str(system_counter) + dron_name, str(system_counter - 1) + dron_name)
          else:
            break
          system_counter += 1
      else:
        break
      data_drones_system_counter += 1
    
    dot.render("drones_system_graph", view=True)

  def print_processed_data_by_processed_data_num(self, pr_dt_num):
    message = self.processed_data.get_elem_by_position(pr_dt_num).data
    print("+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+")
    print("Nombre del mensaje: " + message.message_name)
    print("Mensaje Final: " + message.final_message)
    print("Tiempo óptimo: " +message.rows.get_length())

    row_counter = 1
    while True:
      row = message.rows.get_elem_by_position(row_counter)

      if row:
        row_to_print = str(row.data.time) + ","
        first_row_to_print = str("Tiempo (seg)") + ","

        instdrones_counter = 1
        while True:
          instdrones = row.instdrones.get_elem_by_position(row_counter)

          if instdrones:
            if row_counter == 1:
              first_row_to_print += instdrones.data.drone + ","
            row_to_print += str(instdrones.data.inst) + ","
          else:
            break
          instdrones_counter += 1

        if row_counter == 1:
          print(first_row_to_print)
        print(row_to_print)
        
      else:
        break
      row_counter += 1
    print("+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+")

  def print_all_processed_data(self):
    processed_data_counter = 1
    while True:
      processed_data = self.processed_data.get_elem_by_position(processed_data_counter)
      if processed_data:
        self.print_processed_data_by_processed_data_num(processed_data_counter)
      else:
        break
      processed_data_counter += 1

  def print_specific_processed_data(self):
    self.processed_data.print_as_list(type="processed_data")
    pr_dt_num = input("Elija el número de mensaje que quiere imprimir: ")

    self.print_processed_data_by_processed_data_num(pr_dt_num)
    self.generate_graph_specific_processed_data(pr_dt_num)

  def generate_graph_specific_processed_data(self, pr_dt_num):
    message = self.processed_data.get_elem_by_position(pr_dt_num).data

    dot = graphviz.Digraph()

    dot.node("head", f"Nombre mensaje: {message.message_name}")
    dot.node("time_title", "Tiempo (seg)")
    dot.edge("time_title", "head")
    row_counter = 1
    while True:
      row = message.rows.get_elem_by_position(row_counter)

      if row:
        dot.node("t_" + str(row_counter), str(row.data.time))
        if row_counter == 1:
          dot.edge("t_" + str(row_counter), "time_title")
        else:
          dot.edge("t_" + str(row_counter), str(row_counter - 1))

        instdrones_counter = 1
        while True:
          instdrones = row.instdrones.get_elem_by_position(row_counter)

          if instdrones:
            dot.node(str(row_counter) + instdrones.data.drone, instdrones.data.inst)

            if row_counter == 1:
              dot.node(instdrones.data.drone, instdrones.data.drone)
              dot.edge(instdrones.data.drone, "head")
              dot.edge(str(row_counter) + instdrones.data.drone, instdrones.data.drone)
            else:
              dot.edge(str(row_counter) + instdrones.data.drone, str(row_counter - 1) + instdrones.data.drone)

          else:
            break
          instdrones_counter += 1
        
      else:
        break
      row_counter += 1
    
    dot.render("graph_processed_data", view=True)

  def generate_output_xml(self):
    root = ET.Element("respuesta")
    lista_mensajes = ET.SubElement(root, "listaMensajes")

    processed_data_counter = 1
    while True:
      processed_data = self.processed_data.get_elem_by_position(processed_data_counter)

      if processed_data:
        mensaje = ET.SubElement(lista_mensajes, "mensaje", nombre=processed_data.data.message_name)
        sistema_drones = ET.SubElement(mensaje, "sistemaDrones")
        sistema_drones.text = self.get_drones_system_name_by_message_name(self, processed_data.data.message_name)
        tiempo_optimo = ET.SubElement(mensaje, "tiempoOptimo")
        tiempo_optimo.text = processed_data.data.rows.get_length()
        mensaje_recibido = ET.SubElement(mensaje, "mensajeRecibido")
        mensaje_recibido.text = processed_data.data.final_message

        instrucciones = ET.SubElement(mensaje, "instrucciones")

        row_counter = 1
        while True:
          row = processed_data.data.rows.get_elem_by_position(row_counter)

          if row:
            tiempo = ET.SubElement(instrucciones, "tiempo", valor=row.data.time)
            acciones = ET.SubElement(tiempo, "acciones")

            instdrones_counter = 1

            while True:
              instdrones = row.get_elem_by_position(instdrones_counter)

              if instdrones:
                dron = ET.SubElement(acciones, "dron", nombre=str(instdrones.data.drone))
                dron.text = instdrones.data.inst
              else:
                break

              instdrones_counter += 1
          else:
            break
          row_counter += 1
      else:
        break

      processed_data_counter += 1

  def get_drones_system_name_by_message_name(self, message_name):
    message_counter = 1
    founded_drones_system_name = None

    while True:
      message = self.messages.get_elem_by_position(message_counter)
      
      if message:
        if message.data.name == message_name:
          founded_drones_system_name = message.data.drones_system
      else:
        break
      message_counter += 1

    return founded_drones_system_name
  
  
  def print_data_drones(self):
    print("/-/-/-/-/-/-/-/-/-/-/-/-/")
    print("DRONES")
    self.drones.print_as_list()
    print("/-/-/-/-/-/-/-/-/-/-/-/-/")

  def print_data_systems(self):
    print("/-/-/-/-/-/-/-/-/-/-/-/-/")
    print("SYSTEMS")

    systems_counter = 1
    while True:
      systems = self.systems.get_elem_by_position(systems_counter)

      if systems:
        print(f"System_{systems_counter}:")
        print(f"* name: {systems.data.name}")

        drones_systems_counter = 1
        while True:
          drones_systems = systems.data.drones_systems.get_elem_by_position(drones_systems_counter)

          if drones_systems:
            print(f"* dronesSystem_{drones_systems_counter}:")
            print(f"** drone: {drones_systems.data.drone}")

            system_counter = 1
            while True:
              system = drones_systems.data.system.get_elem_by_position(system_counter)

              if system:
                print(f"** system_{system_counter}:")
                print(f"*** height: {system.data.height}")
                print(f"*** text: {system.data.text}")
              else:
                break
              system_counter += 1
          else:
            break
          drones_systems_counter += 1
      else:
        break
      systems_counter += 1
    print("/-/-/-/-/-/-/-/-/-/-/-/-/")

  def print_data_messages(self):
    print("/-/-/-/-/-/-/-/-/-/-/-/-/")
    print("MESSAGES")

    messages_counter = 1
    while True:
      messages = self.messages.get_elem_by_position(messages_counter)

      if messages:
        print(f"Message_{messages_counter}:")
        print(f"* name: {messages.data.name}")
        print(f"* dronesSystem: {messages.data.drones_system}")

        instructions_counter = 1
        while True:
          instructions = messages.data.instructions.get_elem_by_position(instructions_counter)

          if instructions:
            print(f"* instructions_{instructions_counter}:")
            print(f"** drone: {instructions.data.drone}")
            print(f"** moveNum: {instructions.data.move_num}")
            print(f"** status: {instructions.data.status}")

          else:
            break
          instructions_counter += 1
      else:
        break
      messages_counter += 1
    print("/-/-/-/-/-/-/-/-/-/-/-/-/")

  def print_data_processed_data(self):
    print("/-/-/-/-/-/-/-/-/-/-/-/-/")
    print("PROCESSED DATA")

    processed_data_counter = 1
    while True:
      processed_data = self.processed_data.get_elem_by_position(processed_data_counter)

      if processed_data:
        print(f"ProcessedData_{processed_data_counter}:")
        print(f"* messageName: {processed_data.data.message_name}")
        print(f"* finalMessage: {processed_data.data.final_message}")

        rows_counter = 1
        while True:
          rows = processed_data.data.rows.get_elem_by_position(rows_counter)

          if rows:
            print(f"* rows_{rows_counter}:")
            print(f"** time: {rows.data.time}")

            instdrones_counter = 1
            while True:
              instdrones = rows.data.instdrones.get_elem_by_position(instdrones_counter)

              if instdrones:
                print(f"** instdrones_{instdrones_counter}:")
                print(f"*** drone: {instdrones.data.drone}")
                print(f"*** inst: {instdrones.data.inst}")
              else:
                break
              instdrones_counter += 1
          else:
            break
          rows_counter += 1
      else:
        break
      processed_data_counter += 1
    print("/-/-/-/-/-/-/-/-/-/-/-/-/")

  def print_data_all(self):
    print("##########################")
    print("##       ALL DATA       ##")
    print("##########################")
    self.print_data_drones()
    self.print_data_messages()
    self.print_data_systems()
    self.print_data_processed_data()