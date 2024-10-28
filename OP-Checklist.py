import tkinter as tk
from tkinter import simpledialog, ttk, filedialog
import os
import json

class ChecklistApp:
    def __init__(self, root):
        self.root = root
        self.root.title("OP-Checklist")  # Set the new title
        self.checklist_items = []  # Store items as dictionaries

        # Set the initial background color to red and ensure it updates based on the current state
        self.root.configure(bg="red")

        # Frame for checklist items
        self.items_frame = tk.Frame(self.root)
        self.items_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Button Frame
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=5)

        # "Stay On Top" Toggle positioned in the button frame
        self.stay_on_top_var = tk.BooleanVar(value=False)
        stay_on_top_check = tk.Checkbutton(button_frame, text="Stay On Top", variable=self.stay_on_top_var, command=self.toggle_stay_on_top)
        stay_on_top_check.pack(side=tk.LEFT, padx=5)

        # Add Button
        add_button = tk.Button(button_frame, text="Add Item", command=self.open_add_item_popup)
        add_button.pack(side=tk.LEFT, padx=5)

        # Save Setup Button
        save_button = tk.Button(button_frame, text="Save Setup", command=self.save_setup)
        save_button.pack(side=tk.LEFT, padx=5)

        # Load Setup Button
        load_button = tk.Button(button_frame, text="Load Setup", command=self.load_setup)
        load_button.pack(side=tk.LEFT, padx=5)

        # Placeholder for red/green icons (commented for future use)
        # self.red_icon_path = os.path.join(os.path.dirname(__file__), "red.ico")
        # self.green_icon_path = os.path.join(os.path.dirname(__file__), "green.ico")

        # Initial status update to ensure color sync on startup
        self.update_status()

    def toggle_stay_on_top(self):
        # Toggle the window's "always on top" state based on the checkbox
        self.root.attributes("-topmost", self.stay_on_top_var.get())

    def open_add_item_popup(self):
        # Popup window for selecting the type of item to add
        popup = tk.Toplevel(self.root)
        popup.title("Add Item")
        popup.geometry("200x100")

        # Dropdown for item type selection
        dropdown_label = tk.Label(popup, text="Select Item Type:")
        dropdown_label.pack(pady=5)

        item_type_var = tk.StringVar()
        item_type_dropdown = ttk.Combobox(popup, textvariable=item_type_var, values=["Check", "Timer"], state="readonly")
        item_type_dropdown.pack(pady=5)
        item_type_dropdown.set("Check")  # Default selection

        # Confirm Button to add the selected item type
        confirm_button = tk.Button(popup, text="Confirm", command=lambda: self.add_item(item_type_var.get(), popup))
        confirm_button.pack(pady=5)

    def add_item(self, item_type, popup):
        # Add the selected type of item and close the popup
        if item_type == "Check":
            item = {"var": tk.BooleanVar(), "type": "check", "desc": "Do this", "info": "", "label": None}
            self.checklist_items.append(item)
            self.display_check_item(item)

        elif item_type == "Timer":
            item = {
                "var": tk.BooleanVar(),
                "type": "timer",
                "desc": "Timer Task",
                "info": "",
                "label": None,
                "time_left": 60,
                "initial_time": 60,  # Store initial time
                "timer_running": False
            }
            self.checklist_items.append(item)
            self.display_timer_item(item)

        popup.destroy()  # Close the popup after adding the item
        self.update_status()  # Update status after adding a new item

    def display_check_item(self, item):
        # Create a row for a standard checklist item
        row_frame = tk.Frame(self.items_frame)
        row_frame.pack(fill=tk.X, pady=2)

        # Checkbox
        check_button = tk.Checkbutton(row_frame, variable=item["var"], command=self.update_status)
        check_button.pack(side=tk.LEFT)

        # Info button
        info_button = tk.Button(row_frame, text="?", command=lambda: self.show_info(item))
        info_button.pack(side=tk.LEFT, padx=5)

        # Description label
        desc_label = tk.Label(row_frame, text=item["desc"], width=30, anchor="w")
        desc_label.pack(side=tk.LEFT, padx=5)
        item["label"] = desc_label

        # Edit button
        edit_button = tk.Button(row_frame, text="✏️", command=lambda: self.edit_description(item))
        edit_button.pack(side=tk.LEFT, padx=5)

        # Delete button
        delete_button = tk.Button(row_frame, text="🗑️", command=lambda: self.delete_item(item, row_frame))
        delete_button.pack(side=tk.LEFT)

    def display_timer_item(self, item):
        # Create a row for a timer item
        row_frame = tk.Frame(self.items_frame)
        row_frame.pack(fill=tk.X, pady=2)

        # Checkbox for starting/stopping timer
        check_button = tk.Checkbutton(row_frame, variable=item["var"], command=lambda: self.toggle_timer(item))
        check_button.pack(side=tk.LEFT)

        # Info button
        info_button = tk.Button(row_frame, text="?", command=lambda: self.show_info(item))
        info_button.pack(side=tk.LEFT, padx=5)

        # Description label with timer
        desc_label = tk.Label(row_frame, text=f"{item['desc']} - Time: {item['time_left']}s", width=30, anchor="w")
        desc_label.pack(side=tk.LEFT, padx=5)
        item["label"] = desc_label  # Store label reference for updates

        # Edit button
        edit_button = tk.Button(row_frame, text="✏️", command=lambda: self.edit_timer(item))
        edit_button.pack(side=tk.LEFT, padx=5)

        # Delete button
        delete_button = tk.Button(row_frame, text="🗑️", command=lambda: self.delete_item(item, row_frame))
        delete_button.pack(side=tk.LEFT)

    def show_info(self, item):
        # Display or edit the additional info in a "text pad" style with paragraphs
        info_window = tk.Toplevel(self.root)
        info_window.title("Additional Info")

        # Position the window at the bottom of the main app window
        self.root.update_idletasks()
        x = self.root.winfo_x()
        y = self.root.winfo_y() + self.root.winfo_height()
        info_window.geometry(f"+{x}+{y}")

        info_text = tk.Text(info_window, wrap=tk.WORD, height=10, width=50)
        info_text.insert(tk.END, item["info"])
        info_text.pack(pady=10, padx=10)
        
        # Save Button
        save_button = tk.Button(info_window, text="Save", command=lambda: self.save_info(item, info_text, info_window))
        save_button.pack()

    def save_info(self, item, info_text, window):
        # Save the text pad contents to the item's "info" field
        item["info"] = info_text.get("1.0", tk.END).strip()
        window.destroy()

    def edit_description(self, item):
        new_desc = simpledialog.askstring("Edit Description", "Enter new description:", initialvalue=item["desc"])
        if new_desc:
            item["desc"] = new_desc
            item["label"].config(text=new_desc)

    def edit_timer(self, item):
        # Unified popup for editing description and setting time
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Timer")

        # Description editing
        desc_label = tk.Label(edit_window, text="Edit Description:")
        desc_label.pack(pady=5)
        desc_entry = tk.Entry(edit_window, width=30)
        desc_entry.insert(0, item["desc"])
        desc_entry.pack(pady=5)

        # Time setting
        time_label = tk.Label(edit_window, text="Set Timer (seconds):")
        time_label.pack(pady=5)
        time_entry = tk.Entry(edit_window, width=10)
        time_entry.insert(0, str(item["initial_time"]))  # Show initial time
        time_entry.pack(pady=5)

        # Save button to apply changes
        save_button = tk.Button(edit_window, text="Save", command=lambda: self.save_timer_settings(item, desc_entry, time_entry, edit_window))
        save_button.pack(pady=10)

    def save_timer_settings(self, item, desc_entry, time_entry, window):
        # Update description and time from entries
        item["desc"] = desc_entry.get()
        item["initial_time"] = int(time_entry.get()) if time_entry.get().isdigit() else item["initial_time"]
        item["time_left"] = item["initial_time"]  # Reset to initial time when edited
        item["label"].config(text=f"{item['desc']} - Time: {item['time_left']}s")
        window.destroy()

    def toggle_timer(self, item):
        if item["var"].get():  # Start timer if checked
            item["timer_running"] = True
            self.run_timer(item)
            self.update_status()
        else:  # Reset timer if unchecked
            item["timer_running"] = False
            item["time_left"] = item["initial_time"]  # Reset time to initial time
            item["label"].config(text=f"{item['desc']} - Time: {item['time_left']}s")  # Update label
            self.update_status()

    def run_timer(self, item):
        if item["timer_running"] and item["time_left"] > 0:
            item["time_left"] -= 1
            item["label"].config(text=f"{item['desc']} - Time: {item['time_left']}s")
            self.root.after(1000, lambda: self.run_timer(item))
        elif item["time_left"] == 0:
            item["timer_running"] = False
            item["var"].set(False)  # Untick the checkbox
            item["time_left"] = item["initial_time"]  # Reset time to initial time
            item["label"].config(text=f"{item['desc']} - Time: {item['time_left']}s")  # Update label
            self.update_status()

    def delete_item(self, item, frame):
        frame.destroy()
        self.checklist_items.remove(item)
        self.update_status()

    def save_setup(self):
        # File dialog to save the current setup in JSON
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

    def load_setup(self):
        # File dialog to load a saved setup in JSON
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
                    item = {
                        "var": tk.BooleanVar(value=item_data["var"]),
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
            self.update_status()  # Ensure correct color on load

    def update_status(self):
        all_checked = all(item["var"].get() for item in self.checklist_items)
        if all_checked:
            self.root.configure(bg="green")
            # self.root.iconbitmap(self.green_icon_path)  # Uncomment to enable icon update
        else:
            self.root.configure(bg="red")
            # self.root.iconbitmap(self.red_icon_path)  # Uncomment to enable icon update

# Initialize the app
root = tk.Tk()
app = ChecklistApp(root)
root.mainloop()
