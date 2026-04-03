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
        tree.heading(c, text=heading)
        tree.column(c, width=width)

    tree.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Bind mousewheel / trackpad scrolling (macOS + Windows + Linux)
    def _on_mousewheel(event):
        if platform.system() == "Darwin":
            tree.yview_scroll(-1 * event.delta, "units")
        else:
            tree.yview_scroll(-1 * (event.delta // 120), "units")

    tree.bind("<MouseWheel>", _on_mousewheel)
    tree.bind("<Button-4>", lambda e: tree.yview_scroll(-3, "units"))
    tree.bind("<Button-5>", lambda e: tree.yview_scroll(3, "units"))

    return tree
