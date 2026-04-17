# Student Name: Omar Alfrouh
# Student ID: 24020879

import customtkinter as ctk
from views import theme as T
from views.ui_helpers import (
    setup_treeview_scroll, autofit_columns, apply_row_stripes,
    enable_trackpad_scroll, create_page_header, create_card, create_card_fill,
    create_primary_button, create_ghost_button, create_success_button,
    show_success, show_error, show_warning, export_table_to_csv,
)

_LBL_W = 110


class ApartmentView:
    def __init__(self, parent, property_manager):
        self.property_manager = property_manager
        self._root = parent.winfo_toplevel()

        frame = ctk.CTkScrollableFrame(parent, fg_color=T.BG,
                                        scrollbar_button_color=T.SURFACE_3)
        frame.pack(fill="both", expand=True)

        create_page_header(frame, "🏠 Apartments",
                            subtitle="Register and manage property units")

        # ── Add Apartment card ──
        inner = create_card(frame, title="Add Apartment")
        # 4-col grid: lbl | entry | lbl | entry  both entry cols expand equally
        inner.grid_columnconfigure(0, minsize=_LBL_W)
        inner.grid_columnconfigure(1, weight=1)
        inner.grid_columnconfigure(2, minsize=_LBL_W)
        inner.grid_columnconfigure(3, weight=1)

        def _lbl(text, row, col, req=False):
            ctk.CTkLabel(inner, text=text + (" *" if req else ""),
                          font=T.FONT_BODY,
                          text_color=T.DANGER if req else T.TEXT_MUTED,
                          anchor="e").grid(
                row=row, column=col, padx=(T.SP_M, T.SP_S),
                pady=T.SP_S, sticky="e")

        def _entry(row, col, placeholder=""):
            e = ctk.CTkEntry(inner, height=T.INPUT_HEIGHT,
                              fg_color=T.SURFACE_3, border_color=T.BORDER,
                              text_color=T.TEXT, placeholder_text=placeholder)
            e.grid(row=row, column=col, padx=(0, T.SP_M),
                   pady=T.SP_S, sticky="ew")
            return e

        _lbl("Unit #",     0, 0, True); self.unit_entry    = _entry(0, 1)
        _lbl("Address",    0, 2, True); self.address_entry = _entry(0, 3)

        _lbl("City",       1, 0, True)
        default_cities = ["Bristol", "Cardiff", "London", "Manchester"]
        existing = self.property_manager.get_cities()
        city_options = sorted(set(default_cities + existing))
        self.city_combo = ctk.CTkComboBox(
            inner, values=city_options, height=T.INPUT_HEIGHT,
            fg_color=T.SURFACE_3, border_color=T.BORDER,
            button_color=T.SURFACE_3, dropdown_fg_color=T.SURFACE,
            text_color=T.TEXT)
        self.city_combo.grid(row=1, column=1, padx=(0, T.SP_M),
                              pady=T.SP_S, sticky="ew")
        self.city_combo.set("Bristol")

        _lbl("Rooms",      1, 2);       self.rooms_entry  = _entry(1, 3, "e.g. 2")
        _lbl("Rent (£)",   2, 0, True); self.rent_entry   = _entry(2, 1, "e.g. 850")
        _lbl("Size (sqft)",2, 2, True); self.size_entry   = _entry(2, 3, "e.g. 650")

        btn = create_primary_button(inner, "Add Apartment", self.submit_apartment)
        btn.grid(row=3, column=0, columnspan=4, pady=T.SP_L,
                  padx=T.SP_M, sticky="ew")

        # ── Apartments table ──
        list_inner = create_card_fill(frame, title="Apartments")
        toolbar = ctk.CTkFrame(list_inner, fg_color="transparent")
        toolbar.pack(fill="x", pady=(0, T.SP_S))
        create_ghost_button(toolbar, "⟳  Refresh", self.refresh_list).pack(side="right")
        create_ghost_button(toolbar, "⬇  Export CSV",
                             self._export_apartments_csv).pack(side="right", padx=(0, T.SP_S))
        self._apt_del_btn = ctk.CTkButton(
            toolbar, text="🗑  Delete", width=80, height=28,
            fg_color=T.DANGER_MUTED, hover_color=T.DANGER,
            text_color=T.TEXT_MUTED, font=T.FONT_CAPTION_B,
            corner_radius=T.RADIUS_SM, state="disabled",
            command=self._delete_selected_apt)
        self._apt_del_btn.pack(side="right", padx=(0, T.SP_S))
        self._apt_detail_btn = ctk.CTkButton(
            toolbar, text="🔍  View Details", width=120, height=28,
            fg_color=T.SURFACE_3, hover_color=T.SURFACE_2,
            text_color=T.TEXT_MUTED, font=T.FONT_CAPTION_B,
            corner_radius=T.RADIUS_SM, state="disabled",
            command=self._show_apt_detail)
        self._apt_detail_btn.pack(side="right", padx=(0, T.SP_S))

        cols     = ("id", "unit", "address", "city", "rooms", "rent", "sqft", "status")
        headings = ["ID", "Unit", "Address", "City", "Rooms", "Rent", "Sqft", "Status"]
        self.tree = setup_treeview_scroll(
            list_inner, columns=cols, headings=headings,
            col_widths=[50, 100, 100, 100, 80, 100, 100, 100],
            height=10,
            status_columns=["status"],
            empty_message="No apartments registered yet",
        )
        self.tree.bind("<<TreeviewSelect>>", self._on_apt_select)

        # ── Edit Apartment card ──
        self._edit_apt_id = None
        edit_inner = create_card(frame, title="Edit Apartment")
        edit_inner.grid_columnconfigure(0, minsize=_LBL_W)
        edit_inner.grid_columnconfigure(1, weight=1)
        edit_inner.grid_columnconfigure(2, minsize=_LBL_W)
        edit_inner.grid_columnconfigure(3, weight=1)
        self._apt_edit_inner = edit_inner

        self._apt_placeholder = ctk.CTkLabel(
            edit_inner,
            text="Select an apartment from the table above to edit its details.",
            font=T.FONT_BODY, text_color=T.TEXT_SUBTLE)
        self._apt_placeholder.grid(row=0, column=0, columnspan=4,
                                    pady=T.SP_L, padx=T.SP_M)

        def _el(text, row, col, req=False):
            return ctk.CTkLabel(edit_inner,
                                text=text + (" *" if req else ""),
                                font=T.FONT_BODY,
                                text_color=T.DANGER if req else T.TEXT_MUTED,
                                anchor="e")

        def _ee(row, col, placeholder=""):
            e = ctk.CTkEntry(edit_inner, height=T.INPUT_HEIGHT,
                              fg_color=T.SURFACE_3, border_color=T.BORDER,
                              text_color=T.TEXT, placeholder_text=placeholder)
            return e

        self._ea_lbl_unit    = _el("Unit # (read-only)", 0, 0)
        self._ea_val_unit    = ctk.CTkLabel(edit_inner, text="", font=T.FONT_BODY_B,
                                             text_color=T.TEXT, anchor="w")
        self._ea_lbl_addr    = _el("Address *", 0, 2, True)
        self._ea_entry_addr  = _ee(0, 3)
        self._ea_lbl_city    = _el("City *", 1, 0, True)
        default_cities       = ["Bristol", "Cardiff", "London", "Manchester"]
        existing_cities      = self.property_manager.get_cities()
        self._ea_city_combo  = ctk.CTkComboBox(
            edit_inner, values=sorted(set(default_cities + existing_cities)),
            height=T.INPUT_HEIGHT, fg_color=T.SURFACE_3, border_color=T.BORDER,
            button_color=T.SURFACE_3, dropdown_fg_color=T.SURFACE, text_color=T.TEXT)
        self._ea_lbl_rooms   = _el("Rooms", 1, 2)
        self._ea_entry_rooms = _ee(1, 3, "e.g. 2")
        self._ea_lbl_rent    = _el("Rent (£) *", 2, 0, True)
        self._ea_entry_rent  = _ee(2, 1, "e.g. 850")
        self._ea_lbl_sqft    = _el("Size (sqft) *", 2, 2, True)
        self._ea_entry_sqft  = _ee(2, 3, "e.g. 650")
        self._apt_btn_frame  = ctk.CTkFrame(edit_inner, fg_color="transparent")

        self.refresh_list()
        frame.after(200, lambda: enable_trackpad_scroll(frame))

    def _on_apt_select(self, event=None):
        selected = self.tree.selection()
        has = bool(selected)
        color = T.TEXT if has else T.TEXT_MUTED
        self._apt_del_btn.configure(state="normal" if has else "disabled",
                                    text_color=color)
        self._apt_detail_btn.configure(state="normal" if has else "disabled",
                                       text_color=color)
        if not selected:
            return
        v = self.tree.item(selected[0], "values")
        # values: (id, unit, address, city, rooms, rent, sqft, status)
        self._edit_apt_id = int(v[0])
        unit    = v[1]
        address = v[2]
        city    = v[3]
        rooms   = v[4]
        rent    = str(v[5]).replace("£", "")
        sqft    = v[6]

        self._apt_placeholder.grid_remove()
        ei = self._apt_edit_inner

        self._ea_lbl_unit.grid(row=0, column=0, padx=(T.SP_M, T.SP_S), pady=T.SP_S, sticky="e")
        self._ea_val_unit.configure(text=unit)
        self._ea_val_unit.grid(row=0, column=1, padx=(0, T.SP_M), pady=T.SP_S, sticky="w")
        self._ea_lbl_addr.grid(row=0, column=2, padx=(T.SP_M, T.SP_S), pady=T.SP_S, sticky="e")
        self._ea_entry_addr.delete(0, "end"); self._ea_entry_addr.insert(0, address)
        self._ea_entry_addr.grid(row=0, column=3, padx=(0, T.SP_M), pady=T.SP_S, sticky="ew")

        self._ea_lbl_city.grid(row=1, column=0, padx=(T.SP_M, T.SP_S), pady=T.SP_S, sticky="e")
        self._ea_city_combo.set(city)
        self._ea_city_combo.grid(row=1, column=1, padx=(0, T.SP_M), pady=T.SP_S, sticky="ew")
        self._ea_lbl_rooms.grid(row=1, column=2, padx=(T.SP_M, T.SP_S), pady=T.SP_S, sticky="e")
        self._ea_entry_rooms.delete(0, "end"); self._ea_entry_rooms.insert(0, rooms)
        self._ea_entry_rooms.grid(row=1, column=3, padx=(0, T.SP_M), pady=T.SP_S, sticky="ew")

        self._ea_lbl_rent.grid(row=2, column=0, padx=(T.SP_M, T.SP_S), pady=T.SP_S, sticky="e")
        self._ea_entry_rent.delete(0, "end"); self._ea_entry_rent.insert(0, rent)
        self._ea_entry_rent.grid(row=2, column=1, padx=(0, T.SP_M), pady=T.SP_S, sticky="ew")
        self._ea_lbl_sqft.grid(row=2, column=2, padx=(T.SP_M, T.SP_S), pady=T.SP_S, sticky="e")
        self._ea_entry_sqft.delete(0, "end"); self._ea_entry_sqft.insert(0, sqft)
        self._ea_entry_sqft.grid(row=2, column=3, padx=(0, T.SP_M), pady=T.SP_S, sticky="ew")

        self._apt_btn_frame.grid(row=3, column=0, columnspan=4,
                                  pady=(T.SP_S, T.SP_L), padx=T.SP_M, sticky="ew")
        for w in self._apt_btn_frame.winfo_children():
            w.destroy()
        self._apt_btn_frame.grid_columnconfigure(0, weight=1)
        self._apt_btn_frame.grid_columnconfigure(1, weight=1)
        create_success_button(self._apt_btn_frame, "Save Changes",
                              self._save_apt_edit).grid(
            row=0, column=0, padx=(0, T.SP_S), sticky="ew")
        create_ghost_button(self._apt_btn_frame, "Cancel",
                            self._clear_apt_edit).grid(row=0, column=1, sticky="ew")

    def _clear_apt_edit(self):
        self._edit_apt_id = None
        self._apt_placeholder.grid(row=0, column=0, columnspan=4,
                                    pady=T.SP_L, padx=T.SP_M)
        for w in (self._ea_lbl_unit, self._ea_val_unit,
                  self._ea_lbl_addr, self._ea_entry_addr,
                  self._ea_lbl_city, self._ea_city_combo,
                  self._ea_lbl_rooms, self._ea_entry_rooms,
                  self._ea_lbl_rent, self._ea_entry_rent,
                  self._ea_lbl_sqft, self._ea_entry_sqft,
                  self._apt_btn_frame):
            w.grid_remove()
        self.tree.selection_remove(self.tree.selection())

    def _save_apt_edit(self):
        if self._edit_apt_id is None:
            return
        address = self._ea_entry_addr.get()
        city    = self._ea_city_combo.get()
        rooms   = self._ea_entry_rooms.get() or "1"
        rent    = self._ea_entry_rent.get()
        sqft    = self._ea_entry_sqft.get()
        try:
            self.property_manager.update_apartment(
                self._edit_apt_id, address, city, rooms, rent, sqft)
            show_success(self._root, "Apartment updated successfully.")
            self._clear_apt_edit()
            self.refresh_list()
        except Exception as ex:
            show_error(self._root, str(ex))

    def _delete_selected_apt(self):
        selected = self.tree.selection()
        if not selected:
            return
        v = self.tree.item(selected[0], "values")
        apt_id, unit = int(v[0]), v[1]
        from views.ui_helpers import confirm_dialog
        if not confirm_dialog(self._root, "Delete Apartment",
                              f"Permanently delete Unit {unit}?", danger=True):
            return
        try:
            self.property_manager.delete_apartment(apt_id)
            show_success(self._root, f"Unit {unit} deleted.")
            self._clear_apt_edit()
            self.refresh_list()
        except Exception as ex:
            show_error(self._root, str(ex))

    def _show_apt_detail(self):
        selected = self.tree.selection()
        if not selected:
            return
        apt_id = int(self.tree.item(selected[0], "values")[0])
        try:
            d = self.property_manager.get_apartment_detail(apt_id)
        except Exception as ex:
            show_error(self._root, str(ex))
            return

        import tkinter as _tk
        popup = ctk.CTkToplevel(self._root)
        popup.title(f"Unit {d['unit_number']} — Details")
        popup.geometry("440x480")
        popup.resizable(False, False)
        popup.grab_set()
        popup.configure(fg_color=T.SURFACE)

        band = ctk.CTkFrame(popup, fg_color=T.PRIMARY_MUTED, corner_radius=0)
        band.pack(fill="x")
        ctk.CTkLabel(band, text=f"🏠  Unit {d['unit_number']}",
                      font=T.FONT_H2, text_color=T.TEXT).pack(pady=(T.SP_L, T.SP_XS))
        ctk.CTkLabel(band, text=f"{d['address']}, {d['city']}",
                      font=T.FONT_BODY, text_color=T.TEXT_MUTED).pack(pady=(0, T.SP_L))
        _tk.Frame(popup, bg=T.BORDER, height=1).pack(fill="x")

        body = ctk.CTkScrollableFrame(popup, fg_color="transparent",
                                       scrollbar_button_color=T.SURFACE_3)
        body.pack(fill="both", expand=True, padx=T.SP_XL, pady=T.SP_L)

        def _section(title, fields):
            sec = ctk.CTkFrame(body, fg_color=T.SURFACE_2, corner_radius=T.RADIUS_SM)
            sec.pack(fill="x", pady=(0, T.SP_S))
            ctk.CTkLabel(sec, text=title, font=T.FONT_CAPTION_B,
                          text_color=T.TEXT_SUBTLE).pack(
                anchor="w", padx=T.SP_M, pady=(T.SP_S, 0))
            for label, value in fields:
                r = ctk.CTkFrame(sec, fg_color="transparent")
                r.pack(fill="x", padx=T.SP_M, pady=T.SP_XS)
                ctk.CTkLabel(r, text=label, font=T.FONT_CAPTION,
                              text_color=T.TEXT_MUTED, width=110, anchor="e").pack(side="left")
                ctk.CTkLabel(r, text=str(value) if value is not None else "-",
                              font=T.FONT_CAPTION_B, text_color=T.TEXT,
                              anchor="w").pack(side="left", padx=(T.SP_S, 0))
            ctk.CTkFrame(sec, height=T.SP_XS, fg_color="transparent").pack()

        _section("Property", [
            ("Rooms",   d["rooms"]),
            ("Rent",    f"£{d['rent']:.2f}"),
            ("Size",    f"{d['sqft']} sqft"),
            ("Status",  d["status"]),
            ("Maintenance tickets", d["maintenance_count"]),
        ])

        if d["tenant_name"]:
            _section("Current Tenant", [
                ("Name",        d["tenant_name"]),
                ("Email",       d["tenant_email"] or "-"),
                ("Phone",       d["tenant_phone"] or "-"),
                ("Monthly Rent", f"£{d['tenant_rent']:.2f}" if d["tenant_rent"] else "-"),
                ("Lease Start", d["tenant_lease_start"] or "-"),
                ("Lease End",   d["tenant_lease_end"] or "-"),
            ])
        else:
            sec = ctk.CTkFrame(body, fg_color=T.SURFACE_2, corner_radius=T.RADIUS_SM)
            sec.pack(fill="x", pady=(0, T.SP_S))
            ctk.CTkLabel(sec, text="No active tenant assigned.",
                          font=T.FONT_BODY, text_color=T.TEXT_MUTED).pack(
                pady=T.SP_M, padx=T.SP_M, anchor="w")

        _tk.Frame(popup, bg=T.BORDER, height=1).pack(fill="x")
        from views.ui_helpers import create_primary_button as _cpb
        _cpb(popup, "Close", popup.destroy, width=120).pack(pady=T.SP_L)
        popup.bind("<Escape>", lambda e: popup.destroy())
        popup.bind("<Return>", lambda e: popup.destroy())

    def _export_apartments_csv(self):
        from tkinter import filedialog
        path = filedialog.asksaveasfilename(
            parent=self._root, defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="apartments_export.csv", title="Export Apartments to CSV")
        if not path:
            return
        rows = self.property_manager.get_all_apartments()
        export_table_to_csv(
            ["ID", "Unit", "Address", "City", "Rooms", "Rent", "Sqft", "Status"],
            rows, path)
        show_success(self._root, f"Exported {len(rows)} rows to CSV.")

    def submit_apartment(self):
        try:
            self.property_manager.add_apartment(
                self.unit_entry.get(), self.address_entry.get(),
                self.rent_entry.get(), self.size_entry.get(),
                self.city_combo.get(), self.rooms_entry.get() or "1")
            show_success(self._root, "Apartment added successfully.")
            for e in [self.unit_entry, self.address_entry,
                      self.rooms_entry, self.rent_entry, self.size_entry]:
                e.delete(0, "end")
            self.refresh_list()
        except Exception as ex:
            show_error(self._root, str(ex))

    def refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for apt in self.property_manager.get_all_apartments():
            self.tree.insert("", "end", values=(
                apt[0], apt[1], apt[2], apt[3], apt[4],
                f"£{apt[5]:.2f}", apt[6], apt[7]))
        apply_row_stripes(self.tree)
        autofit_columns(self.tree)
