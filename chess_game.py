import tkinter as tk
from tkinter import messagebox

class ChessBoard:
    def __init__(self, master):
        self.master = master
        self.master.title("Chess Game")
        self.selected_piece = None
        self.player_turn = 'white'
        
        # Colors for the board
        self.colors = ['#f0d9b5', '#b58863']  # Light and dark squares
        
        # Unicode chess pieces
        self.pieces = {
            'white': {'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘', 'P': '♙'},
            'black': {'K': '♚', 'Q': '♛', 'R': '♜', 'B': '♝', 'N': '♞', 'P': '♟'}
        }
        
        # Initialize the board (8x8 grid)
        self.board = {}
        self.buttons = {}
        
        # Configure window
        self.master.configure(bg='#302e2b')  # Dark background
        self.master.resizable(False, False)
        
        # Create the main frame with padding
        self.frame = tk.Frame(self.master, padx=20, pady=20, bg='#302e2b')
        self.frame.pack()
        
        # Create control panel
        self.control_panel = tk.Frame(self.master, bg='#302e2b', padx=20, pady=10)
        self.control_panel.pack()
        
        # Add New Game button
        self.new_game_btn = tk.Button(self.control_panel, text="New Game", 
                                    command=self.reset_game,
                                    bg='#4d4d4d', fg='white',
                                    font=('Arial', 12))
        self.new_game_btn.pack()
        
        self.init_board()
        self.update_turn_display()
        
    def init_board(self):
        # Create file (a-h) labels
        for col in range(8):
            label = tk.Label(self.frame, text=chr(97 + col), bg='#302e2b', fg='white')
            label.grid(row=8, column=col)
        
        # Create rank (1-8) labels
        for row in range(8):
            label = tk.Label(self.frame, text=str(8 - row), bg='#302e2b', fg='white')
            label.grid(row=row, column=8)
        
        # Create the chess board grid
        for row in range(8):
            for col in range(8):
                color = self.colors[(row + col) % 2]
                button = tk.Button(self.frame, width=3, height=1, bg=color,
                                 font=('Arial', 24), relief='flat',
                                 command=lambda r=row, c=col: self.button_click(r, c))
                button.grid(row=row, column=col)
                self.buttons[(row, col)] = button
        
        # Set up initial piece positions
        self.setup_pieces()
    
    def setup_pieces(self):
        # Initialize the piece positions dictionary
        self.board = {}
        
        # Set up pawns
        for col in range(8):
            self.board[(1, col)] = ('black', 'P')
            self.board[(6, col)] = ('white', 'P')
        
        # Set up other pieces
        piece_order = ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
        for col in range(8):
            self.board[(0, col)] = ('black', piece_order[col])
            self.board[(7, col)] = ('white', piece_order[col])
        
        self.update_display()
    
    def update_display(self):
        # Update the display of pieces on the board
        for row in range(8):
            for col in range(8):
                button = self.buttons[(row, col)]
                position = (row, col)
                color = self.colors[(row + col) % 2]
                
                # Reset button color and text
                button.config(bg=color, text='')
                
                # If there's a piece at this position, show it
                if position in self.board:
                    piece_color, piece_type = self.board[position]
                    unicode_piece = self.pieces[piece_color][piece_type]
                    button.config(text=unicode_piece,
                                fg='#000000' if piece_color == 'white' else '#000000')
    
    def button_click(self, row, col):
        position = (row, col)
        
        # Reset colors from previous highlights
        self.reset_colors()
        
        # If no piece is selected and the clicked square has a piece
        if self.selected_piece is None and position in self.board:
            color, piece = self.board[position]
            if color == self.player_turn:
                self.selected_piece = position
                self.buttons[position].config(bg='yellow')  # Highlight selected piece
                self.show_valid_moves(position)  # Show possible moves
        
        # If a piece is already selected
        elif self.selected_piece is not None:
            # If clicking the same square, deselect the piece
            if position == self.selected_piece:
                self.selected_piece = None
            
            # Try to move the piece
            if self.is_valid_move(self.selected_piece, position):
                self.make_move(self.selected_piece, position)
                    
    def make_move(self, start, end):
        """Execute a move and handle its consequences"""
        # Make the move
        self.board[end] = self.board[start]
        del self.board[start]
        
        # Reset selection and switch turns
        self.selected_piece = None
        self.player_turn = 'black' if self.player_turn == 'white' else 'white'
        
        # Update the display
        self.update_display()
        self.update_turn_display()
        
        # Check for checkmate or check
        if self.is_in_checkmate(self.player_turn):
            messagebox.showinfo("Checkmate!", 
                f"Checkmate! {('White' if self.player_turn == 'black' else 'Black')} wins!\n\nClick 'New Game' to play again.")
            self.reset_game()
        elif self.is_in_check(self.player_turn):
            messagebox.showinfo("Check!", 
                f"{self.player_turn.capitalize()}'s King is in check!\nFind a safe move!")
                    
    def reset_game(self):
        """Reset the game to its initial state"""
        self.board = {}
        self.selected_piece = None
        self.player_turn = 'white'
        self.setup_pieces()
        self.update_turn_display()
        
    def is_in_checkmate(self, color):
        """Check if the given color is in checkmate"""
        if not self.is_in_check(color):
            return False
            
        # Try all possible moves for all pieces
        for start_pos, (piece_color, piece_type) in dict(self.board).items():
            if piece_color == color:
                for end_row in range(8):
                    for end_col in range(8):
                        end_pos = (end_row, end_col)
                        if self.is_valid_move(start_pos, end_pos):
                            # Try the move
                            original_board = dict(self.board)
                            if end_pos in self.board:
                                captured_piece = self.board[end_pos]
                            self.board[end_pos] = self.board[start_pos]
                            del self.board[start_pos]
                            
                            # If this move gets us out of check, restore board and return False
                            if not self.is_in_check(color):
                                self.board = original_board
                                return False
                                
                            # Restore the board
                            self.board = original_board
        
        return True
        
    def update_turn_display(self):
        """Update the turn indicator"""
        if hasattr(self, 'turn_label'):
            self.turn_label.destroy()
        self.turn_label = tk.Label(self.frame, 
                                 text=f"{self.player_turn.capitalize()}'s turn",
                                 bg='#302e2b', fg='white',
                                 font=('Arial', 14))
        self.turn_label.grid(row=9, column=0, columnspan=8)
    
    def reset_colors(self):
        """Reset all square colors to their original state"""
        for row in range(8):
            for col in range(8):
                self.buttons[(row, col)].config(bg=self.colors[(row + col) % 2])
    
    def show_valid_moves(self, position):
        """Highlight valid moves for the selected piece"""
        for row in range(8):
            for col in range(8):
                target = (row, col)
                if self.is_valid_move(position, target):
                    if target in self.board:
                        self.buttons[target].config(bg='red')  # Capture moves
                    else:
                        self.buttons[target].config(bg='lightgreen')  # Valid moves
    
    def is_in_check(self, color):
        """Determine if the given color's king is in check"""
        # Find the king's position
        king_pos = None
        for pos, piece in self.board.items():
            if piece == (color, 'K'):
                king_pos = pos
                break
        
        if not king_pos:
            return False
        
        # Check if any opponent's piece can capture the king
        opponent_color = 'black' if color == 'white' else 'white'
        for pos, piece in self.board.items():
            if piece[0] == opponent_color:
                if self.is_valid_move(pos, king_pos):
                    return True
        
        return False
    
    def is_valid_move(self, start, end):
        if end in self.board and self.board[end][0] == self.player_turn:
            return False
            
        start_row, start_col = start
        end_row, end_col = end
        piece_color, piece_type = self.board[start]
        
        # Calculate movement distances
        row_diff = end_row - start_row
        col_diff = end_col - start_col
        
        # Pawn movement
        if piece_type == 'P':
            direction = -1 if piece_color == 'white' else 1
            
            # Regular move
            if col_diff == 0 and not end in self.board:
                if row_diff == direction:
                    return True
                # First move can be two squares
                if (start_row == 1 and piece_color == 'black') or (start_row == 6 and piece_color == 'white'):
                    if row_diff == 2 * direction and not (start_row + direction, start_col) in self.board:
                        return True
            
            # Capture move
            if abs(col_diff) == 1 and row_diff == direction:
                if end in self.board and self.board[end][0] != piece_color:
                    return True
            return False
            
        # Rook movement
        if piece_type == 'R':
            return self.is_clear_path(start, end) and (row_diff == 0 or col_diff == 0)
            
        # Knight movement
        if piece_type == 'N':
            return (abs(row_diff) == 2 and abs(col_diff) == 1) or (abs(row_diff) == 1 and abs(col_diff) == 2)
            
        # Bishop movement
        if piece_type == 'B':
            return self.is_clear_path(start, end) and abs(row_diff) == abs(col_diff)
            
        # Queen movement
        if piece_type == 'Q':
            return self.is_clear_path(start, end) and (row_diff == 0 or col_diff == 0 or abs(row_diff) == abs(col_diff))
            
        # King movement
        if piece_type == 'K':
            return abs(row_diff) <= 1 and abs(col_diff) <= 1
            
        return False
        
    def is_clear_path(self, start, end):
        """Check if there are any pieces blocking the path between start and end positions"""
        start_row, start_col = start
        end_row, end_col = end
        
        row_diff = end_row - start_row
        col_diff = end_col - start_col
        
        # Horizontal movement
        if row_diff == 0:
            step = 1 if col_diff > 0 else -1
            for col in range(start_col + step, end_col, step):
                if (start_row, col) in self.board:
                    return False
                    
        # Vertical movement
        elif col_diff == 0:
            step = 1 if row_diff > 0 else -1
            for row in range(start_row + step, end_row, step):
                if (row, start_col) in self.board:
                    return False
                    
        # Diagonal movement
        else:
            row_step = 1 if row_diff > 0 else -1
            col_step = 1 if col_diff > 0 else -1
            current_row = start_row + row_step
            current_col = start_col + col_step
            
            while current_row != end_row and current_col != end_col:
                if (current_row, current_col) in self.board:
                    return False
                current_row += row_step
                current_col += col_step
                
        return True

def main():
    root = tk.Tk()
    root.title("Chess Game")
    game = ChessBoard(root)
    root.mainloop()

if __name__ == "__main__":
    main()
