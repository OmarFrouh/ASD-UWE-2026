# Student Name: Omar Alfrouh
# Student ID: 24020879

import customtkinter as ctk
from report_manager import ReportManager
from views.ui_helpers import setup_treeview_scroll, autofit_columns, apply_row_stripes


class ReportView:
    def __init__(self, parent, db_manager):
        self.db_manager = db_manager
        self.report_manager = ReportManager(db_manager)

        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame, text="📈 Reports", font=("Arial", 22, "bold")).pack(pady=(0, 10))

        # Tab view for 3 report types
        self.tabview = ctk.CTkTabview(frame)
        self.tabview.pack(fill="both", expand=True)

        tab_occupancy = self.tabview.add("Occupancy")
        tab_financial = self.tabview.add("Financial Summary")
        tab_maintenance = self.tabview.add("Maintenance Costs")

        self.build_occupancy_tab(tab_occupancy)
        self.build_financial_tab(tab_financial)
        self.build_maintenance_tab(tab_maintenance)

    # ─── OCCUPANCY REPORT ───────────────────────────────────
    def build_occupancy_tab(self, tab):
        # Filter bar
        filter_frame = ctk.CTkFrame(tab)
        filter_frame.pack(fill="x", padx=10, pady=(10, 5))

        ctk.CTkLabel(filter_frame, text="Filter by City:", font=("Arial", 13)).pack(side="left", padx=(10, 5))
        cities = ["All"] + self.report_manager.get_cities()
        self.occ_city_filter = ctk.CTkComboBox(filter_frame, values=cities, width=180,
                                                command=lambda _: self.refresh_occupancy())
        self.occ_city_filter.pack(side="left", padx=5)
        self.occ_city_filter.set("All")

        # Summary cards
        self.occ_summary_frame = ctk.CTkFrame(tab)
        self.occ_summary_frame.pack(fill="x", padx=10, pady=5)

        # Data table
        tree_frame = ctk.CTkFrame(tab, fg_color="transparent")
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)

        cols = ("Unit", "Address", "City", "Rooms", "Rent", "Status")
        self.occ_tree = setup_treeview_scroll(tree_frame, columns=cols, height=12)

        self.refresh_occupancy()

    def refresh_occupancy(self):
        city = self.occ_city_filter.get()

        # Update summary cards
        for w in self.occ_summary_frame.winfo_children():
            w.destroy()
        summary = self.report_manager.get_occupancy_summary(city)
        cards = [
            ("Total", str(summary["total"])),
            ("Occupied", str(summary["occupied"])),
            ("Vacant", str(summary["vacant"])),
            ("Rate", f"{summary['occupancy_rate']}%"),
        ]
        for i, (label, val) in enumerate(cards):
            card = ctk.CTkFrame(self.occ_summary_frame, corner_radius=10)
            card.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")
            self.occ_summary_frame.grid_columnconfigure(i, weight=1)
            ctk.CTkLabel(card, text=val, font=("Arial", 28, "bold")).pack(pady=(15, 3))
            ctk.CTkLabel(card, text=label, font=("Arial", 12), text_color="gray").pack(pady=(0, 15))

        # Update table
        for item in self.occ_tree.get_children():
            self.occ_tree.delete(item)
        for apt in self.report_manager.get_occupancy_report(city):
            self.occ_tree.insert("", "end", values=(
                apt[0], apt[1], apt[2], apt[3], f"£{apt[4]:.2f}", apt[5]))
        apply_row_stripes(self.occ_tree)
        autofit_columns(self.occ_tree)

    # ─── FINANCIAL SUMMARY ──────────────────────────────────
    def build_financial_tab(self, tab):
        # Summary cards
        self.fin_summary_frame = ctk.CTkFrame(tab)
        self.fin_summary_frame.pack(fill="x", padx=10, pady=10)

        # Per-tenant breakdown table
        tree_frame = ctk.CTkFrame(tab, fg_color="transparent")
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)

        cols = ("Tenant", "Total Invoiced", "Total Paid", "Outstanding")
        self.fin_tree = setup_treeview_scroll(tree_frame, columns=cols, height=12)

        ctk.CTkButton(tab, text="🔄 Refresh", command=self.refresh_financial).pack(pady=5)
        self.refresh_financial()

    def refresh_financial(self):
        # Update summary cards
        for w in self.fin_summary_frame.winfo_children():
            w.destroy()
        summary = self.report_manager.get_financial_summary()
        cards = [
            ("Collected", f"£{summary['collected']:.2f}"),
            ("Pending", f"£{summary['pending']:.2f}"),
            ("Total Invoiced", f"£{summary['total_invoiced']:.2f}"),
            ("Collection Rate", f"{summary['collection_rate']}%"),
        ]
        for i, (label, val) in enumerate(cards):
            card = ctk.CTkFrame(self.fin_summary_frame, corner_radius=10)
            card.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")
            self.fin_summary_frame.grid_columnconfigure(i, weight=1)
            ctk.CTkLabel(card, text=val, font=("Arial", 24, "bold")).pack(pady=(15, 3))
            ctk.CTkLabel(card, text=label, font=("Arial", 12), text_color="gray").pack(pady=(0, 15))

        # Update table
        for item in self.fin_tree.get_children():
            self.fin_tree.delete(item)
        for row in self.report_manager.get_financial_breakdown():
            self.fin_tree.insert("", "end", values=(
                row[0], f"£{row[1]:.2f}", f"£{row[2]:.2f}", f"£{row[3]:.2f}"))
        apply_row_stripes(self.fin_tree)
        autofit_columns(self.fin_tree)

    # ─── MAINTENANCE COST REPORT ────────────────────────────
    def build_maintenance_tab(self, tab):
        # Filter bar
        filter_frame = ctk.CTkFrame(tab)
        filter_frame.pack(fill="x", padx=10, pady=(10, 5))

        ctk.CTkLabel(filter_frame, text="Filter by City:", font=("Arial", 13)).pack(side="left", padx=(10, 5))
        cities = ["All"] + self.report_manager.get_cities()
        self.mnt_city_filter = ctk.CTkComboBox(filter_frame, values=cities, width=180,
                                                command=lambda _: self.refresh_maintenance())
        self.mnt_city_filter.pack(side="left", padx=5)
        self.mnt_city_filter.set("All")

        # Summary cards
        self.mnt_summary_frame = ctk.CTkFrame(tab)
        self.mnt_summary_frame.pack(fill="x", padx=10, pady=5)

        # Data table
        tree_frame = ctk.CTkFrame(tab, fg_color="transparent")
        tree_frame.pack(fill="both", expand=True, padx=10, pady=5)

        cols = ("Unit", "City", "Tickets", "Total Cost", "Total Hours")
        self.mnt_tree = setup_treeview_scroll(tree_frame, columns=cols, height=12)

        self.refresh_maintenance()

    def refresh_maintenance(self):
        city = self.mnt_city_filter.get()

        # Update summary
        for w in self.mnt_summary_frame.winfo_children():
            w.destroy()
        summary = self.report_manager.get_maintenance_cost_summary()
        cards = [
            ("Total Spend", f"£{summary['total_cost']:.2f}"),
            ("Avg Cost", f"£{summary['avg_cost']:.2f}"),
            ("Total Hours", f"{summary['total_hours']:.1f}h"),
            ("Completed", str(summary["completed_tickets"])),
        ]
        for i, (label, val) in enumerate(cards):
            card = ctk.CTkFrame(self.mnt_summary_frame, corner_radius=10)
            card.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")
            self.mnt_summary_frame.grid_columnconfigure(i, weight=1)
            ctk.CTkLabel(card, text=val, font=("Arial", 24, "bold")).pack(pady=(15, 3))
            ctk.CTkLabel(card, text=label, font=("Arial", 12), text_color="gray").pack(pady=(0, 15))

        # Update table
        for item in self.mnt_tree.get_children():
            self.mnt_tree.delete(item)
        for row in self.report_manager.get_maintenance_cost_report(city):
            self.mnt_tree.insert("", "end", values=(
                row[0], row[1], row[2], f"£{row[3]:.2f}", f"{row[4]:.1f}h"))
        apply_row_stripes(self.mnt_tree)
        autofit_columns(self.mnt_tree)
