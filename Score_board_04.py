import numpy as np
from Blossom import Board

def score_board(gs):
    if gs.is_checkmate():
        return -float('inf') if gs.white_to_move else float('inf')
    
    if gs.is_stalemate() or gs.is_draw():
        return 0

    wp = np.sum(gs.wp_bitboard)
    bp = np.sum(gs.bp_bitboard)
    wN = np.sum(gs.wN_bitboard)
    bN = np.sum(gs.bN_bitboard)
    wB = np.sum(gs.wB_bitboard)
    bB = np.sum(gs.bB_bitboard)
    wR = np.sum(gs.wR_bitboard)
    bR = np.sum(gs.bR_bitboard)
    wQ = np.sum(gs.wQ_bitboard)
    bQ = np.sum(gs.bQ_bitboard)

    score = (
        100 * (wp - bp) +
        305 * (wN - bN) +
        333 * (wB - bB) +
        563 * (wR - bR) +
        950 * (wQ - bQ)
    )

    return score

print(score_board(Board()))