import tkinter as tk
from PIL import Image, ImageTk
from Blossom import Board, Move
from Blossom_Brain_08 import get_ai_move
from Score_board_tab import score_board

# Inizializza Tkinter
root = tk.Tk()
root.title("Blossom Chess")

screen_height = root.winfo_screenheight()

# Costanti
BOARD_WIDTH = BOARD_HEIGHT = round(round(int(screen_height * 0.78)) / 8) * 8
DIMENSION = 8
SQ_SIZE = BOARD_HEIGHT // DIMENSION
IMAGES = {}
SIDEBAR_WIDTH = int(BOARD_WIDTH / 10)
BORDER_WIDTH = int(BOARD_WIDTH / 100)

# Crea il Canvas
canvas_width = int(BOARD_WIDTH + SIDEBAR_WIDTH + 2 * BORDER_WIDTH)
canvas_height = int(BOARD_HEIGHT + 2 * BORDER_WIDTH)
canvas = tk.Canvas(root, width=canvas_width, height=canvas_height)
canvas.pack()

def load_images():
    """Carica le immagini dei pezzi degli scacchi e le ridimensiona alla dimensione appropriata."""
    pieces = ['wp', 'wR', 'wN', 'wB', 'wQ', 'wK', 'bp', 'bR', 'bN', 'bB', 'bQ', 'bK']
    for piece in pieces:
        try:
            image = Image.open("imag/" + piece + ".png")
            resized_image = image.resize((SQ_SIZE, SQ_SIZE))
            IMAGES[piece] = ImageTk.PhotoImage(resized_image)
        except Exception as e:
            print(f"Errore caricando {piece}: {e}")

def show_start_screen():
    """Mostra una schermata iniziale e attende l'interazione dell'utente."""
    canvas.delete("all")
    canvas.create_rectangle(0, 0, canvas_width, canvas_height, fill="#EEE69A", outline="")
    canvas.update()

    def on_click(event):
        canvas.unbind("<Button-1>")
        main_game_loop()

    canvas.bind("<Button-1>", on_click)

def main_game_loop():
    global gs, valid_moves, move_made, animate_move_flag, sq_selected, player_clicks, game_over, player_white, player_black, score, current_score

    gs = Board()
    valid_moves = gs.get_legal_valid_moves()
    move_made = False
    animate_move_flag = False

    load_images()

    sq_selected = ()
    player_clicks = []
    game_over = False

    player_white = True
    player_black = True

    score = 0.5
    current_score = score

    draw_game_state(gs, valid_moves, sq_selected)
    animate_sidebar(current_score, score)

    # Associa gli eventi
    canvas.bind("<Button-1>", mouse_clicked)
    root.bind("<Key>", key_pressed)

    # Avvia il loop principale
    update()

def update():
    global gs, valid_moves, move_made, animate_move_flag, sq_selected, player_clicks, game_over, score, current_score

    human_turn = (gs.white_to_move and player_white) or (not gs.white_to_move and player_black)

    if not game_over and not human_turn:
        valid_moves = gs.get_legal_valid_moves()
        ai_move = get_ai_move(valid_moves, gs, Move)
        gs.make_move(Move(ai_move[0], ai_move[1], gs.board))
        move_made = True

    if move_made:
        valid_moves = gs.get_legal_valid_moves()
        score = score_board(gs)
        move_made = False

    draw_game_state(gs, valid_moves, sq_selected)
    current_score = animate_sidebar(current_score, score)

    if gs.is_checkmate():
        game_over = True
        if gs.white_to_move:
            draw_endgame_text("Black wins")
        else:
            draw_endgame_text("White wins")
    elif gs.is_stalemate():
        game_over = True
        draw_endgame_text("Stalemate")
    elif gs.is_draw():
        game_over = True
        draw_endgame_text("Draw")

    root.after(50, update)  # Aggiorna ogni 50ms (~20 FPS)

def mouse_clicked(event):
    global sq_selected, player_clicks, gs, valid_moves, move_made, animate_move_flag, game_over

    x = event.x - BORDER_WIDTH
    y = event.y - BORDER_WIDTH
    if 0 <= x < BOARD_WIDTH and 0 <= y < BOARD_HEIGHT:
        col = x // SQ_SIZE
        row = y // SQ_SIZE
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
                    sq_selected = ()
                    player_clicks = []
                    draw_game_state(gs, valid_moves, sq_selected)
                    break
            if not move_made:
                player_clicks = [sq_selected]

