# Shared UI helpers for PAMS views
import tkinter as tk
from tkinter import ttk
import tkinter.font as tkfont


# ─── Theme constants ───
_BG = "#333333"
_BG_ALT = "#3c3c3c"       # alternating row stripe (slightly lighter)
_FG = "#e0e0e0"
_SEL_BG = "#1f6aa5"
_SEL_FG = "#ffffff"
_HEADER_BG = "#1f538d"
_HEADER_FG = "#ffffff"
_SCROLL_BG = "#444444"
_SCROLL_TROUGH = "#2b2b2b"
_FONT = ("Arial", 11)
_FONT_BOLD = ("Arial", 11, "bold")
_ROW_HEIGHT = 30
_COL_PAD = 20          # extra pixels added per column beyond measured text


def setup_treeview_scroll(parent, columns, headings=None, col_widths=None, height=15):
    """Create a dark-themed Treeview.

    Column widths default to measured heading width.  After inserting data,
    call ``autofit_columns(tree)`` to resize to the widest cell.
    """
    _apply_dark_treeview_style()

    # Outer container uses grid so scrollbars sit *outside* the tree widget
    container = tk.Frame(parent, bg=_BG, highlightthickness=0)
    container.pack(fill="both", expand=True)
    container.grid_rowconfigure(0, weight=1)
    container.grid_columnconfigure(0, weight=1)

    tree = ttk.Treeview(container, columns=columns, show="headings",
                        height=height, style="Dark.Treeview")

    v_bar = ttk.Scrollbar(container, orient="vertical",   command=tree.yview,
                          style="Dark.Vertical.TScrollbar")
    h_bar = ttk.Scrollbar(container, orient="horizontal", command=tree.xview,
                          style="Dark.Horizontal.TScrollbar")
    tree.configure(yscrollcommand=v_bar.set, xscrollcommand=h_bar.set)

    tree.grid(row=0, column=0, sticky="nsew")
    v_bar.grid(row=0, column=1, sticky="ns")
    h_bar.grid(row=1, column=0, sticky="ew")

    # ─── Alternate-row tags ───
    tree.tag_configure("even", background=_BG,     foreground=_FG)
    tree.tag_configure("odd",  background=_BG_ALT, foreground=_FG)
    tree.tag_configure("sel",  background=_SEL_BG, foreground=_SEL_FG)

    # ─── Column headings ───
    hfont = tkfont.Font(family="Arial", size=11, weight="bold")
    num_cols = len(columns)
    for i, c in enumerate(columns):
        label = headings[i] if headings else c
        # Minimum width = heading text measured as pixels
        measured = hfont.measure(str(label)) + _COL_PAD
        w = col_widths[i] if col_widths else max(measured, 90)

        tree.heading(c, text=label, anchor="w",
                     command=lambda _c=c: _sort_column(tree, _c, False))
        tree.column(c, width=w, minwidth=60, anchor="w", stretch=True)

    # ─── Smooth macOS trackpad scrolling ───
    def _vscroll(event):
        # event.delta on macOS is continuous (e.g. 3, -7 …)
        tree.yview_scroll(int(-1 * event.delta), "units")

    def _hscroll(event):
        tree.xview_scroll(int(-1 * event.delta), "units")

    tree.bind("<MouseWheel>",       _vscroll)
    tree.bind("<Shift-MouseWheel>", _hscroll)
    tree.bind("<Button-4>",         lambda e: tree.yview_scroll(-3, "units"))
    tree.bind("<Button-5>",         lambda e: tree.yview_scroll( 3, "units"))

    return tree


def apply_row_stripes(tree):
    """Re-tag every row with even/odd for alternating background colours.
    Call this after populating (or refreshing) the tree."""
    for i, iid in enumerate(tree.get_children("")):
        tag = "even" if i % 2 == 0 else "odd"
        tree.item(iid, tags=(tag,))


def autofit_columns(tree):
    """Resize each column to fit the widest cell (heading or data).
    Call this after populating the tree so content is never truncated."""
    dfont = tkfont.Font(family="Arial", size=11)
    hfont = tkfont.Font(family="Arial", size=11, weight="bold")

    for col in tree["columns"]:
        heading_text = tree.heading(col)["text"]
        max_w = hfont.measure(str(heading_text)) + _COL_PAD

        for iid in tree.get_children(""):
            cell_val = str(tree.set(iid, col))
            cell_w   = dfont.measure(cell_val) + _COL_PAD
            if cell_w > max_w:
                max_w = cell_w

        tree.column(col, width=max_w)


def _apply_dark_treeview_style():
    """Configure ttk styles to match the dark CustomTkinter theme."""
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure("Dark.Treeview",
        background=_BG,
        foreground=_FG,
        fieldbackground=_BG,
        borderwidth=0,
        font=_FONT,
        rowheight=_ROW_HEIGHT,
    )
    style.configure("Dark.Treeview.Heading",
        background=_HEADER_BG,
        foreground=_HEADER_FG,
        font=_FONT_BOLD,
        borderwidth=1,
        relief="flat",
        padding=(8, 5),
    )
    style.map("Dark.Treeview",
        background=[("selected", _SEL_BG)],
        foreground=[("selected", _SEL_FG)],
    )
    style.map("Dark.Treeview.Heading",
        background=[("active", "#2980b9")],
    )

    style.configure("Dark.Vertical.TScrollbar",
        background=_SCROLL_BG, troughcolor=_SCROLL_TROUGH,
        borderwidth=0, arrowsize=14,
    )
    style.configure("Dark.Horizontal.TScrollbar",
        background=_SCROLL_BG, troughcolor=_SCROLL_TROUGH,
        borderwidth=0, arrowsize=14,
    )
    style.map("Dark.Vertical.TScrollbar",   background=[("active", "#666")])
    style.map("Dark.Horizontal.TScrollbar", background=[("active", "#666")])


def _sort_column(tree, col, reverse):
    """Sort treeview by column on header click."""
    data = [(tree.set(k, col), k) for k in tree.get_children("")]
    try:
        data.sort(
            key=lambda t: float(
                t[0].replace("£","").replace(",","").replace("h","")
                    .replace(" days","").strip()
            ),
            reverse=reverse,
        )
    except ValueError:
        data.sort(reverse=reverse)

    for idx, (_, k) in enumerate(data):
        tree.move(k, "", idx)

    apply_row_stripes(tree)
    tree.heading(col, command=lambda _c=col: _sort_column(tree, _c, not reverse))
