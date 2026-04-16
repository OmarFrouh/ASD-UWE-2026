# Student Name: Omar Alfrouh
# Student ID: 24020879

import customtkinter as ctk
from views import theme as T
from views.ui_helpers import show_error


class LoginView:
    def __init__(self, root, auth_manager, on_login_success):
        self.root = root
        self.auth_manager = auth_manager
        self.on_login_success = on_login_success

        self.root.title("PAMS — Login")
        w, h = 480, 580
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry(f"{w}x{h}+{max(0,(sw-w)//2)}+{max(0,(sh-h)//2)}")
        self.root.resizable(False, False)
        self.root.configure(fg_color=T.BG)

        # ── Outer wrapper centres the card vertically ──
        wrapper = ctk.CTkFrame(root, fg_color="transparent")
        wrapper.place(relx=0.5, rely=0.5, anchor="center")

        # ── Brand block ──
        brand = ctk.CTkFrame(wrapper, fg_color="transparent")
        brand.pack(pady=(0, T.SP_XL))
        ctk.CTkLabel(brand, text="🏢", font=("Arial", 48)).pack()
        ctk.CTkLabel(brand, text="PAMS", font=T.FONT_DISPLAY,
                     text_color=T.TEXT).pack()
        ctk.CTkLabel(brand, text="Paragon Apartment Management",
                     font=T.FONT_CAPTION, text_color=T.TEXT_MUTED).pack()

        # ── Form card ──
        card = ctk.CTkFrame(wrapper,
                            fg_color=T.SURFACE,
                            corner_radius=T.RADIUS_LG,
                            border_width=1, border_color=T.BORDER,
                            width=360)
        card.pack(padx=T.SP_XL)
        card.grid_propagate(False)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(padx=T.SP_2XL, pady=T.SP_2XL, fill="both", expand=True)

        ctk.CTkLabel(inner, text="Sign in", font=T.FONT_H2,
                     text_color=T.TEXT).pack(anchor="w", pady=(0, T.SP_XL))

        # Username
        ctk.CTkLabel(inner, text="Username", font=T.FONT_BODY,
                     text_color=T.TEXT_MUTED).pack(anchor="w")
        self.username_entry = ctk.CTkEntry(
            inner, placeholder_text="Enter username",
            width=300, height=T.INPUT_HEIGHT,
            fg_color=T.SURFACE_3, border_color=T.BORDER, text_color=T.TEXT)
        self.username_entry.pack(pady=(T.SP_XS, T.SP_M), fill="x")

        # Password
        ctk.CTkLabel(inner, text="Password", font=T.FONT_BODY,
                     text_color=T.TEXT_MUTED).pack(anchor="w")
        self.password_entry = ctk.CTkEntry(
            inner, placeholder_text="Enter password",
            show="•", width=300, height=T.INPUT_HEIGHT,
            fg_color=T.SURFACE_3, border_color=T.BORDER, text_color=T.TEXT)
        self.password_entry.pack(pady=(T.SP_XS, T.SP_XL), fill="x")

        # Login button
        ctk.CTkButton(
            inner, text="Login", command=self.handle_login,
            width=300, height=40,
            fg_color=T.PRIMARY, hover_color=T.PRIMARY_HOVER,
            text_color=T.TEXT, font=T.FONT_H3,
            corner_radius=T.RADIUS_SM
        ).pack(fill="x")

        # Status band — reserved 36 px, prevents layout shift
        self.status_label = ctk.CTkLabel(inner, text="",
                                          font=T.FONT_CAPTION,
                                          text_color=T.DANGER,
                                          height=36)
        self.status_label.pack(pady=(T.SP_S, 0))

        # ── Footer ──
        ctk.CTkLabel(wrapper, text="© 2026 · Group 28 · UWE Bristol",
                     font=T.FONT_CAPTION, text_color=T.TEXT_SUBTLE).pack(
            pady=(T.SP_XL, 0))

        # ── Bindings ──
        self.username_entry.bind("<Return>",  lambda e: self.handle_login())
        self.password_entry.bind("<Return>",  lambda e: self.handle_login())
        self.username_entry.bind("<Tab>",     lambda e: self.password_entry.focus_set())
        self.root.bind("<Escape>", self._clear_fields)
        self.username_entry.focus_set()

    def _clear_fields(self, _event=None):
        self.username_entry.delete(0, "end")
        self.password_entry.delete(0, "end")
        self.status_label.configure(text="")
        self.username_entry.focus_set()

    def handle_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username or not password:
            self.status_label.configure(text="Please enter both fields",
                                         text_color=T.WARNING)
            return

        user = self.auth_manager.login(username, password)
        if user:
            self.status_label.configure(text="Login successful!",
                                         text_color=T.SUCCESS)
            self.on_login_success(user)
        else:
            self.status_label.configure(text="Invalid username or password",
                                         text_color=T.DANGER)
