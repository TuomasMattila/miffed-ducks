"""
Elementary programming 2021 course project: A Wee Bit Miffed Ducks.
A game where you shoot ducks at objects.
"""
import math
import sweeperlib
import json
import random
import pyglet


WIN_WIDTH = 1280
WIN_HEIGHT = 720
BG_COLOR = (200, 255, 255, 255)
GRAVITATIONAL_ACCEL = 1.5
LAUNCH_X = 100
LAUNCH_Y = 100
DRAG_RADIUS = 100
FORCE_FACTOR = 0.5
ELASTICITY = 0.5

box_breaking_sound = pyglet.media.load("box_breaking_sound.wav", streaming=False)

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
    "level": "menu",
    "boxes": [],
    "ducks": 5,
    "next_level": None,
    "time": 0.0,
    "random_levels_passed": 0,
    "used_ducks": []
}

animation = {
    "animation_time": 0.0,
    "frame": "duck",
    "points": []
}


def order(box):
    """
    Used to sort the list of boxes according to their height measured from the top of the box
    """
    return box["y"] + box["h"]


def create_boxes(quantity):
    """
    Creates a speficied number of boxes with random positions inside the specified
    area. Boxes are represented as dictionaries with the following keys:
    x: x coordinate of the bottom left corner
    y: y coordinate of the bottom left corner
    w: box width
    h: box height
    vy: falling velocity of the box
    """
    boxlist = []
    for i in range(quantity):
        if i < quantity / 2:
            type = "target"
        else:
            type = "obstacle"
        box = {
            'type': type,
            'x': random.randint(WIN_WIDTH - 400, WIN_WIDTH - 60),
            'y': random.randint(0, WIN_HEIGHT/2),
            'w': 40,
            'h': 40,
            'vy': 0
        }
        boxlist.append(box)
        boxlist.sort(key=order)

    return boxlist


def drop(boxes):
    """
    Drops rectangular objects that are given as a list. Each object is to be
    defined as a dictionary with x and y coordinates, width, height, and falling
    velocity. Drops boxes for one time unit.
    """
    boxes.sort(key=order)
    try:
        boxes[0]["initial_height"]
    except KeyError:
        for i in range(len(boxes)):
            boxes[i]["initial_height"] = boxes[i]["y"] + boxes[i]["h"]  
    for i in range(len(boxes)):
        if boxes[i]["y"] <= 0:
            boxes[i]["y"] = 0
            boxes[i]["vy"] = 0
            continue
         
        allowFalling = True
        for j in range(len(boxes)):
            if i == j:
                continue
            if boxes[i]["initial_height"] < boxes[j]["initial_height"]:
                continue
            if is_overlapping(boxes[i], boxes[j]):
                boxes[i]["y"] = boxes[j]["y"] + boxes[j]["h"]
                boxes[i]["vy"] = 0
                allowFalling = False      

        if allowFalling:
            boxes[i]["vy"] += GRAVITATIONAL_ACCEL
            boxes[i]["y"] -= boxes[i]["vy"]


def is_overlapping(box, other):
    """
    Checks whether the box is overlapping the other box.
    Returns the direction to which the duck has to bounce from an obstacle.
    """
    # Check if the other box"s upper left corner is inside the box
    if (box["x"] <= other["x"] <= box["x"] + box["w"] and 
            box["y"] <= other["y"] + other["h"] <= box["y"] + box["h"]):
        return "left"
    # Check if the other box"s upper right corner is inside the box
    elif (box["x"] <= other["x"] + other["w"] <= box["x"] + box["w"] and 
            box["y"] <= other["y"] + other["h"] <= box["y"] + box["h"]):
        return "right"
    # Check if the other box"s lower left corner is inside the box
    elif (box["x"] <= other["x"] <= box["x"] + box["w"] and 
            box["y"] <= other["y"] <= box["y"] + box["h"]):
        return "left"
    # Check if the other box"s lower right corner is inside the box
    elif (box["x"] <= other["x"] + other["w"] <= box["x"] + box["w"] and 
            box["y"] <= other["y"] <= box["y"] + box["h"]):
        return "right"
    # Check if the box goes on top of the other box through the bottom of the other box
    elif (other["x"] <= box["x"] <= other["x"] + other["w"] and
            other["x"] <= box["x"] + box["w"] <= other["x"] + other["w"] and
            other["y"] <= box["y"] + box["h"] <= other["y"] + other["h"]):
        return "down"   
    # Check if the box goes on top of the other box through the top of the other box
    elif (other["x"] <= box["x"] <= other["x"] + other["w"] and
            other["x"] <= box["x"] + box["w"] <= other["x"] + other["w"] and
            other["y"] <= box["y"] <= other["y"] + other["h"]):
        return "up"
    # Check if the box goes on top of the other box through the left side of the other box
    elif (other["y"] <= box["y"] <= other["y"] + other["h"] and
            other["y"] <= box["y"] + box["h"] <= other["y"] + other["h"] and
            other["x"] <= box["x"] + box["w"] <= other["x"] + other["w"]):
        return "left"
    # Check if the box goes on top of the other box through the right side of the other box
    elif (other["y"] <= box["y"] <= other["y"] + other["h"] and
            other["y"] <= box["y"] + box["h"] <= other["y"] + other["h"] and
            other["x"] <= box["x"] <= other["x"] + other["w"]):
        return "right"
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
    if game["ducks"] == 0:
        if game["level"].endswith(".json"):
            load_level(game["level"])
        else:
            game["level"] = "lose"


