import pygame as pg
import os
class GameState : 
    def __init__(self) -> None:
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        ]
        self.white_to_move = True
        self.move_log = []
        self.move_funtions = {
            "p": self.getPawnMoves,
            "R": self.getRookMoves,
            "N": self.getKnightMoves,
            "B": self.getBishopMoves,
            "Q": self.getQueenMoves,
            "K": self.getKingMoves
        }
        self.white_king_location = (7, 4)
        self.black_king_location = (0, 4)
        self.stale_mate = False
        self.check_mate = False
        self.pins = []
        self.checks = []
        self.in_check = False
        self.espassant_possible = ()
        self.current_castle_rights = CastleRights(True, True, True, True)
        self.castle_rights_log = [CastleRights(self.current_castle_rights.wks, self.current_castle_rights.bks, self.current_castle_rights.wqs, self.current_castle_rights.bqs)]
    def makeMove(self,move) : 
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move)
        # update king location
        if move.piece_moved == "wK":
            self.white_king_location = (move.end_row, move.end_col)
        elif move.piece_moved == "bK":
            self.black_king_location = (move.end_row, move.end_col)
        # check for pawn promotion
        if move.isPawnPromotion:
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + "Q"
        #print(print(move.start_row, move.start_col, move.end_row, move.end_col,move.piece_moved, move.piece_captured, move.ispassant))
        if move.ispassant:
                self.board[move.start_row][move.end_col] = "--"
        if move.piece_moved[1] == "p" and abs(move.start_row - move.end_row) == 2:
            self.espassant_possible = ((move.start_row + move.end_row)//2, move.end_col)
        else: 
            self.espassant_possible = ()
        print(move.isCastleMoved)
        if move.isCastleMoved:
            if move.end_col - move.start_col == 2: # king side castle
                self.board[move.start_row][move.end_col - 1] = move.piece_moved[0] + "R"
                self.board[move.start_row][move.end_col + 1] = "--"
            else: # queen side castle
                self.board[move.start_row][move.end_col + 1] = move.piece_moved[0] + "R"
                self.board[move.start_row][move.end_col - 2] = "--"
        self.updateCatleRights(move)
        self.white_to_move = not self.white_to_move
    def updateCatleRights(self,move) :
        if move.piece_moved == "wK":
            self.current_castle_rights.wks = False
            self.current_castle_rights.wqs = False
        elif move.piece_moved == "bK":
            self.current_castle_rights.bks = False
            self.current_castle_rights.bqs = False
        elif move.piece_moved == "wR":
            if move.start_row == 7 and move.start_col == 0:
                self.current_castle_rights.wqs = False
            elif move.start_row == 7 and move.start_col == 7:
                self.current_castle_rights.wks = False
        elif move.piece_moved == "bR":
            if move.start_row == 0 and move.start_col == 0:
                self.current_castle_rights.bqs = False
            elif move.start_row == 0 and move.start_col == 7:
                self.current_castle_rights.bks = False
        self.castle_rights_log.append(CastleRights(self.current_castle_rights.wks, self.current_castle_rights.bks, 
                                                   self.current_castle_rights.wqs, self.current_castle_rights.bqs))

    def undoMove(self) : 
        """Undo the last move made."""
        if len(self.move_log) == 0 : return
        if len(self.move_log) != 0:
            move = self.move_log.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            self.white_to_move = not self.white_to_move
        if move.piece_moved == "wK":    
            self.white_king_location = (move.start_row, move.start_col)
        elif move.piece_moved == "bK":
            self.black_king_location = (move.start_row, move.start_col)
        if move.piece_moved[1] == "p" and abs(move.start_row - move.end_row) == 2:
            self.board[move.end_row][move.end_col] = "--"
            self.espassant_possible = ()
        if move.ispassant:
            self.board[move.end_row][move.end_col] = "--"
            self.board[move.start_row][move.end_col] = move.piece_captured
            self.espassant_possible = (move.end_row, move.end_col)
        self.castle_rights_log.pop()
        self.current_castle_rights = self.castle_rights_log[-1]
        if move.isCastleMoved :
            if move.end_col - move.start_col == 2:
                self.board[move.start_row][move.end_col + 1] = self.board[move.start_row][move.end_col - 1] 
                self.board[move.start_row][move.end_col - 1] = "--"
            else:
                self.board[move.start_row][move.end_col - 2] = self.board[move.start_row][move.end_col + 1]
                self.board[move.start_row][move.end_col + 1] = "--"
    def getAllPossibleMoves(self) :
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                piece = self.board[r][c]
                if piece != "--":
                    if (piece[0] == "w" and self.white_to_move) or (piece[0] == "b" and not self.white_to_move):
                         self.move_funtions[piece[1]](r, c, moves)             
        return moves
    def getValidMoves(self) :
        moves = []
        tempEnpassant = self.espassant_possible
        tempCastleRights = CastleRights(self.current_castle_rights.wks, self.current_castle_rights.bks, self.current_castle_rights.wqs, self.current_castle_rights.bqs)
        for move in moves : 
            print(f"move : {move.start_row} {move.start_col} {move.end_row} {move.end_col} {move.piece_moved} {move.piece_captured} {move.isCastleMoved} {move.ispassant}")
        self.in_check ,self.pins, self.checks = self.checkForPinsAndChecks()
        color = "w" if self.white_to_move else "b"
        #print(self.in_check,color)
        if self.white_to_move:
            king_row, king_col = self.white_king_location
        else:
            king_row, king_col = self.black_king_location
        if self.in_check:
            if len(self.checks) == 1: # only one check , block check or move king
                moves = self.getAllPossibleMoves()
                #to block check, must move a piece into one of the squares between king and checking piece
                check = self.checks[0] #check infomation
                check_row, check_col = check[0], check[1]
                piece_checking = self.board[check_row][check_col] # enemy piece causing check
                valid_squares = [] # squares that piece can move to
                #if knight, must capture knight or move king, others pieces can be blocked
                if piece_checking[1] == "N":
                    valid_squares.append((check_row, check_col))
                else:
                    for i in range(1, 8):
                        valid_square = (king_row + check[2] * i, king_col  + check[3] * i) # check2 and check3 are the check direction
                        valid_squares.append(valid_square)
                        if valid_square[0] == check_row and valid_square[1] == check_col: # once you reach the checking piece, stop
                            break
                # get rid of any moves that don't block check or move king
                for i in range(len(moves)-1, -1, -1):
                    if moves[i].piece_moved[1] == "K":
                        if moves[i].end_row == king_row and moves[i].end_col == king_col:
                            moves.remove(moves[i])
            else : # double check, must move king
                self.getKingMoves(king_row, king_col, moves)
        else : 
            moves = self.getAllPossibleMoves()
        self.getCastleMoves(king_row, king_col, moves)
        self.espassant_possible = tempEnpassant
        self.current_castle_rights = tempCastleRights
        return moves
    def checkForPinsAndChecks(self):
        pins = []
        checks = []
        in_check = False
        if self.white_to_move:
            enemy_color = "b"
            ally_color = "w"
            start_row = self.white_king_location[0]
            start_col = self.white_king_location[1]
        else:
            enemy_color = "w"
            ally_color = "b"
            start_row = self.black_king_location[0]
            start_col = self.black_king_location[1]
        #print(start_row, start_col)
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
        for j in range(len(directions)):
            d = directions[j]
            #print(d)
            possible_pin = ()
            for i in range(1, 8):
                end_row = start_row + d[0] * i
                end_col = start_col + d[1] * i
                
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                   # print(start_row, start_col, end_row, end_col,end_piece)
                    if end_piece == "--": # empty square
                        continue
                    if end_piece[0] == ally_color and end_piece[1] != "K": # allied piece
                        if possible_pin == (): # 1st allied piece could be pinned
                            possible_pin = (end_row, end_col, d[0], d[1])
                        else: # 2nd allied piece, so no pin or check possible in this direction
                            break
                    # 5 possibility here in this complex conditinal
                    # 1. orthogonally alway from king and piece is rook
                    # 2. diagonally away from king and piece is bishop
                    # 3. 1 square away diagonally from king and piece is a pawn
                    # 4. any direction and piece is queen
                    # 5. any direction 1 square away and piece is king(this is neccessary  to prevent a king move to square controlled by another king)
                    elif end_piece[0] == enemy_color: # enemy piece
                        type = end_piece[1]
                        #print(end_piece)
                        if (0 <= j <= 3 and type == "R") or\
                            (4 <= j <= 7 and type == "B") or\
                                (i == 1 and type == 'p') and ((enemy_color == "w" and 4 <= j <= 55) or (enemy_color == "b" and 6 <= j <= 77)) or\
                                (type == "Q") or\
                                (i == 2 and type == "K"):
                            if possible_pin == ():
                                in_check = True
                                checks.append((end_row, end_col, d[0], d[1]))
                            else: # allied piece is blocking,so pin
                                pins.append(possible_pin)

        #print(checks)
        #check for knight checks
        knight_moves = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]
        for m in knight_moves:
            end_row = start_row + m[0]
            end_col = start_col + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] == enemy_color and end_piece[1] == "N": # enemy knight attack king
                    in_check = True
                    checks.append((end_row, end_col, m[0], m[1]))
        return in_check, pins, checks
                    
    def in_check(self) :
        if self.white_to_move:
            return self.square_under_attack(self.white_king_location[0], self.white_king_location[1])
        else:
            return self.square_under_attack(self.black_king_location[0], self.black_king_location[1])
    def square_under_attack(self, r, c):
        self.white_to_move = not self.white_to_move
        # Check for pawns
        opponet_Moves = self.getAllPossibleMoves()
        self.white_to_move = not self.white_to_move
        for move in opponet_Moves:
            if move.end_row == r and move.end_col == c:
                return True
        return False

    def getPawnMoves(self, r, c, moves):
        pinsDirection = ()
        piecePinned = False
        for i in range(len(self.pins) - 1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinsDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        #print(self.espassant_possible)
        if self.white_to_move:
            if self.board[r-1][c] == "--":
                if not piecePinned or pinsDirection == (-1, 0):
                    moves.append(Move((r, c), (r-1, c), self.board))
                    if r == 6 and self.board[r-2][c] == "--":
                        moves.append(Move((r, c), (r-2, c), self.board))
            if c - 1 >= 0:
                if self.board[r-1][c-1][0] == "b":
                    if not piecePinned or pinsDirection == (-1, -1):
                      moves.append(Move((r, c), (r-1, c-1), self.board))
                elif (r - 1, c - 1) == self.espassant_possible:
                    if not piecePinned or pinsDirection == (-1, -1):
                        moves.append(Move((r, c), (r-1, c-1), self.board,isenpassant=True))
                        x = Move((r, c), (r-1, c-1), self.board,isenpassant=True)
                        print("enpassant")
                        print(r,c,r-1,c-1)
                        print(x.ispassant)
            if c + 1 <= 7:
                if self.board[r-1][c+1][0] == "b":
                    if not piecePinned or pinsDirection == (-1, 1):
                      moves.append(Move((r, c), (r-1, c+1), self.board))
                elif (r - 1, c + 1) == self.espassant_possible:
                    if not piecePinned or pinsDirection == (-1, 1):
                        moves.append(Move((r, c), (r-1, c+1), self.board,isenpassant=True))
                        x = Move((r, c), (r-1, c+1), self.board,isenpassant=True)
                        print("enpassant")
                        print(r,c,r-1,c+1)
                        print(x.ispassant)
                        
        else:
            if self.board[r+1][c] == "--":
                if not piecePinned or pinsDirection == (1, 0):
                    moves.append(Move((r, c), (r+1, c), self.board))
                    if r == 1 and self.board[r+2][c] == "--":
                        moves.append(Move((r, c), (r+2, c), self.board))
            if c - 1 >= 0:
                if self.board[r+1][c-1][0] == "w":
                    if not piecePinned or pinsDirection == (1, -1):
                        moves.append(Move((r, c), (r+1, c-1), self.board))
                elif (r + 1, c - 1) == self.espassant_possible:
                    if not piecePinned or pinsDirection == (1, -1):
                        moves.append(Move((r, c), (r+1, c-1), self.board,isenpassant=True))
                        x = Move((r, c), (r+1, c-1), self.board,isenpassant=True)
                        print("enpassant")
                        print(r,c,r+1,c-1)
                        print(x.ispassant)
            if c + 1 <= 7:
                if self.board[r+1][c+1][0] == "w":
                    if not piecePinned or pinsDirection == (1, 1):
                        moves.append(Move((r, c), (r+1, c+1), self.board))
                elif (r + 1, c + 1) == self.espassant_possible:
                    if not piecePinned or pinsDirection == (1, 1):
                        moves.append(Move((r, c), (r+1, c+1), self.board,isenpassant=True))
                        x = Move((r, c), (r+1, c+1), self.board,isenpassant=True)
                        print("enpassant")
                        print(r,c,r+1,c+1)
                        print(x.ispassant)
    def getRookMoves(self, r, c, moves):
        # Rook moves in straight lines
        pinDirection = ()
        piecePinned = False
        for i in range(len(self.pins) - 1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        for d in directions:
            for i in range(1, 8):
                new_r = r + d[0] * i
                new_c = c + d[1] * i
                if 0 <= new_r < 8 and 0 <= new_c < 8:
                    if self.board[new_r][new_c] == "--":
                        if not piecePinned or pinDirection == (d[0], d[1]):
                            moves.append(Move((r, c), (new_r, new_c), self.board))
                    elif self.board[new_r][new_c][0] != self.board[r][c][0]:
                        if not piecePinned or pinDirection == (d[0], d[1]):
                          moves.append(Move((r, c), (new_r, new_c), self.board))
                        break
                    else:
                        break
                else:
                    break
    def getKnightMoves(self, r, c, moves):
        # Knight moves in L-shape
        pinDirection = ()
        piecePinned = False
        for i in range(len(self.pins) - 1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        knight_moves = [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)]
        for move in knight_moves:
            new_r = r + move[0]
            new_c = c + move[1]
            if 0 <= new_r < 8 and 0 <= new_c < 8:
                if self.board[new_r][new_c] == "--" or self.board[new_r][new_c][0] != self.board[r][c][0]:
                    if not piecePinned :
                       moves.append(Move((r, c), (new_r, new_c), self.board))
    def getBishopMoves(self, r, c, moves):
        # Bishop moves in diagonals
        pinDirection = ()
        piecePinned = False
        for i in range(len(self.pins) - 1,-1,-1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        for d in directions:
            for i in range(1, 8):
                new_r = r + d[0] * i
                new_c = c + d[1] * i
                if 0 <= new_r < 8 and 0 <= new_c < 8:
                    if self.board[new_r][new_c] == "--":
                        if not piecePinned or pinDirection == (d[0], d[1]):
                          moves.append(Move((r, c), (new_r, new_c), self.board))
                    elif self.board[new_r][new_c][0] != self.board[r][c][0]:
                        if not piecePinned or pinDirection == (d[0], d[1]):
                            moves.append(Move((r, c), (new_r, new_c), self.board))
                        break
                    else:
                        break
                else:
                    break
    def getQueenMoves(self, r, c, moves):
        # Queen moves like both a rook and a bishop
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)
    def getKingMoves(self, r, c, moves):
        # King moves one square in any direction
        king_moves = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
        ally_color = "w" if self.white_to_move else "b"
        check = 0
        for move in king_moves:
            new_r = r + move[0]
            new_c = c + move[1]
            if 0 <= new_r < 8 and 0 <= new_c < 8:
                piece = self.board[new_r][new_c]
                if piece[0] != ally_color:
                    if ally_color == "w":
                        self.white_king_location = (new_r, new_c)
                    else:
                        self.black_king_location = (new_r, new_c)
                in_check,pins,checks = self.checkForPinsAndChecks()
                if not in_check and piece[0] != ally_color:
                    check = 1
                    moves.append(Move((r, c), (new_r, new_c), self.board))
                if ally_color == "w":
                    self.white_king_location = (r, c)
                else:
                    self.black_king_location = (r, c)
        if check == 0 :
            self.check_mate = True
            self.stale_mate = True
    def getCastleMoves(self, r, c, moves,):
        if self.square_under_attack(r, c):
            return
        if (self.white_to_move and self.current_castle_rights.wks) or (not self.white_to_move and self.current_castle_rights.bks):
            self.getKingSideCastleMoves(r, c, moves)
        if (self.white_to_move and self.current_castle_rights.wqs) or (not self.white_to_move and self.current_castle_rights.bqs):
            self.getQueenSideCastleMoves(r, c, moves)
    def getKingSideCastleMoves(self, r, c, moves,):
        if self.board[r][c + 1] == "--" and self.board[r][c + 2] == "--":
            if not self.square_under_attack(r, c + 1) and not self.square_under_attack(r, c + 2):
                print('can castle')
                moves.append(Move((r, c), (r, c + 2), self.board,isCastleMoved = True))
        
    def getQueenSideCastleMoves(self, r, c, moves):
        if self.board[r][c - 1] == "--" and self.board[r][c - 2] == "--" and self.board[r][c - 3] == "--":
            if not self.square_under_attack(r, c - 1) and not self.square_under_attack(r, c - 2):
                print('can castle')
                moves.append(Move((r, c), (r, c - 2), self.board,isCastleMoved = True))
class CastleRights :
     def __init__(self,wks,bks,wqs,bqs) :
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

class Move :
    # maps keys to values
    ranks_to_rows = {"1": 7, "2": 6, "3": 5, "4": 4, "5": 3, "6": 2, "7": 1, "8": 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}
    cols_to_files = {v: k for k, v in files_to_cols.items()}

    def __init__(self, start_sq, end_sq, board,isenpassant=False,isCastleMoved=False): 
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        self.isPawnPromotion = False
        self.ispassant = isenpassant
        self.isCastleMoved = isCastleMoved
        # pawn promotion
        if (self.piece_moved == "wp" and self.end_row == 0) or (self.piece_moved == "bp" and self.end_row == 7):
            self.isPawnPromotion = True
        # en passant
        #print(self.ispassant)
        if self.ispassant: 
            self.piece_captured = "bp" if self.piece_moved == "wp" else "wp"
        self.move_id = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_id == other.move_id
        return False
    def get_chess_notation(self):
        return self.get_rank_file(self.start_row, self.start_col) + self.get_rank_file(self.end_row, self.end_col)
    def get_rank_file(self, r, c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]

class dragger:
    def __init__(self):
        self.piece = None
        self.mouse_x = -1
        self.mouse_y = -1
        self.dragging = False
        self.initial_x = -1
        self.initial_y = -1
    def update_mouse(self, x, y):
        self.mouse_x = x
        self.mouse_y = y
    def save_initial_position(self, x, y):
        self.initial_x = x
        self.initial_y = y
    def drag_piece(self, piece):
        self.piece = piece
        self.dragging = True
    def undrag_piece(self):
        self.piece = None
        self.dragging = False
        self.initial_x = -1
        self.initial_y = -1
    def update_blit(self, screen, SQ_SIZE):
        piece= self.piece
        path = f'images/{piece}.png'
        img = pg.transform.scale(pg.image.load(path), (SQ_SIZE, SQ_SIZE))
        # print(pg.image.load(f'images/{piece}.png'))
        center_x = self.mouse_x* SQ_SIZE + SQ_SIZE // 2
        center_y = self.mouse_y * SQ_SIZE + SQ_SIZE // 2
        img_center = (center_x, center_y)
        rect = img.get_rect(center=img_center)
        screen.blit(img,rect)

       