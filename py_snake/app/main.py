import json
import os
import random
import bottle

from api import ping_response, start_response, move_response, end_response


@bottle.route('/')
def index():
    return '''
    Battlesnake documentation can be found at
       <a href="https://docs.battlesnake.com">https://docs.battlesnake.com</a>.
    '''


@bottle.route('/static/<path:path>')
def static(path):
    """
    Given a path, return the static file located relative
    to the static folder.

    This can be used to return the snake head URL in an API response.
    """
    return bottle.static_file(path, root='static/')


@bottle.post('/ping')
def ping():
    """
    A keep-alive endpoint used to prevent cloud application platforms,
    such as Heroku, from sleeping the application instance.
    """
    return ping_response()


@bottle.post('/start')
def start():
    data = bottle.request.json

    """
    TODO: If you intend to have a stateful snake AI,
            initialize your snake state here using the
            request's data if necessary.
    """
    print(json.dumps(data))

    color = "#2E86C1"
    headType = "bendr"
    tailType = "bwc-ice-skate"

    return start_response(color, headType, tailType)


@bottle.post('/move')
def move():
    data = bottle.request.json

    """
    TODO: Using the data from the endpoint request object, your
            snake AI must choose a direction to move in.
    """
    print(json.dumps(data))

    directions = ['up', 'down', 'left', 'right']
    direction = directions[1]
    up = directions[0]
    down = directions[1]
    left = directions[2]
    right = directions[3]

    snake = data['you']['body'][0]
    height = data['board']['height']
    width = data['board']['width']
    food = data['board']['food']

    closest_food = get_closest_food(food, snake)
    tmp_food = closest_food

    # Move towards closest food, pretty up later
    if(tmp_food[0][0] > 0):
        while(tmp_food[0][0] > 0):
            return move_response(left)
    elif(tmp_food[0][0] < 0):
        while(tmp_food[0][0] < 0):
            return move_response(right)

    if(tmp_food[0][1] > 0):
        while(tmp_food[0][1] > 0):
            return move_response(up)
    elif(tmp_food[0][1] < 0):
        while(tmp_food[0][1] < 0):
            return move_response(down)

    # if(snake['x'] == 0):
    #     return move_response(down)
    # if(snake['y'] == height):
    #     return move_response(right)
    # elif(snake['x'] == width and snake['y'] == 0):
    #     return move_response(up)
    # elif(snake['y'] == 0 and snake['x'] == width):
    #     return move_response(left)


@bottle.post('/end')
def end():
    data = bottle.request.json

    """
    TODO: If your snake AI was stateful,
        clean up any stateful objects here.
    """
    print(json.dumps(data))

    return end_response()

# get_closest_food
# Parameters: list of food coordinates, snake head coordinates
# Returns: sorted list of coordinates to closest food
def get_closest_food(food, snake):
    size = len(food)
    snake_loc = (snake['x'], snake['y'])
    food_loc = []
    for i in range(size):
        x, y = food[i]['x'], food[i]['y']
        food_loc.append((x, y))
    closest_food = [((snake_loc[0]-food_loc[i][0]), (snake_loc[1]-food_loc[i][1])) for i in range(size)]

    return sorted(closest_food, key  = add_coord)

# add_coord
# Parameters: list item
# Returns: sum of coordinates
# If a number is negative, make it positive as this function serves to help sort coordinates in terms of relative position to snake    
def add_coord(item):
    tmp_x = item[0]
    tmp_y = item[1]
    if(item[0] < 0):
        tmp_x *= -1
    if(item[1] < 0):
        tmp_y *= -1
    return tmp_x + tmp_y


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '8080'),
        debug=os.getenv('DEBUG', True)
    )
