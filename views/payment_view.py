# Student Name: Ahmed Deraz
# Student ID: 24046227

import customtkinter as ctk
from tkinter import messagebox
from payment_manager import PaymentManager
from views.ui_helpers import setup_treeview_scroll, autofit_columns, apply_row_stripes

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
        tab_summary = self.tabview.add("Financial Summary")

        # Record Tab
        rec_frame = ctk.CTkFrame(tab_record)
        rec_frame.pack(pady=30)

        ctk.CTkLabel(rec_frame, text="Invoice ID *:", text_color="red").grid(row=0, column=0, padx=15, pady=8, sticky="e")
        self.inv_id_entry = ctk.CTkEntry(rec_frame, width=220)
        self.inv_id_entry.grid(row=0, column=1, padx=15, pady=8, sticky="w")

        ctk.CTkLabel(rec_frame, text="Amount (£) *:", text_color="red").grid(row=1, column=0, padx=15, pady=8, sticky="e")
        self.pay_amount_entry = ctk.CTkEntry(rec_frame, width=220)
        self.pay_amount_entry.grid(row=1, column=1, padx=15, pady=8, sticky="w")

        ctk.CTkLabel(rec_frame, text="Method *:", text_color="red").grid(row=2, column=0, padx=15, pady=8, sticky="e")
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
        self.pay_tree = setup_treeview_scroll(pay_frame, columns=cols, height=15)
        ctk.CTkButton(tab_history, text="Refresh", command=self.refresh).pack(pady=5)

        self.build_summary_tab(tab_summary)
        self.refresh()

    def build_summary_tab(self, tab):
        """Builds the Financial Summary tab showing collected vs pending."""
        # Summary cards
        self.sum_card_frame = ctk.CTkFrame(tab)
        self.sum_card_frame.pack(fill="x", padx=10, pady=10)

        # Payment method breakdown
        ctk.CTkLabel(tab, text="Payment Method Breakdown", font=("Arial", 13, "bold")).pack(anchor="w", padx=15)
        tree_frame = ctk.CTkFrame(tab, fg_color="transparent")
        tree_frame.pack(fill="x", padx=10, pady=(0, 5))

        cols = ("Payment Method", "Total Amount", "Transaction Count")
        self.sum_tree = setup_treeview_scroll(tree_frame, columns=cols, col_widths=[180, 150, 150], height=4)

        # Monthly revenue (last 6 months)
        ctk.CTkLabel(tab, text="Monthly Revenue (Last 6 Months)", font=("Arial", 13, "bold")).pack(anchor="w", padx=15, pady=(5, 0))
        rev_frame = ctk.CTkFrame(tab, fg_color="transparent")
        rev_frame.pack(fill="both", expand=True, padx=10, pady=(0, 5))

        rev_cols = ("Month", "Total Collected")
        self.rev_tree = setup_treeview_scroll(rev_frame, columns=rev_cols, col_widths=[200, 200], height=6)

    def refresh_summary(self):
        """Refreshes the Financial Summary tab data."""
        if not hasattr(self, 'sum_card_frame'):
            return

        # Summary cards
        for w in self.sum_card_frame.winfo_children():
            w.destroy()
        summary = self.payment_manager.get_collected_vs_pending()
        cards = [
            ("Collected", f"£{summary['collected']:.2f}"),
            ("Pending", f"£{summary['pending']:.2f}"),
            ("Total Invoiced", f"£{summary['total']:.2f}"),
        ]
        for i, (label, val) in enumerate(cards):
            card = ctk.CTkFrame(self.sum_card_frame, corner_radius=10)
            card.grid(row=0, column=i, padx=15, pady=10, sticky="nsew")
            self.sum_card_frame.grid_columnconfigure(i, weight=1)
            ctk.CTkLabel(card, text=val, font=("Arial", 28, "bold")).pack(pady=(15, 3))
            ctk.CTkLabel(card, text=label, font=("Arial", 12), text_color="gray").pack(pady=(0, 15))

        # Payment method breakdown
        for item in self.sum_tree.get_children():
            self.sum_tree.delete(item)
        for row in self.payment_manager.get_payment_history_by_method():
            self.sum_tree.insert("", "end", values=(row[0], f"£{row[1]:.2f}", row[2]))
        apply_row_stripes(self.sum_tree)
        autofit_columns(self.sum_tree)

        # Monthly revenue
        for item in self.rev_tree.get_children():
            self.rev_tree.delete(item)
        for row in self.payment_manager.get_monthly_revenue():
            self.rev_tree.insert("", "end", values=(row[0], f"£{row[1]:.2f}"))
        apply_row_stripes(self.rev_tree)
        autofit_columns(self.rev_tree)

    def show_receipt(self, payment_id):
        """Shows a formatted billing/dues receipt popup after recording a payment.
        This is the brief's 'generating the billing/dues receipts' requirement."""
        try:
            r = self.payment_manager.get_receipt_data(payment_id)
        except Exception:
            return  # Silently skip if receipt data unavailable

        popup = ctk.CTkToplevel()
        popup.title("Payment Receipt")
        popup.geometry("460x520")
        popup.grab_set()

        # ─── Header ───
        ctk.CTkLabel(popup, text="PAMS — Payment Receipt",
                     font=("Arial", 18, "bold")).pack(pady=(20, 3))
        ctk.CTkLabel(popup, text="Paragon Apartment Management System",
                     font=("Arial", 11), text_color="gray").pack(pady=(0, 10))
        ctk.CTkLabel(popup, text="━" * 45, text_color="gray").pack()

        # ─── Receipt Body ───
        lines = [
            ("Receipt #:", f"PAY-{r['payment_id']}"),
            ("Date:", r["payment_date"]),
            ("", ""),
            ("Tenant:", r["tenant_name"]),
            ("NI:", r["ni_number"]),
            ("Email:", r["email"]),
            ("Phone:", r["phone"]),
            ("Property:", f"Unit {r['unit']}, {r['address']}"),
            ("City:", r["city"]),
            ("", ""),
            ("Invoice #:", f"INV-{r['invoice_id']}"),
            ("Invoice Total:", f"£{r['invoice_total']:.2f}"),
            ("Amount Paid:", f"£{r['amount']:.2f}"),
            ("Method:", r["method"]),
            ("Reference:", r["reference"]),
            ("", ""),
            ("Invoice Status:", r["invoice_status"]),
        ]

        body_frame = ctk.CTkFrame(popup, fg_color="transparent")
        body_frame.pack(fill="x", padx=30, pady=5)

        for label, value in lines:
            if not label and not value:
                ctk.CTkLabel(body_frame, text="").pack()
                continue
            row = ctk.CTkFrame(body_frame, fg_color="transparent")
            row.pack(fill="x")
            ctk.CTkLabel(row, text=label, font=("Arial", 12), text_color="gray",
                         width=120, anchor="e").pack(side="left")
            ctk.CTkLabel(row, text=value, font=("Arial", 12, "bold"),
                         anchor="w").pack(side="left", padx=(10, 0))

        # ─── Footer ───
        ctk.CTkLabel(popup, text="━" * 45, text_color="gray").pack(pady=(10, 0))
        ctk.CTkButton(popup, text="Close", command=popup.destroy, width=120).pack(pady=15)

    def record(self):
        iid = self.inv_id_entry.get()
        amt = self.pay_amount_entry.get()
        method = self.method_combo.get()
        ref = self.ref_entry.get()

        if not iid or not amt:
            messagebox.showwarning("Error", "Invoice ID and Amount required.")
            return

        try:
            payment_id = self.payment_manager.record_payment(int(iid), float(amt), method, ref)
            for e in [self.inv_id_entry, self.pay_amount_entry, self.ref_entry]:
                e.delete(0, 'end')
            self.refresh()
            self.show_receipt(payment_id)
        except ValueError:
            messagebox.showerror("Error", "Invoice ID and Amount must be valid numbers.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def refresh(self):
        for item in self.pay_tree.get_children():
            self.pay_tree.delete(item)
        for p in self.payment_manager.get_all_payments():
            self.pay_tree.insert("", "end", values=(
                p[0], p[1], f"£{p[2]:.2f}", p[3], p[4], p[5], p[6]))
        apply_row_stripes(self.pay_tree)
        autofit_columns(self.pay_tree)
        self.refresh_summary()