import cv2 as cv
import numpy as np 
import pytesseract
from imagemethods import ImageMethods, Cell
import backtracking
import threading

class Sudoku():
    def __init__(self, image, contours=None, hierarchy=None, 
                    matrix=np.zeros(shape=(9,9), dtype='int'),
                    solved_matrix=np.zeros(shape=(9,9), dtype='int'), solved_image=cv.imread(f'dependencies/sudoku_grid.png')):
        self.image = cv.imread(image)                       # LUAM IMAGINEA DIN PATH
        self.contours = contours                            # CONTURURILE GASITE IN IMAGINE
        self.hierarchy = hierarchy                          # [Next, Previous, First_Child, Parent]
        self.matrix = matrix                                # MATRICEA JOCULUI
        self.solved_matrix = solved_matrix
        self.solved_image = solved_image
        pytesseract.pytesseract.tesseract_cmd = 'dependencies/pytesseract/tesseract.exe'
     

    def get_edges(self, nrblur=0, nrkernel=0):
        # ACTUALIZEAZA CONTURURILE
        image_aux = self.image
        if nrblur!=0:
            image_aux = cv.GaussianBlur(self.image, (3,3), 1)  
        
        canny = cv.Canny(image_aux,0,50)                        
        if nrkernel!=0:                 
            kernel = np.ones((nrkernel,nrkernel))                             
            canny = cv.dilate(canny, kernel)                       

        self.contours, self.hierarchy = cv.findContours(canny, mode=cv.RETR_TREE, method=cv.CHAIN_APPROX_SIMPLE)
        self.hierarchy = self.hierarchy[0]


    def validate_sudoku(self):          
        # verifica daca exista un patrat cu 81 de copii (patrate)
        #   si ii returneaza indexul din self.contours[]
        nr = [0 for _ in range(len(self.hierarchy))]
        for cnt in self.hierarchy: 
            cnt_parent = cnt[3]                       
            if cnt_parent!=-1 and ImageMethods.get_shape(self.contours[cnt_parent])==4:             
                nr[cnt_parent]+=1

        # cel mai mare dintre toate patratele cu 81 de copii    
        max_area, poz = -1, -1
        for i in range(len(nr)):                     
            if nr[i] == 81: 
                area = cv.contourArea(self.contours[i])
                if area > max_area:
                    max_area = area
                    poz = i

        return poz          # daca poz == -1 e invalid
                            # daca poz >= 0 e valid


    def crop_image(self, poz, rectangle = False):
        corners = ImageMethods.remove_duplicate_contours(self.contours, poz)   
        img = self.image  
        if rectangle:   # True -> creeaza inca un patrat, False -> da crop la patratul existent
            img = img[corners[0]:corners[1], corners[2]:corners[3]]
            img = cv.rectangle(img, (0,0), (img.shape[1]-1, img.shape[0]-1), color=(0,0,0), thickness=1) 
        else:
            img = img[corners[0]+2:corners[1]-2, corners[2]+2:corners[3]-2]
        #cv.imshow(f'{poz}', img)
        return img


    def automatic_get_edges(self):        
        # detecteaza conturul pt sudoku automat, modificand valorile limpezirii imaginilor
        # actualizeaza automat conturul [vectorii self.contours si self.hierarchy]
        for i in range(1,11, +2):
            nrk = i
            self.get_edges(0, nrk)
            if self.validate_sudoku() !=-1:
                return True
            self.get_edges(1, nrk)
            if self.validate_sudoku() !=-1:
                return True
        return False                            


    def read_digit(self, cell_contour_index, i, j):
        # prelucram imaginea celulei, apoi citim textul din ea
        img = self.crop_image(cell_contour_index)
        img = cv.cvtColor(img, code=cv.COLOR_BGR2GRAY)
        resize_multiplier = cv.contourArea(self.contours[cell_contour_index]) / 2000                # 2000 -> 1.0 multiplier
        resize_multiplier = 1 / resize_multiplier
        #resize_multiplier = 1
        if resize_multiplier > 1.5: resize_multiplier = 1.5
        if resize_multiplier < 0.5 : resize_multiplier = 0.5
        #print(resize_multiplier)

        img = cv.resize(img, None, fx=resize_multiplier, fy=resize_multiplier, interpolation=cv.INTER_CUBIC)
        text = pytesseract.image_to_string(image=img, config='--psm 6 digits')
        
        if text[0].isnumeric(): text = int(text[0])
        else: text = 0

        self.matrix[i,j] = int(text)
 


    def create_matrix(self):
        # CREEAZA MATRICEA PT SUDOKU, REZOLVAND SI NISTE PROBLEME DIN LIBRARIA OPENCV :|

        main_square_index = [i for i in range(len(self.hierarchy)) if self.hierarchy[i][3]==-1][0]      
        cells_indexes = [i for i in range(len(self.hierarchy)) if self.hierarchy[i][3] == main_square_index] 
        
        # ORDONAM TOATE CELULELE IN FUNCTIE DE COORDONATE, DEOARECE UNEORI OPENCV NU LE ORDONEAZA BINE
        cells = [] 
        for cell_index in cells_indexes:  
            cell_coords = ImageMethods.remove_duplicate_contours(self.contours, cell_index)
            cells.append(Cell(x=cell_coords[0], y=cell_coords[2], index=cell_index))

        cells.sort(key= lambda cell: cell.x)    
        for i in range(9):
            cells_sample = cells[9*i:9*(i+1)]
            cells_sample.sort(key= lambda cell: cell.y)
            cells[9*i:9*(i+1)] = cells_sample   

        #INTRODUCEM ELEMENTELE DIN FIECARE CELULA IN MATRICE
        threads = []
        i, j = 0, 0 
        for cell in cells:                       
            #print(cv.contourArea(self.contours[cell.index]))
            #cv.imshow(f'{9*i+j}', cell_img)
            t = threading.Thread( target=self.read_digit, args=[cell.index, i, j])
            t.start()
            threads.append(t)
            j+=1
            if j%9==0:
                j=0
                i+=1
        for t in threads:
            t.join()

        #AFISARE REZULTAT
        blank = np.zeros(self.image.shape, self.image.dtype)
        cv.drawContours(blank, self.contours, -1, (255,0,0),2)
        i, j = 0, 0 
        for cell in cells:
            cell_index = cell.index
            corners = ImageMethods.remove_duplicate_contours(self.contours, cell_index)
            if self.matrix[j,i]: cv.putText(blank, f'{self.matrix[j,i]}', (corners[0]+5, corners[3]-5), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,255))
            j+=1
            if j%9==0:
                j=0
                i+=1

        
        #cv.imshow('der',blank)


    def solve(self):
        solver_sudoku = backtracking.Solver(self.matrix)
        solver_sudoku.solve_sudoku()
        #print(solver_sudoku.solve_sudoku())
        self.solved_matrix = solver_sudoku.puzzle

    def create_solved_image(self):
        self.solved_image=cv.imread(f'dependencies/sudoku_grid.png')
        column_height, row_length = 46,10
        for row in self.solved_matrix:
            row_text = ""
            for digit in row:
                row_text+= str(digit) + " "
            cv.putText(img=self.solved_image, text=row_text, org=(row_length, column_height) ,fontFace=cv.FONT_HERSHEY_DUPLEX , fontScale=1.4, color=(0,0,0) )

            column_height+=46
            if column_height>100:
                column_height+=1
            #cv.imshow(f"{column_height} +  {row_length}",self.solved_image)





