from tkinter import filedialog

from .renderer import (
    BooleanVar,
    DoubleVar,
    Font,
    Image,
    IntVar,
    StringVar,
)

# FileDialog
def select_file(**kwargs): return filedialog.askopenfilename(**kwargs)
def select_directory(**kwargs): return filedialog.askdirectory(**kwargs)
