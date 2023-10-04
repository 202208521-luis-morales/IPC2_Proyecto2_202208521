from data_schemas.Db import Db
from data_schemas.LinkedList import LinkedList
from typing import Union
import os

db = LinkedList()

def check_file(ruta: str) -> Union[bool, str]:
  if not os.path.exists(ruta):
    return "# ERROR: El archivo no existe"
  
  extension = os.path.splitext(ruta)[1]
  extension_correcta = ".xml"
  
  if extension != extension_correcta:
    return f"# ERROR: Extensión incorrecta. Debe ser {extension_correcta}"
  
  return True

print("PROYECTO 2")
print("Luis Rodrigo Morales Florián")
print("Sección B")
print("Segundo Semestre 2023")

while True:
  print("\n")
  print("MENU")
  print("1. Inicialización")
  print("2. Cargar un archivo XML de entrada")
  print("3. Generar un archivo XML de salida")
  print("4. Gestión de drones")
  print("5. Gestión de sistemas de drones")
  print("6. Gestión de Mensajes")
  print("7. Ayuda")
  res1 = input("Ingrese el número de opción: ")
  print("\n")

  if res1 == "1":
    print("¿Está seguro de borrar todos los datos?")
    print("1. Sí")
    print("2. No")
    res2 = input("Ingrese el número de opción: ")
    
    if res2 == "1":
      db = LinkedList()
      print("Los datos se han borrado con éxito")
  if res1 == "2":
    print("Ha elegido '2. Cargar un archivo XML de entrada'")
    fl = input("Ingrese la ruta del archivo xml: ")
    ck_f = check_file(fl)
    if ck_f == True:
      db.append(Db(filename=fl))
      db.get_elem_by_position(db.get_length()).data.process_file()
      # db.get_elem_by_position(db.get_length()).data.print_data_all()
      print("# ÉXITO: El archivo ha sido cargado con éxito")
    else:
      print(ck_f)
  if res1 == "3":
    print("Ha elegido '3. Generar un archivo XML de salida'")

    if not db.is_empty():
      db.print_as_list(type="files")
      print("\n")
      pos_elem = input("Elija número de archivo que quiere procesar: ")

      db.get_elem_by_position(int(pos_elem)).data.generate_output_xml()
      print("# ÉXITO: El archivo salida.xml ha sido generado en la raíz de este proyecto")
    else:
      print("# ERROR: No hay ningún archivo. Debe de subir un archivo xml")

  if res1 == "4":
    print("Ha elegido '4. Gestión de drones'")
    if not db.is_empty():
      db.print_as_list(type="files")
      print("\n")
      pos_elem = input("Elija número de archivo que quiere procesar: ")
      print("Opciones")
      print("1. Ver listado de drones")
      print("2. Agregar un nuevo dron")
      res3 = input("Elija el número de opción: ")

      if res3 == "1":
        db.get_elem_by_position(int(pos_elem)).data.print_drones()
      elif res3 == "2":
        new_drone_name = input("Escriba el nombre del nuevo dron a agregar: ")
        db.get_elem_by_position(int(pos_elem)).data.add_drone(new_drone_name)

    else:
      print("# ERROR: No hay ningún archivo. Debe de subir un archivo xml")
    
  if res1 == "5":
    print("Has elegido '5. Gestión de sistemas de drones'")
    if not db.is_empty():
      db.print_as_list(type="files")
      print("\n")
      pos_elem = input("Elija número de archivo que quiere procesar: ")
      db.get_elem_by_position(int(pos_elem)).data.generate_graph_drones_system()
      print("\n")
      print("# ÉXITO: Gráfica generada con éxito")

    else:
      print("# ERROR: No hay ningún archivo. Debe de subir un archivo xml")
  if res1 == "6":
    print("Has elegido '6. Gestión de Mensajes'")
    if not db.is_empty():
      db.print_as_list(type="files")
      print("\n")
      pos_elem = input("Elija número de archivo que quiere procesar: ")
      print("1. Ver listado de mensajes y sus instrucciones")
      print("2. Ver instrucciones para enviar un mensaje")
      res2 = input("Elija el número de opción: ")

      if res2 == "1":
        db.get_elem_by_position(pos_elem).data.print_all_processed_data()
      elif res2 == "2":
        pass

      # db.get_elem_by_position(int(pos_elem)).data.generate_graph_drones_system()
      print("\n")
      print("# ÉXITO: Gráfica generada con éxito")

    else:
      print("# ERROR: No hay ningún archivo. Debe de subir un archivo xml")
  if res1 == "7":
    print("Ha elegido '7. Ayuda'")
    print("DATOS ESTUDIANTE")
    print("- Luis Rodrigo Morales Florián")
    print("- 202208521")
    print("- LABORATORIO INTRODUCCION A LA PROGRAMACION Y COMPUTACION 2 Sección B")

    print("\n")
    print("Link de la documentación: https://")