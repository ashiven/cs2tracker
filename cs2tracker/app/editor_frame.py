import tkinter as tk
from queue import Empty, Queue
from shutil import copy
from subprocess import PIPE, STDOUT
from threading import Thread
from tkinter import messagebox, ttk

from nodejs import node
from ttk_text import ThemedText

from cs2tracker.constants import (
    CONFIG_FILE,
    CONFIG_FILE_BACKUP,
    DATA_DIR,
    INVENTORY_IMPORT_FILE,
    INVENTORY_IMPORT_SCRIPT,
)
from cs2tracker.util import get_config

ADD_CUSTOM_ITEM_TITLE = "Add Custom Item"
ADD_CUSTOM_ITEM_SIZE = "500x220"

IMPORT_INVENTORY_TITLE = "Import Steam Inventory"
IMPORT_INVENTORY_SIZE = "600x550"

IMPORT_INVENTORY_PROCESS_TITLE = "Importing Steam Inventory..."
IMPORT_INVENTORY_PROCESS_SIZE = "700x500"

config = get_config()


class ConfigEditorFrame(ttk.Frame):
    def __init__(self, parent):
        """Initialize the configuration editor frame that allows users to view and edit
        the configuration options.
        """
        super().__init__(parent, padding=15)

        self.parent = parent
        self.edit_entry = None
        self._add_widgets()

        self.tree.focus_set()

    def _add_widgets(self):
        """Configure the main editor frame which displays the configuration options in a
        structured way.
        """
        self._configure_treeview()
        self.tree.pack(expand=True, fill="both")

        button_frame = ConfigEditorButtonFrame(self)
        button_frame.pack(side="bottom", padx=10, pady=(0, 10))

    def save_config(self):
        """Save the current configuration from the treeview to the config file."""
        config.delete_display_sections()
        for section in self.tree.get_children():
            config.add_section(section)
            for item in self.tree.get_children(section):
                item_name = self.tree.item(item, "text")
                if section not in ("App Settings", "User Settings"):
                    config_option = config.name_to_option(item_name, href=True)
                else:
                    config_option = config.name_to_option(item_name)
                value = self.tree.item(item, "values")[0]
                config.set(section, config_option, value)

        config.write_to_file()
        if not config.valid:
            config.load_from_file()
            self.reload_config_into_tree()
            messagebox.showerror(
                "Config Error", f"The configuration is invalid. ({config.last_error})", parent=self
            )
        self.parent.focus_set()
        self.tree.focus_set()

    def _save_edit(self, event, row, column):
        """Save the edited value in the treeview and destroy the entry widget."""
        self.tree.set(row, column=column, value=event.widget.get())
        self.save_config()
        event.widget.destroy()

    def _set_cell_value(self, event, row=None, column=None):
        """
        Set the value of a cell in the treeview to be editable when double-clicked.

        Source: https://stackoverflow.com/questions/75787251/create-an-editable-tkinter-treeview-with-keyword-connection
        """
        try:
            if not row or not column:
                row = self.tree.identify_row(event.y)
                column = self.tree.identify_column(event.x)

            item_text = self.tree.item(row, "text")
            if column == "#0" or any(item_text == section for section in config.sections()):
                return
            item_value = self.tree.item(row, "values")[0]

            x, y, w, h = self.tree.bbox(row, column)
            self.edit_entry = ttk.Entry(self, justify="center", font=("Helvetica", 11))
            self.edit_entry.place(x=x, y=y, width=w, height=h + 3)  # type: ignore
            self.edit_entry.insert("end", item_value)
            self.edit_entry.bind("<Return>", lambda e: self._save_edit(e, row, column))
            self.edit_entry.focus_set()
            self.edit_entry.grab_set()
        except Exception:
            return

    def _set_selection_value(self, _):
        """Set the value of the currently selected cell in the treeview to be
        editable.
        """
        selected = self.tree.selection()
        if selected:
            row = selected[0]
            column = "#1"
            self._set_cell_value(None, row=row, column=column)

    def _delete_selection_value(self, _):
        """
        Delete the value of the currently selected cell in the treeview.

        This only works for custom items, as other sections are not editable.
        """
        selected = self.tree.selection()
        if selected:
            row = selected[0]
            section_name = self.tree.parent(row)
            if section_name == "Custom Items":
                self.tree.delete(row)
                self.save_config()
                self.tree.focus("Custom Items")
                self.tree.selection_set("Custom Items")

    def _destroy_entry(self, _):
        """Destroy any entry widgets in the treeview on an event, such as a mouse wheel
        movement.
        """
        if self.edit_entry:
            self.edit_entry.destroy()
            self.edit_entry = None
            self.tree.focus_set()

    def _make_tree_editable(self):
        """Add a binding to the treeview that allows double-clicking on a cell to edit
        its value.
        """
        self.tree.bind("<Double-1>", self._set_cell_value)
        self.tree.bind("<Return>", self._set_selection_value)
        self.tree.bind("<BackSpace>", self._delete_selection_value)
        self.parent.bind("<MouseWheel>", self._destroy_entry)
        self.parent.bind("<Escape>", self._destroy_entry)

    def _load_config_into_tree(self):
        """Load the configuration options into the treeview for display and editing."""
        for section in config.sections():
            if section == "App Settings":
                continue
            section_level = self.tree.insert("", "end", iid=section, text=section)
            for config_option, value in config.items(section):
                if section not in ("User Settings", "App Settings"):
                    option_name = config.option_to_name(config_option, href=True)
                    self.tree.insert(section_level, "end", text=option_name, values=[value])
                else:
                    option_name = config.option_to_name(config_option)
                    self.tree.insert(section_level, "end", text=option_name, values=[value])

        self.tree.focus("User Settings")
        self.tree.selection_set("User Settings")

    def reload_config_into_tree(self):
        """Reload the configuration options into the treeview for display and
        editing.
        """
        for item in self.tree.get_children():
            self.tree.delete(item)
        self._load_config_into_tree()

    def _configure_treeview(self):
        """Configure a treeview to display and edit configuration options."""
        scrollbar = ttk.Scrollbar(self)
        scrollbar.pack(side="right", fill="y", padx=(5, 0))

        self.tree = ttk.Treeview(  # pylint: disable=attribute-defined-outside-init
            self,
            columns=(1,),
            height=10,
            selectmode="browse",
            yscrollcommand=scrollbar.set,
        )
        scrollbar.config(command=self.tree.yview)

        self.tree.column("#0", anchor="w", width=200)
        self.tree.column(1, anchor="center", width=25)
        self.tree.heading("#0", text="Option")
        self.tree.heading(1, text="Value")

        self._load_config_into_tree()
        self._make_tree_editable()


