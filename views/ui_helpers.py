# Student Name: Omar Alfrouh
# Student ID: 24020879

import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont
import customtkinter as ctk
from views import theme as T


# ─── Treeview Style Constants ────────────────────────────────────────────────
_BG        = T.SURFACE
_BG_ALT    = T.SURFACE_2
_FG        = T.TEXT
_SEL_BG    = T.PRIMARY_MUTED
_SEL_FG    = T.TEXT
_HEADER_BG = T.SURFACE_2
_HEADER_FG = T.TEXT
_SCROLL_BG = T.SURFACE_3
_SCROLL_TR = T.BG
_FONT      = ("Arial", 11)
_FONT_BOLD = ("Arial", 11, "bold")
_ROW_H     = T.ROW_HEIGHT
_COL_PAD   = 32
_SCROLL_W  = 18

# Status/priority → (foreground_colour, background_tint)
_STATUS_COLORS = {
    "Paid":        (T.SUCCESS,  T.SUCCESS_MUTED),
    "Pending":     (T.WARNING,  T.WARNING_MUTED),
    "Overdue":     (T.DANGER,   T.DANGER_MUTED),
    "Active":      (T.PRIMARY,  T.PRIMARY_MUTED),
    "Archived":    (T.TEXT_MUTED, T.SURFACE_3),
    "Terminated":  (T.DANGER,   T.DANGER_MUTED),
    "Open":        (T.INFO,     T.INFO_MUTED),
    "Assigned":    (T.PRIMARY,  T.PRIMARY_MUTED),
    "In Progress": (T.WARNING,  T.WARNING_MUTED),
    "Fixed":       (T.SUCCESS,  T.SUCCESS_MUTED),
    "Closed":      (T.TEXT_MUTED, T.SURFACE_3),
    "Low":         (T.TEXT_MUTED, T.SURFACE_3),
    "Medium":      (T.INFO,     T.INFO_MUTED),
    "High":        (T.WARNING,  T.WARNING_MUTED),
    "Urgent":      (T.DANGER,   T.DANGER_MUTED),
    "Occupied":    (T.PRIMARY,  T.PRIMARY_MUTED),
    "Vacant":      (T.TEXT_MUTED, T.SURFACE_3),
    "Resolved":    (T.SUCCESS,  T.SUCCESS_MUTED),
}


# ─────────────────────────────────────────────────────────────────────────────
# Treeview
# ─────────────────────────────────────────────────────────────────────────────

