botName = "klatchu27-1"

import random
import numpy as np
import functools
import json
from random import randint, choice

# global variables
n = 8  # n*n is the size of the board


def calculateMove(gameState):
    if "handCount" not in persistentData:
        persistentData["handCount"] = 0
    if gameState["Round"] == 0:
        move = deployRandomly(gameState)
    else:
        persistentData["handCount"] += 1
        move = customMove(gameState)
    print("worse", str(persistentData["handCount"]) + ". MOVE: " + str(move))
    return move


def customMove(gameState):

    afloat = shipsStillAfloat(gameState)

    hit = []
    for i in range(n):
        for j in range(n):
            if gameState["OppBoard"][i][j] == "H":
                hit.append([i, j])

    p = np.zeros((n, n, 3), dtype=int)

    if len(hit) == 0:
        if len(afloat) <= 2:
            return chooseRandomValidTarget(gameState)
        print("random possible")
        return choosePosRandomValidTarget(gameState["OppBoard"], afloat)
    else:
        print(afloat)
        for l in afloat:
            for i in range(n):
                for j in range(n):
                    h1 = checkShip(i, j, gameState["OppBoard"], l, 1)
                    h2 = checkShip(i, j, gameState["OppBoard"], l, 0)
                    perc = int((max(h1, h2) * 100) / l)
                    if p[i][j][0] < perc and perc != 100:
                        if h1 >= h2:
                            p[i][j] = np.array([perc, int(l), 1])
                        else:
                            p[i][j] = np.array([perc, int(l), 0])

    ordered = []
    for i in range(n):
        for j in range(n):
            ordered.append(p[i][j][0])
    ordered.sort(reverse=True)

    for val in ordered:
        same = []
        for i in range(n):
            for j in range(n):
                if p[i][j][0] == val:
                    same.append([i, j])
        random.shuffle(same)
        for ii in same:
            i = ii[0]
            j = ii[1]
            pos = getSpecific(i, j, gameState["OppBoard"], p[i][j][1], p[i][j][2])
            if pos != [-1, -1]:
                print(i, j, p[i][j])
                return translateMove(pos[0], pos[1])

    print("random enddd")
    return chooseRandomValidTarget(gameState)


# Rank each empty positon by no of possible afloat ships which can
# be placed and randomly choose one of the positon with max possible ships
def choosePosRandomValidTarget(board, afloat):
    prob = np.zeros((n, n))

    for length in afloat:
        for i in range(n):
            for j in range(n):
                ver = True
                hor = True

                if i + length - 1 < n:
                    for l in range(length):
                        if board[i + l][j] != "":
                            ver = False
                            break
                    if ver == True:
                        # prob[i][j] += 1
                        for l in range(length):
                            prob[i + l][j] += 1
                if j + length - 1 < n:
                    for l in range(length):
                        if board[i][j + l] != "":
                            hor = False
                            break
                    if hor == True:
                        # prob[i][j] += 1
                        for l in range(length):
                            prob[i][j + l] += 1

    result = np.where(prob == np.amax(prob))
    same = list(zip(result[0], result[1]))
    random.shuffle(same)
    return {"Row": chr(int(same[0][0]) + 65), "Column": (int(same[0][1]) + 1)}


# returns [i,j],a empty position of possible ship given the length,orientation
# and starting pt of that ship
# If fails to do so, funtion returns [-1,-1]
def getSpecific(i, j, board, length, orientation):

    if length == 0:
        return [-1, -1]
    if orientation == 1:
        if i + length - 1 >= len(board):
            return [-1, -1]
        for l in range(length):
            if board[i + l][j] == "":
                return [i + l, j]
    else:
        if j + length - 1 >= len(board[0]):
            return [-1, -1]
        for l in range(length):
            if board[i][j + l] == "":
                return [i, j + l]
    return [-1, -1]


# returns no of already hit positions of a ship
# given its starting pt, length and orientation
def checkShip(i, j, board, length, orientation):
    hits_count = 0
    if orientation == 1:
        if i + length - 1 >= len(board):
            return -1
        for l in range(length):
            if (
                board[i + l][j] == "M"
                or board[i + l][j] == "LM"
                or board[i + l][j] == "L"
                or len(board[i + l][j]) == 2
            ):
                return 0
            if board[i + l][j] == "H":
                hits_count += 1
    else:
        if j + length - 1 >= len(board[0]):
            return -1
        for l in range(length):
            if (
                board[i][j + l] == "M"
                or board[i][j + l] == "LM"
                or board[i][j + l] == "L"
                or len(board[i][j + l]) == 2
            ):
                return 0
            if board[i][j + l] == "H":
                hits_count += 1
    return hits_count


