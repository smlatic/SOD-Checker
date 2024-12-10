import tkinter as tk
from tkinter import simpledialog, ttk, filedialog
import os
import json

class ChecklistApp:
    def __init__(self, root):
        self.root = root
        self.root.title("OP-Checklist")

        # Use a ttk Style for a modern look
        style = ttk.Style()
        style.theme_use("clam")

        # Set a uniform font for all widgets
        self.root.option_add("*Font", "Helvetica 11")

        # Create a header frame at the top
        self.header_frame = tk.Frame(self.root, bg="yellow", pady=10)
        self.header_frame.pack(fill=tk.X)

        self.header_label = tk.Label(
            self.header_frame,
            text="Standby",
            bg="yellow",
            fg="black",
            font=("Helvetica", 14, "bold")
        )
        self.header_label.pack(side=tk.TOP, expand=True)

        # A label to display the settings file loaded, initially empty
        self.filename_label = tk.Label(
            self.header_frame,
            text="",
            bg="yellow",
            fg="black",
            font=("Helvetica", 11, "italic")
        )
        self.filename_label.pack(side=tk.TOP, pady=(5,0))  # Add a small vertical padding for spacing

        self.main_frame = ttk.Frame(self.root, padding="10 10 10 10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.checklist_items = []  # Store items as dictionaries

        # Frame for checklist items
        self.items_frame = ttk.Frame(self.main_frame)
        self.items_frame.pack(fill=tk.BOTH, expand=True)

        # Button Frame
        button_frame = ttk.Frame(self.main_frame, padding="0 10 0 0")
        button_frame.pack(fill=tk.X, pady=5)

        # "Stay On Top" Toggle
        self.stay_on_top_var = tk.BooleanVar(value=False)
        stay_on_top_check = ttk.Checkbutton(button_frame, text="Stay On Top", variable=self.stay_on_top_var, command=self.toggle_stay_on_top)
        stay_on_top_check.pack(side=tk.LEFT, padx=5)

        # Add Button
        add_button = ttk.Button(button_frame, text="Add Item", command=self.open_add_item_popup)
        add_button.pack(side=tk.LEFT, padx=5)

        # Save Setup Button
        save_button = ttk.Button(button_frame, text="Save Setup", command=self.save_setup)
        save_button.pack(side=tk.LEFT, padx=5)

        # Load Setup Button
        load_button = ttk.Button(button_frame, text="Load Setup", command=self.load_setup)
        load_button.pack(side=tk.LEFT, padx=5)

        # Variables for drag-and-drop reordering
        self.drag_data = {"item": None, "y": 0, "index": None}
        self.drag_ghost = None  
        self.loaded_filename = ""  # Track the currently loaded filename
        self.update_status()

    def toggle_stay_on_top(self):
        self.root.attributes("-topmost", self.stay_on_top_var.get())

    def open_add_item_popup(self):
        popup = tk.Toplevel(self.root)
        popup.title("Add Item")
        popup.geometry("250x120")
        popup.attributes("-topmost", True)

        popup_frame = ttk.Frame(popup, padding="10 10 10 10")
        popup_frame.pack(fill=tk.BOTH, expand=True)

        dropdown_label = ttk.Label(popup_frame, text="Select Item Type:")
        dropdown_label.pack(pady=5)

        item_type_var = tk.StringVar()
        item_type_dropdown = ttk.Combobox(popup_frame, textvariable=item_type_var, values=["Check", "Timer"], state="readonly")
        item_type_dropdown.pack(pady=5)
        item_type_dropdown.set("Check")

        confirm_button = ttk.Button(popup_frame, text="Confirm", command=lambda: self.add_item(item_type_var.get(), popup))
        confirm_button.pack(pady=5)

    def add_item(self, item_type, popup):
        if item_type == "Check":
            item = {"var": tk.BooleanVar(), "type": "check", "desc": "Do this", "info": "", "label": None, "frame": None}
            self.checklist_items.append(item)
            self.display_check_item(item)

        elif item_type == "Timer":
            item = {
                "var": tk.BooleanVar(),
                "type": "timer",
                "desc": "Timer Task",
                "info": "",
                "label": None,
                "frame": None,
                "time_left": 60,
                "initial_time": 60,
                "timer_running": False
            }
            self.checklist_items.append(item)
            self.display_timer_item(item)

        popup.destroy()
        self.update_status()

    def display_check_item(self, item):
        row_frame = ttk.Frame(self.items_frame, padding="5 5 5 5")
        row_frame.pack(fill=tk.X, pady=2)
        item["frame"] = row_frame

        # Drag handle label
        handle = ttk.Label(row_frame, text="≡", width=2, anchor="center")
        handle.pack(side=tk.LEFT)
        self.make_draggable(handle, item)

        check_button = ttk.Checkbutton(row_frame, variable=item["var"], command=self.update_status)
        check_button.pack(side=tk.LEFT)

        info_button = ttk.Button(row_frame, text="?", width=2, command=lambda: self.show_info(item))
        info_button.pack(side=tk.LEFT, padx=5)

        desc_label = ttk.Label(row_frame, text=item["desc"], width=30, anchor="w")
        desc_label.pack(side=tk.LEFT, padx=5)
        item["label"] = desc_label

        edit_button = ttk.Button(row_frame, text="🖊️", width=3, command=lambda: self.edit_description(item))
        edit_button.pack(side=tk.LEFT, padx=5)

        delete_button = ttk.Button(row_frame, text="🗑️", width=3, command=lambda: self.delete_item(item, row_frame))
        delete_button.pack(side=tk.RIGHT)

    def display_timer_item(self, item):
        row_frame = ttk.Frame(self.items_frame, padding="5 5 5 5")
        row_frame.pack(fill=tk.X, pady=2)
        item["frame"] = row_frame

        handle = ttk.Label(row_frame, text="≡", width=2, anchor="center")
        handle.pack(side=tk.LEFT)
        self.make_draggable(handle, item)

        check_button = ttk.Checkbutton(row_frame, variable=item["var"], command=lambda: self.toggle_timer(item))
        check_button.pack(side=tk.LEFT)

        info_button = ttk.Button(row_frame, text="?", width=2, command=lambda: self.show_info(item))
        info_button.pack(side=tk.LEFT, padx=5)

        minutes = item['time_left'] // 60
        seconds = item['time_left'] % 60
        time_str = f"{minutes}:{seconds:02d}"

        desc_label = ttk.Label(row_frame, text=f"{item['desc']} - Time: {time_str}", width=30, anchor="w")
        desc_label.pack(side=tk.LEFT, padx=5)
        item["label"] = desc_label

        edit_button = ttk.Button(row_frame, text="🖊️", width=3, command=lambda: self.edit_timer(item))
        edit_button.pack(side=tk.LEFT, padx=5)

        delete_button = ttk.Button(row_frame, text="🗑️", width=3, command=lambda: self.delete_item(item, row_frame))
        delete_button.pack(side=tk.RIGHT)

    def make_draggable(self, widget, item):
        widget.bind("<ButtonPress-1>", lambda e, i=item: self.on_drag_start(e, i))
        widget.bind("<B1-Motion>", self.on_drag_motion)
        widget.bind("<ButtonRelease-1>", self.on_drag_release)

    def on_drag_start(self, event, item):
        self.drag_data["item"] = item
        self.drag_data["index"] = self.checklist_items.index(item)
        self.drag_data["y"] = event.y_root

        if self.drag_ghost is not None:
            self.drag_ghost.destroy()

        self.drag_ghost = tk.Toplevel(self.root)
        self.drag_ghost.overrideredirect(True)
        self.drag_ghost.attributes("-alpha", 0.8)
        self.drag_ghost.configure(bg="lightgrey")

        ghost_label = ttk.Label(self.drag_ghost, text=item["desc"], background="lightgrey", padding=5)
        ghost_label.pack()

        self.drag_ghost.geometry(f"+{event.x_root+10}+{event.y_root+10}")

    def on_drag_motion(self, event):
        if self.drag_data["item"] is None:
            return
        if self.drag_ghost is not None:
            self.drag_ghost.geometry(f"+{event.x_root+10}+{event.y_root+10}")

    def on_drag_release(self, event):
        if self.drag_data["item"] is None:
            return

        orig_index = self.drag_data["index"]
        final_index = orig_index

        item_positions = []
        for i, it in enumerate(self.checklist_items):
            f = it["frame"]
            item_positions.append((i, f.winfo_rooty()))

        drop_y = event.y_root
        item_positions.sort(key=lambda x: x[1])

        for i, y_pos in item_positions:
            if drop_y > y_pos:
                final_index = i

        if final_index != orig_index:
            item = self.drag_data["item"]
            self.checklist_items.remove(item)
            if final_index >= len(self.checklist_items):
                self.checklist_items.append(item)
            else:
                self.checklist_items.insert(final_index, item)
            self.refresh_items()

        self.drag_data = {"item": None, "y": 0, "index": None}

        if self.drag_ghost:
            self.drag_ghost.destroy()
            self.drag_ghost = None

        self.update_status()

    def refresh_items(self):
        for widget in self.items_frame.winfo_children():
            widget.pack_forget()
        for item in self.checklist_items:
            item["frame"].pack(fill=tk.X, pady=2)

    def show_info(self, item):
        info_window = tk.Toplevel(self.root)
        info_window.title("Additional Info")
        info_window.attributes("-topmost", True)

        info_frame = ttk.Frame(info_window, padding="10 10 10 10")
        info_frame.pack(fill=tk.BOTH, expand=True)

        info_text = tk.Text(info_frame, wrap=tk.WORD, height=10, width=50)
        info_text.insert(tk.END, item["info"])
        info_text.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        save_button = ttk.Button(info_frame, text="Save", command=lambda: self.save_info(item, info_text, info_window))
        save_button.pack()

        info_window.update_idletasks()
        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()
        root_w = self.root.winfo_width()
        root_h = self.root.winfo_height()

        info_w = info_window.winfo_reqwidth()
        info_h = info_window.winfo_reqheight()

        pos_x = root_x + (root_w // 2) - (info_w // 2)
        pos_y = root_y + (root_h // 2) - (info_h // 2)

        info_window.geometry(f"+{pos_x}+{pos_y}")

    def save_info(self, item, info_text, window):
        item["info"] = info_text.get("1.0", tk.END).strip()
        window.destroy()

    def edit_description(self, item):
        new_desc = simpledialog.askstring("Edit Description", "Enter new description:", initialvalue=item["desc"], parent=self.root)
        if new_desc:
            item["desc"] = new_desc
            item["label"].config(text=new_desc)

    def edit_timer(self, item):
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Timer")
        edit_window.attributes("-topmost", True)

        edit_frame = ttk.Frame(edit_window, padding="10 10 10 10")
        edit_frame.pack(fill=tk.BOTH, expand=True)

        desc_label = ttk.Label(edit_frame, text="Edit Description:")
        desc_label.pack(pady=5)
        desc_entry = ttk.Entry(edit_frame, width=30)
        desc_entry.insert(0, item["desc"])
        desc_entry.pack(pady=5)

        time_label = ttk.Label(edit_frame, text="Set Timer (minutes):")
        time_label.pack(pady=5)
        time_entry = ttk.Entry(edit_frame, width=10)
        current_minutes = item["initial_time"] // 60
        time_entry.insert(0, str(current_minutes))
        time_entry.pack(pady=5)

        save_button = ttk.Button(edit_frame, text="Save", command=lambda: self.save_timer_settings(item, desc_entry, time_entry, edit_window))
        save_button.pack(pady=10)

        edit_window.update_idletasks()
        root_x = self.root.winfo_x()
        root_y = self.root.winfo_y()
        root_w = self.root.winfo_width()
        root_h = self.root.winfo_height()

        edit_w = edit_window.winfo_reqwidth()
        edit_h = edit_window.winfo_reqheight()

        pos_x = root_x + (root_w // 2) - (edit_w // 2)
        pos_y = root_y + (root_h // 2) - (edit_h // 2)
        edit_window.geometry(f"+{pos_x}+{pos_y}")

    def save_timer_settings(self, item, desc_entry, time_entry, window):
        item["desc"] = desc_entry.get()
        time_str = time_entry.get()
        if time_str.isdigit():
            item["initial_time"] = int(time_str) * 60
        item["time_left"] = item["initial_time"]

        minutes = item['time_left'] // 60
        seconds = item['time_left'] % 60
        time_str = f"{minutes}:{seconds:02d}"
        item["label"].config(text=f"{item['desc']} - Time: {time_str}")

        window.destroy()

    def toggle_timer(self, item):
        if item["var"].get():
            item["timer_running"] = True
            self.run_timer(item)
            self.update_status()
        else:
            item["timer_running"] = False
            item["time_left"] = item["initial_time"]
            minutes = item['time_left'] // 60
            seconds = item['time_left'] % 60
            time_str = f"{minutes}:{seconds:02d}"
            item["label"].config(text=f"{item['desc']} - Time: {time_str}")
            self.update_status()

    def run_timer(self, item):
        if item["timer_running"] and item["time_left"] > 0:
            item["time_left"] -= 1
            minutes = item['time_left'] // 60
            seconds = item['time_left'] % 60
            time_str = f"{minutes}:{seconds:02d}"
            item["label"].config(text=f"{item['desc']} - Time: {time_str}")
            self.root.after(1000, lambda: self.run_timer(item))
        elif item["time_left"] == 0:
            item["timer_running"] = False
            item["var"].set(False)
            item["time_left"] = item["initial_time"]
            minutes = item['time_left'] // 60
            seconds = item['time_left'] % 60
            time_str = f"{minutes}:{seconds:02d}"
            item["label"].config(text=f"{item['desc']} - Time: {time_str}")
            self.update_status()

    def delete_item(self, item, frame):
        frame.destroy()
        self.checklist_items.remove(item)
        self.update_status()

    def save_setup(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json")],
            initialdir=os.path.dirname(os.path.abspath(__file__)),
            title="Save Setup As"
        )
        if file_path:
            setup_data = []
            for item in self.checklist_items:
                item_data = {
                    "type": item["type"],
                    "desc": item["desc"],
                    "var": item["var"].get(),
                    "info": item["info"]
                }
                if item["type"] == "timer":
                    item_data["initial_time"] = item["initial_time"]
                setup_data.append(item_data)
            
            with open(file_path, "w") as file:
                json.dump(setup_data, file, indent=4)
            
            # Update the filename label
            base_name = os.path.basename(file_path)
            self.loaded_filename = base_name
            self.filename_label.configure(text=self.loaded_filename, font=("Helvetica",11,"italic"))
            self.update_status()

    def load_setup(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON Files", "*.json")],
            initialdir=os.path.dirname(os.path.abspath(__file__)),
            title="Open Setup"
        )
        if file_path:
            with open(file_path, "r") as file:
                setup_data = json.load(file)
                self.checklist_items.clear()
                for widget in self.items_frame.winfo_children():
                    widget.destroy()
                for item_data in setup_data:
                    # Regardless of what var was in the file, start all unchecked
                    item = {
                        "var": tk.BooleanVar(value=False),  # Force unchecked
                        "type": item_data["type"],
                        "desc": item_data["desc"],
                        "info": item_data["info"],
                        "initial_time": item_data.get("initial_time", 60),
                        "time_left": item_data.get("initial_time", 60),
                        "timer_running": False
                    }
                    self.checklist_items.append(item)
                    if item["type"] == "check":
                        self.display_check_item(item)
                    elif item["type"] == "timer":
                        self.display_timer_item(item)

                # Update the filename label
                base_name = os.path.basename(file_path)
                self.loaded_filename = base_name
                self.filename_label.configure(text=self.loaded_filename, font=("Helvetica",11,"italic"))
                self.update_status()


    def update_status(self):
        all_checked = all(item["var"].get() for item in self.checklist_items)
        if all_checked:
            # Green with white bold text "Ready"
            self.header_frame.configure(bg="green")
            self.header_label.configure(text="Ready", bg="green", fg="white", font=("Helvetica",14,"bold"))
            # If a file is loaded, keep filename visible with italic font, same background
            self.filename_label.configure(bg="green", fg="white")
        else:
            # Yellow with black bold text "Standby"
            self.header_frame.configure(bg="yellow")
            self.header_label.configure(text="Standby", bg="yellow", fg="black", font=("Helvetica",14,"bold"))
            self.filename_label.configure(bg="yellow", fg="black")

        self.root.configure(bg="white" if not all_checked else "#d4edda")


# Initialize the app
root = tk.Tk()
app = ChecklistApp(root)
root.mainloop()
