import cv2 as cv
import numpy as np 
import pytesseract

class ImageMethods():
    TESSERACT_CONFIG = '--oem 3 --psm 6 outputbase digits'   

    @staticmethod
    def get_shape(contour):                                 # IA NUMARUL DE COLTURI
        perimeter = cv.arcLength(contour, True)
        points_number = cv.approxPolyDP(contour, 0.02 * perimeter, True)
        return len(points_number)       


    @staticmethod
    def remove_duplicate_contours(contours, poz):           # ELIMINA DUPLICATELE   
        corners = contours[poz]
        corners = corners.tolist()

        xmax =-1
        ymax=-1
        xmin=1000000
        ymin=1000000
        for corner in corners:
            if corner[0][1] > xmax:
                xmax = corner[0][1]
            if corner[0][1] < xmin:
                xmin = corner[0][1]
            if corner[0][0] > ymax:
                ymax = corner[0][0]
            if corner[0][0] < ymin:
                ymin = corner[0][0]

        corners = [xmin, xmax, ymin, ymax] 
        # AXA X -> 1; AXA Y -> 0
        # 0 stanga sus
        # 1 stanga jos
        # 2 dreapta jos
        # 3 dreapta sus
        return corners


    @staticmethod
    def read_digit(img):
        img = cv.cvtColor(img, code=cv.COLOR_BGR2GRAY)
        cv.imshow('12345', img)
        cv.imwrite('img.png', img)
        text = pytesseract.image_to_string(image=img, config='--psm 6 digits')
        
        if text[0].isnumeric(): text = int(text)
        else: text = 0
        return text

    

class Sudoku():
    def __init__(self, image, contours=None, hierarchy=None, 
                    matrix=np.zeros(shape=(9,9), dtype='int')):
        self.image = cv.imread(image)                       # LUAM IMAGINEA DIN PATH
        self.contours = contours                            # CONTURURILE GASITE IN IMAGINE
        self.hierarchy = hierarchy                          # RANGUL CONTURURILOR -> [Next, Previous, First_Child, Parent]
        self.matrix = matrix                                # MATRICEA JOCULUI
        pytesseract.pytesseract.tesseract_cmd = r'E:\Fisiere\code\Useful\pytesseract\tesseract.exe'
     

    def get_edges(self, nrblur=0, nrkernel=0):
        image_aux = self.image
        if nrblur!=0:
            image_aux = cv.GaussianBlur(self.image, (3,3), 1)  
        
        canny = cv.Canny(image_aux,0,50)                        
        if nrkernel!=0:                 
            kernel = np.ones((nrkernel,nrkernel))                             
            canny = cv.dilate(canny, kernel)                       

        self.contours, self.hierarchy = cv.findContours(canny, mode=cv.RETR_TREE, method=cv.CHAIN_APPROX_SIMPLE)
        self.hierarchy = self.hierarchy[0]
        #cv.imshow(f'{nrkernel}',cv.resize(canny, (700,700)))


    def validate_sudoku(self):          # verifica daca exista un patrat cu 81 de copii (patrate)
        nr = [0 for i in range(len(self.hierarchy))]
        for cnt in self.hierarchy:                                                  # cnt[3] este parintele conturului din ierarhie
            if cnt[3]!=-1 and ImageMethods.get_shape(self.contours[cnt[3]])==4:     # daca cnt e patrat, crestem nr pt parintele sau
                nr[cnt[3]]+=1

        # cel mai mare dintre toate patratele cu 81 de copii    
        max_area = -1
        poz = -1
        for i in range(len(nr)):                     
            if nr[i] == 81: # am sters nr[i] == 9
                area = cv.contourArea(self.contours[i])
                if area > max_area:
                    max_area = area
                    poz = i

        # returneaza pozitia celui mai mare patrat cu 81 de copii in self.contours;
        return poz          # daca poz == -1 e invalid
                            # daca poz >= 0 e valid


    def crop_image(self, poz, rectangle = False):
        # crop image
        corners = ImageMethods.remove_duplicate_contours(self.contours, poz)   
        img = self.image  
        if rectangle:   
            img = img[corners[0]:corners[1], corners[2]:corners[3]]
            img = cv.rectangle(img, (0,0), (img.shape[1]-1, img.shape[0]-1), color=(0,0,0), thickness=1) #in caz ca se da crop la border
        else:
            img = img[corners[0]+2:corners[1]-2, corners[2]+2:corners[3]-2]
        cv.imshow(f'{poz}', img)
        return img


    def automatic_edge_detection(self):        
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
        main_square_index = [i for i in range(len(self.hierarchy)) if self.hierarchy[i][3]==-1][0]      # IA INDEXUL PATRATULUI PRINCIPAL
        children_indexes = [i for i in range(len(self.hierarchy)) if self.hierarchy[i][3] == main_square_index] # CREEAZA O LISTA CU INDEXURILE
        children_indexes.sort(key=None, reverse=True)                                                           #  COPIILOR PATRATULUI
        i=0
        j=0
        for child_index in children_indexes:                        #INTRODUCEM ELEMENTELE DIN FIECARE PATRAT IN MATRICE
            cell_img = self.crop_image(child_index)
            cv.imshow("12313131", cell_img)
            self.matrix[i,j] = ImageMethods.read_digit(cell_img)
            j+=1
            if j%9==0:
                j=0
                i+=1
        

    def solve(self):
        pass



def backend():
    sudoku = Sudoku('images/sudoku6.png')
    cv.imshow('test',sudoku.image)
    sudoku.automatic_edge_detection()
    poz = sudoku.validate_sudoku()
    if poz!=-1:
        sudoku.image = sudoku.crop_image(poz, True)

        sudoku.automatic_edge_detection()
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
    # REPARA TEXT RECOGNITIONUL
    # VEZI DE CE (DACA) SE AMESTECA INTRE ELE CELULELE