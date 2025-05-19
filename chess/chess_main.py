import pygame as pg
import time
from . import chess_engine

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
def draw_game(screen, gs):
    """Draw the game state on the screen."""
    draw_board(screen)
    draw_pieces(screen, gs.board)
def draw_board(screen):
    """Draw the chessboard."""
    colors = [pg.Color("white"), pg.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r + c) % 2]
            pg.draw.rect(screen, color, pg.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
def draw_pieces(screen, board):
    """Draw the pieces on the board."""
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], pg.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
def main():
    """Main function to run the chess game."""
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    clock = pg.time.Clock()
    screen.fill(pg.Color("white"))
    load_images()
    gs = chess_engine.GameState()
    running = True
    while running:
        for e in pg.event.get():
            if e.type == pg.QUIT:
                running = False
        draw_game(screen, gs)
        clock.tick(MAX_FPS)
        pg.display.flip()
if __name__ == "__main__":
    main()
