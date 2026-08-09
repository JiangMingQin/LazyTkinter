import lazytkinter as ltk

ltk.set_theme(ltk.Theme.Gruvbox)
app = ltk.Application()

# declare variables
user_input_var = ltk.StringVar()  # to store user input
welcome_msg_var = ltk.StringVar()  # to store welcome message

# event functions
def on_login_click(value=None):
    name = user_input_var.get()
    if name:
        welcome_msg_var.set(f"Welcome back, {name}!")
    else:
        welcome_msg_var.set("Please enter a username!")

def on_cancel_click(value=None):
    # clear input and result message
    user_input_var.set("")
    welcome_msg_var.set("")

# build UI
app.size("small").window_title("Login Example").gap(16).center().column(
    # title label
    ltk.Label().text("User Login").font(family="Arial", size=20, weight="bold"),
    # main content
    ltk.Column().padding(10).gap(10).align("center").add(
        # Entry: user_input_var
        ltk.Entry()
            .height(35)
            .width(400)
            .radius(100)
            .variable(user_input_var),  # <--- bind variable
        # Row: Login and Cancel buttons
        ltk.Row().justify("center").gap(10).add(
            # Login Button
            ltk.Button()
                .text("Login")
                .radius(100)
                .event(on_login_click),  # <--- bind function
            # Cancel Button
            ltk.Button()
                .text("Cancel")
                .fg_color("gray")
                .radius(100)
                .event(on_cancel_click),
        ),
    ),
    # result message label: welcome_msg_var
    ltk.Label().variable(welcome_msg_var),  # <--- bind variable, auto refresh
)

app.run()
