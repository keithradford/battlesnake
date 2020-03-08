import json
import os
import random
import bottle

from api import ping_response, start_response, move_response, end_response

height = 0
width = 0
optimal_size = 3

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

    color = "#"
    headType = "bwc-bonhomme"
    tailType = "skinny"

    return start_response(color, headType, tailType)


@bottle.post('/move')
def move():
    global height
    global width
    global optimal_size
    global opp_head
    global name

    data = bottle.request.json

    """
    TODO: Using the data from the endpoint request object, your
            snake AI must choose a direction to move in.
    """
    # print(json.dumps(data))
    print("TURN#", data['turn'])

    name = data['you']['name']
    directions = ['up', 'down', 'left', 'right']
    direction = directions[1]
    up = directions[0]
    down = directions[1]
    left = directions[2]
    right = directions[3]

    head = data['you']['body'][0]
    snake = data['you']['body']
    snake_len = len(snake)
    height = data['board']['height']
    width = data['board']['width']
    food_list = data['board']['food']
    opponents = data['board']['snakes']
 
    closest_opponent = get_closest_opponent(opponents, snake)
    opp_list = sanitize_opponents(opponents, snake)
    # print(opp_list)
    # print("Opponents relative to me", closest_opponent)
    food = get_closest_food(food_list, head)
    opp_head = opponents_heads(opponents, snake)

    move = up

    # Goes through list of closest food, incase it cannot move to the closest food. Should improve this, works for now.
    # Eventually move_to_food will be replaced with move_away_from_opponent as the first play called.
    # Try and deprecate current verification steps and put them up here in more organized fashion.
    # ^^^ After the algorithms work..!s

    if(snake_len <= optimal_size or data['you']['health'] < 20):
        for i in range(len(food)):
            if move_to_food(food[i], snake, opp_list):
                return move_response(verify(snake, move_to_food(food[i], snake, opp_list), opp_list))
    elif(random.randint(0, 100) > 95):
        # print("bog lottery winnnner")
        # print("verify random")
        return move_response(verify(snake, random.choice(directions), opp_list))
    elif(verify(snake, decide_direction_self(snake, opp_list), opp_list) != False):
        # print("I'm already pretty big, I don' tneed food. Let me move away from myself")
        # print("verify self")
        return move_response(verify(snake, decide_direction_self(snake, opp_list), opp_list))
    elif(verify(snake, decide_direction_wall(snake, 0), opp_list) != False):
        # print("I'm already pretty big, I don' tneed food. Let me move away from the wall")
        # print("verify wall")
        return move_response(verify(snake, decide_direction_wall(snake, 0), opp_list))
    else:
        # print("got nothing go for food")
        for i in range(len(food)):
            if move_to_food(food[i], snake, opp_list):
                return move_response(move_to_food(food[i], snake, opp_list))

    # print("verify random")
    return move_response(random.choice(directions))

@bottle.post('/end')
def end():
    data = bottle.request.json

    """
    TODO: If your snake AI was stateful,
        clean up any stateful objects here.
    """
    print(json.dumps(data))

    return end_response()

def move_away_from_opp(opponents, snake):
    pass

def move_to_food(food, snake, opponents):
    if(food[0] > 0):
        while(food[0] > 0):
            # print("verify left")
            return verify(snake, 'left', opponents)
    elif(food[0] < 0):
        while(food[0] < 0):
            # print("verify right")
            return verify(snake, 'right', opponents)
    if(food[1] > 0):
        while(food[1] > 0):
            # print("verify up")
            return verify(snake, 'up', opponents)
    elif(food[1] < 0):
        while(food[1] < 0):
            # print("verify down")
            return verify(snake, 'down', opponents)  