def setup_treeview_scroll(parent, columns, headings=None, col_widths=None,
                          height=15, bind_scroll=True,
                          status_columns=None, empty_message=None):
    """Dark-themed Treeview.

    Backwards-compatible: all existing call sites still work with the original
    positional/keyword args.  New optional params:
      status_columns  – list of column names that get coloured tags by value
      empty_message   – string shown centred over the tree when no rows
    """
    _apply_dark_style()

    container = tk.Frame(parent, bg=T.BG, highlightthickness=0)
    container.pack(fill="both", expand=True)
    container.grid_rowconfigure(0, weight=1)
    container.grid_columnconfigure(0, weight=1)

    tree = ttk.Treeview(container, columns=columns, show="headings",
                        height=height, style="Dark.Treeview")

    vsb = ttk.Scrollbar(container, orient="vertical",   command=tree.yview,
                        style="Dark.Vertical.TScrollbar")
    hsb = ttk.Scrollbar(container, orient="horizontal", command=tree.xview,
                        style="Dark.Horizontal.TScrollbar")
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

    tree.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    hsb.grid(row=1, column=0, sticky="ew")

    # Alternating row colours
    tree.tag_configure("even", background=_BG,     foreground=_FG)
    tree.tag_configure("odd",  background=_BG_ALT, foreground=_FG)

    # Status/priority colour tags
    for status, (fg, bg) in _STATUS_COLORS.items():
        tag_name = f"status_{status.replace(' ', '_')}"
        tree.tag_configure(tag_name, foreground=fg, background=bg)

    # Hover highlight
    tree.tag_configure("hover", background=T.SURFACE_3)
    _last_hover = [None]
    def _on_motion(event):
        row = tree.identify_row(event.y)
        if row == _last_hover[0]:
            return
        # Remove hover from previous row
        if _last_hover[0]:
            try:
                tags = list(tree.item(_last_hover[0], "tags"))
                if "hover" in tags:
                    tags.remove("hover")
                tree.item(_last_hover[0], tags=tuple(tags))
            except Exception:
                pass
        # Add hover to current row
        _last_hover[0] = row
        if row:
            try:
                tags = list(tree.item(row, "tags"))
                if "hover" not in tags:
                    tags.append("hover")
                tree.item(row, tags=tuple(tags))
            except Exception:
                pass
    def _on_leave(event):
        if _last_hover[0]:
            try:
                tags = list(tree.item(_last_hover[0], "tags"))
                if "hover" in tags:
                    tags.remove("hover")
                tree.item(_last_hover[0], tags=tuple(tags))
            except Exception:
                pass
            _last_hover[0] = None
    tree.bind("<Motion>", _on_motion)
    tree.bind("<Leave>", _on_leave)

    # Column headings
    hfont = tkfont.Font(family="Arial", size=11, weight="bold")
    for i, c in enumerate(columns):
        label = headings[i] if headings else c
        w     = col_widths[i] if col_widths else max(hfont.measure(str(label)) + _COL_PAD, 80)
        tree.heading(c, text=label, anchor="w",
                     command=lambda _c=c: _sort_column(tree, _c, False))
        tree.column(c, width=w, minwidth=60, anchor="w", stretch=True)

    tree._min_widths = {}
    for c in columns:
        tree._min_widths[c] = tree.column(c, "width")

    # Right-align currency columns
    for c in columns:
        label = (headings[list(columns).index(c)] if headings else c).lower()
        if any(k in label for k in ("rent", "amount", "cost", "revenue", "paid",
                                     "invoiced", "outstanding", "total", "collected",
                                     "pending", "spend", "avg")):
            tree.column(c, anchor="e")

    def _on_resize(event):
        redistribute_columns(tree, event.width)
    container.bind("<Configure>", _on_resize)

    if bind_scroll:
        def _vscroll(event):
            tree.yview_scroll(int(-1 * event.delta), "units")
        def _hscroll(event):
            tree.xview_scroll(int(-1 * event.delta), "units")
        tree.bind("<MouseWheel>",       _vscroll)
        tree.bind("<Shift-MouseWheel>", _hscroll)
        tree.bind("<Button-4>", lambda e: tree.yview_scroll(-3, "units"))
        tree.bind("<Button-5>", lambda e: tree.yview_scroll( 3, "units"))

    # Empty-state overlay label
    if empty_message:
        tree._empty_label = ctk.CTkLabel(
            container, text=empty_message,
            font=T.FONT_BODY, text_color=T.TEXT_MUTED,
            fg_color="transparent"
        )
        tree._empty_msg = empty_message
    else:
        tree._empty_label = None

    tree._status_columns = status_columns or []
    return tree


def apply_row_stripes(tree):
    """Re-tag every row with even/odd alternating colours.
    If a row's value in a status column matches a known status, the status tag
    takes priority (overrides the stripe) so the whole row is tinted.
    """
    cols = list(tree["columns"])
    status_col_indices = []
    for sc in tree._status_columns if hasattr(tree, "_status_columns") else []:
        if sc in cols:
            status_col_indices.append(cols.index(sc))

    for i, iid in enumerate(tree.get_children("")):
        stripe_tag = "even" if i % 2 == 0 else "odd"
        status_tag = None

        if status_col_indices:
            vals = tree.item(iid, "values")
            for idx in status_col_indices:
                if idx < len(vals):
                    v = str(vals[idx])
                    key = v.replace("⚠️ ", "")  # strip emoji prefix
                    if key in _STATUS_COLORS:
                        status_tag = f"status_{key.replace(' ', '_')}"
                        break

        tree.item(iid, tags=(status_tag or stripe_tag,))

    # Toggle empty-state label
    if hasattr(tree, "_empty_label") and tree._empty_label:
        if tree.get_children(""):
            tree._empty_label.place_forget()
        else:
            tree._empty_label.place(relx=0.5, rely=0.5, anchor="center")


