import tkinter as tk
from tkinter import messagebox
from datetime import datetime
import sqlite3

# --- Base de datos ---
conn = sqlite3.connect("tareas.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS tareas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    texto TEXT NOT NULL,
    completada INTEGER DEFAULT 0
)
""")
conn.commit()

# --- Funciones ---
def cargar_tareas():
    lista_tareas.delete(0, tk.END)
    for row in cursor.execute("SELECT id, texto, completada FROM tareas"):
        texto = f"✅ {row[1]}" if row[2] else row[1]
        lista_tareas.insert(tk.END, f"{row[0]}. {texto}")

def agregar_tarea():
    tarea = entrada.get().strip()
    if tarea:
        cursor.execute("INSERT INTO tareas (texto) VALUES (?)", (tarea,))
        conn.commit()
        entrada.delete(0, tk.END)
        cargar_tareas()

def eliminar_tarea():
    seleccion = lista_tareas.curselection()
    if seleccion:
        tarea_id = int(lista_tareas.get(seleccion[0]).split(".")[0])
        cursor.execute("DELETE FROM tareas WHERE id=?", (tarea_id,))
        conn.commit()
        cargar_tareas()

def limpiar_tareas():
    if messagebox.askyesno("¿Confirmar?", "¿Eliminar todas las tareas?"):
        cursor.execute("DELETE FROM tareas")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='tareas'")  # Reinicia el ID a 1
        conn.commit()
        cargar_tareas()

def alternar_completado(event):
    seleccion = lista_tareas.curselection()
    if seleccion:
        tarea_id = int(lista_tareas.get(seleccion[0]).split(".")[0])
        cursor.execute("SELECT completada FROM tareas WHERE id=?", (tarea_id,))
        estado = cursor.fetchone()[0]
        nuevo_estado = 0 if estado == 1 else 1
        cursor.execute("UPDATE tareas SET completada=? WHERE id=?", (nuevo_estado, tarea_id))
        conn.commit()
        cargar_tareas()

def actualizar_reloj():
    # Formato 12 horas con AM/PM
    ahora = datetime.now()
    hora_formateada = ahora.strftime("%I:%M:%S %p")
    reloj.config(text=hora_formateada)
    root.after(1000, actualizar_reloj)

def alternar_tema():
    global modo_oscuro
    modo_oscuro = not modo_oscuro
    if modo_oscuro:
        aplicar_estilo("#2d3436", "#dfe6e9", "#636e72", "#00cec9")
    else:
        aplicar_estilo("#f4f4f4", "#2d3436", "#ffffff", "#55efc4")

def aplicar_estilo(fondo, texto, entrada_bg, boton_bg):
    root.configure(bg=fondo)
    frame_superior.configure(bg=fondo)
    frame_lista.configure(bg=fondo)
    frame_entrada.configure(bg=fondo)
    reloj.configure(bg=fondo, fg=texto)
    titulo.configure(bg=fondo, fg=texto)
    entrada.configure(bg=entrada_bg, fg=texto, highlightbackground="#74b9ff", highlightcolor="#74b9ff", highlightthickness=2)
    for btn in [btn_agregar, btn_eliminar, btn_limpiar]:
        btn.configure(bg=boton_bg, fg="black")
    lista_tareas.configure(bg=entrada_bg, fg=texto, selectbackground="#74b9ff")

# --- Interfaz ---
modo_oscuro = False
root = tk.Tk()
root.title("Grupo 4 - Informatorio")
root.geometry("650x300")  # Más alto para que se vea cómodo
root.resizable(False, False)
root.configure(bg="#f4f4f4")

# Menú
menu = tk.Menu(root)
archivo = tk.Menu(menu, tearoff=0)
archivo.add_command(label="Modo Claro/Oscuro", command=alternar_tema)
archivo.add_separator()
archivo.add_command(label="Salir", command=root.quit)
menu.add_cascade(label="Archivo", menu=archivo)
root.config(menu=menu)

# Encabezado
frame_superior = tk.Frame(root, bg="#dfe6e9")
frame_superior.pack(fill="x")

titulo = tk.Label(frame_superior, text="Mis Tareas", font=("Segoe UI", 14, "bold"), bg="#dfe6e9")
titulo.pack(side="left", padx=10, pady=10)

reloj = tk.Label(frame_superior, font=("Segoe UI", 12), bg="#dfe6e9", fg="#2d3436")
reloj.pack(side="right", padx=10)
actualizar_reloj()

# Lista
frame_lista = tk.Frame(root, bg="#f4f4f4")
frame_lista.pack(fill="both", expand=True, padx=10, pady=(5,0))

scroll = tk.Scrollbar(frame_lista)
scroll.pack(side=tk.RIGHT, fill=tk.Y)

lista_tareas = tk.Listbox(frame_lista, font=("Segoe UI", 11), yscrollcommand=scroll.set,
                          bd=1, relief="solid", selectbackground="#74b9ff", height=8)
lista_tareas.pack(side=tk.LEFT, fill="both", expand=True)
scroll.config(command=lista_tareas.yview)
lista_tareas.bind("<Double-Button-1>", alternar_completado)

# Entrada
frame_entrada = tk.Frame(root, bg="#f4f4f4")
frame_entrada.pack(fill="x", padx=10, pady=10)

entrada = tk.Entry(frame_entrada, font=("Segoe UI", 12), relief="flat", bg="#ffffff", bd=2,
                   highlightthickness=2, highlightbackground="#74b9ff", highlightcolor="#74b9ff")
entrada.pack(side="left", fill="x", expand=True, pady=5, padx=(0,10))

btn_agregar = tk.Button(frame_entrada, text="Agregar", font=("Segoe UI", 11), bg="#55efc4", fg="black", command=agregar_tarea)
btn_agregar.pack(side="left", padx=5, ipady=5, ipadx=10)

btn_eliminar = tk.Button(frame_entrada, text="Eliminar", font=("Segoe UI", 11), bg="#fab1a0", fg="black", command=eliminar_tarea)
btn_eliminar.pack(side="left", padx=5, ipady=5, ipadx=10)

btn_limpiar = tk.Button(frame_entrada, text="Limpiar todo", font=("Segoe UI", 11), bg="#ffeaa7", fg="black", command=limpiar_tareas)
btn_limpiar.pack(side="left", padx=5, ipady=5, ipadx=10)

# Inicial
cargar_tareas()
root.mainloop()
