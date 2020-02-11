import json
import os
import random
import bottle

from api import ping_response, start_response, move_response, end_response

height = 0
width = 0

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

    color = "#1E86C1"
    headType = "bendr"
    tailType = "bwc-ice-skate"

    return start_response(color, headType, tailType)


@bottle.post('/move')
def move():
    global height
    global width

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

    head = data['you']['body'][0]
    snake = data['you']['body']
    height = data['board']['height']
    width = data['board']['width']
    food_list = data['board']['food']

    closest_food = get_closest_food(food_list, head)
    food = closest_food

    move = up

    # Move towards closest food, pretty up later
    for i in range(len(food)):
        if move_to_food(food[i], snake):
            return move_response(move_to_food(food[i], snake))

@bottle.post('/end')
def end():
    data = bottle.request.json

    """
    TODO: If your snake AI was stateful,
        clean up any stateful objects here.
    """
    # print(json.dumps(data))
    print(data['turn'])

    return end_response()

def move_to_food(food, snake):
    if(food[0] > 0):
        while(food[0] > 0):
            move = verify(snake, 'left')
            return move
    elif(food[0] < 0):
        while(food[0] < 0):
            move = verify(snake, 'right')
            return move
    if(food[1] > 0):
        while(food[1] > 0):
            move = verify(snake, 'up')
            return move
    elif(food[1] < 0):
        while(food[1] < 0):
            move = verify(snake, 'down')
            return move  

# verify
# Parameters: list of snake's body coordinates, the move to be verified
# Returns: a boolean value; true if the move is good to execute, false otherwise
# This function will replace verify_left/down/up/right to avoid the recursion errors with the current system.
# Instead of choosing a random direction if the move won't be succesful, when returned false the next best move will be chosen.
# This will mitigate the need for recursion, and recursion can be used only as a fallback.
def verify(snake, move):
    global height
    global width

    #THINK OF HOW TO CLEAN THIS UP
    #PRIORITIZE TURNING AWAY FROM WALLS AND FROM BODY? !? ?!!!
    if(move == 'left' and verify_move('left', snake, height, width) == True):
        return 'left'
    elif(decide_direction_self(snake) != False and verify_move(decide_direction_self(snake), snake, height, width) == True):
        return decide_direction_self(snake)
    if(decide_direction_wall(snake, 0) != False and verify_move(decide_direction_wall(snake, 0), snake, height, width) == True):
        print("TRYING TO MOVE AWAY FROM WALL")
        return decide_direction_wall(snake, 0)
    elif(decide_direction_wall(snake, 1) != False and verify_move(decide_direction_wall(snake, 1), snake, height, width) == True):
        print("TRYING TO MOVE AWAY FROM WALL")
        return decide_direction_wall(snake, 1)

    elif(move == 'left' and verify_move('right', snake, height, width) == True):
        return 'right'
    elif(move == 'left' and verify_move('up', snake, height, width) == True):
        return 'up'
    elif(move == 'left' and verify_move('down', snake, height, width) == True):
        return 'down'

    if(move == 'right' and verify_move('right', snake, height, width) == True):
        return 'right'
    elif(decide_direction_self(snake) != False and verify_move(decide_direction_self(snake), snake, height, width) == True):
        return decide_direction_self(snake)
    if(decide_direction_wall(snake, 0) != False and verify_move(decide_direction_wall(snake, 0), snake, height, width) == True):
        print("TRYING TO MOVE AWAY FROM WALL")
        return decide_direction_wall(snake, 0)
    elif(decide_direction_wall(snake, 1) != False and verify_move(decide_direction_wall(snake, 1), snake, height, width) == True):
        print("TRYING TO MOVE AWAY FROM WALL")
        return decide_direction_wall(snake, 1)

    elif(move == 'right' and verify_move('left', snake, height, width) == True):
        return 'left'
    elif(move == 'right' and verify_move('up', snake, height, width) == True):
        return 'up'
    elif(move == 'right' and verify_move('down', snake, height, width) == True):
        return 'down'

    if(move == 'up' and verify_move('up', snake, height, width) == True):
        return 'up'
    elif(decide_direction_self(snake) != False and verify_move(decide_direction_self(snake), snake, height, width) == True):
        return decide_direction_self(snake)
    if(decide_direction_wall(snake, 0) != False and verify_move(decide_direction_wall(snake, 0), snake, height, width) == True):
        print("TRYING TO MOVE AWAY FROM WALL")
        return decide_direction_wall(snake, 0)
    elif(decide_direction_wall(snake, 1) != False and verify_move(decide_direction_wall(snake, 1), snake, height, width) == True):
        print("TRYING TO MOVE AWAY FROM WALL")
        return decide_direction_wall(snake, 1)

    elif(move == 'up' and verify_move('right', snake, height, width) == True):
        return 'right'
    elif(move == 'up' and verify_move('left', snake, height, width) == True):
        return 'left'
    elif(move == 'up' and verify_move('down', snake, height, width) == True):
        return 'down'

    if(move == 'down' and verify_move('down', snake, height, width) == True):
        return 'down'
    elif(decide_direction_self(snake) != False and verify_move(decide_direction_self(snake), snake, height, width) == True):
        return decide_direction_self(snake)
    if(decide_direction_wall(snake, 0) != False and verify_move(decide_direction_wall(snake, 0), snake, height, width) == True):
        print("TRYING TO MOVE AWAY FROM WALL")
        return decide_direction_wall(snake, 0)
    elif(decide_direction_wall(snake, 1) != False and verify_move(decide_direction_wall(snake, 1), snake, height, width) == True):
        print("TRYING TO MOVE AWAY FROM WALL")
        return decide_direction_wall(snake, 1)

    elif(move == 'down' and verify_move('right', snake, height, width) == True):
        return 'right'
    elif(move == 'down' and verify_move('up', snake, height, width) == True):
        return 'up'
    elif(move == 'down' and verify_move('left', snake, height, width) == True):
        return 'left'

