from tkinter import *
import random

# MODEL VIEW CONTROLLER (MVC)
####################################
# MODEL:       the data
# VIEW:        redrawAll and its helper functions
# CONTROLLER:  event-handling functions and their helper functions
####################################

def init(data):
    # load data as appropriate
    data.rows, data.cols = 8,15
    data.headRow = data.rows//2
    data.headCol = data.cols//2
    initBoard(data)
    data.dir = (1,0)
    placeFood(data)
    data.isGameOver = False
    data.margin = 100
    data.isIgnoreStep = False
    data.isPaused = False
    data.score = 0 
    data.highscores = []
    data.highScoreLimit = 3
    #'first' is a boolean that allows the score to be appended to the 
    #'highscores' list only once 
    data.first = True
    data.numOfFood = 0
    #number of food needed to go to Level 2
    data.level2Threshold = 3 
    #total number of moves
    data.moves = 0 
    #number of moves needed for bonus points at the end of level 1
    data.moveThreshold = 20
    data.walls = 0
    data.timerDelay = 400
    
def placeFood(data):
    r = random.randint(0, data.rows-1)
    c = random.randint(0, data.cols-1)
    #generates random coordinates that are not part of snake
    while (data.board[r][c] != 0): 
        r = random.randint(0, data.rows-1)
        c = random.randint(0, data.cols-1)
    data.board[r][c] = -1
    
def placePoison(data):
    r = random.randint(0, data.rows-1)
    c = random.randint(0, data.cols-1)
    drow, dcol = data.dir
    newHeadRow = data.headRow + drow
    newHeadCol = data.headCol + dcol
    #generates random coordinates that are not part of snake or food 
    #and are not right in front of snake 
    while (data.board[r][c] != 0 and r != newHeadRow and c != newHeadCol):
        r = random.randint(0, data.rows-1)
        c = random.randint(0, data.cols-1)
    data.board[r][c] = -2

def deletePoison(data):
    for row in range(data.rows):
        for col in range(data.cols):
            if data.board[row][col] == -2:
                data.board[row][col] = 0
    
def initBoard(data):
    data.board = []
    #initializes an empty board and snake position
    for row in range(data.rows):
        data.board.append([0] * data.cols)
    data.board[data.headRow][data.headCol] = 1