def autofit_columns(tree):
    """Resize each column to fit its widest cell then redistribute extra space."""
    dfont = tkfont.Font(family="Arial", size=11)
    hfont = tkfont.Font(family="Arial", size=11, weight="bold")

    for col in tree["columns"]:
        heading_text = tree.heading(col)["text"]
        max_w = hfont.measure(str(heading_text)) + _COL_PAD
        for iid in tree.get_children(""):
            cw = dfont.measure(str(tree.set(iid, col))) + _COL_PAD
            if cw > max_w:
                max_w = cw
        tree.column(col, width=max_w)

    if hasattr(tree, "_min_widths"):
        for col in tree["columns"]:
            tree._min_widths[col] = tree.column(col, "width")

    try:
        w = tree.master.winfo_width()
        if w > 1:
            redistribute_columns(tree, w)
    except Exception:
        pass


def redistribute_columns(tree, container_width):
    if not hasattr(tree, "_min_widths") or not tree._min_widths:
        return
    cols       = tree["columns"]
    min_widths = [tree._min_widths.get(c, 80) for c in cols]
    total_min  = sum(min_widths)
    available  = container_width - _SCROLL_W
    if available <= 0:
        return
    if available <= total_min:
        for c, w in zip(cols, min_widths):
            tree.column(c, width=w)
    else:
        extra = available - total_min
        for c, w in zip(cols, min_widths):
            ratio = w / total_min
            tree.column(c, width=int(w + extra * ratio))


# ─────────────────────────────────────────────────────────────────────────────
# Treeview dark style
# ─────────────────────────────────────────────────────────────────────────────

def _apply_dark_style():
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass
    style.configure("Dark.Treeview",
        background=_BG, foreground=_FG, fieldbackground=_BG,
        borderwidth=0, font=_FONT, rowheight=_ROW_H,
    )
    style.configure("Dark.Treeview.Heading",
        background=_HEADER_BG, foreground=_HEADER_FG,
        font=_FONT_BOLD, borderwidth=0, relief="flat", padding=(10, 6),
    )
    style.map("Dark.Treeview",
        background=[("selected", _SEL_BG)],
        foreground=[("selected", _SEL_FG)],
    )
    style.map("Dark.Treeview.Heading",
        background=[("active", T.SURFACE_3)],
    )
    style.configure("Dark.Vertical.TScrollbar",
        background=_SCROLL_BG, troughcolor=_SCROLL_TR, borderwidth=0, arrowsize=12)
    style.configure("Dark.Horizontal.TScrollbar",
        background=_SCROLL_BG, troughcolor=_SCROLL_TR, borderwidth=0, arrowsize=12)
    style.map("Dark.Vertical.TScrollbar",   background=[("active", T.BORDER)])
    style.map("Dark.Horizontal.TScrollbar", background=[("active", T.BORDER)])


# ─────────────────────────────────────────────────────────────────────────────
# Trackpad scroll
# ─────────────────────────────────────────────────────────────────────────────

def enable_trackpad_scroll(scrollable_frame):
    """Make macOS trackpad scrolling work inside a CTkScrollableFrame."""
    try:
        canvas = scrollable_frame._parent_canvas
    except AttributeError:
        return

    def _scroll(event):
        canvas.yview_scroll(int(-1 * event.delta), "units")
        return "break"

    def _bind_recursive(widget):
        if isinstance(widget, ttk.Treeview):
            return
        widget.bind("<MouseWheel>", _scroll)
        for child in widget.winfo_children():
            _bind_recursive(child)

    canvas.bind("<MouseWheel>", _scroll)
    _bind_recursive(scrollable_frame)


# ─────────────────────────────────────────────────────────────────────────────
# Column sort
# ─────────────────────────────────────────────────────────────────────────────

def _sort_column(tree, col, reverse):
    data = [(tree.set(k, col), k) for k in tree.get_children("")]
    try:
        data.sort(key=lambda t: float(
            t[0].replace("£", "").replace(",", "").replace("h", "")
                .replace(" days", "").strip()
        ), reverse=reverse)
    except ValueError:
        data.sort(reverse=reverse)
    for idx, (_, k) in enumerate(data):
        tree.move(k, "", idx)
    apply_row_stripes(tree)
    tree.heading(col, command=lambda _c=col: _sort_column(tree, _c, not reverse))


