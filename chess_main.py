
#this is responsible for handling user input and displaying the current game state objects
#this is the main driver file

import pygame as p
import sys
import chess_engine,smart_move_finder

BOARD_WIDTH = BOARD_HEIGHT = 512
MOVE_LOG_PANEL_WIDTH = 200
MOVE_LOG_PANEL_HEIGHT = BOARD_HEIGHT
DIMENSION = 8 #like 8*8 board
SQ_SIZE = BOARD_HEIGHT//DIMENSION
MAX_FPS = 15 #used for animation
playerOne = True
playerTwo = True
color1 = "white"
color2 = "light gray"

IMAGES = {}

'''
initialize a global dictionary for images
it will be called once in the main
'''

def loadImages():
    pieces = ["bR", "bN", "bB", "bQ", "bK", "bp", "wR", "wN", "wB", "wQ", "wK", "wp"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/"+piece+".png"),(SQ_SIZE,SQ_SIZE))


#this will handle the user input and updating the graphics

def menu():
    p.init()
    screen = p.display.set_mode((BOARD_WIDTH+MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    clock = p.time.Clock()
    #screen.fill(p.Color("white"))
    bg = p.transform.scale(p.image.load("images/menuback.jpg"),(BOARD_WIDTH+MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    screen.blit(bg,(0,0))
    click = False
    font = p.font.SysFont('Helvitca', 32, True, False)  # font-name,size,bold,italic

    game_btn = p.draw.rect(screen, 'gray', p.Rect(3 * SQ_SIZE, 4 * SQ_SIZE, 130, 30))
    drawText("Play Game", font, p.Color('black'), screen, 3 * SQ_SIZE, 4 * SQ_SIZE)

    options_btn = p.draw.rect(screen, 'gray', p.Rect(3 * SQ_SIZE, 5 * SQ_SIZE, 130, 30))
    drawText("Options", font, p.Color('black'), screen, 3 * SQ_SIZE, 5 * SQ_SIZE)

    exit_btn = p.draw.rect(screen, 'gray', p.Rect(3 * SQ_SIZE, 6 * SQ_SIZE, 130, 30))
    drawText("Exit Game", font, p.Color('black'), screen, 3 * SQ_SIZE, 6 * SQ_SIZE)

    running = True
    while running :
        if click:
            if game_btn.collidepoint(p.mouse.get_pos()) and p.mouse.get_pressed()[0]:
                running = False
                game()
            elif options_btn.collidepoint(p.mouse.get_pos()) and p.mouse.get_pressed()[0]:
                running = False
                options()
            elif exit_btn.collidepoint(p.mouse.get_pos()) and p.mouse.get_pressed()[0]:
                sys.exit()

        for e in p.event.get() :
            if e.type == p.QUIT :
                running = False
            elif e.type == p.MOUSEBUTTONDOWN :
                click = True
            elif e.type == p.KEYDOWN :
                if e.key == p.K_ESCAPE : #when ESCAPE is pressed
                    sys.exit()



        clock.tick(MAX_FPS)
        p.display.flip()

def game():
    p.init()
    screen = p.display.set_mode((BOARD_WIDTH+MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    #screen.blit(p.image.load("images/menuback.png"),0,0)
    gs = chess_engine.GameState()
    #print(gs.board)

    validMoves = gs.getValidMoves()
    moveLogFont = p.font.SysFont('Arial', 12, False, False)  # font-name,size,bold,italic
    moveMade = False    #flag variable when move is made
    animate = False     #flag variable when animate is made
    loadImages() #it loaded once
    running = True
    gameOver = False
    global playerOne
    global playerTwo
    #playerOne = True #if human is playing then true else if ai is playing then false
    #playerTwo = True #if human is playiing then true else if ai is playing then false

    sqSelected = () #to keep the selected square
    playerClicks = [] #to keep the track of two clicks of player
    while running :
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        r = 0
        c = 0
        move = chess_engine.Move((0,0),(1,1),gs.board)
        for e in p.event.get() :
            if e.type == p.QUIT :
                running = False
            elif e.type == p.MOUSEBUTTONDOWN :
                location = p.mouse.get_pos()
                r = location[0]
                c = location[1]
                if gameOver and location[0]>=3*SQ_SIZE and location[0]<=3*SQ_SIZE+130 and location[1]>=5*SQ_SIZE and location[1]<=5*SQ_SIZE+30:
                    gs = chess_engine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False
                elif not gameOver and humanTurn :
                    location = p.mouse.get_pos() #in (x,y)
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    if sqSelected == (row,col) or col>=8:   #to deselect the click
                        sqSelected = ()
                        playerClicks = []
                    else :
                        sqSelected = (row,col)
                        playerClicks.append(sqSelected) #append the both click
                    if len(playerClicks)==2 : #make move after two clicks
                        move = chess_engine.Move(playerClicks[0],playerClicks[1],gs.board)
                        print(move.getChessNotation())
                        for i in range(len(validMoves)) :
                            if move == validMoves[i] :
                                gs.makeMove(validMoves[i])
                                if move.pawnPromotion:
                                    promotedPiece = drawPawnPromotion(screen,gs)
                                    gs.board[move.endRow][move.endCol] = promotedPiece
                                moveMade = True
                                animate = True
                                sqSelected = () #reset the clicks
                                playerClicks = []
                        if not moveMade :
                            playerClicks = [sqSelected]
            elif e.type == p.KEYDOWN :
                if e.key == p.K_z : #when z is pressed
                    gs.undoMove()
                    moveMade = True
                    animate = False
                elif e.key == p.K_r : #when r is pressed then reset
                    gs = chess_engine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                elif e.key==p.K_ESCAPE :
                    running = False
                    menu()

        #AI move finder
        if not gameOver and not humanTurn :
            AIMove = smart_move_finder.findBestMinMaxRecurMove(gs, validMoves)   #multi level possibility
            #AIMove = smart_move_finder.findMinMaxMove(gs, validMoves)   #at 2 level possibility
            #AIMove = smart_move_finder.findGreedyMove(gs,validMoves)
            #AIMove = smart_move_finder.findRandomMove(validMoves)      #get any random moves
            if AIMove is None :
                AIMove = smart_move_finder.findRandomMove(validMoves)
            gs.makeMove(AIMove)
            moveMade = True
            animate = True

        if moveMade :   #if move is made then go for next move
            if animate :
                animateMove(gs.moveLog[-1],screen,gs.board,clock)

            validMoves = gs.getValidMoves() #call for next valid moves
            moveMade = False
            animate = False

        drawGameState(screen,gs,validMoves,sqSelected,moveLogFont,move)
        if gs.checkMate or gs.staleMate :
            running = False
            gameOver = True
            if gs.staleMate :
                text = "Stalemate"
            else :
                text ="Black king wins the game" if gs.whiteToMove else "White king wins the game"

            drawEndGameText(screen,text)
        clock.tick(MAX_FPS)
        p.display.flip()

def options():
    p.init()
    screen = p.display.set_mode((BOARD_WIDTH+MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    clock = p.time.Clock()
    #screen.fill(p.Color("white"))
    bg = p.transform.scale(p.image.load("images/menuback.jpg"), (BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    screen.blit(bg, (0, 0))
    click = False
    font = p.font.SysFont('Helvitca', 32, True, False)  # font-name,size,bold,italic

    player_option_btn = p.draw.rect(screen, 'gray', p.Rect(3 * SQ_SIZE, 4 * SQ_SIZE, 130, 30))
    drawText("Player Option", font, p.Color('black'), screen, 3 * SQ_SIZE, 4 * SQ_SIZE)

    color_option_btn = p.draw.rect(screen, 'gray', p.Rect(3 * SQ_SIZE, 5 * SQ_SIZE, 130, 30))
    drawText("Color Options", font, p.Color('black'), screen, 3 * SQ_SIZE, 5 * SQ_SIZE)

    back_btn = p.draw.rect(screen, 'gray', p.Rect(3 * SQ_SIZE, 6 * SQ_SIZE, 130, 30))
    drawText("Back To Menu", font, p.Color('black'), screen, 3 * SQ_SIZE, 6 * SQ_SIZE)

    running = True
    while running :

        if click:
            if player_option_btn.collidepoint(p.mouse.get_pos()) and p.mouse.get_pressed()[0]:
                running = False
                player_option()
            elif color_option_btn.collidepoint(p.mouse.get_pos()) and p.mouse.get_pressed()[0]:
                running = False
                color_option()
            elif back_btn.collidepoint(p.mouse.get_pos()) and p.mouse.get_pressed()[0]:
                running = False
                menu()

        for e in p.event.get() :
            if e.type == p.QUIT :
                running = False
            elif e.type == p.MOUSEBUTTONDOWN :
                click = True

            elif e.type == p.KEYDOWN :
                if e.key == p.K_ESCAPE : #when ESCAPE is pressed
                    running = False
                    menu()

        clock.tick(MAX_FPS)
        p.display.flip()


def player_option():
    p.init()
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    clock = p.time.Clock()
    #screen.fill(p.Color("white"))
    bg = p.transform.scale(p.image.load("images/menuback.jpg"), (BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    screen.blit(bg, (0, 0))
    click = False
    font = p.font.SysFont('Helvitca', 32, True, False)  # font-name,size,bold,italic

    humanVsComputer_btn = p.draw.rect(screen, 'white', p.Rect(3 * SQ_SIZE, 3 * SQ_SIZE, 250, 30))
    drawText("Human Vs Computer", font, p.Color('black'), screen, 3 * SQ_SIZE, 3 * SQ_SIZE)

    humanVsHuman_btn = p.draw.rect(screen, 'white', p.Rect(3 * SQ_SIZE, 4 * SQ_SIZE, 250, 30))
    drawText("Human vs Human", font, p.Color('black'), screen, 3 * SQ_SIZE, 4 * SQ_SIZE)

    playing_white_btn = p.draw.rect(screen, 'white', p.Rect(3 * SQ_SIZE, 5 * SQ_SIZE, 250, 30))
    drawText("Playing from white side", font, p.Color('black'), screen, 3 * SQ_SIZE, 5 * SQ_SIZE)

    playing_black_btn = p.draw.rect(screen, 'white', p.Rect(3 * SQ_SIZE, 6 * SQ_SIZE, 250, 30))
    drawText("Playing from black side", font, p.Color('black'), screen, 3 * SQ_SIZE, 6 * SQ_SIZE)

    back_btn = p.draw.rect(screen, 'white', p.Rect(3 * SQ_SIZE, 7 * SQ_SIZE, 250, 30))
    drawText("Back To Options", font, p.Color('black'), screen, 3 * SQ_SIZE, 7 * SQ_SIZE)

    global playerOne
    global playerTwo

    running = True
    while running:

        if click:
            if humanVsComputer_btn.collidepoint(p.mouse.get_pos()) and p.mouse.get_pressed()[0]:
                playerTwo = False
            elif humanVsHuman_btn.collidepoint(p.mouse.get_pos()) and p.mouse.get_pressed()[0]:
                playerTwo = True
            elif playing_white_btn.collidepoint(p.mouse.get_pos()) and p.mouse.get_pressed()[0]:
                playerOne = True
            elif playing_black_btn.collidepoint(p.mouse.get_pos()) and p.mouse.get_pressed()[0]:
                playerTwo = True
            elif back_btn.collidepoint(p.mouse.get_pos()) and p.mouse.get_pressed()[0]:
                running = False
                options()

        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                click = True

            elif e.type == p.KEYDOWN:
                if e.key == p.K_ESCAPE:  # when ESCAPE is pressed
                    running = False
                    options()

        clock.tick(MAX_FPS)
        p.display.flip()


def color_option():
    p.init()
    screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    clock = p.time.Clock()
    #screen.fill(p.Color("white"))
    bg = p.transform.scale(p.image.load("images/menuback.jpg"), (BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    screen.blit(bg, (0, 0))
    click = False
    font = p.font.SysFont('Helvitca', 32, True, False)  # font-name,size,bold,italic

    white_light_gray_btn = p.draw.rect(screen, 'white', p.Rect(3 * SQ_SIZE, 3 * SQ_SIZE, 130, 30))
    drawText("White & light gray", font, p.Color('black'), screen, 3 * SQ_SIZE, 3 * SQ_SIZE)

    white_blue_btn = p.draw.rect(screen, 'white', p.Rect(3 * SQ_SIZE, 4 * SQ_SIZE, 130, 30))
    drawText("White & blue", font, p.Color('black'), screen, 3 * SQ_SIZE, 4 * SQ_SIZE)

    white_green_btn = p.draw.rect(screen, 'white', p.Rect(3 * SQ_SIZE, 5 * SQ_SIZE, 130, 30))
    drawText("White & green", font, p.Color('black'), screen, 3 * SQ_SIZE, 5 * SQ_SIZE)

    white_gold_btn = p.draw.rect(screen, 'white', p.Rect(3 * SQ_SIZE, 6 * SQ_SIZE, 130, 30))
    drawText("White & gold", font, p.Color('black'), screen, 3 * SQ_SIZE, 6 * SQ_SIZE)

    light_dark_blue_btn = p.draw.rect(screen, 'white', p.Rect(3 * SQ_SIZE, 7 * SQ_SIZE, 130, 30))
    drawText("Light blue & dark blue", font, p.Color('black'), screen, 3 * SQ_SIZE, 7 * SQ_SIZE)
    running = True
    #without making it global you cannot modify it
    global color1
    global color2

    while running:

        if click:
            if white_light_gray_btn.collidepoint(p.mouse.get_pos()) and p.mouse.get_pressed()[0]:
                color1 = (249, 250, 251)
                color2 = (115, 118, 120)
            elif white_blue_btn.collidepoint(p.mouse.get_pos()) and p.mouse.get_pressed()[0]:
                color1 = (223, 236, 244)
                color2 = (24, 78, 148)
            elif white_gold_btn.collidepoint(p.mouse.get_pos()) and p.mouse.get_pressed()[0]:
                color1 = (249, 200, 54)
                color2 = (188, 100, 12)
            elif white_green_btn.collidepoint(p.mouse.get_pos()) and p.mouse.get_pressed()[0]:
                color1 = (221, 253, 232)
                color2 = (89, 153, 16)
            elif light_dark_blue_btn.collidepoint(p.mouse.get_pos()) and p.mouse.get_pressed()[0]:
                color1 = (184, 243, 251)
                color2 = (67, 133, 176)

        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                click = True

            elif e.type == p.KEYDOWN:
                if e.key == p.K_ESCAPE:  # when ESCAPE is pressed
                    running = False
                    options()

        clock.tick(MAX_FPS)
        p.display.flip()


def drawPawnPromotion(screen,gs):
    p.init()
    #screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    clock = p.time.Clock()
    #screen.fill(p.Color("white"))
    font = p.font.SysFont('Helvitca',10,True, False)  # font-name,size,bold,italic
    turn = 'b' if gs.whiteToMove else 'w'
    rook_btn = p.draw.rect(screen, 'white', p.Rect(2 * SQ_SIZE - 40, 4 * SQ_SIZE, SQ_SIZE, SQ_SIZE))
    #drawText("Rook", font, p.Color('black'), screen, SQ_SIZE, SQ_SIZE)
    screen.blit(IMAGES[turn+'R'], p.Rect(2 * SQ_SIZE - 40, 4 * SQ_SIZE, SQ_SIZE, SQ_SIZE))

    bishop_btn = p.draw.rect(screen, 'white', p.Rect(3 * SQ_SIZE - 40, 4 * SQ_SIZE, SQ_SIZE, SQ_SIZE))
    #drawText("Bishop", font, p.Color('black'), screen, SQ_SIZE, SQ_SIZE)
    screen.blit(IMAGES[turn + 'B'], p.Rect(3 * SQ_SIZE - 40, 4 * SQ_SIZE, SQ_SIZE, SQ_SIZE))

    knight_btn = p.draw.rect(screen, 'white', p.Rect(4 * SQ_SIZE - 40, 4 * SQ_SIZE, SQ_SIZE, SQ_SIZE))
    #drawText("Knight", font, p.Color('black'), screen, SQ_SIZE, SQ_SIZE)
    screen.blit(IMAGES[turn + 'N'], p.Rect(4 * SQ_SIZE - 40, 4 * SQ_SIZE, SQ_SIZE, SQ_SIZE))

    queen_btn = p.draw.rect(screen, 'white', p.Rect(5 * SQ_SIZE - 40, 4 * SQ_SIZE, SQ_SIZE, SQ_SIZE))
    #drawText("Queen", font, p.Color('black'), screen, SQ_SIZE, SQ_SIZE)
    screen.blit(IMAGES[turn + 'Q'], p.Rect(5 * SQ_SIZE - 40, 4 * SQ_SIZE, SQ_SIZE, SQ_SIZE))
    promotedPiece = 'wQ'
    click = False
    running = True
    while running :
        if click :
            if rook_btn.collidepoint(p.mouse.get_pos()) and p.mouse.get_pressed()[0]:
                running = False
                promotedPiece = turn + 'R'
            elif bishop_btn.collidepoint(p.mouse.get_pos()) and p.mouse.get_pressed()[0]:
                running = False
                promotedPiece = turn + 'B'
            elif knight_btn.collidepoint(p.mouse.get_pos()) and p.mouse.get_pressed()[0]:
                running = False
                promotedPiece = turn + 'N'
            elif queen_btn.collidepoint(p.mouse.get_pos()) and p.mouse.get_pressed()[0]:
                running = False
                promotedPiece = turn + 'Q'

        for e in p.event.get() :
            if e.type==p.QUIT :
                running = False
            elif e.type==p.MOUSEBUTTONDOWN :
                click = True
            elif e.type==p.KEYDOWN :
                if e.type==p.K_ESCAPE :
                    sys.exit()
        clock.tick(MAX_FPS)
        p.display.flip()
    return promotedPiece

def highlightingSquares(screen,gs,validMoves,sqSelected) :
    if sqSelected != () :
        r,c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b') :
            #highlighting selected squares
            s = p.Surface((SQ_SIZE,SQ_SIZE))
            s.set_alpha(100)    #0 means transparent 255 means opaque
            s.fill(p.Color('blue')) #fill the surface with blue color
            screen.blit(s,(c*SQ_SIZE,r*SQ_SIZE))    #place that surface to the r,c position
            #highlighting moves squares of the selected square
            s.fill(p.Color('green'))
            for move in validMoves :
                if move.startRow==r and move.startCol==c :
                    screen.blit(s,(move.endCol*SQ_SIZE,move.endRow*SQ_SIZE))

def animateMove(move,screen,board,clock) :
    global colors
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 10
    frameCounts = (abs(dR)+abs(dC))*framesPerSquare
    for frame in range(frameCounts+1) :
        r, c = (move.startRow + dR*frame/frameCounts, move.startCol + dC*frame/frameCounts)
        drawBoard(screen)
        drawPieces(screen,board)
        #erase the piece moved from the ending square
        color = colors[(move.endRow+move.endCol)%2]
        endSquare = p.Rect(move.endCol*SQ_SIZE,move.endRow*SQ_SIZE,SQ_SIZE,SQ_SIZE)
        p.draw.rect(screen,color,endSquare)
        #draw captured piece on rectangle
        if move.pieceCaptured != "--" :
            if move.isEnPassantMove :
                enPassantRow = move.endRow+1 if move.pieceCaptured[0]=='b' else move.endRow-1
                endSquare = p.Rect(move.endCol*SQ_SIZE,enPassantRow*SQ_SIZE,SQ_SIZE,SQ_SIZE)
            screen.blit(IMAGES[move.pieceCaptured],endSquare)
        #draw moved piece
        screen.blit(IMAGES[move.pieceMoved],p.Rect(c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE))#r and c is continuously changing
        p.display.flip()
        clock.tick(60)

def drawEndGameText(screen,text) :
    font = p.font.SysFont('Helvitca',32,True,False)#font-name,size,bold,italic
    textObject = font.render(text,0,p.Color('Gray'))
    # textLocation = p.Rect(0,0,BOARD_WIDTH,BOARD_HEIGHT).move(BOARD_WIDTH/2 - textObject.get_width()/2,BOARD_HEIGHT/2 - textObject.get_height()/2)
    textLocation = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(2*SQ_SIZE,3*SQ_SIZE)
    screen.blit(textObject,textLocation)
    textObject = font.render(text,2,p.Color('Black'))
    screen.blit(textObject,textLocation.move(2,2))
    drawMenuOption(screen)

def drawCheckSquare(screen,gs):
    if gs.whiteToMove :
        r = gs.whiteKingPosition[0]
        c = gs.whiteKingPosition[1]
    else :
        r = gs.blackKingPosition[0]
        c = gs.blackKingPosition[1]
    p.draw.rect(screen, 'red', p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def drawMenuOption(screen):
    p.init()
    #screen = p.display.set_mode((BOARD_WIDTH + MOVE_LOG_PANEL_WIDTH, BOARD_HEIGHT))
    clock = p.time.Clock()
    #screen.fill(p.Color("white"))
    font = p.font.SysFont('Helvitca', 32, True, False)  # font-name,size,bold,italic
    click = False
    menu_btn = p.draw.rect(screen, 'white', p.Rect(3 * SQ_SIZE, 4 * SQ_SIZE, 130, 30))
    drawText("Go To Menu", font, p.Color('black'), screen, 3 * SQ_SIZE, 4 * SQ_SIZE)

    restart_btn = p.draw.rect(screen, 'white', p.Rect(3 * SQ_SIZE, 5 * SQ_SIZE, 130, 30))
    drawText("Restart", font, p.Color('black'), screen, 3 * SQ_SIZE, 5 * SQ_SIZE)

    exit_btn = p.draw.rect(screen, 'white', p.Rect(3 * SQ_SIZE, 6 * SQ_SIZE, 130, 30))
    drawText("Exit Game", font, p.Color('black'), screen, 3 * SQ_SIZE, 6 * SQ_SIZE)

    running = True
    while running :
        if click :
            if menu_btn.collidepoint(p.mouse.get_pos()) and p.mouse.get_pressed()[0]:
                running = False
                menu()
            elif restart_btn.collidepoint(p.mouse.get_pos()) and p.mouse.get_pressed()[0]:
                running = False
                game()
            elif exit_btn.collidepoint(p.mouse.get_pos()) and p.mouse.get_pressed()[0]:
                sys.exit()

        for e in p.event.get() :
            if e.type==p.QUIT :
                running = False
            elif e.type==p.MOUSEBUTTONDOWN :
                click = True
            elif e.type==p.KEYDOWN :
                if e.type==p.K_ESCAPE :
                    sys.exit()
        clock.tick(MAX_FPS)
        p.display.flip()

def drawText(text,font,color,screen,x,y):
    textObject = font.render(text,1,color)
    textRect = textObject.get_rect()
    textRect.topleft = (x,y)
    screen.blit(textObject,textRect)

def drawGameState(screen, gs, validMoves, sqSelected,moveLogFont,move):
    drawBoard(screen) #draw square black and white on the board
    highlightingSquares(screen,gs,validMoves,sqSelected)    #add in piece highlighting and add move suggestion
    if gs.inCheck() :
        drawCheckSquare(screen,gs)
    drawPieces(screen,gs.board) #draw pieces on the board
    drawMoveLog(screen,gs,moveLogFont)

def drawBoard(screen):
    global colors
    colors = [p.Color(color1),p.Color(color2)]
    for r in range(DIMENSION) :
        for c in range(DIMENSION) :
            color = colors[((r+c)%2)]
            p.draw.rect(screen,color,p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawPieces(screen,board):
    for r in range(DIMENSION) :
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--" :
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE))

def drawMoveLog(screen,gs,font) :
    moveLogRect = p.Rect(BOARD_WIDTH,0,MOVE_LOG_PANEL_WIDTH,MOVE_LOG_PANEL_HEIGHT)
    p.draw.rect(screen,p.Color('gray'),moveLogRect)
    moveLog = gs.moveLog
    wc = 0
    wr = 4
    bc = 0
    br = 0
    for piece in gs.pieceCapturedLog :
        if piece!="--":
            if piece[0]=='w' :
                pieceCapturedLogRect = p.Rect(BOARD_WIDTH + 11.2*(wc+1) + wc * 36, wr * 36+20*wr, 36, 36)
                wc = (wc + 1) % 4
                if wc == 0:
                    wr = wr + 1
            else :
                pieceCapturedLogRect = p.Rect(BOARD_WIDTH + 11.2*(bc+1) + bc * 36, br * 36+20*br, 36, 36)
                bc = (bc + 1) % 4
                if bc == 0:
                    br = br + 1
            screen.blit(IMAGES[piece],pieceCapturedLogRect)



if __name__ == '__main__':
    menu()