# verify_move
# Parameters: move to make, list of snake's body coordinates
# Returns: the appropriate move to make
# Fist checks to see if the snake can turn left, if not find an appropriate move
def verify_move(move, snake, h, w):
    head = snake[0]
    snake_len = len(snake)

    if(move == 'left'):
        left_move = head.copy()
        left_move['x'] -= 1
        if(left_move['x'] == -1):   #wall
            print("almost collided with wall, left")
            return False
        for i in range(snake_len):  #body
            if(left_move == snake[i]):
                print("almost collided with self, left", left_move, snake[i])
                return False
        return True

    elif(move == 'right'):
        head = snake[0]
        snake_len = len(snake)
        right_move = head.copy()
        right_move['x'] += 1
        if(right_move['x'] == w):   #wall
            print("almost collided with wall, right")
            return False
        for i in range(snake_len):  #body
            if(right_move == snake[i]):
                print("almost collided with self, right", right_move, snake[i])
                return False
        return True

    elif(move == 'up'):
        up_move = head.copy()
        up_move['y'] -= 1
        if(up_move['y'] == -1):   #wall
            print("almost collided with wall, up")
            return False
        for i in range(snake_len):  #body
            if(up_move == snake[i]):
                print("almost collided with self, up", up_move, snake[i])
                return False
        return True
    
    elif(move == 'down'):
        down_move = head.copy()
        down_move['y'] += 1
        if(down_move['y'] == h):   #wall
            print("almost collided with wall, down")
            return False
        for i in range(snake_len):  #body
            if(down_move == snake[i]):
                print("almost collided with self, down", down_move, snake[i])
                return False
        return True

# DEPRECATED VERIFY FUNCTIONS, NOW IN VERIFY_MOVE

# verify_left
# Parameters: list of snake's body coordinates
# Returns: the appropriate move to make
# Fist checks to see if the snake can turn left, if not find an appropriate move
# def verify_left(snake, h, w):
#     head = snake[0]
#     snake_len = len(snake)
#     left_move = head.copy()
#     left_move['x'] -= 1
#     if(left_move['x'] == -1):   #wall
#         print("almost collided with wall, left")
#         return False
#     for i in range(snake_len):  #body
#         if(left_move == snake[i]):
#             print("almost collided with self, left", left_move, snake[i])
#             return False
#     return True
#     #OTHER SNAKE