def launch():
    """
    Launches a duck and calculates its starting velocity. Stores x and y velocity
    components to the game dictionary.
    """
    if not game["flight"]:
        game["x_velocity"] = game["force"] * math.cos(math.radians(game["angle"]))
        game["y_velocity"] = game["force"] * math.sin(math.radians(game["angle"]))
        game["flight"] = True
        game["ducks"] -= 1
        animation["points"].clear()


def update(elapsed):
    """
    This is called 60 times/second.
    """
    game["time"] += elapsed
    if game["level"].startswith("level"):
        drop(game["boxes"])
        drop_ducks(game["used_ducks"])
    if game["flight"]:
        animation["points"].append({"x": game["x"] + 20, "y": game["y"] + 20})
        # TODO: Before actually changing position, we should check if the duck is about to go through a box
        game["x"] += game["x_velocity"]
        game["y"] += game["y_velocity"]
        game["y_velocity"] -= GRAVITATIONAL_ACCEL
        if game["y"] <= 0:
            game["used_ducks"].append({
                "x": game["x"],
                "y": game["y"],
                "vy": 0
            })
            initial_state()
        for i in range(len(game["boxes"])):
            overlap = is_overlapping(game, game["boxes"][i])
            if overlap:
                if game["boxes"][i]["type"] == "target":
                    game["boxes"].remove(game["boxes"][i])
                    box_breaking_sound.play()
                    if not targets_remaining(game["boxes"]):
                        initial_state()
                        load_level(game["next_level"])
                    break
                elif game["boxes"][i]["type"] == "obstacle":
                    bounce(game["boxes"][i], overlap)
                    # TODO: Might implement bouncing off an obstacle instead of this if I have time.
                    #game["used_ducks"].append({
                    #    "x": game["x"],
                    #    "y": game["y"],
                    #    "vy": 0
                    #})
                    #initial_state()
                    break


def bounce(obstacle, direction):
    # TODO: First, find out if there is a box on top of the obstacle. If there is, do not bounce up from this obstacle.
    do_not_bounce_up = False
    print("Duck number", game["ducks"] + 1)
    if direction == "left":
        for box in game["boxes"]:
            if (box["y"] == obstacle["y"] + obstacle["h"] and
                box["x"] <= obstacle["x"] and
                obstacle["x"] <= box["x"] + box["w"] <= obstacle["x"] + obstacle["w"]):
                    do_not_bounce_up = True
        print("Left", do_not_bounce_up)
        if obstacle["x"] <= game["x"] + game["w"] / 2 and not do_not_bounce_up:
            game["y"] = obstacle["y"] + obstacle["h"]
            game["y_velocity"] = game["y_velocity"] * -ELASTICITY
        else:
            game["x"] = obstacle["x"] - obstacle["w"]
            game["x_velocity"] = game["x_velocity"] * -ELASTICITY
    elif direction == "right":
        for box in game["boxes"]:
            if (box["y"] == obstacle["y"] + obstacle["h"] and
                box["x"] + box["w"] >= obstacle["x"] + obstacle["w"] and
                obstacle["x"] <= box["x"] <= obstacle["x"] + obstacle["w"]):
                    do_not_bounce_up = True
        print("Right", do_not_bounce_up)
        if obstacle["x"] + obstacle["w"] >= game["x"] + game["w"] / 2 and not do_not_bounce_up:
            game["y"] = obstacle["y"] + obstacle["h"]
            game["y_velocity"] = game["y_velocity"] * -ELASTICITY
        else:
            game["x"] = obstacle["x"] + obstacle["w"]
            game["x_velocity"] = game["x_velocity"] * -ELASTICITY
    elif direction == "up":
        print("Up")
        game["y"] = obstacle["y"] + obstacle["h"]
        game["y_velocity"] = game["y_velocity"] * -ELASTICITY
    elif direction == "down":
        print("Down")
        game["y"] = obstacle["y"] - obstacle["h"]
        game["y_velocity"] = game["y_velocity"] * -ELASTICITY


