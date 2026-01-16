import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.append(root_dir)

import lazytkinter as ltk

ltk.set_theme(ltk.Theme.Gruvbox) # set theme

# create program
app = ltk.Application()

# creat event
def on_click():
    print("click!")

# build UI
app.window_size( # set window size
        "400x300"
    ).window_title( # set title
        "My first app"
    ).column( # vertical arrangment
        ltk.Button() 
            .margin((100, 150)) 
            .weight(0) 
            .text("Click!")
            .event(on_click),
    )

# run
app.run()