class ConfigEditorButtonFrame(ttk.Frame):
    def __init__(self, editor_frame):
        """Initialize the button frame that contains buttons for saving the updated
        configuration and adding custom items.
        """
        super().__init__(editor_frame, padding=10)

        self.editor_frame = editor_frame
        self.custom_item_dialog = None

        self._add_widgets()

    def _add_widgets(self):
        """Add buttons to the button frame for saving the configuration and adding
        custom items.
        """
        reset_button = ttk.Button(self, text="Reset", command=self._reset_config)
        reset_button.pack(side="left", expand=True, padx=5)

        custom_item_button = ttk.Button(self, text="Add Custom Item", command=self._add_custom_item)
        custom_item_button.pack(side="left", expand=True, padx=5)

        import_inventory_button = ttk.Button(
            self, text="Import Steam Inventory", command=self._import_steam_inventory
        )
        import_inventory_button.pack(side="left", expand=True, padx=5)

    def _reset_config(self):
        """Reset the configuration file to its default state."""
        confirm = messagebox.askokcancel(
            "Reset Config", "Are you sure you want to reset the configuration?", parent=self
        )
        if confirm:
            copy(CONFIG_FILE_BACKUP, CONFIG_FILE)
            config.load_from_file()
            self.editor_frame.reload_config_into_tree()
        self.editor_frame.focus_set()
        self.editor_frame.tree.focus_set()

    def _add_custom_item(self):
        """Open a window to add a new custom item."""
        custom_item_window = tk.Toplevel(self.editor_frame)
        custom_item_window.title(ADD_CUSTOM_ITEM_TITLE)
        custom_item_window.geometry(ADD_CUSTOM_ITEM_SIZE)
        custom_item_window.focus_set()

        custom_item_frame = CustomItemFrame(custom_item_window, self.editor_frame)
        custom_item_frame.pack(expand=True, fill="both", padx=15, pady=15)
        self.editor_frame.tree.focus_set()

    def _import_steam_inventory(self):
        """Open a window to import the user's Steam inventory."""
        steam_inventory_window = tk.Toplevel(self.editor_frame)
        steam_inventory_window.title(IMPORT_INVENTORY_TITLE)
        steam_inventory_window.geometry(IMPORT_INVENTORY_SIZE)
        steam_inventory_window.focus_set()

        steam_inventory_frame = InventoryImportFrame(steam_inventory_window, self.editor_frame)
        steam_inventory_frame.pack(expand=True, fill="both", padx=15, pady=15)
        self.editor_frame.tree.focus_set()


