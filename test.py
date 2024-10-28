import tkinter as tk
from tkinter import messagebox, simpledialog

class ChecklistApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Checklist")
        self.checklist_items = []  # Store items as dictionaries

        # Set the initial background color to red
        self.root.configure(bg="red")

        # Frame for checklist items
        self.items_frame = tk.Frame(self.root)
        self.items_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Add Button
        add_button = tk.Button(self.root, text="Add Item", command=self.add_item)
        add_button.pack(pady=5)

    def add_item(self):
        # Create a new item dictionary and add it to the checklist
        item = {"var": tk.BooleanVar(), "desc": "Do this", "info": "", "label": None}
        self.checklist_items.append(item)

        # Display the item in the UI
        self.display_item(item)

    def display_item(self, item):
        # Container frame for each checklist row
        row_frame = tk.Frame(self.items_frame)
        row_frame.pack(fill=tk.X, pady=2)

        # Checkbox
        check_button = tk.Checkbutton(row_frame, variable=item["var"], command=self.update_status)
        check_button.pack(side=tk.LEFT)

        # Info button (to display and edit additional info)
        info_button = tk.Button(row_frame, text="?", command=lambda: self.show_info(item))
        info_button.pack(side=tk.LEFT, padx=5)

        # Description label (single-line)
        desc_label = tk.Label(row_frame, text=item["desc"], width=20, anchor="w")
        desc_label.pack(side=tk.LEFT, padx=5)
        item["label"] = desc_label  # Store the label reference for updating

        # Edit button
        edit_button = tk.Button(row_frame, text="✏️", command=lambda: self.edit_description(item))
        edit_button.pack(side=tk.LEFT, padx=5)

        # Move up button
        up_button = tk.Button(row_frame, text="↑", command=lambda: self.move_item(item, -1))
        up_button.pack(side=tk.LEFT)

        # Move down button
        down_button = tk.Button(row_frame, text="↓", command=lambda: self.move_item(item, 1))
        down_button.pack(side=tk.LEFT)

        # Delete button
        delete_button = tk.Button(row_frame, text="🗑️", command=lambda: self.delete_item(item, row_frame))
        delete_button.pack(side=tk.LEFT)

        item["frame"] = row_frame  # Store row frame for easy access

    def show_info(self, item):
        # Display or edit the additional info in a "text pad" style with paragraphs
        info_window = tk.Toplevel(self.root)
        info_window.title("Additional Info")

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
        # Simple dialog to edit main description text
        new_desc = simpledialog.askstring("Edit Description", "Enter new description:", initialvalue=item["desc"])
        if new_desc:
            item["desc"] = new_desc
            item["label"].config(text=new_desc)  # Update the label with new description

    def move_item(self, item, direction):
        # Move item up (-1) or down (+1) in the list
        index = self.checklist_items.index(item)
        new_index = index + direction

        if 0 <= new_index < len(self.checklist_items):
            # Swap items in the list
            self.checklist_items[index], self.checklist_items[new_index] = self.checklist_items[new_index], self.checklist_items[index]
            self.refresh_items()

    def delete_item(self, item, frame):
        # Remove the item and its row frame
        frame.destroy()
        self.checklist_items.remove(item)
        self.update_status()

    def refresh_items(self):
        # Clear and redraw items in the list (after a move)
        for widget in self.items_frame.winfo_children():
            widget.destroy()
        for item in self.checklist_items:
            self.display_item(item)

    def update_status(self):
        # Check if all items are completed
        all_checked = all(item["var"].get() for item in self.checklist_items)

        # Update window background color based on completion status
        self.root.configure(bg="green" if all_checked else "red")

# Initialize the app
root = tk.Tk()
app = ChecklistApp(root)
root.mainloop()
