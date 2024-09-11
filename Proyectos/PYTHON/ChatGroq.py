import os
import tkinter as tk
from tkinter import simpledialog, scrolledtext, messagebox, ttk
from groq import Groq

# Configurar la ventana principal
ventana = tk.Tk()
ventana.title("Chat con IA")
ventana.geometry("600x500")
ventana.configure(bg="#f0f4f8")  # Fondo claro

# Variable global para almacenar la API key, cliente y modelo
api_key = None
client = None
selected_model = None

# Función para solicitar la API key
def solicitar_api_key():
    global api_key
    api_key = simpledialog.askstring("API Key", "Introduce tu API Key de Groq:")
    if not api_key:
        messagebox.showerror("Error", "API Key es requerida")
        ventana.destroy()
        return
    os.environ["GROQ_API_KEY"] = api_key
    mostrar_seleccion_modelo()

# Función para mostrar la selección de modelo
def mostrar_seleccion_modelo():
    ventana.withdraw()
    model_window = tk.Toplevel(ventana)
    model_window.title("Seleccionar Modelo")
    model_window.geometry("400x160")
    model_window.configure(bg="#f0f4f8")

    model_label = tk.Label(model_window, text="Selecciona un Model ID:", bg="#f0f4f8", font=('Helvetica', 14))
    model_label.pack(pady=10)

    # Opciones de Model IDs
    model_ids = [
        "llama-3.1-70b-versatile",
        "llama-3.1-8b-instant",
        "llama3-groq-70b-8192-tool-use-preview",
        "llama3-groq-8b-8192-tool-use-preview",
        "llama-guard-3-8b",
        "llama3-70b-8192",
        "llama3-8b-8192",
        "mixtral-8x7b-32768",
        "gemma-7b-it",
        "gemma2-9b-it",
        "whisper-large-v3"
    ]

    # Dropdown para seleccionar el modelo
    model_var = tk.StringVar()
    model_var.set(model_ids[0])  # Selección por defecto

    dropdown = ttk.Combobox(model_window, textvariable=model_var, values=model_ids, font=('Helvetica', 12), state="readonly")
    dropdown.pack(pady=10)

    # Botón para confirmar la selección del modelo
    done_button = tk.Button(model_window, text="Listo", font=('Helvetica', 14, 'bold'), command=lambda: iniciar_cliente(model_var.get(), model_window), bg="#1f77b4", fg="#ffffff", borderwidth=0, relief='flat')
    done_button.pack(pady=20)

# Función para iniciar el cliente Groq
def iniciar_cliente(model_id, model_window):
    global client, selected_model
    try:
        client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
        selected_model = model_id
        model_window.destroy()
        ventana.deiconify()  # Mostrar la ventana principal
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo conectar a la API: {str(e)}")
        ventana.destroy()

# Función para enviar el mensaje al servidor de IA y recibir la respuesta
def enviar_mensaje(event=None):
    user_input = entry.get("1.0", tk.END).strip()
    if user_input:
        chat_area.config(state=tk.NORMAL)
        chat_area.insert(tk.END, f"Tú: {user_input}\n", 'user')
        chat_area.config(state=tk.DISABLED)
        entry.delete("1.0", tk.END)

        try:
            # Enviar el mensaje a la API de Groq
            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "user", "content": user_input}
                ],
                model=selected_model,
            )

            ia_response = chat_completion.choices[0].message.content

        except Exception as e:
            ia_response = f"Error al conectar con la API: {str(e)}"

        # Mostrar la respuesta de la IA
        chat_area.config(state=tk.NORMAL)
        chat_area.insert(tk.END, f"IA: {ia_response}\n", 'ai')
        chat_area.config(state=tk.DISABLED)
        chat_area.yview(tk.END)

# Ocultar la ventana principal mientras se solicita la API key
ventana.withdraw()

# Solicitar la API key al iniciar
solicitar_api_key()

# Configurar la cuadrícula principal para que se ajuste al tamaño
ventana.grid_columnconfigure(0, weight=1)
ventana.grid_rowconfigure(0, weight=1)
ventana.grid_rowconfigure(1, weight=0)

# Área de chat (texto ampliado)
chat_area = scrolledtext.ScrolledText(ventana, wrap=tk.WORD, font=('Helvetica', 14), state=tk.DISABLED, bg="#ffffff", fg="#000000", insertbackground='black')
chat_area.tag_configure('user', foreground="#1f77b4", font=('Helvetica', 14, 'bold'))
chat_area.tag_configure('ai', foreground="#ff7f0e", font=('Helvetica', 14, 'italic'))
chat_area.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

# Frame para entrada de texto y botón de enviar
entry_frame = tk.Frame(ventana, bg="#f0f4f8")
entry_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)

# Configurar la cuadrícula dentro del frame de entrada
entry_frame.grid_columnconfigure(0, weight=1)
entry_frame.grid_columnconfigure(1, weight=0)

# Campo de entrada de texto
entry = tk.Text(entry_frame, height=2, font=('Helvetica', 15), bg="#ffffff", fg="#000000", borderwidth=2, relief='groove')
entry.grid(row=0, column=0, sticky="ew", padx=10)

# Botón de enviar
send_button = tk.Button(entry_frame, text="Enviar", font=('Helvetica', 14, 'bold'), command=enviar_mensaje, bg="#1f77b4", fg="#ffffff", borderwidth=0, relief='flat')
send_button.grid(row=0, column=1, sticky="nsew", padx=10)

# Asegurar que el campo de texto tenga la misma altura que el botón
entry_frame.update_idletasks()
entry_height = send_button.winfo_height()
entry.config(height=int(entry_height / 30))  # Ajustar altura del campo de texto

# Enviar mensaje al presionar Enter
entry.bind("<Return>", enviar_mensaje)

# Iniciar la interfaz
ventana.mainloop()
