import lazytkinter as ltk

ltk.set_theme(ltk.Theme.Gruvbox)  # set theme

# create program
app = ltk.Application()

# create event
def on_click(value=None):
    print("click!")

# build UI
app.size("small").window_title(  # set window size & title
        "My first app"
    ).center().column(  # center on both axes at the window root
        ltk.Button().text("Click!").event(on_click),
    )

# run
app.run()
