import tkinter as tk
import random

# Constants for game dimensions
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 400
PACMAN_RADIUS = 15
STEP_SIZE = 20

# Colors
BACKGROUND_COLOR = "black"
PACMAN_COLOR = "yellow"
FOOD_COLOR = "red"
WALL_COLOR = "blue"

class PacmanGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Pacman Game")

        self.canvas = tk.Canvas(root, width=WINDOW_WIDTH, height=WINDOW_HEIGHT, bg=BACKGROUND_COLOR)
        self.canvas.pack()

        # Initialize pacman position
        self.pacman_x = WINDOW_WIDTH // 2
        self.pacman_y = WINDOW_HEIGHT // 2

        # Draw pacman
        self.pacman = self.canvas.create_oval(
            self.pacman_x - PACMAN_RADIUS, 
            self.pacman_y - PACMAN_RADIUS, 
            self.pacman_x + PACMAN_RADIUS, 
            self.pacman_y + PACMAN_RADIUS, 
            fill=PACMAN_COLOR
        )

        # Create initial food
        self.food = None
        self.walls = []
        self.create_walls()
        self.create_food()

        # Create walls
        self.walls = []
        self.create_walls()
        self.create_walls()

        # Bind keyboard events
        self.root.bind("<Up>", self.move_up)
        self.root.bind("<Down>", self.move_down)
        self.root.bind("<Left>", self.move_left)
        self.root.bind("<Right>", self.move_right)

    def create_food(self):
        # Generate random coordinates for food
        while True:
            food_x = random.randint(0, WINDOW_WIDTH // STEP_SIZE - 1) * STEP_SIZE + STEP_SIZE // 2
            food_y = random.randint(0, WINDOW_HEIGHT // STEP_SIZE - 1) * STEP_SIZE + STEP_SIZE // 2

            # Ensure food does not spawn inside a wall
            if not any(self.check_collision(food_x, food_y, self.canvas.coords(wall)) for wall in self.walls):
                break

        if self.food:
            self.canvas.delete(self.food)

        # Draw food
        self.food = self.canvas.create_oval(
            food_x - PACMAN_RADIUS // 2,
            food_y - PACMAN_RADIUS // 2,
            food_x + PACMAN_RADIUS // 2,
            food_y + PACMAN_RADIUS // 2,
            fill=FOOD_COLOR
        )

    def create_walls(self):
        # Define wall coordinates (x1, y1, x2, y2)
        wall_coords = [
            (50, 50, 350, 70),
            (50, 150, 200, 170),
            (250, 150, 350, 170),
            (50, 250, 350, 270),
            (150, 350, 250, 370)
        ]

        # Create wall rectangles on the canvas
        for x1, y1, x2, y2 in wall_coords:
            wall = self.canvas.create_rectangle(x1, y1, x2, y2, fill=WALL_COLOR)
            self.walls.append(wall)

    def move_pacman(self, dx, dy):
        # Calculate new position
        new_x = self.pacman_x + dx
        new_y = self.pacman_y + dy

        # Check for wall collisions
        for wall in self.walls:
            wall_coords = self.canvas.coords(wall)
            if self.check_collision(new_x, new_y, wall_coords):
                return  # Do not move if colliding with a wall

        # Update pacman position
        self.pacman_x = new_x
        self.pacman_y = new_y

        # Wrap around boundaries
        if self.pacman_x < 0:
            self.pacman_x = WINDOW_WIDTH
        elif self.pacman_x > WINDOW_WIDTH:
            self.pacman_x = 0

        if self.pacman_y < 0:
            self.pacman_y = WINDOW_HEIGHT
        elif self.pacman_y > WINDOW_HEIGHT:
            self.pacman_y = 0

        # Move the pacman on the canvas
        self.canvas.coords(
            self.pacman,
            self.pacman_x - PACMAN_RADIUS,
            self.pacman_y - PACMAN_RADIUS,
            self.pacman_x + PACMAN_RADIUS,
            self.pacman_y + PACMAN_RADIUS
        )

        # Check for collision with food
        food_coords = self.canvas.coords(self.food)
        if self.check_collision(self.pacman_x, self.pacman_y, food_coords):
            self.create_food()

    def check_collision(self, x, y, coords):
        x1, y1, x2, y2 = coords
        if x1 <= x <= x2 and y1 <= y <= y2:
            return True
        return False

    def move_up(self, event):
        self.move_pacman(0, -STEP_SIZE)

    def move_down(self, event):
        self.move_pacman(0, STEP_SIZE)

    def move_left(self, event):
        self.move_pacman(-STEP_SIZE, 0)

    def move_right(self, event):
        self.move_pacman(STEP_SIZE, 0)

if __name__ == "__main__":
    root = tk.Tk()
    game = PacmanGame(root)
    root.mainloop()
