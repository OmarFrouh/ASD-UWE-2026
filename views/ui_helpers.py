# Shared UI helpers for PAMS views
from tkinter import ttk

def setup_treeview_scroll(parent, columns, headings=None, col_widths=None, height=15):
    """Create a Treeview with vertical + horizontal scrollbars, consistent alignment, and smooth scrolling."""
    tree_frame = parent

    tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=height)

    # ─── Scrollbars ───
    v_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    h_scroll = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

    # ─── Column setup: consistent left-alignment for both headings and data ───
    for i, c in enumerate(columns):
        heading = headings[i] if headings else c
        width = col_widths[i] if col_widths else 110
        tree.heading(c, text=heading, anchor="w", command=lambda _c=c: _treeview_sort_column(tree, _c, False))
        tree.column(c, width=width, anchor="w", minwidth=60)

    # ─── Layout ───
    tree.pack(side="left", fill="both", expand=True)
    v_scroll.pack(side="right", fill="y")
    h_scroll.pack(side="bottom", fill="x")

    # ─── Style: consistent font, row height, and alternating stripe ───
    style = ttk.Style()
    style.configure("Treeview", font=("Arial", 11), rowheight=28)
    style.configure("Treeview.Heading", font=("Arial", 11, "bold"))

    # ─── Smooth mousewheel / trackpad scrolling (macOS + Windows + Linux) ───
    def _on_mousewheel(event):
        if event.delta > 0:
            tree.yview_scroll(-2, "units")
        elif event.delta < 0:
            tree.yview_scroll(2, "units")

    tree.bind("<MouseWheel>", _on_mousewheel)
    tree.bind("<Button-4>", lambda e: tree.yview_scroll(-2, "units"))
    tree.bind("<Button-5>", lambda e: tree.yview_scroll(2, "units"))

    return tree

def _treeview_sort_column(tree, col, reverse):
    """Sort tree contents when a column header is clicked."""
    l = [(tree.set(k, col), k) for k in tree.get_children('')]

    # Try sorting numerically if possible
    try:
        l.sort(key=lambda t: float(t[0].replace('£', '').replace(',', '').replace('h', '').strip()), reverse=reverse)
    except ValueError:
        l.sort(reverse=reverse)

    for index, (val, k) in enumerate(l):
        tree.move(k, '', index)

    # Reverse sort next time
    tree.heading(col, command=lambda _c=col: _treeview_sort_column(tree, _c, not reverse))
