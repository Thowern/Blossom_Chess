import pygame as p
from Blossom import Board, Move
from Blossom_Brain_08 import get_ai_move
from Score_board_tab import score_board

# Constants
BOARD_WIDTH = BOARD_HEIGHT = 480
DIMENSION = 8
SQ_SIZE = BOARD_HEIGHT // DIMENSION
MAX_FPS = 15
IMAGES = {}
SIDEBAR_WIDTH = int(BOARD_WIDTH / 10)
BORDER_WIDTH = int(BOARD_WIDTH / 100)

p.init()

def load_images():
    """Load the images for the chess pieces and resize them to the appropriate size."""
    pieces = ['wp', 'wR', 'wN', 'wB', 'wQ', 'wK', 'bp', 'bR', 'bN', 'bB', 'bQ', 'bK']
    for piece in pieces:
        try:
            image = p.image.load("imag/" + piece + ".png")
            resized_image = p.transform.scale(image, (SQ_SIZE, SQ_SIZE))
            IMAGES[piece] = resized_image
        except Exception as e:
            print(f"Errore caricando {piece}: {e}")


def preload_images():
    """Wait for all images to be loaded."""
    print("Caricamento immagini in corso...")
    while len(IMAGES) < 12:  # Attendi finché tutte le immagini non sono caricate
        p.time.wait(100)
    print("Immagini caricate.")


def show_start_screen(screen):
    """Show a start screen and wait for user interaction."""
    screen.fill((238, 230, 154))  # Sfondo
    font = p.font.SysFont(None, 48)
    text = font.render("Clicca per iniziare", True, (0, 0, 0))
    screen.blit(text, (BOARD_WIDTH // 4, BOARD_HEIGHT // 2))
    p.display.flip()

    # Aspetta l'interazione dell'utente
    waiting = True
    while waiting:
        for event in p.event.get():
            if event.type == p.MOUSEBUTTONDOWN:
                waiting = False
        p.time.wait(100)  # Evita di consumare troppe risorse


def main():
    global game_over
    screen = p.display.set_mode((BOARD_WIDTH + SIDEBAR_WIDTH + 2 * BORDER_WIDTH, BOARD_HEIGHT + 2 * BORDER_WIDTH))
    p.display.set_caption("Blossom Chess")
    clock = p.time.Clock()
    screen.fill(p.Color(238, 230, 154))

    # Mostra lo schermo iniziale per garantire l'interazione
    show_start_screen(screen)

    gs = Board()
    valid_moves = gs.get_legal_valid_moves()
    move_made = False
    animate_move_flag = False

    load_images()
    preload_images()

    running = True
    sq_selected = ()
    player_clicks = []
    game_over = False

    player_white = True
    player_black = False

    score = 0.5
    current_score = score

    while running:
        human_turn = (gs.white_to_move and player_white) or (not gs.white_to_move and player_black)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                if not game_over and human_turn:
                    location = p.mouse.get_pos()
                    col = (location[0] - BORDER_WIDTH) // SQ_SIZE
                    row = (location[1] - BORDER_WIDTH) // SQ_SIZE
                    if 0 <= col < DIMENSION and 0 <= row < DIMENSION:
                        if sq_selected == (row, col):
                            sq_selected = ()
                            player_clicks = []
                        else:
                            sq_selected = [row, col]
                            player_clicks.append(sq_selected)
                        if len(player_clicks) == 2:
                            move = [player_clicks[0], player_clicks[1]]
                            for i in range(len(valid_moves)):
                                if move == valid_moves[i]:
                                    gs.make_move(Move(player_clicks[0], player_clicks[1], gs.board))
                                    move_made = True
                                    animate_move_flag = True
                                    sq_selected = ()
                                    player_clicks = []
                                    break
                            if not move_made:
                                player_clicks = [sq_selected]

            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undo_move()
                    move_made = True
                    game_over = False

        current_score = animate_sidebar(screen, current_score, score)

        if not game_over and not human_turn:
            ai_move = get_ai_move(valid_moves, gs, Move)
            gs.make_move(Move(ai_move[0], ai_move[1], gs.board))
            move_made = True
            animate_move_flag = True

        if move_made:
            if animate_move_flag:
                if gs.move_log:
                    animate_move(gs.move_log[-1], screen, gs.board, clock, gs)

            valid_moves = gs.get_legal_valid_moves()
            score = score_board(gs)
            move_made = False

        draw_game_state(screen, gs, valid_moves, sq_selected)

        if gs.is_checkmate():
            game_over = True
            if gs.white_to_move:
                draw_endgame_text(screen, "Black wins")
            else:
                draw_endgame_text(screen, "White wins")

        elif gs.is_stalemate():
            game_over = True
            draw_endgame_text(screen, "Stalemate")

        elif gs.is_draw():
            game_over = True
            draw_endgame_text(screen, "Draw")

        clock.tick(MAX_FPS)
        p.display.flip()

def draw_game_state(screen, gs, valid_moves, sq_selected):
    draw_board(screen)
    highlight_last_move(screen, gs)
    highlight_valid_moves(screen, gs, valid_moves, sq_selected)
    draw_pieces(screen, gs.board)

def draw_board(screen):
    board_rect = p.Rect(BORDER_WIDTH, BORDER_WIDTH, BOARD_WIDTH, BOARD_HEIGHT)
    p.draw.rect(screen, p.Color("black"), board_rect, BORDER_WIDTH)  # Draw the border around the board
    colors = [p.Color('white'), p.Color(158,203,200)]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE + BORDER_WIDTH, r * SQ_SIZE + BORDER_WIDTH, SQ_SIZE, SQ_SIZE))


