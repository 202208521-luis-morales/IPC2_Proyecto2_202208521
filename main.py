from data_schemas.Db import Db

db = Db()

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
      db = Db()
      print("Los datos se han borrado con éxito")
  if res1 == "2":
    pass
  if res1 == "3":
    pass
  if res1 == "4":
    pass
  if res1 == "5":
    pass
  if res1 == "6":
    pass
  if res1 == "7":
    pass