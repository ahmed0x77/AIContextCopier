import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, filedialog
import os
import json
import pyperclip

# --- Constants ---
SETTINGS_FILE = "app_settings.json"

# --- UI Classes ---

class SettingsWindow(ctk.CTkToplevel):
    """A pop-up window for managing persistent application settings."""
    
    def __init__(self, master, *args, **kwargs):
        """Initializes the Settings window."""
        super().__init__(master, *args, **kwargs)
        self.app = master
        self.title("Settings")
        
        # --- Window Sizing and Centering ---
        window_width, window_height = 400, 200
        self.geometry(f"{window_width}x{window_height}")
        self.update_idletasks()
        
        master_x, master_y = self.master.winfo_x(), self.master.winfo_y()
        master_width, master_height = self.master.winfo_width(), self.master.winfo_height()
        center_x = master_x + (master_width // 2) - (window_width // 2)
        center_y = master_y + (master_height // 2) - (window_height // 2)
        self.geometry(f"+{center_x}+{center_y}")

        # --- Window Behavior ---
        self.transient(master)  # Keep on top of the main window
        self.grab_set()         # Make modal (block interaction with main window)

        # --- Widgets ---
        ctk.CTkLabel(self, text="Options", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10,5))
        
        # The checkbox's variable is the one in the main app, so changes are instant.
        # The command saves settings automatically whenever the checkbox is toggled.
        self.include_tree_checkbox = ctk.CTkCheckBox(self,
            text="Include Project Structure Tree in Clipboard",
            variable=self.app.include_tree_var,
            command=self.app.save_settings)
        self.include_tree_checkbox.pack(pady=10, padx=20)
        
        close_button = ctk.CTkButton(self, text="Close", command=self.destroy)
        close_button.pack(pady=20)


class DirectorySelectorWindow(ctk.CTkToplevel):
    """A custom pop-up window for selecting favorite or recent directories."""

    def __init__(self, master, *args, **kwargs):
        """Initializes the Directory Selector window."""
        super().__init__(master, *args, **kwargs)
        self.app = master
        self.title("Select a Project")
        
        window_width, window_height = 600, 450
        self.geometry(f"{window_width}x{window_height}")
        self.update_idletasks()
        
        master_x, master_y = self.master.winfo_x(), self.master.winfo_y()
        master_width, master_height = self.master.winfo_width(), self.master.winfo_height()
        center_x = master_x + (master_width // 2) - (window_width // 2)
        center_y = master_y + (master_height // 2) - (window_height // 2)
        self.geometry(f"+{center_x}+{center_y}")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1); self.grid_rowconfigure(3, weight=1)
        self.transient(master); self.grab_set()

        # --- Widgets ---
        fav_frame = ctk.CTkFrame(self)
        fav_frame.grid(row=1, column=0, padx=10, pady=(10, 5), sticky="nsew")
        fav_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(fav_frame, text="Favorites ⭐", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=10, pady=5)
        self.fav_list_frame = ctk.CTkScrollableFrame(fav_frame, fg_color="transparent")
        self.fav_list_frame.pack(fill="both", expand=True, padx=5, pady=(0,5))
        
        rec_frame = ctk.CTkFrame(self)
        rec_frame.grid(row=3, column=0, padx=10, pady=5, sticky="nsew")
        rec_frame.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(rec_frame, text="Recent", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=10, pady=5)
        self.rec_list_frame = ctk.CTkScrollableFrame(rec_frame, fg_color="transparent")
        self.rec_list_frame.pack(fill="both", expand=True, padx=5, pady=(0,5))

        browse_button = ctk.CTkButton(self, text="Browse for another folder...", command=self.browse_and_select)
        browse_button.grid(row=4, column=0, padx=10, pady=10, sticky="ew")
        
        self.populate_lists()

    def populate_lists(self):
        """Clears and fills the Favorites and Recents lists from app memory."""
        for widget in self.fav_list_frame.winfo_children(): widget.destroy()
        for widget in self.rec_list_frame.winfo_children(): widget.destroy()
        for path in self.app.favorite_folders: self.create_list_entry(self.fav_list_frame, path, is_favorite=True)
        for path in self.app.recent_folders:
            if path not in self.app.favorite_folders: self.create_list_entry(self.rec_list_frame, path, is_favorite=False)
    
    def create_list_entry(self, parent_frame, path, is_favorite):
        """Creates a single entry (row) in the Favorites or Recents list."""
        entry_frame = ctk.CTkFrame(parent_frame)
        entry_frame.pack(fill="x", pady=2)
        entry_frame.grid_columnconfigure(0, weight=1)
        
        path_button = ctk.CTkButton(entry_frame, text=path, anchor="w", fg_color="transparent", command=lambda p=path: self.select_path(p))
        path_button.grid(row=0, column=0, sticky="ew", padx=5)
        
        if is_favorite:
            remove_button = ctk.CTkButton(entry_frame, text="X", width=25, height=25, command=lambda p=path: self.unfavorite(p))
            remove_button.grid(row=0, column=1, padx=(0,5))
        else:
            fav_button = ctk.CTkButton(entry_frame, text="⭐", width=25, height=25, command=lambda p=path: self.favorite(p))
            fav_button.grid(row=0, column=1, padx=(0,5))

    def select_path(self, path):
        """Handles the selection of a path from the lists."""
        if os.path.isdir(path):
            self.app.set_project_directory(path)
            self.destroy()
        else:
            # If a path is no longer valid, remove it from memory and refresh the list.
            self.app.status_label.configure(text=f"Directory not found: {path}", text_color="orange")
            if path in self.app.recent_folders: self.app.recent_folders.remove(path)
            if path in self.app.favorite_folders: self.app.favorite_folders.remove(path)
            self.app.save_settings(); self.populate_lists()

    def favorite(self, path):
        """Promotes a recent path to favorites."""
        self.app.favorite_folder(path); self.populate_lists()
    
    def unfavorite(self, path):
        """Removes a path from favorites."""
        self.app.unfavorite_folder(path); self.populate_lists()
    
    def browse_and_select(self):
        """Opens the standard system file dialog."""
        directory = filedialog.askdirectory(title="Select Project Directory")
        if directory: self.app.set_project_directory(directory); self.destroy()


class FileContentCopier(ctk.CTk):
    """The main application window for browsing and copying file contents."""

    def __init__(self):
        """Initializes the main application UI and loads settings."""
        super().__init__()
        self.title("File Content Copier V5.6")
        self.geometry("1200x750")
        
        # Set app icon
        try:
            self.iconbitmap("app_icon.ico")
        except:
            pass  # Continue if icon file is not found

        # --- 1. App Setup & Variables ---
        self.icon_map = { 
            "folder": "📁", ".py": "🐍", ".js": "📜", ".ts": "📜", ".tsx": "📜", ".html": "🎨", 
            ".css": "🎨", ".json": "🗃️", ".md": "📝", ".sql": "🗄️", ".sh": "⚙️", 
            ".yml": "⚙️", ".yaml": "⚙️", ".txt": "📄", ".gitignore": "🗑️", "file": "📄" 
        }
        self.root_directory, self.selected_items = "", {}
        self.favorite_folders, self.recent_folders = [], []
        self.full_tree_data = []  # Store complete tree data for search functionality
        self.is_pulsing = True  # Control pulsing animation
        
        # This variable is shared with the SettingsWindow
        self.include_tree_var = tk.BooleanVar()
        self.load_settings()

        # --- 2. Main Window Layout ---
        self.grid_columnconfigure(0, weight=5, uniform="group1")
        self.grid_columnconfigure(1, weight=1, uniform="group1")
        self.grid_columnconfigure(2, weight=3, uniform="group1")
        self.grid_rowconfigure(1, weight=1)

        # --- 3. Top Frame (Directory Selection & Settings) ---
        self.top_frame = ctk.CTkFrame(self)
        self.top_frame.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="ew")
        
        self.select_dir_button = ctk.CTkButton(self.top_frame, text="Select Project Directory", command=self.open_directory_selector)
        self.select_dir_button.pack(side="left", padx=(0, 10))
        self.dir_label = ctk.CTkLabel(self.top_frame, text="No directory selected.", wraplength=800, anchor="w")
        self.dir_label.pack(side="left", fill="x", expand=True)
        
        self.settings_button = ctk.CTkButton(self.top_frame, text="⚙️", width=30, command=self.open_settings_window)
        self.settings_button.pack(side="right", padx=(0,5))

        # --- 4. Left Panel (Tree Browser with Search) ---
        self.tree_panel = ctk.CTkFrame(self)
        self.tree_panel.grid(row=1, column=0, padx=(10, 5), pady=5, sticky="nsew")
        self.tree_panel.grid_rowconfigure(1, weight=1); self.tree_panel.grid_columnconfigure(0, weight=1)
        
        # Search bar above the tree
        self.search_frame = ctk.CTkFrame(self.tree_panel)
        self.search_frame.grid(row=0, column=0, columnspan=2, padx=5, pady=(5, 0), sticky="ew")
        self.search_frame.grid_columnconfigure(0, weight=1)
        
        self.search_entry = ctk.CTkEntry(self.search_frame, placeholder_text="Search files and folders...", height=35)
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(5, 5), pady=5)
        self.search_entry.bind('<KeyRelease>', self.on_search)
        
        self.clear_search_button = ctk.CTkButton(self.search_frame, text="✕", width=35, height=35, command=self.clear_search)
        self.clear_search_button.grid(row=0, column=1, padx=(0, 5), pady=5)

        self.style = ttk.Style()
        self.style.theme_use("default")
        fg_color, bg_color = ("#DCE4EE", "#2B2B2B")
        self.style.configure("Treeview", background=bg_color, foreground=fg_color, fieldbackground=bg_color, borderwidth=0, rowheight=36, font=('Segoe UI', 16))
        self.style.map('Treeview', background=[('selected', '#2a2d2e')], foreground=[('selected', ctk.ThemeManager.theme["CTkButton"]["fg_color"][1])])
        self.style.configure("Treeview.Heading", background="#565b5e", foreground="white", relief="flat", font=('Segoe UI', 12, 'bold'))
        self.style.map("Treeview.Heading", background=[('active', '#3484F0')])

        self.tree = ttk.Treeview(self.tree_panel, selectmode="extended")
        self.tree.grid(row=1, column=0, sticky="nsew")
        self.tree_scrollbar = ctk.CTkScrollbar(self.tree_panel, command=self.tree.yview)
        self.tree_scrollbar.grid(row=1, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=self.tree_scrollbar.set)
        self.tree["columns"] = ("fullpath",); self.tree.column("#0", anchor="w", width=400); self.tree.column("fullpath", width=0, stretch=tk.NO)
        self.tree.heading("#0", text="Project Browser", anchor="w")
        
        # Empty state message (use place, not grid, to avoid re-grid side-effects)
        self.empty_state_label = ctk.CTkLabel(
            self.tree_panel,
            text="📁 No Project Selected\n\nClick 'Select Project Directory' above\nto browse your project files",
            font=ctk.CTkFont(size=16),
            text_color="#888888",
            justify="center"
        )
        # Hidden by default; we will place it when needed
        self.empty_state_label.place_forget()

        # --- 5. Middle Panel (Control Buttons) ---
        self.controls_panel = ctk.CTkFrame(self)
        self.controls_panel.grid(row=1, column=1, padx=5, pady=5, sticky="ns")
        self.controls_panel.grid_rowconfigure((0, 3), weight=1)
        self.add_button = ctk.CTkButton(self.controls_panel, text="Add >>", command=self.add_selected_item)
        self.add_button.grid(row=1, column=0, pady=10)
        self.remove_button = ctk.CTkButton(self.controls_panel, text="<< Remove", command=self.remove_checked_items, fg_color="#A83232", hover_color="#7A2424")
        self.remove_button.grid(row=2, column=0, pady=10)

        # --- 6. Right Panel (Selected Items List) ---
        self.selected_panel = ctk.CTkFrame(self)
        self.selected_panel.grid(row=1, column=2, padx=(5, 10), pady=5, sticky="nsew")
        self.selected_panel.grid_columnconfigure(0, weight=1); self.selected_panel.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(self.selected_panel, text="Selected Items", font=ctk.CTkFont(weight="bold", size=14)).grid(row=0, column=0, pady=(5,0), padx=10, sticky="w")
        self.selected_items_frame = ctk.CTkScrollableFrame(self.selected_panel, fg_color="transparent")
        self.selected_items_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        
        # --- 7. Bottom Frame (Action Panel) ---
        self.bottom_frame = ctk.CTkFrame(self)
        self.bottom_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=(5, 10), sticky="ew")
        self.copy_button = ctk.CTkButton(self.bottom_frame, text="Copy All Selected Items to Clipboard", command=self.copy_to_clipboard, fg_color="#1F6E43", hover_color="#14482C", border_width=0)
        self.copy_button.pack(pady=10)
        self.status_label = ctk.CTkLabel(self.bottom_frame, text="")
        self.status_label.pack(pady=(0, 5))
        
        # Start pulsing animation for the select directory button
        self.start_pulsing_animation()
        
        # Show empty state initially
        self.show_empty_state()
    
    # --- Settings and Project Management ---
    
    def load_settings(self):
        """Loads favorites, recents, and other settings from the JSON file."""
        try:
            with open(SETTINGS_FILE, 'r') as f: settings = json.load(f)
            self.favorite_folders = settings.get("favorites", [])
            self.recent_folders = settings.get("recents", [])
            self.include_tree_var.set(settings.get("include_tree", True))
        except (FileNotFoundError, json.JSONDecodeError):
            self.favorite_folders, self.recent_folders = [], []
            self.include_tree_var.set(True) # Default to True if no settings file
            
    def save_settings(self):
        """Saves current settings to the JSON file."""
        settings = {
            "favorites": self.favorite_folders,
            "recents": self.recent_folders,
            "include_tree": self.include_tree_var.get()
        }
        with open(SETTINGS_FILE, 'w') as f: json.dump(settings, f, indent=4)

    def open_directory_selector(self):
        """Opens the custom window for choosing a project."""
        DirectorySelectorWindow(self)
        
    def open_settings_window(self):
        """Opens the settings pop-up window."""
        SettingsWindow(self)

    def set_project_directory(self, directory):
        """Loads a new project into the UI, resetting the view."""
        self.root_directory = directory
        self.dir_label.configure(text=f"Project: {self.root_directory}")
        
        # Stop the pulsing animation since a project has been selected
        self.stop_pulsing_animation()
        
        # Hide empty state and show tree
        self.show_tree_view()
        
        # Clear current state
        for i in self.tree.get_children(): self.tree.delete(i)
        for path in list(self.selected_items.keys()): self.remove_item_from_ui(path)
        
        # Build and store the complete tree data for search functionality
        self.full_tree_data = self.build_tree_data(self.root_directory)
        
        # Populate with new project
        self.process_directory("", self.root_directory)
        # Update and save recents
        if directory in self.recent_folders: self.recent_folders.remove(directory)
        self.recent_folders.insert(0, directory); self.recent_folders = self.recent_folders[:5]
        self.save_settings()

    def favorite_folder(self, path):
        """Adds a path to the favorites list and saves."""
        if path not in self.favorite_folders: self.favorite_folders.insert(0, path); self.save_settings()
        
    def unfavorite_folder(self, path):
        """Removes a path from the favorites list and saves."""
        if path in self.favorite_folders: self.favorite_folders.remove(path); self.save_settings()

    # --- Core Application Logic ---

    def process_directory(self, parent_id, path):
        """Recursively populates the tree view with files and folders."""
        try:
            items = os.listdir(path)
            folders = sorted([item for item in items if os.path.isdir(os.path.join(path, item))])
            files = sorted([item for item in items if os.path.isfile(os.path.join(path, item))])
            for item in folders + files:
                abspath = os.path.join(path, item)
                isdir = os.path.isdir(abspath)
                # Get the appropriate icon for the item
                if isdir: icon = self.icon_map.get("folder")
                else: _, extension = os.path.splitext(item); icon = self.icon_map.get(extension.lower(), self.icon_map["file"])
                text = f"{icon}  {item}"
                oid = self.tree.insert(parent_id, "end", text=text, values=[abspath], open=False)
                if isdir: self.process_directory(oid, abspath)
        except OSError as e: print(f"Could not access path: {path}. Reason: {e}")
    
    def build_tree_data(self, path):
        """Builds a data structure representing the complete directory tree."""
        tree_data = []
        try:
            items = os.listdir(path)
            folders = sorted([item for item in items if os.path.isdir(os.path.join(path, item))])
            files = sorted([item for item in items if os.path.isfile(os.path.join(path, item))])
            
            for item in folders + files:
                abspath = os.path.join(path, item)
                isdir = os.path.isdir(abspath)
                
                item_data = {
                    'path': abspath,
                    'name': item,
                    'is_dir': isdir
                }
                
                if isdir:
                    item_data['children'] = self.build_tree_data(abspath)
                
                tree_data.append(item_data)
        except OSError as e:
            print(f"Could not access path: {path}. Reason: {e}")
        
        return tree_data

    def add_selected_item(self):
        """Adds all selected items from the tree view to the right-hand list."""
        selected_ids = self.tree.selection()
        if not selected_ids: return
        added_count = 0
        for item_id in selected_ids:
            item_path = self.tree.item(item_id, "values")[0]
            # 1. Check if the item is already covered by a selected parent folder.
            is_redundant = any(os.path.isdir(ep) and item_path.startswith(os.path.join(ep, '')) for ep in self.selected_items)
            if is_redundant: continue
            # 2. If adding a folder, remove any of its children already in the list.
            if os.path.isdir(item_path):
                for child_path in [p for p in self.selected_items if p.startswith(os.path.join(item_path, ''))]: self.remove_item_from_ui(child_path)
            # 3. Add the new item if it's not a duplicate.
            if item_path not in self.selected_items: self.add_item_to_ui(item_path); added_count += 1
        self.status_label.configure(text=f"Added {added_count} item(s)." if added_count > 0 else "Selected items are already included.", text_color="green" if added_count > 0 else "orange")

    def add_item_to_ui(self, item_path):
        """Adds a single item to the 'Selected Items' list on the right."""
        relative_path = os.path.relpath(item_path, self.root_directory)
        if os.path.isdir(item_path): icon = self.icon_map.get("folder")
        else: _, extension = os.path.splitext(item_path); icon = self.icon_map.get(extension.lower(), self.icon_map["file"])
        display_text = f"{icon} {relative_path}"
        
        checkbox_var = tk.BooleanVar()
        entry_frame = ctk.CTkFrame(self.selected_items_frame)
        entry_frame.pack(fill="x", pady=2)
        entry_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkCheckBox(entry_frame, text="", variable=checkbox_var, width=0).grid(row=0, column=0, padx=5)
        ctk.CTkLabel(entry_frame, text=display_text, anchor="w").grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        ctk.CTkButton(entry_frame, text="X", width=25, height=25, command=lambda p=item_path: self.remove_item_from_ui(p)).grid(row=0, column=2, padx=5, pady=2)
        self.selected_items[item_path] = {'frame': entry_frame, 'var': checkbox_var}
        
        # Update copy button visual state
        self.update_copy_button_state()

    def remove_item_from_ui(self, item_path):
        """Removes a single item from the 'Selected Items' list."""
        if item_path in self.selected_items: self.selected_items.pop(item_path)['frame'].destroy()
        
        # Update copy button visual state
        self.update_copy_button_state()

    def remove_checked_items(self):
        """Removes all items that are checked in the 'Selected Items' list."""
        items_to_remove = [path for path, data in self.selected_items.items() if data['var'].get()]
        if not items_to_remove: self.status_label.configure(text="No items checked for removal.", text_color="orange"); return
        for path in items_to_remove: self.remove_item_from_ui(path)
        self.status_label.configure(text=f"Removed {len(items_to_remove)} item(s).", text_color="green")
        
        # Update copy button visual state (remove_item_from_ui already calls this, but we call it again to ensure it's updated)
        self.update_copy_button_state()

    def _generate_project_tree(self, file_paths):
        """Generates a text-based tree diagram from a flat list of file paths."""
        tree_dict = {}
        for path in file_paths:
            rel_path = os.path.relpath(path, self.root_directory)
            parts = rel_path.replace('\\', '/').split('/')
            current_level = tree_dict
            for part in parts:
                if part not in current_level: current_level[part] = {}
                current_level = current_level[part]

        def _render_tree_recursive(d, prefix=""):
            """Helper function to recursively draw the tree."""
            lines = []
            entries = list(d.keys())
            for i, entry in enumerate(entries):
                connector = "└── " if i == len(entries) - 1 else "├── "
                is_dir = bool(d[entry])
                if is_dir: icon = self.icon_map.get("folder")
                else: _, ext = os.path.splitext(entry); icon = self.icon_map.get(ext.lower(), self.icon_map["file"])
                lines.append(f"{prefix}{connector}{icon} {entry}")
                if d[entry]:
                    extension = "    " if i == len(entries) - 1 else "│   "
                    lines.extend(_render_tree_recursive(d[entry], prefix + extension))
            return lines

        tree_lines = _render_tree_recursive(tree_dict)
        return "\n".join(tree_lines)

    def copy_to_clipboard(self):
        """The main function to gather, format, and copy all content."""
        if not self.selected_items:
            self.status_label.configure(text="No items selected!", text_color="orange"); return
            
        all_content = []
        processed_files, files_to_process = set(), []
        
        # 1. Gather the full list of files to be processed by expanding selected folders.
        for item_path in sorted(self.selected_items.keys()):
            if os.path.isfile(item_path):
                if item_path not in processed_files: files_to_process.append(item_path); processed_files.add(item_path)
            elif os.path.isdir(item_path):
                for dirpath, _, filenames in os.walk(item_path):
                    if any(folder in dirpath for folder in ['.git', '__pycache__', 'node_modules']): continue
                    for filename in filenames:
                        file_path = os.path.join(dirpath, filename)
                        if any(file_path.endswith(ext) for ext in ['.pyc', '.DS_Store']) or file_path in processed_files: continue
                        files_to_process.append(file_path); processed_files.add(file_path)

        # 2. Generate the project tree from the full file list (if enabled).
        if self.include_tree_var.get():
            tree_string = self._generate_project_tree(files_to_process)
            all_content.append(f"**Selected Project Structure:**\n```text\n{os.path.basename(self.root_directory)}/\n{tree_string}\n```\n\n")

        # 3. Add the main context header.
        all_content.append("# Project Context\n\n")
        
        # 4. Process each file and format it into a Markdown block.
        language_map = {'.py': 'python', '.js': 'javascript', '.ts': 'typescript', '.tsx': 'typescript', '.html': 'html', '.css': 'css', '.json': 'json', '.sql': 'sql', '.sh': 'shell', '.yml': 'yaml', '.yaml': 'yaml', '.txt': 'text', '.gitignore': 'text', '.md': 'markdown'}
        for file_path in sorted(files_to_process):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f: content = f.read()
                relative_path = os.path.relpath(file_path, self.root_directory).replace('\\', '/')
                _, extension = os.path.splitext(file_path); basename = os.path.basename(file_path)
                lang = language_map.get(extension.lower(), language_map.get(basename, 'text') if '.' not in basename else 'text')
                all_content.append(f"### `{relative_path}`\n```{lang}\n{content}\n```\n\n")
            except Exception as e:
                rel_path = os.path.relpath(file_path, self.root_directory)
                rel_path = rel_path.replace('\\', '/')
                all_content.append(f"### `{rel_path}`\n```text\nError: {e}\n```\n\n")
        
        # 5. Copy the final string to the clipboard.
        final_string = "".join(all_content).strip()
        try:
            pyperclip.copy(final_string)
            self.status_label.configure(text=f"Copied content of {len(processed_files)} files to clipboard!", text_color="green")
        except pyperclip.PyperclipException:
            self.status_label.configure(text="Pyperclip is not installed or not working.", text_color="red")

    # --- Search Functionality ---
    
    def on_search(self, event=None):
        """Handles search functionality when user types in the search bar."""
        search_term = self.search_entry.get().lower().strip()
        if not search_term:
            self.rebuild_tree_from_data()
            self.status_label.configure(text="Showing all items", text_color="green")
            return
        
        # Filter the tree data based on search term
        filtered_data = self._filter_tree_data(search_term)
        
        # Rebuild tree with filtered data
        self._rebuild_tree_with_data(filtered_data)
        
        if filtered_data:
            self.status_label.configure(text=f"Found {len(filtered_data)} matching items", text_color="green")
        else:
            self.status_label.configure(text="No matching items found", text_color="orange")
    
    def _filter_tree_data(self, search_term):
        """Filters the full tree data based on search term."""
        matching_items = []
        
        def search_recursive(data_list):
            for item in data_list:
                item_path = item['path']
                item_name = os.path.basename(item_path)
                
                # Check if current item matches
                if (search_term in item_name.lower() or 
                    search_term in item_path.lower()):
                    matching_items.append(item)
                
                # If it's a directory, search its children
                if item['is_dir'] and 'children' in item:
                    search_recursive(item['children'])
        
        search_recursive(self.full_tree_data)
        return matching_items
    
    def _rebuild_tree_with_data(self, data_list):
        """Rebuilds the tree view with the given data."""
        # Clear current tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Create a set of all paths that need to be shown (including parents)
        paths_to_show = set()
        for item in data_list:
            item_path = item['path']
            paths_to_show.add(item_path)
            
            # Add all parent directories
            parent_path = os.path.dirname(item_path)
            while parent_path != self.root_directory and parent_path.startswith(self.root_directory):
                paths_to_show.add(parent_path)
                parent_path = os.path.dirname(parent_path)
        
        # Build tree structure from paths
        self._build_tree_from_paths(sorted(paths_to_show), "")
        
        # Ensure tree view is visible
        self.show_tree_view()
    
    def _build_tree_from_paths(self, paths, parent_id):
        """Builds tree structure from a list of paths."""
        # Group paths by their immediate parent
        path_groups = {}
        for path in paths:
            if path == self.root_directory:
                continue
            
            parent = os.path.dirname(path)
            if parent not in path_groups:
                path_groups[parent] = []
            path_groups[parent].append(path)
        
        # Insert items for current level
        if parent_id == "":  # Root level
            current_paths = path_groups.get(self.root_directory, [])
        else:
            current_parent = self.tree.item(parent_id, "values")[0]
            current_paths = path_groups.get(current_parent, [])
        
        for path in sorted(current_paths):
            name = os.path.basename(path)
            is_dir = os.path.isdir(path)
            
            if is_dir:
                icon = self.icon_map.get("folder")
                text = f"{icon}  {name}"
                item_id = self.tree.insert(parent_id, "end", text=text, values=[path], open=True)
                
                # Recursively add children
                if path in path_groups:
                    self._build_tree_from_paths(path_groups[path], item_id)
            else:
                _, extension = os.path.splitext(name)
                icon = self.icon_map.get(extension.lower(), self.icon_map["file"])
                text = f"{icon}  {name}"
                self.tree.insert(parent_id, "end", text=text, values=[path])
    
    def rebuild_tree_from_data(self):
        """Rebuilds the tree view from the stored full tree data."""
        # Clear current tree
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Rebuild from stored data
        self._rebuild_tree_recursive(self.full_tree_data, "")
        
        # Ensure tree view is visible
        self.show_tree_view()
    
    def _rebuild_tree_recursive(self, data_list, parent_id):
        """Recursively rebuilds the tree from stored data."""
        for item in data_list:
            item_path = item['path']
            item_name = os.path.basename(item_path)
            
            if item['is_dir']:
                icon = self.icon_map.get("folder")
                text = f"{icon}  {item_name}"
                item_id = self.tree.insert(parent_id, "end", text=text, values=[item_path], open=False)
                
                if 'children' in item:
                    self._rebuild_tree_recursive(item['children'], item_id)
            else:
                _, extension = os.path.splitext(item_name)
                icon = self.icon_map.get(extension.lower(), self.icon_map["file"])
                text = f"{icon}  {item_name}"
                self.tree.insert(parent_id, "end", text=text, values=[item_path])
    
    def clear_search(self):
        """Clears the search bar and shows all items."""
        self.search_entry.delete(0, tk.END)
        self.rebuild_tree_from_data()
        self.status_label.configure(text="Showing all items", text_color="green")

    # --- Pulsing Animation ---
    
    def start_pulsing_animation(self):
        """Starts the pulsing animation for the select directory button."""
        if self.is_pulsing and not self.root_directory:
            self.pulse_button()
    
    def pulse_button(self):
        """Creates a pulsing effect on the select directory button."""
        if not self.is_pulsing or self.root_directory:
            return
        
        # Get current button colors
        current_fg = self.select_dir_button.cget("fg_color")
        current_hover = self.select_dir_button.cget("hover_color")
        
        # Create pulsing effect by changing colors
        if current_fg == ctk.ThemeManager.theme["CTkButton"]["fg_color"]:
            # Pulse to a brighter color
            self.select_dir_button.configure(
                fg_color="#4CAF50",  # Bright green
                hover_color="#45a049"
            )
        else:
            # Return to normal color
            self.select_dir_button.configure(
                fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"],
                hover_color=ctk.ThemeManager.theme["CTkButton"]["hover_color"]
            )
        
        # Schedule next pulse in 1 second
        self.after(1000, self.pulse_button)
    
    def stop_pulsing_animation(self):
        """Stops the pulsing animation."""
        self.is_pulsing = False
        # Reset button to normal appearance
        self.select_dir_button.configure(
            fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"],
            hover_color=ctk.ThemeManager.theme["CTkButton"]["hover_color"]
        )
    
    def update_copy_button_state(self):
        """Updates the copy button's visual state based on whether items are selected."""
        if self.selected_items:
            # Items are selected - add a subtle border highlight
            self.copy_button.configure(
                border_width=2,
                border_color="#4CAF50"  # Subtle green border
            )
        else:
            # No items selected - remove border
            self.copy_button.configure(
                border_width=0
            )
    
    def show_empty_state(self):
        """Shows the empty state message and hides the tree view."""
        self.tree.grid_remove()
        self.tree_scrollbar.grid_remove()
        # Center the label over the tree area using place
        self.empty_state_label.place(relx=0.5, rely=0.5, anchor="center")
    
    def show_tree_view(self):
        """Shows the tree view and hides the empty state message."""
        self.empty_state_label.place_forget()
        self.tree.grid()
        self.tree_scrollbar.grid()

# --- Application Entry Point ---
if __name__ == "__main__":
    app = FileContentCopier()
    app.mainloop()