# verify (possibly rename to better fit it's function)
# Parameters: List of the snake's body coordinates, the move to be verified
# Returns: Final decision for the current turn's direction
# Current function:
# Based on the move being passed into the function (likely moving towards food) follows set amount of steps:
# 1. Can it go this direction at all (no wall, won't go into itself)? If it can it should. Later want to decide if that's even an optimal move... for now it's #1 decision
# 2. Can it move a direction that will **likely** not corner itself?
# 3/4. Can it try and move away from the wall? This won't happen much, but as a "last resort" it tries to move to the center of the map. Needs a revamp, should only really happen if no food is near.
# 5. Just go wherever it can. Also needs a revamp, don't want it to check in order of the directions I placed down but rather check in order of what makes sense based on it's position, similar/merge with step 2.
#
# If decide_direction_self can be optimized to an ideal point, it should take priority over going towards food. Especially If it's already pretty big.
def verify(snake, move, opponents):
    global height
    global width

    # print("I WANT TO MOVE:", move)

    if(move == 'left'):
        if(verify_move('left', snake, height, width, opponents) == True):
            # print("TURN TO FOOD", snake[0]['x'], snake[0]['y'])
            return 'left'
        elif(decide_direction_self(snake, opponents) != False and verify_move(decide_direction_self(snake, opponents), snake, height, width, opponents) == True):
            # print("MOVE AWAY FROM SELF", snake[0]['x'], snake[0]['y'])
            return decide_direction_self(snake, opponents)
        elif(decide_direction_wall(snake, 0) != False and verify_move(decide_direction_wall(snake, 0), snake, height, width, opponents) == True):
            # print("TRYING TO MOVE AWAY FROM WALL", snake[0]['x'], snake[0]['y'])
            return decide_direction_wall(snake, 0)
        elif(decide_direction_wall(snake, 1) != False and verify_move(decide_direction_wall(snake, 1), snake, height, width, opponents) == True):
            # print("TRYING TO MOVE AWAY FROM WALL", snake[0]['x'], snake[0]['y'])
            return decide_direction_wall(snake, 1)

        elif(move == 'left' and verify_move('right', snake, height, width, opponents) == True):
            return 'right'
        elif(move == 'left' and verify_move('up', snake, height, width, opponents) == True):
            return 'up'
        elif(move == 'left' and verify_move('down', snake, height, width, opponents) == True):
            return 'down'

    elif(move == 'right'):
        if(verify_move('right', snake, height, width, opponents) == True):
            # print("TURN TO FOOD", snake[0]['x'], snake[0]['y'])
            return 'right'
        elif(decide_direction_self(snake, opponents) != False and verify_move(decide_direction_self(snake, opponents), snake, height, width, opponents) == True):
            # print("MOVE AWAY FROM SELF", snake[0]['x'], snake[0]['y'])
            return decide_direction_self(snake, opponents)
        elif(decide_direction_wall(snake, 0) != False and verify_move(decide_direction_wall(snake, 0), snake, height, width, opponents) == True):
            # print("TRYING TO MOVE AWAY FROM WALL", snake[0]['x'], snake[0]['y'])
            return decide_direction_wall(snake, 0)
        elif(decide_direction_wall(snake, 1) != False and verify_move(decide_direction_wall(snake, 1), snake, height, width, opponents) == True):
            # print("TRYING TO MOVE AWAY FROM WALL", snake[0]['x'], snake[0]['y'])
            return decide_direction_wall(snake, 1)

        elif(move == 'right' and verify_move('left', snake, height, width, opponents) == True):
            return 'left'
        elif(move == 'right' and verify_move('up', snake, height, width, opponents) == True):
            return 'up'
        elif(move == 'right' and verify_move('down', snake, height, width, opponents) == True):
            return 'down'

    elif(move == 'up'):
        if(verify_move('up', snake, height, width, opponents) == True):
            # print("TURN TO FOOD", snake[0]['x'], snake[0]['y'])
            return 'up'
        elif(decide_direction_self(snake, opponents) != False and verify_move(decide_direction_self(snake, opponents), snake, height, width, opponents) == True):
            print("MOVE AWAY FROM SELF", snake[0]['x'], snake[0]['y'])
            # return decide_direction_self(snake, opponents)
        elif(decide_direction_wall(snake, 0) != False and verify_move(decide_direction_wall(snake, 0), snake, height, width, opponents) == True):
            # print("TRYING TO MOVE AWAY FROM WALL", snake[0]['x'], snake[0]['y'])
            return decide_direction_wall(snake, 0)
        elif(decide_direction_wall(snake, 1) != False and verify_move(decide_direction_wall(snake, 1), snake, height, width, opponents) == True):
            # print("TRYING TO MOVE AWAY FROM WALL", snake[0]['x'], snake[0]['y'])
            return decide_direction_wall(snake, 1)

        elif(move == 'up' and verify_move('right', snake, height, width, opponents) == True):
            return 'right'
        elif(move == 'up' and verify_move('left', snake, height, width, opponents) == True):
            return 'left'
        elif(move == 'up' and verify_move('down', snake, height, width, opponents) == True):
            return 'down'

    elif(move == 'down'):
        if(verify_move('down', snake, height, width, opponents) == True):
            # print("TURN TO FOOD", snake[0]['x'], snake[0]['y'])
            return 'down'
        elif(decide_direction_self(snake, opponents) != False and verify_move(decide_direction_self(snake, opponents), snake, height, width, opponents) == True):
            # print("MOVE AWAY FROM SELF", snake[0]['x'], snake[0]['y'])
            return decide_direction_self(snake, opponents)
        elif(decide_direction_wall(snake, 0) != False and verify_move(decide_direction_wall(snake, 0), snake, height, width, opponents) == True):
            # print("TRYING TO MOVE AWAY FROM WALL", snake[0]['x'], snake[0]['y'])
            return decide_direction_wall(snake, 0)
        elif(decide_direction_wall(snake, 1) != False and verify_move(decide_direction_wall(snake, 1), snake, height, width, opponents) == True):
            # print("TRYING TO MOVE AWAY FROM WALL", snake[0]['x'], snake[0]['y'])
            return decide_direction_wall(snake, 1)

        elif(move == 'down' and verify_move('right', snake, height, width, opponents) == True):
            return 'right'
        elif(move == 'down' and verify_move('up', snake, height, width, opponents) == True):
            return 'up'
        elif(move == 'down' and verify_move('left', snake, height, width, opponents) == True):
            return 'left'

    return False

