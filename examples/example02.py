import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.append(root_dir)

import lazytkinter as ltk

class App:
    """
    Using classes to organize the code
    """
    def __init__(self) -> None:
        ltk.set_theme(ltk.Theme.Catppuccin)

    # event
    def search_something(self):
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

    # layout
    def main(self):
        # create app
        app = ltk.Application()

        # build page
        app.size("large").window_title("My first app").column(
            ltk.Column().gap(5).padding(5).height("fill").add(
                # Top Bar
                ltk.Row().gap(10).padding(10).align("center").height(60).add(
                    ltk.Label().text("LazyTkinter"),
                    ltk.Empty().width(10),  # fixed placeholder
                    ltk.Entry().width("fill").height(35).radius(100).placeholder_text("entry..."),
                    ltk.Button().width(80).text("search").event(self.search_something),
                ),
                # Main Area
                ltk.Row().gap(10).padding(5).height("fill").add(
                    # Left Sidebar
                    ltk.Column().width(150).gap(10).padding(10).height("fill").add(
                        ltk.Button().height(30).text("Page 1").event(lambda: self.turn_to_page(1)),
                        ltk.Button().height(30).text("Page 2").event(lambda: self.turn_to_page(2)),
                        ltk.Button().height(30).text("Disabled").state("disabled"),
                        ltk.Spacer(),
                        ltk.Switch().height(30).radius(10).text("Dark/Light").event(self.switch_mode),
                    ),
                    # Right Main Content
                    ltk.Column().gap(10).padding(10).height("fill").add(
                        ltk.Row().height(130).gap(10).add(
                            # Checkbox
                            ltk.Column().width(60).gap(5).add(
                                ltk.CheckBox().height(20).radius(8),
                                ltk.CheckBox().height(20).radius(8),
                                ltk.CheckBox().height(20).radius(8),
                                ltk.CheckBox().height(20).radius(8),
                            ),
                            # RadioButton
                            ltk.Column().width(60).gap(5).add(
                                ltk.RadioButton().height(20),
                                ltk.RadioButton().height(20),
                                ltk.RadioButton().height(20),
                            ),
                            # Textbox
                            ltk.Textbox().width("fill").height("fill").radius(8),
                        ),
                        # Slider
                        ltk.Slider().height(20),
                        # ProgressBar
                        ltk.ProgressBar().value(0.7).height(10),
                        # SegmentedButton
                        ltk.Row().height(30).add(
                            ltk.SegmentedButton().radius(100).values([
                                "Option A",
                                "Option B",
                                "Option C",
                            ]).event(self.on_segment_click).set_value("Option A"),
                        ),
                        # ComboBox & OptionMenu
                        ltk.Row().height(30).gap(10).add(
                            ltk.ComboBox().width("fill").values([
                                "Combo 1",
                                "Combo 2",
                            ]).event(self.on_combo_change),
                            ltk.OptionMenu().width("fill").values([
                                "Menu 1",
                                "Menu 2",
                            ]),
                        ),
                        # Scrollable list
                        ltk.Scroll(
                            ltk.Column().gap(5).add(
                                ltk.Button().radius(10).text("Item 1"),
                                ltk.Button().radius(10).text("Item 2"),
                                ltk.Button().radius(10).text("Item 3"),
                                ltk.Button().radius(10).text("Item 4"),
                                ltk.Button().radius(10).text("Item 5"),
                                ltk.Button().radius(10).text("Item 6"),
                                ltk.Button().radius(10).text("Item 7"),
                            ),
                        ),
                    ),
                ),
            ),
        )

        # run program
        app.run()

if __name__ == "__main__":
    app = App()
    app.main()
