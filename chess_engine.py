
#this class is responsible for storing current state of the game
#this class is also responsible for the valid moves

import chess_main
class GameState():
    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.whiteToMove = True
        self.moveLog = []
        self.pieceCapturedLog = []
        self.whiteKingPosition = (7,4)
        self.blackKingPosition = (0,4)
        self.checkMate = False
        self.staleMate = False
        self.enPassantPossible = ()
        self.enPassantPossibleLog = [self.enPassantPossible]
        self.currentCastleRight = CastleRights(True,True,True,True)
        #self.castleRightsLog = [self.currentCastleRight]
        self.castleRightsLog = [CastleRights(self.currentCastleRight.wks,self.currentCastleRight.bks,
                                                 self.currentCastleRight.wqs,self.currentCastleRight.bqs)]
        #self.enPassantPossibles = []

    def makeMove(self,move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) #to keep track for all move for undo later on
        self.whiteToMove = not self.whiteToMove #to swap the move
        #update the king position if needed
        if move.pieceMoved=="wK" :
            self.whiteKingPosition = (move.endRow,move.endCol)
        elif move.pieceMoved=="bK" :
            self.blackKingPosition = (move.endRow,move.endCol)

        #pawn promotion
        if move.pawnPromotion :
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'

        #en passant move
        if move.isEnPassantMove :
            self.board[move.startRow][move.endCol] = "--"
        #update en passant possible variable
        if move.pieceMoved[1] == 'p' and abs(move.startRow-move.endRow)==2 :
            self.enPassantPossible = ((move.startRow+move.endRow)//2,move.endCol)
        else :
            self.enPassantPossible = ()
        self.enPassantPossibleLog.append(self.enPassantPossible)    #it will append at every move
        #castling move
        if move.isCastleMove :
            if move.endCol - move.startCol == 2 :   #king side
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1]
                self.board[move.endRow][move.endCol+1] = "--"
            else :  #queen side
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]
                self.board[move.endRow][move.endCol - 2] = "--"

        #update the castling rights - whenever it is rook or king move
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastleRight.wks,self.currentCastleRight.bks,
                                                 self.currentCastleRight.wqs,self.currentCastleRight.bqs))

        self.pieceCapturedLog.append(move.pieceCaptured)



    def undoMove(self):
        if len(self.moveLog) != 0 :
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            # update the king position if needed
            if move.pieceMoved == "wK":
                self.whiteKingPosition = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingPosition = (move.startRow, move.startCol)
            #on en passant
            if move.isEnPassantMove :
                self.board[move.endRow][move.endCol] = "--"
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                #self.enPassantPossible = (move.endRow,move.endCol)
                #no need to find it because it is already there in enPassantPossibleLog

            #undo 2 square moved of pawn
            # if move.pieceMoved[1]=='p' and abs(move.startRow-move.endRow)==2 :
            #     self.enPassantPossible = ()
            self.enPassantPossibleLog.pop()
            self.enPassantPossible = self.enPassantPossibleLog[-1]  #end of the list

            #undo castle right
            self.castleRightsLog.pop() #remove the castle right
            self.currentCastleRight = self.castleRightsLog[-1] #set it to last castle right of the list
            self.currentCastleRight = CastleRights(self.currentCastleRight.wks,self.currentCastleRight.bks,
                                                   self.currentCastleRight.wqs,self.currentCastleRight.bqs)
            #undo castle move
            if move.isCastleMove :
                if move.endCol-move.startCol==2 :   #king side
                    self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-1]
                    self.board[move.endRow][move.endCol-1] = "--"
                else :  #queen side
                    self.board[move.endRow][move.endCol-2] = self.board[move.endRow][move.endCol+1]
                    self.board[move.endRow][move.endCol+1] = "--"
            self.pieceCapturedLog.pop()
            self.checkMate = False
            self.staleMate = False


    def updateCastleRights(self,move):
        #when rook or king is moved
        if move.pieceMoved=="wK" :
            self.currentCastleRight.wks = False
            self.currentCastleRight.wqs = False
        elif move.pieceMoved=="bK" :
            self.currentCastleRight.bks = False
            self.currentCastleRight.bqs = False
        elif move.pieceMoved=="wR":
            if move.startRow==7 :
                if move.startCol==0:#left Rook
                    self.currentCastleRight.wqs = False
                elif move.startCol==7 :  #right rook
                    self.currentCastleRight.wks = False
        elif move.pieceMoved=="bR":
            if move.startRow == 0:
                if move.startCol == 0:  # left Rook
                    self.currentCastleRight.bqs = False
                elif move.startCol == 7:  # right rook
                    self.currentCastleRight.bks = False
        # when rook is captured
        if move.pieceCaptured == "wR":
            if move.startRow == 7:
                if move.startCol == 0:  # left Rook
                    self.currentCastleRight.wqs = False
                elif move.startCol == 7:  # right rook
                    self.currentCastleRight.wks = False
        elif move.pieceCaptured == "bR":
            if move.startRow == 0:
                if move.startCol == 0:  # left Rook
                    self.currentCastleRight.bqs = False
                elif move.startCol == 7:  # right rook
                    self.currentCastleRight.bks = False


    def getValidMoves(self):
        tempEnPassantPossible = self.enPassantPossible
        tempCastleRights = CastleRights(self.currentCastleRight.wks,self.currentCastleRight.bks,
                                        self.currentCastleRight.wqs,self.currentCastleRight.bqs)    #copy the current castling rights
        #generate all the moves
        moves = self.getAllPossibleMoves()
        if self.whiteToMove :
            self.getCastleMoves(self.whiteKingPosition[0],self.whiteKingPosition[1],moves)
        else :
            self.getCastleMoves(self.blackKingPosition[0],self.blackKingPosition[1],moves)

        #for each move, make a move
        for i in range(len(moves)-1,-1,-1) : #when removing a list go backward
            self.makeMove(moves[i]) #let white turn then black turn because of inside turn in make move
            self.whiteToMove = not self.whiteToMove #flip the turn white again
            if self.inCheck() : #now incheck for white king
                moves.remove(moves[i])
            #to undo the move first make it black turn so the previous white turn can restore
            self.whiteToMove = not self.whiteToMove
            self.undoMove()

        if len(moves) == 0 :
            if self.inCheck() :
                self.checkMate = True
            else :
                self.staleMate = True
        else :
            self.checkMate = False
            self.staleMate = False
        self.enPassantPossible = tempEnPassantPossible
        self.currentCastleRight = tempCastleRights
        return moves

    def inCheck(self):
        if self.whiteToMove :
            return self.squareUnderAttack(self.whiteKingPosition[0],self.whiteKingPosition[1])
        else :
            return self.squareUnderAttack(self.blackKingPosition[0], self.blackKingPosition[1])
    def squareUnderAttack(self,r,c):
        self.whiteToMove = not self.whiteToMove #turn it to black
        opponentMoves = self.getAllPossibleMoves()
        #check whether any opponent moves collide with our king
        for move in opponentMoves :
            if move.endRow == r and move.endCol == c :
                self.whiteToMove = not self.whiteToMove
                return True

        self.whiteToMove = not self.whiteToMove
        return False



    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)) :
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                #piece = self.board[r][c][1]
                if (turn=='w' and self.whiteToMove) or (turn=='b' and not self.whiteToMove) :
                    if self.board[r][c][1]=='p' :
                        self.getPawnMoves(r,c,moves)
                    elif self.board[r][c][1]=='R' :
                        self.getRockMoves(r,c,moves)
                    elif self.board[r][c][1]=='N' :
                        self.getKnightMoves(r,c,moves)
                    elif self.board[r][c][1]=='B' :
                        self.getBishopMoves(r,c,moves)
                    elif self.board[r][c][1]=='Q' :
                        self.getQueenMoves(r,c,moves)
                    elif self.board[r][c][1]=='K' :
                        self.getKingMoves(r,c,moves)
        return moves

    def getPawnMoves(self,r,c,moves):
        if self.whiteToMove :
            if r-1>=0 and c-1>=0 and self.board[r-1][c-1][0]=='b' : #left
                moves.append(Move((r,c),(r-1,c-1),self.board))
            if r-1>=0 and c+1<8 and self.board[r-1][c+1][0]=='b' : #right
                moves.append(Move((r,c),(r-1,c+1),self.board))
            #en passant move
            if r-1>=0 and c-1>=0 and (r-1,c-1)==self.enPassantPossible :
                moves.append(Move((r,c),(r-1,c-1),self.board,isEnPassantMove=True))

            if r-1>=0 and c+1<8 and (r-1,c+1)==self.enPassantPossible :
                moves.append(Move((r,c),(r-1,c+1),self.board,isEnPassantMove=True))

            if self.board[r-1][c]=="--" :
                moves.append(Move((r,c),(r-1,c),self.board))
                if r==6 and self.board[r-2][c]=="--" :
                    moves.append(Move((r,c),(r-2,c),self.board))
        else :
            if r+1<8 and c-1>=0 and self.board[r+1][c-1][0]=='w' :
                moves.append(Move((r,c),(r+1,c-1),self.board))
            if r+1<8 and c+1<8 and self.board[r+1][c+1][0]=='w' :
                moves.append(Move((r,c),(r+1,c+1),self.board))
            #en passant move
            if r+1>=0 and c-1>=0 and (r+1,c-1)==self.enPassantPossible :
                moves.append(Move((r,c),(r+1,c-1),self.board,isEnPassantMove=True))
            if r+1>=0 and c+1<8 and (r+1,c+1)==self.enPassantPossible :
                moves.append(Move((r,c),(r+1,c+1),self.board,isEnPassantMove=True))
            if self.board[r+1][c]=="--" :
                moves.append(Move((r,c),(r+1,c),self.board))
                if r==1 and self.board[r+2][c]=="--" :
                    moves.append(Move((r,c),(r+2,c),self.board))


    def getRockMoves(self,r,c,moves):
        #upper direction
        i=r-1
        j=c
        while i>=0 :
            if self.board[i][j]!="--":
                if self.board[i][j][0]==self.board[r][c][0] :
                    break
                else :
                    moves.append(Move((r, c), (i, j), self.board))
                    break
            moves.append(Move((r, c), (i, j), self.board))
            i=i-1
        #down direction
        i=r+1
        j=c
        while i<8 :
            if self.board[i][j]!="--" :
                if self.board[i][j][0] == self.board[r][c][0]:
                    break
                else :
                    moves.append(Move((r, c), (i, j), self.board))
                    break
            moves.append(Move((r, c), (i, j), self.board))
            i=i+1
        #right direction
        i=r
        j=c+1
        while j<8 :
            if self.board[i][j]!="--" :
                if self.board[i][j][0] == self.board[r][c][0]:
                    break
                else :
                    moves.append(Move((r, c), (i, j), self.board))
                    break
            moves.append(Move((r, c), (i, j), self.board))
            j=j+1
        #left direction
        i=r
        j=c-1
        while j>=0 :
            if self.board[i][j]!="--" :
                if self.board[i][j][0] == self.board[r][c][0]:
                    break
                else :
                    moves.append(Move((r, c), (i, j), self.board))
                    break
            moves.append(Move((r, c), (i, j), self.board))
            j=j-1

    def getKnightMoves(self,r,c,moves):
        # upper direction
        if r-2 >= 0 :
            if c-1>=0 and (self.board[r-2][c-1]=="--" or self.board[r-2][c-1][0]!=self.board[r][c][0]) :
                moves.append(Move((r,c),(r-2,c-1),self.board))
            if c+1<8 and (self.board[r-2][c+1]=="--" or self.board[r-2][c+1][0]!=self.board[r][c][0]) :
                moves.append(Move((r,c),(r-2,c+1),self.board))
        #down direction
        if r + 2 < 8:
            if c - 1 >= 0 and (self.board[r + 2][c - 1] == "--" or self.board[r + 2][c - 1][0]!=self.board[r][c][0]):
                moves.append(Move((r, c), (r + 2, c - 1), self.board))
            if c + 1 < 8 and (self.board[r + 2][c + 1] == "--" or self.board[r + 2][c + 1][0]!=self.board[r][c][0]):
                moves.append(Move((r, c), (r + 2, c + 1), self.board))
        # right direction
        if c + 2 < 8:
            if r - 1 >= 0 and (self.board[r - 1][c + 2] == "--" or self.board[r - 1][c + 2][0]!=self.board[r][c][0]):
                moves.append(Move((r, c), (r - 1, c + 2), self.board))
            if r + 1 < 8 and (self.board[r + 1][c + 2] == "--" or self.board[r + 1][c + 2][0]!=self.board[r][c][0]):
                moves.append(Move((r, c), (r + 1, c + 2), self.board))
        # left direction
        if c - 2 >= 0:
            if r - 1 >= 0 and (self.board[r - 1][c - 2] == "--" or self.board[r - 1][c - 2][0]!=self.board[r][c][0]):
                moves.append(Move((r, c), (r - 1, c - 2), self.board))
            if r + 1 < 8 and (self.board[r + 1][c - 2] == "--" or self.board[r + 1][c - 2][0]!=self.board[r][c][0]):
                moves.append(Move((r, c), (r + 1, c - 2), self.board))

    def getBishopMoves(self,r,c,moves):
        # upper right direction
        i = r - 1
        j = c + 1
        while i >= 0 and j < 8:
            if self.board[i][j] != "--":
                if self.board[i][j][0] == self.board[r][c][0]:
                    break
                else:
                    moves.append(Move((r, c), (i, j), self.board))
                    break
            moves.append(Move((r, c), (i, j), self.board))
            i = i - 1
            j = j + 1
        # down right direction
        i = r + 1
        j = c + 1
        while i < 8 and j < 8:
            if self.board[i][j] != "--":
                if self.board[i][j][0] == self.board[r][c][0]:
                    break
                else:
                    moves.append(Move((r, c), (i, j), self.board))
                    break
            moves.append(Move((r, c), (i, j), self.board))
            i = i + 1
            j = j + 1
        # upper left direction
        i = r - 1
        j = c - 1
        while i >= 0 and j >= 0:
            if self.board[i][j] != "--":
                if self.board[i][j][0] == self.board[r][c][0]:
                    break
                else:
                    moves.append(Move((r, c), (i, j), self.board))
                    break
            moves.append(Move((r, c), (i, j), self.board))
            i = i - 1
            j = j - 1
        # down left direction
        i = r + 1
        j = c - 1
        while i < 8 and j >= 0:
            if self.board[i][j] != "--":
                if self.board[i][j][0] == self.board[r][c][0]:
                    break
                else:
                    moves.append(Move((r, c), (i, j), self.board))
                    break
            moves.append(Move((r, c), (i, j), self.board))
            i = i + 1
            j = j - 1
    def getQueenMoves(self,r,c,moves):
        self.getBishopMoves(r,c,moves)
        self.getRockMoves(r,c,moves)
    def getKingMoves(self,r,c,moves):
        # kingMoves = ((-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1))
        '''
        for i in range(8) :
            x = r + kingMoves[i][0]
            y = c + kingMoves[i][1]
            if x>=0 and x<8 and y>=0 and y<8 and (self.board[x][y]=="--" or self.board[x][y][0]!=self.board[r][c][0]) :
                moves.append(Move((r,c),(x,y),self.board))
        '''
        #upper side
        if r-1 >= 0 :
            if self.board[r-1][c]=="--" or self.board[r-1][c][0]!=self.board[r][c][0] :
                moves.append(Move((r,c),(r-1,c),self.board))
            if c-1>=0 and (self.board[r-1][c-1]=="--" or self.board[r-1][c-1][0]!=self.board[r][c][0]) :
                moves.append(Move((r,c),(r-1,c-1),self.board))
            if c+1<8 and (self.board[r-1][c+1]=="--" or self.board[r-1][c+1][0]!=self.board[r][c][0]) :
                moves.append(Move((r,c),(r-1,c+1),self.board))

        # down side
        if r + 1 < 8:
            if self.board[r + 1][c] == "--" or self.board[r + 1][c][0] != self.board[r][c][0]:
                moves.append(Move((r, c), (r + 1, c), self.board))
            if c - 1 >= 0 and (self.board[r + 1][c - 1] == "--" or self.board[r + 1][c - 1][0] != self.board[r][c][0]):
                moves.append(Move((r, c), (r + 1, c - 1), self.board))
            if c + 1 < 8 and (self.board[r + 1][c + 1] == "--" or self.board[r + 1][c + 1][0] != self.board[r][c][0]):
                moves.append(Move((r, c), (r + 1, c + 1), self.board))

        #left side
        if c-1 >= 0 :
            if self.board[r][c-1] == "--" or self.board[r][c-1][0] != self.board[r][c][0]:
                moves.append(Move((r, c), (r, c-1), self.board))
        #right side
        if c+1 < 8 :
            if self.board[r][c+1] == "--" or self.board[r][c+1][0] != self.board[r][c][0]:
                moves.append(Move((r, c), (r, c+1), self.board))

        #allyColor = 'w' if self.whiteToMove else 'b'
        #self.getCastleMoves(r,c,moves)


    def getCastleMoves(self,r,c,moves):
        if self.inCheck() :
            return
        if (self.whiteToMove and self.currentCastleRight.wks) or (not self.whiteToMove and self.currentCastleRight.bks):
            self.getKingSideCastleMoves(r,c,moves)
        if (self.whiteToMove and self.currentCastleRight.wqs) or (not self.whiteToMove and self.currentCastleRight.bqs):
            self.getQueenSideCastleMoves(r,c,moves)

    def getKingSideCastleMoves(self,r,c,moves):
        pieceColor = 'w' if self.whiteToMove else 'b'
        if (self.board[r][c+1]=="--" and self.board[r][c+2]=="--" and self.board[r][c+3]==pieceColor+'R'):
            if not self.squareUnderAttack(r,c+1) and not self.squareUnderAttack(r,c+2) :
                moves.append(Move((r,c),(r,c+2),self.board,isCastleMove=True))

    def getQueenSideCastleMoves(self,r,c,moves):
        pieceColor = 'w' if self.whiteToMove else 'b'
        if self.board[r][c-1]=="--" and self.board[r][c-2]=="--" and self.board[r][c-3]=="--" and self.board[r][c+3]==pieceColor+'R':
            if not self.squareUnderAttack(r,c-1) and not self.squareUnderAttack(r,c-2) :
                moves.append(Move((r,c),(r,c-2),self.board,isCastleMove=True))

