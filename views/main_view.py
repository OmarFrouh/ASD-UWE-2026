# Student Name: Omar Alfrouh
# Student ID: 24020879

import tkinter as tk
import customtkinter as ctk
from notification_manager import NotificationManager
from views import theme as T
from views.ui_helpers import (
    confirm_dialog, show_error, show_success, show_toast
)


class MainView:
    def __init__(self, root, auth_manager, property_manager, db_manager,
                 current_user, on_logout=None):
        self.root = root
        self.auth_manager = auth_manager
        self.property_manager = property_manager
        self.db_manager = db_manager
        self.current_user = current_user
        self.on_logout = on_logout
        self._current_view = "dashboard"
        self._nav_buttons = {}

        self.notification_manager = NotificationManager(db_manager)

        self.root.title("PAMS")
        self.root.resizable(True, True)
        self.root.minsize(1024, 640)
        w, h = 1280, 760
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry(f"{w}x{h}+{max(0,(sw-w)//2)}+{max(0,(sh-h)//2)}")
        self.root.configure(fg_color=T.BG)

        self._build_header()
        self._build_sidebar()

        # Content area
        self.content_frame = ctk.CTkFrame(self.root,
                                           fg_color=T.BG,
                                           corner_radius=0)
        self.content_frame.pack(side="right", expand=True, fill="both")

        # Global keybindings
        self.root.bind("<F11>",       self._toggle_fullscreen)
        self.root.bind("<Control-l>", lambda e: self.logout())
        self.root.bind("<Control-r>", lambda e: self._refresh_current_view())
        self.root.bind("<Escape>",    lambda e: self._focus_content())

        self.show_view("dashboard")

    # ─── Header ──────────────────────────────────────────────────────────────

    def _build_header(self):
        header = ctk.CTkFrame(self.root,
                               height=T.HEADER_HEIGHT,
                               fg_color=T.SURFACE,
                               corner_radius=0)
        header.pack(side="top", fill="x")
        header.pack_propagate(False)

        # Bottom border
        sep = tk.Frame(self.root, bg=T.BORDER, height=1)
        sep.pack(side="top", fill="x")

        # Left: brand
        left = ctk.CTkFrame(header, fg_color="transparent")
        left.pack(side="left", padx=T.SP_XL, pady=T.SP_M)
        ctk.CTkLabel(left, text="🏢 PAMS", font=T.FONT_H2,
                     text_color=T.TEXT).pack(side="left")
        ctk.CTkLabel(left, text=" · ", font=T.FONT_BODY,
                     text_color=T.BORDER).pack(side="left")
        self.header_page_label = ctk.CTkLabel(
            left, text="Dashboard", font=T.FONT_BODY_B,
            text_color=T.TEXT_MUTED)
        self.header_page_label.pack(side="left")

        # Right: logout · bell · user chip (packed right-to-left)
        right = ctk.CTkFrame(header, fg_color="transparent")
        right.pack(side="right", padx=T.SP_XL, pady=T.SP_M)

        # Logout icon button
        ctk.CTkButton(right, text="🚪", command=self.logout,
                       width=36, height=36, corner_radius=18,
                       fg_color="transparent", hover_color=T.SURFACE_2,
                       text_color=T.TEXT_MUTED, font=("Arial", 16)).pack(
            side="right", padx=(T.SP_S, 0))

        # Bell — with red dot if notifications exist
        self._bell_frame = ctk.CTkFrame(right, fg_color="transparent")
        self._bell_frame.pack(side="right", padx=T.SP_S)
        self._build_bell()

        # User chip: initials circle + username + role
        chip = ctk.CTkFrame(right, fg_color="transparent")
        chip.pack(side="right", padx=(0, T.SP_M))
        username = self.current_user[1]
        role     = self.current_user[3]
        initials = "".join(p[0].upper() for p in username.split()[:2]) or username[0].upper()

        circle = ctk.CTkFrame(chip,
                               width=32, height=32,
                               corner_radius=16,
                               fg_color=T.PRIMARY_MUTED)
        circle.pack(side="left")
        circle.pack_propagate(False)
        ctk.CTkLabel(circle, text=initials, font=T.FONT_CAPTION_B,
                     text_color=T.PRIMARY).place(relx=0.5, rely=0.5, anchor="center")

        info = ctk.CTkFrame(chip, fg_color="transparent")
        info.pack(side="left", padx=(T.SP_S, 0))
        ctk.CTkLabel(info, text=username, font=T.FONT_BODY_B,
                     text_color=T.TEXT).pack(anchor="w")
        ctk.CTkLabel(info, text=role.replace("_", " "),
                     font=T.FONT_CAPTION, text_color=T.TEXT_MUTED).pack(anchor="w")

    def _build_bell(self):
        for w in self._bell_frame.winfo_children():
            w.destroy()
        count = self.notification_manager.get_notification_count()

        btn = ctk.CTkButton(self._bell_frame, text="🔔",
                             width=36, height=36, corner_radius=18,
                             fg_color="transparent", hover_color=T.SURFACE_2,
                             text_color=T.TEXT_MUTED if count == 0 else T.WARNING,
                             font=("Arial", 16),
                             command=self.show_notifications)
        btn.pack()
        if count > 0:
            dot = ctk.CTkLabel(self._bell_frame,
                                text=str(count) if count < 100 else "99+",
                                font=("Arial", 9, "bold"),
                                text_color="#ffffff",
                                fg_color=T.DANGER,
                                corner_radius=10,
                                width=18, height=18)
            dot.place(relx=0.7, rely=0.0, anchor="n")

    def update_notification_badge(self):
        self._build_bell()

    # ─── Notifications dropdown ───────────────────────────────────────────────

    def show_notifications(self):
        notifications = self.notification_manager.get_notifications()
        popup = ctk.CTkToplevel(self.root)
        popup.title("Notifications")
        popup.geometry("440x480")
        popup.resizable(False, False)
        popup.grab_set()
        popup.attributes("-topmost", True)
        popup.configure(fg_color=T.SURFACE)

        # Header
        hdr = ctk.CTkFrame(popup, fg_color="transparent")
        hdr.pack(fill="x", padx=T.SP_XL, pady=T.SP_L)
        ctk.CTkLabel(hdr, text="🔔 Notifications", font=T.FONT_H2,
                     text_color=T.TEXT).pack(side="left")
        count = len(notifications)
        if count:
            ctk.CTkLabel(hdr, text=f"  {count}",
                          font=T.FONT_CAPTION_B,
                          fg_color=T.DANGER, text_color="#fff",
                          corner_radius=10, width=24).pack(side="left", padx=T.SP_S)

        tk.Frame(popup, bg=T.BORDER, height=1).pack(fill="x")

        if not notifications:
            ctk.CTkLabel(popup, text="✓  You're all caught up",
                          font=T.FONT_BODY, text_color=T.TEXT_MUTED).pack(
                expand=True)
        else:
            scroll = ctk.CTkScrollableFrame(popup,
                                             fg_color="transparent",
                                             scrollbar_button_color=T.SURFACE_3)
            scroll.pack(fill="both", expand=True, padx=T.SP_L, pady=T.SP_L)
            for n in notifications:
                row = ctk.CTkFrame(scroll,
                                    fg_color=T.SURFACE_2,
                                    corner_radius=T.RADIUS_SM)
                row.pack(fill="x", pady=T.SP_XS)
                icon = "⚠️" if "overdue" in n["text"].lower() else "⏰"
                ctk.CTkLabel(row, text=icon, font=T.FONT_BODY,
                              width=28).pack(side="left", padx=(T.SP_M, T.SP_S),
                                             pady=T.SP_M)
                ctk.CTkLabel(row, text=n["text"], font=T.FONT_BODY,
                              text_color=T.TEXT, anchor="w",
                              wraplength=340).pack(side="left", fill="x",
                                                    expand=True, pady=T.SP_M)

        tk.Frame(popup, bg=T.BORDER, height=1).pack(fill="x")
        ctk.CTkButton(popup, text="Close", command=popup.destroy,
                       width=120, height=T.BUTTON_HEIGHT,
                       fg_color=T.SURFACE_3, hover_color=T.SURFACE_2,
                       text_color=T.TEXT, corner_radius=T.RADIUS_SM).pack(
            pady=T.SP_L)
        popup.bind("<Escape>", lambda e: popup.destroy())

    # ─── Sidebar ─────────────────────────────────────────────────────────────

    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self.root,
                                     width=T.SIDEBAR_WIDTH,
                                     fg_color=T.SURFACE,
                                     corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Right border
        tk.Frame(self.root, bg=T.BORDER, width=1).pack(side="left", fill="y")

        self._setup_sidebar()

    def _setup_sidebar(self):
        role = self.current_user[3]
        items = [("📊", "Dashboard", "dashboard")]

        if role == "admin":
            items.append(("👥", "Users", "users"))
        if role in ("admin",):
            items.append(("🏠", "Apartments", "apartments"))
        if role in ("admin", "front_desk"):
            items.append(("👤", "Tenants", "tenants"))
        if role in ("admin", "finance_manager"):
            items += [("💰", "Invoices", "invoices"),
                      ("💳", "Payments", "payments")]
        if role in ("admin", "maintenance"):
            items.append(("🔧", "Maintenance", "maintenance"))
        if role in ("admin", "manager"):
            items.append(("📈", "Reports", "reports"))

        nav_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        nav_frame.pack(fill="both", expand=True, pady=(T.SP_XL, 0))

        for i, (icon, label, view_name) in enumerate(items):
            self._make_nav_button(nav_frame, icon, label, view_name)
            # Alt+N binding
            self.root.bind(f"<Alt-Key-{i+1}>",
                           lambda e, v=view_name: self.show_view(v))

        # User card at bottom
        sep = tk.Frame(self.sidebar, bg=T.BORDER, height=1)
        sep.pack(side="bottom", fill="x", pady=0)
        bottom = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        bottom.pack(side="bottom", fill="x", padx=T.SP_M, pady=T.SP_M)
        ctk.CTkLabel(bottom, text=self.current_user[1],
                      font=T.FONT_CAPTION_B, text_color=T.TEXT).pack(anchor="w")
        ctk.CTkLabel(bottom, text=self.current_user[3].replace("_", " "),
                      font=T.FONT_CAPTION, text_color=T.TEXT_MUTED).pack(anchor="w")

    def _make_nav_button(self, parent, icon, label, view_name):
        btn = ctk.CTkButton(
            parent,
            text=f"  {icon}  {label}",
            command=lambda v=view_name: self.show_view(v),
            anchor="w",
            height=40,
            width=T.SIDEBAR_WIDTH - 16,
            font=T.FONT_BODY,
            fg_color="transparent",
            hover_color=T.SURFACE_2,
            text_color=T.TEXT_MUTED,
            corner_radius=T.RADIUS_SM,
        )
        btn.pack(padx=8, pady=2)
        self._nav_buttons[view_name] = btn
        return btn

    def _set_active_nav(self, view_name):
        for v, btn in self._nav_buttons.items():
            if v == view_name:
                btn.configure(fg_color=T.PRIMARY_MUTED,
                               text_color=T.TEXT)
            else:
                btn.configure(fg_color="transparent",
                               text_color=T.TEXT_MUTED)

    # ─── View routing ─────────────────────────────────────────────────────────

    ROLE_PERMISSIONS = {
        "admin":
            ["dashboard", "users", "apartments", "tenants",
             "invoices", "payments", "maintenance", "reports"],
        "front_desk":    ["dashboard", "tenants"],
        "finance_manager": ["dashboard", "invoices", "payments"],
        "maintenance":   ["dashboard", "maintenance"],
        "manager":       ["dashboard", "reports"],
    }

    _VIEW_LABELS = {
        "dashboard": "Dashboard", "users": "Users",
        "apartments": "Apartments", "tenants": "Tenants",
        "invoices": "Invoices", "payments": "Payments",
        "maintenance": "Maintenance", "reports": "Reports",
    }

    def show_view(self, view_name):
        role    = self.current_user[3]
        allowed = self.ROLE_PERMISSIONS.get(role, ["dashboard"])
        if view_name not in allowed:
            show_error(self.root, f"Your role cannot access {view_name}.")
            return

        self._current_view = view_name
        self.header_page_label.configure(
            text=self._VIEW_LABELS.get(view_name, view_name.title()))
        self._set_active_nav(view_name)

        for widget in self.content_frame.winfo_children():
            widget.destroy()

        if view_name == "dashboard":
            self._show_dashboard()
        elif view_name == "users":
            from views.user_view import UserView
            UserView(self.content_frame, self.auth_manager)
        elif view_name == "apartments":
            from views.apartment_view import ApartmentView
            ApartmentView(self.content_frame, self.property_manager)
        elif view_name == "tenants":
            from views.tenant_view import TenantView
            TenantView(self.content_frame, self.db_manager, self.current_user[3])
        elif view_name == "invoices":
            from views.invoice_view import InvoiceView
            InvoiceView(self.content_frame, self.db_manager)
        elif view_name == "payments":
            from views.payment_view import PaymentView
            PaymentView(self.content_frame, self.db_manager)
        elif view_name == "maintenance":
            from views.maintenance_view import MaintenanceView
            MaintenanceView(self.content_frame, self.db_manager)
        elif view_name == "reports":
            from views.report_view import ReportView
            ReportView(self.content_frame, self.db_manager)

    def _refresh_current_view(self):
        self.show_view(self._current_view)

    # ─── Dashboard ────────────────────────────────────────────────────────────

    def _show_dashboard(self):
        from views.ui_helpers import (
            create_page_header, create_kpi_tile, create_card_fill, create_card
        )
        self.update_notification_badge()

        scroll = ctk.CTkScrollableFrame(self.content_frame,
                                         fg_color=T.BG,
                                         scrollbar_button_color=T.SURFACE_3)
        scroll.pack(fill="both", expand=True)

        create_page_header(scroll, "📊 Dashboard",
                            subtitle=f"Welcome back, {self.current_user[1]}")

        # ── KPI row ──
        stats = self.auth_manager.get_dashboard_stats()
        kpi_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        kpi_frame.pack(fill="x", padx=T.SP_XL, pady=(0, T.SP_M))
        kinds = ["primary", "success", "warning", "info"]
        for i, (key, val) in enumerate(stats.items()):
            tile = create_kpi_tile(kpi_frame, label=key, value=val,
                                    kind=kinds[i % len(kinds)])
            tile.grid(row=0, column=i, padx=T.SP_M, pady=T.SP_S, sticky="nsew")
            kpi_frame.grid_columnconfigure(i, weight=1)

        # ── Lower row: Alerts + Activity ──
        row2 = ctk.CTkFrame(scroll, fg_color="transparent")
        row2.pack(fill="both", expand=True, padx=T.SP_XL, pady=T.SP_M)
        row2.grid_columnconfigure(0, weight=1)
        row2.grid_columnconfigure(1, weight=1)

        # Alerts card
        alerts_outer = ctk.CTkFrame(row2, fg_color=T.SURFACE,
                                     corner_radius=T.RADIUS_MD,
                                     border_width=1, border_color=T.BORDER)
        alerts_outer.grid(row=0, column=0, padx=(0, T.SP_S), sticky="nsew")
        ctk.CTkLabel(alerts_outer, text="⚡ Alerts", font=T.FONT_H3,
                      text_color=T.TEXT).pack(anchor="w", padx=T.SP_L, pady=(T.SP_L, T.SP_S))
        tk.Frame(alerts_outer, bg=T.BORDER, height=1).pack(fill="x")
        notifications = self.notification_manager.get_notifications()
        if not notifications:
            ctk.CTkLabel(alerts_outer, text="✓  No active alerts",
                          font=T.FONT_BODY, text_color=T.TEXT_MUTED).pack(
                pady=T.SP_XL)
        else:
            for n in notifications[:8]:
                row = ctk.CTkFrame(alerts_outer,
                                    fg_color=T.SURFACE_2, corner_radius=T.RADIUS_SM)
                row.pack(fill="x", padx=T.SP_M, pady=T.SP_XS)
                ctk.CTkLabel(row, text="⚠️", font=T.FONT_BODY,
                              width=24).pack(side="left", padx=(T.SP_S, T.SP_XS),
                                             pady=T.SP_S)
                ctk.CTkLabel(row, text=n["text"], font=T.FONT_CAPTION,
                              text_color=T.TEXT, anchor="w",
                              wraplength=340).pack(side="left", pady=T.SP_S)

        # Activity card
        info_outer = ctk.CTkFrame(row2, fg_color=T.SURFACE,
                                   corner_radius=T.RADIUS_MD,
                                   border_width=1, border_color=T.BORDER)
        info_outer.grid(row=0, column=1, padx=(T.SP_S, 0), sticky="nsew")
        ctk.CTkLabel(info_outer, text="🔐 Quick Access",
                      font=T.FONT_H3, text_color=T.TEXT).pack(
            anchor="w", padx=T.SP_L, pady=(T.SP_L, T.SP_S))
        tk.Frame(info_outer, bg=T.BORDER, height=1).pack(fill="x")

        role  = self.current_user[3]
        perms = self.ROLE_PERMISSIONS.get(role, [])
        icons_map = {
            "users": "👥 Users", "apartments": "🏠 Apartments",
            "tenants": "👤 Tenants", "invoices": "💰 Invoices",
            "payments": "💳 Payments", "maintenance": "🔧 Maintenance",
            "reports": "📈 Reports",
        }
        for v, label in icons_map.items():
            if v in perms:
                btn = ctk.CTkButton(
                    info_outer, text=label,
                    command=lambda vn=v: self.show_view(vn),
                    anchor="w", height=38,
                    fg_color=T.SURFACE_2, hover_color=T.SURFACE_3,
                    text_color=T.TEXT, font=T.FONT_BODY,
                    corner_radius=T.RADIUS_SM
                )
                btn.pack(fill="x", padx=T.SP_L, pady=T.SP_XS)

    # ─── Logout ───────────────────────────────────────────────────────────────

    def logout(self):
        if confirm_dialog(self.root, "Logout", "Are you sure you want to log out?"):
            if self.on_logout:
                self.on_logout()
            else:
                self.root.destroy()

    # ─── Fullscreen toggle ────────────────────────────────────────────────────

    def _toggle_fullscreen(self, _event=None):
        current = self.root.attributes("-fullscreen")
        self.root.attributes("-fullscreen", not current)

    def _focus_content(self):
        """Escape: move focus away from any entry widget back to the content frame."""
        self.content_frame.focus_set()
