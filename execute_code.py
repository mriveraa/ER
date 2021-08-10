# -*- coding: utf-8 -*-
"""
Created on Wed Jun 30 17:04:13 2021

@author: mriveraa
"""
# Import the function
import run_main as run
import tkinter
from tkinter.filedialog import askdirectory

#Open folder GUI and return in a string the Path
root = tkinter.Tk()
folder = askdirectory()
print("\nThe folder selected is: " + folder)
root.destroy()


# Run function
# Folder with input data
run.simulation_er(folder)


