# Student Name: Ahmed Deraz
# Student ID: 24046227

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
from datetime import datetime
from invoice_manager import InvoiceManager
from payment_manager import PaymentManager
from views import theme as T
from views.ui_helpers import (
    setup_treeview_scroll, autofit_columns, apply_row_stripes,
    create_page_header, create_card, create_card_fill, create_tabview,
    create_primary_button, create_ghost_button, create_success_button,
    create_danger_button,
    show_success, show_error, show_warning,
    create_empty_state, confirm_dialog, export_table_to_csv,
)


class InvoiceView:
    def __init__(self, parent, db_manager):
        self.db_manager      = db_manager
        self.invoice_manager = InvoiceManager(db_manager)
        self.payment_manager = PaymentManager(db_manager)
        self._root = parent.winfo_toplevel()

        frame = ctk.CTkFrame(parent, fg_color=T.BG)
        frame.pack(fill="both", expand=True)

        create_page_header(frame, "💰 Invoices",
                            subtitle="Generate and track tenant invoices")

        self.tabview = create_tabview(frame)

        tab_gen    = self.tabview.add("Generate Invoice")
        tab_list   = self.tabview.add("All Invoices")
        tab_od     = self.tabview.add("Overdue")
        tab_notif  = self.tabview.add("Late Notifications")

        self._build_generate_tab(tab_gen)
        self._build_list_tab(tab_list)
        self._build_overdue_tab(tab_od)
        self._build_notif_tab(tab_notif)
        self.refresh()

    # ── Generate tab ──────────────────────────────────────────────────────────

    def _build_generate_tab(self, tab):
        scroll = ctk.CTkScrollableFrame(tab, fg_color=T.BG,
                                         scrollbar_button_color=T.SURFACE_3)
        scroll.pack(fill="both", expand=True)
        inner = create_card(scroll, title="Generate Invoice")
        inner.grid_columnconfigure(0, minsize=140)
        inner.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(inner, text="Tenant ID *", font=T.FONT_BODY,
                      text_color=T.DANGER, anchor="e").grid(
            row=0, column=0, padx=(T.SP_M, T.SP_S), pady=T.SP_S, sticky="e")
        self.tenant_id_entry = ctk.CTkEntry(inner, height=T.INPUT_HEIGHT,
                                             fg_color=T.SURFACE_3, border_color=T.BORDER,
                                             text_color=T.TEXT)
        self.tenant_id_entry.grid(row=0, column=1, pady=T.SP_S,
                                   padx=(0, T.SP_M), sticky="ew")

        ctk.CTkLabel(inner, text="Amount (optional)", font=T.FONT_BODY,
                      text_color=T.TEXT_MUTED, anchor="e").grid(
            row=1, column=0, padx=(T.SP_M, T.SP_S), pady=T.SP_S, sticky="e")
        self.amount_entry = ctk.CTkEntry(inner, height=T.INPUT_HEIGHT,
                                          fg_color=T.SURFACE_3, border_color=T.BORDER,
                                          text_color=T.TEXT,
                                          placeholder_text="Uses monthly rent if blank")
        self.amount_entry.grid(row=1, column=1, pady=T.SP_S,
                                padx=(0, T.SP_M), sticky="ew")

        btn = create_primary_button(inner, "Generate Invoice", self.generate)
        btn.grid(row=2, column=0, columnspan=2, pady=T.SP_L, padx=T.SP_M, sticky="ew")

        self.tenant_id_entry.bind("<Return>", lambda e: self.generate())
        self.amount_entry.bind("<Return>",    lambda e: self.generate())

    # ── All Invoices tab ──────────────────────────────────────────────────────

    def _build_list_tab(self, tab):
        frame = ctk.CTkFrame(tab, fg_color=T.BG)
        frame.pack(fill="both", expand=True)

        toolbar = ctk.CTkFrame(frame, fg_color="transparent")
        toolbar.pack(fill="x", padx=T.SP_L, pady=T.SP_S)
        create_ghost_button(toolbar, "⟳  Refresh", self._apply_filter).pack(side="right")
        self._pdf_btn = ctk.CTkButton(
            toolbar, text="📄  Save PDF", width=110, height=28,
            fg_color=T.SURFACE_3, hover_color=T.SURFACE_2,
            text_color=T.TEXT_MUTED, font=T.FONT_CAPTION_B,
            corner_radius=T.RADIUS_SM, state="disabled",
            command=self._save_selected_pdf)
        self._pdf_btn.pack(side="right", padx=(0, T.SP_S))

        self._receipt_btn = ctk.CTkButton(
            toolbar, text="🧾  View Details", width=120, height=28,
            fg_color=T.SURFACE_3, hover_color=T.SURFACE_2,
            text_color=T.TEXT_MUTED, font=T.FONT_CAPTION_B,
            corner_radius=T.RADIUS_SM, state="disabled",
            command=self._show_invoice_receipt)
        self._receipt_btn.pack(side="right", padx=(0, T.SP_S))

        self._mark_paid_btn = ctk.CTkButton(
            toolbar, text="✓  Mark Paid", width=100, height=28,
            fg_color=T.SUCCESS_MUTED, hover_color=T.SUCCESS,
            text_color=T.TEXT_MUTED, font=T.FONT_CAPTION_B,
            corner_radius=T.RADIUS_SM, state="disabled",
            command=self._mark_selected_paid)
        self._mark_paid_btn.pack(side="right", padx=(0, T.SP_S))

        self._del_inv_btn = ctk.CTkButton(
            toolbar, text="🗑  Delete", width=80, height=28,
            fg_color=T.DANGER_MUTED, hover_color=T.DANGER,
            text_color=T.TEXT_MUTED, font=T.FONT_CAPTION_B,
            corner_radius=T.RADIUS_SM, state="disabled",
            command=self._delete_selected_invoice)
        self._del_inv_btn.pack(side="right", padx=(0, T.SP_S))

        create_ghost_button(toolbar, "⬇  Export CSV",
                            self._export_invoices_csv).pack(side="right", padx=(0, T.SP_S))

        # Search + filter controls
        self._inv_search_var  = ctk.StringVar()
        self._inv_status_var  = ctk.StringVar(value="All")

        filter_row = ctk.CTkFrame(frame, fg_color="transparent")
        filter_row.pack(fill="x", padx=T.SP_L, pady=(0, T.SP_S))

        ctk.CTkLabel(filter_row, text="🔍", font=T.FONT_BODY,
                      text_color=T.TEXT_MUTED).pack(side="left", padx=(0, T.SP_XS))
        search_entry = ctk.CTkEntry(
            filter_row, textvariable=self._inv_search_var,
            height=T.INPUT_HEIGHT, width=200,
            fg_color=T.SURFACE_3, border_color=T.BORDER, text_color=T.TEXT,
            placeholder_text="Search by tenant name…")
        search_entry.pack(side="left", padx=(0, T.SP_M))
        self._inv_search_var.trace_add("write", lambda *_: self._apply_filter())

        for label in ("All", "Paid", "Pending", "Overdue"):
            btn = ctk.CTkButton(
                filter_row, text=label, width=72, height=28,
                fg_color=T.PRIMARY if label == "All" else T.SURFACE_3,
                hover_color=T.PRIMARY_HOVER if label == "All" else T.SURFACE_2,
                text_color=T.TEXT, font=T.FONT_CAPTION_B,
                corner_radius=T.RADIUS_SM,
                command=lambda l=label: self._set_status_filter(l))
            btn.pack(side="left", padx=(0, T.SP_XS))
            setattr(self, f"_inv_btn_{label.lower()}", btn)

        cols = ("ID", "Tenant", "Issued", "Due", "Amount", "Status")
        self.inv_tree = setup_treeview_scroll(
            frame, columns=cols, height=14,
            status_columns=["Status"],
            empty_message="No invoices match the current filter",
        )
        self.inv_tree.bind("<<TreeviewSelect>>", self._on_inv_select)

    # ── Overdue tab ───────────────────────────────────────────────────────────

    def _build_overdue_tab(self, tab):
        frame = ctk.CTkFrame(tab, fg_color=T.BG)
        frame.pack(fill="both", expand=True)

        # Danger header strip
        strip = ctk.CTkFrame(frame, fg_color=T.DANGER_MUTED, corner_radius=T.RADIUS_SM)
        strip.pack(fill="x", padx=T.SP_L, pady=(T.SP_S, 0))
        ctk.CTkLabel(strip, text="⚠️  These invoices are past their due date.",
                      font=T.FONT_CAPTION_B, text_color=T.DANGER).pack(
            anchor="w", padx=T.SP_M, pady=T.SP_S)

        od_toolbar = ctk.CTkFrame(frame, fg_color="transparent")
        od_toolbar.pack(fill="x", padx=T.SP_L, pady=(T.SP_S, 0))
        create_ghost_button(od_toolbar, "⟳  Refresh", self.refresh).pack(side="right")
        create_ghost_button(od_toolbar, "⬇  Export CSV",
                             self._export_overdue_csv).pack(side="right", padx=(0, T.SP_S))

        od_cols = ("ID", "Tenant", "Due Date", "Amount")
        self.od_tree = setup_treeview_scroll(
            frame, columns=od_cols, height=14,
            empty_message="✓  No overdue invoices",
        )

    # ── Late Notifications tab ─────────────────────────────────────────────────

    def _build_notif_tab(self, tab):
        frame = ctk.CTkFrame(tab, fg_color=T.BG)
        frame.pack(fill="both", expand=True)

        strip = ctk.CTkFrame(frame, fg_color=T.WARNING_MUTED, corner_radius=T.RADIUS_SM)
        strip.pack(fill="x", padx=T.SP_L, pady=(T.SP_S, 0))
        ctk.CTkLabel(strip,
                      text="⏰  These tenants have overdue invoices. Contact them for payment.",
                      font=T.FONT_CAPTION_B, text_color=T.WARNING).pack(
            anchor="w", padx=T.SP_M, pady=T.SP_S)

        notif_toolbar = ctk.CTkFrame(frame, fg_color="transparent")
        notif_toolbar.pack(fill="x", padx=T.SP_L, pady=(T.SP_S, 0))
        create_ghost_button(notif_toolbar, "⟳  Refresh", self.refresh).pack(side="right")
        create_ghost_button(notif_toolbar, "⬇  Export CSV",
                             self._export_notif_csv).pack(side="right", padx=(0, T.SP_S))

        cols = ("Invoice", "Tenant", "Email", "Phone", "Due Date", "Amount", "Days Overdue")
        self.notif_tree = setup_treeview_scroll(
            frame, columns=cols, height=11,
            status_columns=["Days Overdue"],
            empty_message="✓  No late payment notifications",
        )
        for c in cols:
            self.notif_tree.heading(c, text=c)
            self.notif_tree.column(c, width=100)

    # ── Actions ───────────────────────────────────────────────────────────────

    def _show_invoice_receipt(self):
        selected = self.inv_tree.selection()
        if not selected:
            return
        inv_id   = int(self.inv_tree.item(selected[0], "values")[0])
        payments = self.invoice_manager.get_payments_for_invoice(inv_id)

        try:
            d = self.invoice_manager.get_invoice_pdf_data(inv_id)
        except Exception as ex:
            show_error(self._root, str(ex))
            return

        popup = ctk.CTkToplevel(self._root)
        popup.geometry("480x640")
        popup.resizable(False, False)
        popup.grab_set()
        popup.configure(fg_color=T.SURFACE)

        import tkinter as _tk

        if payments:
            popup.title("Payment Receipt")
            payment_id = payments[0][0]
            try:
                r = self.payment_manager.get_receipt_data(payment_id)
            except Exception as ex:
                show_error(self._root, str(ex))
                popup.destroy()
                return
            header_text  = "Payment Receipt"
            band_color   = T.PRIMARY_MUTED
        else:
            popup.title("Invoice Details")
            r            = None
            header_text  = "Invoice Details"
            band_color   = T.SURFACE_2

        band = ctk.CTkFrame(popup, fg_color=band_color, corner_radius=0)
        band.pack(fill="x")
        ctk.CTkLabel(band, text="🏢  PAMS", font=T.FONT_H2,
                      text_color=T.TEXT).pack(pady=(T.SP_L, T.SP_XS))
        ctk.CTkLabel(band, text=header_text, font=T.FONT_H3,
                      text_color=T.TEXT_MUTED).pack(pady=(0, T.SP_L))
        _tk.Frame(popup, bg=T.BORDER, height=1).pack(fill="x")

        body = ctk.CTkScrollableFrame(popup, fg_color="transparent",
                                       scrollbar_button_color=T.SURFACE_3)
        body.pack(fill="both", expand=True, padx=T.SP_XL, pady=T.SP_L)

        if r:
            if len(payments) > 1:
                ctk.CTkLabel(body,
                              text=f"Showing most recent of {len(payments)} payments.",
                              font=T.FONT_CAPTION, text_color=T.TEXT_MUTED).pack(
                    anchor="w", pady=(0, T.SP_S))
            sections = [
                ("Tenant", [
                    ("Receipt #",  f"PAY-{r['payment_id']}"),
                    ("Date",       r["payment_date"]),
                    ("Tenant",     r["tenant_name"]),
                    ("NI",         r["ni_number"]),
                    ("Email",      r["email"]),
                    ("Phone",      r["phone"]),
                ]),
                ("Property", [
                    ("Unit",    f"Unit {r['unit']}" if r["unit"] else "-"),
                    ("Address", r["address"]),
                    ("City",    r["city"]),
                ]),
                ("Invoice", [
                    ("Invoice #",     f"INV-{r['invoice_id']}"),
                    ("Invoice Total", f"£{r['invoice_total']:.2f}"),
                ]),
                ("Payment", [
                    ("Amount Paid", f"£{r['amount']:.2f}"),
                    ("Method",      r["method"]),
                    ("Reference",   r["reference"]),
                    ("Status",      r["invoice_status"]),
                ]),
            ]
        else:
            sections = [
                ("Invoice", [
                    ("Invoice #",  f"INV-{d['invoice_id']:04d}"),
                    ("Issue Date", d["issue_date"]),
                    ("Due Date",   d["due_date"]),
                    ("Amount",     f"£{d['total_amount']:.2f}"),
                    ("Status",     d["status"]),
                ]),
                ("Tenant", [
                    ("Name",  d["tenant_name"]),
                    ("NI",    d["ni_number"]),
                    ("Email", d["email"] or "-"),
                    ("Phone", d["phone"] or "-"),
                ]),
                ("Property", [
                    ("Unit",    f"Unit {d['unit']}" if d["unit"] else "-"),
                    ("Address", d["address"] or "-"),
                    ("City",    d["city"] or "-"),
                ]),
            ]

        for section_title, fields in sections:
            sec = ctk.CTkFrame(body, fg_color=T.SURFACE_2, corner_radius=T.RADIUS_SM)
            sec.pack(fill="x", pady=(0, T.SP_S))
            ctk.CTkLabel(sec, text=section_title, font=T.FONT_CAPTION_B,
                          text_color=T.TEXT_SUBTLE).pack(
                anchor="w", padx=T.SP_M, pady=(T.SP_S, 0))
            for label, value in fields:
                row = ctk.CTkFrame(sec, fg_color="transparent")
                row.pack(fill="x", padx=T.SP_M, pady=T.SP_XS)
                ctk.CTkLabel(row, text=label, font=T.FONT_CAPTION,
                              text_color=T.TEXT_MUTED, width=120, anchor="e").pack(side="left")
                ctk.CTkLabel(row, text=str(value) if value else "-",
                              font=T.FONT_CAPTION_B, text_color=T.TEXT,
                              anchor="w").pack(side="left", padx=(T.SP_S, 0))
            ctk.CTkFrame(sec, height=T.SP_XS, fg_color="transparent").pack()

        _tk.Frame(popup, bg=T.BORDER, height=1).pack(fill="x")
        from views.ui_helpers import create_primary_button
        create_primary_button(popup, "Close", popup.destroy, width=120).pack(pady=T.SP_L)
        popup.bind("<Return>", lambda e: popup.destroy())
        popup.bind("<Escape>", lambda e: popup.destroy())

    def _on_inv_select(self, event=None):
        selected = self.inv_tree.selection()
        has = bool(selected)
        color = T.TEXT if has else T.TEXT_MUTED
        self._pdf_btn.configure(state="normal" if has else "disabled",
                                text_color=color)
        self._receipt_btn.configure(state="normal" if has else "disabled",
                                    text_color=color)
        # Mark Paid + Delete only for Pending/Overdue
        is_unpaid = False
        if has:
            status = self.inv_tree.item(selected[0], "values")[5]
            is_unpaid = status in ("Pending", "Overdue")
        btn_color = T.TEXT if is_unpaid else T.TEXT_MUTED
        self._mark_paid_btn.configure(
            state="normal" if is_unpaid else "disabled",
            text_color=btn_color)
        self._del_inv_btn.configure(
            state="normal" if is_unpaid else "disabled",
            text_color=btn_color)

    def _mark_selected_paid(self):
        selected = self.inv_tree.selection()
        if not selected:
            return
        inv_id = int(self.inv_tree.item(selected[0], "values")[0])
        tenant = self.inv_tree.item(selected[0], "values")[1]
        if not confirm_dialog(self._root, "Mark as Paid",
                              f"Mark invoice #{inv_id} for {tenant} as Paid?"):
            return
        try:
            self.invoice_manager.mark_paid(inv_id)
            show_success(self._root, f"Invoice #{inv_id} marked as Paid.")
            self.refresh()
        except Exception as ex:
            show_error(self._root, str(ex))

    def _delete_selected_invoice(self):
        selected = self.inv_tree.selection()
        if not selected:
            return
        inv_id = int(self.inv_tree.item(selected[0], "values")[0])
        tenant = self.inv_tree.item(selected[0], "values")[1]
        if not confirm_dialog(self._root, "Delete Invoice",
                              f"Permanently delete invoice #{inv_id} for {tenant}?",
                              danger=True):
            return
        try:
            self.invoice_manager.delete_invoice(inv_id)
            show_success(self._root, f"Invoice #{inv_id} deleted.")
            self.refresh()
        except Exception as ex:
            show_error(self._root, str(ex))

    def _export_overdue_csv(self):
        from tkinter import filedialog
        path = filedialog.asksaveasfilename(
            parent=self._root, defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="overdue_invoices.csv", title="Export Overdue Invoices to CSV")
        if not path:
            return
        rows = self.invoice_manager.get_overdue_invoices()
        export_table_to_csv(["ID", "Tenant", "Due Date", "Amount"], rows, path)
        show_success(self._root, f"Exported {len(rows)} rows to CSV.")

    def _export_notif_csv(self):
        from tkinter import filedialog
        path = filedialog.asksaveasfilename(
            parent=self._root, defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="late_notifications.csv", title="Export Late Notifications to CSV")
        if not path:
            return
        rows = self.invoice_manager.get_overdue_with_details()
        export_table_to_csv(
            ["Invoice ID", "Tenant", "Email", "Phone", "Due Date", "Amount", "Days Overdue"],
            rows, path)
        show_success(self._root, f"Exported {len(rows)} rows to CSV.")

    def _export_invoices_csv(self):
        from tkinter import filedialog
        filepath = filedialog.asksaveasfilename(
            parent=self._root,
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="invoices_export.csv",
            title="Export Invoices to CSV",
        )
        if not filepath:
            return
        status      = self._inv_status_var.get()  if hasattr(self, "_inv_status_var")  else None
        tenant_name = self._inv_search_var.get()   if hasattr(self, "_inv_search_var")   else None
        rows = self.invoice_manager.search_invoices(status, tenant_name)
        headers = ["ID", "Tenant", "Issue Date", "Due Date", "Amount", "Status"]
        export_table_to_csv(headers, rows, filepath)
        show_success(self._root, f"Exported {len(rows)} rows to CSV.")

    def _save_selected_pdf(self):
        selected = self.inv_tree.selection()
        if not selected:
            show_warning(self._root, "Select an invoice from the list first.")
            return
        invoice_id = int(self.inv_tree.item(selected[0], "values")[0])
        filepath = filedialog.asksaveasfilename(
            parent=self._root,
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=f"Invoice_INV-{invoice_id:04d}.pdf",
            title="Save Invoice PDF",
        )
        if not filepath:
            return
        try:
            data = self.invoice_manager.get_invoice_pdf_data(invoice_id)
            from views.pdf_generator import generate_invoice_pdf, open_file
            generate_invoice_pdf(data, filepath)
            open_file(filepath)
            show_success(self._root,
                         f"PDF saved: {__import__('os').path.basename(filepath)}")
        except Exception as ex:
            show_error(self._root, str(ex))

    def _set_status_filter(self, label):
        self._inv_status_var.set(label)
        for l in ("All", "Paid", "Pending", "Overdue"):
            btn = getattr(self, f"_inv_btn_{l.lower()}", None)
            if btn:
                active = l == label
                btn.configure(
                    fg_color=T.PRIMARY if active else T.SURFACE_3,
                    hover_color=T.PRIMARY_HOVER if active else T.SURFACE_2)
        self._apply_filter()

    def _apply_filter(self):
        status      = self._inv_status_var.get() if hasattr(self, "_inv_status_var") else None
        tenant_name = self._inv_search_var.get()  if hasattr(self, "_inv_search_var")  else None
        for item in self.inv_tree.get_children():
            self.inv_tree.delete(item)
        for inv in self.invoice_manager.search_invoices(status, tenant_name):
            status_display = inv[5]
            if inv[5] == "Pending":
                try:
                    if datetime.strptime(inv[3], "%Y-%m-%d") < datetime.now():
                        status_display = "Overdue"
                except (ValueError, TypeError):
                    pass
            self.inv_tree.insert("", "end", values=(
                inv[0], inv[1], inv[2], inv[3], f"£{inv[4]:.2f}", status_display))
        apply_row_stripes(self.inv_tree)
        autofit_columns(self.inv_tree)

    def generate(self):
        tid = self.tenant_id_entry.get()
        amt = self.amount_entry.get()
        if not tid:
            show_warning(self._root, "Tenant ID is required.")
            return
        try:
            val = float(amt) if amt.strip() else None
            self.invoice_manager.generate_invoice(int(tid), val)
            show_success(self._root, "Invoice generated successfully.")
            self.tenant_id_entry.delete(0, "end")
            self.amount_entry.delete(0, "end")
            self.refresh()
        except ValueError:
            show_error(self._root, "Tenant ID and Amount must be valid numbers.")
        except Exception as ex:
            show_error(self._root, str(ex))

    def refresh(self):
        # All Invoices — delegate to filter (preserves current search/filter state)
        self._apply_filter()

        # Overdue
        for item in self.od_tree.get_children():
            self.od_tree.delete(item)
        for od in self.invoice_manager.get_overdue_invoices():
            self.od_tree.insert("", "end", values=(
                od[0], od[1], od[2], f"£{od[3]:.2f}"))
        apply_row_stripes(self.od_tree)
        autofit_columns(self.od_tree)

        # Late Notifications
        if hasattr(self, "notif_tree"):
            for item in self.notif_tree.get_children():
                self.notif_tree.delete(item)
            for row in self.invoice_manager.get_overdue_with_details():
                self.notif_tree.insert("", "end", values=(
                    row[0], row[1], row[2] or "N/A", row[3] or "N/A",
                    row[4], f"£{row[5]:.2f}", f"{row[6]} days"))
            apply_row_stripes(self.notif_tree)
            autofit_columns(self.notif_tree)