# Justen McLean
# Python 3.4
# Distributed Computing
# Project 1-B
# Sudoku Race Client
# The server part of this program needs to be running before clicking connect on the client
# To Run the client, python3 and pygame need to be installed on the client computer
# From a terminal or command prompt cd to the folder the game is located in
# Enter 'python3 client.py' and the game will launch

import pygame
import time
import math
import sys
import json
from socket import *


# Server Config
serverName = '192.168.0.102'                                # The IP address of this computer
serverPort = 12001                                          # The port number the server is listening from
clientSocket = socket(AF_INET, SOCK_STREAM)                 # Create a socket

# The json data that will be sent to the server
client_data = {
    'client_id': '',
    'puzzle_string': '',
    'puzzle_id': '',
    'submit': '',
    'attempts': '',
    'match_number': '',
    'solve_time': '',
    'in_lobby': 'False',
    'lobby_ready': 'False',
    'ready_to_start': 'False',
    'started': 'False',
    'solution': '',
    'request': '',
    'leader_board': '',
    'attempts': '0',
    'finished': 'False',
}

# Initialize pygame
pygame.init()

# Set up the window
windowSurface = pygame.display.set_mode((500, 600), 0, 32)
pygame.display.set_caption('Sudoku Race')

# Set the font sizes
font40 = pygame.font.Font(None, 40)
font30 = pygame.font.Font(None, 30)
font20 = pygame.font.Font(None, 20)
font10 = pygame.font.Font(None, 10)

# Set the Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
DARK_GRAY = (150,150,150)
RED = (255, 0, 0)
GREEN = (0, 200, 0)

# Set up board variables
WINDOWMULTIPLIER = 5
BOARDSIZE = 90
BOARDWIDTH = BOARDSIZE * WINDOWMULTIPLIER
BOARDHEIGHT = BOARDSIZE * WINDOWMULTIPLIER
CELLSIZE = int(((BOARDSIZE * WINDOWMULTIPLIER) / 9))
SQUARESIZE = int(((BOARDSIZE * WINDOWMULTIPLIER) / 3))
NUMBERSIZE = CELLSIZE / 3
XOFFSET = 25
YOFFSET = 100

# Timer Variables
startTime = time.time()
stopTime = 0
currentTime = time.time()
elapsedTime = math.floor(currentTime - startTime)
timerRunning = False
WAITTIME = 0.1

# Lives Variable
lives = 3

# Game Variables
state = "Disconnected"
currentSquare = [-1, -1]

# Sudoku Board Variables
given = ""
givenPuzzle = [None] * 9
puzzle = [None] * 9

# Button variables
connectButtonX = 0
connectButtonY = 0
connectButtonW = 0
connectButtonH = 0
submitButtonX = 0
submitButtonY = 0
submitButtonW = 0
submitButtonH = 0

# Draws the board to the screen
def drawBoard():
    # Draw light lines
    for x in range(0, BOARDWIDTH, CELLSIZE):
        pygame.draw.line(windowSurface, GRAY, (x+XOFFSET, 0+YOFFSET), (x+XOFFSET, BOARDHEIGHT+YOFFSET), 1)
    for y in range(0, BOARDWIDTH, CELLSIZE):
        pygame.draw.line(windowSurface, GRAY, (0+XOFFSET, y+YOFFSET), (BOARDHEIGHT+XOFFSET, y+YOFFSET), 1)

    # Draw dark lines
    for x in range(0, BOARDWIDTH+1, SQUARESIZE):
        pygame.draw.line(windowSurface, BLACK, (x+XOFFSET, 0+YOFFSET), (x+XOFFSET, BOARDHEIGHT+YOFFSET))
    for y in range(0, BOARDHEIGHT+1, SQUARESIZE):
        pygame.draw.line(windowSurface, BLACK, (0+XOFFSET, y+YOFFSET), (BOARDWIDTH+XOFFSET, y+YOFFSET))
    return None

