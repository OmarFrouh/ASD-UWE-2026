# Student Name: Ahmed Deraz
# Student ID: 24046227

import customtkinter as ctk
from tkinter import messagebox
from invoice_manager import InvoiceManager
from views.ui_helpers import setup_treeview_scroll, autofit_columns, apply_row_stripes

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
        tab_notif = self.tabview.add("Late Notifications")

        # Generate Tab
        gen_frame = ctk.CTkFrame(tab_gen)
        gen_frame.pack(pady=40)

        ctk.CTkLabel(gen_frame, text="Tenant ID *:", text_color="red").grid(row=0, column=0, padx=15, pady=10, sticky="e")
        self.tenant_id_entry = ctk.CTkEntry(gen_frame, width=220)
        self.tenant_id_entry.grid(row=0, column=1, padx=15, pady=10, sticky="w")

        ctk.CTkLabel(gen_frame, text="Amount (optional):").grid(row=1, column=0, padx=15, pady=10, sticky="e")
        self.amount_entry = ctk.CTkEntry(gen_frame, width=220, placeholder_text="Uses monthly rent if blank")
        self.amount_entry.grid(row=1, column=1, padx=15, pady=10, sticky="w")

        ctk.CTkButton(gen_frame, text="Generate Invoice", command=self.generate, width=250).grid(
            row=2, column=0, columnspan=2, pady=20)

        # All Invoices Tab
        inv_frame = ctk.CTkFrame(tab_list, fg_color="transparent")
        inv_frame.pack(fill="both", expand=True, padx=10, pady=10)

        cols = ("ID", "Tenant", "Issued", "Due", "Amount", "Status")
        self.inv_tree = setup_treeview_scroll(inv_frame, columns=cols, height=15)
        ctk.CTkButton(tab_list, text="Refresh", command=self.refresh).pack(pady=5)

        # Overdue Tab
        od_frame = ctk.CTkFrame(tab_overdue, fg_color="transparent")
        od_frame.pack(fill="both", expand=True, padx=10, pady=10)

        od_cols = ("ID", "Tenant", "Due Date", "Amount")
        self.od_tree = setup_treeview_scroll(od_frame, columns=od_cols, height=15)

        self.build_notification_tab(tab_notif)
        self.refresh()

    def build_notification_tab(self, tab):
        """Builds the Late Payment Notification tab with tenant contact info."""
        ctk.CTkLabel(tab, text="⚠️ Late Payment Notifications",
                     font=("Arial", 16, "bold"), text_color="orange").pack(pady=(10, 5))
        ctk.CTkLabel(tab, text="These tenants have overdue invoices. Contact them for payment.",
                     font=("Arial", 12), text_color="gray").pack(pady=(0, 10))

        tree_frame = ctk.CTkFrame(tab, fg_color="transparent")
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

        cols = ("Invoice", "Tenant", "Email", "Phone", "Due Date", "Amount", "Days Overdue")
        self.notif_tree = setup_treeview_scroll(tree_frame, columns=cols, height=12)
        for c in cols:
            self.notif_tree.heading(c, text=c)
            self.notif_tree.column(c, width=100)

    def generate(self):
        tid = self.tenant_id_entry.get()
        amt = self.amount_entry.get()
        if not tid:
            messagebox.showwarning("Error", "Tenant ID is required")
            return
            
        try:
            val = float(amt) if amt.strip() else None
            self.invoice_manager.generate_invoice(int(tid), val)
            messagebox.showinfo("Success", "Invoice generated")
            self.tenant_id_entry.delete(0, 'end')
            self.amount_entry.delete(0, 'end')
            self.refresh()
        except ValueError:
            messagebox.showerror("Error", "Tenant ID and Amount must be valid numbers.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def refresh(self):
        # ─── All Invoices Tab ───
        for item in self.inv_tree.get_children():
            self.inv_tree.delete(item)
        for inv in self.invoice_manager.get_all_invoices():
            # Add visual overdue tag
            status_display = inv[5]
            if inv[5] == "Pending":
                from datetime import datetime
                try:
                    due = datetime.strptime(inv[3], "%Y-%m-%d")
                    if due < datetime.now():
                        status_display = "⚠️ OVERDUE"
                except (ValueError, TypeError):
                    pass
            self.inv_tree.insert("", "end", values=(
                inv[0], inv[1], inv[2], inv[3], f"£{inv[4]:.2f}", status_display))
        apply_row_stripes(self.inv_tree)
        autofit_columns(self.inv_tree)

        # ─── Overdue Tab ───
        for item in self.od_tree.get_children():
            self.od_tree.delete(item)
        for od in self.invoice_manager.get_overdue_invoices():
            self.od_tree.insert("", "end", values=(
                od[0], od[1], od[2], f"£{od[3]:.2f}"))
        apply_row_stripes(self.od_tree)
        autofit_columns(self.od_tree)

        # ─── Late Payment Notification Tab ───
        if hasattr(self, 'notif_tree'):
            for item in self.notif_tree.get_children():
                self.notif_tree.delete(item)
            for row in self.invoice_manager.get_overdue_with_details():
                # invoice_id, name, email, phone, due_date, amount, days_overdue
                self.notif_tree.insert("", "end", values=(
                    row[0], row[1], row[2] or "N/A", row[3] or "N/A",
                    row[4], f"£{row[5]:.2f}", f"{row[6]} days"))
            apply_row_stripes(self.notif_tree)
            autofit_columns(self.notif_tree)