def backend(image_name):
    sudoku = Sudoku(image_name)
    #sudoku = Sudoku(f'images/{image_name}.png')
    #cv.imshow('test',sudoku.image)
    sudoku.automatic_get_edges()
    poz = sudoku.validate_sudoku()
    if poz!=-1:
        sudoku.image = sudoku.crop_image(poz, True)

        sudoku.automatic_get_edges()
        ok = sudoku.validate_sudoku()
        
        if ok!=-1:
            #cv.imshow('d',sudoku.image)
            sudoku.create_matrix()
            #print(sudoku.matrix)
            #print('..........................')
            sudoku.solve()       
            sudoku.create_solved_image()
            #print(sudoku.solved_matrix)
            cv.imshow(f"{image_name}",sudoku.solved_image)
            cv.waitKey(0)  
            return sudoku.solved_matrix     
        else:
            return 'sudoku_invalid'
            #print('SUDOKU NU POATE FI REZOLVAT!')

    else:
        return 'image_invalid'
        #print('IMAGINE INVALIDA! INCARCATI O ALTA IMAGINE.')
    #cv.waitKey(0)



if __name__ == '__main__':
    print(backend(f'images/sudoku1.png'))
    # POSIBILA EROARE:
    # IMAGINEA SE DILATEAZA AUTOMAT ( DILATAREA INCEPE DE LA 1, NU DE LA 0 )
    # DE CE NU CRED CA TB REPARAT:
    # DACA IMAGINEA ESTE ATAT DE INGHESUITA INCAT NU RECUNOASTE SUDOKU DE LA KERNEL 1 PT DILATARE,
    # ATUNCI PROBABIL NU AR RECUNOASTE FIDEL TEXTUL
    # AR FI O SOLUTIE SA DAU STRETCH LA IMAGINE (DE LA INCEPUT) LA O POZITIE FINALA RELATIVA
    # DA E PREA MULTA BATAIE DE CAP SI N ARE ROST PT ATESTATUL ASTA
    # MAJORITATEA EXEMPLELOR MERG BN