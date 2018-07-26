# Justen McLean
# Python 3.4
# Distributed Computing
# Sudoku Race Server
# The server needs to be running before attempting to connect any clients
# To Run the server python3 must be installed on the host computer
# From a terminal or command prompt, cd to the folder the game is located in
# Enter 'python3 TCPServer.py' and the server will launch

import json
import time
import random
from socket import*                                  # Get needed socket library
from threading import *


# Server Variables
serverPort = 12000                                   # Set the server port
serverSocket = socket(AF_INET, SOCK_STREAM)          # Create the server socket
serverSocket.bind(('', serverPort))                  # Tell the socket where to listen for connections
serverSocket.listen(5)                               # Tell the server how many connection request we want to listen for

# Multithreading variables
sem = Semaphore()                                    # Semaphore to allow safe access to globals from threads
WAITTIME = 0.1                                       # How long to wait if delaying a thread

# Game Variables
numPlayers = 0          # The number of players in the game
puzzleString = ""       # The sudoku puzzle in string form
puzzles = {}            # Dictionary of all possible puzzles
gameStarted = False     # Has the game started
puzzleID = ''           # The id of the current puzzle
puzzleSolution = ''     # The solution to the sudoku puzzle in string form
player_solutions = {}   # The current status of the player that has submitted the puzzle
playersComplete = 0     # The number of players that have completed the puzzle


playersInLobby = 0
playersToStart = 2      # The number of players to start a game, can be increased to allow more people to compete
playersReady = 0        # How many players are ready to play


print("The server is ready to receive")              # Notify the user the server is listening

# Sample puzzle for initial testing
def getPuzzleString():
    puzzle = "0,5,6,9,0,7,4,0,0,0,8,1,0,4,0,0,0,0,0,0,0,0,1,5,0,9,0,0,0,0,0,0,3,8,5,7,8,4,0,0,6,0,0,2,3,7,3,9,2,0,0,0,0,0,0,6,0,5,8,0,0,0,0,0,0,0,0,7,0,3,6,0,0,0,8,3,0,6,5,7,0"
    puzzleId = 1
    puzzleString = puzzle
    return [puzzleString, puzzleId]

# Fills out the client_data dictionary
def setClientData(client):
    global numPlayers
    client['client_id'] = str(numPlayers+1)     # Set the players client_id
    return client

# Reads sudoku puzzles from a file
def readPuzzleFromFile():
    # Get the puzzles and solutions from the file
    puzzle_file = open('sudoku_puzzles.txt', 'r')
    puzzleInput = puzzle_file.readlines()  # read all the lines from the file
    puzzles = {}  # dictionary key = puzzle_id, value = {given: puzzle, solution: puzzle}
    curPair = {}  # temporarily holds the puzzle_id value
    curPuzzleID = 1  # the id of the puzzle being added
    count = 1  # count variable for skipping white spaces
    for x in range(0, len(puzzleInput), 1):
        if count == 1:              # This is the puzzle
            curPair['given'] = puzzleInput[x][:81].replace('.', '0')
            count += 1
        elif count == 2:            # This is the solution
            curPair['solution'] = puzzleInput[x][:81]
            count += 1
        elif count == 3:            # Blank Line in between
            count = 1
            puzzles[str(curPuzzleID)] = dict(curPair)
            curPair = {}
            curPuzzleID += 1

    return puzzles

# Selects a random puzzle from the available puzzles
def selectRandomPuzzle():
    global puzzle
    global puzzleID
    global puzzleString
    global puzzleSolution

    puzzle = random.choice(list(puzzles.items()))
    puzzleID = puzzle[0]
    puzzleString = puzzle[1]['given']
    puzzleSolution = puzzle[1]['solution']

# Checks a player solution against the known puzzle solution
def checkSolution(userSolution):
    global puzzleSolution
    if userSolution == puzzleSolution:
        return True
    return False

