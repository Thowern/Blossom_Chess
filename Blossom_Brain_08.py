

MAX_DEPTH = 8
TIME_LIMIT = 0.5













piece_score = {
    'p': 100,
    'N': 288,
    'B': 345,
    'R': 480,
    'Q': 1077,
    'K': 30
}

from Score_board_02 import score_board
import random

INITIAL_SX = 12

def order_moves(moves, gs, Move):
    def move_value(move):
        value = 0
        capturing_piece = gs.board[move[0][0]][move[0][1]]
        captured_piece = gs.board[move[1][0]][move[1][1]]
        if captured_piece != '--':
            value += piece_score[captured_piece[1]] / piece_score[capturing_piece[1]]
        if (capturing_piece == 'wp' and move[1][0] == 0) or (capturing_piece == 'bp' and move[1][0] == 7):
            value += 20
        if check_controll(move, gs, Move):
            value += 5
        return value

    moves.sort(key=move_value, reverse=True)
    return moves

def check_controll(move, gs, Move):
    gs.make_move(Move(move[0], move[1], gs.board))
    controll = gs.in_check
    gs.undo_move()
    return controll




def get_ai_move(valid_moves, gs, Move):
    random.shuffle(valid_moves)
    valid_moves = order_moves(valid_moves, gs, Move)
    return iterative_deepening(valid_moves, gs, Move)

import time

def iterative_deepening(valid_moves, gs, Move):
    global best_move, DEPTH
    best_move = None
    start_time = time.time()
    DEPTH = 1

    while DEPTH <= MAX_DEPTH:
        if time.time() - start_time >= TIME_LIMIT:
            break

        get_best_move(valid_moves, gs, Move, DEPTH, gs.white_to_move, float('-inf'), float('inf'), INITIAL_SX)

        current_best_move = best_move

        if time.time() - start_time < TIME_LIMIT:
            best_move = current_best_move

        print(f"Best move at depth {DEPTH}: {best_move} - time: {time.time() - start_time}")

        DEPTH += 1

    print(f"Time taken: {time.time() - start_time} seconds")
    return best_move








def get_best_move(valid_moves, gs, Move, depth, white_turn, alpha, beta, sx):
    global best_move, DEPTH
    if sx <= 0 or depth == 0:
        return quiescence_search(gs, Move, alpha, beta, white_turn, sx)

    if white_turn:
        max_score = float('-inf')
        for index, move in enumerate(valid_moves):
            gs.make_move(Move(move[0], move[1], gs.board))
            next_moves = gs.get_legal_valid_moves()

            move_sxdec = calculate_sxdec(move, gs, Move)
            new_depth = depth - 1

            if index >= 4 and depth > 2:
                new_depth -= 1  # Late Move Reduction

            score = get_best_move(next_moves, gs, Move, new_depth, False, alpha, beta, sx - move_sxdec)
            gs.undo_move()

            if score > max_score:
                max_score = score
                if depth == DEPTH:
                    best_move = move
            alpha = max(alpha, score)
            if beta <= alpha:
                break
        return max_score
    else:
        min_score = float('inf')
        for index, move in enumerate(valid_moves):
            gs.make_move(Move(move[0], move[1], gs.board))
            next_moves = gs.get_legal_valid_moves()

            move_sxdec = calculate_sxdec(move, gs, Move)
            new_depth = depth - 1

            if index >= 5 and depth > 2:
                new_depth -= 1  # Late Move Reduction

            score = get_best_move(next_moves, gs, Move, new_depth, True, alpha, beta, sx - move_sxdec)
            gs.undo_move()

            if score < min_score:
                min_score = score
                if depth == DEPTH:
                    best_move = move
            beta = min(beta, score)
            if beta <= alpha:
                break
        return min_score

def calculate_sxdec(move, gs, Move):
    capturing_piece = gs.board[move[0][0]][move[0][1]]
    captured_piece = gs.board[move[1][0]][move[1][1]]

    if captured_piece != '-':
        return 3
    if (capturing_piece == 'wp' and move[1][0] == 0) or (capturing_piece == 'bp' and move[1][0] == 7):
        return 4
    if check_controll(move, gs, Move):
        return 2
    else:
        return 1

def quiescence_search(gs, Move, alpha, beta, white_turn, sx):
    stand_pat = score_board(gs)

    if white_turn:
        if stand_pat >= beta:
            return beta
        if alpha < stand_pat:
            alpha = stand_pat

        legal_moves = gs.get_legal_valid_moves()
        capturing_moves = [move for move in legal_moves if gs.board[move[1][0]][move[1][1]][1] != '-']
        capturing_moves = order_moves(capturing_moves, gs, Move)

        for move in capturing_moves:
            gs.make_move(Move(move[0], move[1], gs.board))
            score = quiescence_search(gs, Move, alpha, beta, not white_turn, sx - 1)
            gs.undo_move()

            if score >= beta:
                return beta
            if score > alpha:
                alpha = score
        return alpha

    else:
        if stand_pat <= alpha:
            return alpha
        if beta > stand_pat:
            beta = stand_pat

        legal_moves = gs.get_legal_valid_moves()
        capturing_moves = [move for move in legal_moves if gs.board[move[1][0]][move[1][1]][1] != '-']
        capturing_moves = order_moves(capturing_moves, gs, Move)

        for move in capturing_moves:
            gs.make_move(Move(move[0], move[1], gs.board))
            score = quiescence_search(gs, Move, alpha, beta, not white_turn, sx - 1)
            gs.undo_move()

            if score <= alpha:
                return alpha
            if score < beta:
                beta = score
        return beta