def key_pressed(event):
    global gs, move_made, game_over
    if event.keysym == 'z':
        gs.undo_move()
        move_made = True
        game_over = False

def draw_game_state(gs, valid_moves, sq_selected):
    canvas.delete("all")
    draw_board()
    highlight_last_move(gs)
    highlight_valid_moves(gs, valid_moves, sq_selected)
    draw_pieces(gs.board)
    draw_sidebar(current_score)

def draw_board():
    colors = ["white", "#9ECBC8"]  # Bianco e azzurro chiaro
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[(r + c) % 2]
            x1 = c * SQ_SIZE + BORDER_WIDTH
            y1 = r * SQ_SIZE + BORDER_WIDTH
            x2 = x1 + SQ_SIZE
            y2 = y1 + SQ_SIZE
            canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

def highlight_valid_moves(gs, valid_moves, sq_selected):
    if sq_selected:
        r, c = sq_selected
        piece = gs.board[r][c]

        x1 = c * SQ_SIZE + BORDER_WIDTH
        y1 = r * SQ_SIZE + BORDER_WIDTH
        x2 = x1 + SQ_SIZE
        y2 = y1 + SQ_SIZE

        # Evidenzia la casella selezionata
        canvas.create_rectangle(x1, y1, x2, y2, fill="#B3B5E3", outline="gray")

        if (piece[0] == 'w' and gs.white_to_move) or (piece[0] == 'b' and not gs.white_to_move):
            for move in valid_moves:
                if move[0][0] == r and move[0][1] == c:
                    end_r, end_c = move[1]
                    x1 = end_c * SQ_SIZE + BORDER_WIDTH
                    y1 = end_r * SQ_SIZE + BORDER_WIDTH
                    x2 = x1 + SQ_SIZE
                    y2 = y1 + SQ_SIZE
                    canvas.create_rectangle(x1, y1, x2, y2, fill="#EEE69A", outline="gray")

    # Evidenzia il re in scacco
    if gs.in_check:
        king_r, king_c = gs.king_square
        x1 = king_c * SQ_SIZE + BORDER_WIDTH
        y1 = king_r * SQ_SIZE + BORDER_WIDTH
        x2 = x1 + SQ_SIZE
        y2 = y1 + SQ_SIZE
        canvas.create_rectangle(x1, y1, x2, y2, fill="#F0B040", outline="gray")

def highlight_last_move(gs):
    if len(gs.move_log) > 0:
        last_move = gs.move_log[-1]
        squares = [(last_move.start_row, last_move.start_col), (last_move.end_row, last_move.end_col)]
        for r, c in squares:
            x1 = c * SQ_SIZE + BORDER_WIDTH
            y1 = r * SQ_SIZE + BORDER_WIDTH
            x2 = x1 + SQ_SIZE
            y2 = y1 + SQ_SIZE
            canvas.create_rectangle(x1, y1, x2, y2, fill="#B7E6BB", outline="gray")

def draw_pieces(board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                x = c * SQ_SIZE + BORDER_WIDTH
                y = r * SQ_SIZE + BORDER_WIDTH
                canvas.create_image(x, y, image=IMAGES[piece], anchor='nw')

def draw_endgame_text(text):
    canvas.create_text(BOARD_WIDTH // 2 + BORDER_WIDTH, BOARD_HEIGHT // 2 + BORDER_WIDTH, text=text, font=("Verdana", int(BOARD_WIDTH / 10), "bold"), fill="#F0B040")

def animate_sidebar(current_score, target_score):
    step = 0.01
    if current_score < target_score:
        current_score = min(current_score + step, target_score)
    elif current_score > target_score:
        current_score = max(current_score - step, target_score)
    draw_sidebar(current_score)
    return current_score

def draw_sidebar(score):
    x1 = BOARD_WIDTH + 2 * BORDER_WIDTH
    y1 = BORDER_WIDTH
    x2 = x1 + SIDEBAR_WIDTH
    y2 = y1 + BOARD_HEIGHT

    # Sfondo
    canvas.create_rectangle(x1, y1, x2, y2, fill="gray", outline="")

    white_height = int(score * BOARD_HEIGHT)
    black_height = BOARD_HEIGHT - white_height

    if white_height > 0:
        canvas.create_rectangle(x1, y1, x2, y1 + white_height, fill="white", outline="")
    if black_height > 0:
        canvas.create_rectangle(x1, y1 + white_height, x2, y2, fill="#9ECBC8", outline="")

# Avvia il gioco
show_start_screen()
root.mainloop()
