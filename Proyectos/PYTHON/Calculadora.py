import tkinter as tk

class Calculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Calculadora")
        self.geometry("400x600")
        self.create_widgets()

    def create_widgets(self):
        self.entry = tk.Entry(self, font=('Arial', 24), borderwidth=2, relief='solid', justify='right')
        self.entry.grid(row=0, column=0, columnspan=4, sticky='nsew')
        
        buttons = [
            '7', '8', '9', '/',
            '4', '5', '6', '*',
            '1', '2', '3', '-',
            '0', '.', '=', '+'
        ]
        
        row_val = 1
        col_val = 0
        for button in buttons:
            action = lambda x=button: self.click_event(x)
            b = tk.Button(self, text=button, font=('Arial', 18), command=action, borderwidth=1, relief='solid')
            b.grid(row=row_val, column=col_val, sticky='nsew')
            col_val += 1
            if col_val > 3:
                col_val = 0
                row_val += 1

        for i in range(4):
            self.grid_columnconfigure(i, weight=1)
            self.grid_rowconfigure(i + 1, weight=1)

    def click_event(self, key):
        if key == '=':
            try:
                result = str(eval(self.entry.get()))
                self.entry.delete(0, tk.END)
                self.entry.insert(tk.END, result)
            except Exception as e:
                self.entry.delete(0, tk.END)
                self.entry.insert(tk.END, 'Error')
        elif key == 'C':
            self.entry.delete(0, tk.END)
        else:
            self.entry.insert(tk.END, key)

if __name__ == "__main__":
    app = Calculator()
    app.mainloop()
