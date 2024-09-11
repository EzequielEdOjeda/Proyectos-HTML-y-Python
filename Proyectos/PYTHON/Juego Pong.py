import tkinter as tk
import random

class PongGame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Pong Game")
        self.geometry("800x600")
        self.resizable(False, False)
        self.center_window()

        # Pantalla de presentación
        self.start_screen = tk.Frame(self)
        self.start_screen.pack(fill="both", expand=True)
        self.start_label = tk.Label(self.start_screen, text="Pong Game", font=("Helvetica", 32))
        self.start_label.pack(pady=100)
        self.start_button = tk.Button(self.start_screen, text="Empezar", font=("Helvetica", 24), command=self.start_game, bg="lightblue", relief="groove", borderwidth=5)
        self.start_button.pack(pady=20)
        self.quit_button = tk.Button(self.start_screen, text="Salir", font=("Helvetica", 24), command=self.quit, bg="lightcoral", relief="groove", borderwidth=5)
        self.quit_button.pack(pady=20)

        # Pantalla del juego
        self.canvas = tk.Canvas(self, width=800, height=600, bg="black")
        self.paddle_left = None
        self.paddle_right = None
        self.ball = None
        self.score_left = 0
        self.score_right = 0
        self.score_text = None
        self.game_running = False

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    def start_game(self):
        self.start_screen.pack_forget()
        self.canvas.pack(fill="both", expand=True)
        self.paddle_left = self.canvas.create_rectangle(50, 250, 60, 350, fill="white")
        self.paddle_right = self.canvas.create_rectangle(740, 250, 750, 350, fill="white")
        # Pelota más grande (20x20 en lugar de 10x10)
        self.ball = self.canvas.create_oval(390, 290, 410, 310, fill="white")
        self.score_text = self.canvas.create_text(400, 50, text="0 - 0", font=("Helvetica", 24), fill="white")
        self.bind("<KeyPress>", self.key_press)
        self.bind("<KeyRelease>", self.key_release)
        self.game_running = True
        self.ball_speed_x = 5 * random.choice([-1, 1])
        self.ball_speed_y = 5 * random.choice([-1, 1])
        self.paddle_speed = 5
        self.paddle_left_moving = 0
        self.paddle_right_moving = 0
        self.update_game()

    def key_press(self, event):
        if event.keysym == 'q':
            self.paddle_left_moving = -1
        elif event.keysym == 'a':
            self.paddle_left_moving = 1
        elif event.keysym == 'p':
            self.paddle_right_moving = -1
        elif event.keysym == 'l':
            self.paddle_right_moving = 1

    def key_release(self, event):
        if event.keysym in ['q', 'a']:
            self.paddle_left_moving = 0
        elif event.keysym in ['p', 'l']:
            self.paddle_right_moving = 0

    def update_game(self):
        if self.game_running:
            self.move_paddles()
            self.move_ball()
            self.check_collisions()
            self.after(20, self.update_game)

    def move_paddles(self):
        self.canvas.move(self.paddle_left, 0, self.paddle_left_moving * self.paddle_speed)
        self.canvas.move(self.paddle_right, 0, self.paddle_right_moving * self.paddle_speed)

        # Mantener las paletas dentro de los límites
        for paddle in [self.paddle_left, self.paddle_right]:
            paddle_pos = self.canvas.coords(paddle)
            if paddle_pos[1] < 0:
                self.canvas.move(paddle, 0, -paddle_pos[1])
            elif paddle_pos[3] > 600:
                self.canvas.move(paddle, 0, 600 - paddle_pos[3])

    def move_ball(self):
        self.canvas.move(self.ball, self.ball_speed_x, self.ball_speed_y)

    def check_collisions(self):
        ball_pos = self.canvas.coords(self.ball)
        paddle_left_pos = self.canvas.coords(self.paddle_left)
        paddle_right_pos = self.canvas.coords(self.paddle_right)

        # Colisión con los bordes superior e inferior
        if ball_pos[1] <= 0 or ball_pos[3] >= 600:
            self.ball_speed_y = -self.ball_speed_y

        # Colisión con las paletas
        if (self.ball_speed_x < 0 and
            paddle_left_pos[0] <= ball_pos[2] <= paddle_left_pos[2] and
            paddle_left_pos[1] <= ball_pos[3] and ball_pos[1] <= paddle_left_pos[3]):
            self.ball_speed_x = abs(self.ball_speed_x)
            self.ball_speed_y += self.paddle_left_moving  # Añadir efecto basado en el movimiento de la paleta

        elif (self.ball_speed_x > 0 and
              paddle_right_pos[0] <= ball_pos[2] <= paddle_right_pos[2] and
              paddle_right_pos[1] <= ball_pos[3] and ball_pos[1] <= paddle_right_pos[3]):
            self.ball_speed_x = -abs(self.ball_speed_x)
            self.ball_speed_y += self.paddle_right_moving  # Añadir efecto basado en el movimiento de la paleta

        # Limitar la velocidad vertical de la pelota
        self.ball_speed_y = max(min(self.ball_speed_y, 10), -10)

        # Anotar puntos
        if ball_pos[0] <= 0:
            self.score_right += 1
            self.check_win()
            self.reset_ball()
        elif ball_pos[2] >= 800:
            self.score_left += 1
            self.check_win()
            self.reset_ball()

        self.canvas.itemconfig(self.score_text, text=f"{self.score_left} - {self.score_right}")

    def reset_ball(self):
        self.canvas.coords(self.ball, 390, 290, 410, 310)
        self.ball_speed_x = 5 * random.choice([-1, 1])
        self.ball_speed_y = 5 * random.choice([-1, 1])

    def check_win(self):
        if self.score_left >= 5:
            self.game_over("¡Izquierdo Gana!")
        elif self.score_right >= 5:
            self.game_over("¡Derecho Gana!")

    def game_over(self, message):
        self.game_running = False
        self.canvas.create_rectangle(200, 200, 600, 400, fill="black", outline="white")
        self.canvas.create_text(400, 260, text=message, fill="white", font=("Helvetica", 30))
        self.canvas.create_text(400, 340, text="Presiona 'R' Para Reiniciar", fill="white", font=("Helvetica", 20))
        self.bind("<r>", self.restart_game)

    def restart_game(self, event):
        self.canvas.delete("all")
        self.score_left = 0
        self.score_right = 0
        self.start_game()

if __name__ == "__main__":
    game = PongGame()
    game.mainloop()
