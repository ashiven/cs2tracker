import tkinter as tk
from shutil import copy
from tkinter import messagebox, ttk

from cs2tracker.constants import CONFIG_FILE, CONFIG_FILE_BACKUP
from cs2tracker.util import get_config

ADD_CUSTOM_ITEM_TITLE = "Add Custom Item"
ADD_CUSTOM_ITEM_SIZE = "500x200"

config = get_config()


class ConfigEditorFrame(ttk.Frame):
    def __init__(self, parent):
        """Initialize the configuration editor frame that allows users to view and edit
        the configuration options.
        """

        super().__init__(parent, style="Card.TFrame", padding=15)

        self.parent = parent
        self._add_widgets()

    def _add_widgets(self):
        """Configure the main editor frame which displays the configuration options in a
        structured way.
        """
        self._configure_treeview()
        self.tree.pack(expand=True, fill="both")

        button_frame = ConfigEditorButtonFrame(self, self.tree)
        button_frame.pack(side="bottom", padx=10, pady=(0, 10))

    def _set_cell_value(self, event):
        """
        Set the value of a cell in the treeview to be editable when double- clicked.

        Source: https://stackoverflow.com/questions/75787251/create-an-editable-tkinter-treeview-with-keyword-connection
        """

        def save_edit(event):
            self.tree.set(row, column=column, value=event.widget.get())
            event.widget.destroy()

        try:
            row = self.tree.identify_row(event.y)
            column = self.tree.identify_column(event.x)
            item_text = self.tree.set(row, column)
            if item_text.strip() == "":
                left_item_text = self.tree.item(row, "text")
                # Don't allow editing of section headers
                if any(left_item_text == section for section in config.sections()):
                    return
            x, y, w, h = self.tree.bbox(row, column)
            entryedit = ttk.Entry(self)
            entryedit.place(x=x, y=y, width=w, height=h + 3)  # type: ignore
            entryedit.insert("end", item_text)
            entryedit.bind("<Return>", save_edit)
            entryedit.focus_set()
            entryedit.grab_set()
        except Exception:
            pass

    def _destroy_entries(self, _):
        """Destroy any entry widgets in the treeview on an event, such as a mouse wheel
        movement.
        """
        for widget in self.winfo_children():
            if isinstance(widget, ttk.Entry):
                widget.destroy()

    def _destroy_entry(self, event):
        """Destroy the entry widget on an even targeting it."""
        if isinstance(event.widget, ttk.Entry):
            event.widget.destroy()

    def _make_tree_editable(self):
        """Add a binding to the treeview that allows double-clicking on a cell to edit
        its value.
        """
        self.tree.bind("<Double-1>", self._set_cell_value)
        self.parent.bind("<MouseWheel>", self._destroy_entries)  # type: ignore
        self.parent.bind("<Button-1>", self._destroy_entry)  # type: ignore

    def _load_config_into_tree(self):
        """Load the configuration options into the treeview for display and editing."""
        for section in config.sections():
            if section == "App Settings":
                continue
            section_level = self.tree.insert("", "end", iid=section, text=section)
            for config_option, value in config.items(section):
                title_option = config_option.replace("_", " ").title()
                self.tree.insert(section_level, "end", text=title_option, values=[value])

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
        self.tree.column(1, anchor="w", width=25)
        self.tree.heading("#0", text="Option")
        self.tree.heading(1, text="Value")

        self._load_config_into_tree()
        self._make_tree_editable()


