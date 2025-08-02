import csv
from tkinter import messagebox, ttk
from tkinter.filedialog import asksaveasfilename

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
        self._configure_sheet()
        self.sheet.pack()

    def _readjust_sheet_size_with_window_size(self, event):
        """Ensures that the sheet resizes with the window."""
        if event.widget == self.parent:
            width, height = event.width, event.height
            if width != self.sheet_width or height != self.sheet_height:
                self.sheet_width = width
                self.sheet_height = height
                self.sheet.height_and_width(height, width)
                self.parent.update()
                self.parent.update_idletasks()

    def _configure_sheet(self):
        """Configure the sheet widget with initial data and settings."""
        self.sheet = Sheet(  # pylint: disable=attribute-defined-outside-init
            self,
            data=[],
            theme="light" if self.dark_theme else "dark",  # This is on purpose to add contrast
            height=self.sheet_height,
            width=self.sheet_width,
            auto_resize_columns=150,
            sticky="nsew",
        )
        self.sheet.enable_bindings()
        self.sheet.insert_row(
            ["Item Name", "Item Owned", "Steam Market Price (USD)", "Total Value Owned (USD)"]
        )
        self.sheet.column_width(0, 220)
        self.sheet.column_width(1, 20)
        self.sheet.align_rows([0], "c")
        self.sheet.align_columns([1, 2, 3], "c")
        self.sheet.popup_menu_add_command("Save Sheet", self._save_sheet)

        self.parent.bind("<Configure>", self._readjust_sheet_size_with_window_size)

    def _save_sheet(self):
        """Export the current sheet data to a CSV file."""
        filepath = asksaveasfilename(
            title="Save Price Sheet",
            filetypes=[("CSV File", ".csv")],
            defaultextension=".csv",
        )
        if filepath:
            with open(filepath, "w", newline="", encoding="utf-8") as sheet_file:
                writer = csv.writer(sheet_file)
                writer.writerows(self.sheet.data)

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

        row_heights = self.sheet.get_row_heights()
        last_row_index = len(row_heights) - 1
        self.sheet.align_rows(last_row_index, "c")

        if self.scraper.error_stack:
            last_error = self.scraper.error_stack[-1]
            messagebox.showerror("An Error Occurred", f"{last_error.message}", parent=self)
