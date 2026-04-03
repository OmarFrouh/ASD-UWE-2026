# Student Name: Ahmed Deraz
# Student ID: 24046227

import customtkinter as ctk
from tkinter import messagebox
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
        rec_frame.pack(pady=30)

        ctk.CTkLabel(rec_frame, text="Invoice ID:").grid(row=0, column=0, padx=15, pady=8, sticky="e")
        self.inv_id_entry = ctk.CTkEntry(rec_frame, width=220)
        self.inv_id_entry.grid(row=0, column=1, padx=15, pady=8, sticky="w")

        ctk.CTkLabel(rec_frame, text="Amount (£):").grid(row=1, column=0, padx=15, pady=8, sticky="e")
        self.pay_amount_entry = ctk.CTkEntry(rec_frame, width=220)
        self.pay_amount_entry.grid(row=1, column=1, padx=15, pady=8, sticky="w")

        ctk.CTkLabel(rec_frame, text="Method:").grid(row=2, column=0, padx=15, pady=8, sticky="e")
        self.method_combo = ctk.CTkComboBox(rec_frame, values=["Card", "Cash", "Bank Transfer"], width=220)
        self.method_combo.grid(row=2, column=1, padx=15, pady=8, sticky="w")
        self.method_combo.set("Card")

        ctk.CTkLabel(rec_frame, text="Reference:").grid(row=3, column=0, padx=15, pady=8, sticky="e")
        self.ref_entry = ctk.CTkEntry(rec_frame, width=220, placeholder_text="Optional")
        self.ref_entry.grid(row=3, column=1, padx=15, pady=8, sticky="w")

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
        iid = self.inv_id_entry.get()
        amt = self.pay_amount_entry.get()
        method = self.method_combo.get()
        ref = self.ref_entry.get()

        if not iid or not amt:
            messagebox.showwarning("Error", "Invoice ID and Amount required.")
            return

        try:
            self.payment_manager.record_payment(int(iid), float(amt), method, ref)
            messagebox.showinfo("Success", "Payment recorded!")
            for e in [self.inv_id_entry, self.pay_amount_entry, self.ref_entry]:
                e.delete(0, 'end')
            self.refresh()
        except ValueError:
            messagebox.showerror("Error", "Invoice ID and Amount must be valid numbers.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def refresh(self):
        for item in self.pay_tree.get_children():
            self.pay_tree.delete(item)
        for p in self.payment_manager.get_all_payments():
            self.pay_tree.insert("", "end", values=(p[0], p[1], f"£{p[2]:.2f}", p[3], p[4], p[5], p[6]))