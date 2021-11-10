"""
Elementary programming 2021 course project: A Wee Bit Miffed Ducks.
A game where you shoot ducks at objects.
"""
import math
import sweeperlib
import json


WIN_WIDTH = 1280
WIN_HEIGHT = 720
BG_COLOR = (200, 255, 255, 255)
GRAVITATIONAL_ACCEL = 1.5
LAUNCH_X = 100
LAUNCH_Y = 100
FORCE_FACTOR = 0.4


game = {
    "x": LAUNCH_X,
    "y": LAUNCH_Y,
    "w": 40,
    "h": 40,
    "angle": 0,
    "force": 0,
    "x_velocity": 0,
    "y_velocity": 0,
    "flight": False,
    "mouse_down": False,
    "level_data": None,
    "level": 0,
    "boxes": [],
    "ducks": 5,
    "next_level": "level1.json"
}


def order(box):
    """
    Used to sort the list of boxes according to their height measured from the top of the box
    """
    return box['y'] + box['h']


def drop(boxes):
    """
    Drops rectangular objects that are given as a list. Each object is to be
    defined as a dictionary with x and y coordinates, width, height, and falling
    velocity. Drops boxes for one time unit.
    """
    boxes.sort(key=order)
    try:
        boxes[0]['initial_height']
    except KeyError:
        for i in range(len(boxes)):
            boxes[i]['initial_height'] = boxes[i]['y'] + boxes[i]['h']  
    for i in range(len(boxes)):
        if boxes[i]['y'] <= 0:
            boxes[i]['y'] = 0
            boxes[i]['vy'] = 0
            continue
         
        allowFalling = True
        for j in range(len(boxes)):
            if i == j:
                continue
            if boxes[i]['initial_height'] < boxes[j]['initial_height']:
                continue
            if checkOverlaps(boxes[i], boxes[j]):
                boxes[i]['y'] = boxes[j]['y'] + boxes[j]['h']
                boxes[i]['vy'] = 0
                allowFalling = False      

        if allowFalling:
            boxes[i]['vy'] += GRAVITATIONAL_ACCEL
            boxes[i]['y'] -= boxes[i]['vy']


def checkOverlaps(box, other):
    """
    Checks wether the box is overlapping the other box.
    The other box should be lower than the box.
    """
    # Check if the other box's upper left corner is inside the box
    if (box['x'] <= other['x'] <= box['x'] + box['w'] and 
            box['y'] <= other['y'] + other['h'] <= box['y'] + box['h']):
        return True
    # Check if the other box's upper right corner is inside the box
    elif (box['x'] <= other['x'] + other['w'] <= box['x'] + box['w'] and 
            box['y'] <= other['y'] + other['h'] <= box['y'] + box['h']):
        return True
    # Check if the other box's lower left corner is inside the box
    elif (box['x'] <= other['x'] <= box['x'] + box['w'] and 
            box['y'] <= other['y'] <= box['y'] + box['h']):
        return True
    # Check if the other box's lower right corner is inside the box
    elif (box['x'] <= other['x'] + other['w'] <= box['x'] + box['w'] and 
            box['y'] <= other['y'] <= box['y'] + box['h']):
        return True
    # Check if the box goes on top of the other box through the bottom of the other box
    elif (other['x'] <= box['x'] <= other['x'] + other['w'] and
            other['x'] <= box['x'] + box['w'] <= other['x'] + other['w'] and
            other['y'] <= box['y'] + box['h'] <= other['y'] + other['h']):
        return True    
    # Check if the box goes on top of the other box through the top of the other box
    elif (other['x'] <= box['x'] <= other['x'] + other['w'] and
            other['x'] <= box['x'] + box['w'] <= other['x'] + other['w'] and
            other['y'] <= box['y'] <= other['y'] + other['h']):
        return True
    # Check if the box goes on top of the other box through the left side of the other box
    elif (other['y'] <= box['y'] <= other['y'] + other['h'] and
            other['y'] <= box['y'] + box['h'] <= other['y'] + other['h'] and
            other['x'] <= box['x'] + box['w'] <= other['x'] + other['w']):
        return True
    # Check if the box goes on top of the other box through the right side of the other box
    elif (other['y'] <= box['y'] <= other['y'] + other['h'] and
            other['y'] <= box['y'] + box['h'] <= other['y'] + other['h'] and
            other['x'] <= box['x'] <= other['x'] + other['w']):
        return True
    else:
        return False


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


def update(elapsed):
    """
    This is called 60 times/second.
    """
    if game['level'] > 0:
        drop(game['boxes'])
    if game["flight"]:
        game["x"] += game["x_velocity"]
        game["y"] += game["y_velocity"]
        game["y_velocity"] -= GRAVITATIONAL_ACCEL
        if game["y"] <= 0:
            game["ducks"] -= 1
            initial_state()
        for i in range(len(game['boxes'])):
            if checkOverlaps(game, game['boxes'][i]):
                if game['boxes'][i]['type'] == "target":
                    game['boxes'].remove(game['boxes'][i])
                    # TODO: Check if there are any targets left. If not, proceed to next level.
                    initial_state()
                    break
                elif game['boxes'][i]['type'] == "obstacle":
                    game['ducks'] -= 1 # TODO: Might implement bouncing off an obstacle instead of this if I have time.
                    initial_state()
                    break
        if game["ducks"] == 0:
            load_level()


