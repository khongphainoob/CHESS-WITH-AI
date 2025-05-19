import pygame as pg
import time
from chess import chess_engine

WIDTH = HEIGHT = 512
DIMENSION = 8
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}
def load_images():
    """Load images for the chess pieces."""
    pieces = ['wK', 'wN', 'wB', 'wQ', 'wR', 'wp', 'bK', 'bN', 'bB', 'bQ', 'bR', 'bp']
    for piece in pieces:
        IMAGES[piece] = pg.transform.scale(pg.image.load(f'images/{piece}.png'), (SQ_SIZE, SQ_SIZE))
def draw_game(screen, gs,dragger):
    """Draw the game state on the screen."""
    draw_board(screen)
    draw_pieces(screen, gs.board,dragger)
def draw_board(screen):
    """Draw the chessboard."""
    GREEN = (234,235,200) #light green
    WHITE = (119,154,86) #dark green
    colors = [WHITE, GREEN]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r + c) % 2]
            pg.draw.rect(screen, color, pg.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
def draw_pieces(screen, board,dragger):
    """Draw the pieces on the board."""
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece == "--":
                continue
            if (r,c) != (dragger.initial_y, dragger.initial_x):
                    screen.blit(IMAGES[piece], pg.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
def highlight_squares(screen, gs, valid_moves, sqSelected):
    """Highlight the squares on the board."""
    if gs.in_check == True:
        s = pg.Surface((SQ_SIZE, SQ_SIZE), pg.SRCALPHA)
        s.set_alpha(15050)
        king_pos = gs.white_king_location if gs.white_to_move else gs.black_king_location
        row = king_pos[0]
        col = king_pos[1]
        piece = gs.board[row][col]
        pg.draw.rect(screen, (255, 153, 153), (col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE , SQ_SIZE))
        #pg.draw.circle(s, (255, 0, 0), (SQ_SIZE // 2, SQ_SIZE // 2), SQ_SIZE // 8)
        screen.blit(s, (col * SQ_SIZE, row * SQ_SIZE))
        screen.blit(IMAGES[piece], pg.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ("w" if gs.white_to_move else "b"):
            s = pg.Surface((SQ_SIZE, SQ_SIZE), pg.SRCALPHA)
            s.set_alpha(10000)
            pg.draw.rect(screen, (255, 0, 0), (c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE , SQ_SIZE), 3)
            pg.draw.circle(s, (255, 0, 0), (SQ_SIZE // 2, SQ_SIZE // 2), SQ_SIZE // 8)
            for move in valid_moves:
                if move.start_row == r and move.start_col == c:
                    screen.blit(s, (move.end_col * SQ_SIZE, move.end_row * SQ_SIZE))
def main():
    """Main function to run the chess game."""
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    clock = pg.time.Clock()
    screen.fill(pg.Color("white"))
    load_images()
    gs = chess_engine.GameState()
    valid_moves = gs.getValidMoves()
    move_made = False
    sqSelected = ()
    playerClicks = []
    running = True
    dragger = chess_engine.dragger()
    while running:
        draw_game(screen, gs,dragger)
        highlight_squares(screen, gs, valid_moves, sqSelected)
        if dragger.dragging:
            dragger.update_blit(screen, SQ_SIZE)
        for e in pg.event.get():
            if e.type == pg.QUIT:
                running = False
            if e.type == pg.MOUSEBUTTONDOWN:
                
                location = pg.mouse.get_pos()
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE
                #print(f"row: {row}, col: {col}")
                if sqSelected == (row, col):
                    sqSelected = ()
                    playerClicks = []
                else : 
                     sqSelected = (row, col)
                     playerClicks.append(sqSelected)
                if len(playerClicks) == 2:
                    move = chess_engine.Move(playerClicks[0], playerClicks[1], gs.board)
                    valid_moves = gs.getValidMoves()
                    for i in range(len(valid_moves)):
                        if move == valid_moves[i]:  
                            move_made = True
                            gs.makeMove(valid_moves[i])
                            sqSelected = ()
                            playerClicks = []
                    if not move_made:
                        playerClicks = [sqSelected]
                dragger.update_mouse(col,row)
                if gs.board[row][col] != "--":
                       piece = gs.board[row][col]
                       dragger.save_initial_position(col,row)
                       dragger.drag_piece(piece)
            elif e.type == pg.MOUSEMOTION:
                location = pg.mouse.get_pos()
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE
                if dragger.dragging:
                    dragger.update_mouse(col,row)
                    draw_game(screen, gs,dragger)
                    highlight_squares(screen, gs, valid_moves, sqSelected)
                    dragger.update_blit(screen, SQ_SIZE)
                   # print(f"Dragging {dragger.piece} to {dragger.initial_x}, {dragger.initial_y}")
                   # print(f"Dragging {dragger.piece} to {col}, {row}")
            elif e.type == pg.MOUSEBUTTONUP:
                location = pg.mouse.get_pos()
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE
                if dragger.dragging and (row, col) != (dragger.initial_y, dragger.initial_x):
                    move = chess_engine.Move((dragger.initial_y, dragger.initial_x), (row, col), gs.board)
                    valid_moves = gs.getValidMoves()
                    for i in range(len(valid_moves)):
                        if move == valid_moves[i]:  
                            move_made = True
                            gs.makeMove(valid_moves[i])
                            dragger.undrag_piece()
                    if not move_made:
                        dragger.undrag_piece()
                else : dragger.undrag_piece()
            elif e.type == pg.KEYDOWN:
                if e.key == pg.K_z:
                    gs.undoMove()
                    move_made = True
        if move_made:
            valid_moves = gs.getValidMoves()
            move_made = False
        clock.tick(MAX_FPS)
        pg.display.flip()
if __name__ == "__main__":
    main()
