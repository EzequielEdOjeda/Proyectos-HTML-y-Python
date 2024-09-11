import tkinter as tk
import random
import math

class ShootingGame(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Shooting Game")
        self.geometry("800x600")
        self.resizable(False, False)  # Evitar maximización
        self.center_window()
        
        # Pantalla de presentación
        self.start_screen = tk.Frame(self)
        self.start_screen.pack(fill="both", expand=True)
        self.start_label = tk.Label(self.start_screen, text="Shooting Game", font=("Helvetica", 32))
        self.start_label.pack(pady=100)
        self.start_button = tk.Button(self.start_screen, text="Empezar", font=("Helvetica", 24), command=self.start_game, bg="lightblue", relief="groove", borderwidth=5)
        self.start_button.pack(pady=20)
        self.quit_button = tk.Button(self.start_screen, text="Salir", font=("Helvetica", 24), command=self.quit, bg="lightcoral", relief="groove", borderwidth=5)
        self.quit_button.pack(pady=20)
        
        # Pantalla del juego
        self.canvas = tk.Canvas(self, width=800, height=600, bg="white")
        self.triangle = None
        self.angle = 0
        self.score = 0
        self.score_text = None
        self.targets = []
        self.bullets = []
        self.game_running = True
        self.restart_button = None
        
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
        self.triangle = self.draw_triangle(400, 300, self.angle)
        self.score_text = self.canvas.create_text(50, 20, text="Puntos: 0", font=("Helvetica", 16), fill="orange")
        self.bind("<Left>", self.rotate_left)
        self.bind("<Right>", self.rotate_right)
        self.bind("<space>", self.shoot)
        self.game_running = True
        self.update_game()
        
    def create_target(self):
        x, y = random.choice([0, 800]), random.randint(0, 600)
        if x == 0:
            y = random.choice([0, 600])
        if random.choice([True, False]):
            target = self.canvas.create_oval(x, y, x + 20, y + 20, fill="red")
            self.targets.append((target, "circle", random.uniform(3, 6)))
        else:
            target = self.canvas.create_rectangle(x, y, x + 20, y + 20, fill="green")
            self.targets.append((target, "square", random.uniform(3, 6)))
    
    def rotate_left(self, event):
        if self.game_running:
            self.angle -= 10
            self.canvas.delete("triangle")  # Eliminar todos los dibujos relacionados con el triángulo
            self.triangle = self.draw_triangle(400, 300, self.angle)
        
    def rotate_right(self, event):
        if self.game_running:
            self.angle += 10
            self.canvas.delete("triangle")  # Eliminar todos los dibujos relacionados con el triángulo
            self.triangle = self.draw_triangle(400, 300, self.angle)
        
    def draw_triangle(self, x, y, angle):
        angle_rad = math.radians(angle)
        points = [
            (x + 20 * math.cos(angle_rad), y - 20 * math.sin(angle_rad)),
            (x + 20 * math.cos(angle_rad + 2 * math.pi / 3), y - 20 * math.sin(angle_rad + 2 * math.pi / 3)),
            (x + 20 * math.cos(angle_rad - 2 * math.pi / 3), y - 20 * math.sin(angle_rad - 2 * math.pi / 3))
        ]
        center_point = (x + 10 * math.cos(angle_rad), y - 10 * math.sin(angle_rad))
        self.canvas.create_polygon(points, fill="blue", outline="black", width=2, tags="triangle")
        return self.canvas.create_line(x, y, center_point[0], center_point[1], fill="black", width=2, tags="triangle")
        
    def shoot(self, event):
        if self.game_running:
            angle_rad = math.radians(self.angle)
            bullet = self.canvas.create_oval(395, 295, 405, 305, fill="black")
            self.bullets.append((bullet, angle_rad))
        
    def update_game(self):
        if self.game_running:
            self.update_bullets()
            self.move_targets()
            self.check_collisions()
            if random.randint(1, 5) == 1:  # Creación más rápida de obstáculos
                self.create_target()
            self.after(50, self.update_game)
        
    def update_bullets(self):
        for bullet, angle in self.bullets[:]:
            self.canvas.move(bullet, 10 * math.cos(angle), -10 * math.sin(angle))
            bullet_coords = self.canvas.coords(bullet)
            if not (0 <= bullet_coords[0] <= 800 and 0 <= bullet_coords[1] <= 600):
                self.canvas.delete(bullet)
                self.bullets.remove((bullet, angle))
            
    def move_targets(self):
        for target, target_type, speed in self.targets[:]:
            target_coords = self.canvas.coords(target)
            target_x = (target_coords[0] + target_coords[2]) / 2
            target_y = (target_coords[1] + target_coords[3]) / 2
            angle_to_center = math.atan2(300 - target_y, 400 - target_x)
            self.canvas.move(target, speed * math.cos(angle_to_center), speed * math.sin(angle_to_center))
            
    def check_collisions(self):
        bullets_to_remove = []
        targets_to_remove = []
        
        for bullet, _ in self.bullets[:]:
            bullet_coords = self.canvas.coords(bullet)
            for target, target_type, _ in self.targets[:]:
                target_coords = self.canvas.coords(target)
                if self.is_collision(bullet_coords, target_coords):
                    bullets_to_remove.append(bullet)
                    targets_to_remove.append((target, target_type))
                    self.update_score(target_type)
        
        for bullet in bullets_to_remove:
            self.canvas.delete(bullet)
            self.bullets = [b for b in self.bullets if b[0] != bullet]
            
        for target, target_type in targets_to_remove:
            self.canvas.delete(target)
            self.targets = [t for t in self.targets if t[0] != target]
        
        for target, target_type, _ in self.targets[:]:
            target_coords = self.canvas.coords(target)
            if self.is_collision_with_triangle(target_coords):
                self.game_over()
    
    def is_collision(self, bullet_coords, target_coords):
        bullet_x = (bullet_coords[0] + bullet_coords[2]) / 2
        bullet_y = (bullet_coords[1] + bullet_coords[3]) / 2
        target_x = (target_coords[0] + target_coords[2]) / 2
        target_y = (target_coords[1] + target_coords[3]) / 2
        return math.hypot(target_x - bullet_x, target_y - bullet_y) < 15
    
    def is_collision_with_triangle(self, target_coords):
        target_x = (target_coords[0] + target_coords[2]) / 2
        target_y = (target_coords[1] + target_coords[3]) / 2
        return math.hypot(400 - target_x, 300 - target_y) < 20
    
    def update_score(self, target_type):
        if target_type == "circle":
            self.score += 1
        else:
            self.score += 5
        self.canvas.itemconfigure(self.score_text, text=f"Puntos: {self.score}")
    
    def game_over(self):
        self.game_running = False
        self.canvas.create_text(400, 300, text="GAME OVER", fill="red", font=("Helvetica", 30))
        self.restart_button = tk.Button(self, text="Volver a Jugar", font=("Helvetica", 20), command=self.restart_game, bg="lightgreen", relief="groove", borderwidth=5)
        self.canvas.create_window(400, 370, window=self.restart_button)
    
    def restart_game(self):
        self.canvas.pack_forget()
        self.restart_button.destroy()
        self.targets.clear()
        self.bullets.clear()
        self.canvas.delete("all")
        self.score = 0
        self.start_game()

if __name__ == "__main__":
    game = ShootingGame()
    game.mainloop()
