# Student Name: Omar Alfrouh
# Student ID: 24020879

import customtkinter as ctk
from views import theme as T
from views.ui_helpers import (
    setup_treeview_scroll, autofit_columns, apply_row_stripes,
    enable_trackpad_scroll, create_page_header, create_card, create_card_fill,
    create_primary_button, create_ghost_button, create_danger_button,
    create_success_button,
    show_success, show_error, show_warning, confirm_dialog, export_table_to_csv,
)

_LBL_W = 130   # fixed label column width — entries fill the rest


class UserView:
    def __init__(self, parent_frame, auth_manager, current_user=None):
        self.parent       = parent_frame
        self.auth_manager = auth_manager
        self.current_user = current_user
        self._root        = parent_frame.winfo_toplevel()

        scroll = ctk.CTkScrollableFrame(parent_frame, fg_color=T.BG,
                                         scrollbar_button_color=T.SURFACE_3)
        scroll.pack(fill="both", expand=True)

        create_page_header(scroll, "👥 Users",
                            subtitle="Manage staff and admin accounts")

        # ── Add User card ──
        form_inner = create_card(scroll, title="Add User")
        form_inner.grid_columnconfigure(0, minsize=_LBL_W)
        form_inner.grid_columnconfigure(1, weight=1)   # ← entries expand

        def _e(row, show=""):
            e = ctk.CTkEntry(form_inner, height=T.INPUT_HEIGHT,
                              fg_color=T.SURFACE_3, border_color=T.BORDER,
                              text_color=T.TEXT, show=show)
            e.grid(row=row, column=1, pady=T.SP_S,
                   padx=(0, T.SP_M), sticky="ew")
            return e

        def _l(text, row, req=False):
            ctk.CTkLabel(form_inner,
                          text=text + (" *" if req else ""),
                          font=T.FONT_BODY,
                          text_color=T.DANGER if req else T.TEXT_MUTED,
                          anchor="e").grid(
                row=row, column=0, pady=T.SP_S,
                padx=(T.SP_M, T.SP_S), sticky="e")

        _l("Username",    0, True); self.username_entry = _e(0)
        _l("Password",    1, True); self.password_entry = _e(1, show="•")
        _l("Role",        2, True)

        self.role_combo = ctk.CTkComboBox(
            form_inner,
            values=["front_desk", "finance_manager", "maintenance", "manager", "admin"],
            height=T.INPUT_HEIGHT,
            fg_color=T.SURFACE_3, border_color=T.BORDER,
            button_color=T.SURFACE_3, dropdown_fg_color=T.SURFACE,
            text_color=T.TEXT,
            command=self.toggle_staff_fields)
        self.role_combo.grid(row=2, column=1, pady=T.SP_S,
                              padx=(0, T.SP_M), sticky="ew")
        self.role_combo.set("front_desk")

        # Conditional staff fields
        self.lbl_empid   = ctk.CTkLabel(form_inner, text="Employee ID *",
                                          font=T.FONT_BODY, text_color=T.DANGER, anchor="e")
        self.entry_empid = ctk.CTkEntry(form_inner, height=T.INPUT_HEIGHT,
                                         fg_color=T.SURFACE_3, border_color=T.BORDER,
                                         text_color=T.TEXT)
        self.lbl_dept    = ctk.CTkLabel(form_inner, text="Department",
                                          font=T.FONT_BODY, text_color=T.TEXT_MUTED, anchor="e")
        self.entry_dept  = ctk.CTkEntry(form_inner, height=T.INPUT_HEIGHT,
                                         fg_color=T.SURFACE_3, border_color=T.BORDER,
                                         text_color=T.TEXT)
        self.toggle_staff_fields()

        btn = create_primary_button(form_inner, "Create User", self.create_user)
        btn.grid(row=6, column=0, columnspan=2,
                 pady=T.SP_L, padx=T.SP_M, sticky="ew")

        # ── All Users card ──
        list_inner = create_card_fill(scroll, title="All Users")

        toolbar = ctk.CTkFrame(list_inner, fg_color="transparent")
        toolbar.pack(fill="x", pady=(0, T.SP_S))
        create_ghost_button(toolbar, "⟳  Refresh", self.refresh_list).pack(side="right")
        create_ghost_button(toolbar, "⬇  Export CSV",
                             self._export_users_csv).pack(side="right", padx=(0, T.SP_S))
        create_danger_button(toolbar, "🗑  Delete Selected", self.delete_user).pack(side="right", padx=(0, T.SP_S))

        cols = ("ID", "Username", "Role", "Employee ID", "Department", "Created", "Last Login")
        self.tree = setup_treeview_scroll(
            list_inner, columns=cols,
            col_widths=[40, 120, 130, 110, 120, 140, 140],
            height=10,
            status_columns=["Role"],
            empty_message="No users found",
        )
        self.tree.bind("<<TreeviewSelect>>", self._on_user_select)

        # ── Edit User card ──
        self._edit_user_id = None
        edit_inner = create_card(scroll, title="Edit User")
        edit_inner.grid_columnconfigure(0, minsize=_LBL_W)
        edit_inner.grid_columnconfigure(1, weight=1)
        self._edit_inner = edit_inner

        self._edit_placeholder = ctk.CTkLabel(
            edit_inner, text="Select a user from the table above to edit their details.",
            font=T.FONT_BODY, text_color=T.TEXT_SUBTLE)
        self._edit_placeholder.grid(row=0, column=0, columnspan=2,
                                     pady=T.SP_L, padx=T.SP_M)

        def _el(text, row, req=False):
            ctk.CTkLabel(edit_inner,
                          text=text + (" *" if req else ""),
                          font=T.FONT_BODY,
                          text_color=T.DANGER if req else T.TEXT_MUTED,
                          anchor="e").grid(
                row=row, column=0, pady=T.SP_S,
                padx=(T.SP_M, T.SP_S), sticky="e")

        # Username read-only row (hidden until populated)
        self._edit_lbl_uname = ctk.CTkLabel(edit_inner, text="Username",
                                              font=T.FONT_BODY, text_color=T.TEXT_MUTED, anchor="e")
        self._edit_val_uname = ctk.CTkLabel(edit_inner, text="",
                                              font=T.FONT_BODY_B, text_color=T.TEXT, anchor="w")

        # Role combo
        self._edit_lbl_role = ctk.CTkLabel(edit_inner, text="Role *",
                                             font=T.FONT_BODY, text_color=T.DANGER, anchor="e")
        self._edit_role_combo = ctk.CTkComboBox(
            edit_inner,
            values=["front_desk", "finance_manager", "maintenance", "manager", "admin"],
            height=T.INPUT_HEIGHT,
            fg_color=T.SURFACE_3, border_color=T.BORDER,
            button_color=T.SURFACE_3, dropdown_fg_color=T.SURFACE,
            text_color=T.TEXT,
            command=self._toggle_edit_staff_fields)

        # Staff-only fields
        self._edit_lbl_empid  = ctk.CTkLabel(edit_inner, text="Employee ID *",
                                               font=T.FONT_BODY, text_color=T.DANGER, anchor="e")
        self._edit_entry_empid = ctk.CTkEntry(edit_inner, height=T.INPUT_HEIGHT,
                                               fg_color=T.SURFACE_3, border_color=T.BORDER,
                                               text_color=T.TEXT)
        self._edit_lbl_dept   = ctk.CTkLabel(edit_inner, text="Department",
                                               font=T.FONT_BODY, text_color=T.TEXT_MUTED, anchor="e")
        self._edit_entry_dept  = ctk.CTkEntry(edit_inner, height=T.INPUT_HEIGHT,
                                               fg_color=T.SURFACE_3, border_color=T.BORDER,
                                               text_color=T.TEXT)

        # Action buttons row
        self._edit_btn_frame = ctk.CTkFrame(edit_inner, fg_color="transparent")

        # Reset password section (shown below save buttons when editing)
        self._edit_sep       = ctk.CTkFrame(edit_inner, fg_color=T.BORDER, height=1)
        self._edit_lbl_newpw = ctk.CTkLabel(edit_inner, text="New Password",
                                              font=T.FONT_BODY, text_color=T.TEXT_MUTED,
                                              anchor="e")
        self._edit_pw_entry  = ctk.CTkEntry(edit_inner, height=T.INPUT_HEIGHT,
                                             fg_color=T.SURFACE_3, border_color=T.BORDER,
                                             text_color=T.TEXT, show="•",
                                             placeholder_text="Min 6 characters")
        self._edit_reset_frame = ctk.CTkFrame(edit_inner, fg_color="transparent")

        self.refresh_list()
        scroll.after(200, lambda: enable_trackpad_scroll(scroll))
        scroll.winfo_toplevel().bind("<Control-f>",
                                     lambda e: self.username_entry.focus_set())

    def _on_user_select(self, event=None):
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0], "values")
        self._edit_user_id = int(values[0])
        username    = values[1]
        role        = values[2]
        employee_id = values[3]
        department  = values[4]

        self._edit_placeholder.grid_remove()

        ei = self._edit_inner
        self._edit_lbl_uname.grid(row=0, column=0, pady=T.SP_S,
                                   padx=(T.SP_M, T.SP_S), sticky="e")
        self._edit_val_uname.configure(text=username)
        self._edit_val_uname.grid(row=0, column=1, pady=T.SP_S,
                                   padx=(0, T.SP_M), sticky="w")

        self._edit_lbl_role.grid(row=1, column=0, pady=T.SP_S,
                                  padx=(T.SP_M, T.SP_S), sticky="e")
        self._edit_role_combo.grid(row=1, column=1, pady=T.SP_S,
                                    padx=(0, T.SP_M), sticky="ew")
        self._edit_role_combo.set(role)
        self._toggle_edit_staff_fields(role, employee_id, department)

        self._edit_btn_frame.grid(row=5, column=0, columnspan=2,
                                   pady=(T.SP_S, T.SP_S), padx=T.SP_M, sticky="ew")
        for w in self._edit_btn_frame.winfo_children():
            w.destroy()
        self._edit_btn_frame.grid_columnconfigure(0, weight=1)
        self._edit_btn_frame.grid_columnconfigure(1, weight=1)
        create_success_button(self._edit_btn_frame, "Save Changes",
                              self._save_user_edit).grid(
            row=0, column=0, padx=(0, T.SP_S), sticky="ew")
        create_ghost_button(self._edit_btn_frame, "Cancel", self._clear_edit).grid(
            row=0, column=1, sticky="ew")

        # Reset password section
        self._edit_sep.grid(row=6, column=0, columnspan=2,
                             sticky="ew", padx=T.SP_M, pady=(T.SP_M, T.SP_S))
        self._edit_lbl_newpw.grid(row=7, column=0, pady=T.SP_S,
                                   padx=(T.SP_M, T.SP_S), sticky="e")
        self._edit_pw_entry.delete(0, "end")
        self._edit_pw_entry.grid(row=7, column=1, pady=T.SP_S,
                                  padx=(0, T.SP_M), sticky="ew")
        self._edit_reset_frame.grid(row=8, column=0, columnspan=2,
                                     pady=(T.SP_S, T.SP_L), padx=T.SP_M, sticky="ew")
        for w in self._edit_reset_frame.winfo_children():
            w.destroy()
        create_danger_button(self._edit_reset_frame, "🔑  Reset Password",
                             self._reset_user_password).pack(fill="x")

    def _toggle_edit_staff_fields(self, role=None, employee_id="", department=""):
        if role is None:
            role = self._edit_role_combo.get()
        needs = role in ("manager", "maintenance", "front_desk", "finance_manager")
        if needs:
            self._edit_lbl_empid.grid(row=2, column=0, pady=T.SP_S,
                                       padx=(T.SP_M, T.SP_S), sticky="e")
            self._edit_entry_empid.grid(row=2, column=1, pady=T.SP_S,
                                         padx=(0, T.SP_M), sticky="ew")
            self._edit_lbl_dept.grid(row=3, column=0, pady=T.SP_S,
                                      padx=(T.SP_M, T.SP_S), sticky="e")
            self._edit_entry_dept.grid(row=3, column=1, pady=T.SP_S,
                                        padx=(0, T.SP_M), sticky="ew")
            if isinstance(employee_id, str):
                self._edit_entry_empid.delete(0, "end")
                self._edit_entry_empid.insert(0, employee_id)
            if isinstance(department, str):
                self._edit_entry_dept.delete(0, "end")
                self._edit_entry_dept.insert(0, department)
        else:
            self._edit_lbl_empid.grid_remove()
            self._edit_entry_empid.grid_remove()
            self._edit_lbl_dept.grid_remove()
            self._edit_entry_dept.grid_remove()

    def _clear_edit(self):
        self._edit_user_id = None
        self._edit_placeholder.grid(row=0, column=0, columnspan=2,
                                     pady=T.SP_L, padx=T.SP_M)
        for w in (self._edit_lbl_uname, self._edit_val_uname,
                  self._edit_lbl_role, self._edit_role_combo,
                  self._edit_lbl_empid, self._edit_entry_empid,
                  self._edit_lbl_dept, self._edit_entry_dept,
                  self._edit_btn_frame, self._edit_sep,
                  self._edit_lbl_newpw, self._edit_pw_entry,
                  self._edit_reset_frame):
            w.grid_remove()
        self.tree.selection_remove(self.tree.selection())

    def _reset_user_password(self):
        if self._edit_user_id is None:
            return
        new_pw   = self._edit_pw_entry.get()
        username = self._edit_val_uname.cget("text")
        if not confirm_dialog(self._root, "Reset Password",
                              f"Reset password for '{username}'?", danger=True):
            return
        try:
            self.auth_manager.reset_password(self._edit_user_id, new_pw)
            self._edit_pw_entry.delete(0, "end")
            show_success(self._root, f"Password for '{username}' has been reset.")
        except Exception as ex:
            show_error(self._root, str(ex))

    def _save_user_edit(self):
        if self._edit_user_id is None:
            return
        role        = self._edit_role_combo.get()
        employee_id = self._edit_entry_empid.get()
        department  = self._edit_entry_dept.get()
        current_id  = self.current_user[0] if self.current_user else None
        username    = self._edit_val_uname.cget("text")
        try:
            self.auth_manager.update_user(
                self._edit_user_id, role, employee_id, department, current_id)
            show_success(self._root, f"User '{username}' updated.")
            self._clear_edit()
            self.refresh_list()
        except Exception as ex:
            show_error(self._root, str(ex))

    def toggle_staff_fields(self, *args):
        role = self.role_combo.get()
        if role in ("manager", "maintenance", "front_desk", "finance_manager"):
            self.lbl_empid.grid(row=3, column=0, pady=T.SP_S,
                                 padx=(T.SP_M, T.SP_S), sticky="e")
            self.entry_empid.grid(row=3, column=1, pady=T.SP_S,
                                   padx=(0, T.SP_M), sticky="ew")
            self.lbl_dept.grid(row=4, column=0, pady=T.SP_S,
                                padx=(T.SP_M, T.SP_S), sticky="e")
            self.entry_dept.grid(row=4, column=1, pady=T.SP_S,
                                  padx=(0, T.SP_M), sticky="ew")
        else:
            self.lbl_empid.grid_remove()
            self.entry_empid.grid_remove()
            self.lbl_dept.grid_remove()
            self.entry_dept.grid_remove()

    def delete_user(self):
        selected = self.tree.selection()
        if not selected:
            show_warning(self._root, "Select a user from the list to delete.")
            return
        values   = self.tree.item(selected[0], "values")
        user_id  = int(values[0])
        username = values[1]
        current_id = self.current_user[0] if self.current_user else None
        if not confirm_dialog(self._root, "Delete User",
                              f"Delete user '{username}'? This cannot be undone.",
                              danger=True):
            return
        try:
            self.auth_manager.delete_user(user_id, current_id)
            show_success(self._root, f"User '{username}' deleted.")
            self.refresh_list()
        except Exception as ex:
            show_error(self._root, str(ex))

    def refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in self.auth_manager.get_all_users():
            self.tree.insert("", "end", values=row)
        apply_row_stripes(self.tree)
        autofit_columns(self.tree)

    def _export_users_csv(self):
        from tkinter import filedialog
        path = filedialog.asksaveasfilename(
            parent=self._root, defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="users_export.csv", title="Export Users to CSV")
        if not path:
            return
        rows = self.auth_manager.get_all_users()
        export_table_to_csv(
            ["ID", "Username", "Role", "Employee ID", "Department", "Created", "Last Login"],
            rows, path)
        show_success(self._root, f"Exported {len(rows)} rows to CSV.")

    def create_user(self):
        username    = self.username_entry.get()
        password    = self.password_entry.get()
        role        = self.role_combo.get()
        employee_id = self.entry_empid.get()
        department  = self.entry_dept.get()

        if not username or not password:
            show_warning(self._root, "Username and password are required.")
            return
        if len(password) < 6:
            show_warning(self._root, "Password must be at least 6 characters.")
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