# Handles the different Clients, executed in a different thread to avoid blocking the other client
def clienthandler(connect, a):
    global numPlayers
    global playersToStart
    global playersReady
    global puzzleString
    global puzzleID
    global playersComplete
    print("Connected to client")
    try:
        while True:
            request = connect.recv(1024)  # Receive the sentence from the client
            client_data = json.loads(request.decode('utf-8'))  # Decode the json data from the client
            response_data = client_data
            waiting_for_lobby = True      # Bool to handle loop while waiting for more players to join the lobby
            waiting_for_start = True      # Bool to handle loop while waiting for the players to press start

            # Set up the client identity
            if client_data['client_id'] == '':  # Assign an id if the client does not have one
                sem.acquire()       # Acquire the semaphore to allow safe access to global variables
                client_data = setClientData(client_data)
                client_data['in_lobby'] = 'True'
                numPlayers = numPlayers + 1
                print(numPlayers)
                sem.release()

            # Set up the lobby
            elif client_data['in_lobby'] == 'True' and client_data['lobby_ready'] == 'False' and client_data['ready_to_start'] != 'True':
                while waiting_for_lobby:
                    time.sleep(WAITTIME)   # Wait period to make sure other threads have time to access needed variables
                    sem.acquire()          # Acquire the semaphore to allow safe access to global variables
                    if numPlayers >= playersToStart:
                        print('Lobby Ready')
                        client_data['lobby_ready'] = 'True'   # notify the client the lobby is ready
                        waiting_for_lobby = False
                    sem.release()           # Release the semaphore

            # Send the client the puzzle after all players have pressed start
            elif client_data['ready_to_start'] == 'True' and client_data['started'] == 'False':
                sem.acquire()                 # Acquire the semaphore to allow safe access to global variables
                print('Client ready to start')
                playersReady += 1             # Set this player as ready to start
                sem.release()                 # Release the semaphore
                # Wait for all the players to press start
                while waiting_for_start:
                    time.sleep(WAITTIME)   # Wait period to make sure other threads have time to access needed variables
                    sem.acquire()          # Acquire the semaphore to allow safe access to global variables
                    if playersReady >= numPlayers:
                        client_data['puzzle_string'] = puzzleString     # Send the puzzle
                        client_data['puzzle_id'] = puzzleID             # Set the puzzle_id
                        waiting_for_start = False                       # Stop the waiting loop
                    sem.release()          # Release the semaphore
            # If the client is submitting a puzzle
            elif client_data['submit'] == 'True':
                sem.acquire()               # Acquire the semaphore to allow safe access to global variables
                print('Solution submitted')
                # Check if the solution is correct
                if checkSolution(client_data['solution']):
                    # Add the players data to player_solutions
                    player_solutions[client_data['client_id']] = {'time': client_data['solve_time'], 'attempts': client_data['attempts'], 'solved': 'True'}
                    client_data['submit'] = 'False'     # Stop the submission from being read again
                    client_data['solution'] = 'True'    # Notify the player the solution was correct
                    playersComplete += 1                # increment the number of players finished
                else:
                    client_data['submit'] = 'False'     # Stop the submission from being read again
                    client_data['solution'] = 'False'   # Notify the player the solution was incorrect
                    client_data['attempts'] = str(int(client_data['attempts'])+1)   # Increase the attempts value
                    print(int(client_data['attempts'])+1)
                sem.release()  # Release the semaphore
            # If the client exceeds the allowed number of attempts at submitting the puzzle
            elif client_data['submit'] == 'Give Up':
                print('Give Up')
                sem.acquire()            # Acquire the semaphore to allow safe access to global variables
                client_data['submit'] == ''
                # Add the failed submission to the list of submissions
                player_solutions[client_data['client_id']] = {'time': client_data['solve_time'], 'attempts': client_data['attempts'], 'solved': client_data['solution'],}
                playersComplete += 1    # Increment the players complete
                sem.release()           # Release the semaphore
            # The client is requesting the leader board data
            elif client_data['request'] == 'leader board':
                print('Leader board requested')
                sem.acquire()            # Acquire the semaphore to allow safe access to global variables
                # print(player_solutions)
                client_data['leader_board'] = player_solutions      # Set the leader_board data
                # print(client_data)
                # Notify the client if all players have finished to display the leader board
                if playersComplete >= numPlayers:
                    # The game is over
                    client_data['finished'] = 'True'
                else:
                    client_data['finished'] = 'False'
                sem.release()            # Release the semaphore

            response_data = client_data     # Set the response data
            json_response = json.dumps(response_data)       # Encode the response into JSON
            connect.send(json_response.encode('utf-8'))     # Send the response to the client

    # Close the connection if an exception occurs
    except Exception as inst:
        # playerSockets.remove(c)
        print('Thread exception = ' + str(inst))
        connect.close()
        numPlayers -= 1         # Decrement the number of players


# Get the list of puzzles
puzzles = readPuzzleFromFile()
# Select a puzzle for the current game
selectRandomPuzzle()

# Loop to create new sockets for any request to the server, after creating the new socket, the server goes back to
# waiting for a client to request another connection
while 1:
    connectionSocket, adder = serverSocket.accept()  # Create a new socket
    Thread(target=clienthandler, args=(connectionSocket, adder)).start()   # Start a new thread to handle the client