# Deploys all the ships randomly on a blank board
def deployRandomly(gameState):
    move = []  # Initialise move as an emtpy list
    orientation = None
    row = None
    column = None
    for i in range(len(gameState["Ships"])):  # For every ship that needs to be deployed
        deployed = False
        while (
            not deployed
        ):  # Keep randomly choosing locations until a valid one is chosen
            row = randint(0, len(gameState["MyBoard"]) - 1)  # Randomly pick a row
            column = randint(
                0, len(gameState["MyBoard"][0]) - 1
            )  # Randomly pick a column
            orientation = choice(["H", "V"])  # Randomly pick an orientation
            if deployShip(
                row, column, gameState["MyBoard"], gameState["Ships"][i], orientation, i
            ):  # If ship can be successfully deployed to that location...
                deployed = True  # ...then the ship has been deployed
        move.append(
            {"Row": chr(row + 65), "Column": (column + 1), "Orientation": orientation}
        )  # Add the valid deployment location to the list of deployment locations in move
    return {"Placement": move}  # Return the move


# Returns whether given location can fit given ship onto given board and, if it can, updates the given board with that ships position
def deployShip(i, j, board, length, orientation, ship_num):
    if orientation == "V":  # If we are trying to place ship vertically
        if i + length - 1 >= len(board):  # If ship doesn't fit within board boundaries
            return False  # Ship not deployed
        for l in range(length):  # For every section of the ship
            if (
                board[i + l][j] != ""
            ):  # If there is something on the board obstructing the ship
                return False  # Ship not deployed
        for l in range(length):  # For every section of the ship
            board[i + l][j] = str(ship_num)  # Place the ship on the board
    else:  # If we are trying to place ship horizontally
        if j + length - 1 >= len(
            board[0]
        ):  # If ship doesn't fit within board boundaries
            return False  # Ship not deployed
        for l in range(length):  # For every section of the ship
            if (
                board[i][j + l] != ""
            ):  # If there is something on the board obstructing the ship
                return False  # Ship not deployed
        for l in range(length):  # For every section of the ship
            board[i][j + l] = str(ship_num)  # Place the ship on the board
    return True  # Ship deployed


# Randomly guesses a location on the board that hasn't already been hit
def chooseRandomValidTarget(gameState):
    valid = False
    row = None
    column = None
    while not valid:  # Keep randomly choosing targets until a valid one is chosen
        row = randint(0, len(gameState["MyBoard"]) - 1)  # Randomly pick a row
        column = randint(0, len(gameState["MyBoard"][0]) - 1)  # Randomly pick a column
        if (
            gameState["OppBoard"][row][column] == ""
        ):  # If the target is sea that hasn't already been guessed...
            valid = True  # ...then the target is valid
    move = {
        "Row": chr(row + 65),
        "Column": (column + 1),
    }  # Set move equal to the valid target (convert the row to a letter 0->A, 1->B etc.)
    return move  # Return the move


# Returns a list of the lengths of your opponent's ships that haven't been sunk
def shipsStillAfloat(gameState):
    afloat = []
    ships_removed = []
    for k in range(len(gameState["Ships"])):  # For every ship
        afloat.append(gameState["Ships"][k])  # Add it to the list of afloat ships
        ships_removed.append(False)  # Set its removed from afloat list to false
    for i in range(len(gameState["OppBoard"])):
        for j in range(len(gameState["OppBoard"][0])):  # For every grid on the board
            for k in range(len(gameState["Ships"])):  # For every ship
                if (
                    str(k) in gameState["OppBoard"][i][j] and not ships_removed[k]
                ):  # If we can see the ship number on our opponent's board and we haven't already removed it from the afloat list
                    afloat.remove(
                        gameState["Ships"][k]
                    )  # Remove that ship from the afloat list (we can only see an opponent's ship number when the ship has been sunk)
                    ships_removed[
                        k
                    ] = True  # Record that we have now removed this ship so we know not to try and remove it again
    return afloat  # Return the list of ships still afloat


# Returns a list of cells adjacent to the input cell that are free to be targeted (not including land)
def selectUntargetedAdjacentCell(row, column, oppBoard):
    adjacent = []  # List of adjacent cells
    if row > 0 and oppBoard[row - 1][column] == "":  # If there is a cell above
        adjacent.append((row - 1, column))  # Add to list of adjacent cells
    if (
        row < len(oppBoard) - 1 and oppBoard[row + 1][column] == ""
    ):  # If there is a cell below
        adjacent.append((row + 1, column))  # Add to list of adjacent cells
    if column > 0 and oppBoard[row][column - 1] == "":  # If there is a cell left
        adjacent.append((row, column - 1))  # Add to list of adjacent cells
    if (
        column < len(oppBoard[0]) - 1 and oppBoard[row][column + 1] == ""
    ):  # If there is a cell right
        adjacent.append((row, column + 1))  # Add to list of adjacent cells
    return adjacent


# Given a valid coordinate on the board returns it as a correctly formatted move
def translateMove(row, column):
    return {"Row": chr(row + 65), "Column": (column + 1)}
