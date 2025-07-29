from tkinter import ttk

from tksheet import Sheet


class ScraperFrame(ttk.Frame):
    def __init__(self, parent, scraper, sheet_size, dark_theme):
        """Initialize the frame for running the scraper."""
        super().__init__(parent)

        self.parent = parent
        self.scraper = scraper
        self.sheet_width = sheet_size.split("x")[0]
        self.sheet_height = sheet_size.split("x")[1]
        self.dark_theme = dark_theme

        self._add_widgets()

    def _add_widgets(self):
        """Add widgets to the frame."""
        self.sheet = Sheet(
            self,
            data=[],
            theme="light" if self.dark_theme else "dark",
            height=self.sheet_height,
            width=self.sheet_width,
            auto_resize_columns=150,
        )
        self.sheet.enable_bindings()
        self.sheet.insert_row(
            ["Item Name", "Item Owned", "Steam Market Price", "Total Price Owned"]
        )
        self.sheet.column_width(0, 220)
        self.sheet.column_width(1, 20)
        self.sheet.align_columns([1, 2, 3], "c")
        self.sheet.align_rows([0], "c")

        self.sheet.pack()

    def start(self):
        """Start the scraper and update the sheet with the latest price data in real-
        time.
        """

        def update_sheet_callback(row):
            """Callback for the scraper to insert the latest price data into the
            sheet.
            """
            self.sheet.insert_row(row)
            self.parent.update()
            self.parent.update_idletasks()

        self.scraper.scrape_prices(update_sheet_callback)
