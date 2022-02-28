from fileinput import filename
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
import tkinter
from tkinter.messagebox import showinfo, showwarning
from PIL import Image, ImageTk
import sudoku

# create the root window
root = tk.Tk()
root.title('Convenient Sudoku Solver')
root.resizable(False, False)
root.geometry('400x275')




def select_file():
	filename, outcome=0, 0

	filetypes = (
		('Toate imaginile', '*.png; *.jpg'),
		('Fisiere .png', '*.png'),
		('Fisiere .jpg', '*.jpg')
	)

	filename = fd.askopenfilename (
		title = 'Selecteaza o imagine',
		initialdir = '/',
		filetypes=filetypes
	)

	

	print(filename)
	if filename: 
		root.withdraw()
		outcome = sudoku.backend(filename)

	
	if outcome == 'sudoku_invalid':
		showwarning(title=f'{outcome}', message='Puzzle-ul nu are solutii')
	elif outcome == 'image_invalid':
		showwarning(title=f'{outcome}', message='Nu a fost detectat un puzzle sudoku in imagine')

	root.deiconify()
	
	
def help_function():
	showinfo(title=f'Informatii', message='Cum se foloseste aplicatia?\nE foarte simplu. Doar apasa pe butonul de incarcare imagine, selecteaza o imagine cu un puzzle sudoku nerezolvat, iar apoi lasa programul sa faca toata magia.\n\nFormate acceptate:\npng, jpg')	


style = ttk.Style()
 

style.configure('W.TButton', font =
               ('arial', 10, ),
                foreground = '#152245',
				background = '#4d86d6'
				)


open_button = ttk.Button(
    root,
    text='Incarca Imaginea',
	padding= (0,10,0,10),
	style = "W.TButton",
	width=15,
    command=select_file
)

help_button = ttk.Button (
	root,
	text = 'Informatii',
	padding = (0,10,0,10),
	style = "W.TButton",
	width=15,
	command = help_function
)

logo_image = Image.open(f'dependencies/logo.png')
logo_image = ImageTk.PhotoImage(logo_image)

title_label = ttk.Label(
	root,
	#text = 'Convenient Sudoku Solver',
	image = logo_image,
	font = 'arial 20 bold',
	padding = 10
)

empty_label = ttk.Label(root,text = "",	padding = 10)



#ttk.Label(root,text = "",padding = 2).grid(row=0,column=0)
title_label.place(x=62,y=0)
open_button.place(x=75,y=190)
help_button.place(x=205,y=190)




# run the application
root.mainloop()
