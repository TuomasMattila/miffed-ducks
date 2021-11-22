
def check_collisions():
############## OLD FUNCTION ################

    collisions = []
    bounce_from = None
    
    # Duck's direction: down and right
    if game["y_velocity"] <= 0 and game["x_velocity"] >= 0:
        # Which boxes are colliding or are about to be passed by the duck
        for i in range(len(game["boxes"])):
            if is_inside_area(game["x"], game["x"] + game["x_velocity"] + game["w"], game["y"] + game["y_velocity"], game["y"] + game["h"], game["boxes"][i]):
                collisions.append({"box": game["boxes"][i], "index": i})
        if collisions:
            collisions.sort(key=order_by_distance)
            # Find the closest box and delete target boxes    
            for collision in collisions:
                if collision["box"]["type"] == "target":
                    game["boxes"].remove(game["boxes"][collision["index"]])
                    box_breaking_sound.play()
                elif collision["box"]["type"] == "obstacle":
                    bounce_from = collision["box"]
                    break

            collisions.clear()

            if not bounce_from:
                return False

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
        if collisions:
            collisions.sort(key=order_by_distance)
            # Find the closest box and delete target boxes    
            for collision in collisions:
                if collision["box"]["type"] == "target":
                    game["boxes"].remove(game["boxes"][collision["index"]])
                    box_breaking_sound.play()
                elif collision["box"]["type"] == "obstacle":
                    bounce_from = collision["box"]
                    break

            collisions.clear()

            if not bounce_from:
                return False

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
        if collisions:
            collisions.sort(key=order_by_distance)
            # Find the closest box and delete target boxes    
            for collision in collisions:
                if collision["box"]["type"] == "target":
                    game["boxes"].remove(game["boxes"][collision["index"]])
                    box_breaking_sound.play()
                elif collision["box"]["type"] == "obstacle":
                    bounce_from = collision["box"]
                    break

            collisions.clear()

            if not bounce_from:
                return False

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
            if is_inside_area(game["x"] + game["x_velocity"], game["x"] + game["w"], game["y"], game["y"] + game["y_velocity"] + game["h"], game["boxes"][i]):
                collisions.append({"box": game["boxes"][i], "index": i})
        if collisions:
            collisions.sort(key=order_by_distance)
            # Find the closest box and delete target boxes    
            for collision in collisions:
                if collision["box"]["type"] == "target":
                    game["boxes"].remove(game["boxes"][collision["index"]])
                    box_breaking_sound.play()
                elif collision["box"]["type"] == "obstacle":
                    bounce_from = collision["box"]
                    break

            collisions.clear()

            if not bounce_from:
                return False

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


