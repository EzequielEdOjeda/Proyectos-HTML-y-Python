
# Crear una lista vacía.
alumnos = []

# Ejecutar el siguiente código infintamente.
while True:
    print("Ingrese el número de la operación que desea ejecutar:")
    print("1 - Añadir un alumno a la lista.")
    print("2 - Ver la lista de alumnos.")
    print("3 - Salir.")
    # Esto también podría ser:
    # opcion = input("Ingrese el número de opción: ")
    opcion = input(">>> ") 
    if opcion == "1":
        nombre_alumno = input("Ingrese el nombre del alumno: ")
        # Es condición que la cantidad de cursos sea un número entero.
        # Necesitamos convertirlo ya que el resultado de input() es
        # siempre una cadena.
        cursos = input("Ingrese la cantidad de cursos: ")
        cursos = int(cursos)
        if nombre_alumno == "":
            print("Error: no ha ingresado un nombre válido.")
        else:
            # Agregar un elemento al final de la lista "alumnos" que
            # sea una lista con dos elementos: el nombre del alumno
            # y la cantidad de cursos.
            alumnos.append([nombre_alumno, cursos])
            print("Has ingresado el alumno correctamente.")
        print("Lista de alumnos:")
    elif opcion == "2":
        for alumno in alumnos:
            # Ejecuto este código para cada uno de los elementos
            # dentro de la lista "alumnos", que a su vez son listas
            # cuyo primer elemento es el nombre y el segundo, la
            # cantidad de cursos.
            nombre = alumno[0]
            cursos = alumno[1]
            # Necesito convertir "cursos" a una cadena para poder
            # concatenarlo con otras cadenas.
            print(nombre + " - " + str(cursos) + " cursos")
    elif opcion == "3":
        print("¡Gracias por utilizar el programa!")
        # Forzar el bucle a que termine.
        break
    else:
        print("La opción ingresada no es correcta, vuelva a intentarlo.")


