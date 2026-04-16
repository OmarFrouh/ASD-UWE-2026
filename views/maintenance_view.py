# Student Name: Numair
# Student ID: 24026758

import customtkinter as ctk
import tkinter as tk
from maintenance_manager import MaintenanceManager
from views import theme as T
from views.ui_helpers import (
    setup_treeview_scroll, autofit_columns, apply_row_stripes,
    enable_trackpad_scroll,
    create_page_header, create_card, create_card_fill, create_kpi_tile_l,
    create_primary_button, create_ghost_button, create_success_button,
    show_success, show_error, show_warning,
)


class MaintenanceView:
    def __init__(self, parent, db_manager):
        self.db_manager = db_manager
        self.manager    = MaintenanceManager(db_manager)
        self._root = parent.winfo_toplevel()

        frame = ctk.CTkFrame(parent, fg_color=T.BG)
        frame.pack(fill="both", expand=True)

        create_page_header(frame, "🔧 Maintenance",
                            subtitle="Manage tickets, staff, costs and tenant notifications")

        self.tabview = ctk.CTkTabview(frame,
                                       fg_color=T.SURFACE,
                                       segmented_button_fg_color=T.SURFACE_2,
                                       segmented_button_selected_color=T.PRIMARY,
                                       segmented_button_selected_hover_color=T.PRIMARY_HOVER,
                                       segmented_button_unselected_color=T.SURFACE_2,
                                       segmented_button_unselected_hover_color=T.SURFACE_3,
                                       text_color=T.TEXT)
        self.tabview.pack(fill="both", expand=True, padx=T.SP_XL, pady=(0, T.SP_XL))

        tab_new    = self.tabview.add("New Ticket")
        tab_list   = self.tabview.add("All Tickets")
        tab_manage = self.tabview.add("Manage")
        tab_costs  = self.tabview.add("Cost Report")

        self._build_new_tab(tab_new)
        self._build_list_tab(tab_list)
        self._build_manage_tab(tab_manage)
        self._build_cost_tab(tab_costs)

    # ── New Ticket ────────────────────────────────────────────────────────────

    def _build_new_tab(self, tab):
        scroll = ctk.CTkScrollableFrame(tab, fg_color=T.BG,
                                         scrollbar_button_color=T.SURFACE_3)
        scroll.pack(fill="both", expand=True)
        inner = create_card(scroll, title="Submit Ticket")
        inner.grid_columnconfigure(1, weight=1)

        def _lbl(text, row, req=False):
            ctk.CTkLabel(inner, text=text + (" *" if req else ""),
                          font=T.FONT_BODY,
                          text_color=T.DANGER if req else T.TEXT_MUTED).grid(
                row=row, column=0, padx=(0, T.SP_M), pady=T.SP_S, sticky="e")

        def _entry(row, placeholder=""):
            e = ctk.CTkEntry(inner, width=280, height=T.INPUT_HEIGHT,
                              fg_color=T.SURFACE_3, border_color=T.BORDER,
                              text_color=T.TEXT, placeholder_text=placeholder)
            e.grid(row=row, column=1, pady=T.SP_S, sticky="w")
            return e

        _lbl("Apartment ID", 0, True); self.apt_id_entry    = _entry(0)
        _lbl("Tenant ID",    1);       self.tenant_id_entry = _entry(1, "Optional")
        _lbl("Description",  2, True); self.desc_entry      = _entry(2)
        _lbl("Priority",     3, True)

        self.priority_combo = ctk.CTkComboBox(
            inner, values=["Low", "Medium", "High", "Urgent"],
            width=280, height=T.INPUT_HEIGHT,
            fg_color=T.SURFACE_3, border_color=T.BORDER,
            button_color=T.SURFACE_3, dropdown_fg_color=T.SURFACE,
            text_color=T.TEXT)
        self.priority_combo.grid(row=3, column=1, pady=T.SP_S, sticky="w")
        self.priority_combo.set("Medium")

        btn = create_primary_button(inner, "Submit Ticket",
                                     self.submit_ticket, width=280)
        btn.grid(row=4, column=0, columnspan=2, pady=T.SP_L)

        for e in [self.apt_id_entry, self.tenant_id_entry, self.desc_entry]:
            e.bind("<Return>", lambda ev: self.submit_ticket())

    # ── All Tickets ───────────────────────────────────────────────────────────

    def _build_list_tab(self, tab):
        frame = ctk.CTkFrame(tab, fg_color=T.BG)
        frame.pack(fill="both", expand=True)
        toolbar = ctk.CTkFrame(frame, fg_color="transparent")
        toolbar.pack(fill="x", padx=T.SP_L, pady=T.SP_S)
        create_ghost_button(toolbar, "⟳  Refresh", self.refresh_list).pack(side="right")

        cols = ("ID", "Unit", "Tenant", "Issue", "Priority", "Status",
                "Reported", "Scheduled", "Assigned To", "Hours", "Cost (£)")
        self.tree = setup_treeview_scroll(
            frame, columns=cols, height=15,
            status_columns=["Priority", "Status"])
        self.refresh_list()

    # ── Manage ────────────────────────────────────────────────────────────────

    def _build_manage_tab(self, tab):
        scroll = ctk.CTkScrollableFrame(tab, fg_color=T.BG,
                                         scrollbar_button_color=T.SURFACE_3)
        scroll.pack(fill="both", expand=True)

        # Ticket ID lookup row
        lookup_inner = create_card(scroll)
        ctk.CTkLabel(lookup_inner, text="Ticket ID *", font=T.FONT_BODY_B,
                      text_color=T.DANGER).pack(side="left", padx=(0, T.SP_M))
        self.manage_id = ctk.CTkEntry(lookup_inner, width=200, height=T.INPUT_HEIGHT,
                                       fg_color=T.SURFACE_3, border_color=T.BORDER,
                                       text_color=T.TEXT)
        self.manage_id.pack(side="left")

        # 3-column cards row
        cols_outer = ctk.CTkFrame(scroll, fg_color="transparent")
        cols_outer.pack(fill="x", padx=T.SP_XL, pady=T.SP_M)
        cols_outer.grid_columnconfigure((0, 1, 2), weight=1)

        # Assign card
        assign = ctk.CTkFrame(cols_outer, fg_color=T.SURFACE,
                               corner_radius=T.RADIUS_MD,
                               border_width=1, border_color=T.BORDER)
        assign.grid(row=0, column=0, padx=(0, T.SP_S), sticky="nsew")
        ctk.CTkLabel(assign, text="Assign Staff", font=T.FONT_H3,
                      text_color=T.PRIMARY).pack(
            anchor="w", padx=T.SP_L, pady=(T.SP_L, T.SP_S))
        tk.Frame(assign, bg=T.BORDER, height=1).pack(fill="x")
        a_inner = ctk.CTkFrame(assign, fg_color="transparent")
        a_inner.pack(padx=T.SP_L, pady=T.SP_L, fill="x")
        ctk.CTkLabel(a_inner, text="Staff User ID", font=T.FONT_BODY,
                      text_color=T.TEXT_MUTED).pack(anchor="w")
        self.staff_id_entry = ctk.CTkEntry(a_inner, width=180, height=T.INPUT_HEIGHT,
                                            fg_color=T.SURFACE_3, border_color=T.BORDER,
                                            text_color=T.TEXT)
        self.staff_id_entry.pack(pady=(T.SP_XS, T.SP_M), fill="x")
        ctk.CTkLabel(a_inner, text="Scheduled Date (YYYY-MM-DD)",
                      font=T.FONT_BODY, text_color=T.TEXT_MUTED).pack(anchor="w")
        self.sched_entry = ctk.CTkEntry(a_inner, width=180, height=T.INPUT_HEIGHT,
                                         fg_color=T.SURFACE_3, border_color=T.BORDER,
                                         text_color=T.TEXT,
                                         placeholder_text="optional")
        self.sched_entry.pack(pady=(T.SP_XS, T.SP_L), fill="x")
        create_primary_button(a_inner, "Assign", self.assign).pack(fill="x")

        # Status card
        status_card = ctk.CTkFrame(cols_outer, fg_color=T.SURFACE,
                                    corner_radius=T.RADIUS_MD,
                                    border_width=1, border_color=T.BORDER)
        status_card.grid(row=0, column=1, padx=T.SP_XS, sticky="nsew")
        ctk.CTkLabel(status_card, text="Update Status", font=T.FONT_H3,
                      text_color=T.PRIMARY).pack(
            anchor="w", padx=T.SP_L, pady=(T.SP_L, T.SP_S))
        tk.Frame(status_card, bg=T.BORDER, height=1).pack(fill="x")
        s_inner = ctk.CTkFrame(status_card, fg_color="transparent")
        s_inner.pack(padx=T.SP_L, pady=T.SP_L, fill="x")
        ctk.CTkLabel(s_inner, text="New Status", font=T.FONT_BODY,
                      text_color=T.TEXT_MUTED).pack(anchor="w")
        self.status_combo = ctk.CTkComboBox(
            s_inner, values=["Open", "Assigned", "In Progress", "Fixed", "Closed"],
            width=180, height=T.INPUT_HEIGHT,
            fg_color=T.SURFACE_3, border_color=T.BORDER,
            button_color=T.SURFACE_3, dropdown_fg_color=T.SURFACE,
            text_color=T.TEXT)
        self.status_combo.pack(pady=(T.SP_XS, T.SP_L), fill="x")
        self.status_combo.set("In Progress")
        create_primary_button(s_inner, "Update Status",
                               self.update_status).pack(fill="x")

        # Costs card
        costs_card = ctk.CTkFrame(cols_outer, fg_color=T.SURFACE,
                                   corner_radius=T.RADIUS_MD,
                                   border_width=1, border_color=T.BORDER)
        costs_card.grid(row=0, column=2, padx=(T.SP_S, 0), sticky="nsew")
        ctk.CTkLabel(costs_card, text="Log Costs", font=T.FONT_H3,
                      text_color=T.PRIMARY).pack(
            anchor="w", padx=T.SP_L, pady=(T.SP_L, T.SP_S))
        tk.Frame(costs_card, bg=T.BORDER, height=1).pack(fill="x")
        c_inner = ctk.CTkFrame(costs_card, fg_color="transparent")
        c_inner.pack(padx=T.SP_L, pady=T.SP_L, fill="x")
        ctk.CTkLabel(c_inner, text="Hours Spent", font=T.FONT_BODY,
                      text_color=T.TEXT_MUTED).pack(anchor="w")
        self.hours_entry = ctk.CTkEntry(c_inner, width=180, height=T.INPUT_HEIGHT,
                                         fg_color=T.SURFACE_3, border_color=T.BORDER,
                                         text_color=T.TEXT)
        self.hours_entry.pack(pady=(T.SP_XS, T.SP_M), fill="x")
        ctk.CTkLabel(c_inner, text="Cost (£)", font=T.FONT_BODY,
                      text_color=T.TEXT_MUTED).pack(anchor="w")
        self.cost_entry = ctk.CTkEntry(c_inner, width=180, height=T.INPUT_HEIGHT,
                                        fg_color=T.SURFACE_3, border_color=T.BORDER,
                                        text_color=T.TEXT)
        self.cost_entry.pack(pady=(T.SP_XS, T.SP_L), fill="x")
        create_primary_button(c_inner, "Log Costs", self.log_costs).pack(fill="x")

        # Notify Tenant card (full width)
        notify_inner = create_card(scroll, title="📧 Notify Tenant")
        notify_inner.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(notify_inner, text="Maintenance Date *", font=T.FONT_BODY,
                      text_color=T.DANGER).grid(row=0, column=0,
                                                 padx=(0, T.SP_M), pady=T.SP_S, sticky="e")
        self.notify_date_entry = ctk.CTkEntry(notify_inner, width=220,
                                               height=T.INPUT_HEIGHT,
                                               fg_color=T.SURFACE_3,
                                               border_color=T.BORDER,
                                               text_color=T.TEXT,
                                               placeholder_text="YYYY-MM-DD")
        self.notify_date_entry.grid(row=0, column=1, pady=T.SP_S, sticky="w")
        create_primary_button(notify_inner, "Set Date & Notify Tenant",
                               self.notify_tenant, width=260).grid(
            row=1, column=0, columnspan=2, pady=T.SP_L)

        self.manage_result = ctk.CTkLabel(scroll, text="", font=T.FONT_BODY,
                                           text_color=T.TEXT_MUTED)
        self.manage_result.pack(pady=T.SP_M)

        scroll.after(200, lambda: enable_trackpad_scroll(scroll))

        # Bindings
        self.manage_id.bind("<Return>",       lambda e: self.update_status())
        self.hours_entry.bind("<Return>",     lambda e: self.log_costs())
        self.cost_entry.bind("<Return>",      lambda e: self.log_costs())
        self.staff_id_entry.bind("<Return>",  lambda e: self.assign())
        self.sched_entry.bind("<Return>",     lambda e: self.assign())

    # ── Cost Report tab ───────────────────────────────────────────────────────

    def _build_cost_tab(self, tab):
        scroll = ctk.CTkScrollableFrame(tab, fg_color=T.BG,
                                         scrollbar_button_color=T.SURFACE_3)
        scroll.pack(fill="both", expand=True)

        # KPI tiles frame
        self.cost_kpi_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        self.cost_kpi_frame.pack(fill="x", padx=T.SP_XL, pady=(T.SP_S, 0))

        # Per-apartment table
        apt_inner = create_card_fill(scroll, title="Cost by Apartment")
        cols = ("Unit", "City", "Total Tickets", "Open", "Resolved",
                "Total Cost", "Total Hours", "Avg Cost")
        self.cost_apt_tree = setup_treeview_scroll(
            apt_inner, columns=cols, height=6, bind_scroll=False)
        for c in cols:
            self.cost_apt_tree.column(c, width=90)

        # Per-city table
        city_inner = create_card_fill(scroll, title="Cost by City")
        city_cols = ("City", "Total Tickets", "Total Cost", "Total Hours", "Avg Cost")
        self.cost_city_tree = setup_treeview_scroll(
            city_inner, columns=city_cols, height=5, bind_scroll=False)
        for c in city_cols:
            self.cost_city_tree.column(c, width=120)

        create_ghost_button(scroll, "⟳  Refresh Report",
                             self.refresh_cost_report).pack(pady=T.SP_M)
        self.refresh_cost_report()
        scroll.after(200, lambda: enable_trackpad_scroll(scroll))

    # ── Actions ───────────────────────────────────────────────────────────────

    def submit_ticket(self):
        apt_id = self.apt_id_entry.get()
        tid    = self.tenant_id_entry.get()
        desc   = self.desc_entry.get()
        priority = self.priority_combo.get()
        if not apt_id or not desc:
            show_warning(self._root, "Apartment ID and description are required.")
            return
        try:
            self.manager.create_ticket(int(apt_id), int(tid) if tid else None, desc, priority)
            show_success(self._root, "Ticket created successfully.")
            for e in [self.apt_id_entry, self.tenant_id_entry, self.desc_entry]:
                e.delete(0, "end")
            self.priority_combo.set("Medium")
            self.refresh_list()
        except Exception as ex:
            show_error(self._root, str(ex))

    def assign(self):
        tid = self.manage_id.get()
        sid = self.staff_id_entry.get()
        sched = self.sched_entry.get()
        if not tid or not sid:
            show_warning(self._root, "Ticket ID and Staff ID are required.")
            return
        try:
            self.manager.assign_staff(int(tid), int(sid), sched or None)
            self.manage_result.configure(text="✓ Staff assigned.", text_color=T.SUCCESS)
            self.refresh_list()
        except ValueError:
            show_error(self._root, "Ticket ID and Staff ID must be numbers.")
        except Exception as ex:
            show_error(self._root, str(ex))

    def update_status(self):
        tid = self.manage_id.get()
        if not tid:
            show_warning(self._root, "Enter a Ticket ID first.")
            return
        try:
            new_status = self.status_combo.get()
            self.manager.update_status(int(tid), new_status)
            self.manage_result.configure(
                text=f"✓ Ticket {tid} → {new_status}",
                text_color=T.SUCCESS)
            self.refresh_list()
        except ValueError:
            show_error(self._root, "Ticket ID must be a number.")
        except Exception as ex:
            show_error(self._root, str(ex))

    def log_costs(self):
        tid   = self.manage_id.get()
        hours = self.hours_entry.get()
        cost  = self.cost_entry.get()
        if not tid or not hours or not cost:
            show_warning(self._root, "All fields required.")
            return
        try:
            self.manager.log_costs(int(tid), hours, cost)
            self.manage_result.configure(
                text=f"✓ Costs logged: {hours}h, £{cost}",
                text_color=T.SUCCESS)
            self.hours_entry.delete(0, "end")
            self.cost_entry.delete(0, "end")
            self.refresh_list()
        except ValueError:
            show_error(self._root, "Ticket ID, Hours, and Cost must be numbers.")
        except Exception as ex:
            show_error(self._root, str(ex))

    def notify_tenant(self):
        tid  = self.manage_id.get()
        date = self.notify_date_entry.get()
        if not tid or not date:
            show_warning(self._root, "Ticket ID and date are required.")
            return
        try:
            result = self.manager.notify_tenant_scheduled_date(int(tid), date)
            self.manage_result.configure(
                text=f"✓ Date set and tenant notified: {result['scheduled_date']}",
                text_color=T.SUCCESS)
            self.refresh_list()
        except Exception as ex:
            show_error(self._root, str(ex))

    def refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for t in self.manager.get_all_tickets():
            self.tree.insert("", "end", values=(
                t[0], t[1] or "N/A", t[2] or "N/A",
                (t[3] or "")[:30], t[4], t[5], t[6],
                t[7] or "Not set", t[8] or "Unassigned",
                f"{t[9] or 0.0:.1f}", f"£{(t[10] or 0.0):.2f}"))
        apply_row_stripes(self.tree)
        autofit_columns(self.tree)

    def refresh_cost_report(self):
        for w in self.cost_kpi_frame.winfo_children():
            w.destroy()
        status_counts = self.manager.get_tickets_by_status_count()
        total = sum(status_counts.values())
        kpi_data = [("Total Tickets", str(total), "primary")]
        kind_map = {"Open": "info", "In Progress": "warning",
                    "Fixed": "success", "Closed": "muted"}
        for status, count in status_counts.items():
            kpi_data.append((status, str(count), kind_map.get(status, "neutral")))
        for i, (label, val, kind) in enumerate(kpi_data):
            tile = create_kpi_tile_l(self.cost_kpi_frame, label=label,
                                      value=val, kind=kind)
            tile.grid(row=0, column=i, padx=T.SP_M, pady=T.SP_S, sticky="nsew")
            self.cost_kpi_frame.grid_columnconfigure(i, weight=1)

        for item in self.cost_apt_tree.get_children():
            self.cost_apt_tree.delete(item)
        for row in self.manager.get_cost_report_by_apartment():
            self.cost_apt_tree.insert("", "end", values=(
                row[0], row[1], row[2], row[3], row[4],
                f"£{row[5]:.2f}", f"{row[6]:.1f}h", f"£{row[7]:.2f}"))
        apply_row_stripes(self.cost_apt_tree)
        autofit_columns(self.cost_apt_tree)

        for item in self.cost_city_tree.get_children():
            self.cost_city_tree.delete(item)
        for row in self.manager.get_cost_report_by_city():
            self.cost_city_tree.insert("", "end", values=(
                row[0], row[1], f"£{row[2]:.2f}", f"{row[3]:.1f}h", f"£{row[4]:.2f}"))
        apply_row_stripes(self.cost_city_tree)
        autofit_columns(self.cost_city_tree)
