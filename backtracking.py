
class Solver:
    def __init__(self, puzzle):
        self.puzzle = puzzle

    def find_next_empty(self):
        for r in range(9):
            for c in range(9): 
                if self.puzzle[r][c] == 0:
                    return r, c

        return None, None  

    def is_valid(self, guess, row, col):
        row_vals = self.puzzle[row]
        if guess in row_vals:
            return False 

        col_vals = [self.puzzle[i][col] for i in range(9)]
        if guess in col_vals:
            return False

        row_start = (row // 3) * 3 
        col_start = (col // 3) * 3

        for r in range(row_start, row_start + 3):
            for c in range(col_start, col_start + 3):
                if self.puzzle[r][c] == guess:
                    return False

        return True

    def solve_sudoku(self):
        row, col = self.find_next_empty()

        if row is None:  
            return True 

        for guess in range(1, 10): 
            if self.is_valid( guess, row, col):
                self.puzzle[row][col] = guess
                if self.solve_sudoku():
                    return True

            self.puzzle[row][col] = 0

        return False