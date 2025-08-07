import tkinter as tk
from queue import Empty, Queue
from shutil import copy
from subprocess import PIPE, STDOUT
from threading import Thread
from tkinter import messagebox, ttk

from nodejs import node
from ttk_text import ThemedText

from cs2tracker.config import CUSTOM_SECTIONS, get_config
from cs2tracker.constants import (
    CONFIG_FILE,
    CONFIG_FILE_BACKUP,
    DATA_DIR,
    INVENTORY_IMPORT_FILE,
    INVENTORY_IMPORT_SCRIPT,
)
from cs2tracker.util.tkinter import centered, size_info

ADD_CUSTOM_ITEM_TITLE = "Add Custom Item"
ADD_CUSTOM_ITEM_SIZE = "500x230"

IMPORT_INVENTORY_TITLE = "Import Steam Inventory"
IMPORT_INVENTORY_SIZE = "700x350"

IMPORT_INVENTORY_PROCESS_TITLE = "Importing Steam Inventory..."
IMPORT_INVENTORY_PROCESS_SIZE = "700x500"

config = get_config()


class ConfigEditorFrame(ttk.Frame):
    def __init__(self, window):
        """Initialize the configuration editor frame that allows users to view and edit
        the configuration options.
        """
        super().__init__(window, padding=15)

        self.window = window
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
                "Config Error",
                f"The configuration is invalid. ({config.last_error})",
                parent=self.window,
            )
        self.window.focus_set()
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
            item = selected[0]
            section_name = self.tree.parent(item)
            if section_name in CUSTOM_SECTIONS:
                next_option = self.tree.next(item)
                self.tree.delete(item)
                self.save_config()
                if next_option:
                    self.tree.focus(next_option)
                    self.tree.selection_set(next_option)
                else:
                    self.tree.focus(section_name)
                    self.tree.selection_set(section_name)

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
        self.window.bind("<MouseWheel>", self._destroy_entry)
        self.window.bind("<Escape>", self._destroy_entry)

    def _load_config_into_tree(self):
        """Load the configuration options into the treeview for display and editing."""
        for section in config.sections():
            # App Settings are internal and shouldn't be displayed to the user
            if section == "App Settings":
                continue

            section_level = self.tree.insert("", "end", iid=section, text=section)
            sorted_section_items = sorted(config.items(section))
            for config_option, value in sorted_section_items:
                if section not in ("User Settings", "App Settings"):
                    option_name = config.option_to_name(config_option, href=True)
                else:
                    option_name = config.option_to_name(config_option)
                self.tree.insert(
                    section_level,
                    "end",
                    iid=f"{section}-{option_name}",
                    text=option_name,
                    values=[value],
                )

        self.tree.focus("User Settings")
        self.tree.selection_set("User Settings")

    def reload_config_into_tree(self):
        """Reload the configuration options into the treeview for display and editing
        and maintain the users current selection.
        """
        selected = self.tree.selection()
        selected_text, selected_section = None, None
        if selected:
            selected_text = self.tree.item(selected[0], "text")
            selected_section = self.tree.parent(selected[0])

        for item in self.tree.get_children():
            self.tree.delete(item)
        self._load_config_into_tree()

        if selected_section:
            self.tree.item(selected_section, open=True)
            self.tree.focus(f"{selected_section}-{selected_text}")
            self.tree.selection_set(f"{selected_section}-{selected_text}")
        elif selected:
            self.tree.focus(selected_text)
            self.tree.selection_set(selected_text)  # type: ignore

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

        self.custom_item_window = None
        self.steam_inventory_window = None
        self._add_widgets()

    def _add_widgets(self):
        """Add buttons to the button frame for saving the configuration and adding
        custom items.
        """
        reset_button = ttk.Button(self, text="Reset", command=self._reset_config)
        reset_button.pack(side="left", expand=True, padx=5)

        custom_item_button = ttk.Button(self, text="Add Item", command=self._add_custom_item)
        custom_item_button.pack(side="left", expand=True, padx=5)

        def open_custom_enter(_):
            selected = self.editor_frame.tree.selection()
            if selected and not self.editor_frame.tree.parent(selected[0]):
                selected_section = self.editor_frame.tree.item(selected[0], "text")
                if selected_section in CUSTOM_SECTIONS and not self.editor_frame.tree.get_children(
                    selected_section
                ):
                    custom_item_button.invoke()

        def open_custom_click(event):
            selected_section = self.editor_frame.tree.identify_row(event.y)
            if selected_section in CUSTOM_SECTIONS and not self.editor_frame.tree.get_children(
                selected_section
            ):
                custom_item_button.invoke()

        self.editor_frame.tree.bind("<Return>", open_custom_enter, add="+")
        self.editor_frame.tree.bind("<Double-1>", open_custom_click, add="+")

        import_inventory_button = ttk.Button(
            self, text="Import Steam Inventory", command=self._import_steam_inventory
        )
        import_inventory_button.pack(side="left", expand=True, padx=5)

    def _reset_config(self):
        """Reset the configuration file to its default state."""
        confirm = messagebox.askokcancel(
            "Reset Config",
            "Are you sure you want to reset the configuration?",
            parent=self.editor_frame,
        )
        if confirm:
            copy(CONFIG_FILE_BACKUP, CONFIG_FILE)
            config.load_from_file()
            self.editor_frame.reload_config_into_tree()
        self.editor_frame.focus_set()
        self.editor_frame.tree.focus_set()

    def _add_custom_item(self):
        """Open a window to add a new custom item or lift the existing one if it is
        already open.
        """
        if self.custom_item_window is None or not self.custom_item_window.winfo_exists():
            self._open_custom_item_window()
        else:
            self.custom_item_window.lift()
            self.custom_item_window.focus_set()

    def _open_custom_item_window(self):
        """Open a window to add a new custom item."""
        self.custom_item_window = tk.Toplevel(self.editor_frame)
        self.custom_item_window.title(ADD_CUSTOM_ITEM_TITLE)
        self.custom_item_window.geometry(centered(self.custom_item_window, ADD_CUSTOM_ITEM_SIZE))
        self.custom_item_window.minsize(*size_info(ADD_CUSTOM_ITEM_SIZE))
        self.custom_item_window.focus_set()

        def on_close():
            self.custom_item_window.destroy()  # type: ignore
            self.editor_frame.tree.focus_set()

        self.custom_item_window.protocol("WM_DELETE_WINDOW", on_close)

        custom_item_frame = CustomItemFrame(self.custom_item_window, self.editor_frame)
        custom_item_frame.pack(expand=True, fill="both", padx=15, pady=15)

    def _import_steam_inventory(self):
        """Open a window to import the user's Steam inventory or lift the existing one
        if it is already open.
        """
        if self.steam_inventory_window is None or not self.steam_inventory_window.winfo_exists():
            self._open_steam_inventory_window()
        else:
            self.steam_inventory_window.lift()
            self.steam_inventory_window.focus_set()

    def _open_steam_inventory_window(self):
        """Open a window to import the user's Steam inventory."""
        self.steam_inventory_window = tk.Toplevel(self.editor_frame)
        self.steam_inventory_window.title(IMPORT_INVENTORY_TITLE)
        self.steam_inventory_window.geometry(
            centered(self.steam_inventory_window, IMPORT_INVENTORY_SIZE)
        )
        self.steam_inventory_window.minsize(*size_info(IMPORT_INVENTORY_SIZE))
        self.steam_inventory_window.focus_set()

        def on_close():
            self.steam_inventory_window.destroy()  # type: ignore
            self.editor_frame.tree.focus_set()

        self.steam_inventory_window.protocol("WM_DELETE_WINDOW", on_close)

        steam_inventory_frame = InventoryImportFrame(self.steam_inventory_window, self.editor_frame)
        steam_inventory_frame.pack(expand=True, fill="both", padx=15, pady=15)


