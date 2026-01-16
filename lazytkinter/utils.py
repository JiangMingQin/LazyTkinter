import customtkinter as ctk
from tkinter import filedialog

# Variables
StringVar = ctk.StringVar
IntVar = ctk.IntVar
DoubleVar = ctk.DoubleVar
BooleanVar = ctk.BooleanVar

# Resources
Image = ctk.CTkImage 
Font = ctk.CTkFont

# Toplevel Window
# Toplevel = ctk.CTkToplevel

# FileDialog
from tkinter import filedialog
def select_file(**kwargs): return filedialog.askopenfilename(**kwargs)
def select_directory(**kwargs): return filedialog.askdirectory(**kwargs)