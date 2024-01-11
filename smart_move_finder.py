
import random

scoreMap = {"K" : 0, "Q" : 10, "R" : 5, "B" : 3, "N" : 3, "p" : 1}
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 2
def findRandomMove(validMoves):
    return validMoves[random.randint(0,len(validMoves)-1)]     #range of it from 0 to x and return that validMoves

def findBestMove():
    return

def findGreedyMove(gs,validMoves):
    turnMultiplier = 1 if gs.whiteToMove else -1
    max_score = -CHECKMATE
    bestMove = None
    for move in validMoves :
        gs.makeMove(move)   #make the move and check the score score after it
        if gs.checkMate :
            score = CHECKMATE
        elif gs.staleMate :
            score = STALEMATE
        else :
            score = turnMultiplier * scoreMaterial(gs.board)
        if score > max_score :
            max_score = score
            bestMove = move
        gs.undoMove()   #undo the move then go for the next move
    return bestMove

def findMinMaxMove(gs,validMoves):
    turnMultiplier = 1 if gs.whiteToMove else -1
    opponent_min_max_score = CHECKMATE  #we have to minimize the score to opponent
    bestMove = None

    for move in validMoves :
        gs.makeMove(move)   #make the move and check the score score after it
        opponentMoves = gs.getValidMoves()
        opponent_max_score = -CHECKMATE
        #random.shuffle(validMoves)
        for opponentMove in opponentMoves :
            gs.makeMove(opponentMove)
            if gs.checkMate :
                score = -turnMultiplier*CHECKMATE
            elif gs.staleMate :
                score = -STALEMATE
            else :
                score = -turnMultiplier * scoreMaterial(gs.board)
            if score > opponent_max_score :
                opponent_max_score = score
            gs.undoMove()   #undo the move then go for the next move
        if opponent_min_max_score > opponent_max_score :
            opponent_min_max_score = opponent_max_score
            bestMove = move
        gs.undoMove()
    return bestMove

def findBestMinMaxRecurMove(gs,validMoves) :
    global bestMove
    bestMove = None
    random.shuffle(validMoves)
    findMinMaxRecurMove(gs,validMoves,DEPTH,gs.whiteToMove)
    return bestMove

def findMinMaxRecurMove(gs,validMoves,depth,whiteToMove):
    global bestMove
    if depth==0 :
        return scoreMaterial(gs)

    if gs.whiteToMove :
        max_score = -CHECKMATE
        for move in validMoves :
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMinMaxRecurMove(gs,nextMoves,depth-1,False)
            if score > max_score :
                max_score = score
                if depth==DEPTH :
                    bestMove = move

            gs.undoMove()
        return max_score
    else :
        min_score = CHECKMATE
        for move in validMoves:
            gs.makeMove(move)
            nextMoves = gs.getValidMoves()
            score = findMinMaxRecurMove(gs, nextMoves, depth - 1, True)
            if score < min_score:
                min_score = score
                if depth == DEPTH:
                    bestMove = move

            gs.undoMove()
        return min_score



def scoreMaterial(gs) :
    if gs.checkMate :
        if gs.whiteToMove :     #black king will win
            return -CHECKMATE
        else :      #white king will win
            return CHECKMATE
    if gs.staleMate :
        return STALEMATE

    score = 0
    for row in gs.board :
        for piece in row :
            if piece[0]=='w' :
                score += scoreMap[piece[1]]
            elif piece[0]=='b' :
                score -= scoreMap[piece[1]]
    return score
