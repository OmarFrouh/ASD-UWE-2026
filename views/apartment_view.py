# Student Name: Omar Alfrouh
# Student ID: 24020879

import customtkinter as ctk
from views import theme as T
from views.ui_helpers import (
    setup_treeview_scroll, autofit_columns, apply_row_stripes,
    enable_trackpad_scroll, create_page_header, create_card, create_card_fill,
    create_primary_button, create_ghost_button,
    show_success, show_error,
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

        cols     = ("id", "unit", "address", "city", "rooms", "rent", "sqft", "status")
        headings = ["ID", "Unit", "Address", "City", "Rooms", "Rent", "Sqft", "Status"]
        self.tree = setup_treeview_scroll(
            list_inner, columns=cols, headings=headings,
            col_widths=[50, 100, 100, 100, 80, 100, 100, 100],
            height=10,
            status_columns=["status"],
            empty_message="No apartments registered yet",
        )
        self.refresh_list()
        frame.after(200, lambda: enable_trackpad_scroll(frame))

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
