import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import sqlite3
from datetime import datetime, date

class Database:
    """
    Maneja todas las operaciones de la base de datos (SQLite).
    Esto separa la lógica de la base de datos de la lógica de la interfaz de usuario.
    """
    def __init__(self, db_name='tareas.db'):
        """Inicializa la conexión a la base de datos y crea/actualiza la tabla."""
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self._check_and_update_schema()

    def _check_and_update_schema(self):
        """Crea la tabla si no existe y le añade la columna de fecha si es necesario."""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS tareas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                texto TEXT NOT NULL,
                completada INTEGER DEFAULT 0
            )
        ''')
        # Verificar si la columna fecha_limite existe
        self.cursor.execute("PRAGMA table_info(tareas)")
        columns = [column[1] for column in self.cursor.fetchall()]
        if 'fecha_limite' not in columns:
            self.cursor.execute("ALTER TABLE tareas ADD COLUMN fecha_limite TEXT")
        self.conn.commit()

    def fetch_all_tasks(self):
        """Obtiene todas las tareas de la base de datos, ordenadas por ID."""
        self.cursor.execute("SELECT id, texto, completada, fecha_limite FROM tareas ORDER BY id")
        return [{'id': row[0], 'texto': row[1], 'completada': bool(row[2]), 'fecha_limite': row[3]} for row in self.cursor.fetchall()]

    def add_task(self, texto, fecha_limite):
        """Agrega una nueva tarea a la base de datos."""
        self.cursor.execute("INSERT INTO tareas (texto, fecha_limite) VALUES (?, ?)", (texto, fecha_limite))
        self.conn.commit()
        return self.cursor.lastrowid

    def delete_task(self, task_id):
        """Elimina una tarea por su ID."""
        self.cursor.execute("DELETE FROM tareas WHERE id=?", (task_id,))
        self.conn.commit()

    def update_task_text(self, task_id, nuevo_texto):
        """Actualiza solo el texto de una tarea."""
        self.cursor.execute("UPDATE tareas SET texto=? WHERE id=?", (nuevo_texto, task_id))
        self.conn.commit()

    def update_task_date(self, task_id, fecha_limite):
        """Actualiza solo la fecha de una tarea."""
        self.cursor.execute("UPDATE tareas SET fecha_limite=? WHERE id=?", (fecha_limite, task_id))
        self.conn.commit()

    def toggle_task_status(self, task_id, is_completed):
        """Cambia el estado de completado de una tarea."""
        self.cursor.execute("UPDATE tareas SET completada=? WHERE id=?", (int(is_completed), task_id))
        self.conn.commit()

    def close(self):
        """Cierra la conexión a la base de datos."""
        self.conn.close()

class TodoApp:
    """
    Clase principal de la aplicación que contiene la lógica de la interfaz
    de usuario y el estado de la aplicación.
    """
    def __init__(self, root):
        """Inicializa la aplicación."""
        self.root = root
        self.db = Database()
        self.tasks = self.db.fetch_all_tasks()
        self.visible_tasks = []
        self.current_filter = 'all'
        self.is_dark_mode = False

        # --- Definición de Temas de Color ---
        self.light_theme = {
            "bg": "#F0F0F0", "fg": "#000000", "frame_bg": "#F0F0F0",
            "entry_bg": "#FFFFFF", "entry_fg": "#000000",
            "button_bg": "#E1E1E1", "button_fg": "#000000",
            "active_button_bg": "#C6C6C6",
            "listbox_bg": "#FFFFFF", "listbox_fg": "#000000",
            "listbox_select_bg": "#0078D7", "listbox_select_fg": "#FFFFFF",
            "completed_fg": "#888888", "overdue_fg": "#D32F2F", "due_today_fg": "#F57C00"
        }
        self.dark_theme = {
            "bg": "#2E2E2E", "fg": "#FFFFFF", "frame_bg": "#2E2E2E",
            "entry_bg": "#3C3C3C", "entry_fg": "#FFFFFF",
            "button_bg": "#505050", "button_fg": "#FFFFFF",
            "active_button_bg": "#6A6A6A",
            "listbox_bg": "#3C3C3C", "listbox_fg": "#FFFFFF",
            "listbox_select_bg": "#0078D7", "listbox_select_fg": "#FFFFFF",
            "completed_fg": "#AAAAAA", "overdue_fg": "#E57373", "due_today_fg": "#FFB74D"
        }
        
        self.root.title("Tareas")
        self.root.geometry("700x550")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.style = ttk.Style(self.root)
        self._create_widgets()
        self.apply_theme()
        self.update_clock()
        self.refresh_task_list()

    def _create_widgets(self):
        """Crea y organiza todos los widgets en la ventana."""
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Frame Superior: Título, Reloj y Controles ---
        top_frame = ttk.Frame(self.main_frame)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_clock_frame = ttk.Frame(top_frame)
        title_clock_frame.pack(side=tk.LEFT, anchor='n')

        self.header_label = ttk.Label(title_clock_frame, text="Tareas", font=('Helvetica', 16, 'bold'))
        self.header_label.pack(anchor='w')
        self.clock_label = ttk.Label(title_clock_frame, text="", font=('Helvetica', 10))
        self.clock_label.pack(anchor='w')
        
        right_controls_frame = ttk.Frame(top_frame)
        right_controls_frame.pack(side=tk.RIGHT, anchor='n')

        filter_frame = ttk.Frame(right_controls_frame)
        filter_frame.pack(side=tk.LEFT, padx=(0, 10))
        
        self.filter_buttons = {
            'all': ttk.Button(filter_frame, text="Todas", command=lambda: self.set_filter('all')),
            'completed': ttk.Button(filter_frame, text="Completadas", command=lambda: self.set_filter('completed')),
            'pending': ttk.Button(filter_frame, text="Pendientes", command=lambda: self.set_filter('pending'))
        }
        self.filter_buttons['all'].pack(side=tk.LEFT, padx=2)
        self.filter_buttons['completed'].pack(side=tk.LEFT, padx=2)
        self.filter_buttons['pending'].pack(side=tk.LEFT, padx=2)
        
        self.theme_button = ttk.Button(right_controls_frame, text="🌙", width=3, command=self.toggle_theme)
        self.theme_button.pack(side=tk.RIGHT)

        # --- Frame de Entrada de Tareas ---
        input_frame = ttk.Frame(self.main_frame)
        input_frame.pack(fill=tk.X, pady=5)
        
        self.new_task_entry = ttk.Entry(input_frame, font=('Helvetica', 11))
        self.new_task_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.new_task_entry.bind("<Return>", self.add_task)
        
        self.add_button = ttk.Button(input_frame, text="Agregar Tarea", command=self.add_task)
        self.add_button.pack(side=tk.LEFT)
        
        self.search_entry = ttk.Entry(input_frame, font=('Helvetica', 11))
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(15, 0))
        self.search_entry.bind("<KeyRelease>", self.on_search)
        self.setup_placeholder()

        # --- Frame de la Lista de Tareas ---
        list_frame = ttk.Frame(self.main_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.task_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, font=('Helvetica', 12), highlightthickness=0, borderwidth=0)
        self.task_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.task_listbox.yview)

        self.task_listbox.bind("<Double-Button-1>", self.toggle_task_status)
        self.task_listbox.bind("<Delete>", self.delete_task)
        
        # --- Frame Inferior: Botones de Acción ---
        bottom_frame = ttk.Frame(self.main_frame)
        bottom_frame.pack(fill=tk.X, pady=(10, 0))

        self.edit_button = ttk.Button(bottom_frame, text="Editar Tarea", command=self.edit_task)
        self.edit_button.pack(side=tk.LEFT, padx=2)
        self.set_date_button = ttk.Button(bottom_frame, text="Asignar Fecha", command=self.set_task_date)
        self.set_date_button.pack(side=tk.LEFT, padx=2)
        self.delete_button = ttk.Button(bottom_frame, text="Eliminar Tarea", command=self.delete_task)
        self.delete_button.pack(side=tk.LEFT, padx=2)
        
        self.status_label = ttk.Label(bottom_frame, text="Doble click para completar, 'Supr' para borrar.")
        self.status_label.pack(side=tk.RIGHT)

    def apply_theme(self):
        """Aplica el tema de color seleccionado a todos los widgets."""
        theme = self.dark_theme if self.is_dark_mode else self.light_theme
        
        self.root.config(bg=theme["bg"])
        self.style.theme_use('clam')

        self.style.configure('.', background=theme["bg"], foreground=theme["fg"], font=('Helvetica', 10))
        self.style.configure("TFrame", background=theme["frame_bg"])
        self.style.configure("Header.TLabel", background=theme["bg"], foreground=theme["fg"], font=('Helvetica', 16, 'bold'))
        self.header_label.config(style="Header.TLabel")
        self.clock_label.config(background=theme["bg"], foreground=theme["fg"])

        self.style.configure("TButton", padding=5, font=('Helvetica', 10), background=theme["button_bg"], foreground=theme["button_fg"])
        self.style.map("TButton", background=[('active', theme["active_button_bg"])])
        self.style.configure("Active.TButton", background=theme["active_button_bg"])

        self.style.configure("TEntry", fieldbackground=theme["entry_bg"], foreground=theme["entry_fg"], insertcolor=theme["fg"])
        self.style.configure("Placeholder.TEntry", fieldbackground=theme["entry_bg"], foreground="grey")
        self.setup_placeholder()

        self.task_listbox.config(bg=theme["listbox_bg"], fg=theme["listbox_fg"], 
                                selectbackground=theme["listbox_select_bg"], 
                                selectforeground=theme["listbox_select_fg"])

        self.main_frame.config(style="TFrame")
        self.status_label.config(background=theme["bg"], foreground=theme["fg"])
        self.theme_button.config(text="☀️" if self.is_dark_mode else "🌙")

        self.update_filter_buttons_style()
        self.refresh_task_list()

    def toggle_theme(self):
        """Cambia entre modo claro y oscuro."""
        self.is_dark_mode = not self.is_dark_mode
        self.apply_theme()

    def update_clock(self):
        """Actualiza la etiqueta del reloj cada segundo."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.clock_label.config(text=now)
        self.root.after(1000, self.update_clock)

    def update_filter_buttons_style(self):
        """Actualiza el estilo de los botones de filtro para resaltar el activo."""
        for mode, button in self.filter_buttons.items():
            button.config(style="Active.TButton" if mode == self.current_filter else "TButton")

    def refresh_task_list(self):
        """Limpia y recarga la lista de tareas en la UI aplicando filtros, búsqueda y colores."""
        self.task_listbox.delete(0, tk.END)
        self.visible_tasks.clear()
        
        theme = self.dark_theme if self.is_dark_mode else self.light_theme
        search_query = self.search_entry.get().lower()
        if self.search_entry.cget('style') == "Placeholder.TEntry":
            search_query = ""

        today = date.today()

        for task in self.tasks:
            if (self.current_filter == 'completed' and not task['completada']) or \
               (self.current_filter == 'pending' and task['completada']) or \
               (search_query and search_query not in task['texto'].lower()):
                continue
            self.visible_tasks.append(task)

        for i, task in enumerate(self.visible_tasks):
            date_str = f" [{task['fecha_limite']}]" if task['fecha_limite'] else ""
            display_text = f"✅ {task['texto']}{date_str}" if task['completada'] else f"   {task['texto']}{date_str}"
            self.task_listbox.insert(tk.END, display_text)
            
            fg_color = theme["listbox_fg"]
            if task['completada']:
                fg_color = theme["completed_fg"]
            elif task['fecha_limite']:
                try:
                    due_date = datetime.strptime(task['fecha_limite'], "%Y-%m-%d").date()
                    if due_date < today:
                        fg_color = theme["overdue_fg"]
                    elif due_date == today:
                        fg_color = theme["due_today_fg"]
                except ValueError:
                    pass # Ignorar formato de fecha inválido
            
            self.task_listbox.itemconfig(i, {'fg': fg_color})

    def add_task(self, event=None):
        """Agrega una nueva tarea, pidiendo opcionalmente una fecha."""
        task_text = self.new_task_entry.get().strip()
        if not task_text:
            messagebox.showwarning("Advertencia", "Por favor, ingresa una tarea.")
            return

        fecha_limite_str = simpledialog.askstring("Fecha Límite", "Ingresa la fecha límite (YYYY-MM-DD) (Opcional):")
        if fecha_limite_str:
            try:
                datetime.strptime(fecha_limite_str, "%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Error", "Formato de fecha inválido. Use YYYY-MM-DD.")
                return
        
        new_id = self.db.add_task(task_text, fecha_limite_str)
        self.tasks.append({'id': new_id, 'texto': task_text, 'completada': False, 'fecha_limite': fecha_limite_str})
        self.new_task_entry.delete(0, tk.END)
        self.refresh_task_list()

    def get_selected_task(self):
        """Obtiene la tarea seleccionada usando un mapa interno."""
        selected_indices = self.task_listbox.curselection()
        if not selected_indices:
            return None
        return self.visible_tasks[selected_indices[0]]

    def delete_task(self, event=None):
        """Elimina la tarea seleccionada."""
        selected_task = self.get_selected_task()
        if not selected_task:
            messagebox.showwarning("Advertencia", "Por favor, selecciona una tarea para eliminar.")
            return

        if messagebox.askyesno("Confirmar Eliminación", f"¿Estás seguro de que quieres eliminar la tarea:\n'{selected_task['texto']}'?"):
            self.db.delete_task(selected_task['id'])
            self.tasks = [t for t in self.tasks if t['id'] != selected_task['id']]
            self.refresh_task_list()

    def edit_task(self):
        """Edita el texto de la tarea seleccionada."""
        selected_task = self.get_selected_task()
        if not selected_task:
            messagebox.showwarning("Advertencia", "Por favor, selecciona una tarea para editar.")
            return

        nuevo_texto = simpledialog.askstring("Editar Tarea", "Edita el texto de la tarea:", initialvalue=selected_task['texto'])
        if nuevo_texto and nuevo_texto.strip():
            nuevo_texto = nuevo_texto.strip()
            self.db.update_task_text(selected_task['id'], nuevo_texto)
            selected_task['texto'] = nuevo_texto 
            self.refresh_task_list()
        elif nuevo_texto is not None:
            messagebox.showwarning("Advertencia", "El texto de la tarea no puede estar vacío.")

    def set_task_date(self):
        """Asigna o edita la fecha de la tarea seleccionada."""
        selected_task = self.get_selected_task()
        if not selected_task:
            messagebox.showwarning("Advertencia", "Por favor, selecciona una tarea para asignarle una fecha.")
            return

        fecha_limite_str = simpledialog.askstring("Asignar Fecha", "Ingresa la fecha límite (YYYY-MM-DD):", initialvalue=selected_task.get('fecha_limite', ''))
        if fecha_limite_str:
            try:
                datetime.strptime(fecha_limite_str, "%Y-%m-%d")
                self.db.update_task_date(selected_task['id'], fecha_limite_str)
                selected_task['fecha_limite'] = fecha_limite_str
                self.refresh_task_list()
            except ValueError:
                messagebox.showerror("Error", "Formato de fecha inválido. Use YYYY-MM-DD.")
        elif fecha_limite_str == '': # Permitir borrar la fecha
            self.db.update_task_date(selected_task['id'], None)
            selected_task['fecha_limite'] = None
            self.refresh_task_list()

    def toggle_task_status(self, event=None):
        """Cambia el estado de completado de la tarea seleccionada."""
        selected_task = self.get_selected_task()
        if not selected_task: return
        
        selected_task['completada'] = not selected_task['completada']
        self.db.toggle_task_status(selected_task['id'], selected_task['completada'])
        self.refresh_task_list()

    def set_filter(self, mode):
        """Establece el filtro actual y refresca la lista."""
        self.current_filter = mode
        self.update_filter_buttons_style()
        self.refresh_task_list()

    def on_search(self, event=None):
        """Se llama cada vez que se presiona una tecla en el campo de búsqueda."""
        self.refresh_task_list()

    def setup_placeholder(self):
        """Configura el placeholder para el campo de búsqueda."""
        current_style = self.search_entry.cget('style')
        if not self.search_entry.get() and current_style != "Placeholder.TEntry":
            self.search_entry.insert(0, "Buscar tareas...")
            self.search_entry.config(style='Placeholder.TEntry')

        def on_focus_in(event):
            if self.search_entry.cget('style') == "Placeholder.TEntry":
                self.search_entry.delete(0, tk.END)
                self.search_entry.config(style='TEntry')
        
        def on_focus_out(event):
            if not self.search_entry.get():
                self.search_entry.insert(0, "Buscar tareas...")
                self.search_entry.config(style='Placeholder.TEntry')
        
        self.search_entry.bind("<FocusIn>", on_focus_in, add='+')
        self.search_entry.bind("<FocusOut>", on_focus_out, add='+')

    def on_closing(self):
        """Se ejecuta al cerrar la ventana para cerrar la conexión a la BD."""
        self.db.close()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()
