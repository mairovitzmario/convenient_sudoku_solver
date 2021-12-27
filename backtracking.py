solved_matrix = 0

class Solve:
    def __init__(self, matrix):
        self.matrix = matrix


    def valid(self, x, y):
        # se testeaza pe linie sa nu existe de 2 ori acelasi numar
        for j in range(9):
            if self.matrix[x,j] == self.matrix[x,y] and j!=y:
                return False

        # se testeaza pe coloana sa nu existe de 2 ori acelasi numar
        for i in range(9):
            if self.matrix[i,y] == self.matrix[x,y] and i!=x:
                return False
        
        #se testeaza in patrat sa nu existe de 2 ori acelasi numar
        start_i = int(x/3)*3
        start_j = int(y/3)*3
        for i in range(start_i, start_i+2):
            for j in range(start_j, start_j+2):
                if (self.matrix[x,y] == self.matrix[i,j]) and (x!=i or y!=j):
                    return False

        return True


    def solution(self, x, y):
        if x==8 and y==8:
            return True
        else:
            return False


    def backtracking(self, x=0, y=0):
        if self.matrix[x,y] == 0:
            for i in range(1,10):
                self.matrix[x,y]=i
                if self.valid(x, y) == True:
                    if self.solution(x, y) == True:
                        solved_matrix = self.matrix
                        print(solved_matrix)
                        return
                    else:
                        if y==8:
                            self.backtracking(x+1, 0)
                        else:
                            self.backtracking(x, y+1)
            self.matrix[x,y] = 0

        else:
            if self.solution(x, y) == True:
                solved_matrix = self.matrix
                print(solved_matrix)
                return
            else:
                if y==8:
                    self.backtracking(x+1, 0)
                else:
                    self.backtracking(x, y+1)

    def get_result(self):
        print(solved_matrix)
        return solved_matrix