# Student Name: Omar Alfrouh
# Student ID: 24020879

import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont


# ─── Theme constants ───
_BG        = "#333333"
_BG_ALT    = "#3c3c3c"   # alternating stripe
_FG        = "#e0e0e0"
_SEL_BG    = "#1f6aa5"
_SEL_FG    = "#ffffff"
_HEADER_BG = "#1f538d"
_HEADER_FG = "#ffffff"
_SCROLL_BG = "#444444"
_SCROLL_TR = "#2b2b2b"
_FONT      = ("Arial", 11)
_FONT_BOLD = ("Arial", 11, "bold")
_ROW_H     = 30
_COL_PAD   = 32   # extra pixels added beyond measured text per column
_SCROLL_W  = 18   # approximate width of the vertical scrollbar


def setup_treeview_scroll(parent, columns, headings=None, col_widths=None,
                          height=15, bind_scroll=True):
    """Dark-themed Treeview that:
    - Fills the container in both directions
    - Auto-fits column widths to content after data is inserted
    - Redistributes extra space proportionally on window resize
    """
    _apply_dark_style()

    # grid-based container so scrollbars sit OUTSIDE the tree
    container = tk.Frame(parent, bg=_BG, highlightthickness=0)
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
    vsb.grid (row=0, column=1, sticky="ns")
    hsb.grid (row=1, column=0, sticky="ew")

    # ─── Alternating row colours ───
    tree.tag_configure("even", background=_BG,     foreground=_FG)
    tree.tag_configure("odd",  background=_BG_ALT, foreground=_FG)

    # ─── Column headings (initial sizing from heading text) ───
    hfont = tkfont.Font(family="Arial", size=11, weight="bold")
    for i, c in enumerate(columns):
        label = headings[i] if headings else c
        w     = col_widths[i] if col_widths else max(hfont.measure(str(label)) + _COL_PAD, 80)
        tree.heading(c, text=label, anchor="w",
                     command=lambda _c=c: _sort_column(tree, _c, False))
        # stretch=True → columns grow/shrink with frame; we control the floor via width=
        tree.column(c, width=w, minwidth=60, anchor="w", stretch=True)

    # ─── Resize handler: redistribute extra space after data load and on resize ───
    # Store minimum widths dict on tree object for use by redistribute_columns()
    tree._min_widths = {}
    for c in columns:
        tree._min_widths[c] = tree.column(c, "width")

    def _on_resize(event):
        redistribute_columns(tree, event.width)

    container.bind("<Configure>", _on_resize)

    # ─── Smooth macOS trackpad scrolling ───
    # Only bind if bind_scroll=True. Pass False when the treeview lives inside
    # a CTkScrollableFrame — that way events bubble up to the frame's own handler.
    if bind_scroll:
        def _vscroll(event):
            tree.yview_scroll(int(-1 * event.delta), "units")

        def _hscroll(event):
            tree.xview_scroll(int(-1 * event.delta), "units")

        tree.bind("<MouseWheel>",       _vscroll)
        tree.bind("<Shift-MouseWheel>", _hscroll)
        tree.bind("<Button-4>", lambda e: tree.yview_scroll(-3, "units"))
        tree.bind("<Button-5>", lambda e: tree.yview_scroll( 3, "units"))

    return tree


# ─────────────────────────────────────────────────────────────────────────────
# Public helpers — call after inserting data
# ─────────────────────────────────────────────────────────────────────────────

def apply_row_stripes(tree):
    """Re-tag every row with even/odd for alternating background colours."""
    for i, iid in enumerate(tree.get_children("")):
        tree.item(iid, tags=("even" if i % 2 == 0 else "odd",))


