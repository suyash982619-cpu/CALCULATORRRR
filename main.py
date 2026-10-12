import customtkinter as ctk
from ui import CalculatorUI

def main():
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")
    app = CalculatorUI()
    app.mainloop()

if __name__ == "__main__":
    main()