import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.append(root_dir)

import lazytkinter as ltk


ltk.set_theme(ltk.Theme.Gruvbox)
app = ltk.Application()

# declare variables
user_input_var = ltk.StringVar()  # to store user input
welcome_msg_var = ltk.StringVar()  # to store welcome message

# event functions
def on_login_click():
    name = user_input_var.get()
    if name:
        welcome_msg_var.set(f"Welcome back, {name}!") 
    else:
        welcome_msg_var.set("Please enter a username!")

def on_cancel_click():
    # clear input and result message
    user_input_var.set("")
    welcome_msg_var.set("")

# build Ui
app.window_size("400x300").window_title("Login Example").column(
    ltk.Empty(), # empty space at top
    # title label
    ltk.Label().text("User Login").font(("Arial", 20, "bold")).weight(0),
    # main content
    ltk.Column().padding(10).margin_x(20).spacing(10).transparent(True).add(
        # Entry: user_input_var
        ltk.Entry()
            .height(35)
            .radius(100)
            .weight(0)
            .variable(user_input_var), # <--- bind variable
        # Row: Login and Cancel buttons
        ltk.Row().height(40).padding(5).weight(0).transparent(True).add(
            # Login Button
            ltk.Button()
                .margin_x(5)
                .radius(100)
                .event(on_login_click), # <--- bind function
            # Cancel Button
            ltk.Button()
                .margin_x(5)
                .radius(100)
                .text("Cancel")
                .fg_color("gray")
                .event(on_cancel_click),
        ),
        # result message label: welcome_msg_var
        ltk.Label()
            .weight(0)
            .variable(welcome_msg_var) # <--- bind variable, auto refresh
        ),
        ltk.Empty() # empty space at bottom
    )

app.run()