import cv2 as cv
import numpy as np 
import pytesseract

class ImageMethods():
    TESSERACT_CONFIG = '--oem 3 --psm 6 outputbase digits'   

    @staticmethod
    def get_shape(contour):                                 
        # RETURNEAZA NUMARUL DE COLTURI
        perimeter = cv.arcLength(contour, True)
        points_number = cv.approxPolyDP(contour, 0.02 * perimeter, True)
        return len(points_number)       


    @staticmethod
    def remove_duplicate_contours(contours, poz):           
        corners = contours[poz]
        corners = corners.tolist()

        xmax, ymax =-1, -1
        xmin, ymin=1000000, 1000000
        for corner in corners:
            if corner[0][1] > xmax:
                xmax = corner[0][1]
            if corner[0][1] < xmin:
                xmin = corner[0][1]
            if corner[0][0] > ymax:
                ymax = corner[0][0]
            if corner[0][0] < ymin:
                ymin = corner[0][0]
        # AXA X -> 1; AXA Y -> 0

        # stanga sus -> xmin, ymin
        # stanga jos -> xmin, ymax
        # dreapta jos -> xmax, ymax
        # dreapta sus -> xmax, ymin
        corners = [xmin, xmax, ymin, ymax] 
        return corners


    @staticmethod
    def read_digit(img):
        img = cv.cvtColor(img, code=cv.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(image=img, config='--psm 6 digits')
        
        if text[0].isnumeric(): text = int(text)
        else: text = 0
        return text



class Cell():                                           
    # CLASA MENITA PENTRU A TINE DETALIILE IMPORTANTE ALE UNEI CELULE DIN CELE 81
    def __init__(self, x, y, index):
        self.x = x          # COORDONATA X(MIN)
        self.y = y          # COORDONATA Y(MIN)
        self.index = index  # INDEXUL IN VECTORUL DE CONTURURI



class Sudoku():
    def __init__(self, image, contours=None, hierarchy=None, 
                    matrix=np.zeros(shape=(9,9), dtype='int')):
        self.image = cv.imread(image)                       # LUAM IMAGINEA DIN PATH
        self.contours = contours                            # CONTURURILE GASITE IN IMAGINE
        self.hierarchy = hierarchy                          # [Next, Previous, First_Child, Parent]
        self.matrix = matrix                                # MATRICEA JOCULUI
        pytesseract.pytesseract.tesseract_cmd = r'E:\Fisiere\code\Useful\pytesseract\tesseract.exe'
     

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
        blank = np.zeros(self.image.shape, self.image.dtype)
        i, j = 0, 0 
        for cell in cells:                       
            cell_index = cell.index
            cell_img = self.crop_image(cell_index)
            self.matrix[i,j] = ImageMethods.read_digit(cell_img)
            j+=1
            if j%9==0:
                j=0
                i+=1
        
        # AFISARE REZULTAT
        i, j = 0, 0 
        for cell in cells:
            cell_index = cell.index
            corners = ImageMethods.remove_duplicate_contours(self.contours, cell_index)
            cv.putText(blank, f'{self.matrix[j,i]}', (corners[0]+5, corners[3]-5), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,255))
            j+=1
            if j%9==0:
                j=0
                i+=1

        cv.drawContours(blank, self.contours, -1, (0,255,0),2)
        cv.imshow('der',blank)


    def solve(self):
        pass



def backend():
    sudoku = Sudoku('images/sudoku1.png')
    cv.imshow('test',sudoku.image)
    sudoku.automatic_get_edges()
    poz = sudoku.validate_sudoku()
    if poz!=-1:
        sudoku.image = sudoku.crop_image(poz, True)

        sudoku.automatic_get_edges()
        ok = sudoku.validate_sudoku()
        
        if ok!=-1:
            cv.imshow('d',sudoku.image)
            sudoku.create_matrix()
            print(sudoku.matrix)
    else:
        print('IMAGINE INVALIDA! INCARCATI O ALTA IMAGINE.')
    cv.waitKey(0)



if __name__ == '__main__':
    backend()
    # FA TEXT RECOGNITIONUL MAI ACCURATE
    # erori:
    # test 4 nu detecteaza un '1'
    # test 5 nu detecteaza un '5'