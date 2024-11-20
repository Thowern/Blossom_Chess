import numpy as np


converter = {7: 0, 6: 1, 5: 2, 4: 3, 3: 4, 2: 5, 1: 6, 0: 7}

class Board:
    def __init__(self):
        
        for piece in ['wp', 'wB', 'wN', 'wR', 'wQ', 'wK', 'bp', 'bB', 'bN', 'bR', 'bQ', 'bK']:
            setattr(self, f'{piece}_bitboard', np.zeros(64, dtype=bool))

        self.first_int_piece()

        self.board = np.array([
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
            ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']
        ])

        self.white_to_move = True
        self.in_check = False

        self.wK_moved = False
        self.wR_left_moved = False
        self.wR_right_moved = False
        self.wR_left_captured = False
        self.wR_right_captured = False
        self.bK_moved = False
        self.bR_left_moved = False
        self.bR_right_moved = False
        self.bR_left_captured = False
        self.bR_right_captured = False

        self.en_passant_square = None

        if self.white_to_move:
            row, col = divmod(np.flatnonzero(self.wK_bitboard)[0], 8)
        else:
            row, col = divmod(np.flatnonzero(self.bK_bitboard)[0], 8)

        row = converter[row]

        self.king_square = (row, col)

        self.update_squares_bitboards()

        self.move_log = []
        self.move_right_log = []
        self.board_log = [self.board.tobytes()]






    def first_int_piece(self):
        self.wp_bitboard[8:16] = 1

        self.wB_bitboard[2] = 1
        self.wB_bitboard[5] = 1
        self.wN_bitboard[1] = 1
        self.wN_bitboard[6] = 1
        self.wR_bitboard[0] = 1
        self.wR_bitboard[7] = 1
        self.wQ_bitboard[3] = 1
        self.wK_bitboard[4] = 1

        self.bp_bitboard[48:56] = 1

        self.bB_bitboard[58] = 1
        self.bB_bitboard[61] = 1
        self.bN_bitboard[57] = 1
        self.bN_bitboard[62] = 1
        self.bR_bitboard[56] = 1
        self.bR_bitboard[63] = 1
        self.bQ_bitboard[59] = 1
        self.bK_bitboard[60] = 1

    def int_pieces(self, move, do_move):
        start_row, start_col = move.startSq
        end_row, end_col = move.endSq
        trad_start = (converter[start_row] * 8) + start_col
        trad_end = (converter[end_row] * 8) + end_col
        trad_en_passant = (converter[start_row] * 8) + end_col

        piece_bitboards = {
            'wp': self.wp_bitboard,
            'wB': self.wB_bitboard,
            'wN': self.wN_bitboard,
            'wR': self.wR_bitboard,
            'wQ': self.wQ_bitboard,
            'wK': self.wK_bitboard,
            'bp': self.bp_bitboard,
            'bB': self.bB_bitboard,
            'bN': self.bN_bitboard,
            'bR': self.bR_bitboard,
            'bQ': self.bQ_bitboard,
            'bK': self.bK_bitboard
        }

        if do_move: 

            if move.pieceMoved in piece_bitboards:
                bitboard = piece_bitboards[move.pieceMoved]
                bitboard[trad_start] = 0
                bitboard[trad_end] = 1

            if move.pieceCaptured in piece_bitboards:
                bitboard = piece_bitboards[move.pieceCaptured]
                bitboard[trad_end] = 0

            if move.is_castle:
                if end_col - start_col == 2:
                    piece_bitboards[self.board[end_row][end_col - 1]][trad_end - 1] = 1
                    piece_bitboards[self.board[end_row][end_col - 1]][trad_end + 1] = 0
                else:
                    piece_bitboards[self.board[end_row][end_col + 1]][trad_end + 1] = 1
                    piece_bitboards[self.board[end_row][end_col + 1]][trad_end - 2] = 0


            if move.is_en_passant:
                pawn = 'bp' if self.white_to_move else 'wp'
                piece_bitboards[pawn][trad_en_passant] = 0
            
            if move.is_pawn_promotion:
                if move.pieceMoved == 'wp':
                    piece_bitboards['wQ'][trad_end] = 1
                else:
                    piece_bitboards['bQ'][trad_end] = 1
                piece_bitboards[move.pieceMoved][trad_end] = 0



        else:
            if move.pieceMoved in piece_bitboards:
                bitboard = piece_bitboards[move.pieceMoved]
                bitboard[trad_start] = 1
                bitboard[trad_end] = 0
            if move.pieceCaptured in piece_bitboards:
                bitboard = piece_bitboards[move.pieceCaptured]
                bitboard[trad_end] = 1
                
            if move.is_castle:
                if end_col - start_col == 2:
                    piece_bitboards[self.board[end_row][end_col + 1]][trad_end + 1] = 1
                    piece_bitboards[self.board[end_row][end_col + 1]][trad_end - 1] = 0
                else:
                    piece_bitboards[self.board[end_row][end_col - 2]][trad_end - 2] = 1
                    piece_bitboards[self.board[end_row][end_col - 2]][trad_end + 1] = 0


            if move.is_en_passant:
                pawn = 'wp' if self.white_to_move else 'bp'
                piece_bitboards[pawn][trad_en_passant] = 1

            if move.is_pawn_promotion:
                if move.pieceMoved == 'wp':
                    piece_bitboards['wQ'][trad_end] = 0
                else:
                    piece_bitboards['bQ'][trad_end] = 0

        
        if move.pieceMoved.endswith('p') and abs(start_row - end_row) == 2:
            self.en_passant_square = (trad_end - 8) if self.white_to_move else (trad_end + 8)
        else:
            self.en_passant_square = None

    def update_squares_bitboards(self):
        self.occupate_squares_by_white_bitboards = (
            self.wp_bitboard | self.wB_bitboard | self.wN_bitboard |
            self.wR_bitboard | self.wQ_bitboard | self.wK_bitboard
        )
        self.occupate_squares_by_black_bitboards = (
            self.bp_bitboard | self.bB_bitboard | self.bN_bitboard |
            self.bR_bitboard | self.bQ_bitboard | self.bK_bitboard
        )
        self.occupate_squares_bitboards = (
            self.occupate_squares_by_white_bitboards | self.occupate_squares_by_black_bitboards
        )

        self.square_attacked_by_the_enemy_bitboards = np.zeros(64, dtype=bool)
        self.att_by_p = np.zeros(64, dtype=bool)
        self.att_by_B = np.zeros(64, dtype=bool)
        self.att_by_N = np.zeros(64, dtype=bool)
        self.att_by_R = np.zeros(64, dtype=bool)
        self.att_by_Q = np.zeros(64, dtype=bool)
        self.att_by_K = np.zeros(64, dtype=bool)

        enemy_bitboards = {
        'p': self.bp_bitboard if self.white_to_move else self.wp_bitboard,
        'B': self.bB_bitboard if self.white_to_move else self.wB_bitboard,
        'N': self.bN_bitboard if self.white_to_move else self.wN_bitboard,
        'R': self.bR_bitboard if self.white_to_move else self.wR_bitboard,
        'Q': self.bQ_bitboard if self.white_to_move else self.wQ_bitboard,
        'K': self.bK_bitboard if self.white_to_move else self.wK_bitboard
        }

        for piece, bitboard in enemy_bitboards.items():
            for i in np.flatnonzero(bitboard):
                if piece == 'p':
                    self.att_by_p |= self.get_moves('bp' if self.white_to_move else 'wp', i, not self.white_to_move, True)
                elif piece == 'B':
                    self.att_by_B |= self.get_moves('bB' if self.white_to_move else 'wB', i, not self.white_to_move, True)
                elif piece == 'N':
                    self.att_by_N |= self.get_moves('bN' if self.white_to_move else 'wN', i, not self.white_to_move, True)
                elif piece == 'R':
                    self.att_by_R |= self.get_moves('bR' if self.white_to_move else 'wR', i, not self.white_to_move, True)
                elif piece == 'Q':
                    self.att_by_Q |= self.get_moves('bQ' if self.white_to_move else 'wQ', i, not self.white_to_move, True)
                elif piece == 'K':
                    self.att_by_K |= self.get_moves('bK' if self.white_to_move else 'wK', i, not self.white_to_move, True)

        self.square_attacked_by_the_enemy_bitboards = self.att_by_p | self.att_by_B | self.att_by_N | self.att_by_R | self.att_by_Q | self.att_by_K

        king_bitboard = self.wK_bitboard if self.white_to_move else self.bK_bitboard

        if np.flatnonzero(king_bitboard)[0] in np.flatnonzero(self.square_attacked_by_the_enemy_bitboards):
            self.in_check = True
        else:
            self.in_check = False         


        self.all_attacking_bitboards = {
            'p': self.att_by_p,
            'B': self.att_by_B,
            'N': self.att_by_N,
            'R': self.att_by_R,
            'Q': self.att_by_Q,
            'K': self.att_by_K
        }

        self.attackers = self.get_attackers()

        self.attackers_bitboard = np.zeros(64, dtype=bool)

        for attacker in self.attackers:
            self.attackers_bitboard[attacker[1]] = 1

        self.pinned_pieces = self.get_pinned_pieces()


    def make_move(self, move):
        self.move_log.append(move)
        self.move_right_log.append((self.wK_moved, self.wR_left_moved, self.wR_right_moved,
                              self.wR_left_captured, self.wR_right_captured, self.bK_moved,
                              self.bR_left_moved, self.bR_right_moved, self.bR_left_captured,
                              self.bR_right_captured))
        self.board_log.append(self.board.tobytes())

        self.update_board(move, True)
        self.update_castling_rights(move)
        self.handle_special_moves(move)
        self.int_pieces(move, True)

        move.en_passant_square = self.en_passant_square

        self.white_to_move = not self.white_to_move
        self.update_squares_bitboards()
        self.update_king_position()


    def undo_move(self):
        if not self.move_log:
            print("No moves to undo!")
            return

        move = self.move_log.pop()

        self.wK_moved, self.wR_left_moved, self.wR_right_moved, \
        self.wR_left_captured, self.wR_right_captured, self.bK_moved, \
        self.bR_left_moved, self.bR_right_moved, self.bR_left_captured, \
        self.bR_right_captured = self.move_right_log.pop()

        self.board_log.pop()

        self.update_board(move, False)
        self.handle_special_moves(move, undo=True)
        self.int_pieces(move, False)

        self.en_passant_square = self.move_log[-1].en_passant_square if self.move_log else None

        self.white_to_move = not self.white_to_move
        self.update_squares_bitboards()
        self.update_king_position()


    def update_board(self, move, do_move):
        
        start_row, start_col = move.startSq
        end_row, end_col = move.endSq
        piece_moved = move.pieceMoved
        piece_captured = move.pieceCaptured

        if do_move:
            self.board[start_row][start_col] = "--"
            self.board[end_row][end_col] = piece_moved
        else:
            self.board[start_row][start_col] = piece_moved
            self.board[end_row][end_col] = piece_captured

    def update_castling_rights(self, move):

        piece_moved = move.pieceMoved
        piece_captured = move.pieceCaptured
        start_row, start_col = move.startSq
        end_row, end_col = move.endSq

        if piece_moved == 'wK':
            self.wK_moved = True
        elif piece_moved == 'wR':
            if start_col == 0 and start_row == 7:
                self.wR_left_moved = True
            elif start_col == 7 and start_row == 7:
                self.wR_right_moved = True
        elif piece_moved == 'bK':
            self.bK_moved = True
        elif piece_moved == 'bR':
            if start_col == 0 and start_row == 0:
                self.bR_left_moved = True
            elif start_col == 7 and start_row == 0:
                self.bR_right_moved = True

        if piece_captured == 'wR':
            if end_col == 0 and end_row == 7:
                self.wR_left_captured = True
            elif end_col == 7 and end_row == 7:
                self.wR_right_captured = True
        elif piece_captured == 'bR':
            if end_col == 0 and end_row == 0:
                self.bR_left_captured = True
            elif end_col == 7 and end_row == 0:
                self.bR_right_captured = True
        

    def handle_special_moves(self, move, undo=False):

        start_row, start_col = move.startSq
        end_row, end_col = move.endSq
        piece_moved = move.pieceMoved

        if move.is_pawn_promotion:
            if not undo:
                self.board[end_row][end_col] = piece_moved[0] + 'Q'

        if move.is_en_passant:
            self.board[start_row][end_col] = '--' if not undo else ('wp' if self.white_to_move else 'bp')

        if move.is_castle:
            if end_col - start_col == 2:
                if not undo:
                    self.board[end_row][end_col - 1] = self.board[end_row][end_col + 1]
                    self.board[end_row][end_col + 1] = '--'
                else:
                    self.board[end_row][end_col + 1] = self.board[end_row][end_col - 1]
                    self.board[end_row][end_col - 1] = '--'
            else:
                if not undo:
                    self.board[end_row][end_col + 1] = self.board[end_row][end_col - 2]
                    self.board[end_row][end_col - 2] = '--'
                else:
                    self.board[end_row][end_col - 2] = self.board[end_row][end_col + 1]
                    self.board[end_row][end_col + 1] = '--'

    def update_king_position(self):

        if self.white_to_move:
            row, col = divmod(np.flatnonzero(self.wK_bitboard)[0], 8)
        else:
            row, col = divmod(np.flatnonzero(self.bK_bitboard)[0], 8)
        row = converter[row]
        self.king_square = (row, col)


    def filter_legal_moves(self, moves, position):

        if self.in_check:
            if len(self.attackers) == 1:
                possible_ends = self.attackers_bitboard | self.attackers[0][2]
                moves &= possible_ends
            else:
                moves = np.zeros(64, dtype=bool)

        for pinned in self.pinned_pieces:
            if position == pinned[0]:
                moves &= pinned[1]

        return moves

    def can_castle_kingside(self, white_turn):

        if white_turn:
            conditions = [
                not self.wK_moved,
                not self.wR_right_moved,
                not self.wR_right_captured,
                self.board[7][5] == '--',
                self.board[7][6] == '--',
                not self.is_square_attacked((7, 4)),
                not self.is_square_attacked((7, 5)),
                not self.is_square_attacked((7, 6))
            ]
        
        else:
            conditions = [
                not self.bK_moved,
                not self.bR_right_moved,
                not self.bR_right_captured,
                self.board[0][5] == '--',
                self.board[0][6] == '--',
                not self.is_square_attacked((0, 4)),
                not self.is_square_attacked((0, 5)),
                not self.is_square_attacked((0, 6))
            ]

        return all(conditions)

    def can_castle_queenside(self, white_turn):

        if white_turn:
            conditions = [
                not self.wK_moved,
                not self.wR_left_moved,
                not self.wR_left_captured,
                self.board[7][1] == '--',
                self.board[7][2] == '--',
                self.board[7][3] == '--',
                not self.is_square_attacked((7, 4)),
                not self.is_square_attacked((7, 3)),
                not self.is_square_attacked((7, 2))
            ]
        
        else:
            conditions = [
                not self.bK_moved,
                not self.bR_left_moved,
                not self.bR_left_captured,
                self.board[0][1] == '--',
                self.board[0][2] == '--',
                self.board[0][3] == '--',
                not self.is_square_attacked((0, 4)),
                not self.is_square_attacked((0, 3)),
                not self.is_square_attacked((0, 2))
            ]
        
        return all(conditions)
        
    def is_square_attacked(self, square):
        row, col = square
        pos = converter[row] * 8 + col
        attackers = self.square_attacked_by_the_enemy_bitboards
        return attackers[pos] == 1

    def get_moves(self, piece_type, position, white_turn, attack_only=False):      
        if piece_type.endswith('p'):
            return self.get_pawn_moves(position, white_turn, attack_only)
        elif piece_type.endswith('N'):
            return self.get_knight_moves(position, white_turn, attack_only)
        elif piece_type.endswith('B') or piece_type.endswith('R') or piece_type.endswith('Q'):
            return self.get_linear_moves(piece_type, position, white_turn, attack_only)
        elif piece_type.endswith('K'):
            return self.get_king_moves(position, white_turn, attack_only)
            
        else:
            raise ValueError(f"Unknown piece type: {piece_type}")

    def get_pawn_moves(self, position, white_turn, attack_only=False):
        assert position is not None

        def add_move(moves, pos):
            if 0 <= pos < 64:
                moves[pos] = 1

        def pawn_movement_logic(position, forward_step, double_step_start, double_step_pos, attack_directions):
            moves = np.zeros(64, dtype=bool)
            if not attack_only and self.occupate_squares_bitboards[position + forward_step] == 0:
                add_move(moves, position + forward_step)
                if position in double_step_start and self.occupate_squares_bitboards[position + double_step_pos] == 0:
                    add_move(moves, position + double_step_pos)

            for direction in attack_directions:
                attack_pos = position + direction
                if (direction == 7 and position % 8 != 0) or (direction == 9 and position % 8 != 7) or \
                (direction == -7 and position % 8 != 7) or (direction == -9 and position % 8 != 0):
                    if attack_pos < 64 and attack_pos >= 0:
                        if attack_pos == self.en_passant_square:
                            if attack_only:
                                add_move(moves, attack_pos)
                            else:
                                if not self.is_in_check_after_en_passant(position, attack_pos, white_turn):
                                    add_move(moves, attack_pos)
                        elif occupied_squares_by_enemies[attack_pos] == 1:
                            add_move(moves, attack_pos)
                        if attack_only:
                            add_move(moves, attack_pos)

            if attack_only:
                return moves
            else:
                return self.filter_legal_moves(moves, position)

        occupied_squares_by_enemies = (
            self.occupate_squares_by_black_bitboards
            if white_turn
            else self.occupate_squares_by_white_bitboards
        )

        if white_turn:
            return pawn_movement_logic(position, 8, range(8, 16), 16, [7, 9])
        else:
            return pawn_movement_logic(position, -8, range(48, 56), -16, [-7, -9])

    def is_in_check_after_en_passant(self, start_pos, end_pos, white_turn):
        captured_pawn_pos = end_pos - 8 if white_turn else end_pos + 8

        piece_bitboard = self.wp_bitboard if white_turn else self.bp_bitboard
        enemy_bitboard = self.bp_bitboard if white_turn else self.wp_bitboard

        piece_bitboard[start_pos] = 0
        piece_bitboard[end_pos] = 1
        enemy_bitboard[captured_pawn_pos] = 0

        self.update_squares_bitboards()

        in_check = self.is_in_check(white_turn)

        piece_bitboard[start_pos] = 1
        piece_bitboard[end_pos] = 0
        enemy_bitboard[captured_pawn_pos] = 1

        self.update_squares_bitboards()

        return in_check

    def is_in_check(self, white_turn):
        king_pos = np.flatnonzero(self.wK_bitboard)[0] if white_turn else np.flatnonzero(self.bK_bitboard)[0]
        attacked_positions = self.square_attacked_by_the_enemy_bitboards
        return attacked_positions[king_pos] == 1


    def get_knight_moves(self, position, white_turn, attack_only=False):
        moves = np.zeros(64, dtype=bool)
        occupied_squares_by_allies = self.occupate_squares_by_white_bitboards if white_turn else self.occupate_squares_by_black_bitboards

        knight_moves = [
            (6, lambda p: p % 8 > 1 and p + 6 < 64),
            (-10, lambda p: p % 8 > 1 and p - 10 >= 0),
            (15, lambda p: p % 8 > 0 and p + 15 < 64),
            (-17, lambda p: p % 8 > 0 and p - 17 >= 0),
            (10, lambda p: p % 8 < 6 and p + 10 < 64),
            (-6, lambda p: p % 8 < 6 and p - 6 >= 0),
            (17, lambda p: p % 8 < 7 and p + 17 < 64),
            (-15, lambda p: p % 8 < 7 and p - 15 >= 0),
        ]

        for shift, condition in knight_moves:
            if condition(position) and occupied_squares_by_allies[position + shift] == 0:
                moves[position + shift] = 1
            
        if attack_only:
            return moves
        else:
            return self.filter_legal_moves(moves, position)
    
    def get_linear_moves(self, piece_type, position, white_turn, attack_only=False):
        moves = np.zeros(64, dtype=bool)
        allies = self.occupate_squares_by_white_bitboards if white_turn else self.occupate_squares_by_black_bitboards
        enemies = self.occupate_squares_by_black_bitboards if white_turn else self.occupate_squares_by_white_bitboards
        enemy_king = self.bK_bitboard if white_turn else self.wK_bitboard

        if piece_type.endswith('B'):
            directions = [9, 7, -9, -7]
        elif piece_type.endswith('R'):
            directions = [8, -8, 1, -1]
        elif piece_type.endswith('Q'):
            directions = [9, 7, -9, -7, 8, -8, 1, -1]

        for shift in directions:
            for i in range(1, 8):
                target_position = position + shift * i

                if target_position < 0 or target_position >= 64:
                    break
                if (position % 8 == 0 and shift in (7, -9, -1)) or (position % 8 == 7 and shift in (9, -7, 1)):
                    break
                if allies[target_position]:
                    break
                moves[target_position] = 1
                if attack_only and enemy_king[target_position]:
                    continue
                if enemies[target_position]:
                    break
                if (target_position % 8 == 0 and shift in (7, -9, -1)) or (target_position % 8 == 7 and shift in (9, -7, 1)):
                    break
        if attack_only:
            return moves
        else:
            return self.filter_legal_moves(moves, position)

    KING_MOVES = np.array([9, 8, 7, 1, -1, -7, -8, -9])
    def get_king_moves(self, position, white_turn, attack_only):
        moves = np.zeros(64, dtype=bool)
        allies = self.occupate_squares_by_white_bitboards if white_turn else self.occupate_squares_by_black_bitboards
        enemies = self.occupate_squares_by_black_bitboards if white_turn else self.occupate_squares_by_white_bitboards


        for shift in self.KING_MOVES:
            if (position % 8 == 0 and shift in (7, -9, -1)) or (position % 8 == 7 and shift in (9, -7, 1)):
                continue
            target_position = position + shift
            if target_position < 0 or target_position >= 64:
                continue
            if allies[target_position]:
                continue
            if not attack_only:
                if self.square_attacked_by_the_enemy_bitboards[target_position] == 1 or (enemies[target_position] and self.is_protected(target_position)):
                    continue
            moves[target_position] = 1

        if self.can_castle_kingside(white_turn):
            moves[position + 2] = 1
        if self.can_castle_queenside(white_turn):
            moves[position - 2] = 1

        return moves
    
    def is_protected(self, position):
        original_piece = self.board[converter[position // 8]][position % 8]
        piece_bitboard = getattr(self, f"{original_piece}_bitboard", None)

        if piece_bitboard is not None:
            piece_bitboard[position] = 0

        self.update_squares_bitboards()

        is_attacked = self.square_attacked_by_the_enemy_bitboards[position] == 1


        if piece_bitboard is not None:
            piece_bitboard[position] = 1

        self.update_squares_bitboards()

        return is_attacked
    
    def get_attackers(self):
        attackers = []
        king_position = np.flatnonzero(self.wK_bitboard if self.white_to_move else self.bK_bitboard)[0]

        enemy_piece_bitboards = {
            'p': self.bp_bitboard,
            'N': self.bN_bitboard,
            'B': self.bB_bitboard,
            'R': self.bR_bitboard,
            'Q': self.bQ_bitboard,
        } if self.white_to_move else {
            'N': self.wN_bitboard,
            'B': self.wB_bitboard,
            'R': self.wR_bitboard,
            'Q': self.wQ_bitboard,
            'p': self.wp_bitboard,
        }

        directions = {
            'B': [9, 7, -9, -7],
            'R': [8, -8, 1, -1],
            'Q': [9, 7, -9, -7, 8, -8, 1, -1]
        }

        for piece_type, bitboard in enemy_piece_bitboards.items():
            piece_positions = np.flatnonzero(bitboard)
            for position in piece_positions:
                moves = self.get_moves(piece_type, position, not self.white_to_move, True)
                if moves[king_position] == 1:
                    path_bitboard = np.zeros(64, dtype=bool)
                    if piece_type in ['B', 'R', 'Q']:
                        direction = self.get_direction(position, king_position, directions[piece_type])
                        if direction is not None:
                            path_bitboard = self.get_path_between(position, king_position, direction)
                    attackers.append((piece_type, position, path_bitboard))

        return attackers
    
    def get_pinned_pieces(self):
        pinned_pieces = []
        king_position = np.flatnonzero(self.wK_bitboard if self.white_to_move else self.bK_bitboard)[0]
        occupied_squares_by_allies = self.occupate_squares_by_white_bitboards if self.white_to_move else self.occupate_squares_by_black_bitboards
        occupied_squares_by_enemy = self.occupate_squares_by_black_bitboards if self.white_to_move else self.occupate_squares_by_white_bitboards
        directions = [9, 7, -9, -7, 8, -8, 1, -1]

        for direction in directions:
            potential_pin = None
            potential_pinners = ('wB', 'bB', 'wQ', 'bQ') if (direction in (9, 7, -9, -7)) else ('wR', 'bR', 'wQ', 'bQ')
            for i in range(1, 8):
                target_position = king_position + direction * i
                if target_position < 0 or target_position >= 64:
                    break
                if (king_position % 8 == 0 and direction in (7, -9, -1)) or (king_position % 8 == 7 and direction in (9, -7, 1)):
                    break
                if occupied_squares_by_enemy[target_position]:
                    if potential_pin == None:
                        break
                    else:
                        if self.board[converter[target_position // 8]][target_position % 8] in potential_pinners:
                            path_bitboard = np.zeros(64, dtype=bool)
                            path_bitboard = self.get_path_between(king_position, target_position, direction)
                            path_bitboard[target_position] = 1
                            pinned_pieces.append((potential_pin, path_bitboard))
                            break
                        else:
                            break
                if occupied_squares_by_allies[target_position]:
                    if potential_pin == None:
                        potential_pin = target_position
                    else:
                        break
                if (target_position % 8 == 0 and direction in (7, -9, -1)) or (target_position % 8 == 7 and direction in (9, -7, 1)):
                    break
        return pinned_pieces

    def get_direction(self, start, end, directions):
        for direction in directions:
            for i in range(1, 8):
                if start + direction * i == end:
                    return direction
                if not (0 <= start + direction * i < 64):
                    break
                if (start % 8 == 0 and direction in [7, -9, -1]) or (start % 8 == 7 and direction in [9, -7, 1]):
                    break
        return None

    def get_path_between(self, start, end, direction):
        path_bitboard = np.zeros(64, dtype=bool)
        for i in range(1, 8):
            square = start + direction * i

            if square == end:
                break
            path_bitboard[square] = 1
        return path_bitboard



    def get_all_piece_moves(self, moves, bitboard, get_moves_fn, white_turn):
        pieces = np.flatnonzero(bitboard)
        moves_bitboards = np.array([get_moves_fn(piece, white_turn) for piece in pieces])

        index = 0
        for piece, moves_bitboard in zip(pieces, moves_bitboards):
            start_row, start_col = divmod(piece, 8)
            start_row = converter[start_row]
            for move in np.flatnonzero(moves_bitboard):
                end_row, end_col = divmod(move, 8)
                end_row = converter[end_row]
                moves[index] = ((start_row, start_col), (end_row, end_col))
                index += 1

        return index

    def get_legal_valid_moves(self):
        max_moves = 218
        moves = np.empty((max_moves, 2, 2), dtype=int)
        white_turn = self.white_to_move

        piece_bitboards = {
            'p': self.wp_bitboard if white_turn else self.bp_bitboard,
            'N': self.wN_bitboard if white_turn else self.bN_bitboard,
            'B': self.wB_bitboard if white_turn else self.bB_bitboard,
            'R': self.wR_bitboard if white_turn else self.bR_bitboard,
            'Q': self.wQ_bitboard if white_turn else self.bQ_bitboard,
            'K': self.wK_bitboard if white_turn else self.bK_bitboard
        }

        index = 0
        for piece_type, bitboard in piece_bitboards.items():
            index += self.get_all_piece_moves(moves[index:], bitboard, lambda pos, wt: self.get_moves(piece_type, pos, wt), white_turn)

        moves = moves[:index]
            
        return moves.tolist()
    
    def is_checkmate(self):
        if len(self.get_legal_valid_moves()) == 0 and self.in_check:
            return True
        else: 
            return False

    def is_stalemate(self):
        if len(self.get_legal_valid_moves()) == 0 and not self.in_check:
            return True
        else:
            return False

    def has_three_equal_elements(self, lst):
        element_count = {}

        for element in lst:
            
            if element in element_count:
                element_count[element] += 1
                if element_count[element] == 3:
                    return True
            else:
                element_count[element] = 1

        return False

        
    def is_draw(self):
        num_occupied = np.count_nonzero(self.occupate_squares_bitboards)
        if num_occupied == 2:
            return True
        elif num_occupied == 3 and np.logical_or.reduce([np.any(self.wN_bitboard), np.any(self.bN_bitboard), np.any(self.wB_bitboard), np.any(self.bB_bitboard)]):
            return True
        elif num_occupied == 4 and (np.count_nonzero(self.wN_bitboard) == 2 or np.count_nonzero(self.bN_bitboard) == 2):
            return True
        if self.has_three_equal_elements(self.board_log):
            return True
        else:
            return False

class Move:
    def __init__(self, startSq, endSq, board, en_passant_square = None):
        self.startSq = startSq
        self.endSq = endSq
        self.start_row , self.start_col = startSq
        self.end_row , self.end_col = endSq
        self.pieceMoved = board[startSq[0]][startSq[1]]
        self.pieceCaptured = board[endSq[0]][endSq[1]]
        self.is_pawn_promotion = False
        self.is_en_passant = False
        self.is_castle = False
        self.en_passant_square = en_passant_square

        if self.pieceMoved.endswith('K') and abs(self.start_col - self.end_col) == 2:
            self.is_castle = True
        if self.pieceMoved.endswith('p') and self.pieceCaptured == '--' and self.start_col != self.end_col:
            self.is_en_passant = True
        if (self.pieceMoved == 'wp' and self.end_row == 0) or (self.pieceMoved == 'bp' and self.end_row == 7):
            self.is_pawn_promotion = True