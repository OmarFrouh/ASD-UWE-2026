# Student Name: Omar Alfrouh
# Student ID: [YOUR_ID]

import customtkinter as ctk
from tkinter import messagebox
from views.ui_helpers import setup_treeview_scroll, autofit_columns, apply_row_stripes

class ApartmentView:
    def __init__(self, parent, property_manager):
        self.property_manager = property_manager

        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame, text="🏠 Apartment Management", font=("Arial", 22, "bold")).pack(pady=(0, 15))

        form = ctk.CTkFrame(frame)
        form.pack(pady=10)

        ctk.CTkLabel(form, text="Unit # *:", text_color="red").grid(row=0, column=0, padx=15, pady=8, sticky="e")
        self.unit_entry = ctk.CTkEntry(form, width=180)
        self.unit_entry.grid(row=0, column=1, padx=15, pady=8, sticky="w")

        ctk.CTkLabel(form, text="Address *:", text_color="red").grid(row=0, column=2, padx=15, pady=8, sticky="e")
        self.address_entry = ctk.CTkEntry(form, width=180)
        self.address_entry.grid(row=0, column=3, padx=15, pady=8, sticky="w")

        ctk.CTkLabel(form, text="City *:", text_color="red").grid(row=1, column=0, padx=15, pady=8, sticky="e")
        default_cities = ["Bristol", "Cardiff", "London", "Manchester"]
        existing = self.property_manager.get_cities()
        city_options = sorted(set(default_cities + existing))
        self.city_combo = ctk.CTkComboBox(form, values=city_options, width=180)
        self.city_combo.grid(row=1, column=1, padx=15, pady=8, sticky="w")
        self.city_combo.set("Bristol")

        ctk.CTkLabel(form, text="Rooms:").grid(row=1, column=2, padx=15, pady=8, sticky="e")
        self.rooms_entry = ctk.CTkEntry(form, width=180)
        self.rooms_entry.grid(row=1, column=3, padx=15, pady=8, sticky="w")

        ctk.CTkLabel(form, text="Rent (£) *:", text_color="red").grid(row=2, column=0, padx=15, pady=8, sticky="e")
        self.rent_entry = ctk.CTkEntry(form, width=180)
        self.rent_entry.grid(row=2, column=1, padx=15, pady=8, sticky="w")

        ctk.CTkLabel(form, text="Size (sqft) *:", text_color="red").grid(row=2, column=2, padx=15, pady=8, sticky="e")
        self.size_entry = ctk.CTkEntry(form, width=180)
        self.size_entry.grid(row=2, column=3, padx=15, pady=8, sticky="w")

        ctk.CTkButton(form, text="Add Unit", command=self.submit_apartment, width=200).grid(row=3, column=0, columnspan=4, pady=12)

        # Table
        list_frame = ctk.CTkFrame(frame, fg_color="transparent")
        list_frame.pack(fill="both", expand=True, pady=10, padx=20)

        cols = ("id", "unit", "address", "city", "rooms", "rent", "sqft", "status")
        headings = ["ID", "Unit", "Address", "City", "Rooms", "Rent", "Sqft", "Status"]
        self.tree = setup_treeview_scroll(list_frame, columns=cols, headings=headings, col_widths=[50, 100, 100, 100, 80, 100, 100, 100], height=10)
        self.refresh_list()

    def submit_apartment(self):
        try:
            self.property_manager.add_apartment(
                self.unit_entry.get(), self.address_entry.get(),
                self.rent_entry.get(), self.size_entry.get(),
                self.city_combo.get(), self.rooms_entry.get() or "1"
            )
            messagebox.showinfo("Success", "Apartment added!")
            self.clear_form()
            self.refresh_list()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def clear_form(self):
        for e in [self.unit_entry, self.address_entry, self.rooms_entry, self.rent_entry, self.size_entry]:
            e.delete(0, 'end')

    def refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for apt in self.property_manager.get_all_apartments():
            # Schema: id, unit, address, city, rooms, price, sqft, status
            self.tree.insert("", "end", values=(apt[0], apt[1], apt[2], apt[3], apt[4], f"£{apt[5]:.2f}", apt[6], apt[7]))
        apply_row_stripes(self.tree)
        autofit_columns(self.tree)