def drop_ducks(ducks):
    """
    Makes used ducks fall down to the ground.
    """
    for duck in ducks:
        if duck["y"] <= 0:
            duck["y"] = 0
            continue
        duck["vy"] -= GRAVITATIONAL_ACCEL
        duck["y"] += duck["vy"]


def targets_remaining(boxes):
    """
    Checks if there are any targets left in the list of boxes.
    """
    for box in boxes:
        if box["type"] == "target":
            return True
    return False


def load_level(level):
    """
    Loads a level.
    """
    game["used_ducks"].clear()
    animation["points"].clear()
    # If the player wins the game
    if level == "win":
        game["level"] = level
    # Normal levels
    elif level.endswith(".json"):
        try:
            with open(level) as file:
                data = json.load(file)
                game["level_data"] = data.copy()
                game["level"] = level
                game["boxes"] = data["boxes"].copy()
                game["ducks"] = data["ducks"]
                game["next_level"] = data["next_level"]
        except IOError:
            print("Failed to load level.")
    # Random levels
    else:
        game["boxes"] = create_boxes(random.randint(5, 10))
        game["level"] = level
        game["ducks"] = len(game["boxes"])
        for c in level:
            if c.isdigit():
                level_number = int(c)
                break
        game["next_level"] = "level{}".format(level_number + 1)
        game["random_levels_passed"] = level_number - 1



def draw():
    """
    This function handles interface's and objects drawing.
    """
    sweeperlib.clear_window()
    sweeperlib.draw_background()
    sweeperlib.begin_sprite_draw()
    if game["level"] == "menu":
        sweeperlib.draw_text("A Wee Bit Miffed Ducks", 40, WIN_HEIGHT - 150, size=40)
        sweeperlib.prepare_sprite("duck", 650, WIN_HEIGHT - 140)
        sweeperlib.draw_text("Play levels: P", 40, 184)
        sweeperlib.draw_text("Play random levels: R", 40, 112)
        sweeperlib.draw_text("Quit: Q", 40, 40)
        sweeperlib.draw_text("Controls:", WIN_WIDTH - 350, 400)
        sweeperlib.draw_text("R: Restart level", WIN_WIDTH - 350, 328)
        sweeperlib.draw_text("←/→: Set angle", WIN_WIDTH - 350, 256)
        sweeperlib.draw_text("↑/↓: Set Force", WIN_WIDTH - 350, 184)
        sweeperlib.draw_text("Space: Launch", WIN_WIDTH - 350, 112)
        sweeperlib.draw_text("M: Menu", WIN_WIDTH - 350, 40)
    if game["level"] == "win":
        sweeperlib.draw_text("You win!", WIN_WIDTH/2 - 100, WIN_HEIGHT/2)
        sweeperlib.draw_text("M: Menu", WIN_WIDTH/2 - 100, WIN_HEIGHT/2 -72)
        sweeperlib.draw_text("Q: Quit", WIN_WIDTH/2 - 100, WIN_HEIGHT/2 -144)
    if game["level"] == "lose":
        sweeperlib.draw_text("You lose!", 40, WIN_HEIGHT/2)
        sweeperlib.draw_text("Levels passed: {}".format(game["random_levels_passed"]), 40, WIN_HEIGHT/2 -72)
        sweeperlib.draw_text("M: Menu", 40, WIN_HEIGHT/2 -144)
        sweeperlib.draw_text("Q: Quit", 40, WIN_HEIGHT/2 -216)        
    if game["level"].startswith("level"):
        # Duck animation         
        if game["flight"]:
            if game["time"] >= animation["animation_time"] + 0.2:
                animation["animation_time"] = game["time"]
                if animation["frame"] == "duck":
                    animation["frame"] = "duck2"
                elif animation["frame"] == "duck2":
                    animation["frame"] = "duck"
            sweeperlib.prepare_sprite(animation["frame"], game["x"], game["y"])
        else:
            sweeperlib.prepare_sprite("duck", game["x"], game["y"])
        sweeperlib.prepare_sprite("sling", LAUNCH_X - 20, 0)
        for i in range(len(game["boxes"])):
            if game["boxes"][i]["type"] == "target":
                sweeperlib.prepare_sprite("target", game["boxes"][i]["x"], game["boxes"][i]["y"])
            elif game["boxes"][i]["type"] == "obstacle":
                sweeperlib.prepare_sprite("obstacle", game["boxes"][i]["x"], game["boxes"][i]["y"])
        sweeperlib.draw_text("Level: {} Angle: {:.0f}° Force: {:.0f} Ducks: {}".format(game["level"].lstrip("level").rstrip(".json"), game["angle"], game["force"], game["ducks"]), 10, WIN_HEIGHT - 40, size=20)
        # TODO: Check that these ducks and points are cleared everytime the level changes etc...
        for duck in game["used_ducks"]:
            sweeperlib.prepare_sprite("duck", duck["x"], duck["y"])
        for point in animation["points"]:
            sweeperlib.draw_text("o", point["x"], point["y"], color=(255, 255, 255, 255), size=10)
    sweeperlib.draw_sprites()


