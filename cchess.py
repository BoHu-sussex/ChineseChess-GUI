# -*- coding: utf-8 -*-
# Author: Bo Hu
# Date: 2024-05-08
import tkinter as tk


class ChineseChessGUI:
    def __init__(self, root):
        # Constants for the board size
        self.BOARD_WIDTH = 9
        self.BOARD_HEIGHT = 10
        self.SQUARE_SIZE = 60

        # Define the pieces with their Chinese characters and colors
        self.PIECES = {
            'King': {'weight': 5, 'red': '帥', 'black': '將', 'next': [(0, 60), (0, -60), (-60, 0), (60, 0)]},
            'Chariot': {'weight': 4, 'red': '俥', 'black': '車',
                        'next': [(x, 0) for x in range(-480, 481, 60)] + [(0, y) for y in range(-540, 541, 60)]},
            'Horse': {'weight': 3, 'red': '馬', 'black': '馬',
                      'next': [(-60, -120), (-120, -60), (-120, 60), (-60, 120), (60, 120), (120, 60), (120, -60),
                               (60, -120)]},
            'Cannon': {'weight': 3, 'red': '炮', 'black': '砲',
                       'next': [(x, 0) for x in range(-480, 481, 60)] + [(0, y) for y in range(-540, 541, 60)]},
            'Pawn': {'weight': 2, 'red': '兵', 'black': '卒', 'next': [(0, 60), (0, -60), (-60, 0), (60, 0)]},
            'Advisor': {'weight': 4, 'red': '仕', 'black': '士', 'next': [(60, 60), (60, -60), (-60, 60), (-60, -60)]},
            'Elephant': {'weight': 3, 'red': '相', 'black': '象',
                         'next': [(120, 120), (120, -120), (-120, 120), (-120, -120)]}
        }
        # Initial positions for each piece type (x, y coordinates)
        self.INITIAL_POSITIONS = {
            'King': [(4, 0), (4, 9)],
            'Chariot': [(0, 0), (8, 0), (0, 9), (8, 9)],
            'Horse': [(1, 0), (7, 0), (1, 9), (7, 9)],
            'Cannon': [(1, 2), (7, 2), (1, 7), (7, 7)],
            'Pawn': [(0, 3), (2, 3), (4, 3), (6, 3), (8, 3), (0, 6), (2, 6), (4, 6), (6, 6), (8, 6)],
            'Advisor': [(3, 0), (5, 0), (3, 9), (5, 9)],
            'Elephant': [(2, 0), (6, 0), (2, 9), (6, 9)]
        }

        # Draw the board and frames
        self.create_frame_1(root)
        self.canvas = tk.Canvas(root, width=(self.BOARD_WIDTH + 0.5) * self.SQUARE_SIZE,
                                height=(self.BOARD_HEIGHT + 0.5) * self.SQUARE_SIZE)
        self.canvas.pack(side='top')
        self.canvas.bind("<Button-1>", self.player_move_piece)
        self.create_frame_2(root)
        self.draw_board()

        # Dictionary to keep track of pieces
        self.pieces = {}
        self.board = {}

        # Begin a new game
        self.new_game()

    def create_frame_1(self, root):
        """
        Create the frame above the board canvas
        :param root: The tk.Window
        """
        # Indicate the depth of search tree
        self.difficulty = tk.IntVar()
        self.difficulty.set(2)

        # Whether AI moves first
        self.ai_first = tk.BooleanVar()

        self.frame_1 = tk.Frame(root)
        self.frame_1.pack(side='top')

        self.label2 = tk.Label(self.frame_1, text='Difficulty:', font=('Arial', 20))
        self.label2.grid(row=0, column=0)

        self.scale = tk.Scale(self.frame_1, font=('Arial', 15), variable=self.difficulty, orient=tk.HORIZONTAL, from_=1,
                              to=3)
        self.scale.grid(row=0, column=1)

        self.check = tk.Checkbutton(self.frame_1, text='AI goes first    ', font=('Arial', 20), variable=self.ai_first,
                                    command=self.ai_move_first)
        self.check.grid(row=0, column=2)

        self.button1 = tk.Button(self.frame_1, text="New Game", font=('Arial', 20), fg="blue", command=self.new_game)
        self.button1.grid(row=0, column=3)

    def ai_move_first(self):
        """
        AI make the first move
        """
        self.check.config(state='disabled')
        self.ai_move_piece()

    def new_game(self):
        """
        Begin a new game
        """
        # Destroy the previous board
        for piece_id in self.pieces.keys():
            self.canvas.delete(piece_id)

        # Init the new board
        self.pieces = {}
        self.board = {}
        self.place_pieces()

        # Set the default widget
        self.check.deselect()
        self.check.config(state='normal')

        # Get the Kings' ID in current game
        king_ids = self.get_king_id()
        self.black_king_id = king_ids['black_king']
        self.red_king_id = king_ids['red_king']

        # Init the variables
        self.moves_count = 0
        self.is_moving = False

        self.label3.config(text="")
        self.label4.config(text="")

    def create_frame_2(self, root):
        """
        Create the frame below board canvas to show some information
        :param root: The tk.Window
        """
        self.frame_2 = tk.Frame(root)
        self.frame_2.pack(side='top')

        self.label3 = tk.Label(self.frame_2, text='Choose a piece...', font=('Arial', 20))
        self.label3.grid(row=2, column=0, columnspan=2)

        # This label is to show explanation for invalid move
        self.label4 = tk.Label(self.frame_2, text='', font=('Arial', 15), fg='red')
        self.label4.grid(row=3, column=0, columnspan=2)

    def cord(self, coord):
        """
        Translate the coordinate in board into canvas
        :param coord: coordinate in board
        :return: coordinate in canvas
        """
        return (coord + 0.5) * self.SQUARE_SIZE

    def draw_board(self):
        """
        Draw the board
        """
        for i in range(self.BOARD_WIDTH):
            self.canvas.create_line(self.cord(i), self.cord(0), self.cord(i), self.cord(self.BOARD_HEIGHT - 1))

        for i in range(self.BOARD_HEIGHT):
            self.canvas.create_line(self.cord(0), self.cord(i), self.cord(self.BOARD_WIDTH - 1), self.cord(i))

        # Draw the river
        self.canvas.create_rectangle(self.cord(0), self.cord(4), self.cord(self.BOARD_WIDTH - 1), self.cord(5),
                                     fill='lightblue')

        # Draw the palaces
        for x, y in [(3, 0), (3, 7)]:
            self.canvas.create_line(self.cord(x), self.cord(y), self.cord(x + 2), self.cord(y + 2))
            self.canvas.create_line(self.cord(x + 2), self.cord(y), self.cord(x), self.cord(y + 2))

        # Draw the notation
        self.x_notation = "abcdefghi"
        self.y_notation = "0987654321"
        for x in range(0, 9):
            self.canvas.create_text(self.cord(x), self.cord(9.5), text=self.x_notation[x], font=('Arial', 20),
                                    fill='black')
        for y in range(0, 10):
            self.canvas.create_text(self.cord(8.5), self.cord(y), text=self.y_notation[y], font=('Arial', 20),
                                    fill='black')

    def place_pieces(self):
        """
        Place pieces on the canvas
        """
        for piece_type, positions in self.INITIAL_POSITIONS.items():
            for x, y in positions:
                piece_info = {}
                color = 'black' if y < self.BOARD_HEIGHT / 2 else 'red'
                text = self.PIECES[piece_type][color]
                piece_id = self.canvas.create_text(self.cord(x), self.cord(y), text=text, font=('Arial', 35),
                                                   fill=color)

                # Store the information of pieces
                piece_info['type'] = piece_type
                piece_info['id'] = piece_id
                piece_info['color'] = color
                self.board[(x, y)] = piece_info
                self.pieces[piece_id] = (x, y)

    def player_move_piece(self, event):
        """
        Player moves pieces by click the source and then click the target
        :param event: The mouse click event
        """
        # Make sure the game is not over
        if not self.is_game_over() == 0:
            self.label3.config(text="Game is over! You can begin a new game!")
            return

        # Choose the source piece
        if not self.is_moving:
            # Get the coordinate on the board
            self.x1 = round(event.x / self.SQUARE_SIZE - 0.5)
            self.y1 = round(event.y / self.SQUARE_SIZE - 0.5)

            # Get the item id of current piece
            self.current_item_id = self.canvas.find_closest(self.cord(self.x1), self.cord(self.y1))[0]

            # Ensure that the player chooses a piece
            if self.current_item_id in self.pieces.keys():
                # Make sure player click the piece of the player's side
                if self.board[(self.x1, self.y1)]['color'] == 'red' and self.ai_first.get():
                    self.label3.config(text="Oops...AI is red side, you are black side!")
                    self.label4.config(text="")
                    return
                elif self.board[(self.x1, self.y1)]['color'] == 'black' and not self.ai_first.get():
                    self.label3.config(text="Oops...AI is black side, you are red side!")
                    self.label4.config(text="")
                    return

                # Get the source coordinate for further process
                self.source = (self.cord(self.x1), self.cord(self.y1))
                self.is_moving = True

                # Show information below the canvas
                self.label3.config(
                    text=f"You have chosen the {self.board[self.pieces[self.current_item_id]]['type']} at {self.x_notation[self.x1]}{self.y_notation[self.y1]}.\n Please make a move...")
                self.label4.config(text='', fg='red', font=('Arial', 15))

        # Choose the target
        else:
            # Get the coordinate on the board
            self.x2 = round(event.x / self.SQUARE_SIZE - 0.5)
            self.y2 = round(event.y / self.SQUARE_SIZE - 0.5)

            # Translate the coordinate on the board to canvas
            self.target = (self.cord(self.x2), self.cord(self.y2))
            target_id = self.canvas.find_closest(self.target[0], self.target[1])[0]

            # Get the change amount of piece's coordinate on canvas
            dx = self.target[0] - self.source[0]
            dy = self.target[1] - self.source[1]

            # Ensure piece in chess board
            if self.x2 > 8 or self.y2 > 9:
                return

            # Ensure piece can not move to position with piece with same color
            if target_id in self.pieces.keys() and self.board[self.pieces[target_id]]['color'] == \
                    self.board[self.pieces[self.current_item_id]]['color']:
                return

            # Get the type and color of the source piece
            piece_type = self.board[self.pieces[self.current_item_id]]['type']
            piece_color = self.board[self.pieces[self.current_item_id]]['color']

            # Make sure whether the movement is valid roughly
            if (dx, dy) in self.PIECES[self.board[self.pieces[self.current_item_id]]['type']]['next']:

                # Current piece cannot move if it causes two Kings face each other directly
                if not piece_type == 'King' and self.pieces[self.red_king_id][0] == self.pieces[self.black_king_id][0] == self.x1 and dx:
                    cnt_block = 0  # Count the pieces between Kings
                    for x, y in self.board.keys():
                        if x == self.x1 and self.pieces[self.black_king_id][1] < y < self.pieces[self.red_king_id][1]:
                            cnt_block += 1
                    if cnt_block == 1:
                        self.is_moving = False
                        self.label3.config(text=f"Oops...This is an invalid move!")
                        self.label4.config(text=f"Your move for {piece_type} cause your King face the other King directly!")
                        return

                # Special rules for King and Advisor
                if piece_type in ('King', 'Advisor'):
                    # King and Advisor cannot go past its palace
                    if piece_color == 'red' and 3 <= self.x2 <= 5 and 7 <= self.y2 <= 9:
                        pass
                    elif piece_color == 'black' and 3 <= self.x2 <= 5 and 0 <= self.y2 <= 2:
                        pass
                    else:
                        self.is_moving = False
                        self.label3.config(text=f"Oops...This is an invalid move!")
                        self.label4.config(text=f"{piece_type} can not go past its 3x3 palace!")
                        return

                    # King cannot face another King directly
                    if piece_type == 'King':
                        king_pass = True
                        if piece_color == 'red' and self.x2 == self.pieces[self.black_king_id][
                            0] or piece_color == 'black' and self.x2 == self.pieces[self.red_king_id][0]:
                            king_pass = False
                            for other_x, other_y in self.pieces.values():
                                if other_x == self.x2 and (self.y2 < other_y < self.pieces[self.red_king_id][1] or
                                                           self.pieces[self.black_king_id][1] < other_y < self.y2):
                                    king_pass = True
                                    break
                        if not king_pass:
                            self.is_moving = False
                            self.label3.config(text=f"Oops...This is an invalid move!")
                            self.label4.config(text=f"{piece_type} can not face the King in other side directly!")
                            return

                # Special rules for Elephant
                if piece_type == 'Elephant':
                    # Elephant can not move if there is a piece on the point in between
                    if ((self.x1 + self.x2) / 2, (self.y1 + self.y2) / 2) in self.board.keys():
                        self.is_moving = False
                        self.label3.config(text=f"Oops...This is an invalid move!")
                        self.label4.config(
                            text=f"{piece_type} can not move if there is a piece on the point in between!")
                        return

                    # Elephant cannot go past the river
                    if piece_color == 'black' and 0 <= self.y2 <= 4:
                        pass
                    elif piece_color == 'red' and 5 <= self.y2 <= 9:
                        pass
                    else:
                        self.is_moving = False
                        self.label3.config(text=f"Oops...This is an invalid move!")
                        self.label4.config(text=f"{piece_type} can not go across the river!")
                        return

                # Special rules for Chariot
                if piece_type == 'Chariot':
                    if dy == 0:
                        if dx > 0:
                            for x in range(self.x1 + 1, self.x2):
                                if (x, self.y1) in self.board.keys():
                                    self.is_moving = False
                                    self.label3.config(text=f"Oops...This is an invalid move!")
                                    self.label4.config(text=f"{piece_type} is obstructed!")
                                    return
                        else:
                            for x in range(self.x2 + 1, self.x1):
                                if (x, self.y1) in self.board.keys():
                                    self.is_moving = False
                                    self.label3.config(text=f"Oops...This is an invalid move!")
                                    self.label4.config(text=f"{piece_type} is obstructed!")
                                    return
                    else:
                        if dy > 0:
                            for y in range(self.y1 + 1, self.y2):
                                if (self.x1, y) in self.board.keys():
                                    self.is_moving = False
                                    self.label3.config(text=f"Oops...This is an invalid move!")
                                    self.label4.config(text=f"{piece_type} is obstructed!")
                                    return
                        else:
                            for y in range(self.y2 + 1, self.y1):
                                if (self.x1, y) in self.board.keys():
                                    self.is_moving = False
                                    self.label3.config(text=f"Oops...This is an invalid move!")
                                    self.label4.config(text=f"{piece_type} is obstructed!")
                                    return

                # Special rules for Horse
                if piece_type == 'Horse':
                    if self.x2 - self.x1 == 1 or self.x2 - self.x1 == -1:
                        if dy > 0:
                            if (self.x1, self.y1 + 1) in self.board.keys():
                                self.is_moving = False
                                self.label3.config(text=f"Oops...This is an invalid move!")
                                self.label4.config(
                                    text=f"{piece_type} can not move if there is a piece on the point in between!")
                                return
                        else:
                            if (self.x1, self.y1 - 1) in self.board.keys():
                                self.is_moving = False
                                self.label3.config(text=f"Oops...This is an invalid move!")
                                self.label4.config(
                                    text=f"{piece_type} can not move if there is a piece on the point in between!")
                                return
                    if self.x2 - self.x1 == 2 or self.x2 - self.x1 == -2:
                        if dx > 0:
                            if (self.x1 + 1, self.y1) in self.board.keys():
                                self.is_moving = False
                                self.label3.config(text=f"Oops...This is an invalid move!")
                                self.label4.config(
                                    text=f"{piece_type} can not move if there is a piece on the point in between!")
                                return
                        else:
                            if (self.x1 - 1, self.y1) in self.board.keys():
                                self.is_moving = False
                                self.label3.config(text=f"Oops...This is an invalid move!")
                                self.label4.config(
                                    text=f"{piece_type} can not move if there is a piece on the point in between!")
                                return

                # Special rules for Cannon
                if piece_type == 'Cannon':
                    count = 0
                    if dy == 0:
                        if dx > 0:
                            for x in range(self.x1 + 1, self.x2):
                                if (x, self.y1) in self.board.keys():
                                    count += 1
                        else:
                            for x in range(self.x2 + 1, self.x1):
                                if (x, self.y1) in self.board.keys():
                                    count += 1

                    else:
                        if dy > 0:
                            for y in range(self.y1 + 1, self.y2):
                                if (self.x1, y) in self.board.keys():
                                    count += 1

                        else:
                            for y in range(self.y2 + 1, self.y1):
                                if (self.x1, y) in self.board.keys():
                                    count += 1

                    if count == 0 and not (self.x2, self.y2) in self.board.keys():
                        pass
                    elif count == 1 and (self.x2, self.y2) in self.board.keys():
                        pass
                    elif count == 0 and (self.x2, self.y2) in self.board.keys():
                        self.is_moving = False
                        self.label3.config(text=f"Oops...This is an invalid move!")
                        self.label4.config(text=f"{piece_type} needs one intermittent piece!")
                        return
                    else:
                        self.is_moving = False
                        self.label3.config(text=f"Oops...This is an invalid move!")
                        self.label4.config(text=f"{piece_type} is obstructed!")
                        return

                # Special rules for Pawn
                if piece_type == 'Pawn':
                    if piece_color == 'red':
                        if dy > 0 or self.y1 >= 5 and dx != 0:
                            self.is_moving = False
                            self.label3.config(text=f"Oops...This is an invalid move!")
                            if dy > 0:
                                self.label4.config(text=f"{piece_type} can only move forward!")
                            else:
                                self.label4.config(
                                    text=f"{piece_type} can only move sideways after it goes across the river!")
                            return
                    else:
                        if dy < 0 or self.y1 <= 4 and dx != 0:
                            self.is_moving = False
                            self.label3.config(text=f"Oops...This is an invalid move!")
                            if dy < 0:
                                self.label4.config(text=f"{piece_type} can only move forward!")
                            else:
                                self.label4.config(
                                    text=f"{piece_type} can only move sideways after it goes across the river!")
                            return

                # Check for capture
                capture = False
                if target_id in self.pieces.keys() and self.board[self.pieces[target_id]]['color'] != \
                        self.board[self.pieces[self.current_item_id]]['color']:
                    # Remove captured piece
                    self.label3.config(text=f"You capture opponent’s {self.board[self.pieces[target_id]]['type']}!")
                    self.canvas.delete(target_id)
                    del self.board[(self.x2, self.y2)]
                    del self.pieces[target_id]
                    capture = True

                # Move the piece
                if (self.x2, self.y2) not in self.board or self.board[(self.x2, self.y2)]['color'] != \
                        self.board[self.pieces[self.current_item_id]]['color']:

                    # Move the piece on canvas
                    self.canvas.move(self.current_item_id, dx, dy)
                    self.moves_count += 1
                    self.check.config(state='disabled')

                    # Update the pieces and board
                    self.board[(self.x2, self.y2)] = self.board[self.pieces[self.current_item_id]]
                    del self.board[self.pieces[self.current_item_id]]
                    self.pieces[self.current_item_id] = (self.x2, self.y2)

                    # AI make a move if game is not over
                    if self.is_game_over() == 0:
                        self.ai_move_piece()
                    elif self.is_game_over() == 1:
                        self.label4.config(text=f"You Win!!!", fg='green', font=('Arial', 20))
                    elif self.is_game_over() == 3:
                        self.label4.config(text="Draw", fg='green', font=('Arial', 20))

                    if not capture:
                        self.label3.config(
                            text=f"Valid move {self.x_notation[self.x1]}{self.y_notation[self.y1]}{self.x_notation[self.x2]}{self.y_notation[self.y2]}")
                else:
                    self.label3.config(text=f"Oops...This is an invalid move!")

            # Some warning if player makes invalid operation
            else:
                self.label3.config(text=f"Oops...This is an invalid move!")

                # Errors for corresponding pieces
                if piece_type == 'King':
                    self.label4.config(text="King can only move one block vertically or horizontally!")
                if piece_type == 'Chariot':
                    self.label4.config(text="Chariot can only move vertically or horizontally!")
                if piece_type == 'Horse':
                    self.label4.config(
                        text="Horse can only move to the opposite corner of a rectangle formed by 1x2 blocks!")
                if piece_type == 'Cannon':
                    self.label4.config(text="Cannon can only move vertically or horizontally!")
                if piece_type == 'Pawn':
                    self.label4.config(text="Pawn can only move one block vertically or horizontally!")
                if piece_type == 'Advisor':
                    self.label4.config(text="Advisor can only move diagonally by a block!")
                if piece_type == 'Elephant':
                    self.label4.config(
                        text="Elephant can only move to the opposite corner of a square formed by 2x2 blocks!")

            # Change the flag for next movement
            self.is_moving = False

    def ai_move_piece(self):
        """
        AI moves a piece
        """
        # AI begin evaluation to get the best move
        self.start_evaluation()

        # Get the source and target information of the best move
        best_value = max(self.successor_eval.keys())
        source_id, dx, dy = self.successor_eval[best_value]
        source_x, source_y = self.pieces[source_id]
        target_x, target_y = source_x + dx, source_y + dy

        # AI capture player's pieces
        if (target_x, target_y) in self.board.keys():
            target_id = self.board[(target_x, target_y)]['id']
            del self.board[(target_x, target_y)]
            del self.pieces[target_id]
            self.canvas.delete(target_id)

        # AI make move
        self.board[(target_x, target_y)] = self.board[(source_x, source_y)]
        self.pieces[source_id] = (target_x, target_y)
        del self.board[(source_x, source_y)]
        self.canvas.move(source_id, dx * 60, dy * 60)
        self.moves_count += 1
        self.label4.config(
            text=f"AI makes move {self.x_notation[source_x]}{self.y_notation[source_y]}{self.x_notation[target_x]}{self.y_notation[target_y]}",
            fg='blue', font=('Arial', 20))

        # Check whether game is over
        if self.is_game_over() == 3:
            self.label4.config(text="Draw", fg='green', font=('Arial', 20))
        elif self.is_game_over() == 2:
            self.label4.config(text="You Lose...", fg='green', font=('Arial', 20))

    def is_game_over(self):
        """
        Check whether game is over
        :return: An int value representing the state of game
        """
        # AI wins
        if self.red_king_id not in self.pieces.keys() and self.ai_first.get() or self.black_king_id not in self.pieces.keys() and not self.ai_first.get():
            res = 1
        # Player wins
        elif self.black_king_id not in self.pieces.keys() and self.ai_first.get() or self.red_king_id not in self.pieces.keys() and not self.ai_first.get():
            res = 2
        # Draw
        elif self.moves_count == 50:
            res = 3
        # Game is not over
        else:
            res = 0
        return res

    def get_king_id(self):
        """
        Get the ID of both King for easy further process
        :return: A dict consists of id of King
        """
        res = {}
        for info in self.board.values():
            if info['type'] == 'King':
                if info['color'] == 'red':
                    res['red_king'] = info['id']
                else:
                    res['black_king'] = info['id']
        return res

    def static_evaluation(self):
        """
        Evaluate the current board and return a score
        Higher the score means that the AI's side has more advantage on current board
        :return: The static score value of the current chess board
        """
        # King is captured
        if self.black_king_id not in self.pieces.keys():
            if self.ai_first.get():
                return float("inf")
            else:
                return -float("inf")
        if self.red_king_id not in self.pieces.keys():
            if self.ai_first.get():
                return -float("inf")
            else:
                return float("inf")

        evaluation = 0  # The greater the value, the better for the red side       
        attack_strength = 0  # A measure of the distribution of attacking pieces
        num_advantage = 0  # A weighted measure of the advantage of the number of pieces

        # Go through the pieces on board to calculate the static evaluation
        for (x, y), info in self.board.items():
            # Calculate advantage of nums
            if info['color'] == 'red':
                if self.ai_first.get():
                    num_advantage += self.PIECES[info['type']]['weight'] * 8
                else:
                    num_advantage -= self.PIECES[info['type']]['weight'] * 8

            else:
                if self.ai_first.get():
                    num_advantage -= self.PIECES[info['type']]['weight'] * 8
                else:
                    num_advantage += self.PIECES[info['type']]['weight'] * 8

            # Calculate attack strength
            if info['type'] in ('Chariot', 'Horse', 'Cannon', 'Pawn'):
                if info['color'] == 'red':
                    if self.ai_first.get():
                        attack_strength += (9 - y) * self.PIECES[info['type']]['weight']
                    else:
                        attack_strength -= (9 - y) * self.PIECES[info['type']]['weight']

                else:
                    if self.ai_first.get():
                        attack_strength -= y * self.PIECES[info['type']]['weight']
                    else:
                        attack_strength += y * self.PIECES[info['type']]['weight']

        # Calculate the combination of two metrics
        evaluation += num_advantage + attack_strength
        return evaluation

    def start_evaluation(self):
        """
        Start the evaluation for AI to make a decision
        """
        self.successor_eval = {}
        self.depth_limit = self.difficulty.get()

        # Call the minimax algorithm to evaluate
        self.minimax(None, 0, -float("inf"), float("inf"))

    def occupy(self, action):
        """
        Make the occupy on the board to mark the movement of piece
        :param action: A tuple indicate a movement
        :return: A dict consist of the information of occupy
        """
        if not action:
            return None

        # Get the information of current action
        source_id, dx, dy = action
        x, y = self.pieces[source_id]
        occupy_info = {'source_info': (x, y, self.board[(x, y)])}

        # Make a capture
        if (x + dx, y + dy) in self.board.keys():
            eaten_id = self.board[(x + dx, y + dy)]['id']
            occupy_info['eaten_info'] = (x + dx, y + dy, self.board[(x + dx, y + dy)])
            del self.pieces[eaten_id]

        # Move the piece
        self.board[(x + dx, y + dy)] = self.board[(x, y)]
        del self.board[(x, y)]
        self.pieces[source_id] = (x + dx, y + dy)

        return occupy_info

    def restore(self, occupy_info):
        """
        Restore the board after occupying.
        :param occupy_info: A dict consist of the information produced by occupy
        """
        if not occupy_info:
            return

        # Get the information of changes on board
        source_x, source_y, source_info = occupy_info['source_info']

        # Occupy doesn't make a capture
        if len(occupy_info) == 1:
            # Restore the piece to its original place
            self.board[(source_x, source_y)] = source_info
            del self.board[self.pieces[source_info['id']]]
            self.pieces[source_info['id']] = (source_x, source_y)

        # Occupy make a capture
        else:
            # Restore the piece to its original place
            eaten_x, eaten_y, eaten_info = occupy_info['eaten_info']
            self.board[(source_x, source_y)] = source_info
            del self.board[self.pieces[source_info['id']]]
            self.pieces[source_info['id']] = (source_x, source_y)

            # Restore the piece which has been eaten
            self.board[(eaten_x, eaten_y)] = eaten_info
            self.pieces[eaten_info['id']] = (eaten_x, eaten_y)

    def minimax(self, action, depth, alpha, beta):
        """
        The algorithm implements the minimax evaluation
        :param action: The valid movement of piece to be evaluated
        :param depth: The current depth of minimax search tree
        :param alpha: The evaluation value in AI side
        :param beta: The evaluation value in player side
        :return: The static evaluation at leaf nodes or the static evaluation when game over
        """
        # Whether the current layer is for maximizing player
        is_maximizing_player = True if depth % 2 == 0 else False

        # Store the information of occupy for later restore
        occupy_info = self.occupy(action=action)

        # If reach the depth limit or game over
        best_value = self.static_evaluation()
        if depth >= self.depth_limit or best_value in (float("inf"), -float("inf")):
            pass

        # For AI side
        elif is_maximizing_player:
            best_value = -float("inf")
            next_actions = self.valid_next_actions(is_maximizing_player)

            # Go through all potential actions
            for next_action in next_actions:
                value = self.minimax(next_action, depth + 1, alpha, beta)

                # Record the value at root node
                if depth == 0:
                    self.successor_eval[value] = next_action

                # Choose the larger one
                best_value = max(best_value, value)
                alpha = max(alpha, best_value)
                if alpha > beta:
                    break

        # For player side
        elif not is_maximizing_player:
            next_actions = self.valid_next_actions(is_maximizing_player)
            best_value = float("inf")

            # Go through all potential actions
            for next_action in next_actions:
                value = self.minimax(next_action, depth + 1, alpha, beta)

                # Choose the smaller one
                best_value = min(best_value, value)
                beta = min(beta, best_value)
                if beta < alpha:
                    break

        # Restore the board
        self.restore(occupy_info)

        return best_value

    def valid_next_actions(self, is_maximizing_player):
        """
        This method is to get all the valid actions for one side to move each pieces in its side.
        :param is_maximizing_player: Indicate whether now is AI or player to move.
        :return: A list of tuple (source_id, dx, dy) represents valid next actions for one side
        """
        valid_next_actions = []  # Init the list of final actions

        # Go through all pieces in board
        for (x, y), info in self.board.items():
            # Get the color and type of the current piece
            piece_type = info['type']
            piece_color = info['color']

            # Make sure the piece belongs to the right side
            if ((
                    piece_color == 'red' and is_maximizing_player or piece_color == 'black' and not is_maximizing_player) and self.ai_first.get()
                    or (
                            piece_color == 'red' and not is_maximizing_player or piece_color == 'black' and is_maximizing_player) and not self.ai_first.get()):

                # Go through all potential movements of the current piece
                for dx, dy in self.PIECES[piece_type]['next']:
                    # Translate the coordinate on canvas to board
                    dx, dy = int(dx // 60), int(dy // 60)
                    # Init the flag indicating whether the movement is valid
                    is_valid = True

                    # Ensure piece in chess board
                    if not 0 <= x + dx <= 8 or not 0 <= y + dy <= 9:
                        continue

                    # Make sure current movement will not cause two Kings face each other directly
                    if not piece_type == 'King' and self.pieces[self.black_king_id][0] == self.pieces[self.red_king_id][0] == x and dx:
                        cnt_block = 0  # Count the pieces between two Kings

                        # Go through the pieces on board to check whether the current piece is the only one between two Kings
                        for other_x, other_y in self.board.keys():
                            if other_x == x and self.pieces[self.black_king_id][1] < other_y < self.pieces[self.red_king_id][1]:
                                cnt_block += 1
                        if cnt_block == 1:
                            continue

                    # Ensure piece can not move to position with piece with same color
                    if (x + dx, y + dy) in self.board.keys() and piece_color == self.board[(x + dx, y + dy)]['color']:
                        continue

                    # Special rules for King and Advisor
                    if piece_type in ('King', 'Advisor'):

                        # King and Advisor cannot go pass its 3x3 palace
                        if piece_color == 'red' and 3 <= x + dx <= 5 and 7 <= y + dy <= 9:
                            pass
                        elif piece_color == 'black' and 3 <= x + dx <= 5 and 0 <= y + dy <= 2:
                            pass
                        else:
                            is_valid = False

                        # King's movement cannot cause itself face the other King directly
                        if piece_type == 'King':
                            if piece_color == 'red' and x + dx == self.pieces[self.black_king_id][
                                0] or piece_color == 'black' and x + dx == self.pieces[self.red_king_id][0]:
                                is_valid = False
                                for other_x, other_y in self.pieces.values():
                                    if other_x == x + dx and (y + dy < other_y < self.pieces[self.red_king_id][1] or
                                                              self.pieces[self.red_king_id][1] < other_y < y + dy):
                                        is_valid = True
                                        break

                    # Special rules for Elephant
                    if piece_type == 'Elephant':
                        # Elephant cannot move if there is a block
                        if (x + dx / 2, y + dy / 2) in self.board.keys():
                            is_valid = False

                        # Elephant cannot go pass the river
                        if piece_color == 'black' and 0 <= y + dy <= 4:
                            pass
                        elif piece_color == 'red' and 5 <= y + dy <= 9:
                            pass
                        else:
                            is_valid = False

                    # Special rules for Chariot
                    if piece_type == 'Chariot':
                        if dy == 0:
                            if dx > 0:
                                for i in range(x + 1, x + dx):
                                    if (i, y) in self.board.keys():
                                        is_valid = False
                                        break
                            else:
                                for i in range(x + dx + 1, x):
                                    if (i, y) in self.board.keys():
                                        is_valid = False
                                        break
                        else:
                            if dy > 0:
                                for i in range(y + 1, y + dy):
                                    if (x, i) in self.board.keys():
                                        is_valid = False
                                        break
                            else:
                                for i in range(y + dy + 1, y):
                                    if (x, i) in self.board.keys():
                                        is_valid = False
                                        break

                    # Special rules for Horse
                    if piece_type == 'Horse':
                        # Horse cannot move if blocked
                        if dx == 1 or dx == -1:
                            if dy > 0:
                                if (x, y + 1) in self.board.keys():
                                    is_valid = False
                            else:
                                if (x, y - 1) in self.board.keys():
                                    is_valid = False

                        if dx == 2 or dx == -2:
                            if dx > 0:
                                if (x + 1, y) in self.board.keys():
                                    is_valid = False
                            else:
                                if (x - 1, y) in self.board.keys():
                                    is_valid = False

                    # Special rules for Cannon
                    if piece_type == 'Cannon':
                        count = 0
                        if dy == 0:
                            if dx > 0:
                                for i in range(x + 1, x + dx):
                                    if (i, y) in self.board.keys():
                                        count += 1
                            else:
                                for i in range(x + dx + 1, x):
                                    if (i, y) in self.board.keys():
                                        count += 1

                        else:
                            if dy > 0:
                                for i in range(y + 1, y + dy):
                                    if (x, i) in self.board.keys():
                                        count += 1

                            else:
                                for i in range(y + dy + 1, y):
                                    if (x, i) in self.board.keys():
                                        count += 1

                        if count == 0 and not (x + dx, y + dy) in self.board.keys():
                            pass
                        elif count == 1 and (x + dx, y + dy) in self.board.keys():
                            pass
                        else:
                            is_valid = False

                    # Special rules for Pawn
                    if piece_type == 'Pawn':
                        if piece_color == 'red':
                            if dy > 0 or y >= 5 and dx != 0:
                                is_valid = False
                        else:
                            if dy < 0 or y <= 4 and dx != 0:
                                is_valid = False

                    if is_valid:
                        valid_next_actions.append((info['id'], dx, dy))

        return valid_next_actions


def main():
    # Create the main window
    root = tk.Tk()
    root.title("Chinese Chess")
    root.geometry('800x800')
    root.resizable(False, False)
    my_game = ChineseChessGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
