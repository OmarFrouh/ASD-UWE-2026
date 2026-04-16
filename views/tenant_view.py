# Student Name: Feras Bader
# Student ID: 24033513

import customtkinter as ctk
import tkinter as tk
from tenant_manager import TenantManager
from views import theme as T
from views.ui_helpers import (
    setup_treeview_scroll, autofit_columns, apply_row_stripes,
    enable_trackpad_scroll,
    create_page_header, create_card, create_card_fill, create_tabview,
    create_primary_button, create_secondary_button,
    create_danger_button, create_warning_button, create_success_button,
    create_ghost_button,
    show_success, show_error, show_warning,
    confirm_dialog,
)


class TenantView:
    def __init__(self, parent, db_manager, role="front_desk"):
        self.db_manager     = db_manager
        self.role           = role
        self.tenant_manager = TenantManager(db_manager)
        self._root = parent.winfo_toplevel()

        self.frame = ctk.CTkFrame(parent, fg_color=T.BG)
        self.frame.pack(fill="both", expand=True)

        create_page_header(self.frame, "👤 Tenants",
                            subtitle="Register, manage, and archive tenants")

        self.tabview = create_tabview(self.frame)

        self.tab_list      = self.tabview.add("Active Tenants")
        self.tab_archived  = self.tabview.add("Archived / Terminated")
        self.tab_register  = self.tabview.add("Register")
        self.tab_edit      = self.tabview.add("Edit Tenant")
        self.tab_complaints = self.tabview.add("Complaints")
        self.tab_actions   = self.tabview.add("Actions")
        if self.role == "admin":
            self.tab_assign = self.tabview.add("Assign Apartment")

        self._build_list_tab()
        self._build_archived_tab()
        self._build_register_tab()
        self._build_edit_tab()
        self._build_complaints_tab()
        self._build_actions_tab()
        if self.role == "admin":
            self._build_assign_tab()

    # ── Active Tenants ────────────────────────────────────────────────────────

    def _build_list_tab(self):
        frame = ctk.CTkFrame(self.tab_list, fg_color=T.BG)
        frame.pack(fill="both", expand=True)

        toolbar = ctk.CTkFrame(frame, fg_color="transparent")
        toolbar.pack(fill="x", padx=T.SP_L, pady=T.SP_S)

        # Search
        ctk.CTkLabel(toolbar, text="🔍", font=T.FONT_BODY,
                      text_color=T.TEXT_MUTED).pack(side="left", padx=(0, T.SP_XS))
        self.search_entry = ctk.CTkEntry(
            toolbar, placeholder_text="Name, NI, email, phone…",
            width=200, height=T.INPUT_HEIGHT,
            fg_color=T.SURFACE_3, border_color=T.BORDER, text_color=T.TEXT)
        self.search_entry.pack(side="left", padx=(0, T.SP_M))
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh_list())

        # Status filter
        ctk.CTkLabel(toolbar, text="Status:", font=T.FONT_BODY,
                      text_color=T.TEXT_MUTED).pack(side="left", padx=(0, T.SP_XS))
        self.status_filter = ctk.CTkComboBox(
            toolbar,
            values=["Active", "Archived", "Terminated", "All"],
            width=150, height=T.INPUT_HEIGHT,
            fg_color=T.SURFACE_3, border_color=T.BORDER,
            button_color=T.SURFACE_3, dropdown_fg_color=T.SURFACE,
            text_color=T.TEXT,
            command=lambda _: self.refresh_list())
        self.status_filter.pack(side="left", padx=(0, T.SP_M))
        self.status_filter.set("Active")

        create_ghost_button(toolbar, "⟳  Reset",
                             self.reset_filters, width=90).pack(side="left")
        create_ghost_button(toolbar, "⟳  Refresh",
                             self.refresh_list).pack(side="right")

        # Summary strip
        self.summary_frame = ctk.CTkFrame(frame, fg_color=T.SURFACE_2,
                                           corner_radius=0)
        self.summary_frame.pack(fill="x")

        cols = ("ID", "NI", "Name", "Phone", "Email", "Occupation",
                "Apt", "Start Date", "End Date", "Rent", "Status")
        self.tree = setup_treeview_scroll(
            frame, columns=cols, height=15,
            status_columns=["Status"],
            empty_message="No tenants match the current filter",
        )
        self.refresh_list()

        self._root.bind("<Control-f>",
                        lambda e: self.search_entry.focus_set())

    # ── Archived / Terminated ─────────────────────────────────────────────────

    def _build_archived_tab(self):
        frame = ctk.CTkFrame(self.tab_archived, fg_color=T.BG)
        frame.pack(fill="both", expand=True)
        toolbar = ctk.CTkFrame(frame, fg_color="transparent")
        toolbar.pack(fill="x", padx=T.SP_L, pady=T.SP_S)
        create_ghost_button(toolbar, "⟳  Refresh", self.refresh_archived).pack(side="right")

        cols = ("ID", "NI", "Name", "Status")
        self.archived_tree = setup_treeview_scroll(
            frame, columns=cols, height=15,
            status_columns=["Status"],
            empty_message="No archived or terminated tenants",
        )
        self.refresh_archived()

    # ── Register ──────────────────────────────────────────────────────────────

    def _build_register_tab(self):
        scroll = ctk.CTkScrollableFrame(self.tab_register, fg_color=T.BG,
                                         scrollbar_button_color=T.SURFACE_3)
        scroll.pack(fill="both", expand=True)

        inner = create_card(scroll, title="Tenant Details")
        inner.grid_columnconfigure(0, minsize=160)
        inner.grid_columnconfigure(1, weight=1)

        def _grid_section(label, grid_row):
            """Grid-compatible section header — spans both columns."""
            ctk.CTkLabel(inner, text=label, font=T.FONT_CAPTION_B,
                          text_color=T.TEXT_SUBTLE).grid(
                row=grid_row, column=0, columnspan=2,
                padx=T.SP_M, pady=(T.SP_L, T.SP_XS), sticky="w")
            tk.Frame(inner, bg=T.BORDER, height=1).grid(
                row=grid_row + 1, column=0, columnspan=2,
                sticky="ew", padx=T.SP_M, pady=(0, T.SP_XS))

        required_keys = {"ni", "name", "username", "password"}
        fields = [
            ("NI Number",         "ni"),
            ("Full Name",         "name"),
            ("Phone",             "phone"),
            ("Email",             "email"),
            ("Occupation",        "occupation"),
            ("References",        "refs"),
            ("Emergency Contact", "emergency"),
            ("Apt. Requirements", "apt_req"),
        ]

        self.entries = {}
        row = 0

        _grid_section("Personal Information", row); row += 2

        for label, key in fields:
            req = key in required_keys
            ctk.CTkLabel(inner, text=label + (" *" if req else ""),
                          font=T.FONT_BODY, anchor="e",
                          text_color=T.DANGER if req else T.TEXT_MUTED).grid(
                row=row, column=0, padx=(T.SP_M, T.SP_S), pady=T.SP_S, sticky="e")
            e = ctk.CTkEntry(inner, height=T.INPUT_HEIGHT,
                              fg_color=T.SURFACE_3, border_color=T.BORDER,
                              text_color=T.TEXT)
            e.grid(row=row, column=1, pady=T.SP_S, padx=(0, T.SP_M), sticky="ew")
            self.entries[key] = e
            row += 1

        _grid_section("Account", row); row += 2

        for label, key in [("Username (login)", "username"), ("Password", "password")]:
            ctk.CTkLabel(inner, text=label + " *", font=T.FONT_BODY,
                          text_color=T.DANGER, anchor="e").grid(
                row=row, column=0, padx=(T.SP_M, T.SP_S), pady=T.SP_S, sticky="e")
            show = "\u2022" if key == "password" else ""
            e = ctk.CTkEntry(inner, height=T.INPUT_HEIGHT,
                              fg_color=T.SURFACE_3, border_color=T.BORDER,
                              text_color=T.TEXT, show=show)
            e.grid(row=row, column=1, pady=T.SP_S, padx=(0, T.SP_M), sticky="ew")
            self.entries[key] = e
            row += 1

        btn = create_primary_button(inner, "Register Tenant", self.register_tenant)
        btn.grid(row=row, column=0, columnspan=2, pady=T.SP_L, padx=T.SP_M, sticky="ew")

        scroll.after(200, lambda: enable_trackpad_scroll(scroll))


    # ── Edit Tenant ───────────────────────────────────────────────────────────

    def _build_edit_tab(self):
        scroll = ctk.CTkScrollableFrame(self.tab_edit, fg_color=T.BG,
                                         scrollbar_button_color=T.SURFACE_3)
        scroll.pack(fill="both", expand=True)

        # Lookup
        lookup_inner = create_card(scroll)
        ctk.CTkLabel(lookup_inner, text="Tenant ID *", font=T.FONT_BODY_B,
                      text_color=T.DANGER).pack(side="left", padx=(0, T.SP_M))
        self.edit_id_entry = ctk.CTkEntry(lookup_inner, width=160, height=T.INPUT_HEIGHT,
                                           fg_color=T.SURFACE_3, border_color=T.BORDER,
                                           text_color=T.TEXT)
        self.edit_id_entry.pack(side="left", padx=(0, T.SP_M))
        create_secondary_button(lookup_inner, "Load Tenant",
                                 self.load_tenant_for_edit, width=120).pack(side="left")

        # NI display
        ni_inner = create_card(scroll)
        ctk.CTkLabel(ni_inner, text="NI Number  (read-only):", font=T.FONT_BODY,
                      text_color=T.TEXT_SUBTLE).pack(side="left", padx=(0, T.SP_M))
        self.edit_ni_label = ctk.CTkLabel(ni_inner, text="—",
                                           font=T.FONT_BODY_B, text_color=T.TEXT)
        self.edit_ni_label.pack(side="left")

        # Editable fields
        edit_inner = create_card(scroll, title="Editable Fields")
        edit_inner.grid_columnconfigure(0, minsize=160)
        edit_inner.grid_columnconfigure(1, weight=1)
        edit_fields = [
            ("Full Name",              "edit_name"),
            ("Phone",                  "edit_phone"),
            ("Email",                  "edit_email"),
            ("Occupation",             "edit_occupation"),
            ("References",             "edit_refs"),
            ("Emergency Contact",      "edit_emergency"),
            ("Apt. Requirements",      "edit_apt_req"),
        ]
        self.edit_entries = {}
        for i, (label, key) in enumerate(edit_fields):
            ctk.CTkLabel(edit_inner, text=label, font=T.FONT_BODY,
                          text_color=T.TEXT_MUTED, anchor="e").grid(
                row=i, column=0, padx=(T.SP_M, T.SP_S), pady=T.SP_S, sticky="e")
            e = ctk.CTkEntry(edit_inner, height=T.INPUT_HEIGHT,
                              fg_color=T.SURFACE_3, border_color=T.BORDER,
                              text_color=T.TEXT)
            e.grid(row=i, column=1, pady=T.SP_S, padx=(0, T.SP_M), sticky="ew")
            self.edit_entries[key] = e

        # Lease info
        lease_inner = create_card(scroll)
        ctk.CTkLabel(lease_inner, text="Lease info (read-only):", font=T.FONT_BODY,
                      text_color=T.TEXT_SUBTLE).pack(side="left", padx=(0, T.SP_M))
        self.edit_lease_label = ctk.CTkLabel(lease_inner,
                                              text="Load a tenant to see lease details",
                                              font=T.FONT_CAPTION, text_color=T.TEXT_SUBTLE)
        self.edit_lease_label.pack(side="left")

        # Save + result
        save_inner = create_card(scroll)
        create_success_button(save_inner, "Save Changes",
                               self.save_tenant_edit, width=280).pack(side="left")
        self.edit_result = ctk.CTkLabel(save_inner, text="", font=T.FONT_BODY,
                                         text_color=T.TEXT_MUTED)
        self.edit_result.pack(side="left", padx=T.SP_L)

        scroll.after(200, lambda: enable_trackpad_scroll(scroll))

    # ── Complaints ────────────────────────────────────────────────────────────

    def _build_complaints_tab(self):
        frame = ctk.CTkFrame(self.tab_complaints, fg_color=T.BG)
        frame.pack(fill="both", expand=True)

        # Log complaint card
        log_inner = create_card(frame, title="Log New Complaint")
        log_inner.grid_columnconfigure(1, weight=1)

        log_inner.grid_columnconfigure(0, minsize=120)
        log_inner.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(log_inner, text="Tenant ID *", font=T.FONT_BODY,
                      text_color=T.DANGER, anchor="e").grid(
            row=0, column=0, padx=(T.SP_M, T.SP_S), pady=T.SP_S, sticky="e")
        self.complaint_tid_entry = ctk.CTkEntry(log_inner, height=T.INPUT_HEIGHT,
                                                 fg_color=T.SURFACE_3,
                                                 border_color=T.BORDER,
                                                 text_color=T.TEXT)
        self.complaint_tid_entry.grid(row=0, column=1, pady=T.SP_S,
                                      padx=(0, T.SP_M), sticky="ew")

        ctk.CTkLabel(log_inner, text="Subject *", font=T.FONT_BODY,
                      text_color=T.DANGER, anchor="e").grid(
            row=1, column=0, padx=(T.SP_M, T.SP_S), pady=T.SP_S, sticky="e")
        self.complaint_subject_entry = ctk.CTkEntry(log_inner, height=T.INPUT_HEIGHT,
                                                     fg_color=T.SURFACE_3,
                                                     border_color=T.BORDER,
                                                     text_color=T.TEXT)
        self.complaint_subject_entry.grid(row=1, column=1, pady=T.SP_S,
                                          padx=(0, T.SP_M), sticky="ew")

        ctk.CTkLabel(log_inner, text="Description *", font=T.FONT_BODY,
                      text_color=T.DANGER, anchor="e").grid(
            row=2, column=0, padx=(T.SP_M, T.SP_S), pady=T.SP_S, sticky="e")
        self.complaint_desc_entry = ctk.CTkEntry(log_inner, height=T.INPUT_HEIGHT,
                                                  fg_color=T.SURFACE_3,
                                                  border_color=T.BORDER,
                                                  text_color=T.TEXT,
                                                  placeholder_text="Describe the complaint…")
        self.complaint_desc_entry.grid(row=2, column=1, pady=T.SP_S,
                                       padx=(0, T.SP_M), sticky="ew")

        btn = create_primary_button(log_inner, "Log Complaint", self.do_log_complaint)
        btn.grid(row=3, column=0, columnspan=2, pady=T.SP_L, padx=T.SP_M, sticky="ew")

        # Table + action toolbar
        tbl_inner = create_card_fill(frame, title="All Complaints")
        toolbar = ctk.CTkFrame(tbl_inner, fg_color="transparent")
        toolbar.pack(fill="x", pady=(0, T.SP_S))
        create_success_button(toolbar, "✓  Resolve Selected",
                               self.do_resolve_complaint, width=160).pack(side="left")
        create_ghost_button(toolbar, "⟳  Refresh",
                             self.refresh_complaints).pack(side="right")

        cols = ("ID", "Tenant", "Subject", "Date", "Status", "Description")
        self.complaints_tree = setup_treeview_scroll(
            tbl_inner, columns=cols, height=10,
            status_columns=["Status"],
            empty_message="No complaints logged yet",
        )
        self.refresh_complaints()

    # ── Actions ───────────────────────────────────────────────────────────────

    def _build_actions_tab(self):
        frame = ctk.CTkScrollableFrame(self.tab_actions, fg_color=T.BG,
                                        scrollbar_button_color=T.SURFACE_3)
        frame.pack(fill="both", expand=True)

        # Two cards side-by-side
        row_frame = ctk.CTkFrame(frame, fg_color="transparent")
        row_frame.pack(fill="x", padx=T.SP_XL, pady=T.SP_L)
        row_frame.grid_columnconfigure((0, 1), weight=1)

        # Early termination card
        term_card = ctk.CTkFrame(row_frame, fg_color=T.WARNING_MUTED,
                                  corner_radius=T.RADIUS_MD,
                                  border_width=1, border_color=T.WARNING)
        term_card.grid(row=0, column=0, padx=(0, T.SP_M), sticky="nsew")
        ctk.CTkLabel(term_card, text="⚠️  End Lease Early", font=T.FONT_H3,
                      text_color=T.WARNING).pack(
            anchor="w", padx=T.SP_L, pady=(T.SP_L, T.SP_XS))
        ctk.CTkLabel(term_card,
                      text="A 5% penalty + 1-month notice period applies.",
                      font=T.FONT_CAPTION, text_color=T.TEXT_MUTED).pack(
            anchor="w", padx=T.SP_L, pady=(0, T.SP_S))
        tk.Frame(term_card, bg=T.WARNING, height=1).pack(fill="x")

        t_inner = ctk.CTkFrame(term_card, fg_color="transparent")
        t_inner.pack(padx=T.SP_L, pady=T.SP_L, fill="x")
        ctk.CTkLabel(t_inner, text="Tenant ID *", font=T.FONT_BODY,
                      text_color=T.DANGER).pack(anchor="w")
        self.action_id_entry = ctk.CTkEntry(t_inner, width=200, height=T.INPUT_HEIGHT,
                                             fg_color=T.SURFACE_3, border_color=T.BORDER,
                                             text_color=T.TEXT)
        self.action_id_entry.pack(pady=(T.SP_XS, T.SP_L), fill="x")
        create_warning_button(t_inner, "End Lease Early",
                               self.do_early_termination).pack(fill="x")

        # Archive card (admin/manager only)
        if self.role in ("admin", "manager"):
            arch_card = ctk.CTkFrame(row_frame, fg_color=T.DANGER_MUTED,
                                      corner_radius=T.RADIUS_MD,
                                      border_width=1, border_color=T.DANGER)
            arch_card.grid(row=0, column=1, padx=(T.SP_M, 0), sticky="nsew")
            ctk.CTkLabel(arch_card, text="🗃  Archive Tenant", font=T.FONT_H3,
                          text_color=T.DANGER).pack(
                anchor="w", padx=T.SP_L, pady=(T.SP_L, T.SP_XS))
            ctk.CTkLabel(arch_card,
                          text="Admin / Manager only. This cannot be undone.",
                          font=T.FONT_CAPTION, text_color=T.TEXT_MUTED).pack(
                anchor="w", padx=T.SP_L, pady=(0, T.SP_S))
            tk.Frame(arch_card, bg=T.DANGER, height=1).pack(fill="x")

            a_inner = ctk.CTkFrame(arch_card, fg_color="transparent")
            a_inner.pack(padx=T.SP_L, pady=T.SP_L, fill="x")
            ctk.CTkLabel(a_inner, text="Tenant ID *", font=T.FONT_BODY,
                          text_color=T.DANGER).pack(anchor="w")
            self.archive_id_entry = ctk.CTkEntry(a_inner, width=200,
                                                  height=T.INPUT_HEIGHT,
                                                  fg_color=T.SURFACE_3,
                                                  border_color=T.BORDER,
                                                  text_color=T.TEXT)
            self.archive_id_entry.pack(pady=(T.SP_XS, T.SP_L), fill="x")
            create_danger_button(a_inner, "Archive Tenant",
                                  self.do_archive).pack(fill="x")

        self.action_result = ctk.CTkLabel(frame, text="", font=T.FONT_BODY,
                                           text_color=T.TEXT_MUTED)
        self.action_result.pack(pady=T.SP_M)

    # ── Assign Apartment ──────────────────────────────────────────────────────

    def _build_assign_tab(self):
        scroll = ctk.CTkScrollableFrame(self.tab_assign, fg_color=T.BG,
                                         scrollbar_button_color=T.SURFACE_3)
        scroll.pack(fill="both", expand=True)

        inner = create_card(scroll, title="Assign Apartment to Tenant")
        inner.grid_columnconfigure(0, minsize=180)
        inner.grid_columnconfigure(1, weight=1)

        fields = [
            ("Tenant User ID",           "t_id"),
            ("Apartment ID",             "apt_id"),
            ("Lease Start (YYYY-MM-DD)", "start"),
            ("Lease End (YYYY-MM-DD)",   "end"),
            ("Monthly Rent (£)",         "rent"),
            ("Deposit (£)",              "deposit"),
        ]
        self.assign_entries = {}
        for i, (label, key) in enumerate(fields):
            ctk.CTkLabel(inner, text=label + " *", font=T.FONT_BODY,
                          text_color=T.DANGER, anchor="e").grid(
                row=i, column=0, padx=(T.SP_M, T.SP_S), pady=T.SP_S, sticky="e")
            e = ctk.CTkEntry(inner, height=T.INPUT_HEIGHT,
                              fg_color=T.SURFACE_3, border_color=T.BORDER,
                              text_color=T.TEXT)
            e.grid(row=i, column=1, pady=T.SP_S, padx=(0, T.SP_M), sticky="ew")
            self.assign_entries[key] = e

        self.assign_result = ctk.CTkLabel(inner, text="", font=T.FONT_BODY,
                                           text_color=T.TEXT_MUTED)
        self.assign_result.grid(row=len(fields), column=0, columnspan=2, pady=T.SP_S)

        btn = create_primary_button(inner, "Assign Apartment", self.do_assign)
        btn.grid(row=len(fields) + 1, column=0, columnspan=2,
                  pady=T.SP_L, padx=T.SP_M, sticky="ew")

        scroll.after(200, lambda: enable_trackpad_scroll(scroll))

    # ── Data Actions ──────────────────────────────────────────────────────────

    def register_tenant(self):
        v = {k: e.get() for k, e in self.entries.items()}
        if not all([v["ni"], v["name"], v["username"], v["password"]]):
            show_warning(self._root,
                         "NI Number, Full Name, Username, and Password are required.")
            return
        try:
            self.tenant_manager.register_tenant(
                v["username"], v["password"], v["ni"], v["name"],
                v["phone"], v["email"], v["occupation"], v["refs"],
                v["emergency"], v["apt_req"])
            show_success(self._root, f"Tenant '{v['name']}' registered.")
            for e in self.entries.values():
                e.delete(0, "end")
            self.refresh_list()
        except Exception as ex:
            show_error(self._root, str(ex))

    def load_tenant_for_edit(self):
        tid = self.edit_id_entry.get()
        if not tid:
            show_warning(self._root, "Enter a Tenant ID.")
            return
        try:
            tid_int = int(tid)
        except ValueError:
            show_error(self._root, "Tenant ID must be a number.")
            return

        tenant = self.tenant_manager.get_tenant_by_id(tid_int)
        if not tenant:
            show_error(self._root, f"No tenant found with ID {tid_int}.")
            return
        if tenant[14] in ("Terminated", "Archived"):
            show_error(self._root, f"Tenant is {tenant[14]} — cannot edit.")
            return

        self.edit_ni_label.configure(text=tenant[1] or "N/A")
        field_map = {
            "edit_name":       tenant[2] or "",
            "edit_phone":      tenant[3] or "",
            "edit_email":      tenant[4] or "",
            "edit_occupation": tenant[5] or "",
            "edit_refs":       tenant[6] or "",
            "edit_emergency":  tenant[7] or "",
            "edit_apt_req":    tenant[8] or "",
        }
        for key, val in field_map.items():
            self.edit_entries[key].delete(0, "end")
            self.edit_entries[key].insert(0, val)

        apt_id    = tenant[9]
        lease_start = tenant[10] or "N/A"
        lease_end   = tenant[11] or "N/A"
        rent    = f"£{tenant[12]:.2f}" if tenant[12] else "N/A"
        deposit = f"£{tenant[13]:.2f}" if tenant[13] else "N/A"
        self.edit_lease_label.configure(
            text=f"Apt: {apt_id or 'None'}  |  {lease_start} → {lease_end}"
                 f"  |  Rent: {rent}  |  Deposit: {deposit}",
            text_color=T.TEXT)
        self.edit_result.configure(text=f"Loaded: {tenant[2]}", text_color=T.INFO)

    def save_tenant_edit(self):
        tid = self.edit_id_entry.get()
        if not tid:
            show_warning(self._root, "Load a tenant first.")
            return
        try:
            self.tenant_manager.update_tenant(
                int(tid),
                full_name=self.edit_entries["edit_name"].get() or None,
                phone=self.edit_entries["edit_phone"].get() or None,
                email=self.edit_entries["edit_email"].get() or None,
                occupation=self.edit_entries["edit_occupation"].get() or None,
                references=self.edit_entries["edit_refs"].get() or None,
                emergency_contact=self.edit_entries["edit_emergency"].get() or None,
                apt_requirements=self.edit_entries["edit_apt_req"].get() or None,
            )
            self.edit_result.configure(text="✓ Changes saved.", text_color=T.SUCCESS)
            self.refresh_list()
        except Exception as ex:
            show_error(self._root, str(ex))

    def do_log_complaint(self):
        tid     = self.complaint_tid_entry.get()
        subject = self.complaint_subject_entry.get()
        desc    = self.complaint_desc_entry.get()
        if not tid:
            show_warning(self._root, "Tenant ID is required.")
            return
        try:
            self.tenant_manager.log_complaint(int(tid), subject, desc)
            show_success(self._root, "Complaint logged.")
            self.complaint_tid_entry.delete(0, "end")
            self.complaint_subject_entry.delete(0, "end")
            self.complaint_desc_entry.delete(0, "end")
            self.refresh_complaints()
        except ValueError:
            show_error(self._root, "Tenant ID must be a number.")
        except Exception as ex:
            show_error(self._root, str(ex))

    def do_resolve_complaint(self):
        selected = self.complaints_tree.selection()
        if not selected:
            show_warning(self._root, "Select a complaint from the table first.")
            return
        complaint_id = self.complaints_tree.item(selected[0])["values"][0]
        if not confirm_dialog(self._root, "Resolve Complaint",
                               f"Resolve complaint #{complaint_id}?"):
            return
        try:
            self.tenant_manager.resolve_complaint(int(complaint_id))
            show_success(self._root, f"Complaint #{complaint_id} resolved.")
            self.refresh_complaints()
        except Exception as ex:
            show_error(self._root, str(ex))

    def do_early_termination(self):
        tid = self.action_id_entry.get()
        if not tid:
            show_warning(self._root, "Enter a Tenant ID.")
            return
        try:
            tid_int = int(tid)
        except ValueError:
            show_error(self._root, "Tenant ID must be a number.")
            return

        tenant = self.db_manager.fetch_one(
            "SELECT full_name, status, monthly_rent FROM tenants WHERE user_id=?",
            (tid_int,))
        if not tenant:
            show_error(self._root, f"No tenant found with ID {tid_int}.")
            return
        if tenant[1] in ("Terminated", "Archived"):
            show_error(self._root, f"Tenant '{tenant[0]}' is already {tenant[1]}.")
            return

        penalty = tenant[2] * 0.05 if tenant[2] else 0
        if not confirm_dialog(
                self._root,
                "Confirm Early Termination",
                f"Terminate lease for '{tenant[0]}'?\n\n"
                f"• 1-month notice period applies\n"
                f"• 5% penalty: £{penalty:.2f}",
                danger=True):
            return

        try:
            result = self.tenant_manager.early_termination(tid_int)
            name = tenant[0]
            eff = result['effective_date']
            pen = result['penalty']
            self.action_result.configure(
                text=f"✓ Terminated: {name}. Notice ends {eff}. Penalty: £{pen:.2f}",
                text_color=T.SUCCESS)
            self.refresh_list()
        except Exception as ex:
            show_error(self._root, str(ex))

    def do_archive(self):
        tid = getattr(self, "archive_id_entry", self.action_id_entry).get()
        if not tid:
            show_warning(self._root, "Enter a Tenant ID.")
            return
        try:
            tid_int = int(tid)
        except ValueError:
            show_error(self._root, "Tenant ID must be a number.")
            return

        tenant = self.db_manager.fetch_one(
            "SELECT full_name, status FROM tenants WHERE user_id=?", (tid_int,))
        if not tenant:
            show_error(self._root, f"No tenant found with ID {tid_int}.")
            return
        if tenant[1] == "Archived":
            show_error(self._root, f"'{tenant[0]}' is already archived.")
            return

        if not confirm_dialog(self._root, "Archive Tenant",
                               f"Permanently archive '{tenant[0]}'?\nThis cannot be undone.",
                               danger=True):
            return
        try:
            self.tenant_manager.archive_tenant(tid_int)
            self.action_result.configure(
                text=f"✓ '{tenant[0]}' archived.", text_color=T.SUCCESS)
            self.refresh_list()
        except Exception as ex:
            show_error(self._root, str(ex))

    def do_assign(self):
        try:
            t_id   = self.assign_entries["t_id"].get()
            apt_id = self.assign_entries["apt_id"].get()
            start  = self.assign_entries["start"].get()
            end    = self.assign_entries["end"].get()
            rent   = self.assign_entries["rent"].get()
            dep    = self.assign_entries["deposit"].get()
            if not all([t_id, apt_id, start, end, rent, dep]):
                raise Exception("All fields are required.")
            self.tenant_manager.assign_apartment(
                int(t_id), int(apt_id), start, end, float(rent), float(dep))
            self.assign_result.configure(text="✓ Apartment assigned.",
                                          text_color=T.SUCCESS)
            for e in self.assign_entries.values():
                e.delete(0, "end")
            self.refresh_list()
        except ValueError:
            show_error(self._root, "Enter valid numbers for IDs, rent, and deposit.")
        except Exception as ex:
            show_error(self._root, str(ex))

    # ── Refresh helpers ───────────────────────────────────────────────────────

    def reset_filters(self):
        self.search_entry.delete(0, "end")
        self.status_filter.set("Active")
        self.refresh_list()

    def refresh_list(self):
        search_query = self.search_entry.get().strip() if hasattr(self, "search_entry") else ""
        status = self.status_filter.get() if hasattr(self, "status_filter") else "Active"

        tenants = (self.tenant_manager.search_tenants(search_query) if search_query
                   else self.tenant_manager.filter_tenants_by_status(status))

        # Summary strip
        if hasattr(self, "summary_frame"):
            for w in self.summary_frame.winfo_children():
                w.destroy()
            counts = self.tenant_manager.get_tenant_count_by_status()
            color_map = {"Active": T.SUCCESS, "Archived": T.TEXT_MUTED,
                         "Terminated": T.DANGER}
            for st, count in counts.items():
                ctk.CTkLabel(self.summary_frame,
                              text=f"{st}: {count}",
                              font=T.FONT_CAPTION_B,
                              text_color=color_map.get(st, T.TEXT_MUTED)).pack(
                    side="left", padx=T.SP_L, pady=T.SP_S)

        for item in self.tree.get_children():
            self.tree.delete(item)
        for t in tenants:
            self.tree.insert("", "end", values=(
                t[0], t[1], t[2], t[3], t[4], t[5] or "N/A",
                t[11] or "N/A", t[7] or "N/A", t[8] or "N/A",
                f"£{t[9] or 0:.2f}", t[10]))
        apply_row_stripes(self.tree)
        autofit_columns(self.tree)
        if hasattr(self, "archived_tree"):
            self.refresh_archived()

    def refresh_archived(self):
        for item in self.archived_tree.get_children():
            self.archived_tree.delete(item)
        for t in self.tenant_manager.get_archived_tenants():
            self.archived_tree.insert("", "end", values=(t[0], t[1], t[2], t[3]))
        apply_row_stripes(self.archived_tree)
        autofit_columns(self.archived_tree)

    def refresh_complaints(self):
        for item in self.complaints_tree.get_children():
            self.complaints_tree.delete(item)
        for c in self.tenant_manager.get_all_complaints():
            self.complaints_tree.insert("", "end", values=(
                c[0], c[1], c[2], c[3], c[4], c[5] or ""))
        apply_row_stripes(self.complaints_tree)
        autofit_columns(self.complaints_tree)