# These are the CONTROLLERs.
def mousePressed(event, data):
    cellW = (data.width-2*data.margin)/data.cols
    cellH = (data.height-2*data.margin)/data.rows
    if data.isPaused:
        #calculates col and row coordinates of mouse click
        col = int((event.x-data.margin)//cellW)
        row = int((event.y-data.margin)//cellH) 
        #checks if mousePress is on board 
        if (row < data.rows and col < data.cols and 
            row >= 0 and col >= 0 and 
            data.board[row][col] == 0):
            
            data.board[row][col] = -3 #create wall on cell when clicked
            data.walls += 1
    
def keyPressed(event, data):            
    #'p' pauses and unpauses
    if (event.keysym == 'p'): data.isPaused = not data.isPaused
   
    #if paused, key presses should not be able to control anything
    if data.isPaused:
        return
    
    # restarts game with 'r'
    if event.keysym == 'r':
        temp = [] + data.highscores
        init(data)
        data.highscores = [] + temp
            
    #arrow keys control movment
    if (event.keysym == 'Up'): data.dir = (-1, 0)
    elif (event.keysym == 'Down'): data.dir = (1, 0)
    elif (event.keysym == 'Left'): data.dir = (0, -1)
    elif (event.keysym == 'Right'): data.dir = (0, 1)
    takeStep(data)
    data.isIgnoreStep = True


def timerFired(data):
    #do nothing if paused
    if data.isPaused:
        return 
    #take steps if not paused and if game is not over
    if not data.isPaused or not data.isGameOver:
        if (data.isIgnoreStep):
            data.isIgnoreStep = False
        else:
            takeStep(data)
    
    #append score to 'highscore' list when game ends 
    if data.isGameOver and data.first:
        data.highscores.append(data.score)
        if len(data.highscores) > data.highScoreLimit:
            data.highscores.remove(min(data.highscores))
        data.highscores = sorted(data.highscores)
        data.first = False 

def takeStep(data):
    #snake goes in direction
    drow, dcol = data.dir
    newHeadRow = data.headRow + drow
    newHeadCol = data.headCol + dcol
    
    # snake moves off board or hits self
    if (newHeadRow < 0 or newHeadRow >= data.rows or 
        newHeadCol < 0 or newHeadCol >= data.cols or 
        data.board[newHeadRow][newHeadCol] > 0):
        data.isGameOver = True
        return
    
    if (data.board[newHeadRow][newHeadCol] == -3 ): #wall
        takeStepWall(data, newHeadRow, newHeadCol)
        
    elif (data.board[newHeadRow][newHeadCol] == -2 ): #poison
        moveForward(data, newHeadRow, newHeadCol)
        data.isGameOver = True
        
    elif (data.board[newHeadRow][newHeadCol] == -1 ): #food
        takeStepFood(data, newHeadRow, newHeadCol)
        
    elif (data.board[newHeadRow][newHeadCol] == 0): #normal moving
        moveForward(data, newHeadRow, newHeadCol)
        removeTail(data)
    
    incrementMoves(data)

def takeStepWall(data, newHeadRow, newHeadCol): 
    #specific actions for if step taken into wall
    moveForward(data, newHeadRow, newHeadCol)
    data.score -= 1
    data.walls -= 1
    removeTail(data) #decrease in length
    removeTail(data) #continuous moving
    if data.score < 0: data.isGameOver = True
    
def takeStepFood(data, newHeadRow, newHeadCol): 
    #specific actions for if step taken into food
    moveForward(data, newHeadRow, newHeadCol)
    data.score += 1
    if data.score == data.level2Threshold:
        placePoison(data)
        #bonus
        if data.moves >= data.moveThreshold: data.score += 1
    if data.score > data.level2Threshold:
        deletePoison(data)
        placePoison(data)
    data.numOfFood += 1
    placeFood(data)

def incrementMoves(data):
    #finds number of moves while walls exist
    if data.walls > 0:
        data.moves += 1
    elif data.walls == 0:
        data.moves = 0
        
def moveForward(data, newHeadRow, newHeadCol):
    #moves snake in proper direction and changes coordinates
    data.board[newHeadRow][newHeadCol] = \
            data.board[data.headRow][data.headCol] + 1
    data.headRow = newHeadRow
    data.headCol = newHeadCol

def removeTail(data):
    #removes tail while snake moving forward so that snake is same length
    for row in range(data.rows):
        for col in range(data.cols):
            if data.board[row][col] > 0:
                data.board[row][col] -= 1

# This is the VIEW
def redrawAll(canvas, data):
    # canvas when game is over
    if (data.isGameOver):
        canvas.create_text(data.width/2, data.height/20, 
                           text = 'Press "r" for a new game!')
        canvas.create_text(data.width/2, data.height/10, text = 'High Scores:')
        for i in range(len(data.highscores)):
            length = len(data.highscores)
            canvas.create_text(data.width/2, 
                               (data.height/10)+(20*(i+1)), 
                               text = str(data.highscores[length-i-1]))
        return 
    
    #draws board and score if game is not over
    drawBoard(canvas, data)
    canvas.create_text(data.width/2, data.margin/2, 
                       text = 'Score: ' + str(data.score))
def drawBoard(canvas, data):
    #draws every cell in the board
    for row in range(data.rows):
        for col in range(data.cols):
            drawSnakeCell(canvas, data, row, col)
        
def drawSnakeCell(canvas, data, row, col):
    #draws individual cell
    margin = data.margin
    w = data.width - 2 * margin
    h = data.height - 2 * margin
    cellW = w / data.cols
    cellH = h / data.rows
    x0 = cellW * col
    y0 = cellH * row
    x1 = cellW * (col + 1)
    y1 = cellH * (row + 1)
    
    fill = determineCellColor(data, row, col)
    canvas.create_rectangle(x0+margin,y0+margin,x1+margin,y1+margin, fill=fill)

def determineCellColor(data, row, col):
    #when paused, cells are dimmer colors 
    
    #background
    if data.isPaused: fill = 'gray90'
    else: fill = "white"
    
    #snake cell
    if (data.board[row][col] > 0): fill= "black"
    #food cell
    elif (data.board[row][col] == -1): 
        if data.isPaused:
            fill = 'green4'
        else:
            fill = "green"
    #poison cell
    elif (data.board[row][col] == -2): 
        if data.isPaused:
            fill = 'red4'
        else:
            fill = 'red'
    #wall cell
    elif (data.board[row][col] == -3): 
        if data.isPaused:
            fill = 'brown4'
        else:
            fill = 'brown'
            
    return fill

def run(width=300, height=300):
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        redrawAll(canvas, data)
        canvas.update()    

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        redrawAllWrapper(canvas, data)
        # pause, then call timerFired again
        if data.numOfFood >= data.level2Threshold:
            data.timerDelay = 200
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
        
    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    data.timerDelay = 400 # milliseconds
    init(data)
    # create the root and the canvas
    root = Tk()
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.pack()
    # set up events
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed
    print("bye!")

run(1500, 800)