def autofit_columns(tree):
    """Resize each column to fit the widest cell (heading or data).
    After this, redistribute_columns() will spread leftover space across
    the full container width."""
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

    # Store updated minimums after measuring actual content
    if hasattr(tree, "_min_widths"):
        for col in tree["columns"]:
            tree._min_widths[col] = tree.column(col, "width")

    # Trigger a redistribute right now based on current container width
    try:
        w = tree.master.winfo_width()
        if w > 1:
            redistribute_columns(tree, w)
    except Exception:
        pass


def redistribute_columns(tree, container_width):
    """Distribute any extra container width proportionally to columns.
    Columns never shrink below their measured minimum (_min_widths)."""
    if not hasattr(tree, "_min_widths") or not tree._min_widths:
        return

    cols       = tree["columns"]
    min_widths = [tree._min_widths.get(c, 80) for c in cols]
    total_min  = sum(min_widths)
    available  = container_width - _SCROLL_W

    if available <= 0:
        return

    if available <= total_min:
        # Container too narrow — keep minimum widths (h-scrollbar handles overflow)
        for c, w in zip(cols, min_widths):
            tree.column(c, width=w)
    else:
        # Extra space — distribute proportionally to each column's share
        extra = available - total_min
        for c, w in zip(cols, min_widths):
            ratio = w / total_min
            tree.column(c, width=int(w + extra * ratio))


# ─────────────────────────────────────────────────────────────────────────────
# Private helpers
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
        font=_FONT_BOLD, borderwidth=1, relief="flat", padding=(8, 5),
    )
    style.map("Dark.Treeview",
        background=[("selected", _SEL_BG)],
        foreground=[("selected", _SEL_FG)],
    )
    style.map("Dark.Treeview.Heading",
        background=[("active", "#2980b9")],
    )
    style.configure("Dark.Vertical.TScrollbar",
        background=_SCROLL_BG, troughcolor=_SCROLL_TR, borderwidth=0, arrowsize=14)
    style.configure("Dark.Horizontal.TScrollbar",
        background=_SCROLL_BG, troughcolor=_SCROLL_TR, borderwidth=0, arrowsize=14)
    style.map("Dark.Vertical.TScrollbar",   background=[("active", "#666")])
    style.map("Dark.Horizontal.TScrollbar", background=[("active", "#666")])


def enable_trackpad_scroll(scrollable_frame):
    """Make macOS trackpad scrolling work reliably inside a CTkScrollableFrame.

    The problem: ttk.Treeview and other widgets have CLASS-LEVEL MouseWheel
    bindings that consume the event before CTkScrollableFrame can process it.

    The fix: directly bind EVERY descendant widget (including treeviews) to
    scroll the scrollable frame's internal canvas, and return "break" to stop
    the event from propagating to class-level bindings.

    Call this AFTER all child widgets have been created (use .after(200, ...)).
    """
    try:
        canvas = scrollable_frame._parent_canvas
    except AttributeError:
        return

    def _scroll(event):
        canvas.yview_scroll(int(-1 * event.delta), "units")
        return "break"   # ← KEY: stops ttk class binding from consuming event

    def _bind_recursive(widget):
        # Skip ttk.Treeview — it handles its own trackpad scroll
        if isinstance(widget, ttk.Treeview):
            return
        widget.bind("<MouseWheel>", _scroll)   # NO add="+" — replace, don't append
        for child in widget.winfo_children():
            _bind_recursive(child)

    canvas.bind("<MouseWheel>", _scroll)
    _bind_recursive(scrollable_frame)


def _sort_column(tree, col, reverse):
    data = [(tree.set(k, col), k) for k in tree.get_children("")]
    try:
        data.sort(key=lambda t: float(
            t[0].replace("£","").replace(",","").replace("h","")
                .replace(" days","").strip()
        ), reverse=reverse)
    except ValueError:
        data.sort(reverse=reverse)

    for idx, (_, k) in enumerate(data):
        tree.move(k, "", idx)

    apply_row_stripes(tree)
    tree.heading(col, command=lambda _c=col: _sort_column(tree, _c, not reverse))
