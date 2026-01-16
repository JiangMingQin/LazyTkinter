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
        self.content = f"page {page}"

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
        app.window_size( # set window size
                "800x500"
            ).window_title( # set title
                "My first app"
            ).column(
                ltk.Row().padding(5).height(60).weight(0).radius(0).add(
                        ltk.Row().padding(10).spacing(10).radius(10).add(
                            ltk.Label().width(130).weight(0).text("LazyTkinter"),
                            ltk.Empty().width(10).weight(0), # placeholder
                            ltk.Entry().weight(8).radius(100).placeholder_text("entry..."),
                            ltk.Button().width(80).weight(1).radius(100).text("serach").event(self.search_something)
                    )
                ),
                ltk.Row().padding(5).spacing(10).radius(0).add( 
                    # Left Sidebar
                    ltk.Column().width(150).padding(10).spacing(10).radius(10).weight(0).add(
                        ltk.Button().height(30).weight(0).text("Page 1").event(lambda: self.turn_to_page(1)),
                        ltk.Button().height(30).weight(0).text("Page 2").event(lambda: self.turn_to_page(2)),
                        ltk.Button().height(30).weight(0).text("Disabled").state("disabled"),
                        ltk.Empty().weight(1),
                        ltk.Switch().height(30).weight(0).radius(10).text("Dark/Light").event(self.switch_mode),
                    ),
                    # Right Main Content
                    ltk.Column().padding(10).spacing(10).radius(10).add(
                        ltk.Row().height(130).weight(0).spacing(10).transparent(True).add(
                            # Checkbox
                            ltk.Column().width(60).weight(1).spacing(5).add(
                                ltk.CheckBox().height(20).radius(8),
                                ltk.CheckBox().height(20).radius(8),
                                ltk.CheckBox().height(20).radius(8),
                                ltk.CheckBox().height(20).radius(8),
                            ),
                            # RadioButton
                            ltk.Column().width(60).weight(1).spacing(5).add(
                                ltk.RadioButton().height(20),
                                ltk.RadioButton().height(20),
                                ltk.RadioButton().height(20),
                            ),
                            # Textbox
                            ltk.Textbox().weight(2).radius(8)
                        ),
                        # Slider
                        ltk.Slider().height(20).weight(0),
                        # ProgressBar
                        ltk.ProgressBar().value(0.7).height(10).weight(0),
                        # SegmentedButton
                        ltk.Row().height(30).weight(0).transparent(True).add(
                            ltk.SegmentedButton().radius(100).values([
                                "Option A", 
                                "Option B", 
                                "Option C"
                            ]).event(self.on_segment_click).set_value("Option A")
                        ),
                        ltk.Row().height(30).weight(0).spacing(10).transparent(True).add(
                            # ComboBox
                            ltk.ComboBox().weight(1).values([
                                "Combo 1", 
                                "Combo 2"
                            ]).event(self.on_combo_change),
                            # OptionMenu
                            ltk.OptionMenu().weight(1).values([
                                "Menu 1", 
                                "Menu 2"
                            ]),
                        ),
                        # ScrollableColumn
                        ltk.ScrollableColumn().weight(1).spacing(5).add(
                            ltk.Button().radius(10).text("Item 1"),
                            ltk.Button().radius(10).text("Item 2"),
                            ltk.Button().radius(10).text("Item 3"),
                            ltk.Button().radius(10).text("Item 4"),
                            ltk.Button().radius(10).text("Item 5"),
                            ltk.Button().radius(10).text("Item 6"),
                            ltk.Button().radius(10).text("Item 7"),
                        )
                    )
                )
            )
                
        # run program
        app.run()

if __name__ == "__main__":
    app = App()
    app.main()