# Sets the value
def timer():
    global timerRunning
    global elapsedTime
    global startTime
    if timerRunning:
        elapsedTime = math.floor(time.time() - startTime)          # Update the timer
    return None

# Creates a double nested list from a string
def puzzleFromString(puzzleString):

    puzzleList = list(puzzleString)                 # make a list of the characters in puzzleString

    i = 0                                           # Index of puzzleList
    row = [None] * 9                                # The row of the puzzle

    for y in range(0, 9, 1):
        col = [None] * 9                            # The columns of the puzzle

        for x in range(0, 9, 1):
            #print(puzzleList[i])
            col[x] = puzzleList[i]                  # Set the value at this row col to puzzleList[i]
            i = i + 1
        row[y] = col                                # Add this col to row

    return row


# Prints the puzzle values to the board in the proper position
def setPuzzle(cur_puzzle, color=BLACK):
    global XOFFSET
    global YOFFSET
    global CELLSIZE

    for row in range(0, 9, 1):
        for col in range(0, 9, 1):
            if int(cur_puzzle[row][col]) > 0:
                pos_x = 125 + XOFFSET
                pos_y = 25 + YOFFSET
                numberText = basicFont.render(cur_puzzle[row][col], True, color, WHITE)
                numberRect = text.get_rect()
                # Get the position to place the number
                pos_x += (col * CELLSIZE)        # The center x of the cell at col row
                pos_y += (row * CELLSIZE)        # The center y of the cell at col row
                numberRect.centerx = pos_x
                numberRect.centery = pos_y
                windowSurface.blit(numberText, numberRect)

    return None

# Converts a puzzle to a string for sending to the server
def puzzleToString(puzzleToConvert):
    stringPuzzle = ''
    for x in range(0, 9, 1):
        for y in range(0, 9, 1):
            stringPuzzle += puzzleToConvert[x][y]
    return stringPuzzle

def submitSolution():
    global client_data
    json_data = json.loads(client_data)
    clientSocket.send(json_data.encode('utf-8'))  # Encode the sentence to unicode and send to server
    response = clientSocket.recv(1024)  # Receive response from server
    json_response = response.decode('utf-8')
    client_data = json.loads(json_response)
    if client_data['Correct_Answer'] == True:
        # End the game
        var = True

# button function
def button(x, y, w, h, action=None):
    global state
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    if x+w > mouse[0] > x and y+h > mouse[1] > y:
        if click[0] == 1 and action != None:
            time.sleep(0.1)   # Delay to avoid buttons being clicked multiple times
            if action == "Start":
                # pygame.draw.rect(windowSurface, WHITE,[ startButtonX, startButtonY, startButtonW, startButtonH]  )
                state = "Wait For Puzzle"
            elif action == "Connect":
                state = "Connecting"
                print("Connecting")
            elif action == 'Submit':
                state = "Submit"
                print("Submitting")

    return None

# For debugging purposes
def showMousePos():
    mouse = pygame.mouse.get_pos()
    mouseText = font20.render((str(mouse[0])+', '+str(mouse[1])), True, BLACK, WHITE)
    mouseRect = mouseText.get_rect()
    mouseRect.centerx = windowSurface.get_rect().centerx * .25
    mouseRect.centery = 60
    windowSurface.blit(mouseText, mouseRect)

    return None