class CustomItemFrame(ttk.Frame):
    def __init__(self, window, editor_frame):
        """Initialize the custom item frame that allows users to add custom items."""
        super().__init__(window, style="Card.TFrame", padding=15)
        self.window = window
        self.editor_frame = editor_frame
        self._add_widgets()

    def _add_widgets(self):
        """Add widgets to the custom item frame for entering item details."""
        ttk.Label(self, text="Steam Market Listing URL:").pack(pady=5)
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
        self.window.bind("<Return>", lambda _: add_button.invoke())

    def _update_existing(self, section, item_name, item_owned):
        """
        Try to update an item in the treeview with the new item details.

        :return: True if the item was updated, False if it was not found.
        """
        for existing_item in self.editor_frame.tree.get_children(section):
            existing_item_name = self.editor_frame.tree.item(existing_item, "text")
            if item_name == existing_item_name:
                self.editor_frame.tree.set(existing_item, column="#1", value=item_owned)
                self.editor_frame.focus_set()
                self.editor_frame.save_config()
                self.window.destroy()
                return True
        return False

    def _get_insert_index(self, item_name, section):
        """Get the index to insert the new item in alphabetical order."""
        insert_index = "end"
        for existing_item_index, existing_item in enumerate(
            self.editor_frame.tree.get_children(section)
        ):
            existing_item_name = self.editor_frame.tree.item(existing_item, "text")
            if item_name < existing_item_name:
                insert_index = existing_item_index
                break
        return insert_index

    def _identify_custom_section(self, item_name):
        # pylint: disable=too-many-return-statements
        """Given an item name, identify the custom section it belongs to."""
        if "Patch Pack" in item_name or "Patch Collection" in item_name:
            return "Patch Packs"
        elif "Patch |" in item_name:
            return "Patches"
        elif "Sticker |" in item_name:
            return "Stickers"
        elif "Charm |" in item_name:
            return "Charms"
        elif "Souvenir" in item_name and "|" not in item_name:
            return "Souvenirs"
        elif "★ " in item_name:
            return "Special Items"
        elif " | " in item_name and "(" in item_name and ")" in item_name:
            return "Skins"
        elif "Music Kit |" in item_name:
            return "Others"
        elif " | " in item_name:
            return "Agents"
        else:
            return "Others"

    def _add_custom_item(self, item_href, item_owned):
        """Add a custom item to the configuration."""
        if not item_href or not item_owned:
            messagebox.showerror(
                "Input Error", "All fields must be filled out.", parent=self.window
            )
            return
        if config.option_exists(item_href, exclude_sections=CUSTOM_SECTIONS):
            messagebox.showerror(
                "Item Exists", "This item already exists in another section.", parent=self.window
            )
            return

        try:
            item_name = config.option_to_name(item_href, href=True)
        except ValueError as error:
            messagebox.showerror("Invalid URL", str(error), parent=self.window)
            return

        for section in CUSTOM_SECTIONS:
            if self._update_existing(section, item_name, item_owned):
                return

        section = self._identify_custom_section(item_name)
        insert_index = self._get_insert_index(item_name, section)
        self.editor_frame.tree.insert(
            section,
            insert_index,
            iid=f"{section}-{item_name}",
            text=item_name,
            values=[item_owned],
        )
        self.editor_frame.save_config()
        self.window.destroy()


