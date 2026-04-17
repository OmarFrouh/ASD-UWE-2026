# Student Name: Ahmed Deraz
# Student ID: 24046227

import customtkinter as ctk
import tkinter as tk
from payment_manager import PaymentManager
from views import theme as T
from views.ui_helpers import (
    setup_treeview_scroll, autofit_columns, apply_row_stripes,
    create_page_header, create_card, create_card_fill, create_kpi_tile_l, create_tabview,
    create_primary_button, create_ghost_button,
    show_success, show_error, show_warning,
    confirm_dialog, export_table_to_csv,
)


class PaymentView:
    def __init__(self, parent, db_manager):
        self.db_manager      = db_manager
        self.payment_manager = PaymentManager(db_manager)
        self._root = parent.winfo_toplevel()

        frame = ctk.CTkFrame(parent, fg_color=T.BG)
        frame.pack(fill="both", expand=True)

        create_page_header(frame, "💳 Payments",
                            subtitle="Record payments and view financial data")

        self.tabview = create_tabview(frame)

        tab_record  = self.tabview.add("Record Payment")
        tab_history = self.tabview.add("Payment History")
        tab_summary = self.tabview.add("Financial Summary")

        self._build_record_tab(tab_record)
        self._build_history_tab(tab_history)
        self._build_summary_tab(tab_summary)
        self.refresh()

    # ── Record tab ────────────────────────────────────────────────────────────

    def _build_record_tab(self, tab):
        scroll = ctk.CTkScrollableFrame(tab, fg_color=T.BG,
                                         scrollbar_button_color=T.SURFACE_3)
        scroll.pack(fill="both", expand=True)
        inner = create_card(scroll, title="Record Payment")
        inner.grid_columnconfigure(0, minsize=120)
        inner.grid_columnconfigure(1, weight=1)

        def _lbl(t, row, req=False):
            ctk.CTkLabel(inner, text=t + (" *" if req else ""),
                          font=T.FONT_BODY, anchor="e",
                          text_color=T.DANGER if req else T.TEXT_MUTED).grid(
                row=row, column=0, padx=(T.SP_M, T.SP_S), pady=T.SP_S, sticky="e")

        def _entry(row, placeholder=""):
            e = ctk.CTkEntry(inner, height=T.INPUT_HEIGHT,
                              fg_color=T.SURFACE_3, border_color=T.BORDER,
                              text_color=T.TEXT, placeholder_text=placeholder)
            e.grid(row=row, column=1, pady=T.SP_S, padx=(0, T.SP_M), sticky="ew")
            return e

        _lbl("Invoice ID",  0, True);  self.inv_id_entry     = _entry(0)
        _lbl("Amount (£)", 1, True);  self.pay_amount_entry = _entry(1, "e.g. 850.00")
        _lbl("Method",     2, True)
        self.method_combo = ctk.CTkComboBox(
            inner, values=["Card", "Cash", "Bank Transfer"],
            height=T.INPUT_HEIGHT,
            fg_color=T.SURFACE_3, border_color=T.BORDER,
            button_color=T.SURFACE_3, dropdown_fg_color=T.SURFACE,
            text_color=T.TEXT)
        self.method_combo.grid(row=2, column=1, pady=T.SP_S, padx=(0, T.SP_M), sticky="ew")
        self.method_combo.set("Card")
        _lbl("Reference",  3);         self.ref_entry        = _entry(3, "Optional")

        btn = create_primary_button(inner, "Record Payment", self.record)
        btn.grid(row=4, column=0, columnspan=2, pady=T.SP_L, padx=T.SP_M, sticky="ew")

        for e in [self.inv_id_entry, self.pay_amount_entry, self.ref_entry]:
            e.bind("<Return>", lambda ev: self.record())

    # ── History tab ───────────────────────────────────────────────────────────

    def _build_history_tab(self, tab):
        frame = ctk.CTkFrame(tab, fg_color=T.BG)
        frame.pack(fill="both", expand=True)
        toolbar = ctk.CTkFrame(frame, fg_color="transparent")
        toolbar.pack(fill="x", padx=T.SP_L, pady=T.SP_S)
        create_ghost_button(toolbar, "⟳  Refresh", self.refresh).pack(side="right")

        create_ghost_button(toolbar, "⬇  Export CSV",
                            self._export_payments_csv).pack(side="right", padx=(0, T.SP_S))

        self._void_btn = ctk.CTkButton(
            toolbar, text="🗑  Void", width=80, height=28,
            fg_color=T.DANGER_MUTED, hover_color=T.DANGER,
            text_color=T.TEXT_MUTED, font=T.FONT_CAPTION_B,
            corner_radius=T.RADIUS_SM, state="disabled",
            command=self._void_selected_payment)
        self._void_btn.pack(side="right", padx=(0, T.SP_S))

        self._pay_receipt_btn = ctk.CTkButton(
            toolbar, text="🧾  View Receipt", width=120, height=28,
            fg_color=T.SURFACE_3, hover_color=T.SURFACE_2,
            text_color=T.TEXT_MUTED, font=T.FONT_CAPTION_B,
            corner_radius=T.RADIUS_SM, state="disabled",
            command=self._view_selected_receipt)
        self._pay_receipt_btn.pack(side="right", padx=(0, T.SP_S))

        cols = ("ID", "Tenant", "Amount", "Date", "Method", "Ref", "Invoice")
        self.pay_tree = setup_treeview_scroll(
            frame, columns=cols, height=15,
            empty_message="No payments recorded yet",
        )
        self.pay_tree.bind("<<TreeviewSelect>>", self._on_pay_select)

    # ── Summary tab ───────────────────────────────────────────────────────────

    def _build_summary_tab(self, tab):
        scroll = ctk.CTkScrollableFrame(tab, fg_color=T.BG,
                                         scrollbar_button_color=T.SURFACE_3)
        scroll.pack(fill="both", expand=True)

        # KPI tiles row
        self.kpi_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        self.kpi_frame.pack(fill="x", padx=T.SP_XL, pady=(T.SP_M, 0))

        # Breakdown tables
        bd_inner = create_card_fill(scroll, title="Payment Method Breakdown")
        bd_toolbar = ctk.CTkFrame(bd_inner, fg_color="transparent")
        bd_toolbar.pack(fill="x", pady=(0, T.SP_S))
        create_ghost_button(bd_toolbar, "⬇  Export CSV",
                             self._export_method_breakdown_csv).pack(side="right")
        cols = ("Payment Method", "Total Amount", "Transaction Count")
        self.sum_tree = setup_treeview_scroll(bd_inner, columns=cols,
                                               col_widths=[180, 150, 150], height=4,
                                               empty_message="No payment data yet",
                                               )

        rev_inner = create_card_fill(scroll, title="Monthly Revenue (Last 6 Months)")
        rev_toolbar = ctk.CTkFrame(rev_inner, fg_color="transparent")
        rev_toolbar.pack(fill="x", pady=(0, T.SP_S))
        create_ghost_button(rev_toolbar, "⬇  Export CSV",
                             self._export_monthly_revenue_csv).pack(side="right")
        rev_cols = ("Month", "Total Collected")
        self.rev_tree = setup_treeview_scroll(rev_inner, columns=rev_cols,
                                               col_widths=[200, 200], height=6,
                                               empty_message="No revenue data for the last 6 months",
                                               )

    # ── Payment History actions ────────────────────────────────────────────────

    def _on_pay_select(self, event=None):
        selected = self.pay_tree.selection()
        has = bool(selected)
        color = T.TEXT if has else T.TEXT_MUTED
        self._pay_receipt_btn.configure(state="normal" if has else "disabled",
                                        text_color=color)
        self._void_btn.configure(state="normal" if has else "disabled",
                                 text_color=color)

    def _view_selected_receipt(self):
        selected = self.pay_tree.selection()
        if not selected:
            return
        pay_id = int(self.pay_tree.item(selected[0], "values")[0])
        self.show_receipt(pay_id)

    def _void_selected_payment(self):
        selected = self.pay_tree.selection()
        if not selected:
            return
        pay_id = int(self.pay_tree.item(selected[0], "values")[0])
        tenant = self.pay_tree.item(selected[0], "values")[1]
        amount = self.pay_tree.item(selected[0], "values")[2]
        if not confirm_dialog(self._root, "Void Payment",
                              f"Void {amount} payment for {tenant}?\n"
                              "The invoice will revert to Pending if this was the only payment.",
                              danger=True):
            return
        try:
            self.payment_manager.void_payment(pay_id)
            show_success(self._root, "Payment voided. Invoice reverted if applicable.")
            self.refresh()
        except Exception as ex:
            show_error(self._root, str(ex))

    def _export_method_breakdown_csv(self):
        from tkinter import filedialog
        path = filedialog.asksaveasfilename(
            parent=self._root, defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="payment_methods.csv", title="Export Method Breakdown to CSV")
        if not path:
            return
        rows = self.payment_manager.get_payment_history_by_method()
        export_table_to_csv(["Payment Method", "Total Amount", "Transaction Count"], rows, path)
        show_success(self._root, f"Exported {len(rows)} rows to CSV.")

    def _export_monthly_revenue_csv(self):
        from tkinter import filedialog
        path = filedialog.asksaveasfilename(
            parent=self._root, defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="monthly_revenue.csv", title="Export Monthly Revenue to CSV")
        if not path:
            return
        rows = self.payment_manager.get_monthly_revenue()
        export_table_to_csv(["Month", "Total Collected"], rows, path)
        show_success(self._root, f"Exported {len(rows)} rows to CSV.")

    def _export_payments_csv(self):
        from tkinter import filedialog
        filepath = filedialog.asksaveasfilename(
            parent=self._root,
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="payments_export.csv",
            title="Export Payments to CSV",
        )
        if not filepath:
            return
        rows = self.payment_manager.get_all_payments()
        headers = ["ID", "Tenant", "Amount", "Date", "Method", "Reference", "Invoice ID"]
        export_table_to_csv(headers, rows, filepath)
        show_success(self._root, f"Exported {len(rows)} rows to CSV.")

    # ── Receipt popup ─────────────────────────────────────────────────────────

    def show_receipt(self, payment_id):
        try:
            r = self.payment_manager.get_receipt_data(payment_id)
        except Exception:
            return

        popup = ctk.CTkToplevel()
        popup.title("Payment Receipt")
        popup.geometry("480x600")
        popup.resizable(False, False)
        popup.grab_set()
        popup.configure(fg_color=T.SURFACE)

        # Brand band
        band = ctk.CTkFrame(popup, fg_color=T.PRIMARY_MUTED, corner_radius=0)
        band.pack(fill="x")
        ctk.CTkLabel(band, text="🏢  PAMS", font=T.FONT_H2,
                      text_color=T.TEXT).pack(pady=(T.SP_L, T.SP_XS))
        ctk.CTkLabel(band, text="Payment Receipt", font=T.FONT_H3,
                      text_color=T.TEXT_MUTED).pack(pady=(0, T.SP_L))

        tk.Frame(popup, bg=T.BORDER, height=1).pack(fill="x")

        body = ctk.CTkScrollableFrame(popup, fg_color="transparent",
                                       scrollbar_button_color=T.SURFACE_3)
        body.pack(fill="both", expand=True, padx=T.SP_XL, pady=T.SP_L)

        sections = [
            ("Tenant", [
                ("Receipt #", f"PAY-{r['payment_id']}"),
                ("Date", r["payment_date"]),
                ("Tenant", r["tenant_name"]),
                ("NI", r["ni_number"]),
                ("Email", r["email"]),
                ("Phone", r["phone"]),
            ]),
            ("Property", [
                ("Unit", f"Unit {r['unit']}"),
                ("Address", r["address"]),
                ("City", r["city"]),
            ]),
            ("Invoice", [
                ("Invoice #", f"INV-{r['invoice_id']}"),
                ("Invoice Total", f"£{r['invoice_total']:.2f}"),
            ]),
            ("Payment", [
                ("Amount Paid", f"£{r['amount']:.2f}"),
                ("Method", r["method"]),
                ("Reference", r["reference"]),
                ("Status", r["invoice_status"]),
            ]),
        ]

        for (section_title, fields) in sections:
            sec = ctk.CTkFrame(body, fg_color=T.SURFACE_2,
                                corner_radius=T.RADIUS_SM)
            sec.pack(fill="x", pady=(0, T.SP_S))
            ctk.CTkLabel(sec, text=section_title, font=T.FONT_CAPTION_B,
                          text_color=T.TEXT_SUBTLE).pack(
                anchor="w", padx=T.SP_M, pady=(T.SP_S, 0))
            for label, value in fields:
                row = ctk.CTkFrame(sec, fg_color="transparent")
                row.pack(fill="x", padx=T.SP_M, pady=T.SP_XS)
                ctk.CTkLabel(row, text=label, font=T.FONT_CAPTION,
                              text_color=T.TEXT_MUTED, width=120, anchor="e").pack(side="left")
                ctk.CTkLabel(row, text=str(value) if value else "—",
                              font=T.FONT_CAPTION_B, text_color=T.TEXT,
                              anchor="w").pack(side="left", padx=(T.SP_S, 0))
            ctk.CTkFrame(sec, height=T.SP_XS, fg_color="transparent").pack()

        tk.Frame(popup, bg=T.BORDER, height=1).pack(fill="x")
        create_primary_button(popup, "Close", popup.destroy, width=120).pack(pady=T.SP_L)
        popup.bind("<Return>", lambda e: popup.destroy())
        popup.bind("<Escape>", lambda e: popup.destroy())

    # ── Actions ───────────────────────────────────────────────────────────────

    def record(self):
        iid = self.inv_id_entry.get()
        amt = self.pay_amount_entry.get()
        method = self.method_combo.get()
        ref    = self.ref_entry.get()

        if not iid or not amt:
            show_warning(self._root, "Invoice ID and Amount are required.")
            return
        try:
            payment_id = self.payment_manager.record_payment(
                int(iid), float(amt), method, ref)
            for e in [self.inv_id_entry, self.pay_amount_entry, self.ref_entry]:
                e.delete(0, "end")
            self.refresh()
            self.show_receipt(payment_id)
        except ValueError:
            show_error(self._root, "Invoice ID and Amount must be valid numbers.")
        except Exception as ex:
            show_error(self._root, str(ex))

    def refresh(self):
        # Payment History
        for item in self.pay_tree.get_children():
            self.pay_tree.delete(item)
        for p in self.payment_manager.get_all_payments():
            self.pay_tree.insert("", "end", values=(
                p[0], p[1], f"£{p[2]:.2f}", p[3], p[4], p[5], p[6]))
        apply_row_stripes(self.pay_tree)
        autofit_columns(self.pay_tree)
        self._refresh_summary()

    def _refresh_summary(self):
        if not hasattr(self, "kpi_frame"):
            return
        for w in self.kpi_frame.winfo_children():
            w.destroy()

        summary = self.payment_manager.get_collected_vs_pending()
        kpi_data = [
            ("Collected",     f"£{summary['collected']:.2f}", "success"),
            ("Pending",       f"£{summary['pending']:.2f}",   "warning"),
            ("Total Invoiced",f"£{summary['total']:.2f}",     "primary"),
        ]
        for i, (label, val, kind) in enumerate(kpi_data):
            tile = create_kpi_tile_l(self.kpi_frame, label=label, value=val, kind=kind)
            tile.grid(row=0, column=i, padx=T.SP_M, pady=T.SP_S, sticky="nsew")
            self.kpi_frame.grid_columnconfigure(i, weight=1)

        # Breakdown
        for item in self.sum_tree.get_children():
            self.sum_tree.delete(item)
        for row in self.payment_manager.get_payment_history_by_method():
            self.sum_tree.insert("", "end", values=(row[0], f"£{row[1]:.2f}", row[2]))
        apply_row_stripes(self.sum_tree)
        autofit_columns(self.sum_tree)

        for item in self.rev_tree.get_children():
            self.rev_tree.delete(item)
        for row in self.payment_manager.get_monthly_revenue():
            self.rev_tree.insert("", "end", values=(row[0], f"£{row[1]:.2f}"))
        apply_row_stripes(self.rev_tree)
        autofit_columns(self.rev_tree)