class CustomItemFrame(ttk.Frame):
    def __init__(self, parent, editor_frame):
        """Initialize the custom item frame that allows users to add custom items."""
        super().__init__(parent, style="Card.TFrame", padding=15)
        self.parent = parent
        self.editor_frame = editor_frame
        self._add_widgets()

    def _add_widgets(self):
        """Add widgets to the custom item frame for entering item details."""
        ttk.Label(self, text="Item URL:").pack(pady=5)
        item_url_entry = ttk.Entry(self)
        item_url_entry.pack(fill="x", padx=10)

        ttk.Label(self, text="Owned Count:").pack(pady=5)
        item_owned_entry = ttk.Entry(self)
        item_owned_entry.pack(fill="x", padx=10)

        add_button = ttk.Button(
            self,
            text="Add",
            command=lambda: self._add_custom_item(item_url_entry.get(), item_owned_entry.get()),
        )
        add_button.pack(pady=10)
        self.parent.bind("<Return>", lambda _: add_button.invoke())

    def _add_custom_item(self, item_href, item_owned):
        """Add a custom item to the configuration."""
        if not item_href or not item_owned:
            messagebox.showerror("Input Error", "All fields must be filled out.", parent=self)
            self.editor_frame.focus_set()
            self.parent.focus_set()
            return

        item_name = config.option_to_name(item_href, href=True)

        # Make sure not to reinsert custom items that have already been added
        for option in self.editor_frame.tree.get_children("Custom Items"):
            option_name = self.editor_frame.tree.item(option, "text")
            if option_name == item_name:
                self.editor_frame.tree.set(option, column="#1", value=item_owned)
                self.editor_frame.focus_set()
                self.editor_frame.save_config()
                self.parent.destroy()
                return

        self.editor_frame.tree.insert(
            "Custom Items",
            "end",
            text=item_name,
            values=[item_owned],
        )
        self.editor_frame.focus_set()
        self.editor_frame.save_config()
        self.parent.destroy()