###################### NEWER VERSION ############################
def check_collisions():
    """
    Checks whether the duck collides with boxes. If a target is colliding, it is destroyed.
    If the duck collides with an obstacle, it bounces off it if the circumstances are right.
    """
    collisions = []
    bounce_from = None

    # Duck's direction: down and right
    if game["y_velocity"] <= 0 and game["x_velocity"] >= 0:
        # Which boxes are colliding or are about to be passed by the duck
        for i in range(len(game["boxes"])):
            if is_inside_area(game["x"], game["x"] + game["x_velocity"] + game["w"], game["y"] + game["y_velocity"], game["y"] + game["h"], game["boxes"][i]):
                collisions.append({"box": game["boxes"][i], "index": i})
    # Duck's direction: down and left
    elif game["y_velocity"] <= 0 and game["x_velocity"] <= 0:
        # Which boxes are colliding or are about to be passed by the duck
        for i in range(len(game["boxes"])):
            if is_inside_area(game["x"] + game["x_velocity"], game["x"] + game["w"], game["y"] + game["y_velocity"], game["y"] + game["h"], game["boxes"][i]):
                collisions.append({"box": game["boxes"][i], "index": i})    
    # Duck's direction: up and right
    elif game["y_velocity"] >= 0 and game["x_velocity"] >= 0:
        # Which boxes are colliding or are about to be passed by the duck
        for i in range(len(game["boxes"])):
            if is_inside_area(game["x"], game["x"] + game["x_velocity"] + game["w"], game["y"], game["y"] + game["y_velocity"] + game["h"], game["boxes"][i]):
                collisions.append({"box": game["boxes"][i], "index": i})
    # Duck's direction: up and left
    elif game["y_velocity"] >= 0 and game["x_velocity"] <= 0:
        # Which boxes are colliding or are about to be passed by the duck
        for i in range(len(game["boxes"])):
            if is_inside_area(game["x"] + game["x_velocity"], game["x"] + game["w"], game["y"], game["y"] + game["y_velocity"] + game["h"], game["boxes"][i]):
                collisions.append({"box": game["boxes"][i], "index": i})

    if collisions:
        collisions.sort(key=order_by_distance)
        # Find the closest box and delete target boxes    
        for collision in collisions:
            if collision["box"]["type"] == "target":
                game["boxes"].remove(game["boxes"][collision["index"]])
                box_breaking_sound.play()
            elif collision["box"]["type"] == "obstacle":
                bounce_from = collision["box"]
                break
        collisions.clear()
        if not bounce_from:
            return False
    else:
        return False


    angle = calculate_angle(game["x"], game["y"], game["x"] + game["x_velocity"], game["y"] + game["y_velocity"]) # TODO: use this function in clamp_inside_circle -function

    # When bouncing left
    if game["x_velocity"] >= 0 and game["x"] <= bounce_from["x"]:
        ray = abs((bounce_from["x"] - game["w"] - game["x"]) / math.cos(angle))
        x_movement, y_movement = convert_to_xy(angle, ray)
        # Test whether the box should bounce left
        test_box = {"x": game["x"] + x_movement, 
                    "y": game["y"] + y_movement, 
                    "w": game["w"], 
                    "h": game["h"]
                    }
        if is_inside_area(test_box["x"], test_box["x"] + test_box["w"], test_box["y"], test_box["y"] + test_box["h"], bounce_from):
            game["x"] = test_box["x"]
            game["y"] = test_box["y"]
            game["x_velocity"] = game["x_velocity"] * -ELASTICITY
            return True


    # When bouncing right
    elif game["x_velocity"] <= 0 and game["x"] >= bounce_from["x"]:
        ray = abs((game["x"] - bounce_from["x"] - bounce_from["w"]) / math.cos(angle))
        # TODO: this part is similar at least when checking bouncing left or right
        x_movement, y_movement = convert_to_xy(angle, ray)
        # Test whether the box should bounce right
        test_box = {"x": game["x"] + x_movement, 
                    "y": game["y"] + y_movement, 
                    "w": game["w"], 
                    "h": game["h"]
                    }
        if is_inside_area(test_box["x"], test_box["x"] + test_box["w"], test_box["y"], test_box["y"] + test_box["h"], bounce_from):
            game["x"] = test_box["x"]
            game["y"] = test_box["y"]
            game["x_velocity"] = game["x_velocity"] * -ELASTICITY
            return True

    # When bouncing up
    if game["y_velocity"] <= 0:
        ray = abs((game["y"] - bounce_from["y"] - bounce_from["h"]) / math.sin(angle))
        x_movement, y_movement = convert_to_xy(angle, ray)
        # Test whether the box should bounce up
        test_box = {"x": game["x"] + x_movement, 
                    "y": game["y"] + y_movement, 
                    "w": game["w"], 
                    "h": game["h"]
                    }
        if is_inside_area(test_box["x"], test_box["x"] + test_box["w"], test_box["y"], test_box["y"] + test_box["h"], bounce_from):
            game["x"] = test_box["x"]
            game["y"] = test_box["y"]
            game["y_velocity"] = game["y_velocity"] * -ELASTICITY
            return True