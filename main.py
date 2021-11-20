"""
Elementary programming 2021 course project: A Wee Bit Miffed Ducks.
A game where you shoot ducks at objects.
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
    "fullscreen": True
}

animation = {
    "animation_time": 0.0,
    "frame": "duck",
    "points": []
}


def order_by_height(box):
    """
    Used to sort the list of boxes according to their height measured from the top of the box.
    """
    return box["y"] + box["h"]


def order_by_distance(collision):
    """
    Used to sort the list of colliding boxes according to their distance from the duck.
    """
    return calculate_distance(game["x"], game["y"], collision["box"]["x"], collision["box"]["y"])


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
            'y': random.randint(80, WIN_HEIGHT/2),
            'w': 40,
            'h': 40,
            'vy': 0
        }
        boxlist.append(box)
        boxlist.sort(key=order_by_height)

    return boxlist


def drop(boxes):
    """
    Drops rectangular objects that are given as a list. Each object is to be
    defined as a dictionary with x and y coordinates, width, height, and falling
    velocity. Drops boxes for one time unit.
    """
    boxes.sort(key=order_by_height)
    try:
        boxes[0]["initial_height"]
    except KeyError:
        for i in range(len(boxes)):
            boxes[i]["initial_height"] = boxes[i]["y"] + boxes[i]["h"]  
    for i in range(len(boxes)):
        if boxes[i]["y"] <= GROUND_LEVEL:
            boxes[i]["y"] = GROUND_LEVEL
            boxes[i]["vy"] = 0
            continue
         
        allow_falling = True
        for j in range(len(boxes)):
            if i == j:
                continue
            if boxes[i]["initial_height"] < boxes[j]["initial_height"]:
                continue
            if is_inside_area(boxes[i]["x"], boxes[i]["x"] + boxes[i]["w"], boxes[i]["y"], boxes[i]["y"] + boxes[i]["h"], boxes[j]):
                boxes[i]["y"] = boxes[j]["y"] + boxes[j]["h"]
                boxes[i]["vy"] = 0
                allow_falling = False      

        if allow_falling:
            boxes[i]["vy"] += GRAVITATIONAL_ACCEL
            boxes[i]["y"] -= boxes[i]["vy"]


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
        game["x_velocity"] = game["force"] * FORCE_FACTOR * math.cos(math.radians(game["angle"]))
        game["y_velocity"] = game["force"] * FORCE_FACTOR * math.sin(math.radians(game["angle"]))
        game["flight"] = True
        game["ducks"] -= 1
        animation["points"].clear()


def is_inside_area(min_x, max_x, min_y, max_y, object):
    if max_y < object["y"] or min_y > object["y"] + object["h"]:
        return False
    elif max_x < object["x"] or min_x > object["x"] + object["w"]:
        return False
    else: 
        return True


def check_collisions():
    collisions = []
    
    # Duck's direction: down and right
    if game["y_velocity"] <= 0 and game["x_velocity"] >= 0:
        # Which boxes are colliding or are about to be passed by the duck
        for i in range(len(game["boxes"])):
            if is_inside_area(game["x"], game["x"] + game["x_velocity"] + game["w"], game["y"] + game["y_velocity"], game["y"] + game["h"], game["boxes"][i]):
                collisions.append({"box": game["boxes"][i], "index": i})
        # Which box is the closest to the duck's position (a.k.a. which box should the duck bounce off from)
        if collisions:
            collisions.sort(key=order_by_distance)
            # Delete target boxes
            while collisions[0]["box"]["type"] == "target":
                game["boxes"].remove(game["boxes"][collisions[0]["index"]])
                box_breaking_sound.play()
                collisions.remove(collisions[0])
                if not collisions:
                    return False
                collisions.sort(key=order_by_distance)

            bounce_from = collisions[0]["box"]

            # Calculate position, if the box should bounce to the left
            if game["x"] + game["w"] < bounce_from["x"]:
                test_box = {"x": bounce_from["x"] - game["w"], 
                            "y": game["y"] + (game["y_velocity"] / game["x_velocity"] * (bounce_from["x"] - game["w"] - game["x"])), 
                            "w": game["w"], 
                            "h": game["h"]
                            }
                if is_inside_area(test_box["x"], test_box["x"] + test_box["w"], test_box["y"], test_box["y"] + test_box["h"], bounce_from):
                    game["x"] = test_box["x"]
                    game["y"] = test_box["y"]
                    game["x_velocity"] = game["x_velocity"] * -ELASTICITY
                    collisions.clear()
                    return True

            # Calculate position, if the box should bounce up-and-right
            test_box = {"x": game["x"] + (game["x_velocity"] / game["y_velocity"] * (game["y"] - bounce_from["y"] - bounce_from["h"])), 
                        "y": bounce_from["y"] + bounce_from["h"], 
                        "w": game["w"], 
                        "h": game["h"]}
            if is_inside_area(test_box["x"], test_box["x"] + test_box["w"], test_box["y"], test_box["y"] + test_box["h"], bounce_from):
                game["x"] = test_box["x"]
                game["y"] = test_box["y"]
                game["y_velocity"] = game["y_velocity"] * -ELASTICITY
                collisions.clear()
                return True
        else:
            return False
    
    # Duck's direction: down and left
    elif game["y_velocity"] <= 0 and game["x_velocity"] <= 0:
        # Which boxes are colliding or are about to be passed by the duck
        for i in range(len(game["boxes"])):
            if is_inside_area(game["x"] + game["x_velocity"], game["x"] + game["w"], game["y"] + game["y_velocity"], game["y"] + game["h"], game["boxes"][i]):
                collisions.append({"box": game["boxes"][i], "index": i})
        # Which box is the closest to the duck's position (a.k.a. which box should the duck bounce off from)
        if collisions:
            collisions.sort(key=order_by_distance)
            # Delete target boxes
            while collisions[0]["box"]["type"] == "target":
                game["boxes"].remove(game["boxes"][collisions[0]["index"]])
                box_breaking_sound.play()
                collisions.remove(collisions[0])
                if not collisions:
                    return False
                collisions.sort(key=order_by_distance)

            bounce_from = collisions[0]["box"]

            if game["x"] > bounce_from["x"] + bounce_from["w"]:
                # Calculate position, if the box should bounce to the right
                test_box = {"x": bounce_from["x"] + bounce_from["w"], 
                            "y": game["y"] + (game["y_velocity"] / game["x_velocity"] * (game["x"] - bounce_from["x"] - bounce_from["w"])), 
                            "w": game["w"], 
                            "h": game["h"]
                            }
                if is_inside_area(test_box["x"], test_box["x"] + test_box["w"], test_box["y"], test_box["y"] + test_box["h"], bounce_from):
                    game["x"] = test_box["x"]
                    game["y"] = test_box["y"]
                    game["x_velocity"] = game["x_velocity"] * -ELASTICITY
                    collisions.clear()
                    return True

            # Calculate position, if the box should bounce up-and-left
            test_box = {"x": game["x"] + (game["x_velocity"] / game["y_velocity"] * (game["y"] - bounce_from["y"] - bounce_from["h"])), 
                        "y": bounce_from["y"] + bounce_from["h"], 
                        "w": game["w"], 
                        "h": game["h"]}
            if is_inside_area(test_box["x"], test_box["x"] + test_box["w"], test_box["y"], test_box["y"] + test_box["h"], bounce_from):
                game["x"] = test_box["x"]
                game["y"] = test_box["y"]
                game["y_velocity"] = game["y_velocity"] * -ELASTICITY
                collisions.clear()
                return True
        else:
            return False

    # Duck's direction: up and right
    elif game["y_velocity"] >= 0 and game["x_velocity"] >= 0:
        # Which boxes are colliding or are about to be passed by the duck
        for i in range(len(game["boxes"])):
            if is_inside_area(game["x"], game["x"] + game["x_velocity"] + game["w"], game["y"], game["y"] + game["y_velocity"] + game["h"], game["boxes"][i]):
                collisions.append({"box": game["boxes"][i], "index": i})
        # Which box is the closest to the duck's position (a.k.a. which box should the duck bounce off from)
        if collisions:
            collisions.sort(key=order_by_distance)
            # Delete target boxes
            while collisions[0]["box"]["type"] == "target":
                game["boxes"].remove(game["boxes"][collisions[0]["index"]])
                box_breaking_sound.play()
                collisions.remove(collisions[0])
                if not collisions:
                    return False
                collisions.sort(key=order_by_distance)

            bounce_from = collisions[0]["box"]

            # Calculate position, if the box should bounce to the left
            test_box = {"x": bounce_from["x"] - game["w"], 
                        "y": game["y"] + (game["y_velocity"] / game["x_velocity"] * (bounce_from["x"] - game["w"] - game["x"])), 
                        "w": game["w"], 
                        "h": game["h"]
                        }
            if is_inside_area(test_box["x"], test_box["x"] + test_box["w"], test_box["y"], test_box["y"] + test_box["h"], bounce_from):
                game["x"] = test_box["x"]
                game["y"] = test_box["y"]
                game["x_velocity"] = game["x_velocity"] * -ELASTICITY
                collisions.clear()
                return True

            # Calculate position, if the box should bounce down-and-right
            test_box = {"x": game["x"] + (game["x_velocity"] / game["y_velocity"] * (bounce_from["y"] - game["h"] - game["y"])), 
                        "y": bounce_from["y"] - game["h"], 
                        "w": game["w"], 
                        "h": game["h"]}
            if is_inside_area(test_box["x"], test_box["x"] + test_box["w"], test_box["y"], test_box["y"] + test_box["h"], bounce_from):
                game["x"] = test_box["x"]
                game["y"] = test_box["y"]
                game["y_velocity"] = game["y_velocity"] * -ELASTICITY
                collisions.clear()
                return True
        else:
            return False        
    # Duck's direction: up and left
    elif game["y_velocity"] >= 0 and game["x_velocity"] <= 0:
        # Which boxes are colliding or are about to be passed by the duck
        for i in range(len(game["boxes"])):
            if is_inside_area(game["x"] + game["x_velocity"], game["x"] + game["w"], game["y"], game["y"] + game["y_velocity"] + game["h"], game["boxes"][i]): # TODO: this is unique for each direction
                collisions.append({"box": game["boxes"][i], "index": i})
        # Which box is the closest to the duck's position (a.k.a. which box should the duck bounce off from)
        if collisions:
            collisions.sort(key=order_by_distance)
            # Delete target boxes
            while collisions[0]["box"]["type"] == "target":
                game["boxes"].remove(game["boxes"][collisions[0]["index"]])
                box_breaking_sound.play()
                collisions.remove(collisions[0])
                if not collisions:
                    return False
                collisions.sort(key=order_by_distance)

            bounce_from = collisions[0]["box"]

            if game["x"] > bounce_from["x"] + bounce_from["w"]:
                # Calculate position, if the box should bounce to the right
                test_box = {"x": bounce_from["x"] + bounce_from["w"], 
                            "y": game["y"] + (game["y_velocity"] / game["x_velocity"] * (game["x"] - bounce_from["x"] - bounce_from["w"])), 
                            "w": game["w"], 
                            "h": game["h"]
                            }
                if is_inside_area(test_box["x"], test_box["x"] + test_box["w"], test_box["y"], test_box["y"] + test_box["h"], bounce_from):
                    game["x"] = test_box["x"]
                    game["y"] = test_box["y"]
                    game["x_velocity"] = game["x_velocity"] * -ELASTICITY
                    collisions.clear()
                    return True

            # Calculate position, if the box should bounce down-and-left
            test_box = {"x": game["x"] + (game["x_velocity"] / game["y_velocity"] * (bounce_from["y"] - game["h"] - game["y"])), 
                        "y": bounce_from["y"] - game["h"], 
                        "w": game["w"], 
                        "h": game["h"]}
            if is_inside_area(test_box["x"], test_box["x"] + test_box["w"], test_box["y"], test_box["y"] + test_box["h"], bounce_from):
                game["x"] = test_box["x"]
                game["y"] = test_box["y"]
                game["y_velocity"] = game["y_velocity"] * -ELASTICITY
                collisions.clear()
                return True
        else:
            return False

def update(elapsed):
    """
    This is called 60 times/second.
    """
    game["time"] += elapsed
    if game["level"].startswith("level"):
        drop(game["boxes"])
        drop_ducks(game["used_ducks"])
    if game["flight"]:
        #animation["points"].append({"x": game["x"] + 20, "y": game["y"] + 20})
        check_collisions()
        game["x"] += game["x_velocity"]
        game["y"] += game["y_velocity"]
        game["y_velocity"] -= GRAVITATIONAL_ACCEL
        if game["y"] <= GROUND_LEVEL:
            game["used_ducks"].append({
                "x": game["x"],
                "y": game["y"],
                "w": game["w"],
                "h": game["h"],
                "vy": 0
            })
            initial_state()
        if not targets_remaining(game["boxes"]):
            initial_state()
            load_level(game["next_level"])


def drop_ducks(ducks):
    """
    Makes used ducks fall down to the ground.
    """
    for duck in ducks:
        # Used ducks that are falling also destroy targets
        for i in range(len(game["boxes"])):
            if is_inside_area(duck["x"], duck["x"] + duck["w"], duck["y"], duck["y"] + duck["h"], game["boxes"][i]):
                if game["boxes"][i]["type"] == "target":
                    game["boxes"].remove(game["boxes"][i])
                    box_breaking_sound.play()
                if not targets_remaining(game["boxes"]):
                        initial_state()
                        load_level(game["next_level"])
                break
        if duck["y"] <= GROUND_LEVEL:
            duck["y"] = GROUND_LEVEL
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
        sweeperlib.draw_text("Play levels: P", 40, 354)
        sweeperlib.draw_text("Play random levels: R", 40, 282)
        sweeperlib.draw_text("Quit: Q", 40, 210)
        sweeperlib.draw_text("Controls:", WIN_WIDTH - 550, 642)
        sweeperlib.draw_text("R: Restart level", WIN_WIDTH - 550, 570)
        sweeperlib.draw_text("←/→: Set angle", WIN_WIDTH - 550, 498)
        sweeperlib.draw_text("↑/↓: Set Force", WIN_WIDTH - 550, 426)
        sweeperlib.draw_text("Space: Launch", WIN_WIDTH - 550, 354)
        sweeperlib.draw_text("M: Menu", WIN_WIDTH - 550, 282)
        sweeperlib.draw_text("F: Toggle fullscreen on/off", WIN_WIDTH - 550, 210)

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
        # Grid
        #for x in range(0, WIN_WIDTH, 40):
        #    for y in range(0, WIN_HEIGHT, 40):
        #        if x == 0 and y > 0:
        #            sweeperlib.draw_text(".", x, y, size=20)
        #            sweeperlib.draw_text(str(y), x+5, y, size=10)
        #        elif x > 0 and y == 0:
        #            sweeperlib.draw_text(".", x, y, size=20)
        #            sweeperlib.draw_text(str(x), x+5, y, size=10)
        #        else:
        #            sweeperlib.draw_text(".", x, y, size=20)
        
        # Duck animation         
        if game["flight"]:
            if game["time"] >= animation["animation_time"] + 0.1:
                animation["animation_time"] = game["time"]
                if animation["frame"] == "duck":
                    animation["frame"] = "duck2"
                elif animation["frame"] == "duck2":
                    animation["frame"] = "duck"
                animation["points"].append({"x": game["x"] + 20, "y": game["y"] + 20})
            sweeperlib.prepare_sprite(animation["frame"], game["x"], game["y"])
        else:
            sweeperlib.prepare_sprite("duck", game["x"], game["y"])

        # Sling
        sweeperlib.prepare_sprite("sling", LAUNCH_X - 20, GROUND_LEVEL)

        # Boxes
        for i in range(len(game["boxes"])):
            if game["boxes"][i]["type"] == "target":
                sweeperlib.prepare_sprite("target", game["boxes"][i]["x"], game["boxes"][i]["y"])
            elif game["boxes"][i]["type"] == "obstacle":
                sweeperlib.prepare_sprite("obstacle", game["boxes"][i]["x"], game["boxes"][i]["y"])

        # Used ducks
        for duck in game["used_ducks"]:
            sweeperlib.prepare_sprite("duck", duck["x"], duck["y"])

        # Points
        for point in animation["points"]:
            sweeperlib.draw_text("o", point["x"], point["y"], color=(255, 255, 255, 255), size=10)

        # Info texts
        sweeperlib.draw_text("Level: {} Angle: {:.0f}° Force: {:.0f} Ducks: {}".format(game["level"].lstrip("level").rstrip(".json"), game["angle"], game["force"], game["ducks"]), 40, WIN_HEIGHT - 100, size=20)
    sweeperlib.draw_sprites()


def mouse_release_handler(x, y, button, modifiers):
    """
    If the player is using mouse controls, this function is called when a mouse button is released.
    The function determines the angle and the force with which the duck will be launched and launches it.
    """
    if not game["flight"] and game["level"].startswith("level"):
        game["mouse_down"] = False
        game["angle"] = set_angle()
        game["force"] = math.sqrt(pow(game["x"] - LAUNCH_X, 2) + pow(game["y"] - LAUNCH_Y, 2))
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
        game["force"] = math.sqrt(pow(game["x"] - LAUNCH_X, 2) + pow(game["y"] - LAUNCH_Y, 2))


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
    game["x"] = LAUNCH_X - x
    game["y"] = LAUNCH_Y - y


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