def mouse_release_handler(x, y, button, modifiers):
    """
    If the player is using mouse controls, this function is called when a mouse button is released.
    The function determines the angle and the force with which the duck will be launched and launches it.
    """
    if not game["flight"] and game["level"].startswith("level"):
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
    if not game["flight"] and game["level"].startswith("level"):
        game["mouse_down"] = True
        game["x"] += dx
        game["y"] += dy
        game["x"], game["y"] = clamp_inside_circle(game["x"], game["y"], LAUNCH_X, LAUNCH_Y, DRAG_RADIUS)
        game["angle"] = set_angle()
        game["force"] = math.sqrt(pow(game["x"] - LAUNCH_X, 2) + pow(game["y"] - LAUNCH_Y, 2)) * FORCE_FACTOR


def clamp_inside_circle(x, y, circle_center_x, circle_center_y, radius):
    """
    First the function finds out whether the given 
    point is already inside the circle. If it is, its coordinates 
    are simply returned as they are. However, if the point is outside 
    the circle, it is "pulled" to the circle's perimeter. In 
    doing so, the angle from the circle"s center must be maintained 
    while the distance is set exactly to the circle's radius.
    """
    distance = calculate_distance(x, y, circle_center_x, circle_center_y)
    if distance > radius:
        angle = math.atan(abs(y - circle_center_y) / abs(x - circle_center_x))
        if circle_center_x < x:  
            angle += (math.pi / 2 - angle) * 2
        if circle_center_y < y:
            angle = angle * -1
        ray = distance - radius
        move_x, move_y = convert_to_xy(angle, ray)
        return x + move_x, y + move_y
    else:
        return x, y


def calculate_distance(x1, y1, x2, y2):
    """
    Calculates the distance between two points and returns it.
    """
    return math.sqrt(pow(x2 - x1, 2) + pow(y2 - y1, 2))


def convert_to_xy(angle, ray):
    """
    Converts polar coordinates to cartesian coordinates.
    Note that the angle given as a parameter must be a radian value.
    """
    x = ray * math.cos(angle)
    y = ray * math.sin(angle)
    return x, y


def update_position():
    """
    Updates the duck's position when using arrow keys to adjust angle and force.
    """
    x, y = convert_to_xy(math.radians(game["angle"]), game["force"])
    game["x"] = LAUNCH_X - x * 2 
    game["y"] = LAUNCH_Y - y * 2


def keypress(symbol, modifiers):
    """
    This function handles keyboard input.
    """
    key = sweeperlib.pyglet.window.key

    if symbol == key.Q:
        sweeperlib.close()

    if symbol == key.M:
        initial_state()
        game["level"] = "menu"

    # Menu keys
    if game["level"] == "menu":
        if symbol == key.P:
            load_level("level1.json")
        if symbol == key.R:
            load_level("level1")

    # Game keys
    if game["level"].startswith("level"):
        if symbol == key.R:
            initial_state()
            load_level(game["level"])
    
        if symbol == key.RIGHT:
            game["angle"] -= 5
            if game["angle"] < 0:
                game["angle"] = 350
            update_position()
        elif symbol == key.LEFT:
            game["angle"] += 5
            if game["angle"] > 350:
                game["angle"] = 0
            update_position()

        if symbol == key.UP:
            if game["force"] < 50:
                game["force"] += 5
            update_position()
        elif symbol == key.DOWN:
            if game["force"] >= 5:
                game["force"] -= 5
            else:
                game["force"] = 0
            update_position()

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