class CastleRights() :
    def __init__(self,wks,bks,wqs,bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move():

    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    #rowsToRanks = {"0": 8, "1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1}
    rowsToRanks = {v : k for k,v in ranksToRows.items()}

    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    # colsToFiles = {"0": 'a', "1": 'b',"2": 'c', "3": 'd', "4": 'e', "5": 'f', "6": 'g', "7": 'h'}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self,startSq,endSq,board,isEnPassantMove=False,isCastleMove=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        #pawn promotion
        self.pawnPromotion = False
        if self.pieceMoved=="wp" and self.endRow==0 :
            self.pawnPromotion = True
        elif self.pieceMoved=="bp" and self.endRow==7 :
            self.pawnPromotion = True

        #en passant
        self.isEnPassantMove = isEnPassantMove
        if self.isEnPassantMove :
            self.pieceCaptured = "wp" if self.pieceMoved=="bp" else "bp"

        #castling
        self.isCastleMove = isCastleMove

        self.moveId = self.startRow*1000 + self.startCol*100 + self.endRow*10 + self.endCol



    def getChessNotation(self):
        return self.getRankFile(self.startRow,self.startCol) + self.getRankFile(self.endRow,self.endCol)

    def getRankFile(self,r,c):
        return self.colsToFiles[c] + self.rowsToRanks[r]

    def __eq__(self, other):
        if isinstance(other,Move) :
            return other.moveId == self.moveId
        return False
