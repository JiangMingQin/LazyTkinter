import lazytkinter as ltk

ltk.set_theme(ltk.Theme.Gruvbox)  # set theme

# create program
app = ltk.Application()

# counter state
count = 0

# event: every click increments the counter label via the typed access channel
def on_click(value=None):
    global count
    count += 1
    app.config(ltk.Label).aim_id("count").text(f"{count}")

# build UI
app.size("small").window_title("Counter").center().gap(10).column(
    ltk.Label().id("count").text("0").font(family="Arial", size=28, weight="bold"),
    ltk.Button().text("add count").event(on_click),
)

# run
app.run()
