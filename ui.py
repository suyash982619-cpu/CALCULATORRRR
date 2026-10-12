import sys
import threading
import customtkinter as ctk
from calculation import CalculatorEngine

try:
    import winsound
    IS_WINDOWS = True
except ImportError:
    IS_WINDOWS = False

# Palette
BG_WINDOW       = "#090d16"
CARD_SURFACE    = "#131b2e"
SCREEN_BG       = "#0f172a"
GLOW_ACCENT     = "#06b6d4"

# Arcade Button Surfaces
BTN_NUM_BG      = "#1e293b"
BTN_NUM_HOVER   = "#334155"
BTN_FN_BG       = "#182234"
BTN_FN_HOVER    = "#27364f"
BTN_OP_BG       = "#f59e0b"
BTN_OP_HOVER    = "#d97706"
BTN_CLR_BG      = "#e11d48"
BTN_CLR_HOVER   = "#be123c"
BTN_EQ_BG       = "#6366f1"
BTN_EQ_HOVER    = "#4f46e5"

FLASH_NUM       = "#475569"
FLASH_FN        = "#38bdf8"
FLASH_OP        = "#fde047"
FLASH_CLR       = "#fda4af"
FLASH_EQ        = "#a5b4fc"

TXT_WHITE       = "#ffffff"
TXT_LIGHT_SLATE = "#cbd5e1"
TXT_MUTED       = "#64748b"

FONT_MAIN = "Segoe UI, SF Pro Display, Inter, Helvetica"
FONT_MATH = "Cambria Math, Segoe UI Symbol, Arial"


def play_tap_sound(sound_type: str = "normal"):
    def _run():
        if IS_WINDOWS:
            if sound_type == "equals":
                winsound.Beep(987, 35)
                winsound.Beep(1318, 90)
            elif sound_type == "clear":
                winsound.Beep(260, 45)
                winsound.Beep(130, 75)
            elif sound_type == "op":
                for freq in (1200, 950, 700):
                    winsound.Beep(freq, 10)
            elif sound_type == "mode":
                winsound.Beep(523, 20)
                winsound.Beep(659, 20)
                winsound.Beep(784, 35)
            else:
                winsound.Beep(1450, 10)
        else:
            sys.stdout.write('\a')
            sys.stdout.flush()

    threading.Thread(target=_run, daemon=True).start()


class CalculatorUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.engine = CalculatorEngine()

        self.title("calculator goes brr")
        self.geometry("560x750")
        self.resizable(False, False)
        self.configure(fg_color=BG_WINDOW)

        self.buttons_registry = {}

        self._build_top_slider()

        # View Container
        self.view_container = ctk.CTkFrame(self, fg_color="transparent")
        self.view_container.pack(fill="both", expand=True)

        self.calc_view = ctk.CTkFrame(self.view_container, fg_color="transparent")
        self.tools_view = ctk.CTkFrame(self.view_container, fg_color="transparent")

        self._build_calc_ui()
        self._build_tools_ui()

        # Start on Calculator View
        self.calc_view.pack(fill="both", expand=True)
        self._bind_keyboard()

    def _build_top_slider(self):
        top_bar = ctk.CTkFrame(self, fg_color="#0d1424", height=50, corner_radius=0)
        top_bar.pack(fill="x", padx=0, pady=(0, 4))
        top_bar.pack_propagate(False)

        # Tab Segmented Slider Controller
        self.mode_selector = ctk.CTkSegmentedButton(
            top_bar,
            values=["🧮 Calculator", "▦ Converter Hub"],
            command=self._on_view_change,
            font=(FONT_MAIN, 13, "bold"),
            fg_color="#182234",
            selected_color="#6366f1",
            selected_hover_color="#4f46e5",
            unselected_color="#182234",
            unselected_hover_color="#27364f",
            corner_radius=10,
            height=32
        )
        self.mode_selector.set("🧮 Calculator")
        self.mode_selector.pack(expand=True, pady=8)

    def _on_view_change(self, value):
        play_tap_sound("mode")
        if value == "🧮 Calculator":
            self.tools_view.pack_forget()
            self.calc_view.pack(fill="both", expand=True)
        else:
            self.calc_view.pack_forget()
            self.tools_view.pack(fill="both", expand=True)

    # ------------------ CALCULATOR VIEW ------------------
    def _build_calc_ui(self):
        self.shell = ctk.CTkFrame(
            self.calc_view,
            fg_color=CARD_SURFACE,
            corner_radius=22,
            border_width=2.5,
            border_color="#7928ca"
        )
        self.shell.pack(fill="both", expand=True, padx=16, pady=(8, 16))

        self._create_display()
        self._create_keypad()

    def _create_display(self):
        self.display_frame = ctk.CTkFrame(
            self.shell,
            fg_color=SCREEN_BG,
            corner_radius=16,
            border_width=2.0,
            border_color="#00f0ff",
            height=125
        )
        self.display_frame.pack(fill="x", padx=16, pady=(14, 10))
        self.display_frame.pack_propagate(False)

        self.meta_bar = ctk.CTkFrame(self.display_frame, fg_color="transparent")
        self.meta_bar.pack(fill="x", padx=16, pady=(8, 2))

        self.mode_pill = ctk.CTkButton(
            self.meta_bar,
            text=self.engine.mode,
            font=(FONT_MAIN, 11, "bold"),
            text_color="#0f172a",
            fg_color=GLOW_ACCENT,
            hover_color="#22d3ee",
            corner_radius=12,
            width=50,
            height=20,
            command=self._toggle_angle_mode
        )
        self.mode_pill.pack(side="left")

        self.mem_badge = ctk.CTkLabel(
            self.meta_bar,
            text="M",
            font=(FONT_MAIN, 11, "bold"),
            text_color=SCREEN_BG,
            fg_color="#334155",
            corner_radius=6,
            width=24,
            height=20
        )
        self.mem_badge.pack(side="left", padx=(8, 0))

        self.history_label = ctk.CTkLabel(
            self.meta_bar,
            text="",
            font=(FONT_MAIN, 13),
            text_color=TXT_MUTED,
            anchor="e"
        )
        self.history_label.pack(side="right", fill="x", expand=True)

        self.main_display = ctk.CTkLabel(
            self.display_frame,
            text="0",
            font=(FONT_MAIN, 34, "bold"),
            text_color=TXT_WHITE,
            anchor="e"
        )
        self.main_display.pack(fill="x", padx=16, pady=(0, 0))

        self.preview_label = ctk.CTkLabel(
            self.display_frame,
            text="",
            font=(FONT_MAIN, 14, "bold"),
            text_color=GLOW_ACCENT,
            anchor="e"
        )
        self.preview_label.pack(fill="x", padx=16, pady=(0, 4))

    def _create_keypad(self):
        grid = ctk.CTkFrame(self.shell, fg_color="transparent")
        grid.pack(fill="both", expand=True, padx=12, pady=(0, 14))

        for c in range(8):
            grid.columnconfigure(c, weight=1, uniform="col")
        for r in range(8):
            grid.rowconfigure(r, weight=1, uniform="row")

        matrix = [
            [("Rad", "RAD", "fn"), ("Deg", "DEG", "fn"), ("x!", "fact(", "fn"), ("1/x", "1/(", "fn"), ("π", "π", "fn"), ("e", "e", "fn"), ("AC", "AC", "clr"), ("⌫", "DEL", "op_sym")],
            [("sin", "sin(", "fn"), ("cos", "cos(", "fn"), ("tan", "tan(", "fn"), ("log", "log(", "fn"), ("ln", "ln(", "fn"), ("√", "sqrt(", "fn"), ("(", "(", "op"), (")", ")", "op")],
            [("sin⁻¹", "asin(", "fn_sm"), ("cos⁻¹", "acos(", "fn_sm"), ("tan⁻¹", "atan(", "fn_sm"), ("x²", "^2", "fn"), ("x³", "^3", "fn"), ("xʸ", "^", "fn"), ("%", "/100", "op"), ("÷", "÷", "op_sym")],
            [("sinh", "sinh(", "fn_sm"), ("cosh", "cosh(", "fn_sm"), ("tanh", "tanh(", "fn_sm"), ("EXP", "*10^", "fn"), ("7", "7", "num"), ("8", "8", "num"), ("9", "9", "num"), ("×", "×", "op_sym")],
            [("sinh⁻¹", "asinh(", "fn_sm"), ("cosh⁻¹", "acosh(", "fn_sm"), ("tanh⁻¹", "atanh(", "fn_sm"), ("10ˣ", "10^", "fn"), ("4", "4", "num"), ("5", "5", "num"), ("6", "6", "num"), ("−", "−", "op_sym")],
            [("eˣ", "exp(", "fn"), ("∛", "cbrt(", "fn"), ("ʸ√x", "^(1/", "fn_sm"), ("Rand", "RAND", "fn"), ("1", "1", "num"), ("2", "2", "num"), ("3", "3", "num"), ("+", "+", "op_sym")],
            [("MC", "MC", "fn"), ("MR", "MR", "fn"), ("a/b", "/", "fn"), ("S⇔D", "FRAC", "op_sm"), ("0", "0", "num"), (".", ".", "num"), ("±", "NEG", "num"), ("Ans", "Ans", "op")],
            [("M+", "M+", "fn"), ("M-", "M-", "fn")]
        ]

        style_map = {
            "num":    (BTN_NUM_BG, BTN_NUM_HOVER, FLASH_NUM, TXT_WHITE,       "#334155", (FONT_MAIN, 16, "bold")),
            "fn":     (BTN_FN_BG,  BTN_FN_HOVER,  FLASH_FN,  TXT_LIGHT_SLATE, "#26354a", (FONT_MAIN, 13, "bold")),
            "fn_sm":  (BTN_FN_BG,  BTN_FN_HOVER,  FLASH_FN,  TXT_LIGHT_SLATE, "#26354a", (FONT_MAIN, 11, "bold")),
            "op":     (BTN_OP_BG,  BTN_OP_HOVER,  FLASH_OP,  TXT_WHITE,       "#fbbf24", (FONT_MAIN, 15, "bold")),
            "op_sm":  (BTN_OP_BG,  BTN_OP_HOVER,  FLASH_OP,  TXT_WHITE,       "#fbbf24", (FONT_MAIN, 12, "bold")),
            "op_sym": (BTN_OP_BG,  BTN_OP_HOVER,  FLASH_OP,  TXT_WHITE,       "#fbbf24", (FONT_MATH, 18, "bold")),
            "clr":    (BTN_CLR_BG, BTN_CLR_HOVER, FLASH_CLR, TXT_WHITE,       "#f43f5e", (FONT_MAIN, 13, "bold")),
        }

        for r_idx, row in enumerate(matrix):
            for c_idx, item in enumerate(row):
                text, action, btype = item[0], item[1], item[2]
                bg_col, hover_col, flash_col, txt_col, border_col, font_spec = style_map[btype]

                btn = ctk.CTkButton(
                    grid,
                    text=text,
                    font=font_spec,
                    fg_color=bg_col,
                    hover_color=hover_col,
                    text_color=txt_col,
                    corner_radius=10,
                    border_width=1.2,
                    border_color=border_col
                )
                btn.grid(row=r_idx, column=c_idx, padx=3, pady=3, sticky="nsew")

                btn.configure(command=lambda act=action, widget=btn, flash=flash_col, orig=bg_col, b=border_col:
                              self._animate_and_handle(act, widget, flash, orig, b))
                self.buttons_registry[action] = (btn, flash_col, bg_col, border_col)

        eq_btn = ctk.CTkButton(
            grid,
            text="=",
            font=(FONT_MATH, 24, "bold"),
            fg_color=BTN_EQ_BG,
            hover_color=BTN_EQ_HOVER,
            text_color=TXT_WHITE,
            corner_radius=10,
            border_width=1.5,
            border_color="#a855f7"
        )
        eq_btn.grid(row=7, column=2, columnspan=6, padx=3, pady=3, sticky="nsew")
        eq_btn.configure(command=lambda: self._animate_and_handle("=", eq_btn, FLASH_EQ, BTN_EQ_BG, "#a855f7"))
        self.buttons_registry["="] = (eq_btn, FLASH_EQ, BTN_EQ_BG, "#a855f7")

    # ------------------ TOOLS HUB VIEW ------------------
    def _build_tools_ui(self):
        hub_shell = ctk.CTkFrame(
            self.tools_view,
            fg_color=CARD_SURFACE,
            corner_radius=22,
            border_width=2.5,
            border_color="#7928ca"
        )
        hub_shell.pack(fill="both", expand=True, padx=16, pady=(8, 16))

        # Main Hub Scroll/Content Container
        self.hub_container = ctk.CTkFrame(hub_shell, fg_color="transparent")
        self.hub_container.pack(fill="both", expand=True, padx=14, pady=14)

        self._show_hub_grid()

    def _show_hub_grid(self):
        for widget in self.hub_container.winfo_children():
            widget.destroy()

        header = ctk.CTkLabel(
            self.hub_container,
            text="SELECT CONVERTER",
            font=(FONT_MAIN, 16, "bold"),
            text_color=GLOW_ACCENT
        )
        header.pack(pady=(10, 24))

        # 3-Column Icon Grid matching the reference style
        grid = ctk.CTkFrame(self.hub_container, fg_color="transparent")
        grid.pack(expand=True, fill="both")

        for c in range(3):
            grid.columnconfigure(c, weight=1)

        tools = [
            ("🏷️", "Discount", self._open_discount_calculator),
            ("🏛️", "GST", self._open_gst_calculator),
            ("📈", "Interest", self._open_interest_calculator),
        ]

        for i, (icon, label, callback) in enumerate(tools):
            btn_frame = ctk.CTkFrame(grid, fg_color="#182234", corner_radius=16, border_width=1.5, border_color="#334155")
            btn_frame.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")

            btn = ctk.CTkButton(
                btn_frame,
                text=f"{icon}\n\n{label}",
                font=(FONT_MAIN, 14, "bold"),
                text_color=TXT_WHITE,
                fg_color="transparent",
                hover_color="#27364f",
                corner_radius=16,
                height=130,
                command=lambda cb=callback: [play_tap_sound("mode"), cb()]
            )
            btn.pack(fill="both", expand=True)

    # --- Tool 1: GST Calculator ---
    def _open_gst_calculator(self):
        self._create_tool_page("GST Calculator", self._render_gst_form)

    def _render_gst_form(self, container):
        amount_entry = self._create_input_field(container, "Initial Amount (₹ / $):")
        rate_entry = self._create_input_field(container, "GST Rate (%):", default="18")

        inc_var = ctk.BooleanVar(value=False)
        inc_switch = ctk.CTkSwitch(container, text="GST Inclusive", variable=inc_var, font=(FONT_MAIN, 13, "bold"), text_color=TXT_LIGHT_SLATE)
        inc_switch.pack(pady=10)

        result_box = ctk.CTkLabel(container, text="", font=(FONT_MAIN, 14, "bold"), text_color=GLOW_ACCENT, justify="left")
        result_box.pack(pady=14)

        def _calc():
            try:
                base, gst_amt, total = self.engine.calculate_gst(float(amount_entry.get()), float(rate_entry.get()), inc_var.get())
                result_box.configure(text=f"Base Amount: {base}\nGST Amount: {gst_amt}\nTotal Price: {total}")
                play_tap_sound("equals")
            except Exception:
                result_box.configure(text="Invalid Input!")
                play_tap_sound("clear")

        self._create_calc_action_btn(container, "CALCULATE GST", _calc)

    # --- Tool 2: Discount Calculator ---
    def _open_discount_calculator(self):
        self._create_tool_page("Discount Calculator", self._render_discount_form)

    def _render_discount_form(self, container):
        price_entry = self._create_input_field(container, "Original Price:")
        disc_entry = self._create_input_field(container, "Discount (%):")

        result_box = ctk.CTkLabel(container, text="", font=(FONT_MAIN, 14, "bold"), text_color=GLOW_ACCENT, justify="left")
        result_box.pack(pady=14)

        def _calc():
            try:
                saved, final = self.engine.calculate_discount(float(price_entry.get()), float(disc_entry.get()))
                result_box.configure(text=f"You Save: {saved}\nFinal Discounted Price: {final}")
                play_tap_sound("equals")
            except Exception:
                result_box.configure(text="Invalid Input!")
                play_tap_sound("clear")

        self._create_calc_action_btn(container, "CALCULATE DISCOUNT", _calc)

    # --- Tool 3: Interest Calculator ---
    def _open_interest_calculator(self):
        self._create_tool_page("Interest Calculator", self._render_interest_form)

    def _render_interest_form(self, container):
        p_entry = self._create_input_field(container, "Principal Amount:")
        r_entry = self._create_input_field(container, "Annual Interest Rate (%):")
        t_entry = self._create_input_field(container, "Time Period (Years):")

        comp_var = ctk.BooleanVar(value=False)
        comp_switch = ctk.CTkSwitch(container, text="Compound Annually", variable=comp_var, font=(FONT_MAIN, 13, "bold"), text_color=TXT_LIGHT_SLATE)
        comp_switch.pack(pady=10)

        result_box = ctk.CTkLabel(container, text="", font=(FONT_MAIN, 14, "bold"), text_color=GLOW_ACCENT, justify="left")
        result_box.pack(pady=14)

        def _calc():
            try:
                interest, total = self.engine.calculate_interest(float(p_entry.get()), float(r_entry.get()), float(t_entry.get()), comp_var.get())
                result_box.configure(text=f"Total Interest: {interest}\nTotal Maturity Amount: {total}")
                play_tap_sound("equals")
            except Exception:
                result_box.configure(text="Invalid Input!")
                play_tap_sound("clear")

        self._create_calc_action_btn(container, "CALCULATE INTEREST", _calc)

    # --- Helpers for Forms ---
    def _create_tool_page(self, title, form_builder):
        for widget in self.hub_container.winfo_children():
            widget.destroy()

        top_row = ctk.CTkFrame(self.hub_container, fg_color="transparent")
        top_row.pack(fill="x", pady=(4, 16))

        back_btn = ctk.CTkButton(
            top_row, text="← Back", width=70, height=28,
            font=(FONT_MAIN, 12, "bold"), fg_color="#1e293b", hover_color="#334155",
            command=lambda: [play_tap_sound("op"), self._show_hub_grid()]
        )
        back_btn.pack(side="left")

        title_lbl = ctk.CTkLabel(top_row, text=title, font=(FONT_MAIN, 16, "bold"), text_color=TXT_WHITE)
        title_lbl.pack(side="left", padx=20)

        form_builder(self.hub_container)

    def _create_input_field(self, parent, label_text, default=""):
        lbl = ctk.CTkLabel(parent, text=label_text, font=(FONT_MAIN, 13, "bold"), text_color=TXT_LIGHT_SLATE, anchor="w")
        lbl.pack(fill="x", padx=30, pady=(6, 2))

        entry = ctk.CTkEntry(
            parent, font=(FONT_MAIN, 15, "bold"), fg_color="#0f172a",
            border_color="#334155", border_width=1.5, height=36, text_color=TXT_WHITE
        )
        if default:
            entry.insert(0, default)
        entry.pack(fill="x", padx=30, pady=(0, 6))
        return entry

    def _create_calc_action_btn(self, parent, text, command):
        btn = ctk.CTkButton(
            parent, text=text, font=(FONT_MAIN, 14, "bold"),
            fg_color="#6366f1", hover_color="#4f46e5", height=40,
            corner_radius=10, command=command
        )
        btn.pack(fill="x", padx=30, pady=(8, 0))

    # ------------------ ANIMATION & EVENTS ------------------
    def _animate_button_press(self, widget, flash_color, original_color, border_color):
        if not widget:
            return
        widget.configure(fg_color=flash_color, border_width=2.2, border_color="#ffffff")
        self.after(75, lambda: widget.configure(fg_color=original_color, border_width=1.2, border_color=border_color))

    def _pulse_screen_glow(self):
        self.display_frame.configure(border_color="#ffffff", border_width=2.5)
        self.after(140, lambda: self.display_frame.configure(border_color="#00f0ff", border_width=2.0))

    def _animate_and_handle(self, action: str, widget=None, flash_col=None, orig_col=None, border_col=None):
        if not widget and action in self.buttons_registry:
            widget, flash_col, orig_col, border_col = self.buttons_registry[action]

        if widget and flash_col and orig_col:
            self._animate_button_press(widget, flash_col, orig_col, border_col)

        if action == "=":
            play_tap_sound("equals")
            self._pulse_screen_glow()
        elif action in ("AC", "DEL"):
            play_tap_sound("clear")
        elif action in ("DEG", "RAD"):
            play_tap_sound("mode")
        elif action in ("+", "−", "×", "÷", "^", "%"):
            play_tap_sound("op")
        else:
            play_tap_sound("normal")

        self._handle_input(action)

    def _bind_keyboard(self):
        self.bind("<Key>", self._on_key_press)

    def _on_key_press(self, event):
        if self.mode_selector.get() != "🧮 Calculator":
            return
        key = event.char
        keysym = event.keysym

        mapping = {
            "Return": "=", "BackSpace": "DEL", "Escape": "AC",
            "+": "+", "-": "−", "*": "×", "/": "÷", "^": "^"
        }

        action = mapping.get(keysym, mapping.get(key, key if key in "0123456789.()" else None))
        if action:
            self._animate_and_handle(action)

    def _toggle_angle_mode(self):
        new_mode = "RAD" if self.engine.mode == "DEG" else "DEG"
        self._animate_and_handle(new_mode)

    def _handle_input(self, action: str):
        if action == "AC":
            self.engine.clear()
            self.history_label.configure(text="")
            self.preview_label.configure(text="")
        elif action == "DEL":
            self.engine.backspace()
        elif action == "=":
            prev = self.engine.expression
            result = self.engine.evaluate()
            if result != "Error":
                self.history_label.configure(text=f"{prev} =")
                self.preview_label.configure(text="")
        elif action in ("DEG", "RAD"):
            self.engine.toggle_mode(action)
            self.mode_pill.configure(text=action)
        elif action == "NEG":
            self.engine.negate()
        elif action == "RAND":
            self.engine.add_random()
        elif action == "FRAC":
            self.engine.to_fraction_or_decimal()
        elif action == "MC":
            self.engine.memory = 0.0
            self.mem_badge.configure(text_color=SCREEN_BG)
        elif action == "MR":
            self.engine.append(str(self.engine.memory))
        elif action in ("M+", "M-"):
            val = self.engine.evaluate()
            if val != "Error":
                delta = float(val) if action == "M+" else -float(val)
                self.engine.memory += delta
                self.mem_badge.configure(text_color=GLOW_ACCENT)
        else:
            self.engine.append(action)

        current = self.engine.expression
        display_text = current if current else "0"

        if len(display_text) > 16:
            self.main_display.configure(font=(FONT_MAIN, 22, "bold"))
        elif len(display_text) > 11:
            self.main_display.configure(font=(FONT_MAIN, 28, "bold"))
        else:
            self.main_display.configure(font=(FONT_MAIN, 34, "bold"))

        self.main_display.configure(text=display_text)

        if action != "=" and current:
            self.preview_label.configure(text=self.engine.live_preview())
        elif not current:
            self.preview_label.configure(text="")