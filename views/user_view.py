# Student Name: Omar Alfrouh
# Student ID: 24020879

import customtkinter as ctk
from views import theme as T
from views.ui_helpers import (
    setup_treeview_scroll, autofit_columns, apply_row_stripes,
    enable_trackpad_scroll, create_page_header, create_card, create_card_fill,
    create_primary_button, create_secondary_button, create_ghost_button,
    show_success, show_error, show_warning,
)


class UserView:
    def __init__(self, parent_frame, auth_manager):
        self.parent = parent_frame
        self.auth_manager = auth_manager
        self._root = parent_frame.winfo_toplevel()

        scroll = ctk.CTkScrollableFrame(parent_frame, fg_color=T.BG,
                                         scrollbar_button_color=T.SURFACE_3)
        scroll.pack(fill="both", expand=True)

        create_page_header(scroll, "👥 Users",
                            subtitle="Manage staff and admin accounts")

        # ── Add User card ──
        form_inner = create_card(scroll, title="Add User")
        form_inner.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(form_inner, text="Username *", font=T.FONT_BODY,
                      text_color=T.DANGER).grid(row=0, column=0, padx=(0, T.SP_M),
                                                 pady=T.SP_S, sticky="e")
        self.username_entry = ctk.CTkEntry(form_inner, width=280,
                                            height=T.INPUT_HEIGHT,
                                            fg_color=T.SURFACE_3,
                                            border_color=T.BORDER,
                                            text_color=T.TEXT)
        self.username_entry.grid(row=0, column=1, pady=T.SP_S, sticky="w")

        ctk.CTkLabel(form_inner, text="Password *", font=T.FONT_BODY,
                      text_color=T.DANGER).grid(row=1, column=0, padx=(0, T.SP_M),
                                                 pady=T.SP_S, sticky="e")
        self.password_entry = ctk.CTkEntry(form_inner, show="•", width=280,
                                            height=T.INPUT_HEIGHT,
                                            fg_color=T.SURFACE_3,
                                            border_color=T.BORDER,
                                            text_color=T.TEXT)
        self.password_entry.grid(row=1, column=1, pady=T.SP_S, sticky="w")

        ctk.CTkLabel(form_inner, text="Role *", font=T.FONT_BODY,
                      text_color=T.DANGER).grid(row=2, column=0, padx=(0, T.SP_M),
                                                  pady=T.SP_S, sticky="e")
        self.role_combo = ctk.CTkComboBox(
            form_inner,
            values=["front_desk", "finance_manager", "maintenance", "manager", "admin"],
            width=280, height=T.INPUT_HEIGHT,
            fg_color=T.SURFACE_3, border_color=T.BORDER,
            button_color=T.SURFACE_3, dropdown_fg_color=T.SURFACE,
            text_color=T.TEXT,
            command=self.toggle_staff_fields
        )
        self.role_combo.grid(row=2, column=1, pady=T.SP_S, sticky="w")
        self.role_combo.set("front_desk")

        self.lbl_empid  = ctk.CTkLabel(form_inner, text="Employee ID *",
                                        font=T.FONT_BODY, text_color=T.DANGER)
        self.entry_empid = ctk.CTkEntry(form_inner, width=280,
                                         height=T.INPUT_HEIGHT,
                                         fg_color=T.SURFACE_3,
                                         border_color=T.BORDER,
                                         text_color=T.TEXT)
        self.lbl_dept   = ctk.CTkLabel(form_inner, text="Department",
                                        font=T.FONT_BODY, text_color=T.TEXT_MUTED)
        self.entry_dept  = ctk.CTkEntry(form_inner, width=280,
                                         height=T.INPUT_HEIGHT,
                                         fg_color=T.SURFACE_3,
                                         border_color=T.BORDER,
                                         text_color=T.TEXT)
        self.toggle_staff_fields()

        btn = create_primary_button(form_inner, "Create User",
                                     self.create_user, width=280)
        btn.grid(row=6, column=0, columnspan=2, pady=T.SP_L)

        # ── All Users card ──
        list_inner = create_card_fill(scroll, title="All Users")

        toolbar = ctk.CTkFrame(list_inner, fg_color="transparent")
        toolbar.pack(fill="x", pady=(0, T.SP_S))
        refresh_btn = create_ghost_button(toolbar, "⟳  Refresh", self.refresh_list)
        refresh_btn.pack(side="right")

        cols = ("ID", "Username", "Role", "Employee ID", "Department", "Created", "Last Login")
        self.tree = setup_treeview_scroll(
            list_inner, columns=cols,
            col_widths=[40, 120, 130, 110, 120, 140, 140],
            height=10,
            status_columns=["Role"],
            empty_message="No users found",
        )
        self.refresh_list()
        scroll.after(200, lambda: enable_trackpad_scroll(scroll))

        # Ctrl+F focuses search (no search bar here, focuses username instead)
        scroll.winfo_toplevel().bind("<Control-f>",
                                     lambda e: self.username_entry.focus_set())

    def toggle_staff_fields(self, *args):
        role = self.role_combo.get()
        if role in ("manager", "maintenance", "front_desk", "finance_manager"):
            self.lbl_empid.grid(row=3, column=0, padx=(0, T.SP_M), pady=T.SP_S, sticky="e")
            self.entry_empid.grid(row=3, column=1, pady=T.SP_S, sticky="w")
            self.lbl_dept.grid(row=4, column=0, padx=(0, T.SP_M), pady=T.SP_S, sticky="e")
            self.entry_dept.grid(row=4, column=1, pady=T.SP_S, sticky="w")
        else:
            self.lbl_empid.grid_remove()
            self.entry_empid.grid_remove()
            self.lbl_dept.grid_remove()
            self.entry_dept.grid_remove()

    def refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in self.auth_manager.get_all_users():
            self.tree.insert("", "end", values=row)
        apply_row_stripes(self.tree)
        autofit_columns(self.tree)

    def create_user(self):
        username   = self.username_entry.get()
        password   = self.password_entry.get()
        role       = self.role_combo.get()
        employee_id = self.entry_empid.get()
        department  = self.entry_dept.get()

        if not username or not password:
            show_warning(self._root, "Username and password are required.")
            return
        try:
            self.auth_manager.create_user(username, password, role, employee_id, department)
            show_success(self._root, f"User '{username}' created successfully.")
            for e in [self.username_entry, self.password_entry,
                      self.entry_empid, self.entry_dept]:
                e.delete(0, "end")
            self.refresh_list()
        except Exception as ex:
            show_error(self._root, str(ex))