# verify_move
# Parameters: Move to make, list of snake's body coordinates
# Returns: Boolean value based on the ability to make this move
# Checks if the move will turn the snake into a wall, then if it will turn the snake into itself.
# Will add verification of turning into other snakes.
# If all tests pass, return True.
def verify_move(move, snake, h, w, opponents):
    global opp_head
    global name
    possible_x = {}
    possible_y = {}
    print(opp_head[0][0])
    head = snake[0]
    snake_len = len(snake)
    opp_len = len(opponents)
    possible = []
    i = 0
    possible.extend([{'x':opp_head[i][0], 'y':opp_head[i][1] + 1} for i in range(len(opp_head))])#up
    i = 0
    possible.extend([{'x':opp_head[i][0], 'y':opp_head[i][1] - 1} for i in range(len(opp_head))])#down
    i = 0
    possible.extend([{'x':opp_head[i][0] - 1, 'y':opp_head[i][1]} for i in range(len(opp_head))])#left
    i = 0
    possible.extend([{'x':opp_head[i][0] + 1, 'y':opp_head[i][1]} for i in range(len(opp_head))])#right
    print("POSSIBLE HEADS", possible, name)
    # Rather make a list of coordinates of all the possible positions the head can be so don't  have to zip them together down the line.
    
    # print("X", possible_x, "Y", possible_y)
    for j in range(opp_len):  #opponent
        possible.append({'x': opponents[j][0], 'y': opponents[j][1]})
    print("POSSIBLE", possible, name)

    if(move == 'left'):
        left_move = head.copy()
        left_move['x'] -= 1
        print("try to move:", left_move)
        if(left_move['x'] == -1 or left_move in possible or left_move in snake):
            return False
        return True

    elif(move == 'right'):
        right_move = head.copy()
        right_move['x'] += 1
        print("try to move:", right_move)
        if(right_move['x'] == w or right_move in possible or right_move in snake):
            return False 
        return True

    elif(move == 'up'):
        up_move = head.copy()
        up_move['y'] -= 1
        print("try to move:", up_move)
        if(up_move['y'] == -1 or up_move in possible or up_move in snake):
            return False
        return True
    
    elif(move == 'down'):
        down_move = head.copy()
        down_move['y'] += 1
        print("try to move:", down_move)
        if(down_move['y'] == h or down_move in possible or down_move in snake):
            return False
        return True

