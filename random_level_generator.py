"""
A program that drops a bunch of randomly placed boxes down from 
the sky so that they pile up on top of each other.
"""

import sweeperlib
import random

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 600
GRAVITATIONAL_ACCEL = 1.5

game = {
    "boxes": []
}


def order(box):
    """
    Used to sort the list of boxes according to their height measured from the top of the box
    """
    return box['y'] + box['h']


def create_boxes(quantity, min_height):
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
        box = {
            'x': random.randint(400, 800), # 0, WINDOW_WIDTH
            'y': random.randint(200, 400), # min_height, WINDOW_HEIGHT
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
    if (box['x'] < other['x'] < box['x'] + box['w'] and 
            box['y'] <= other['y'] + other['h'] <= box['y'] + box['h']):
        return True
    # Check if the other box's upper right corner is inside the box
    elif (box['x'] < other['x'] + other['w'] < box['x'] + box['w'] and 
            box['y'] <= other['y'] + other['h'] <= box['y'] + box['h']):
        return True
    # Check if the other box's lower left corner is inside the box
    elif (box['x'] < other['x'] < box['x'] + box['w'] and 
            box['y'] <= other['y'] <= box['y'] + box['h']):
        return True
    # Check if the other box's lower right corner is inside the box
    elif (box['x'] < other['x'] + other['w'] < box['x'] + box['w'] and 
            box['y'] <= other['y'] <= box['y'] + box['h']):
        return True
    # Check if the box goes on top of the other box through the bottom of the other box
    elif (other['x'] < box['x'] < other['x'] + other['w'] and
            other['x'] < box['x'] + box['w'] < other['x'] + other['w'] and
            other['y'] <= box['y'] + box['h'] <= other['y'] + other['h']):
        return True    
    # Check if the box goes on top of the other box through the top of the other box
    elif (other['x'] < box['x'] < other['x'] + other['w'] and
            other['x'] < box['x'] + box['w'] < other['x'] + other['w'] and
            other['y'] <= box['y'] <= other['y'] + other['h']):
        return True
    # Check if the box goes on top of the other box through the left side of the other box
    elif (other['y'] <= box['y'] <= other['y'] + other['h'] and
            other['y'] <= box['y'] + box['h'] <= other['y'] + other['h'] and
            other['x'] < box['x'] + box['w'] < other['x'] + other['w']):
        return True
    # Check if the box goes on top of the other box through the right side of the other box
    elif (other['y'] <= box['y'] <= other['y'] + other['h'] and
            other['y'] <= box['y'] + box['h'] <= other['y'] + other['h'] and
            other['x'] < box['x'] < other['x'] + other['w']):
        return True
    else:
        return False


def draw():
    """
    Draws all boxes into the window.
    """
    sweeperlib.clear_window()
    sweeperlib.draw_background()
    sweeperlib.begin_sprite_draw()
    for i in range(len(game['boxes'])):
        sweeperlib.prepare_sprite(" ", game['boxes'][i]['x'], game['boxes'][i]['y'])
    sweeperlib.draw_sprites()


def update(elapsed_time):
    drop(game["boxes"])


if __name__ == "__main__":

    game['boxes'] = create_boxes(10, 50)
    sweeperlib.load_sprites("sprites")
    sweeperlib.create_window(width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
    sweeperlib.set_draw_handler(draw)
    sweeperlib.set_interval_handler(update, interval=1/60)
    sweeperlib.start()