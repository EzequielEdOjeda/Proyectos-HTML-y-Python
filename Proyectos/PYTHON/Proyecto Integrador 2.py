

def verificar(dato):
    while dato == "":
        print("Error")
        dato = input("Ingrese el dato nuevamente: ")
    return dato


def convertir(valor):
    while valor.isdecimal() == False:
        print("Error")
        valor = input("Ingrese valor nuevamente: ")
    return valor



##############################################################################


# Crear un diccionario vacío.
alumnos = {}

# Ejecutar el siguiente código infintamente.
while True:
    print("Ingrese el número de la operación que desea ejecutar:")
    print("1 - Añadir un alumno a la lista.")
    print("2 - Ver la lista de alumnos.")
    print("3 - Ver la cantidad de cursos de un alumno.")
    print("4 - Salir.")
    # Esto también podría ser:
    # opcion = input("Ingrese el número de opción: ")
    opcion = input(">>> ")
    
    if opcion == "1":
        #ingreso del alumno
        nombre_alumno = input("Ingrese el nombre del alumno: ")
        #funcion para verificar que no este vacio.
        nombre_alumno = verificar(nombre_alumno)
        # Es condición que la cantidad de cursos sea un número entero.
        # Necesitamos convertirlo ya que el resultado de input() es
        # siempre una cadena.
        cursos = input("Ingrese la cantidad de cursos: ")
        #usamos una funcion para convertir
        cursos = convertir(cursos)
        # Agregar un nuevo par clave-valor al diccionario "alumnos".
        # La clave es el nombre del alumno y el valor, la cantidad
        # de cursos.
        alumnos[nombre_alumno] = cursos
        print("Has ingresado el alumno correctamente.")
    elif opcion == "2":
        print("Los alumnos:")  
        # El bucle "for" aplicado sobre un diccionario recorre sus claves.  
        for nombre in alumnos:
            cursos = alumnos[nombre]
            # Necesito convertir "cursos" a una cadena para poder
            # concatenarlo con otras cadenas.
            print(nombre + " - " + str(cursos) + " cursos")
    elif opcion == "3":
        nombre = input("Ingrese el nombre del alumno: ")
        if nombre in alumnos:
            print(nombre +" tiene "+ str(alumnos[nombre])+" cursos.")
        else:
            print("Ese alumno no tiene cursos asignados")
    elif opcion == "4":
        print("¡Gracias por utilizar el programa!")
        # Forzar el bucle a que termine.
        break
    else:
        print("La opción ingresada no es correcta, vuelva a intentarlo.")