# Gets the square the mouse is hovering over
def selectSquare():
    mouse = pygame.mouse.get_pos()
    mX = mouse[0]
    mY = mouse[1]
    col = 0
    row = 0
    pos = [None] * 2

    if( mX < 25 or mX > 475):
        col = -1
    elif 25 < mX < 75:
        col = 0
    elif 75 < mX < 125:
        col = 1
    elif 125 < mX < 175:
        col = 2
    elif 175 < mX < 225:
        col = 3
    elif 225 < mX < 275:
        col = 4
    elif 275 < mX < 325:
        col = 5
    elif 325 < mX < 375:
        col = 6
    elif 375 < mX < 425:
        col = 7
    elif 425 < mX < 475:
        col = 8

    if(mY < 100 or mY > 575):
        row = -1
    elif 100 < mY < 150 :
        row = 0
    elif 150 < mY < 200:
        row = 1
    elif 200 < mY < 250:
        row = 2
    elif 250 < mY < 300:
        row = 3
    elif 300 < mY < 350:
        row = 4
    elif 350 < mY < 400:
        row = 5
    elif 400 < mY < 450:
        row = 6
    elif 450 < mY < 500:
        row = 7
    elif 500 < mY < 550:
        row = 8

    pos[0] = row
    pos[1] = col

    return pos

# Determines the square that was clicked
def cellClick():
    global state
    global currentSquare
    pos = selectSquare()
    click = pygame.mouse.get_pressed()
    # print(pos[0], pos[1])
    # Check that the mouse is over a square in the board
    if pos[0] >= 0 and pos[1] >= 0:
        if click[0] == 1:
            print("Cell was clicked")
            state = "Waiting for input"
            currentSquare = pos

    return None


# Gets key inputs for squares
def getKeyInput():
    value = -1
    pygame.event.pump()  # Get the latest key updates
    pressedKeys = pygame.key.get_pressed()  # Get the keys being pressed
    if pressedKeys[pygame.K_1] == 1 or pressedKeys[pygame.K_KP1] == 1:
        value = 1
    elif pressedKeys[pygame.K_2] == 1 or pressedKeys[pygame.K_KP2] == 1:
        value = 2
    elif pressedKeys[pygame.K_3] == 1 or pressedKeys[pygame.K_KP3] == 1:
        value = 3
    elif pressedKeys[pygame.K_4] == 1 or pressedKeys[pygame.K_KP4] == 1:
        value = 4
    elif pressedKeys[pygame.K_5] == 1 or pressedKeys[pygame.K_KP5] == 1:
        value = 5
    elif pressedKeys[pygame.K_6] == 1 or pressedKeys[pygame.K_KP6] == 1:
        value = 6
    elif pressedKeys[pygame.K_7] == 1 or pressedKeys[pygame.K_KP7] == 1:
        value = 7
    elif pressedKeys[pygame.K_8] == 1 or pressedKeys[pygame.K_KP8] == 1:
        value = 8
    elif pressedKeys[pygame.K_9] == 1 or pressedKeys[pygame.K_KP9] == 1:
        value = 9

    return value


# Set the value of a square
def setCellValue(pos, val):
    global puzzle
    puzzle[pos[0]][pos[1]] = str(val)
    return None


def drawConnectButton():
    global connectButtonH
    global connectButtonW
    global connectButtonX
    global connectButtonY
    # Set up the connect button
    connectText = basicFont.render('Connect', True, WHITE, GREEN)
    connectRect = startText.get_rect()

    connectPadding = connectRect.copy()
    connectPadding.w = connectRect.w + 70
    connectPadding.h = connectRect.h + 10
    connectRect.centerx = windowSurface.get_rect().centerx - 28
    connectRect.centery = windowSurface.get_rect().centery
    connectPadding.centerx = windowSurface.get_rect().centerx
    connectPadding.centery = connectRect.centery
    # draw the start button back ground
    pygame.draw.rect(windowSurface, GREEN, connectPadding)
    windowSurface.blit(connectText, connectRect)

    connectButtonH = connectPadding.h
    connectButtonW = connectPadding.w
    connectButtonX = connectPadding.x
    connectButtonY = connectPadding.y

    return None

def drawWaitingForPlayers():

    # Set up the connect button
    waitingText = basicFont.render('Waiting for players', True, BLACK)
    waitingRect = waitingText.get_rect()
    waitingRect.centerx = windowSurface.get_rect().centerx - 28
    waitingRect.centery = windowSurface.get_rect().centery

    windowSurface.blit(waitingText, waitingRect)
    return None

