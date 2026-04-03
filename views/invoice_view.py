# Student Name: Ahmed Deraz
# Student ID: 24046227

import customtkinter as ctk
from tkinter import messagebox, ttk
from invoice_manager import InvoiceManager
from views.ui_helpers import setup_treeview_scroll

class InvoiceView:
    def __init__(self, parent, db_manager):
        self.db_manager = db_manager
        self.invoice_manager = InvoiceManager(db_manager)

        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame, text="💰 Invoice Management", font=("Arial", 22, "bold")).pack(pady=(0, 10))

        self.tabview = ctk.CTkTabview(frame)
        self.tabview.pack(fill="both", expand=True)

        tab_gen = self.tabview.add("Generate Invoice")
        tab_list = self.tabview.add("All Invoices")
        tab_overdue = self.tabview.add("Overdue")

        # Generate Tab
        gen_frame = ctk.CTkFrame(tab_gen)
        gen_frame.pack(pady=30, padx=40)

        ctk.CTkLabel(gen_frame, text="Tenant ID:").grid(row=0, column=0, padx=10, pady=10)
        self.tenant_id_entry = ctk.CTkEntry(gen_frame, width=200)
        self.tenant_id_entry.grid(row=0, column=1, padx=10, pady=10)

        ctk.CTkLabel(gen_frame, text="Amount (optional):").grid(row=1, column=0, padx=10, pady=10)
        self.amount_entry = ctk.CTkEntry(gen_frame, width=200, placeholder_text="Uses monthly rent if blank")
        self.amount_entry.grid(row=1, column=1, padx=10, pady=10)

        ctk.CTkButton(gen_frame, text="Generate Invoice", command=self.generate, width=250).grid(
            row=2, column=0, columnspan=2, pady=20)

        # All Invoices Tab
        inv_frame = ctk.CTkFrame(tab_list, fg_color="transparent")
        inv_frame.pack(fill="both", expand=True, padx=10, pady=10)

        cols = ("ID", "Tenant", "Issued", "Due", "Amount", "Status")
        self.inv_tree = setup_treeview_scroll(inv_frame, columns=cols, col_widths=[110]*6, height=15)
        ctk.CTkButton(tab_list, text="Refresh", command=self.refresh).pack(pady=5)

        # Overdue Tab
        od_frame = ctk.CTkFrame(tab_overdue, fg_color="transparent")
        od_frame.pack(fill="both", expand=True, padx=10, pady=10)

        od_cols = ("ID", "Tenant", "Due Date", "Amount")
        self.od_tree = setup_treeview_scroll(od_frame, columns=od_cols, col_widths=[130]*4, height=15)

        self.refresh()

    def generate(self):
        tid = self.tenant_id_entry.get()
        amt = self.amount_entry.get()
        if not tid:
            messagebox.showwarning("Error", "Enter tenant ID.")
            return
        try:
            self.invoice_manager.generate_invoice(int(tid), float(amt) if amt else None)
            messagebox.showinfo("Success", "Invoice generated!")
            self.refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def refresh(self):
        for item in self.inv_tree.get_children():
            self.inv_tree.delete(item)
        for inv in self.invoice_manager.get_all_invoices():
            self.inv_tree.insert("", "end", values=(inv[0], inv[1], inv[2], inv[3], f"£{inv[4]:.2f}", inv[5]))

        for item in self.od_tree.get_children():
            self.od_tree.delete(item)
        for od in self.invoice_manager.get_overdue_invoices():
            self.od_tree.insert("", "end", values=(od[0], od[1], od[2], f"£{od[3]:.2f}"))