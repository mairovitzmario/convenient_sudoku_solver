from fileinput import filename
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
import tkinter
from tkinter.messagebox import showinfo
import sudoku

# create the root window
root = tk.Tk()
root.title('Convenient Sudoku Solver')
root.resizable(False, False)




def select_file():
	filename=0
	outcome_message = ''

	filetypes = (
		('Fisiere .png', '*.png'),
		('Fisiere .jpeg', '*.jpeg'),
		('Fisiere .jpg', '*.jpg'),
        ('Toate fisierele', '*.*')
	)

	filename = fd.askopenfilename (
		title = 'Selecteaza o imagine',
		initialdir = '/',
		filetypes=filetypes
	)

	

	print(filename)
	if filename: outcome = sudoku.backend(filename)
	
	if outcome == 'sudoku_invalid':
		showinfo(title=f'Eroare {outcome}', message='Puzzle-ul nu are solutii')
	elif outcome == 'image_invalid':
		showinfo(title=f'Eroare {outcome}', message='Nu a fost detectat un puzzle Sudoku in imagine')

	
	
	

# open button
open_button = ttk.Button(
    root,
    text='Incarca imagine',
	padding= 15,
    command=select_file
)

title_label = ttk.Label(
	root,
	text = 'Convenient Sudoku Solver',
	font = 'arial 20 bold',
	padding = 10
)

empty_label = ttk.Label(
	root,
	text = "",
	padding = 10
)



#ttk.Label(root,text = "",padding = 2).grid(row=0,column=0)
title_label.grid(row=1,column=0)
open_button.grid(row=2,column=0)
empty_label.grid(row=3,column=0)

# run the application
root.mainloop()
