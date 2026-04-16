# Student Name: Ahmed Deraz
# Student ID: 24046227

import customtkinter as ctk
import tkinter as tk
from datetime import datetime
from invoice_manager import InvoiceManager
from views import theme as T
from views.ui_helpers import (
    setup_treeview_scroll, autofit_columns, apply_row_stripes,
    create_page_header, create_card, create_card_fill,
    create_primary_button, create_ghost_button,
    show_success, show_error, show_warning,
    create_empty_state,
)


class InvoiceView:
    def __init__(self, parent, db_manager):
        self.db_manager     = db_manager
        self.invoice_manager = InvoiceManager(db_manager)
        self._root = parent.winfo_toplevel()

        frame = ctk.CTkFrame(parent, fg_color=T.BG)
        frame.pack(fill="both", expand=True)

        create_page_header(frame, "💰 Invoices",
                            subtitle="Generate and track tenant invoices")

        self.tabview = ctk.CTkTabview(frame,
                                       fg_color=T.SURFACE,
                                       segmented_button_fg_color=T.SURFACE_2,
                                       segmented_button_selected_color=T.PRIMARY,
                                       segmented_button_selected_hover_color=T.PRIMARY_HOVER,
                                       segmented_button_unselected_color=T.SURFACE_2,
                                       segmented_button_unselected_hover_color=T.SURFACE_3,
                                       text_color=T.TEXT)
        self.tabview.pack(fill="both", expand=True, padx=T.SP_XL, pady=(0, T.SP_XL))

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
        create_ghost_button(toolbar, "⟳  Refresh", self.refresh).pack(side="right")

        cols = ("ID", "Tenant", "Issued", "Due", "Amount", "Status")
        self.inv_tree = setup_treeview_scroll(
            frame, columns=cols, height=15,
            status_columns=["Status"],
            empty_message="No invoices yet — generate one from the first tab",
        )

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

        od_cols = ("ID", "Tenant", "Due Date", "Amount")
        self.od_tree = setup_treeview_scroll(
            frame, columns=od_cols, height=15,
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

        cols = ("Invoice", "Tenant", "Email", "Phone", "Due Date", "Amount", "Days Overdue")
        self.notif_tree = setup_treeview_scroll(
            frame, columns=cols, height=12,
            status_columns=["Days Overdue"],
            empty_message="✓  No late payment notifications",
        )
        for c in cols:
            self.notif_tree.heading(c, text=c)
            self.notif_tree.column(c, width=100)

    # ── Actions ───────────────────────────────────────────────────────────────

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
        # All Invoices
        for item in self.inv_tree.get_children():
            self.inv_tree.delete(item)
        for inv in self.invoice_manager.get_all_invoices():
            status_display = inv[5]
            if inv[5] == "Pending":
                try:
                    due = datetime.strptime(inv[3], "%Y-%m-%d")
                    if due < datetime.now():
                        status_display = "Overdue"
                except (ValueError, TypeError):
                    pass
            self.inv_tree.insert("", "end", values=(
                inv[0], inv[1], inv[2], inv[3], f"£{inv[4]:.2f}", status_display))
        apply_row_stripes(self.inv_tree)
        autofit_columns(self.inv_tree)

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