# ─────────────────────────────────────────────────────────────────────────────
# Layout Helpers
# ─────────────────────────────────────────────────────────────────────────────

def create_page_header(parent, title, subtitle=None, actions=None):
    """Top-of-page title bar: H1 title + optional muted subtitle + right-aligned buttons."""
    bar = ctk.CTkFrame(parent, fg_color="transparent")
    bar.pack(fill="x", padx=T.SP_XL, pady=(T.SP_XL, T.SP_M))
    bar.grid_columnconfigure(0, weight=1)

    left = ctk.CTkFrame(bar, fg_color="transparent")
    left.grid(row=0, column=0, sticky="w")

    ctk.CTkLabel(left, text=title, font=T.FONT_H1,
                 text_color=T.TEXT).pack(anchor="w")
    if subtitle:
        ctk.CTkLabel(left, text=subtitle, font=T.FONT_CAPTION,
                     text_color=T.TEXT_MUTED).pack(anchor="w")

    if actions:
        right = ctk.CTkFrame(bar, fg_color="transparent")
        right.grid(row=0, column=1, sticky="e")
        for btn_cfg in actions:
            ctk.CTkButton(right, **btn_cfg,
                          height=T.BUTTON_HEIGHT, corner_radius=T.RADIUS_SM).pack(
                side="left", padx=(T.SP_S, 0))
    return bar


def create_card(parent, title=None, padding=None):
    """Bordered surface card. Returns the inner content frame."""
    if padding is None:
        padding = T.SP_L
    outer = ctk.CTkFrame(parent,
                         fg_color=T.SURFACE,
                         corner_radius=T.RADIUS_MD,
                         border_width=1,
                         border_color=T.BORDER)
    outer.pack(fill="x", padx=T.SP_XL, pady=T.SP_M)

    if title:
        ctk.CTkLabel(outer, text=title, font=T.FONT_H3,
                     text_color=T.TEXT).pack(
            anchor="w", padx=padding, pady=(padding, T.SP_S))
        sep = tk.Frame(outer, bg=T.BORDER, height=1)
        sep.pack(fill="x", padx=0)

    inner = ctk.CTkFrame(outer, fg_color="transparent")
    inner.pack(fill="both", expand=True, padx=padding, pady=padding)
    return inner


def create_card_fill(parent, title=None, padding=None):
    """Like create_card but expands to fill vertically — for table cards."""
    if padding is None:
        padding = T.SP_L
    outer = ctk.CTkFrame(parent,
                         fg_color=T.SURFACE,
                         corner_radius=T.RADIUS_MD,
                         border_width=1,
                         border_color=T.BORDER)
    outer.pack(fill="both", expand=True, padx=T.SP_XL, pady=T.SP_M)

    if title:
        ctk.CTkLabel(outer, text=title, font=T.FONT_H3,
                     text_color=T.TEXT).pack(
            anchor="w", padx=padding, pady=(padding, T.SP_S))
        sep = tk.Frame(outer, bg=T.BORDER, height=1)
        sep.pack(fill="x")

    inner = ctk.CTkFrame(outer, fg_color="transparent")
    inner.pack(fill="both", expand=True, padx=padding, pady=padding)
    return inner


def create_kpi_tile(parent, label, value, kind="neutral"):
    """Dashboard/report KPI tile. kind: neutral|primary|success|warning|danger|info."""
    color_map = {
        "neutral": T.BORDER,
        "primary": T.PRIMARY,
        "success": T.SUCCESS,
        "warning": T.WARNING,
        "danger":  T.DANGER,
        "info":    T.INFO,
    }
    border_color = color_map.get(kind, T.BORDER)

    tile = ctk.CTkFrame(parent,
                        fg_color=T.SURFACE,
                        corner_radius=T.RADIUS_MD,
                        border_width=2,
                        border_color=border_color)
    ctk.CTkLabel(tile, text=str(value), font=T.FONT_NUMERIC_XL,
                 text_color=T.TEXT).pack(pady=(T.SP_XL, T.SP_XS))
    ctk.CTkLabel(tile, text=label, font=T.FONT_CAPTION,
                 text_color=T.TEXT_MUTED).pack(pady=(0, T.SP_XL))
    return tile