# decide_direction_wall
# Parameters: Coordinates of self
# Returns: A direction to try and leave the proximity of a corner/wall
# Checks if the position of the snakes head is in a corner or near a wall, will try and make an appropriate move based on it's corner.
# Returns False if not near a wall.
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

#-----------------------
# BIGGEST PRIORITY!!!!! |
#-----------------------
# decide_direction_self
# Parameters: Coordinates of self
# Returns: A direction to move away from itself, False if it's in a good position.
# The algorithm checks where the snakes head is with respect to the average x and y location of the rest of it's body,
# Based on this result and the quadrant of the board the snake is in, it will try and determine an appropriate move to minimize the likelyhood of cornering itself.
# Function only really needed when the snake is much bigger, somehwere > 10.
# See comments in function for further improvement plan.
def decide_direction_self(snake, opponents):
    global width
    global height
    global optimal_size

    head = snake[0]
    avg_snake = [0, 0]
    snake_len = len(snake)

    # TO DO: IF FIRST OPTION AND FALLBACK OPTION FAIL: VERIFY THE NEXT MOVE VIA IT'S ABILITY TO MOVE AFTER THAT MOVE. AVOID THE 1 BLOCK KILLER
    for i in range(snake_len):
        avg_snake[0] += snake[i]['x'] 
        avg_snake[1] += snake[i]['y']
    avg_snake[0] /= snake_len
    avg_snake[1] /= snake_len

    buff = snake_len / 5

    check_x = head['x'] - avg_snake[0]
    check_y = head['y'] - avg_snake[1]
    if(check_x < 0):
        check_x *= -1
    if(check_y < 0):
        check_y *= -1

    if(check_x > check_y and snake_len > optimal_size and x_first(snake, avg_snake, buff, opponents) != False and verify_move(x_first(snake, avg_snake, buff, opponents), snake, height, width, opponents) == True):
        return x_first(snake, avg_snake, buff, opponents)
    elif(check_x > check_y and snake_len > optimal_size and y_first(snake, avg_snake, buff, opponents) != False and verify_move(y_first(snake, avg_snake, buff, opponents), snake, height, width, opponents) == True):
        # print('go to y now')
        return y_first(snake, avg_snake, buff, opponents)
    elif(check_y > check_x and snake_len > optimal_size and y_first(snake, avg_snake, buff, opponents) != False and verify_move(y_first(snake, avg_snake, buff, opponents), snake, height, width, opponents) == True):
        return y_first(snake, avg_snake, buff, opponents)
    elif(check_y > check_x and snake_len > optimal_size and x_first(snake, avg_snake, buff, opponents) != False and verify_move(x_first(snake, avg_snake, buff, opponents), snake, height, width, opponents) == True):
        # print('go to x now')
        return x_first(snake, avg_snake, buff, opponents)

    return False


def x_first(snake, avg_snake, buff, opponents):
    global width
    global height

    head = snake[0]

    print("Doing X first")
    if(avg_snake[0] >= width/2 and avg_snake[1] >= height/2): #bottom right
        # print("bottom right")
        if(head['x'] > avg_snake[0] - buff and verify_move('left', snake, height, width, opponents) == True):
            return 'left'
    elif(avg_snake[0] >= width/2 and avg_snake[1] <= height/2): #top right
        # print("top right")
        if(head['x'] > avg_snake[0] - buff and verify_move('left', snake, height, width, opponents) == True):
            return 'left'
    elif(avg_snake[0] <= width/2 and avg_snake[1] >= height/2 and verify_move('right', snake, height, width, opponents) == True): #bottom left
        # print("bottom left")
        if(head['x'] < avg_snake[0] + buff): 
            return 'right'
    elif(avg_snake[0] <= width/2 and avg_snake[1] <= height/2 and verify_move('right', snake, height, width, opponents) == True): #top left
        # print("top left")
        if(head['x'] < avg_snake[0] + buff):
            return 'right'
    # print('in x false next')

    return False