class InventoryImportFrame(ttk.Frame):
    # pylint: disable=too-many-instance-attributes
    def __init__(self, parent, editor_frame):
        """Initialize the inventory import frame that allows users to import their Steam
        inventory.
        """
        super().__init__(parent, style="Card.TFrame", padding=10)
        self.parent = parent
        self.editor_frame = editor_frame
        self._add_widgets()

    def _add_widgets(self):
        """Add widgets to the inventory import frame."""
        self._configure_checkboxes()
        self.storage_units_checkbox.pack(anchor="w", padx=20, pady=(15, 5))
        self.regular_inventory_checkbox.pack(anchor="w", padx=20, pady=5)

        self.import_cases_checkbox.pack(anchor="w", padx=20, pady=5)
        self.import_sticker_capsules_checkbox.pack(anchor="w", padx=20, pady=5)
        self.import_stickers_checkbox.pack(anchor="w", padx=20, pady=5)
        self.import_others_checkbox.pack(anchor="w", padx=20, pady=5)

        self._configure_entries()
        self.user_name_label.pack(pady=(20, 10))
        self.user_name_entry.pack(fill="x", padx=50)
        self.password_label.pack(pady=10)
        self.password_entry.pack(fill="x", padx=50)
        self.two_factor_label.pack(pady=10)
        self.two_factor_entry.pack(fill="x", padx=50)

        self.import_button = ttk.Button(
            self, text="Import", command=self._import_inventory, state="disabled"
        )
        self.import_button.pack(pady=10)
        self.parent.bind("<Return>", lambda _: self.import_button.invoke())

        def form_complete(_):
            if (
                len(self.user_name_entry.get().strip()) > 0
                and len(self.password_entry.get().strip()) > 0
                and len(self.two_factor_entry.get().strip()) > 0
            ):
                self.import_button.configure(state="normal")
            else:
                self.import_button.configure(state="disabled")

        self.parent.bind("<KeyRelease>", form_complete)

    def _configure_checkboxes(self):
        # pylint: disable=attribute-defined-outside-init
        """Configure the checkboxes for selecting what to import from the Steam
        inventory.
        """
        self.regular_inventory_value = tk.BooleanVar(value=False)
        self.regular_inventory_checkbox = ttk.Checkbutton(
            self,
            text="Regular Inventory",
            variable=self.regular_inventory_value,
            style="Switch.TCheckbutton",
        )

        self.storage_units_value = tk.BooleanVar(value=True)
        self.storage_units_checkbox = ttk.Checkbutton(
            self,
            text="Storage Units",
            variable=self.storage_units_value,
            style="Switch.TCheckbutton",
        )

        self.import_cases_value = tk.BooleanVar(value=True)
        self.import_cases_checkbox = ttk.Checkbutton(
            self, text="Import Cases", variable=self.import_cases_value, style="Switch.TCheckbutton"
        )

        self.import_sticker_capsules_value = tk.BooleanVar(value=True)
        self.import_sticker_capsules_checkbox = ttk.Checkbutton(
            self,
            text="Import Sticker Capsules",
            variable=self.import_sticker_capsules_value,
            style="Switch.TCheckbutton",
        )

        self.import_stickers_value = tk.BooleanVar(value=False)
        self.import_stickers_checkbox = ttk.Checkbutton(
            self,
            text="Import Stickers",
            variable=self.import_stickers_value,
            style="Switch.TCheckbutton",
        )

        self.import_others_value = tk.BooleanVar(value=False)
        self.import_others_checkbox = ttk.Checkbutton(
            self,
            text="Import Other Items",
            variable=self.import_others_value,
            style="Switch.TCheckbutton",
        )

    def _configure_entries(self):
        # pylint: disable=attribute-defined-outside-init
        """Configure the entry fields for Steam username, password, and two-factor
        code.
        """
        self.user_name_label = ttk.Label(self, text="Steam Username:")
        self.user_name_entry = ttk.Entry(self, justify="center", font=("Helvetica", 11))

        self.password_label = ttk.Label(self, text="Steam Password:")
        self.password_entry = ttk.Entry(self, show="*", justify="center", font=("Helvetica", 11))

        self.two_factor_label = ttk.Label(self, text="Steam Guard Code:")
        self.two_factor_entry = ttk.Entry(self, justify="center", font=("Helvetica", 11))

    def _import_inventory(self):
        """
        Call the node.js script to import the user's Steam inventory.

        This will also install the necessary npm packages if they are not already
        installed.
        """
        regular_inventory = self.regular_inventory_value.get()
        storage_units = self.storage_units_value.get()

        import_cases = self.import_cases_value.get()
        import_sticker_capsules = self.import_sticker_capsules_value.get()
        import_stickers = self.import_stickers_value.get()
        import_others = self.import_others_value.get()

        username = self.user_name_entry.get().strip()
        password = self.password_entry.get().strip()
        two_factor_code = self.two_factor_entry.get().strip()

        self._display_node_subprocess(
            [
                INVENTORY_IMPORT_SCRIPT,
                INVENTORY_IMPORT_FILE,
                str(regular_inventory),
                str(storage_units),
                str(import_cases),
                str(import_sticker_capsules),
                str(import_stickers),
                str(import_others),
                username,
                password,
                two_factor_code,
            ]
        )

        self.parent.destroy()

    def _display_node_subprocess(self, node_cmd):
        text_window = tk.Toplevel(self.editor_frame)
        text_window.title(IMPORT_INVENTORY_PROCESS_TITLE)
        text_window.geometry(IMPORT_INVENTORY_PROCESS_SIZE)
        text_window.focus_set()

        process_frame = InventoryImportProcessFrame(text_window, self.editor_frame)
        process_frame.pack(expand=True, fill="both", padx=15, pady=15)
        process_frame.console.focus_set()
        process_frame.start(node_cmd)