def create_kpi_tile_l(parent, label, value, kind="neutral"):
    """Smaller KPI tile variant using FONT_NUMERIC_L."""
    color_map = {
        "neutral": T.BORDER,
        "primary": T.PRIMARY,
        "success": T.SUCCESS,
        "warning": T.WARNING,
        "danger":  T.DANGER,
        "info":    T.INFO,
    }
    tile = ctk.CTkFrame(parent,
                        fg_color=T.SURFACE,
                        corner_radius=T.RADIUS_MD,
                        border_width=2,
                        border_color=color_map.get(kind, T.BORDER))
    ctk.CTkLabel(tile, text=str(value), font=T.FONT_NUMERIC_L,
                 text_color=T.TEXT).pack(pady=(T.SP_L, T.SP_XS))
    ctk.CTkLabel(tile, text=label, font=T.FONT_CAPTION,
                 text_color=T.TEXT_MUTED).pack(pady=(0, T.SP_L))
    return tile


# ─────────────────────────────────────────────────────────────────────────────
# Buttons
# ─────────────────────────────────────────────────────────────────────────────

def create_primary_button(parent, text, command, width=None):
    kw = dict(text=text, command=command,
              fg_color=T.PRIMARY, hover_color=T.PRIMARY_HOVER,
              text_color=T.TEXT, font=T.FONT_H3,
              height=T.BUTTON_HEIGHT, corner_radius=T.RADIUS_SM)
    if width:
        kw["width"] = width
    return ctk.CTkButton(parent, **kw)


def create_secondary_button(parent, text, command, width=None):
    kw = dict(text=text, command=command,
              fg_color=T.SURFACE_3, hover_color=T.SURFACE_2,
              text_color=T.TEXT, font=T.FONT_BODY,
              border_width=1, border_color=T.BORDER,
              height=T.BUTTON_HEIGHT, corner_radius=T.RADIUS_SM)
    if width:
        kw["width"] = width
    return ctk.CTkButton(parent, **kw)


def create_danger_button(parent, text, command, width=None):
    kw = dict(text=text, command=command,
              fg_color=T.DANGER, hover_color=T.DANGER_HOVER,
              text_color="#ffffff", font=T.FONT_BODY_B,
              height=T.BUTTON_HEIGHT, corner_radius=T.RADIUS_SM)
    if width:
        kw["width"] = width
    return ctk.CTkButton(parent, **kw)


def create_warning_button(parent, text, command, width=None):
    kw = dict(text=text, command=command,
              fg_color=T.WARNING, hover_color=T.WARNING_HOVER,
              text_color="#000000", font=T.FONT_BODY_B,
              height=T.BUTTON_HEIGHT, corner_radius=T.RADIUS_SM)
    if width:
        kw["width"] = width
    return ctk.CTkButton(parent, **kw)


def create_success_button(parent, text, command, width=None):
    kw = dict(text=text, command=command,
              fg_color=T.SUCCESS, hover_color=T.SUCCESS_HOVER,
              text_color="#000000", font=T.FONT_BODY_B,
              height=T.BUTTON_HEIGHT, corner_radius=T.RADIUS_SM)
    if width:
        kw["width"] = width
    return ctk.CTkButton(parent, **kw)


def create_ghost_button(parent, text, command, width=None):
    kw = dict(text=text, command=command,
              fg_color="transparent", hover_color=T.SURFACE_2,
              text_color=T.TEXT_MUTED, font=T.FONT_BODY,
              height=T.BUTTON_HEIGHT, corner_radius=T.RADIUS_SM)
    if width:
        kw["width"] = width
    return ctk.CTkButton(parent, **kw)


# ─────────────────────────────────────────────────────────────────────────────
# Form helpers
# ─────────────────────────────────────────────────────────────────────────────

