import ctypes
import tkinter as tk
from shutil import copy
from subprocess import Popen
from threading import Thread
from tkinter import messagebox, ttk
from tkinter.filedialog import askopenfilename, asksaveasfile
from typing import cast

import matplotlib.pyplot as plt
import sv_ttk
from matplotlib.axes import Axes
from matplotlib.dates import DateFormatter

from cs2tracker.background_task import BackgroundTask
from cs2tracker.constants import (
    CONFIG_FILE,
    CONFIG_FILE_BACKUP,
    ICON_FILE,
    OS,
    OUTPUT_FILE,
    POWERSHELL_COLORIZE_OUTPUT,
    PYTHON_EXECUTABLE,
    RUNNING_IN_EXE,
    OSType,
)
from cs2tracker.price_logs import PriceLogs
from cs2tracker.scraper import Scraper

APPLICATION_NAME = "CS2Tracker"
WINDOW_SIZE = "630x380"

CONFIG_EDITOR_TITLE = "Config Editor"
CONFIG_EDITOR_SIZE = "800x750"

SCRAPER_WINDOW_HEIGHT = 40
SCRAPER_WINDOW_WIDTH = 120
SCRAPER_WINDOW_BACKGROUND_COLOR = "Black"


class Application:
    def __init__(self):
        self.scraper = Scraper()
        self.application_window = None
        self.config_editor_window = None

    def run(self):
        """Run the main application window with buttons for scraping prices, editing the
        configuration, showing history in a chart, and editing the log file.
        """
        self.application_window = self._configure_window()

        sv_ttk.use_dark_theme()

        self.application_window.mainloop()

    def _add_button(self, frame, text, command, row):
        """Create and style a button for the button frame."""
        grid_pos = {"row": row, "column": 0, "sticky": "ew", "padx": 10, "pady": 10}
        button = ttk.Button(frame, text=text, command=command)
        button.grid(**grid_pos)

    def _configure_button_frame(self, main_frame):
        """Configure the button frame of the application main frame."""
        button_frame = ttk.Frame(main_frame, style="Card.TFrame", padding=15)
        button_frame.columnconfigure(0, weight=1)
        button_frame.grid(row=0, column=0, padx=10, pady=(7, 20), sticky="nsew")

        self._add_button(button_frame, "Run!", self.scrape_prices, 0)
        self._add_button(button_frame, "Edit Config", self._edit_config, 1)
        self._add_button(button_frame, "Reset Config", self._reset_config, 2)
        self._add_button(button_frame, "Show History", self._draw_plot, 3)
        self._add_button(button_frame, "Export History", self._export_log_file, 4)
        self._add_button(button_frame, "Import History", self._import_log_file, 5)

    def _add_checkbox(
        self, frame, text, variable, command, row
    ):  # pylint: disable=too-many-arguments,too-many-positional-arguments
        """Create and style a checkbox for the checkbox frame."""
        grid_pos = {"row": row, "column": 0, "sticky": "w", "padx": (20, 0), "pady": 10}
        checkbox = ttk.Checkbutton(
            frame,
            text=text,
            variable=variable,
            command=command,
        )
        checkbox.grid(**grid_pos)

    def _configure_checkbox_frame(self, main_frame):
        """Configure the checkbox frame for background tasks and settings."""
        checkbox_frame = ttk.LabelFrame(main_frame, text="Settings", padding=15)
        checkbox_frame.grid(row=0, column=1, padx=10, pady=(0, 20), sticky="nsew")

        background_checkbox_value = tk.BooleanVar(value=BackgroundTask.identify())
        self._add_checkbox(
            checkbox_frame,
            "Background Task",
            background_checkbox_value,
            lambda: self._toggle_background_task(background_checkbox_value.get()),
            0,
        )

        discord_webhook_checkbox_value = tk.BooleanVar(
            value=self.scraper.config.getboolean(
                "App Settings", "discord_notifications", fallback=False
            )
        )
        self._add_checkbox(
            checkbox_frame,
            "Discord Notifications",
            discord_webhook_checkbox_value,
            lambda: discord_webhook_checkbox_value.set(
                self._toggle_discord_webhook(discord_webhook_checkbox_value.get())
            ),
            1,
        )

        use_proxy_checkbox_value = tk.BooleanVar(
            value=self.scraper.config.getboolean("App Settings", "use_proxy", fallback=False)
        )
        self._add_checkbox(
            checkbox_frame,
            "Proxy Requests",
            use_proxy_checkbox_value,
            lambda: use_proxy_checkbox_value.set(
                self._toggle_use_proxy(use_proxy_checkbox_value.get())
            ),
            2,
        )

    def _configure_main_frame(self, window):
        """Configure the main frame of the application window with buttons and
        checkboxes.
        """
        main_frame = ttk.Frame(window, padding=15)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)

        self._configure_button_frame(main_frame)
        self._configure_checkbox_frame(main_frame)

        main_frame.pack(expand=True, fill="both")

    def _configure_window(self):
        """Configure the main application window UI and add buttons for the main
        functionalities.
        """
        window = tk.Tk()
        window.title(APPLICATION_NAME)
        window.geometry(WINDOW_SIZE)

        if OS == OSType.WINDOWS:
            app_id = "cs2tracker.unique.id"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)

        icon = tk.PhotoImage(file=ICON_FILE)
        window.wm_iconphoto(True, icon)

        self._configure_main_frame(window)

        return window

    def _construct_scraper_command_windows(self):
        """Construct the command to run the scraper in a new window for Windows."""
        get_size = "$size = $Host.UI.RawUI.WindowSize;"
        set_size = "$Host.UI.RawUI.WindowSize = $size;"
        set_window_title = f"$Host.UI.RawUI.WindowTitle = '{APPLICATION_NAME}';"
        set_window_width = (
            f"$size.Width = [Math]::Min({SCRAPER_WINDOW_WIDTH}, $Host.UI.RawUI.BufferSize.Width);"
        )
        set_window_height = f"$size.Height = {SCRAPER_WINDOW_HEIGHT};"
        set_background_color = (
            f"$Host.UI.RawUI.BackgroundColor = '{SCRAPER_WINDOW_BACKGROUND_COLOR}';"
        )
        clear = "Clear-Host;"

        if RUNNING_IN_EXE:
            # The python executable is set as the executable itself in PyInstaller
            scraper_cmd = f"{PYTHON_EXECUTABLE} --only-scrape | {POWERSHELL_COLORIZE_OUTPUT}"
        else:
            scraper_cmd = f"{PYTHON_EXECUTABLE} -m cs2tracker --only-scrape"

        cmd = (
            'start powershell -NoExit -Command "& {'
            + set_window_title
            + get_size
            + set_window_width
            + set_window_height
            + set_size
            + set_background_color
            + clear
            + scraper_cmd
            + '}"'
        )
        return cmd

    def _construct_scraper_command(self):
        """Construct the command to run the scraper in a new window."""
        if OS == OSType.WINDOWS:
            return self._construct_scraper_command_windows()
        else:
            # TODO: Implement for Linux
            return ""

    def scrape_prices(self):
        """Scrape prices from the configured sources, print the total, and save the
        results to a file.
        """
        if OS == OSType.WINDOWS:
            scraper_cmd = self._construct_scraper_command()
            Popen(scraper_cmd, shell=True)
        else:
            # TODO: implement external window for Linux
            self.scraper.scrape_prices()

    def _make_tree_editable(self, editor_frame, tree):
        """
        Add a binding to the treeview that allows double-clicking on a cell to edit its
        value.

        Source: https://stackoverflow.com/questions/75787251/create-an-editable-tkinter-treeview-with-keyword-connection
        """

        def set_cell_value(event):
            def save_edit(event):
                tree.set(row, column=column, value=event.widget.get())
                event.widget.destroy()

            try:
                row = tree.identify_row(event.y)
                column = tree.identify_column(event.x)
                item_text = tree.set(row, column)
                if item_text.strip() == "":
                    left_item_text = tree.item(row, "text")
                    # Don't allow editing of section headers
                    if any(left_item_text == section for section in self.scraper.config.sections()):
                        return
                x, y, w, h = tree.bbox(row, column)
                entryedit = ttk.Entry(editor_frame)
                entryedit.place(x=x, y=y, width=w, height=h + 3)  # type: ignore
                entryedit.insert("end", item_text)
                entryedit.bind("<Return>", save_edit)
                entryedit.focus_set()
                entryedit.grab_set()
            except Exception:
                pass

        def destroy_entries(_):
            """Destroy any entry widgets in the treeview when the mouse wheel is
            used.
            """
            for widget in editor_frame.winfo_children():
                if isinstance(widget, ttk.Entry):
                    widget.destroy()

        def destroy_entry(event):
            """Destroy the entry widget if the user clicks outside of it."""
            if isinstance(event.widget, ttk.Entry):
                event.widget.destroy()

        tree.bind("<Double-1>", set_cell_value)
        self.config_editor_window.bind("<MouseWheel>", destroy_entries)  # type: ignore
        self.config_editor_window.bind("<Button-1>", destroy_entry)  # type: ignore

    def _add_treeview(self, editor_frame):
        """Add a treeview to the editor frame to display and edit configuration
        options.
        """
        scrollbar = ttk.Scrollbar(editor_frame)
        scrollbar.pack(side="right", fill="y", padx=(5, 0))

        tree = ttk.Treeview(
            editor_frame,
            columns=(1,),
            height=10,
            selectmode="browse",
            yscrollcommand=scrollbar.set,
        )
        scrollbar.config(command=tree.yview)

        tree.pack(expand=True, fill="both")
        tree.column("#0", anchor="w", width=200)
        tree.column(1, anchor="w", width=25)
        tree.heading("#0", text="Option")
        tree.heading(1, text="Value")

        for section in self.scraper.config.sections():
            if section == "App Settings":
                continue
            section_level = tree.insert("", "end", text=section)
            for config_option, value in self.scraper.config.items(section):
                title_option = config_option.replace("_", " ").title()
                tree.insert(section_level, "end", text=title_option, values=(value,))

        self._make_tree_editable(editor_frame, tree)

        return tree

    def _add_save_button(self, editor_frame, tree):
        """Save updated options and values from the treeview back to the config file."""

        def save_config():
            for child in tree.get_children():
                for item in tree.get_children(child):
                    title_option = tree.item(item, "text")
                    config_option = title_option.lower().replace(" ", "_")
                    value = tree.item(item, "values")[0]
                    section = tree.parent(item)
                    section_name = tree.item(section, "text")
                    self.scraper.config.set(section_name, config_option, value)

            self.scraper.config.write_to_file()
            if self.scraper.config.valid:
                messagebox.showinfo(
                    "Config Saved", "The configuration has been saved successfully."
                )
            else:
                messagebox.showerror(
                    "Config Error",
                    f"The configuration is invalid. ({self.scraper.config.last_error})",
                )

        save_button = ttk.Button(editor_frame, text="Save", command=save_config)
        save_button.pack(side="bottom", pady=10, padx=10)

    def _configure_editor_frame(self):
        """Configure the main editor frame which displays the configuration options in a
        structured way.
        """
        editor_frame = ttk.Frame(self.config_editor_window, padding=30)
        editor_frame.pack(expand=True, fill="both")

        tree = self._add_treeview(editor_frame)
        self._add_save_button(editor_frame, tree)

    def _edit_config(self):
        """Open a new window with a config editor GUI."""
        self.config_editor_window = tk.Toplevel(self.application_window)
        self.config_editor_window.geometry(CONFIG_EDITOR_SIZE)
        self.config_editor_window.title(CONFIG_EDITOR_TITLE)

        self._configure_editor_frame()

    def _reset_config(self):
        """Reset the configuration file to its default state."""
        confirm = messagebox.askokcancel(
            "Reset Config", "Are you sure you want to reset the configuration?"
        )
        if confirm:
            copy(CONFIG_FILE_BACKUP, CONFIG_FILE)
            self.scraper.load_config()

    def _draw_plot(self):
        """Draw a plot of the scraped prices over time."""
        dates, usd_prices, eur_prices = PriceLogs.read()

        fig, ax_raw = plt.subplots(figsize=(10, 8), num="CS2Tracker Price History")
        fig.suptitle("CS2Tracker Price History", fontsize=16)
        fig.autofmt_xdate()

        ax = cast(Axes, ax_raw)
        ax.plot(dates, usd_prices, label="Dollars")
        ax.plot(dates, eur_prices, label="Euros")
        ax.legend()
        date_formatter = DateFormatter("%Y-%m-%d")
        ax.xaxis.set_major_formatter(date_formatter)

        plt.show()

    def _export_log_file(self):
        """Lets the user export the log file to a different location."""
        export_path = asksaveasfile(
            title="Export Log File",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
        )
        if export_path:
            copy(OUTPUT_FILE, export_path.name)

    def _import_log_file(self):
        """Lets the user import a log file from a different location."""
        import_path = askopenfilename(
            title="Import Log File",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
        )
        if not PriceLogs.validate_file(import_path):
            return
        copy(import_path, OUTPUT_FILE)

    def _toggle_background_task(self, enabled: bool):
        """Toggle whether a daily price calculation should run in the background."""
        BackgroundTask.toggle(enabled)

    def _toggle_use_proxy(self, enabled: bool):
        """Toggle whether the scraper should use proxy servers for requests."""
        proxy_api_key = self.scraper.config.get("User Settings", "proxy_api_key", fallback=None)
        if not proxy_api_key and enabled:
            messagebox.showerror(
                "Config Error",
                "You need to enter a valid crawlbase API key into the config file to use this feature.",
            )
            return False

        self.scraper.toggle_use_proxy(enabled)
        return True

    def _toggle_discord_webhook(self, enabled: bool):
        """Toggle whether the scraper should send notifications to a Discord webhook."""
        discord_webhook_url = self.scraper.config.get(
            "User Settings", "discord_webhook_url", fallback=None
        )
        if not discord_webhook_url and enabled:
            messagebox.showerror(
                "Config Error",
                "You need to enter a valid Discord webhook URL into the config file to use this feature.",
            )
            return False

        self.scraper.toggle_discord_webhook(enabled)
        return True


def _popen_and_call(popen_args, callback):
    """
    Runs the given args in a subprocess.Popen, and then calls the function callback when
    the subprocess completes.

    Source: https://stackoverflow.com/questions/2581817/python-subprocess-callback-when-cmd-exits
    """

    def process_and_callback(popen_args, callback):
        process = Popen(**popen_args)
        process.wait()
        callback()

    thread = Thread(target=process_and_callback, args=(popen_args, callback), daemon=True)
    thread.start()