def drawSubmitButton():
    global submitButtonH
    global submitButtonW
    global submitButtonX
    global submitButtonY
    # Set up the connect button
    submitText = basicFont.render('Submit', True, WHITE, RED)
    submitRect = startText.get_rect()

    submitPadding = submitRect.copy()
    submitPadding.w = submitRect.w + 60
    submitPadding.h = submitRect.h + 10
    submitRect.centerx = windowSurface.get_rect().centerx - 20
    submitRect.centery = 60
    submitPadding.centerx = windowSurface.get_rect().centerx
    submitPadding.centery = submitRect.centery
    # draw the start button back ground
    pygame.draw.rect(windowSurface, RED, submitPadding)
    windowSurface.blit(submitText, submitRect)

    submitButtonH = submitPadding.h
    submitButtonW = submitPadding.w
    submitButtonX = submitPadding.x
    submitButtonY = submitPadding.y

    return None

# Draws the timer to the screen
def drawTimer():
    # Set up the timer text
    timerText = basicFont.render(str(elapsedTime), True, BLACK, WHITE)
    timerRect = timerText.get_rect()
    timerRect.centerx = (windowSurface.get_rect().centerx / 2) + windowSurface.get_rect().centerx
    timerRect.centery = 60
    windowSurface.blit(timerText, timerRect)

    return None

# Draw text to the top of the screen
def drawTextToCenter(textToWrite):
    # Set up the lives text
    centerText = basicFont.render(textToWrite, True, BLACK, WHITE)
    centerRect = centerText.get_rect()
    centerRect.centerx = windowSurface.get_rect().centerx
    centerRect.centery = windowSurface.get_rect().centery
    windowSurface.blit(centerText, centerRect)
    return None

# Draw text to the top of the screen
def drawTextToTop(textToWrite):
    # Set up the lives text
    topText = basicFont.render(textToWrite, True, BLACK, WHITE)
    topRect = topText.get_rect()
    topRect.centerx = windowSurface.get_rect().centerx
    topRect.centery = windowSurface.get_rect().centery / 10
    windowSurface.blit(topText, topRect)
    return None

# Draws the stats of the players from the game
def drawLeaderBoard(leaderBoardData):
    # Set up the lives text
    # print('leader_board =' + str(leaderBoardData))
    # Draw the player data to the screen
    offset = 20
    for key in leaderBoardData.items():
        playerData = ''
        playerData += 'Player: ' + str(key[0]) + ' Solved: ' + key[1]['solved']
        playerData += ' Attempts: ' + key[1]['attempts'] + ' Time: ' + key[1]['time']
        leaderBoardListText = font20.render(playerData, True, BLACK, WHITE)
        leaderBoardRect = leaderBoardListText.get_rect()
        leaderBoardRect.centerx = windowSurface.get_rect().centerx
        leaderBoardRect.centery = windowSurface.get_rect().centery + offset
        windowSurface.blit(leaderBoardListText, leaderBoardRect)
        offset += 20
        # print('Player = ' + str(key[0]) + ' Data = ' + str(key[1]))
    # Write the title to the screen
    leaderBoardTitleText = font30.render('Leader Board', True, BLACK, WHITE)
    leaderBoardTitleRect = leaderBoardTitleText.get_rect()
    leaderBoardTitleRect.centerx = windowSurface.get_rect().centerx
    leaderBoardTitleRect.centery = windowSurface.get_rect().centery
    windowSurface.blit(leaderBoardTitleText, leaderBoardTitleRect)

    return None

# Draws the number of lives left
def drawLives():
    # Set up the lives text
    #print('Lives: ' + str(lives))
    livesText = basicFont.render('Lives: ' + str(lives), True, BLACK, WHITE)
    livesRect = livesText.get_rect()
    livesRect.centerx = (windowSurface.get_rect().centerx / 2) - 20
    livesRect.centery = 60
    windowSurface.blit(livesText, livesRect)
    return None


