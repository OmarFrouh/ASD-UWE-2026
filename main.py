import tkinter as tk
import customtkinter as ctk

# Note: If customtkinter is not installed, run: pip install customtkinter
# Fallback to standard tkinter if needed, but this template uses modern styling.

def main():
    # Setup the main window
    ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
    ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

    root = ctk.CTk()
    root.title("PAMS - Group Project")
    root.geometry("600x400")

    # Create a nice header
    header_frame = ctk.CTkFrame(root)
    header_frame.pack(pady=20, padx=20, fill="x")

    label = ctk.CTkLabel(header_frame, text="Paragon Apartment Management System", font=("Arial", 24, "bold"))
    label.pack(pady=10)

    sub_label = ctk.CTkLabel(header_frame, text="Week 1: Initial Setup Complete", font=("Arial", 14))
    sub_label.pack(pady=5)

    # Status indicator
    status_label = ctk.CTkLabel(root, text="System Status: ONLINE", text_color="green")
    status_label.pack(pady=20)

    # Quit button
    quit_button = ctk.CTkButton(root, text="Exit Application", command=root.quit)
    quit_button.pack(pady=10)

    # Start the loop
    root.mainloop()

if __name__ == "__main__":
    main()
