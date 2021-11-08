"""
Elementary programming 2021 course project: A Wee Bit Miffed Ducks.
A game where you shoot ducks at objects.
"""
import math
import sweeperlib


WIN_WIDTH = 1200
WIN_HEIGHT = 600
BG_COLOR = (200, 255, 255, 255)
GRAVITATIONAL_ACCEL = 1.5
LAUNCH_X = 100
LAUNCH_Y = 100
FORCE_FACTOR = 0.5


game = {
    "x": LAUNCH_X,
    "y": LAUNCH_Y,
    "angle": 0,
    "force": 0,
    "x_velocity": 0,
    "y_velocity": 0,
    "flight": False,
    "mouse_down": False
}


def initial_state():
    """
    Puts the game back into its initial state: the duck is put back into the
    launch position, its speed to zero, and its flight state to False.
    """
    game["x"] = LAUNCH_X
    game["y"] = LAUNCH_Y
    game["angle"] = 0
    game["force"] = 0
    game["x_velocity"] = 0
    game["y_velocity"] = 0
    game["flight"] = False


def launch():
    """
    Launches a duck and calculates its starting velocity. Stores x and y velocity
    components to the game dictionary.
    """
    game["x_velocity"] = game["force"] * math.cos(math.radians(game["angle"]))
    game["y_velocity"] = game["force"] * math.sin(math.radians(game["angle"]))
    game["flight"] = True


def flight(elapsed):
    """
    Updates duck's x and y coordinates based on corresponding velocity vectors.
    """
    if game["flight"]:
        game["x"] += game["x_velocity"]
        game["y"] += game["y_velocity"]
        game["y_velocity"] -= GRAVITATIONAL_ACCEL
        if game["y"] <= 0:
            initial_state()


def draw():
    """
    This function handles interface's and objects drawing.
    You do NOT need to modify this.
    """
    sweeperlib.clear_window()
    sweeperlib.draw_background()
    sweeperlib.begin_sprite_draw()
    sweeperlib.prepare_sprite("duck", game["x"], game["y"])
    sweeperlib.prepare_sprite("sling", LAUNCH_X - 20, 0)
    sweeperlib.draw_sprites()
    sweeperlib.draw_text("Level 1 | Q: Quit | R: Random levels", 10, 560, size=20)
    sweeperlib.draw_text("1", 380, 175, size=22)
    sweeperlib.draw_text("2", 830, 225, size=22)
    sweeperlib.draw_text("3", 170, 455, size=22)
    sweeperlib.draw_text("4", 50, 455, size=22)
    sweeperlib.draw_text("5", 700, 455, size=22)


def mouse_release_handler(x, y, button, modifiers):
    if not game["flight"]:
        game["mouse_down"] = False
        game["angle"] = set_angle()
        game["force"] = math.sqrt(pow(game["x"] - LAUNCH_X, 2) + pow(game["y"] - LAUNCH_Y, 2)) * FORCE_FACTOR
        launch()


def set_angle():
    x_distance = LAUNCH_X - game["x"]
    y_distance = LAUNCH_Y - game["y"]
    return math.degrees(math.atan2(y_distance, x_distance))


def handle_drag(mouse_x, mouse_y, dx, dy, mouse_button, modifier_keys):
    """
    This function is called when the mouse is moved while one of its buttons is
    pressed down. Moves a box on the screen the same amount as the cursor moved.
    """
    if not game["flight"]:
        game["mouse_down"] = True
        game["x"] += dx
        if game['x'] < 0:
            game['x'] = 1
        game["y"] += dy
        if game['y'] < 0:
            game['y'] = 1


def keypress(symbol, modifiers):
    """
    This function handles keyboard input.
    You do NOT need to modify this.
    """
    key = sweeperlib.pyglet.window.key

    if symbol == key.Q:
        sweeperlib.close()

    if symbol == key.R:
        print("Not yet implemented")


if __name__ == "__main__":

    sweeperlib.load_sprites("sprites")
    sweeperlib.load_duck("sprites")
    sweeperlib.create_window(width=WIN_WIDTH, height=WIN_HEIGHT, bg_color=BG_COLOR)
    sweeperlib.set_draw_handler(draw)
    sweeperlib.set_release_handler(mouse_release_handler)
    sweeperlib.set_drag_handler(handle_drag)
    sweeperlib.set_keyboard_handler(keypress)
    sweeperlib.set_interval_handler(flight, interval=1/60)
    sweeperlib.start()