def highlight_valid_moves(screen, gs, valid_moves, sq_selected):
    s = p.Surface((SQ_SIZE, SQ_SIZE))
    if sq_selected:
        r, c = sq_selected
        piece = gs.board[r][c]

        rect_position = (c * SQ_SIZE + BORDER_WIDTH, r * SQ_SIZE + BORDER_WIDTH) 
        
        # Highlight selected square
        s.fill((179, 181, 227))
        screen.blit(s, rect_position)
        p.draw.rect(screen, p.Color('gray'), (rect_position[0], rect_position[1], SQ_SIZE, SQ_SIZE), 1)

        # Highlight possible moves
        s.fill((238, 230, 154))
        if (piece[0] == 'w' and gs.white_to_move) or (piece[0] == 'b' and not gs.white_to_move):
            for move in valid_moves:
                if move[0][0] == r and move[0][1] == c:
                    rect_position = (move[1][1] * SQ_SIZE + BORDER_WIDTH, move[1][0] * SQ_SIZE + BORDER_WIDTH)
                    screen.blit(s, rect_position)
                    p.draw.rect(screen, p.Color('gray'), (rect_position[0], rect_position[1], SQ_SIZE, SQ_SIZE), 1)

    s.fill(p.Color(240, 176, 64))
    if gs.in_check:
        rect_position = (gs.king_square[1] * SQ_SIZE + BORDER_WIDTH, gs.king_square[0] * SQ_SIZE + BORDER_WIDTH)
        screen.blit(s, rect_position)
        p.draw.rect(screen, p.Color('gray'), (rect_position[0], rect_position[1], SQ_SIZE, SQ_SIZE), 1)

def highlight_last_move(screen, gs):
    """Highlights the last move made on the board."""
    if len(gs.move_log) > 0:
        last_move = gs.move_log[-1]
        s = p.Surface((SQ_SIZE, SQ_SIZE))
        s.fill(p.Color(183, 230, 187))
        rect_position = (last_move.start_col * SQ_SIZE + BORDER_WIDTH, last_move.start_row * SQ_SIZE + BORDER_WIDTH)
        screen.blit(s, rect_position)
        p.draw.rect(screen, p.Color('gray'), (rect_position[0], rect_position[1], SQ_SIZE, SQ_SIZE), 1)

        rect_position = (last_move.end_col * SQ_SIZE + BORDER_WIDTH, last_move.end_row * SQ_SIZE + BORDER_WIDTH)
        screen.blit(s, rect_position)
        p.draw.rect(screen, p.Color('gray'), (rect_position[0], rect_position[1], SQ_SIZE, SQ_SIZE), 1)


def draw_pieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE + BORDER_WIDTH, r * SQ_SIZE + BORDER_WIDTH, SQ_SIZE, SQ_SIZE))

def draw_endgame_text(screen, text):
    font = p.font.SysFont("verdana", int(BOARD_WIDTH / 10), True, False)
    text_surface = font.render(text, True, p.Color(0, 46, 108))
    text_rect = p.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(
        BOARD_WIDTH // 2 - text_surface.get_width() // 2 + BORDER_WIDTH,
        BOARD_HEIGHT // 2 - text_surface.get_height() // 2 + BORDER_WIDTH
    )
    screen.blit(text_surface, text_rect)
    text_surface = font.render(text, True, p.Color(240, 176, 64))
    screen.blit(text_surface, text_rect.move(2, 2))

def animate_move(move, screen, board, clock, gs):
    """Animate a move on the board."""
    colors = [p.Color("white"), p.Color("gray")]
    delta_row = move.end_row - move.start_row
    delta_col = move.end_col - move.start_col
    frames_per_square = 5
    frame_count = (abs(delta_row) + abs(delta_col)) * frames_per_square

    for frame in range(frame_count + 1):
        r, c = (move.start_row + delta_row * frame / frame_count,
                move.start_col + delta_col * frame / frame_count)
        draw_board(screen)
        draw_pieces(screen, board)
        color = colors[(move.end_row + move.end_col) % 2]
        end_square = p.Rect(move.end_col * SQ_SIZE + BORDER_WIDTH, move.end_row * SQ_SIZE + BORDER_WIDTH, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, end_square)
        if move.pieceCaptured != '--':
            screen.blit(IMAGES[move.pieceCaptured], end_square)
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c * SQ_SIZE + BORDER_WIDTH, r * SQ_SIZE + BORDER_WIDTH, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)

def animate_sidebar(screen, current_score, target_score):
    """Animates the sidebar to gradually fill towards the target score."""
    step = 0.01
    if current_score < target_score:
        current_score = min(current_score + step, target_score)
    elif current_score > target_score:
        current_score = max(current_score - step, target_score)
    draw_sidebar(screen, current_score)
    return current_score

def draw_sidebar(screen, score):
    """Draws a sidebar that fills with white and black based on the score."""
    sidebar_rect = p.Rect(BOARD_WIDTH + 2 * BORDER_WIDTH, BORDER_WIDTH, SIDEBAR_WIDTH, BOARD_HEIGHT)
    p.draw.rect(screen, p.Color("gray"), sidebar_rect)

    white_height = int(score * BOARD_HEIGHT)
    black_height = BOARD_HEIGHT - white_height

    if white_height > 0:
        white_rect = p.Rect(BOARD_WIDTH + 2 * BORDER_WIDTH, BORDER_WIDTH, SIDEBAR_WIDTH, white_height)
        p.draw.rect(screen, p.Color("white"), white_rect)
    
    if black_height > 0:
        black_rect = p.Rect(BOARD_WIDTH + 2 * BORDER_WIDTH, BORDER_WIDTH + white_height, SIDEBAR_WIDTH, black_height)
        p.draw.rect(screen, p.Color(158,203,200), black_rect)

if __name__ == "__main__":
    main()