# # verify_left
# # Parameters: list of snake's body coordinates
# # Returns: the appropriate move to make
# # Fist checks to see if the snake can turn left, if not find an appropriate move
# def verify_right(snake, h, w):
#     head = snake[0]
#     snake_len = len(snake)
#     right_move = head.copy()
#     right_move['x'] += 1
#     if(right_move['x'] == w):   #wall
#         print("almost collided with wall, right")
#         return False
#     for i in range(snake_len):  #body
#         if(right_move == snake[i]):
#             print("almost collided with self, right", right_move, snake[i])
#             return False
#     return True
#     #OTHER SNAKE

# # verify_left
# # Parameters: list of snake's body coordinates
# # Returns: the appropriate move to make
# # Fist checks to see if the snake can turn left, if not find an appropriate move
# def verify_up(snake, h, w):
#     head = snake[0]
#     snake_len = len(snake)
#     up_move = head.copy()
#     up_move['y'] -= 1
#     if(up_move['y'] == -1):   #wall
#         print("almost collided with wall, up")
#         return False
#     for i in range(snake_len):  #body
#         if(up_move == snake[i]):
#             print("almost collided with self, up", up_move, snake[i])
#             return False
#     return True
#     #OTHER SNAKE

# # verify_left
# # Parameters: list of snake's body coordinates
# # Returns: the appropriate move to make
# # Fist checks to see if the snake can turn left, if not find an appropriate move
# def verify_down(snake, h, w):
#     head = snake[0]
#     snake_len = len(snake)
#     down_move = head.copy()
#     down_move['y'] += 1
#     if(down_move['y'] == h):   #wall
#         print("almost collided with wall, down")
#         return False
#     for i in range(snake_len):  #body
#         if(down_move == snake[i]):
#             print("almost collided with self, down", down_move, snake[i])
#             return False
#     return True
#     #OTHER SNAKE

# decide_direction_wall
# Parameters: coordinates of self
# if near wall, try and go away
def decide_direction_wall(snake, try_flag):
    global height
    global width

    head = snake[0]

    # TOP RIGHT OR LEFT CORNER, TRY TO GO TO MIDDLE HORIZONTALLY. IF ALREADY TRIED, TRY DOWN.
    if((width - head['x']) < 1 and head['y'] < 1 and try_flag == 0):
        return 'left'
    elif(head['x'] < 1 and head['y'] < 1 and try_flag == 0):
        return 'right'
    elif((((width - head['x'] < 1) and head['y'] < 1) or (head['x'] < 1 and head['y'] < 1)) and try_flag == 1):
        return 'down'

    # BOTTOM RIGHT OR LEFT CORNER, TRY TO GO TO MIDDLE HORIZONTALLY. IF ALREADY TRIED, TRY UP.
    if((width - head['x']) < 1 and (height - head['y']) < 1 and try_flag == 0):
        return 'left'
    elif(head['x'] < 1 and (height - head['y']) < 1 and try_flag == 0):
        return 'right'
    elif(((width - head['x'] < 1 and (height - head['y']) < 1) or (head['x'] < 1 and (height - head['y']) < 1)) and try_flag == 1):
        return 'up'

    # NEAR BOTTOM or NEAR TOP
    if(height - head['y'] < 1):
        return 'up'
    elif(head['y'] < 1):
        return 'down'

    # NEAR LEFT or RIGHT
    if(width - head['x'] < 1):
        return 'left'
    elif(head['x'] < 1):
        return 'right'

    return False

# decide_direction_self
# Parameters: coordinates of self
# if near self, try and go away
def decide_direction_self(snake):
    global width
    global height

    head = snake[0]
    avg_snake = [0, 0]
    snake_len = len(snake)

    #CHECK WHICH QUADRANT IT'S IN, THEN MOVE AWAY FROM AVG SNAKE LOCATION BASED ON THAT
    for i in range(snake_len):
        avg_snake[0] += snake[i]['x'] 
        avg_snake[1] += snake[i]['y']
    avg_snake[0] /= snake_len
    avg_snake[1] /= snake_len
    # print(avg_snake, "AVERAGE----------!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    if(head['x'] > width/2):
        if(head['x'] > avg_snake[0]):
            return 'right'
    elif(head['x'] < width/2):
        if(head['x'] > avg_snake[0]):
            return 'right'
        elif(head['y'] > avg_snake[1]):
            return 'down'
    # elif(head['x'] < avg_snake[0]):
    #     return 'left'
    # elif(head['y'] < avg_snake[1]):
    #     return 'up'
        

    return False

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