# Draw the white background
windowSurface.fill(WHITE)

# Set up the font
basicFont = pygame.font.SysFont(None, 48)

# Set up the title text
text = basicFont.render('Sudoku Race!', True, BLACK, WHITE)
textRect = text.get_rect()
textRect.centerx = windowSurface.get_rect().centerx
textRect.centery = 20



# Set up the start button
startText = basicFont.render('Start', True, WHITE, GREEN)
startRect = startText.get_rect()
startRect.centerx = windowSurface.get_rect().centerx
startRect.centery = windowSurface.get_rect().centery
startPadding = startRect.copy()
startPadding.inflate_ip(10, 10)

# draw the start button back ground
pygame.draw.rect(windowSurface, GREEN, startPadding)
startButtonX = startPadding.x
startButtonY = startPadding.y
startButtonW = startPadding.w
startButtonH = startPadding.h

# draw the board
drawBoard()


def main():
    global elapsedTime
    global given
    global givenPuzzle
    global puzzle
    global state
    global serverName
    global serverPort
    global client_data
    global startTime
    global timerRunning
    global lives
    global WAITTIME

    request = json.dumps(client_data)           # JSON encoded data to be sent to the server
    makingConnectionAttempt = False
    gameFinished = False

    # run the game loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        if state == 'Disconnected':
            # print('State = Disconnected')
            windowSurface.fill(WHITE)
            drawTextToTop('Sudoku Race!')
            drawConnectButton()
            button(connectButtonX, connectButtonY, connectButtonW, connectButtonH, "Connect")
        elif state == 'Connecting':
            # print('State = Connecting')
            if makingConnectionAttempt == False:
                makingConnectionAttempt = True
                clientSocket.connect((serverName, serverPort))
                clientSocket.send(request.encode('utf-8'))  # Encode the sentence to unicode and send to server
                response = clientSocket.recv(1024)  # Receive response from server
                json_response = response.decode('utf-8')
                client_data = json.loads(json_response)
                print('From server:', json_response)  # Print the server response to the console
                if client_data['in_lobby'] == 'True':
                    state = 'In lobby'
                    windowSurface.fill(WHITE)
                    drawWaitingForPlayers()
                    clientSocket.send(response)
        elif state == 'In lobby':
            # print('State = In lobby')
            response = clientSocket.recv(1024)  # Receive response from server
            json_response = response.decode('utf-8')
            client_data = json.loads(json_response)
            print('From server:', json_response)  # Print the server response to the console
            if client_data['lobby_ready'] == 'True':
                state = 'Wait For Start'

            windowSurface.fill(WHITE)
            drawWaitingForPlayers()
        elif state == 'Wait For Start':
            windowSurface.fill(WHITE)
            windowSurface.blit(startText, startRect)
            drawTextToTop('Player ' + str(client_data['client_id']))
            button(startButtonX, startButtonY, startButtonW, startButtonH, 'Start')

        elif state == 'Wait For Puzzle':
            windowSurface.fill(WHITE)
            # print('State = Wait For Puzzle')
            # send ready_to_start to server
            client_data['ready_to_start'] = 'True'
            client_data['in_lobby'] == 'False'
            json_data = json.dumps(client_data)
            clientSocket.send(json_data.encode('utf-8'))

            # wait for server to respond with the puzzle
            response = clientSocket.recv(1024)  # Receive response from server
            json_response = response.decode('utf-8')
            client_data = json.loads(json_response)
            print('From server:', json_response)  # Print the server response to the console
            given = client_data['puzzle_string']
            givenPuzzle = puzzleFromString(given)
            puzzle = puzzleFromString(given)

            client_data['started'] = 'True'
            json_data = json.dumps(client_data)
            clientSocket.send(json_data.encode('utf-8'))

            # wait for server to respond with the puzzle
            response = clientSocket.recv(1024)  # Receive response from server
            json_response = response.decode('utf-8')
            client_data = json.loads(json_response)

            startTime = time.time()
            timerRunning = True
            # Draw the GUI text to the surface
            windowSurface.blit(text, textRect)

            drawLives()
            # Draw the grid
            drawBoard()
            drawTimer()         # Draw the timer to the screen
            state = 'Started'

        # If not waiting for keyboard input, check for a cell being clicked on
        elif state == "Started":
            # print('State = Started')
            # Set up the timer
            drawTimer()
            drawLives()
            # Show the submit Button
            drawSubmitButton()
            button(submitButtonX, submitButtonY, submitButtonW, submitButtonH, 'Submit')
            # Fill in the user filled squares in black
            setPuzzle(puzzle, BLACK)
            # Fill in the given pieces in gray
            setPuzzle(givenPuzzle, DARK_GRAY)
            cellClick()
        elif state == "Waiting for input":
            # print('State = Waiting for input')
            drawTimer()
            # Show the submit button
            drawSubmitButton()
            drawLives()
            button(submitButtonX, submitButtonY, submitButtonW, submitButtonH, 'Submit')

            val = getKeyInput()
            if val != -1:
                setCellValue(currentSquare, val)
                state = "Started"
        elif state == "Submit":
            # print('State = Submit')
            puzzleSolution = puzzleToString(puzzle)

            # send client solution to server
            client_data['solution'] = puzzleSolution
            client_data['solve_time'] = str(elapsedTime)
            client_data['submit'] = 'True'
            json_data = json.dumps(client_data)
            clientSocket.send(json_data.encode('utf-8'))

            # wait for server to respond with the puzzle
            response = clientSocket.recv(1024)  # Receive response from server
            json_response = response.decode('utf-8')
            client_data = json.loads(json_response)
            print('From server:', json_response)  # Print the server response to the console

            # Check if the solution was correct
            if client_data['solution'] == 'True':
                state = 'Finished'
            elif client_data['attempts'] == '3':
                state = 'Finished'
                client_data['submit'] = 'Give Up'
                json_data = json.dumps(client_data)
                clientSocket.send(json_data.encode('utf-8'))

                # wait for server to respond with the puzzle
                response = clientSocket.recv(1024)  # Receive response from server
                json_response = response.decode('utf-8')
                client_data = json.loads(json_response)
                client_data['submit'] = ''
            else:
                state = 'Started'
                lives -= 1
            drawTimer()
            # Show the submit button
            # drawSubmitButton()
            # button(submitButtonX, submitButtonY, submitButtonW, submitButtonH, 'Submit')

        elif state == "Finished":
            # print('State == Finished')
            windowSurface.fill(WHITE)

            if client_data['solution'] == 'True':
                drawTextToTop('Correct')
            else:
                drawTextToTop('Out of lives')

            if gameFinished:
                drawLeaderBoard(client_data['leader_board'])
            # Update the display
            pygame.display.update()

            # Request leader_board every WAITTIME until game finished is received from server
            time.sleep(WAITTIME)
            while not gameFinished:
                # send leader_board request to server
                client_data['request'] = 'leader board'
                json_data = json.dumps(client_data)
                clientSocket.send(json_data.encode('utf-8'))

                # wait for server to respond with the puzzle
                response = clientSocket.recv(1024)  # Receive response from server
                json_response = response.decode('utf-8')
                client_data = json.loads(json_response)
                #print(client_data)
                if client_data['finished'] == 'True':
                    gameFinished = True
                    drawLeaderBoard(client_data['leader_board'])
                    #clientSocket.close()
        # showMousePos()
        timer()
        # draw the window onto the screen
        pygame.display.update()


if __name__ == '__main__':
    main()