def create_form_row(parent, row, label, required=False, help_text=None,
                    widget=None, col_offset=0):
    """Label (with * marker) + widget in a grid row.  Returns the widget."""
    lbl_text = label + (" *" if required else "")
    lbl_color = T.DANGER if required else T.TEXT_MUTED
    ctk.CTkLabel(parent, text=lbl_text, font=T.FONT_BODY,
                 text_color=lbl_color, anchor="e").grid(
        row=row, column=col_offset, padx=(0, T.SP_S), pady=T.SP_S, sticky="e")

    if widget is None:
        w = ctk.CTkEntry(parent, height=T.INPUT_HEIGHT,
                         fg_color=T.SURFACE_3,
                         border_color=T.BORDER,
                         text_color=T.TEXT)
    else:
        w = widget

    w.grid(row=row, column=col_offset + 1, padx=(0, T.SP_M),
           pady=T.SP_S, sticky="w")

    if help_text:
        ctk.CTkLabel(parent, text=help_text, font=T.FONT_CAPTION,
                     text_color=T.TEXT_SUBTLE).grid(
            row=row + 1, column=col_offset + 1, sticky="w",
            padx=(0, T.SP_M), pady=(0, T.SP_XS))

    return w


def create_section_divider(parent, text=None):
    """1 px horizontal divider, optional centred label."""
    frame = ctk.CTkFrame(parent, fg_color="transparent")
    frame.pack(fill="x", pady=T.SP_M)
    if text:
        ctk.CTkLabel(frame, text=text, font=T.FONT_CAPTION_B,
                     text_color=T.TEXT_SUBTLE).pack(anchor="w")
    tk.Frame(frame, bg=T.BORDER, height=1).pack(fill="x")


# ─────────────────────────────────────────────────────────────────────────────
# Inline badge label
# ─────────────────────────────────────────────────────────────────────────────

_BADGE_KINDS = {
    "success": (T.SUCCESS,   T.SUCCESS_MUTED),
    "warning": (T.WARNING,   T.WARNING_MUTED),
    "danger":  (T.DANGER,    T.DANGER_MUTED),
    "info":    (T.INFO,      T.INFO_MUTED),
    "muted":   (T.TEXT_MUTED, T.SURFACE_3),
    "primary": (T.PRIMARY,   T.PRIMARY_MUTED),
}

def create_badge(parent, text, kind="muted"):
    fg, bg = _BADGE_KINDS.get(kind, _BADGE_KINDS["muted"])
    return ctk.CTkLabel(parent, text=f"  {text}  ",
                        font=T.FONT_CAPTION_B,
                        text_color=fg, fg_color=bg,
                        corner_radius=T.RADIUS_PILL)


# ─────────────────────────────────────────────────────────────────────────────
# Empty state
# ─────────────────────────────────────────────────────────────────────────────

def create_empty_state(parent, icon, title, message, action=None):
    """Centred empty-state block inside a card/frame."""
    frame = ctk.CTkFrame(parent, fg_color="transparent")
    frame.pack(expand=True, pady=T.SP_2XL)
    ctk.CTkLabel(frame, text=icon, font=("Arial", 40)).pack()
    ctk.CTkLabel(frame, text=title, font=T.FONT_H3,
                 text_color=T.TEXT).pack(pady=(T.SP_S, T.SP_XS))
    ctk.CTkLabel(frame, text=message, font=T.FONT_BODY,
                 text_color=T.TEXT_MUTED).pack()
    if action:
        create_primary_button(frame, **action).pack(pady=T.SP_L)
    return frame


# ─────────────────────────────────────────────────────────────────────────────
# Search bar
# ─────────────────────────────────────────────────────────────────────────────

def create_search_bar(parent, placeholder, on_change):
    """🔍 search entry + ✕ clear button. Returns the CTkEntry widget."""
    bar = ctk.CTkFrame(parent, fg_color="transparent")
    bar.pack(side="left", padx=(0, T.SP_M))

    ctk.CTkLabel(bar, text="🔍", font=T.FONT_BODY).pack(side="left",
                                                         padx=(0, T.SP_XS))
    entry = ctk.CTkEntry(bar, placeholder_text=placeholder,
                         width=200, height=T.INPUT_HEIGHT,
                         fg_color=T.SURFACE_3, border_color=T.BORDER,
                         text_color=T.TEXT)
    entry.pack(side="left")
    entry.bind("<KeyRelease>", lambda e: on_change(entry.get()))

    def _clear():
        entry.delete(0, "end")
        on_change("")

    ctk.CTkButton(bar, text="✕", command=_clear,
                  width=28, height=T.INPUT_HEIGHT,
                  fg_color="transparent", hover_color=T.SURFACE_3,
                  text_color=T.TEXT_MUTED, font=T.FONT_CAPTION).pack(side="left")
    return entry