def load_level():
    """
    Function that loads the current level.
    """
    game['boxes'] = game['level_data']['boxes'].copy()
    game['ducks'] = game['level_data']['ducks']  


def draw():
    """
    This function handles interface's and objects drawing.
    You do NOT need to modify this.
    """
    sweeperlib.clear_window()
    sweeperlib.draw_background()
    sweeperlib.begin_sprite_draw()
    if game["level"] == 0:
        sweeperlib.draw_text("Play levels: P", 10, 500)
        sweeperlib.draw_text("Play random levels: R", 10, 450)
        sweeperlib.draw_text("Quit: Q", 10, 400)
    if game["level"] == 1:
        sweeperlib.prepare_sprite("duck", game["x"], game["y"])
        sweeperlib.prepare_sprite("sling", LAUNCH_X - 20, 0)
        for i in range(len(game['boxes'])):
            if game["boxes"][i]['type'] == "target":
                sweeperlib.prepare_sprite("x", game['boxes'][i]['x'], game['boxes'][i]['y'])
            elif game["boxes"][i]['type'] == "obstacle":
                sweeperlib.prepare_sprite(" ", game['boxes'][i]['x'], game['boxes'][i]['y'])
        sweeperlib.draw_sprites()
        sweeperlib.draw_text("Q: Quit  | R: Reset |  ←/→: Set angle |  ↑/↓: Set Force  |  Space: Launch | M: Menu", 10, WIN_HEIGHT - 40, size=20)
        sweeperlib.draw_text("Angle: {:.0f}°\tForce: {:.0f}\tDucks: {}".format(game["angle"], game["force"], game["ducks"]), 10, WIN_HEIGHT - 80, size=20)
        # TODO: Make sure the player knows the current level. Also make the texts better looking and possibly leave the instructions to the main menu only.


def mouse_release_handler(x, y, button, modifiers):
    """
    If the player is using mouse controls, this function is called when a mouse button is released.
    The function determines the angle and the force with which the duck will be launched and launches it.
    """
    if not game["flight"] and game["level"] > 0:
        game["mouse_down"] = False
        game["angle"] = set_angle()
        game["force"] = math.sqrt(pow(game["x"] - LAUNCH_X, 2) + pow(game["y"] - LAUNCH_Y, 2)) * FORCE_FACTOR
        launch()


def set_angle():
    """
    Sets the launch angle if player is using mouse controls.
    """
    x_distance = LAUNCH_X - game["x"]
    y_distance = LAUNCH_Y - game["y"]
    return math.degrees(math.atan2(y_distance, x_distance))


def handle_drag(mouse_x, mouse_y, dx, dy, mouse_button, modifier_keys):
    """
    This function is called when the mouse is moved while one of its buttons is
    pressed down. Moves a box on the screen the same amount as the cursor moved.
    """
    if not game["flight"] and game["level"] > 0:
        game["mouse_down"] = True
        game["x"] += dx
        # TODO: Use the functions in h3: duck_assignment_inner_circle.py to restrict the drag into a circle
        if game['x'] <= 0:
            game['x'] = 0
        game["y"] += dy
        if game['y'] <= 0:
            game['y'] = 0
        game["angle"] = set_angle()
        game["force"] = math.sqrt(pow(game["x"] - LAUNCH_X, 2) + pow(game["y"] - LAUNCH_Y, 2)) * FORCE_FACTOR


def keypress(symbol, modifiers):
    """
    This function handles keyboard input.
    """
    key = sweeperlib.pyglet.window.key

    if symbol == key.Q:
        sweeperlib.close()

    if symbol == key.M:
        game["level"] = 0

    # Menu keys
    if game["level"] == 0:
        if symbol == key.P:
            game["level"] = 1
            with open("level1.json") as file:
                level = json.load(file)
                game["level_data"] = level.copy()
                game['boxes'] = level['boxes'].copy()
                game["ducks"] = level["ducks"]
                game['next_level'] = level["next_level"]
        if symbol == key.R:
            print("Available soon...")

    # Game keys
    if game["level"] > 0:
        if symbol == key.RIGHT:
            game["angle"] -= 10
            if game["angle"] < 0:
                game["angle"] = 350
        elif symbol == key.LEFT:
            game["angle"] += 10
            if game["angle"] > 350:
                game["angle"] = 0

        if symbol == key.UP:
            if game["force"] < 50:
                game["force"] += 5
        elif symbol == key.DOWN:
            if game["force"] >= 5:
                game["force"] -= 5
            else:
                game["force"] = 0

        if symbol == key.SPACE:
            launch()


if __name__ == "__main__":

    sweeperlib.load_sprites("sprites")
    sweeperlib.load_duck("sprites")
    sweeperlib.create_window(width=WIN_WIDTH, height=WIN_HEIGHT, bg_color=BG_COLOR)
    sweeperlib.set_draw_handler(draw)
    sweeperlib.set_release_handler(mouse_release_handler)
    sweeperlib.set_drag_handler(handle_drag)
    sweeperlib.set_keyboard_handler(keypress)
    sweeperlib.set_interval_handler(update, interval=1/60)
    sweeperlib.start()
