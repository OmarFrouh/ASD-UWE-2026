# Shared UI helpers for PAMS views
import tkinter as tk
from tkinter import ttk


def setup_treeview_scroll(parent, columns, headings=None, col_widths=None, height=15):
    """Create a dark-themed Treeview with proper scrollbars, auto-stretching columns,
    and smooth scrolling that matches the CustomTkinter dark UI."""

    # ─── Apply dark theme styling (idempotent — safe to call many times) ───
    _apply_dark_treeview_style()

    # ─── Container frame with grid for correct scrollbar placement ───
    container = tk.Frame(parent, bg="#2b2b2b", highlightthickness=0)
    container.pack(fill="both", expand=True)
    container.grid_rowconfigure(0, weight=1)
    container.grid_columnconfigure(0, weight=1)

    tree = ttk.Treeview(container, columns=columns, show="headings",
                        height=height, style="Dark.Treeview")

    v_scroll = ttk.Scrollbar(container, orient="vertical", command=tree.yview,
                              style="Dark.Vertical.TScrollbar")
    h_scroll = ttk.Scrollbar(container, orient="horizontal", command=tree.xview,
                              style="Dark.Horizontal.TScrollbar")
    tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

    # ─── Grid layout: tree + scrollbars ───
    tree.grid(row=0, column=0, sticky="nsew")
    v_scroll.grid(row=0, column=1, sticky="ns")
    h_scroll.grid(row=1, column=0, sticky="ew")

    # ─── Column setup: auto-stretch with sensible minimums ───
    num_cols = len(columns)
    for i, c in enumerate(columns):
        heading_text = headings[i] if headings else c
        width = col_widths[i] if col_widths else max(120, 800 // num_cols)

        tree.heading(c, text=heading_text, anchor="w",
                     command=lambda _c=c: _treeview_sort_column(tree, _c, False))
        tree.column(c, width=width, minwidth=80, anchor="w", stretch=True)

    # ─── Smooth scrolling (macOS trackpad + mouse wheel) ───
    def _on_mousewheel(event):
        # macOS trackpad gives continuous small deltas; scale them for smoothness
        if hasattr(event, 'delta'):
            # macOS: delta is in pixels, scroll proportionally
            tree.yview_scroll(int(-1 * (event.delta / 3)), "units")

    def _on_shift_mousewheel(event):
        # Shift+scroll = horizontal
        if hasattr(event, 'delta'):
            tree.xview_scroll(int(-1 * (event.delta / 3)), "units")

    tree.bind("<MouseWheel>", _on_mousewheel)
    tree.bind("<Shift-MouseWheel>", _on_shift_mousewheel)
    # Linux
    tree.bind("<Button-4>", lambda e: tree.yview_scroll(-3, "units"))
    tree.bind("<Button-5>", lambda e: tree.yview_scroll(3, "units"))

    return tree


def _apply_dark_treeview_style():
    """Configure ttk styles to match the dark CustomTkinter theme."""
    style = ttk.Style()

    # Prevent re-applying (check if already configured)
    if "Dark.Treeview" in style.theme_names():
        return

    # Use 'clam' theme as base — it's the most customizable
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    # ─── Dark Treeview ───
    style.configure("Dark.Treeview",
        background="#333333",
        foreground="#e0e0e0",
        fieldbackground="#333333",
        borderwidth=0,
        font=("Arial", 11),
        rowheight=30,
    )

    style.configure("Dark.Treeview.Heading",
        background="#1f538d",
        foreground="white",
        font=("Arial", 11, "bold"),
        borderwidth=1,
        relief="flat",
        padding=(8, 4),
    )

    style.map("Dark.Treeview",
        background=[("selected", "#1f6aa5")],
        foreground=[("selected", "white")],
    )

    style.map("Dark.Treeview.Heading",
        background=[("active", "#2980b9")],
    )

    # ─── Tag for alternating row stripes ───
    # (Applied in tree.insert calls — see _add_stripe_tags)

    # ─── Scrollbar styling ───
    style.configure("Dark.Vertical.TScrollbar",
        background="#444444",
        troughcolor="#2b2b2b",
        borderwidth=0,
        arrowsize=14,
    )
    style.configure("Dark.Horizontal.TScrollbar",
        background="#444444",
        troughcolor="#2b2b2b",
        borderwidth=0,
        arrowsize=14,
    )
    style.map("Dark.Vertical.TScrollbar",
        background=[("active", "#555555")],
    )
    style.map("Dark.Horizontal.TScrollbar",
        background=[("active", "#555555")],
    )


def _treeview_sort_column(tree, col, reverse):
    """Sort tree contents when a column header is clicked."""
    data = [(tree.set(k, col), k) for k in tree.get_children('')]

    # Try numeric sort first
    try:
        data.sort(key=lambda t: float(
            t[0].replace('£', '').replace(',', '').replace('h', '').replace(' days', '').strip()
        ), reverse=reverse)
    except ValueError:
        data.sort(reverse=reverse)

    for index, (val, k) in enumerate(data):
        tree.move(k, '', index)

    tree.heading(col, command=lambda _c=col: _treeview_sort_column(tree, _c, not reverse))