def y_first(snake, avg_snake, buff, opponents):
    global width
    global height

    head = snake[0]

    print("Doing Y first")
    if(avg_snake[0] >= width/2 and avg_snake[1] >= height/2 and verify_move('up', snake, height, width, opponents) == True): #bottom right
        # print("bottom right")
        if(head['y'] > avg_snake[1] - buff):
            return 'up'
    elif(avg_snake[0] >= width/2 and avg_snake[1] <= height/2 and verify_move('down', snake, height, width, opponents) == True): #top right
        # print("top right")
        if(head['y'] < avg_snake[1] + buff):
            return 'down'
    elif(avg_snake[0] <= width/2 and avg_snake[1] >= height/2 and verify_move('up', snake, height, width, opponents) == True): #bottom left
        # print("bottom left")
        if(head['y'] > avg_snake[1] - buff):
            return 'up'
    elif(avg_snake[0] <= width/2 and avg_snake[1] <= height/2 and verify_move('down', snake, height, width, opponents) == True): #top left
        # print("top left")
        if(head['y'] < avg_snake[1] + buff):
            return 'down'
    # print('in y false next')

    return False

def sanitize_opponents(opponents, snake):
    opp_amount = len(opponents)
    snake_len = len(snake)
    head = snake[0]
    snake_loc = (head['x'], head['y'])
    opp_loc = []
    curr_size = 0
    for i in range(opp_amount):
        curr_size = len(opponents[i]['body'])
        for j in range(curr_size):
            x, y = opponents[i]['body'][j]['x'], opponents[i]['body'][j]['y']
            opp_loc.append((x, y))
    to_ret = [
        coord for coord in opp_loc 
        if coord not in [(snake[i]['x'], snake[i]['y']) 
        for i in range(snake_len)]
    ]
    return to_ret

def opponents_heads(opponents, snake):
    opp_amount = len(opponents)
    snake_len = len(snake)
    head = snake[0]
    snake_loc = (head['x'], head['y'])
    opp_loc = []
    for i in range(opp_amount):
        x, y = opponents[i]['body'][0]['x'], opponents[i]['body'][0]['y']
        opp_loc.append((x, y))
    heads = [
        coord for coord in opp_loc 
        if coord not in [(snake[i]['x'], snake[i]['y']) 
        for i in range(snake_len)]
    ]
    return heads

# get_closest_opponent
# Parameters: List of opponents, snake head coordinates
# Returns: Sorted list of steps to an opponent. Order is closest to furthest.
def get_closest_opponent(opponents, snake):
    opp_amount = len(opponents)
    snake_len = len(snake)
    head = snake[0]
    snake_loc = (head['x'], head['y'])
    opp_loc = []
    curr_size = 0
    opponent_size = 0
    for i in range(opp_amount):
        curr_size = len(opponents[i]['body'])
        for j in range(curr_size):
            x, y = opponents[i]['body'][j]['x'], opponents[i]['body'][j]['y']
            opp_loc.append((x, y))
            opponent_size += 1
    opponent_size -= snake_len
    enemy = [
        coord for coord in opp_loc 
        if coord not in [(snake[i]['x'], snake[i]['y']) 
        for i in range(snake_len)]
    ]

    closest_opp = [((snake_loc[0]-enemy[i][0]), (snake_loc[1]-enemy[i][1])) for i in range(opponent_size)]

    return sorted(closest_opp, key = add_coord)
    

# get_closest_food
# Parameters: List of food coord inates, snake head coordinates
# Returns: Sorted list of steps to take to food. Order is closest food to furthest.
def get_closest_food(food, snake):
    size = len(food)
    snake_loc = (snake['x'], snake['y'])
    food_loc = []
    for i in range(size):
        x, y = food[i]['x'], food[i]['y']
        food_loc.append((x, y))
        #todo
    closest_food = [((snake_loc[0]-food_loc[i][0]), (snake_loc[1]-food_loc[i][1])) for i in range(size)]

    return sorted(closest_food, key = add_coord)

# add_coord
# Parameters: Tuple with 2 elements.
# Returns: Sum of "coordinates".
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
