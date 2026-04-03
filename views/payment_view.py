# Student Name: Ahmed Deraz
# Student ID: 24046227

import customtkinter as ctk
from tkinter import messagebox, ttk
from payment_manager import PaymentManager
from views.ui_helpers import setup_treeview_scroll

class PaymentView:
    def __init__(self, parent, db_manager):
        self.db_manager = db_manager
        self.payment_manager = PaymentManager(db_manager)

        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame, text="💳 Payment Processing", font=("Arial", 22, "bold")).pack(pady=(0, 10))

        self.tabview = ctk.CTkTabview(frame)
        self.tabview.pack(fill="both", expand=True)

        tab_record = self.tabview.add("Record Payment")
        tab_history = self.tabview.add("Payment History")

        # Record Tab
        rec_frame = ctk.CTkFrame(tab_record)
        rec_frame.pack(pady=30, padx=40)

        ctk.CTkLabel(rec_frame, text="Invoice ID:").grid(row=0, column=0, padx=10, pady=8)
        self.inv_id_entry = ctk.CTkEntry(rec_frame, width=200)
        self.inv_id_entry.grid(row=0, column=1, padx=10, pady=8)

        ctk.CTkLabel(rec_frame, text="Amount (£):").grid(row=1, column=0, padx=10, pady=8)
        self.pay_amount_entry = ctk.CTkEntry(rec_frame, width=200)
        self.pay_amount_entry.grid(row=1, column=1, padx=10, pady=8)

        ctk.CTkLabel(rec_frame, text="Method:").grid(row=2, column=0, padx=10, pady=8)
        self.method_combo = ctk.CTkComboBox(rec_frame, values=["Card", "Cash", "Bank Transfer"], width=200)
        self.method_combo.grid(row=2, column=1, padx=10, pady=8)
        self.method_combo.set("Card")

        ctk.CTkLabel(rec_frame, text="Reference:").grid(row=3, column=0, padx=10, pady=8)
        self.ref_entry = ctk.CTkEntry(rec_frame, width=200, placeholder_text="Optional")
        self.ref_entry.grid(row=3, column=1, padx=10, pady=8)

        ctk.CTkButton(rec_frame, text="Record Payment", command=self.record, width=250).grid(
            row=4, column=0, columnspan=2, pady=20)

        # History Tab
        pay_frame = ctk.CTkFrame(tab_history, fg_color="transparent")
        pay_frame.pack(fill="both", expand=True, padx=10, pady=10)

        cols = ("ID", "Tenant", "Amount", "Date", "Method", "Ref", "Invoice")
        self.pay_tree = setup_treeview_scroll(pay_frame, columns=cols, col_widths=[100]*7, height=15)
        ctk.CTkButton(tab_history, text="Refresh", command=self.refresh).pack(pady=5)
        self.refresh()

    def record(self):
        inv_id = self.inv_id_entry.get()
        amount = self.pay_amount_entry.get()
        method = self.method_combo.get()
        ref = self.ref_entry.get()

        if not inv_id or not amount:
            messagebox.showwarning("Error", "Invoice ID and Amount required.")
            return
        try:
            self.payment_manager.record_payment(int(inv_id), amount, method, ref)
            messagebox.showinfo("Success", "Payment recorded!")
            for e in [self.inv_id_entry, self.pay_amount_entry, self.ref_entry]:
                e.delete(0, 'end')
            self.refresh()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def refresh(self):
        for item in self.pay_tree.get_children():
            self.pay_tree.delete(item)
        for p in self.payment_manager.get_all_payments():
            self.pay_tree.insert("", "end", values=(p[0], p[1], f"£{p[2]:.2f}", p[3], p[4], p[5], p[6]))