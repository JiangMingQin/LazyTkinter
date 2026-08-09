import lazytkinter as ltk

class App:
    """
    Using classes to organize the code
    """
    def __init__(self) -> None:
        ltk.set_theme(ltk.Theme.Catppuccin)

    # event
    def search_something(self, value=None):
        print("search....")

    def turn_to_page(self, page):
        print(f"turn_to_page{page}")

    def switch_mode(self, val):
        print("switch!")
        if val == False:
            ltk.set_mode("dark")
        else:
            ltk.set_mode("light")

    def on_segment_click(self, value):
        print(f"Segment clicked: {value}")

    def on_combo_change(self, value):
        print(f"Combo chosen: {value}")

    def on_tree_select(self, value):
        print(f"Treeview selected: {value}")

    def on_list_select(self, value):
        print(f"Listbox selected: {value}")

    # layout
    def main(self):
        # create app
        app = ltk.Application()

        # build page
        app.size("large").window_title("My first app").gap(10).padding(10).column(
            # Top Bar
            ltk.Row().gap(10).padding(10).radius(10).align("center").height(60).width().fill().add(
                ltk.Label().text("LazyTkinter").font(family="Arial", size=16, weight="bold"),
                ltk.Empty().width(10),  # fixed placeholder
                ltk.Entry().width().fill().height(35).radius(100).placeholder_text("entry..."),
                ltk.Button().height(35).text("search").event(self.search_something),
            ),
            # Main Area
            ltk.Row().gap(10).radius(10).padding(5).height().fill().width().fill().add(
                # Left Sidebar
                ltk.Column().width(150).gap(10).padding(5).height().fill().transparent().add(
                    ltk.Button().height(30).text("Page 1").event(lambda: self.turn_to_page(1)),
                    ltk.Button().height(30).text("Page 2").event(lambda: self.turn_to_page(2)),
                    ltk.Button().height(30).text("Disabled").state("disabled"),
                    ltk.Spacer(),
                    ltk.Switch().height(30).radius(10).text("Dark/Light").event(self.switch_mode),
                ),
                # Right Main Content
                ltk.Column().gap(10).padding(5).height().fill().width().fill().transparent().add(
                    # Top Content
                    ltk.Row().height(150).width().fill().gap(10).transparent().add(
                        # Selection block: checkbox + radio take 1 part (1:2 vs textbox)
                        ltk.Column().width().fill(weight=1).transparent().gap(10).add(
                            ltk.Row().width().fill().gap(10).transparent().add(
                                # Checkbox
                                ltk.Column().width().fill().transparent().gap(10).add(
                                    ltk.CheckBox().height(20).radius(8),
                                    ltk.CheckBox().height(20).radius(8),
                                    ltk.CheckBox().height(20).radius(8),
                                    ltk.CheckBox().height(20).radius(8),
                                ),
                                # RadioButton
                                ltk.Column().width().fill().transparent().gap(10).add(
                                    ltk.RadioButton().height(20),
                                    ltk.RadioButton().height(20),
                                    ltk.RadioButton().height(20),
                                ),
                            ),
                        ),
                        # Textbox takes 2 parts
                        ltk.Textbox().width().fill(weight=2).height().fill().radius(8),
                    ),
                    # Slider
                    ltk.Slider().height(20).width().fill(),
                    # ProgressBar
                    ltk.ProgressBar().value(0.7).height(10).width().fill(),
                    # SegmentedButton
                    ltk.Row().height(30).width().fill().add(
                        ltk.SegmentedButton().radius(100).fill().values([
                            "Option A",
                            "Option B",
                            "Option C",
                        ]).event(self.on_segment_click).set_value("Option A"),
                    ),
                    # ComboBox & OptionMenu
                    ltk.Row().height(30).width().fill().transparent().gap(10).add(
                        ltk.ComboBox().width().fill().values([
                            "Combo 1",
                            "Combo 2",
                        ]).event(self.on_combo_change),
                        ltk.OptionMenu().width().fill().values([
                            "Menu 1",
                            "Menu 2",
                        ]),
                    ),
                    # Data widgets: Treeview & Listbox
                    ltk.Row().gap(10).height().fill().width().fill().add(
                        ltk.Treeview()
                            .columns(["Item", "Value"])
                            .rows([
                                ("Item 1", "10"),
                                ("Item 2", "20"),
                                ("Item 3", "30"),
                                ("Item 4", "40"),
                                ("Item 5", "50"),
                                ("Item 6", "60"),
                                ("Item 7", "70"),
                            ])
                            .width().fill(weight=1)
                            .height().fill()
                            .event(self.on_tree_select),
                        ltk.Listbox()
                            .items([
                                "Item 1",
                                "Item 2",
                                "Item 3",
                                "Item 4",
                                "Item 5",
                                "Item 6",
                                "Item 7",
                            ])
                            .width().fill(weight=1)
                            .height().fill()
                            .event(self.on_list_select),
                    ),
                ),
            ),
        )

        # run program
        app.run()

if __name__ == "__main__":
    app = App()
    app.main()
