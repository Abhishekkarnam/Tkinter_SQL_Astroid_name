import tkinter as tk
import random
import sqlite3
import math

# Game constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
ASTEROID_MIN_SIZE = 20
ASTEROID_MAX_SIZE = 50
ASTEROID_SPEED = 5
SHIP_WIDTH = 50
SHIP_HEIGHT = 30
SHIP_SPEED = 20

class AsteroidGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Asteroid Game")

        self.main_frame = tk.Frame(root, bg='black')
        self.main_frame.pack(fill="both", expand=True)

        self.setup_database()
        self.show_main_menu()

    def setup_database(self):
        self.conn = sqlite3.connect('asteroid_game.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS high_scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                score INTEGER
            )
        ''')
        self.conn.commit()

    def show_main_menu(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        title = tk.Label(self.main_frame, text="Asteroid Game", font=("Helvetica", 24), fg="white", bg="black")
        title.pack(pady=20)

        start_button = tk.Button(self.main_frame, text="Start Game", font=("Helvetica", 16), command=self.start_game)
        start_button.pack(pady=10)

        high_scores_button = tk.Button(self.main_frame, text="High Scores", font=("Helvetica", 16), command=self.show_high_scores)
        high_scores_button.pack(pady=10)

    def start_game(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        self.canvas = tk.Canvas(self.main_frame, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, bg='black')
        self.canvas.pack()

        # Improved spaceship shape
        self.ship = self.canvas.create_polygon(
            WINDOW_WIDTH // 2, WINDOW_HEIGHT - SHIP_HEIGHT * 2,
            WINDOW_WIDTH // 2 + SHIP_WIDTH // 2, WINDOW_HEIGHT - SHIP_HEIGHT,
            WINDOW_WIDTH // 2, WINDOW_HEIGHT - SHIP_HEIGHT * 1.5,
            WINDOW_WIDTH // 2 - SHIP_WIDTH // 2, WINDOW_HEIGHT - SHIP_HEIGHT,
            fill='white'
        )

        self.asteroids = []
        self.score = 0

        self.score_label = tk.Label(self.main_frame, text=f"Score: {self.score}", fg="white", bg="black", font=("Helvetica", 16))
        self.score_label.pack()

        self.root.bind('<Left>', self.move_left)
        self.root.bind('<Right>', self.move_right)
        self.root.bind('<Up>', self.move_up)
        self.root.bind('<Down>', self.move_down)

        self.create_asteroid()
        self.game_loop()

    def create_asteroid(self):
        size = random.randint(ASTEROID_MIN_SIZE, ASTEROID_MAX_SIZE)
        x = random.randint(0, WINDOW_WIDTH - size)
        y = 0
        points = self.generate_asteroid_shape(x, y, size)
        asteroid = self.canvas.create_polygon(points, fill='gray')
        self.asteroids.append((asteroid, size, random.randint(-2, 2), random.randint(-2, 2)))
        self.root.after(1000, self.create_asteroid)

    def generate_asteroid_shape(self, x, y, size):
        points = []
        num_points = random.randint(5, 9)
        for i in range(num_points):
            angle = math.radians(i * 360 / num_points)
            length = random.uniform(size * 0.5, size)
            px = x + length * math.cos(angle)
            py = y + length * math.sin(angle)
            points.append(px)
            points.append(py)
        return points

    def move_asteroids(self):
        for i, (asteroid, size, dx, dy) in enumerate(self.asteroids):
            self.canvas.move(asteroid, dx, ASTEROID_SPEED + dy)
            pos = self.canvas.coords(asteroid)
            if pos[1] > WINDOW_HEIGHT:
                self.canvas.delete(asteroid)
                self.asteroids.pop(i)
                self.score += 1
                self.score_label.config(text=f"Score: {self.score}")

    def check_collision(self):
        ship_coords = self.canvas.bbox(self.ship)
        for asteroid, size, _, _ in self.asteroids:
            asteroid_coords = self.canvas.bbox(asteroid)
            if (asteroid_coords[0] < ship_coords[2] and
                asteroid_coords[2] > ship_coords[0] and
                asteroid_coords[1] < ship_coords[3] and
                asteroid_coords[3] > ship_coords[1]):
                self.save_score(self.score)
                self.show_game_over()
                return True
        return False

    def save_score(self, score):
        self.cursor.execute('INSERT INTO high_scores (score) VALUES (?)', (score,))
        self.conn.commit()

    def show_game_over(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        game_over_label = tk.Label(self.main_frame, text="Game Over", font=("Helvetica", 24), fg="red", bg="black")
        game_over_label.pack(pady=20)

        score_label = tk.Label(self.main_frame, text=f"Your Score: {self.score}", font=("Helvetica", 16), fg="white", bg="black")
        score_label.pack(pady=10)

        restart_button = tk.Button(self.main_frame, text="Restart Game", font=("Helvetica", 16), command=self.start_game)
        restart_button.pack(pady=10)

        main_menu_button = tk.Button(self.main_frame, text="Main Menu", font=("Helvetica", 16), command=self.show_main_menu)
        main_menu_button.pack(pady=10)

    def move_left(self, event):
        ship_coords = self.canvas.coords(self.ship)
        if ship_coords[0] > SHIP_SPEED:  # Ensure the ship stays within the left boundary
            self.canvas.move(self.ship, -SHIP_SPEED, 0)

    def move_right(self, event):
        ship_coords = self.canvas.coords(self.ship)
        if ship_coords[0] < WINDOW_WIDTH - SHIP_SPEED:  # Ensure the ship stays within the right boundary
            self.canvas.move(self.ship, SHIP_SPEED, 0)

    def move_up(self, event):
        ship_coords = self.canvas.coords(self.ship)
        if ship_coords[1] > SHIP_SPEED:  # Ensure the ship stays within the top boundary
            self.canvas.move(self.ship, 0, -SHIP_SPEED)

    def move_down(self, event):
        ship_coords = self.canvas.coords(self.ship)
        if ship_coords[1] < WINDOW_HEIGHT - SHIP_SPEED:  # Ensure the ship stays within the bottom boundary
            self.canvas.move(self.ship, 0, SHIP_SPEED)

    def game_loop(self):
        if not self.check_collision():
            self.move_asteroids()
            self.root.after(50, self.game_loop)

    def show_high_scores(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        self.cursor.execute('SELECT * FROM high_scores ORDER BY score DESC LIMIT 5')
        scores = self.cursor.fetchall()
        high_scores_text = "\n".join([f"{idx + 1}. Score: {score[1]}" for idx, score in enumerate(scores)])

        high_scores_label = tk.Label(self.main_frame, text="High Scores", font=("Helvetica", 24), fg="white", bg="black")
        high_scores_label.pack(pady=20)

        scores_label = tk.Label(self.main_frame, text=high_scores_text, font=("Helvetica", 16), fg="white", bg="black")
        scores_label.pack(pady=10)

        main_menu_button = tk.Button(self.main_frame, text="Main Menu", font=("Helvetica", 16), command=self.show_main_menu)
        main_menu_button.pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    game = AsteroidGame(root)
    root.mainloop()
