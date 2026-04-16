# Student Name: Omar Alfrouh
# Student ID: 24020879

import customtkinter as ctk
import tkinter as tk
from report_manager import ReportManager
from views import theme as T
from views.ui_helpers import (
    setup_treeview_scroll, autofit_columns, apply_row_stripes,
    create_page_header, create_card, create_card_fill, create_kpi_tile_l,
    create_ghost_button,
)


class ReportView:
    def __init__(self, parent, db_manager):
        self.db_manager     = db_manager
        self.report_manager = ReportManager(db_manager)
        self._root = parent.winfo_toplevel()

        frame = ctk.CTkFrame(parent, fg_color=T.BG)
        frame.pack(fill="both", expand=True)

        create_page_header(frame, "📈 Reports",
                            subtitle="Occupancy, financial, and maintenance analytics")

        self.tabview = ctk.CTkTabview(frame,
                                       fg_color=T.SURFACE,
                                       segmented_button_fg_color=T.SURFACE_2,
                                       segmented_button_selected_color=T.PRIMARY,
                                       segmented_button_selected_hover_color=T.PRIMARY_HOVER,
                                       segmented_button_unselected_color=T.SURFACE_2,
                                       segmented_button_unselected_hover_color=T.SURFACE_3,
                                       text_color=T.TEXT)
        self.tabview.pack(fill="both", expand=True, padx=T.SP_XL, pady=(0, T.SP_XL))

        tab_occ = self.tabview.add("Occupancy")
        tab_fin = self.tabview.add("Financial Summary")
        tab_mnt = self.tabview.add("Maintenance Costs")

        self._build_occupancy_tab(tab_occ)
        self._build_financial_tab(tab_fin)
        self._build_maintenance_tab(tab_mnt)

    # ── Occupancy ─────────────────────────────────────────────────────────────

    def _build_occupancy_tab(self, tab):
        scroll = ctk.CTkScrollableFrame(tab, fg_color=T.BG,
                                         scrollbar_button_color=T.SURFACE_3)
        scroll.pack(fill="both", expand=True)

        # Filter bar card
        filter_inner = create_card(scroll)
        filter_inner.pack_configure(pady=(0, T.SP_XS))
        ctk.CTkLabel(filter_inner, text="City:", font=T.FONT_BODY,
                      text_color=T.TEXT_MUTED).pack(side="left", padx=(0, T.SP_S))
        cities = ["All"] + self.report_manager.get_cities()
        self.occ_city_filter = ctk.CTkComboBox(
            filter_inner, values=cities, width=180, height=T.INPUT_HEIGHT,
            fg_color=T.SURFACE_3, border_color=T.BORDER,
            button_color=T.SURFACE_3, dropdown_fg_color=T.SURFACE,
            text_color=T.TEXT,
            command=lambda _: self.refresh_occupancy())
        self.occ_city_filter.pack(side="left")
        self.occ_city_filter.set("All")

        # KPI tiles
        self.occ_kpi_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        self.occ_kpi_frame.pack(fill="x", padx=T.SP_XL, pady=(0, T.SP_S))

        # Table card
        tbl_inner = create_card_fill(scroll, title="Apartment Occupancy")
        cols = ("Unit", "Address", "City", "Rooms", "Rent", "Status")
        self.occ_tree = setup_treeview_scroll(
            tbl_inner, columns=cols, height=12,
            status_columns=["Status"])
        self.refresh_occupancy()

    def refresh_occupancy(self):
        city = self.occ_city_filter.get()

        for w in self.occ_kpi_frame.winfo_children():
            w.destroy()
        summary = self.report_manager.get_occupancy_summary(city)
        kpi_data = [
            ("Total",    str(summary["total"]),            "primary"),
            ("Occupied", str(summary["occupied"]),         "success"),
            ("Vacant",   str(summary["vacant"]),           "muted"),
            ("Rate",     f"{summary['occupancy_rate']}%",  "info"),
        ]
        for i, (label, val, kind) in enumerate(kpi_data):
            tile = create_kpi_tile_l(self.occ_kpi_frame, label=label,
                                      value=val, kind=kind)
            tile.grid(row=0, column=i, padx=T.SP_M, pady=T.SP_S, sticky="nsew")
            self.occ_kpi_frame.grid_columnconfigure(i, weight=1)

        for item in self.occ_tree.get_children():
            self.occ_tree.delete(item)
        for apt in self.report_manager.get_occupancy_report(city):
            self.occ_tree.insert("", "end", values=(
                apt[0], apt[1], apt[2], apt[3], f"£{apt[4]:.2f}", apt[5]))
        apply_row_stripes(self.occ_tree)
        autofit_columns(self.occ_tree)

    # ── Financial Summary ─────────────────────────────────────────────────────

    def _build_financial_tab(self, tab):
        scroll = ctk.CTkScrollableFrame(tab, fg_color=T.BG,
                                         scrollbar_button_color=T.SURFACE_3)
        scroll.pack(fill="both", expand=True)

        self.fin_kpi_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        self.fin_kpi_frame.pack(fill="x", padx=T.SP_XL, pady=(T.SP_S, 0))

        toolbar_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        toolbar_frame.pack(fill="x", padx=T.SP_XL, pady=T.SP_XS)
        create_ghost_button(toolbar_frame, "⟳  Refresh",
                             self.refresh_financial).pack(side="right")

        tbl_inner = create_card_fill(scroll, title="Per-Tenant Financial Breakdown")
        cols = ("Tenant", "Total Invoiced", "Total Paid", "Outstanding")
        self.fin_tree = setup_treeview_scroll(tbl_inner, columns=cols, height=12)
        self.refresh_financial()

    def refresh_financial(self):
        for w in self.fin_kpi_frame.winfo_children():
            w.destroy()
        summary = self.report_manager.get_financial_summary()
        kpi_data = [
            ("Collected",       f"£{summary['collected']:.2f}",      "success"),
            ("Pending",         f"£{summary['pending']:.2f}",         "warning"),
            ("Total Invoiced",  f"£{summary['total_invoiced']:.2f}",  "primary"),
            ("Collection Rate", f"{summary['collection_rate']}%",     "info"),
        ]
        for i, (label, val, kind) in enumerate(kpi_data):
            tile = create_kpi_tile_l(self.fin_kpi_frame, label=label,
                                      value=val, kind=kind)
            tile.grid(row=0, column=i, padx=T.SP_M, pady=T.SP_S, sticky="nsew")
            self.fin_kpi_frame.grid_columnconfigure(i, weight=1)

        for item in self.fin_tree.get_children():
            self.fin_tree.delete(item)
        for row in self.report_manager.get_financial_breakdown():
            self.fin_tree.insert("", "end", values=(
                row[0], f"£{row[1]:.2f}", f"£{row[2]:.2f}", f"£{row[3]:.2f}"))
        apply_row_stripes(self.fin_tree)
        autofit_columns(self.fin_tree)

    # ── Maintenance Costs ─────────────────────────────────────────────────────

    def _build_maintenance_tab(self, tab):
        scroll = ctk.CTkScrollableFrame(tab, fg_color=T.BG,
                                         scrollbar_button_color=T.SURFACE_3)
        scroll.pack(fill="both", expand=True)

        filter_inner = create_card(scroll)
        ctk.CTkLabel(filter_inner, text="City:", font=T.FONT_BODY,
                      text_color=T.TEXT_MUTED).pack(side="left", padx=(0, T.SP_S))
        cities = ["All"] + self.report_manager.get_cities()
        self.mnt_city_filter = ctk.CTkComboBox(
            filter_inner, values=cities, width=180, height=T.INPUT_HEIGHT,
            fg_color=T.SURFACE_3, border_color=T.BORDER,
            button_color=T.SURFACE_3, dropdown_fg_color=T.SURFACE,
            text_color=T.TEXT,
            command=lambda _: self.refresh_maintenance())
        self.mnt_city_filter.pack(side="left")
        self.mnt_city_filter.set("All")

        self.mnt_kpi_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        self.mnt_kpi_frame.pack(fill="x", padx=T.SP_XL, pady=(T.SP_S, 0))

        tbl_inner = create_card_fill(scroll, title="Maintenance Cost by Apartment")
        cols = ("Unit", "City", "Tickets", "Total Cost", "Total Hours")
        self.mnt_tree = setup_treeview_scroll(tbl_inner, columns=cols, height=12)
        self.refresh_maintenance()

    def refresh_maintenance(self):
        city = self.mnt_city_filter.get()

        for w in self.mnt_kpi_frame.winfo_children():
            w.destroy()
        summary = self.report_manager.get_maintenance_cost_summary()
        kpi_data = [
            ("Total Spend",  f"£{summary['total_cost']:.2f}",   "danger"),
            ("Avg Cost",     f"£{summary['avg_cost']:.2f}",     "warning"),
            ("Total Hours",  f"{summary['total_hours']:.1f}h",  "info"),
            ("Completed",    str(summary["completed_tickets"]), "success"),
        ]
        for i, (label, val, kind) in enumerate(kpi_data):
            tile = create_kpi_tile_l(self.mnt_kpi_frame, label=label,
                                      value=val, kind=kind)
            tile.grid(row=0, column=i, padx=T.SP_M, pady=T.SP_S, sticky="nsew")
            self.mnt_kpi_frame.grid_columnconfigure(i, weight=1)

        for item in self.mnt_tree.get_children():
            self.mnt_tree.delete(item)
        for row in self.report_manager.get_maintenance_cost_report(city):
            self.mnt_tree.insert("", "end", values=(
                row[0], row[1], row[2], f"£{row[3]:.2f}", f"{row[4]:.1f}h"))
        apply_row_stripes(self.mnt_tree)
        autofit_columns(self.mnt_tree)