class ConfigEditorButtonFrame(ttk.Frame):
    def __init__(self, parent, tree):
        """Initialize the button frame that contains buttons for saving the updated
        configuration and adding custom items.
        """

        super().__init__(parent, padding=10)

        self.parent = parent
        self.tree = tree
        self.custom_item_dialog = None

        self._add_widgets()

    def _add_widgets(self):
        """Add buttons to the button frame for saving the configuration and adding
        custom items.
        """
        save_button = ttk.Button(self, text="Save", command=self._save_config)
        save_button.pack(side="left", expand=True, padx=5)

        reset_button = ttk.Button(self, text="Reset", command=self._reset_config)
        reset_button.pack(side="left", expand=True, padx=5)

        custom_item_button = ttk.Button(self, text="Add Custom Item", command=self._add_custom_item)
        custom_item_button.pack(side="left", expand=True, padx=5)

        import_inventory_button = ttk.Button(
            self, text="Import Steam Inventory", command=self._import_steam_inventory
        )
        import_inventory_button.pack(side="left", expand=True, padx=5)

    def _reload_config_into_tree(self):
        """Reload the configuration options into the treeview for display and
        editing.
        """
        for item in self.tree.get_children():
            self.tree.delete(item)

        for section in config.sections():
            if section == "App Settings":
                continue
            section_level = self.tree.insert("", "end", iid=section, text=section)
            for config_option, value in config.items(section):
                title_option = config_option.replace("_", " ").title()
                self.tree.insert(section_level, "end", text=title_option, values=[value])

    def _save_config(self):
        """Save the current configuration from the treeview to the config file."""
        for child in self.tree.get_children():
            for item in self.tree.get_children(child):
                title_option = self.tree.item(item, "text")
                config_option = title_option.lower().replace(" ", "_")
                value = self.tree.item(item, "values")[0]
                section = self.tree.parent(item)
                section_name = self.tree.item(section, "text")
                if section_name == "Custom Items":
                    # custom items are already saved upon creation (Saving them again would result in duplicates)
                    continue
                config.set(section_name, config_option, value)

        config.write_to_file()
        if config.valid:
            messagebox.showinfo("Config Saved", "The configuration has been saved successfully.")
        else:
            config.load()
            self._reload_config_into_tree()
            messagebox.showerror(
                "Config Error",
                f"The configuration is invalid. ({config.last_error})",
            )

    def _reset_config(self):
        """Reset the configuration file to its default state."""
        confirm = messagebox.askokcancel(
            "Reset Config", "Are you sure you want to reset the configuration?"
        )
        if confirm:
            copy(CONFIG_FILE_BACKUP, CONFIG_FILE)
            config.load()
            self._reload_config_into_tree()

    def _add_custom_item(self):
        """Open a dialog to enter custom item details."""
        self.custom_item_dialog = tk.Toplevel(self.parent)
        self.custom_item_dialog.title(ADD_CUSTOM_ITEM_TITLE)
        self.custom_item_dialog.geometry(ADD_CUSTOM_ITEM_SIZE)

        custom_item_frame = CustomItemFrame(self, self.tree)
        custom_item_frame.pack(expand=True, fill="both")

    def _import_steam_inventory(self):
        pass


class CustomItemFrame(ttk.Frame):
    def __init__(self, parent, tree):
        """Initialize the custom item frame that allows users to add custom items."""
        super().__init__(parent, style="Card.TFrame", padding=15)
        self.parent = parent
        self.tree = tree
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

    def _add_custom_item(self, item_url, item_owned):
        """Add a custom item to the configuration."""
        if not item_url or not item_owned:
            messagebox.showerror("Input Error", "All fields must be filled out.")
            return

        try:
            if int(item_owned) < 0:
                raise ValueError("Owned count must be a non-negative integer.")
        except ValueError as error:
            messagebox.showerror("Input Error", f"Invalid owned count: {error}")
            return

        config.set("Custom Items", item_url, item_owned)
        config.write_to_file()
        if config.valid:
            self.tree.insert("Custom Items", "end", text=item_url, values=(item_owned,))
            if self.custom_item_dialog:
                self.custom_item_dialog.destroy()
                self.custom_item_dialog = None
        else:
            config.remove_option("Custom Items", item_url)
            messagebox.showerror(
                "Config Error",
                f"The configuration is invalid. ({config.last_error})",
            )