# ─────────────────────────────────────────────────────────────────────────────
# Toast notifications
# ─────────────────────────────────────────────────────────────────────────────

_KIND_COLORS = {
    "success": T.SUCCESS,
    "error":   T.DANGER,
    "warning": T.WARNING,
    "info":    T.INFO,
}
_KIND_ICONS = {
    "success": "✓",
    "error":   "✕",
    "warning": "⚠",
    "info":    "ℹ",
}

def show_toast(root, message, kind="info", duration=2500):
    """Auto-dismiss toast anchored to the top-right of root."""
    fg = _KIND_COLORS.get(kind, T.INFO)
    icon = _KIND_ICONS.get(kind, "ℹ")

    toast = ctk.CTkToplevel(root)
    toast.overrideredirect(True)
    toast.attributes("-topmost", True)

    # Position top-right
    root.update_idletasks()
    rx, ry = root.winfo_rootx(), root.winfo_rooty()
    rw = root.winfo_width()
    toast.geometry(f"340x60+{rx + rw - 360}+{ry + 12}")

    frame = ctk.CTkFrame(toast, fg_color=T.SURFACE,
                          corner_radius=T.RADIUS_MD,
                          border_width=1, border_color=fg)
    frame.pack(fill="both", expand=True, padx=2, pady=2)

    ctk.CTkLabel(frame, text=icon, font=T.FONT_BODY_B,
                 text_color=fg, width=24).pack(side="left", padx=(T.SP_M, T.SP_S))
    ctk.CTkLabel(frame, text=message, font=T.FONT_BODY,
                 text_color=T.TEXT, wraplength=270, anchor="w").pack(
        side="left", fill="x", expand=True, pady=T.SP_M)

    toast.after(duration, toast.destroy)


def show_success(root, message):
    show_toast(root, message, kind="success")

def show_error(root, message):
    show_toast(root, message, kind="error")

def show_warning(root, message):
    show_toast(root, message, kind="warning")

def show_info(root, message):
    show_toast(root, message, kind="info")


# ─────────────────────────────────────────────────────────────────────────────
# Confirm dialog
# ─────────────────────────────────────────────────────────────────────────────

def confirm_dialog(root, title, message, danger=False):
    """Custom confirm modal. Returns True if confirmed, False if cancelled.
    Replaces messagebox.askyesno — dark-themed, honours app colours.
    """
    result = [False]

    dlg = ctk.CTkToplevel(root)
    dlg.title(title)
    dlg.geometry("420x200")
    dlg.resizable(False, False)
    dlg.grab_set()
    dlg.attributes("-topmost", True)

    # Centre on root
    root.update_idletasks()
    rx, ry = root.winfo_rootx(), root.winfo_rooty()
    rw, rh = root.winfo_width(), root.winfo_height()
    dlg.geometry(f"420x200+{rx + (rw - 420)//2}+{ry + (rh - 200)//2}")

    ctk.CTkLabel(dlg, text=title, font=T.FONT_H3,
                 text_color=T.DANGER if danger else T.TEXT).pack(pady=(T.SP_XL, T.SP_S))
    ctk.CTkLabel(dlg, text=message, font=T.FONT_BODY,
                 text_color=T.TEXT_MUTED, wraplength=380).pack(pady=T.SP_S)

    btn_frame = ctk.CTkFrame(dlg, fg_color="transparent")
    btn_frame.pack(pady=T.SP_L)

    def _confirm():
        result[0] = True
        dlg.destroy()

    def _cancel():
        dlg.destroy()

    create_ghost_button(btn_frame, "Cancel", _cancel, width=120).pack(side="left", padx=T.SP_S)
    if danger:
        create_danger_button(btn_frame, "Confirm", _confirm, width=120).pack(side="left", padx=T.SP_S)
    else:
        create_primary_button(btn_frame, "Confirm", _confirm, width=120).pack(side="left", padx=T.SP_S)

    dlg.bind("<Return>", lambda e: _confirm())
    dlg.bind("<Escape>", lambda e: _cancel())

    dlg.wait_window()
    return result[0]
