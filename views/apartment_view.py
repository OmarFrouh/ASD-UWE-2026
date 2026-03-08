import tkinter as tk
from tkinter import messagebox, ttk

class ApartmentView:
    def __init__(self, parent, property_manager):
        self.property_manager = property_manager
        
        # Main Container
        self.frame = tk.Frame(parent, bg="white")
        self.frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Title
        tk.Label(self.frame, text="Apartment Management", font=("Arial", 18, "bold"), bg="white").pack(pady=(0, 20))
        
        # --- Add Apartment Form ---
        form_frame = tk.LabelFrame(self.frame, text="Add New Unit", bg="white", padx=10, pady=10)
        form_frame.pack(fill="x", pady=10)
        
        # Grid Layout for Form
        tk.Label(form_frame, text="Unit Number:", bg="white").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.unit_entry = tk.Entry(form_frame)
        self.unit_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(form_frame, text="Address:", bg="white").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.address_entry = tk.Entry(form_frame)
        self.address_entry.grid(row=0, column=3, padx=5, pady=5)
        
        tk.Label(form_frame, text="Rent ($):", bg="white").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.rent_entry = tk.Entry(form_frame)
        self.rent_entry.grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(form_frame, text="Size (sqft):", bg="white").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.size_entry = tk.Entry(form_frame)
        self.size_entry.grid(row=1, column=3, padx=5, pady=5)
        
        tk.Button(form_frame, text="Add Unit", command=self.submit_apartment, bg="#4CAF50", fg="white", width=15).grid(row=2, column=0, columnspan=4, pady=15)

        # --- Apartment List (TreeView) ---
        list_frame = tk.Frame(self.frame, bg="white")
        list_frame.pack(fill="both", expand=True, pady=20)
        
        tk.Label(list_frame, text="Unit List", font=("Arial", 12, "bold"), bg="white").pack(anchor="w")
        
        columns = ("unit", "address", "rent", "size", "status")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        self.tree.heading("unit", text="Unit #")
        self.tree.heading("address", text="Address")
        self.tree.heading("rent", text="Rent ($)")
        self.tree.heading("size", text="Size (sqft)")
        self.tree.heading("status", text="Status")
        
        self.tree.column("unit", width=80)
        self.tree.column("address", width=200)
        self.tree.column("rent", width=100)
        self.tree.column("size", width=100)
        self.tree.column("status", width=100)
        
        self.tree.pack(fill="both", expand=True)
        
        self.refresh_list()

    def submit_apartment(self):
        unit = self.unit_entry.get()
        addr = self.address_entry.get()
        rent = self.rent_entry.get()
        size = self.size_entry.get()
        
        try:
            self.property_manager.add_apartment(unit, addr, rent, size)
            messagebox.showinfo("Success", f"Apartment {unit} added successfully!")
            self.clear_form()
            self.refresh_list()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def clear_form(self):
        self.unit_entry.delete(0, tk.END)
        self.address_entry.delete(0, tk.END)
        self.rent_entry.delete(0, tk.END)
        self.size_entry.delete(0, tk.END)
        
    def refresh_list(self):
        # Clear existing
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Fetch updated list
        apartments = self.property_manager.get_all_apartments()
        
        # Insert (DB Schema: id, unit_number, address, rental_price, square_footage, status)
        for apt in apartments:
            # apt is tuple: (id, unit, addr, price, sqft, status)
            self.tree.insert("", tk.END, values=(apt[1], apt[2], f"${apt[3]:.2f}", apt[4], apt[5]))
