# Shared UI helpers for PAMS views
from tkinter import ttk
import platform

def setup_treeview_scroll(parent, columns, headings=None, col_widths=None, height=15):
    """Create a Treeview with vertical scrollbar and mousewheel/trackpad support."""
    tree_frame = parent
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=height)
    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)

    for i, c in enumerate(columns):
        heading = headings[i] if headings else c
        width = col_widths[i] if col_widths else 100
        tree.heading(c, text=heading, command=lambda _c=c: _treeview_sort_column(tree, _c, False))
        tree.column(c, width=width)

    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Bind mousewheel / trackpad scrolling (macOS + Windows + Linux)
    def _on_mousewheel(event):
        # Normalize delta reading. macOS gives variable small/large ints, Windows gives 120 multiples.
        # We scroll exactly 1 unit per event trigger for smooth trackpad UX
        if event.delta > 0:
            tree.yview_scroll(-1, "units")
        elif event.delta < 0:
            tree.yview_scroll(1, "units")

    tree.bind("<MouseWheel>", _on_mousewheel)
    tree.bind("<Button-4>", lambda e: tree.yview_scroll(-1, "units"))
    tree.bind("<Button-5>", lambda e: tree.yview_scroll(1, "units"))

    return tree

def _treeview_sort_column(tree, col, reverse):
    """Sort tree contents when a column header is clicked."""
    l = [(tree.set(k, col), k) for k in tree.get_children('')]
    
    # Try sorting numerically if possible
    try:
        l.sort(key=lambda t: float(t[0].replace('£', '').replace(',', '').strip()), reverse=reverse)
    except ValueError:
        l.sort(reverse=reverse)

    for index, (val, k) in enumerate(l):
        tree.move(k, '', index)

    # Reverse sort next time
    tree.heading(col, command=lambda _c=col: _treeview_sort_column(tree, _c, not reverse))