class InventoryImportFrame(ttk.Frame):
    # pylint: disable=too-many-instance-attributes
    def __init__(self, window, editor_frame):
        """Initialize the inventory import frame that allows users to import their Steam
        inventory.
        """
        super().__init__(window, padding=10)
        self.window = window
        self.editor_frame = editor_frame
        self._add_widgets()

    def _add_widgets(self):
        """Add widgets to the inventory import frame."""
        self._configure_entries()
        self.user_name_label.pack(pady=5)
        self.user_name_entry.pack(fill="x", expand=True, padx=10)
        self.password_label.pack(pady=5)
        self.password_entry.pack(fill="x", expand=True, padx=10)
        self.two_factor_label.pack(pady=5)
        self.two_factor_entry.pack(fill="x", expand=True, padx=10)
        self.import_button.pack(pady=10)
        self.entry_frame.pack(side="left", padx=10, pady=(0, 20), fill="both", expand=True)

        self._configure_checkboxes()
        self.storage_units_checkbox.pack(anchor="w", padx=10, pady=5)
        self.regular_inventory_checkbox.pack(anchor="w", padx=10, pady=5)
        self.import_cases_checkbox.pack(anchor="w", padx=10, pady=5)
        self.import_sticker_capsules_checkbox.pack(anchor="w", padx=10, pady=5)
        self.import_stickers_checkbox.pack(anchor="w", padx=10, pady=5)
        self.import_others_checkbox.pack(anchor="w", padx=10, pady=5)
        self.checkbox_frame.pack(side="left", padx=10, pady=(0, 20), fill="both", expand=True)

    def _configure_checkboxes(self):
        # pylint: disable=attribute-defined-outside-init
        """Configure the checkboxes for selecting what to import from the Steam
        inventory.
        """
        self.checkbox_frame = ttk.LabelFrame(self, text="Import Settings", padding=15)

        self.regular_inventory_value = tk.BooleanVar(value=False)
        self.regular_inventory_checkbox = ttk.Checkbutton(
            self.checkbox_frame,
            text="Regular Inventory",
            variable=self.regular_inventory_value,
            style="Switch.TCheckbutton",
        )

        self.storage_units_value = tk.BooleanVar(value=True)
        self.storage_units_checkbox = ttk.Checkbutton(
            self.checkbox_frame,
            text="Storage Units",
            variable=self.storage_units_value,
            style="Switch.TCheckbutton",
        )

        self.import_cases_value = tk.BooleanVar(value=True)
        self.import_cases_checkbox = ttk.Checkbutton(
            self.checkbox_frame,
            text="Import Cases",
            variable=self.import_cases_value,
            style="Switch.TCheckbutton",
        )

        self.import_sticker_capsules_value = tk.BooleanVar(value=True)
        self.import_sticker_capsules_checkbox = ttk.Checkbutton(
            self.checkbox_frame,
            text="Import Sticker Capsules",
            variable=self.import_sticker_capsules_value,
            style="Switch.TCheckbutton",
        )

        self.import_stickers_value = tk.BooleanVar(value=False)
        self.import_stickers_checkbox = ttk.Checkbutton(
            self.checkbox_frame,
            text="Import Stickers",
            variable=self.import_stickers_value,
            style="Switch.TCheckbutton",
        )

        self.import_others_value = tk.BooleanVar(value=False)
        self.import_others_checkbox = ttk.Checkbutton(
            self.checkbox_frame,
            text="Import Other Items",
            variable=self.import_others_value,
            style="Switch.TCheckbutton",
        )

    def _configure_entries(self):
        # pylint: disable=attribute-defined-outside-init
        """Configure the entry fields for Steam username, password, and two-factor
        code.
        """
        self.entry_frame = ttk.Frame(self, style="Card.TFrame", padding=15)

        self.user_name_label = ttk.Label(self.entry_frame, text="Steam Username:")
        self.user_name_entry = ttk.Entry(self.entry_frame, justify="center", font=("Helvetica", 11))

        self.password_label = ttk.Label(self.entry_frame, text="Steam Password:")
        self.password_entry = ttk.Entry(
            self.entry_frame, show="*", justify="center", font=("Helvetica", 11)
        )

        self.two_factor_label = ttk.Label(self.entry_frame, text="Steam Guard Code:")
        self.two_factor_entry = ttk.Entry(
            self.entry_frame, justify="center", font=("Helvetica", 11)
        )

        self.import_button = ttk.Button(
            self.entry_frame, text="Import", command=self._import_inventory, state="disabled"
        )

        def check_form(_):
            if (
                len(self.user_name_entry.get().strip()) > 0
                and len(self.password_entry.get().strip()) > 0
                and len(self.two_factor_entry.get().strip()) > 0
            ):
                self.import_button.configure(state="normal")
            else:
                self.import_button.configure(state="disabled")

        self.window.bind("<KeyRelease>", check_form)
        self.window.bind("<Return>", lambda _: self.import_button.invoke())

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

        self.window.destroy()

    def _display_node_subprocess(self, node_cmd):
        console_window = tk.Toplevel(self.editor_frame)
        console_window.title(IMPORT_INVENTORY_PROCESS_TITLE)
        console_window.geometry(centered(console_window, IMPORT_INVENTORY_PROCESS_SIZE))
        console_window.minsize(*size_info(IMPORT_INVENTORY_PROCESS_SIZE))
        console_window.focus_force()

        def on_close():
            console_window.destroy()
            config.read_from_inventory_file()
            self.editor_frame.reload_config_into_tree()
            self.editor_frame.tree.focus_set()

        console_window.protocol("WM_DELETE_WINDOW", on_close)

        process_frame = InventoryImportProcessFrame(console_window, self.editor_frame)
        process_frame.pack(expand=True, fill="both", padx=15, pady=15)
        process_frame.console.focus_force()
        process_frame.start(node_cmd)


class InventoryImportProcessFrame(ttk.Frame):
    # pylint: disable=attribute-defined-outside-init
    # Source: https://stackoverflow.com/questions/27327886/issues-intercepting-subprocess-output-in-real-time
    def __init__(self, window, editor_frame):
        """Initialize the frame that displays the output of the subprocess."""
        super().__init__(window)
        self.window = window
        self.editor_frame = editor_frame
        self._add_widgets()

    def _add_widgets(self):
        """Add a text widget to display the output of the subprocess."""
        self.scrollbar = ttk.Scrollbar(self)
        self.scrollbar.pack(side="right", fill="y", padx=(5, 0))

        self.console = ThemedText(self, wrap="word", yscrollcommand=self.scrollbar.set)
        self.console.config(state="disabled")
        self.console.tag_configure("error", foreground="red")
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
            if "[ERROR]" in line:
                self.console.insert("end", line, "error")
            else:
                self.console.insert("end", line)
            self.console.config(state="disabled")
            self.console.yview("end")
        except Empty:
            pass

        if self.process.poll() is None or not self.queue.empty():
            self.after(35, self._update_lines)
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
        self.window.destroy()