class InventoryImportProcessFrame(ttk.Frame):
    # pylint: disable=attribute-defined-outside-init
    # Source: https://stackoverflow.com/questions/27327886/issues-intercepting-subprocess-output-in-real-time
    def __init__(self, parent, editor_frame):
        """Initialize the frame that displays the output of the subprocess."""
        super().__init__(parent)
        self.parent = parent
        self.editor_frame = editor_frame
        self._add_widgets()

    def _add_widgets(self):
        """Add a text widget to display the output of the subprocess."""
        self.scrollbar = ttk.Scrollbar(self)
        self.scrollbar.pack(side="right", fill="y", padx=(5, 0))

        self.console = ThemedText(self, wrap="word", yscrollcommand=self.scrollbar.set)
        self.console.config(state="disabled")
        self.console.pack(expand=True, fill="both", padx=10, pady=10)

        self.scrollbar.config(command=self.console.yview)

    def _read_lines(self, process, queue):
        """Read lines from the subprocess output and put them in a queue."""
        while process.poll() is None:
            line = process.stdout.readline()
            if line:
                queue.put(line)

    def start(self, cmd):
        """Start the NodeJS subprocess with the given command and read its output."""
        self.process = node.Popen(
            cmd,
            stdout=PIPE,
            stdin=PIPE,
            stderr=STDOUT,
            text=True,
            encoding="utf-8",
            shell=True,
            cwd=DATA_DIR,
        )
        self.queue = Queue()
        self.thread = Thread(target=self._read_lines, args=(self.process, self.queue), daemon=True)
        self.thread.start()
        self._update_lines()

    def _update_lines(self):
        """Update the text widget with lines from the subprocess output."""
        try:
            line = self.queue.get(block=False)
            self.console.config(state="normal")
            self.console.insert("end", line)
            self.console.config(state="disabled")
            self.console.yview("end")
        except Empty:
            pass

        if self.process.poll() is None or not self.queue.empty():
            self.after(50, self._update_lines)
        else:
            self._cleanup()

    def _cleanup(self):
        """Clean up the process and thread after completion and trigger a config update
        from the newly written inventory file.
        """
        self.process.wait()
        self.thread.join()

        config.read_from_inventory_file()
        self.editor_frame.reload_config_into_tree()
        self.editor_frame.tree.focus_set()
        self.parent.destroy()
