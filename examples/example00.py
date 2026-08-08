import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.append(root_dir)

import lazytkinter as ltk

ltk.set_theme(ltk.Theme.Gruvbox)  # set theme

# create program
app = ltk.Application()

# create event
def on_click():
    print("click!")

# build UI
app.size("small").window_title(  # set window size & title
        "My first app"
    ).center().column(  # center on both axes at the window root
        ltk.Button().text("Click!").event(on_click),
    )

# run
app.run()
