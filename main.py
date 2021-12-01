"""
A Wee Bit Miffed Ducks: A game where you shoot ducks at objects.
Elementary programming 2021 course project.
"""
import math
import sweeperlib
import json
import random
import pyglet


WIN_WIDTH = 1920
WIN_HEIGHT = 1080
GROUND_LEVEL = 80
BG_COLOR = (200, 255, 255, 255)
GRAVITATIONAL_ACCEL = 1.5
LAUNCH_X = 100
LAUNCH_Y = 100 + GROUND_LEVEL
DRAG_RADIUS = 100
FORCE_FACTOR = 0.6
ELASTICITY = 0.5

box_breaking_sound = pyglet.media.load("box_breaking_sound.wav", streaming=False)
duck_sound = pyglet.media.load("duck_sound.wav", streaming=False)
bounce_sound = pyglet.media.load("bounce_sound.wav", streaming=False)

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
    "used_ducks": [],
    "fullscreen": True,
    "grid": False,  # TODO: Delete later
    "slow_duck": 0
}

animation = {
    "animation_time": 0.0,
    "frame": "duck"
}


############################## Math functions ##############################


def calculate_distance(x1, y1, x2, y2):
    """
    Calculates the distance between two points and returns it.
    """
    return math.sqrt(pow(x2 - x1, 2) + pow(y2 - y1, 2))


def calculate_angle(x1, y1, x2, y2):
    """
    Returns the angle between two points, in radians.
    """
    x_distance = x2 - x1
    y_distance = y2 - y1
    return math.atan2(y_distance, x_distance)


def convert_to_xy(angle, ray):
    """
    Converts polar coordinates to cartesian coordinates.
    Note that the angle given as a parameter must be a radian value.
    """
    x = ray * math.cos(angle)
    y = ray * math.sin(angle)
    return x, y


def clamp_inside_circle(x, y, circle_center_x, circle_center_y, radius):
    """
    First the function finds out whether the given
    point is already inside the circle. If it is, its coordinates
    are simply returned as they are. However, if the point is outside
    the circle, it is "pulled" to the circle's perimeter. In
    doing so, the angle from the circle's center must be maintained
    while the distance is set exactly to the circle's radius.
    """
    distance = calculate_distance(x, y, circle_center_x, circle_center_y)
    if distance > radius:
        angle = calculate_angle(x, y, circle_center_x, circle_center_y)
        ray = distance - radius
        move_x, move_y = convert_to_xy(angle, ray)
        return x + move_x, y + move_y
    else:
        return x, y


############################## Game related auxiliary functions ##############################


def order_by_height(box):
    """
    Used to sort the list of boxes according to their height measured from the top of the box.
    """
    return box["y"] + box["h"]


def order_by_distance(collision):
    """
    Used to sort the list of colliding boxes according to their distance from the duck.
    """
    return calculate_distance(game["x"], game["y"], collision["x"], collision["y"])


def update_position():
    """
    Updates the duck's position when using arrow keys to adjust angle and force.
    """
    x, y = convert_to_xy(math.radians(game["angle"]), game["force"])
    game["x"] = LAUNCH_X - x
    game["y"] = LAUNCH_Y - y


def targets_remaining():
    """
    Checks if there are any targets left in the list of boxes.
    """
    for box in game["boxes"]:
        if box["type"] == "target":
            return True
    return False


