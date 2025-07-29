import tkinter as tk
from tkinter import messagebox, ttk

NEW_CUSTOM_ITEM_TITLE = "Add Custom Item"
NEW_CUSTOM_ITEM_SIZE = "500x200"


class ConfigEditorFrame(ttk.Frame):
    def __init__(self, parent, scraper_config):
        """Initialize the configuration editor frame that allows users to view and edit
        the configuration options.
        """

        super().__init__(parent, style="Card.TFrame", padding=15)

        self.parent = parent
        self.scraper_config = scraper_config
        self._add_widgets()

    def _add_widgets(self):
        """Configure the main editor frame which displays the configuration options in a
        structured way.
        """
        tree = self._configure_treeview()
        tree.pack(expand=True, fill="both")

        button_frame = ConfigEditorButtonFrame(self, self.scraper_config, tree)
        button_frame.pack(side="bottom", padx=10, pady=(0, 10))

    def _make_tree_editable(self, tree):
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
                    if any(left_item_text == section for section in self.scraper_config.sections()):
                        return
                x, y, w, h = tree.bbox(row, column)
                entryedit = ttk.Entry(self)
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
            for widget in self.winfo_children():
                if isinstance(widget, ttk.Entry):
                    widget.destroy()

        def destroy_entry(event):
            """Destroy the entry widget if the user clicks outside of it."""
            if isinstance(event.widget, ttk.Entry):
                event.widget.destroy()

        tree.bind("<Double-1>", set_cell_value)
        self.parent.bind("<MouseWheel>", destroy_entries)  # type: ignore
        self.parent.bind("<Button-1>", destroy_entry)  # type: ignore

    def _configure_treeview(self):
        """Configure a treeview to display and edit configuration options."""
        scrollbar = ttk.Scrollbar(self)
        scrollbar.pack(side="right", fill="y", padx=(5, 0))

        tree = ttk.Treeview(
            self,
            columns=(1,),
            height=10,
            selectmode="browse",
            yscrollcommand=scrollbar.set,
        )
        scrollbar.config(command=tree.yview)

        tree.column("#0", anchor="w", width=200)
        tree.column(1, anchor="w", width=25)
        tree.heading("#0", text="Option")
        tree.heading(1, text="Value")

        for section in self.scraper_config.sections():
            if section == "App Settings":
                continue
            section_level = tree.insert("", "end", iid=section, text=section)
            for config_option, value in self.scraper_config.items(section):
                title_option = config_option.replace("_", " ").title()
                tree.insert(section_level, "end", text=title_option, values=(value,))

        self._make_tree_editable(tree)
        return tree


class ConfigEditorButtonFrame(ttk.Frame):
    def __init__(self, parent, scraper_config, tree):
        """Initialize the button frame that contains buttons for saving the updated
        configuration and adding custom items.
        """

        super().__init__(parent, padding=10)

        self.parent = parent
        self.scraper_config = scraper_config
        self.tree = tree
        self.custom_item_dialog = None

        self._add_widgets()

    def _add_widgets(self):
        """Add buttons to the button frame for saving the configuration and adding
        custom items.
        """
        save_button = self._configure_save_button()
        save_button.pack(side="left", expand=True, padx=5)

        custom_item_button = self._configure_custom_item_button()
        custom_item_button.pack(side="left", expand=True, padx=5)

    def _configure_save_button(self):
        """Configure a button that saves updated options and values from the treeview
        back to the config file.
        """

        def save_config():
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
                    self.scraper_config.set(section_name, config_option, value)

            self.scraper_config.write_to_file()
            if self.scraper_config.valid:
                messagebox.showinfo(
                    "Config Saved", "The configuration has been saved successfully."
                )
            else:
                messagebox.showerror(
                    "Config Error",
                    f"The configuration is invalid. ({self.scraper_config.last_error})",
                )

        save_button = ttk.Button(self, text="Save", command=save_config)
        return save_button

    def _configure_custom_item_button(self):
        """Configure a button that opens an entry dialog to add a custom item to the
        configuration.
        """

        def add_custom_item(item_url, item_owned):
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

            self.scraper_config.set("Custom Items", item_url, item_owned)
            self.scraper_config.write_to_file()
            if self.scraper_config.valid:
                self.tree.insert("Custom Items", "end", text=item_url, values=(item_owned,))
                if self.custom_item_dialog:
                    self.custom_item_dialog.destroy()
            else:
                self.scraper_config.remove_option("Custom Items", item_url)
                messagebox.showerror(
                    "Config Error",
                    f"The configuration is invalid. ({self.scraper_config.last_error})",
                )

        def open_custom_item_dialog():
            """Open a dialog to enter custom item details."""
            self.custom_item_dialog = tk.Toplevel(self.parent)
            self.custom_item_dialog.title(NEW_CUSTOM_ITEM_TITLE)
            self.custom_item_dialog.geometry(NEW_CUSTOM_ITEM_SIZE)

            dialog_frame = ttk.Frame(self.custom_item_dialog, padding=10)
            dialog_frame.pack(expand=True, fill="both")

            ttk.Label(dialog_frame, text="Item URL:").pack(pady=5)
            item_url_entry = ttk.Entry(dialog_frame)
            item_url_entry.pack(fill="x", padx=10)

            ttk.Label(dialog_frame, text="Owned Count:").pack(pady=5)
            item_owned_entry = ttk.Entry(dialog_frame)
            item_owned_entry.pack(fill="x", padx=10)

            add_button = ttk.Button(
                dialog_frame,
                text="Add",
                command=lambda: add_custom_item(item_url_entry.get(), item_owned_entry.get()),
            )
            add_button.pack(pady=10)

        custom_item_button = ttk.Button(
            self, text="Add Custom Item", command=open_custom_item_dialog
        )
        return custom_item_button