def is_inside_area(min_x, max_x, min_y, max_y, object):
    """
    Checks whether the object is inside the area defined by the minimum and maximum x and y values.
    """
    if max_y < object["y"] or min_y > object["y"] + object["h"]:
        return False
    elif max_x < object["x"] or min_x > object["x"] + object["w"]:
        return False
    else:
        return True


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
    Launches a duck and calculates its starting velocity. Stores x- and y-velocity
    components to the game dictionary.
    """
    if not game["flight"]:
        game["x_velocity"] = game["force"] * FORCE_FACTOR * math.cos(math.radians(game["angle"]))
        game["y_velocity"] = game["force"] * FORCE_FACTOR * math.sin(math.radians(game["angle"]))
        game["flight"] = True
        game["ducks"] -= 1
        duck_sound.play()


def create_boxes(quantity):
    """
    Creates a speficied number of boxes with random positions inside the specified
    area. Boxes are represented as dictionaries with the following keys:
    type: either "target" or "obstacle"
    x: x coordinate of the bottom left corner
    y: y coordinate of the bottom left corner
    w: box width
    h: box height
    vy: falling velocity of the box
    To make the random levels always possible to pass, the target boxes are
    spawned higher than obstacles.
    """
    boxlist = []
    for i in range(quantity):
        if i < quantity / 2:
            box = {
                "type": "target",
                "x": random.randint(WIN_WIDTH - 600, WIN_WIDTH - 60),
                "y": random.randint(340, 600),
                "w": 40,
                "h": 40,
                "vy": 0
            }
        else:
            box = {
                "type": "obstacle",
                "x": random.randint(WIN_WIDTH - 600, WIN_WIDTH - 60),
                "y": random.randint(80, 300),
                "w": 40,
                "h": 40,
                "vy": 0
            }
        boxlist.append(box)
        boxlist.sort(key=order_by_height)

    return boxlist


def drop(boxes):
    """
    Drops rectangular objects that are given as a list. Each object is to be
    defined as a dictionary with x and y coordinates, width, height, and falling
    velocity. Drops boxes for one time unit.
    Parameters:
    - boxes: A list of dictionaries that describe boxes.
             The dictionaries must have x, y, w, h and vy values.
    """
    boxes.sort(key=order_by_height)
    try:
        boxes[0]["initial_height"]
    except KeyError:
        for box in game["boxes"]:
            box["initial_height"] = box["y"] + box["h"]
    for box in game["boxes"]:
        if box["y"] <= GROUND_LEVEL:
            box["y"] = GROUND_LEVEL
            box["vy"] = 0
            continue

        allow_falling = True
        for other in game["boxes"]:
            if box == other:
                continue
            if box["initial_height"] < other["initial_height"]:
                continue
            elif box["initial_height"] == other["initial_height"]:
                box["initial_height"] += 1
            if is_inside_area(box["x"], box["x"] + box["w"], box["y"], box["y"] + box["h"], other):
                if not box["x"] == other["x"] + other["w"] and not box["x"] + box["w"] == other["x"]:
                    box["y"] = other["y"] + other["h"]
                    box["vy"] = 0
                    allow_falling = False

        if allow_falling:
            box["vy"] += GRAVITATIONAL_ACCEL
            box["y"] -= box["vy"]


def drop_ducks(ducks):
    """
    Makes used ducks fall down and destroy targets.
    Parameters:
    - ducks: A list of dictionaries that describe ducks.
             The dictionaries must have x, y, w, h and vy values.
    """
    for duck in ducks:
        destroy_targets(duck)
        if duck["y"] <= GROUND_LEVEL:
            duck["y"] = GROUND_LEVEL
            continue
        allow_falling = True
        for box in game["boxes"]:
            if is_inside_area(duck["x"], duck["x"] + duck["w"], duck["y"], duck["y"] + duck["h"], box):
                duck["y"] = box["y"] + box["h"]
                duck["vy"] == 0
                allow_falling = False
        if allow_falling:
            duck["vy"] -= GRAVITATIONAL_ACCEL
            duck["y"] += duck["vy"]


def destroy_targets(duck):
    """
    Destroys targets that are overlapping the duck.
    Parameters:
    - duck: A dictionary describing a duck.
            Has to have x, y, w and h values.
    """
    new_box_list = []
    for box in game["boxes"]:
        if is_inside_area(duck["x"], duck["x"] + duck["w"], duck["y"], duck["y"] + duck["h"], box):
            if box["type"] == "target":
                box_breaking_sound.play()
                continue
            else:
                new_box_list.append(box)
        else:
            new_box_list.append(box)
    game["boxes"] = new_box_list


def predict_collisions():
    """
    Checks whether the duck collides or is about to collide with boxes.
    If the duck collides with an obstacle, it bounces off it if the circumstances are right.
    """
    collisions = []
    bounce_from = None

    # Duck's direction: down and right
    if game["y_velocity"] <= 0 and game["x_velocity"] >= 0:
        for box in game["boxes"]:
            if is_inside_area(game["x"], game["x"] + game["x_velocity"] + game["w"], game["y"] + game["y_velocity"], game["y"] + game["h"], box):
                collisions.append(box)
    # Duck's direction: down and left
    elif game["y_velocity"] <= 0 and game["x_velocity"] <= 0:
        for box in game["boxes"]:
            if is_inside_area(game["x"] + game["x_velocity"], game["x"] + game["w"], game["y"] + game["y_velocity"], game["y"] + game["h"], box):
                collisions.append(box)
    # Duck's direction: up and right
    elif game["y_velocity"] >= 0 and game["x_velocity"] >= 0:
        for box in game["boxes"]:
            if is_inside_area(game["x"], game["x"] + game["x_velocity"] + game["w"], game["y"], game["y"] + game["y_velocity"] + game["h"], box):
                collisions.append(box)
    # Duck's direction: up and left
    elif game["y_velocity"] >= 0 and game["x_velocity"] <= 0:
        for box in game["boxes"]:
            if is_inside_area(game["x"] + game["x_velocity"], game["x"] + game["w"], game["y"], game["y"] + game["y_velocity"] + game["h"], box):
                collisions.append(box)

    if collisions:
        collisions.sort(key=order_by_distance)
        # Find the closest box and delete target boxes
        for collision in collisions:
            if collision["type"] == "obstacle":
                bounce_from = collision
                break
        collisions.clear()
        if not bounce_from:
            return False
    else:
        return False

    angle = calculate_angle(game["x"], game["y"], game["x"] + game["x_velocity"], game["y"] + game["y_velocity"])

    # When bouncing left
    if game["x_velocity"] >= 0 and game["x"] + game["w"] <= bounce_from["x"]:
        try:
            ray = abs((bounce_from["x"] - game["w"] - game["x"]) / math.cos(angle))
        except ZeroDivisionError:
            print("Error: Tried to divide by zero in predict_collisions: ray = abs((bounce_from['x'] - game['w'] - game['x']) / math.cos(angle))")
            ray = abs(game["y"] - bounce_from["y"])
        if try_to_bounce(angle, ray, bounce_from, "x_velocity"):
            return True

    # When bouncing right
    elif game["x_velocity"] <= 0 and game["x"] >= bounce_from["x"] + bounce_from["w"]:
        try:
            ray = abs((game["x"] - bounce_from["x"] - bounce_from["w"]) / math.cos(angle))
        except ZeroDivisionError:
            print("Error: Tried to divide by zero in check_overlaps: ray = abs((game['x'] - bounce_from['x'] - bounce_from['w']) / math.cos(angle))")
            ray = abs(game["y"] - bounce_from["y"])        
        if try_to_bounce(angle, ray, bounce_from, "x_velocity"):
            return True

    # When bouncing up
    if game["y_velocity"] <= 0 and game["y"] >= bounce_from["y"] + bounce_from["h"]:
        try:
            ray = abs((game["y"] - bounce_from["y"] - bounce_from["h"]) / math.sin(angle))
        except ZeroDivisionError:
            print("Error: Tried to divide by zero in check_overlaps: ray = abs((game['y'] - bounce_from['y'] - bounce_from['h']) / math.sin(angle))")
            ray = abs(game["x"] - bounce_from["x"])
        if try_to_bounce(angle, ray, bounce_from, "y_velocity"):
            return True


def try_to_bounce(angle, ray, bounce_from, velocity_axis):
    """
    Tests if the duck should bounce off the bounce_from -obstacle in the direction defined by velocity_axis.
    Parameters:
    - angle: The direction to which the duck is currently heading, in radians.
    - ray: The distance from duck's current position to the assumed next position.
    - bounce_from: A dictionary which describes a box and has x, y, w and h values.
    - velocity_axis: Either "x_velocity" or "y_velocity".
    Returns:
    - True, if the duck bounces off the bounce_from -obstacle.
    - False otherwise.
    """
    x_movement, y_movement = convert_to_xy(angle, ray)
    test_box = {"x": game["x"] + x_movement,
                "y": game["y"] + y_movement,
                "w": game["w"],
                "h": game["h"]
                }
    if is_inside_area(test_box["x"], test_box["x"] + test_box["w"], test_box["y"], test_box["y"] + test_box["h"], bounce_from):
        game["x"] = test_box["x"]
        game["y"] = test_box["y"]
        if velocity_axis == "x_velocity":
            game[velocity_axis] = game[velocity_axis] * -ELASTICITY
        elif velocity_axis == "y_velocity":
            game[velocity_axis] = game[velocity_axis] * -ELASTICITY
            game["x_velocity"] = game["x_velocity"] * ELASTICITY
        if abs(game["x_velocity"]) > 1 or abs(game["y_velocity"]) > 2:
            bounce_sound.play()
        return True
    else:
        return False


def check_overlaps():
    """
    Checks if the duck is currently overlapping with an obstacle.
    If it is, it bounces into an appropriate direction from the obstacle.
    """
    overlapping_box = None

    for box in game["boxes"]:
        if is_inside_area(game["x"], game["x"] + game["w"], game["y"], game["y"] + game["h"], box):
            if box["type"] == "obstacle":
                overlapping_box = box
                break

    if not overlapping_box:
        return False

    angle = calculate_angle(game["x"], game["y"], game["x"] + game["x_velocity"], game["y"] + game["y_velocity"])

    # When bouncing left
    if game["x_velocity"] >= 0 and not check_adjacent_boxes(overlapping_box, "left"):
        try:
            ray = abs((overlapping_box["x"] - game["w"] - game["x"]) / math.cos(angle))
        except ZeroDivisionError:
            print("Error: Tried to divide by zero in check_overlaps: ray = abs((overlapping_box['x'] - game['w'] - game['x']) / math.cos(angle))")
            ray = abs(game["y"] - overlapping_box["y"])
        if try_to_bounce(angle, ray, overlapping_box, "x_velocity"):
            return True

    # When bouncing right
    elif game["x_velocity"] <= 0 and not check_adjacent_boxes(overlapping_box, "right"):
        try:
            ray = abs((game["x"] - overlapping_box["x"] - overlapping_box["w"]) / math.cos(angle))
        except ZeroDivisionError:
            print("Error: Tried to divide by zero in check_overlaps: ray = abs((game['x'] - overlapping_box['x'] - overlapping_box['w']) / math.cos(angle))")
            ray = abs(game["y"] - overlapping_box["y"])
        if try_to_bounce(angle, ray, overlapping_box, "x_velocity"):
            return True

    # When bouncing up
    if game["y_velocity"] <= 0 and not check_adjacent_boxes(overlapping_box, "up"):
        try:
            ray = abs((game["y"] - overlapping_box["y"] - overlapping_box["h"]) / math.sin(angle))
        except ZeroDivisionError:
            print("Error: Tried to divide by zero in check_overlaps: ray = abs((game['y'] - overlapping_box['y'] - overlapping_box['h']) / math.sin(angle))")
            ray = abs(game["x"] - overlapping_box["x"])
        if try_to_bounce(angle, ray, overlapping_box, "y_velocity"):
            return True


def check_adjacent_boxes(box, side):
    """
    Checks if there is an adjacent box on certain side of the box.
    Parameters:
        - box: a box dictionary, with x, y, w and h values.
        - side: "left", "right" or "up".
    Returns:
        - True, if there is an adjacent box on the side specified by the side parameter.
        - False otherwise.
    """
    for other in game["boxes"]:
        if side == "left":
            if (box["y"] == other["y"] or
                    box["y"] + box["h"] == other["y"] + other["h"] and
                    box["x"] == other["x"] + other["w"]):
                return True
        elif side == "right":
            if (box["y"] == other["y"] or
                    box["y"] + box["h"] == other["y"] + other["h"] and
                    box["x"] + box["w"] == other["x"]):
                return True
        elif side == "up":
            if (box["y"] + box["h"] == other["y"] and
                    (box["x"] == other["x"] or
                     box["x"] + box["w"] == other["x"] + other["w"])):
                return True
    return False


def load_level(level):
    """
    Loads a level.
    Parameters:
    - level: String of characters defining the level to be loaded.
             Possible values:
             - "menu", when the player has pressed M to go to the menu.
             - "levelX.json", where X is a normal level's number.
             - "levelX", where X is a random level's number.
             - "lose", when the player loses in random levels -mode.
             - "win", when the player passes all normal levels.
    """
    game["used_ducks"].clear()
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
        level_number = ""
        for c in level:
            if c.isdigit():
                level_number += c
        level_number = int(level_number)
        game["boxes"] = create_boxes(level_number * 2)
        game["level"] = level
        if level_number <= 10:
            game["ducks"] = len(game["boxes"])
        else:
            game["ducks"] = 20
        game["next_level"] = "level{}".format(level_number + 1)
        game["random_levels_passed"] = level_number - 1


############################## Handler functions ##############################


def draw_handler():
    """
    This function draws everything in the game.
    """
    sweeperlib.clear_window()
    sweeperlib.draw_background()
    sweeperlib.begin_sprite_draw()

    if game["level"] == "menu":
        sweeperlib.draw_text("A Wee Bit Miffed Ducks", 40, WIN_HEIGHT - 150, size=40)
        sweeperlib.prepare_sprite("duck", 650, WIN_HEIGHT - 140)
        sweeperlib.draw_text("Play levels: P", 40, 354)
        sweeperlib.draw_text("Play random levels: R", 40, 282)
        sweeperlib.draw_text("Quit: Q", 40, 210)
        sweeperlib.draw_text("Controls:", WIN_WIDTH - 670, 642)
        sweeperlib.draw_text("R: Restart level", WIN_WIDTH - 670, 570)
        sweeperlib.draw_text("←/→ or mouse drag: Set angle", WIN_WIDTH - 670, 498)
        sweeperlib.draw_text("↑/↓ or mouse drag: Set Force", WIN_WIDTH - 670, 426)
        sweeperlib.draw_text("Space or release mouse: Launch", WIN_WIDTH - 670, 354)
        sweeperlib.draw_text("M: Menu", WIN_WIDTH - 670, 282)
        sweeperlib.draw_text("F: Toggle fullscreen on/off", WIN_WIDTH - 670, 210)

    if game["level"] == "win":
        sweeperlib.draw_text("You win!", WIN_WIDTH/2 - 100, WIN_HEIGHT/2)
        sweeperlib.draw_text("M: Menu", WIN_WIDTH/2 - 100, WIN_HEIGHT/2 - 72)
        sweeperlib.draw_text("Q: Quit", WIN_WIDTH/2 - 100, WIN_HEIGHT/2 - 144)

    if game["level"] == "lose":
        sweeperlib.draw_text("You lose!", 40, WIN_HEIGHT/2)
        sweeperlib.draw_text("Levels passed: {}".format(game["random_levels_passed"]), 40, WIN_HEIGHT/2 - 72)
        sweeperlib.draw_text("M: Menu", 40, WIN_HEIGHT/2 - 144)
        sweeperlib.draw_text("Q: Quit", 40, WIN_HEIGHT/2 - 216)

    if game["level"].startswith("level"):
        # Grid TODO: Delete later
        if game["grid"]:
            for x in range(0, WIN_WIDTH, 40):
                for y in range(0, WIN_HEIGHT, 40):
                    if x == 0 and y > 0:
                        sweeperlib.draw_text(".", x, y, size=20)
                        sweeperlib.draw_text(str(y), x+5, y, size=10)
                    elif x > 0 and y == 0:
                        sweeperlib.draw_text(".", x, y, size=20)
                        sweeperlib.draw_text(str(x), x+5, y, size=10)
                    else:
                        sweeperlib.draw_text(".", x, y, size=20)

        if game["flight"]:
            # Duck animation
            if game["time"] >= animation["animation_time"] + 0.1:
                animation["animation_time"] = game["time"]
                if animation["frame"] == "duck":
                    animation["frame"] = "duck2"
                elif animation["frame"] == "duck2":
                    animation["frame"] = "duck"
            sweeperlib.prepare_line(LAUNCH_X - 16, LAUNCH_Y + 43, LAUNCH_X + 20, LAUNCH_Y + 40, 5, (125, 125, 125))
            sweeperlib.prepare_line(LAUNCH_X + 55, LAUNCH_Y + 43, LAUNCH_X + 20, LAUNCH_Y + 40, 5, (125, 125, 125))
            sweeperlib.prepare_sprite(animation["frame"], game["x"], game["y"])          
        else:
            sweeperlib.prepare_line(LAUNCH_X - 16, LAUNCH_Y + 43, game["x"] + 20, game["y"] + 10, 5, (125, 125, 125))
            sweeperlib.prepare_line(LAUNCH_X + 55, LAUNCH_Y + 43, game["x"] + 20, game["y"] + 10, 5, (125, 125, 125))
            sweeperlib.prepare_sprite("duck", game["x"], game["y"])
            # Aiming points
            if game["mouse_down"] or game["force"] > 0:
                point_x = game["x"]
                point_y = game["y"]
                point_xv = game["force"] * FORCE_FACTOR * math.cos(math.radians(game["angle"]))
                point_yv = game["force"] * FORCE_FACTOR * math.sin(math.radians(game["angle"]))
                for i in range(20):
                    sweeperlib.draw_text("o", point_x + 20, point_y + 20, color=(255, 255, 255, 255), size=10)
                    point_x += point_xv
                    point_y += point_yv
                    point_yv -= GRAVITATIONAL_ACCEL

        # Sling
        sweeperlib.prepare_sprite("sling", LAUNCH_X - 20, GROUND_LEVEL)

        # Boxes
        for box in game["boxes"]:
            if box["type"] == "target":
                sweeperlib.prepare_sprite("target", box["x"], box["y"])
            elif box["type"] == "obstacle":
                sweeperlib.prepare_sprite("obstacle", box["x"], box["y"])

        # Remaining ducks
        for i in range(game["ducks"] - 1):
            sweeperlib.prepare_sprite("duck", 40 + i * 50, 20)

        # Used ducks
        for duck in game["used_ducks"]:
            sweeperlib.prepare_sprite("duck", duck["x"], duck["y"])

        # Info texts
        sweeperlib.draw_text("Level: {} Angle: {:.0f}° Force: {:.0f} Ducks: {}".format(
                game["level"].lstrip("level").rstrip(".json"), 
                game["angle"], 
                game["force"], 
                game["ducks"]
                ), 40, WIN_HEIGHT - 100, size=20)
    sweeperlib.draw_sprites()


def mouse_release_handler(x, y, button, modifiers):
    """
    This function is called when a mouse button is released.
    The function determines the angle and the force with which the duck will be launched and launches it.
    """
    if not game["flight"] and game["level"].startswith("level") and game["force"] >= 5:
        game["angle"] = math.degrees(calculate_angle(game["x"], game["y"], LAUNCH_X, LAUNCH_Y))
        game["force"] = math.sqrt(pow(game["x"] - LAUNCH_X, 2) + pow(game["y"] - LAUNCH_Y, 2))
        launch()
    elif not game["flight"] and game["level"].startswith("level") and game["force"] <= 5:
        initial_state()
    game["mouse_down"] = False


def drag_handler(mouse_x, mouse_y, dx, dy, mouse_button, modifier_keys):
    """
    This function is called when the mouse is moved while one of its buttons is
    pressed down. This is used to drag the duck.
    """
    if not game["flight"] and game["level"].startswith("level"):
        game["mouse_down"] = True
        game["x"] += dx
        game["y"] += dy
        game["x"], game["y"] = clamp_inside_circle(game["x"], game["y"], LAUNCH_X, LAUNCH_Y, DRAG_RADIUS)
        game["angle"] = math.degrees(calculate_angle(game["x"], game["y"], LAUNCH_X, LAUNCH_Y))
        game["force"] = math.sqrt(pow(game["x"] - LAUNCH_X, 2) + pow(game["y"] - LAUNCH_Y, 2))


def keyboard_handler(symbol, modifiers):
    """
    This function handles keyboard input.
    """
    key = sweeperlib.pyglet.window.key

    if symbol == key.Q:
        sweeperlib.close()

    if symbol == key.M:
        initial_state()
        game["level"] = "menu"

    # TODO: Delete later
    if symbol == key.G:
        if game["grid"]:
            game["grid"] = False
        else:
            game["grid"] = True

    if symbol == key.F:
        if game["fullscreen"]:
            sweeperlib.graphics["window"].set_fullscreen(fullscreen=False)
            game["fullscreen"] = False
        else:
            sweeperlib.graphics["window"].set_fullscreen(fullscreen=True)
            game["fullscreen"] = True

    # Menu keys
    if game["level"] == "menu":
        if symbol == key.P:
            load_level("level1.json")
        if symbol == key.R:
            load_level("level1")

    # Game keys
    if game["level"].startswith("level"):
        if game["level"].endswith(".json") or game["level"].endswith("1"):
            if symbol == key.R:
                initial_state()
                load_level(game["level"])

        if symbol == key.RIGHT:
            game["angle"] -= 5
            if game["angle"] < -175:
                game["angle"] = game["angle"] * -1
            update_position()
        elif symbol == key.LEFT:
            game["angle"] += 5
            if game["angle"] > 180:
                game["angle"] = game["angle"] * -1 + 10
            update_position()

        if symbol == key.UP:
            if game["force"] < 100:
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

        # TODO: Delete later
        if symbol == key.N:
            initial_state()
            load_level(game["next_level"])


def update(elapsed):
    """
    This is called 60 times/second.
    """
    game["time"] += elapsed
    if game["level"].startswith("level"):
        drop(game["boxes"])
        drop_ducks(game["used_ducks"])
        if game["flight"]:
            destroy_targets(game)
            check_overlaps()
            predict_collisions()
            game["x"] += game["x_velocity"]
            game["y"] += game["y_velocity"]
            game["y_velocity"] -= GRAVITATIONAL_ACCEL
            if abs(game["x_velocity"]) <= 1.5 and abs(game["y_velocity"]) <= 2.5:
                game["slow_duck"] += elapsed
            else:
                game["slow_duck"] = 0
            if game["y"] <= GROUND_LEVEL or game["slow_duck"] > 0.1:
                game["used_ducks"].append({
                    "x": game["x"],
                    "y": game["y"],
                    "w": game["w"],
                    "h": game["h"],
                    "vy": 0
                })
                initial_state()
        else:
            if not targets_remaining():
                load_level(game["next_level"])
            elif game["ducks"] == 0:
                if game["level"].endswith(".json"):
                    load_level(game["level"])
                else:
                    game["level"] = "lose"


if __name__ == "__main__":
    sweeperlib.load_duck("sprites")
    sweeperlib.create_window(width=WIN_WIDTH, height=WIN_HEIGHT, bg_color=BG_COLOR)
    sweeperlib.set_draw_handler(draw_handler)
    sweeperlib.set_release_handler(mouse_release_handler)
    sweeperlib.set_drag_handler(drag_handler)
    sweeperlib.set_keyboard_handler(keyboard_handler)
    sweeperlib.set_interval_handler(update, interval=1/60)
    sweeperlib.start()
