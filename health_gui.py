"""
health_gui.py
TOPICS: tkinter GUI, functions, type conversion, arithmetic operators,
        if/elif/else, f-string formatting, error handling

A desktop GUI version of the Health Metrics Calculator.
Run:  python health_gui.py

The numbers are rough estimates from standard formulas (BMI, Mifflin-St Jeor
BMR, 33 ml of water per kg) and are not medical advice.
"""

# tkinter is Python's built-in toolkit for desktop windows. We import it under
# the short name "tk" so every widget call reads as tk.Label, tk.Button, etc.
import tkinter as tk
# ttk ("themed tk") contains newer-looking widgets. We use it for the dropdown
# (Combobox) and the progress bar, which plain tk doesn't have.
from tkinter import ttk

# ---------- palette ----------
# Colours are stored once as constants so the whole app can be re-themed by
# changing these lines. Each string is a hex colour code: #RRGGBB.
BG = "#0f1117"        # window background
CARD = "#181b24"      # card background
FIELD = "#232735"     # entry background
TEXT = "#e6e8ef"      # main text colour
MUTED = "#8b91a5"     # dimmer text for labels and hints
ACCENT = "#7c9cff"    # button and progress bar colour
# A dictionary maps each BMI category name to the colour that represents it.
# Looking up CATEGORY_COLORS["normal"] gives "#4ade80".
CATEGORY_COLORS = {
    "underweight": "#5cc8ff",
    "normal": "#4ade80",
    "overweight": "#fbbf24",
    "obese": "#f87171",
}


# ---------- calculations (same logic as the console version) ----------
def bmi_category(bmi):
    """Return the category name for a BMI value using the standard cut-offs."""
    # Python checks these conditions top to bottom and stops at the first
    # true one, so each "elif" only runs if the previous test failed.
    if bmi < 18.5:
        return "underweight"
    elif bmi < 25:          # we already know bmi >= 18.5 here
        return "normal"
    elif bmi < 30:          # we already know bmi >= 25 here
        return "overweight"
    else:                   # everything 30 and above
        return "obese"


def compute(weight, height, age, sex):
    """Return (bmi, bmr, water) for the given measurements."""
    # BMI = weight in kg divided by height in metres squared. ** is "power".
    bmi = weight / height ** 2
    # Mifflin-St Jeor BMR formula wants height in cm, so we multiply by 100.
    bmr = 10 * weight + 6.25 * (height * 100) - 5 * age
    # The formula ends with +5 for men and -161 for women. This one-line
    # if/else picks the right number and += adds it to bmr.
    bmr += 5 if sex == "Male" else -161        # Mifflin-St Jeor
    # A common rule of thumb: about 33 ml of water per kg of body weight.
    water = weight * 0.033
    # A function can return several values at once as a tuple.
    return bmi, bmr, water


# ---------- GUI ----------
# Our app is a class that inherits from tk.Tk, the main window class.
# That means HealthApp *is* a window, with all of tk.Tk's abilities plus ours.
class HealthApp(tk.Tk):
    def __init__(self):
        # Always let the parent class (tk.Tk) set itself up first.
        super().__init__()
        # Text shown in the window's title bar.
        self.title("Health Metrics Calculator")
        # Background colour of the window itself.
        self.configure(bg=BG)
        # Our own helper methods (defined below) that set up styles and widgets.
        self._style()
        self._build()
        # Pressing Enter anywhere in the window runs calculate().
        # bind() passes an event object to the function; "lambda _:" is a tiny
        # throwaway function that ignores that event and calls calculate().
        self.bind("<Return>", lambda _: self.calculate())
        # Size the window neatly around its contents.
        self._fit_window()

    def _fit_window(self):
        """Size the window to its content and stop it from shrinking below that."""
        # Force tkinter to lay out all widgets now, so the sizes below are real.
        self.update_idletasks()
        # Ask the window how big it needs to be to show everything.
        w, h = self.winfo_reqwidth(), self.winfo_reqheight()
        # The user can't drag the window smaller than that.
        self.minsize(w, h)
        # Set the starting size to exactly that. geometry wants "WIDTHxHEIGHT".
        self.geometry(f"{w}x{h}")
        # Allow resizing in both directions (width, height).
        self.resizable(True, True)

    def _style(self):
        """Recolour the ttk widgets so they match our dark palette."""
        # A Style object controls how all ttk widgets in this window look.
        s = ttk.Style(self)
        # "clam" is a built-in theme that lets us change colours freely.
        s.theme_use("clam")
        # Base colours for the dropdown box.
        s.configure("TCombobox", fieldbackground=FIELD, background=FIELD,
                    foreground=TEXT, arrowcolor=TEXT, bordercolor=FIELD,
                    lightcolor=FIELD, darkcolor=FIELD)
        # map() sets colours for specific states; our box is "readonly"
        # (the user picks from the list instead of typing), so style that state.
        s.map("TCombobox", fieldbackground=[("readonly", FIELD)],
              foreground=[("readonly", TEXT)])
        # A custom style name for our BMI gauge. "trough" is the empty part,
        # "background" is the filled part.
        s.configure("Gauge.Horizontal.TProgressbar", troughcolor=FIELD,
                    background=ACCENT, bordercolor=FIELD,
                    lightcolor=ACCENT, darkcolor=ACCENT)

    def _build(self):
        """Create every widget in the window."""
        # A Frame is an invisible box used to group widgets. This one adds
        # padding around everything (padx/pady are in pixels).
        outer = tk.Frame(self, bg=BG, padx=28, pady=24)
        # pack() places the widget in its parent. fill="both" + expand=True
        # means "take all available space".
        outer.pack(fill="both", expand=True)

        # Title text. anchor="w" aligns it to the west (left) edge.
        tk.Label(outer, text="Health Metrics", bg=BG, fg=TEXT,
                 font=("Segoe UI", 20, "bold")).pack(anchor="w")
        # Subtitle. pady=(0, 16) means 0 px above and 16 px below.
        tk.Label(outer, text="BMI · BMR · daily water target", bg=BG,
                 fg=MUTED, font=("Segoe UI", 10)).pack(anchor="w", pady=(0, 16))

        # --- input card ---
        # A second frame with the card colour holds the form.
        card = tk.Frame(outer, bg=CARD, padx=20, pady=18)
        # fill="x" stretches it horizontally but not vertically.
        card.pack(fill="x")

        # _entry() (defined below) creates a label + text box and returns the
        # text box, which we keep on self so calculate() can read it later.
        # The last argument is the row number used for positioning.
        self.name = self._entry(card, "Name", 0)
        self.weight = self._entry(card, "Weight (kg)", 1)
        self.height = self._entry(card, "Height (m)", 2)
        self.age = self._entry(card, "Age (years)", 3)

        # The "Sex" label. Inside the card we use grid() instead of pack():
        # grid lays widgets out in rows and columns like a table.
        # Rows 0-7 are used by the four entries (each takes 2 rows), so
        # this label goes on row 8. sticky="w" pins it to the left.
        tk.Label(card, text="Sex", bg=CARD, fg=MUTED,
                 font=("Segoe UI", 9)).grid(row=8, column=0, sticky="w", pady=(10, 2))
        # A dropdown list. state="readonly" stops the user typing free text.
        self.sex = ttk.Combobox(card, values=["Male", "Female"],
                                state="readonly", width=18, font=("Segoe UI", 11))
        # current(0) selects the first option ("Male") as the default.
        self.sex.current(0)
        # sticky="ew" stretches it from east to west, i.e. full width.
        self.sex.grid(row=9, column=0, sticky="ew")

        # An empty label that we fill with a message if the input is invalid.
        # We reuse the "obese" red for errors.
        self.error = tk.Label(card, text="", bg=CARD, fg=CATEGORY_COLORS["obese"],
                              font=("Segoe UI", 9))
        self.error.grid(row=10, column=0, sticky="w", pady=(8, 0))

        # The Calculate button. command= is the function to run when clicked
        # (note: no parentheses, we pass the function itself, not its result).
        # activebackground is the colour while the mouse button is held down.
        btn = tk.Button(card, text="Calculate", command=self.calculate,
                        bg=ACCENT, fg="#0b0d14", activebackground="#9ab3ff",
                        activeforeground="#0b0d14", relief="flat", cursor="hand2",
                        font=("Segoe UI", 11, "bold"), pady=8)
        btn.grid(row=11, column=0, sticky="ew", pady=(14, 0))
        # Let column 0 grow when the window is widened, and never be narrower
        # than 300 px, so the entries stay a comfortable size.
        card.columnconfigure(0, weight=1, minsize=300)

        # --- results card ---
        # Another card frame below the form, with a 14 px gap above it.
        self.result = tk.Frame(outer, bg=CARD, padx=20, pady=18)
        self.result.pack(fill="x", pady=(14, 0))

        # Heading that later changes to "Report for <name>".
        self.heading = tk.Label(self.result, text="Your report", bg=CARD, fg=MUTED,
                                font=("Segoe UI", 13, "bold"))
        self.heading.pack(anchor="w")

        # A small horizontal frame so the big BMI number and its badge sit
        # side by side (pack with side="left" does that).
        row = tk.Frame(self.result, bg=CARD)
        row.pack(fill="x", pady=(12, 6))
        # The large BMI number. Starts as "--" until the user calculates.
        self.bmi_val = tk.Label(row, text="--", bg=CARD, fg=MUTED,
                                font=("Segoe UI", 30, "bold"))
        self.bmi_val.pack(side="left")
        # The category badge next to it. anchor="s" aligns it to the bottom
        # of the row so it lines up with the baseline of the big number.
        self.badge = tk.Label(row, text="BMI", bg=FIELD, fg=MUTED,
                              font=("Segoe UI", 9, "bold"), padx=10, pady=3)
        self.badge.pack(side="left", padx=12, anchor="s", pady=(0, 10))

        # A progress bar used as a BMI gauge from 0 to 40.
        self.gauge = ttk.Progressbar(self.result, maximum=40, length=300,
                                     style="Gauge.Horizontal.TProgressbar")
        self.gauge.pack(fill="x")
        # A row of small numbers under the gauge marking the category edges.
        scale = tk.Frame(self.result, bg=CARD)
        scale.pack(fill="x", pady=(2, 12))
        # A for loop creates one label per number. expand=True shares the
        # width equally between the five labels.
        for t in ("0", "18.5", "25", "30", "40"):
            tk.Label(scale, text=t, bg=CARD, fg=MUTED,
                     font=("Segoe UI", 8)).pack(side="left", expand=True)

        # Two "title on the left, value on the right" rows, made by _stat().
        self.bmr_lbl = self._stat(self.result, "Estimated BMR")
        self.water_lbl = self._stat(self.result, "Water target")

        # A small reminder under everything that these are estimates.
        tk.Label(outer, text="Estimates from standard formulas, not medical advice.",
                 bg=BG, fg=MUTED, font=("Segoe UI", 8)).pack(anchor="w", pady=(12, 0))

    def _entry(self, parent, label, row):
        """Create a labelled text box on the given row and return the text box."""
        # Each entry takes two grid rows: the label on row*2, the box on row*2+1.
        # So row 0 -> grid rows 0 and 1, row 1 -> grid rows 2 and 3, and so on.
        # "10 if row else 0" gives the first entry no top padding and the rest 10 px.
        tk.Label(parent, text=label, bg=CARD, fg=MUTED,
                 font=("Segoe UI", 9)).grid(row=row * 2, column=0, sticky="w",
                                            pady=(10 if row else 0, 2))
        # The text box itself. insertbackground is the cursor colour.
        # highlightthickness/highlightcolor draw a thin accent border when
        # the box has keyboard focus.
        e = tk.Entry(parent, bg=FIELD, fg=TEXT, insertbackground=TEXT,
                     relief="flat", font=("Segoe UI", 11),
                     highlightthickness=1, highlightbackground=FIELD,
                     highlightcolor=ACCENT)
        # ipady adds inner padding so the box is taller than the text.
        e.grid(row=row * 2 + 1, column=0, sticky="ew", ipady=6)
        # Hand the box back so the caller can store it and read its value later.
        return e

    def _stat(self, parent, title):
        """Create a 'title ... value' row and return the value label."""
        # A one-line frame holding the two labels.
        f = tk.Frame(parent, bg=CARD)
        f.pack(fill="x", pady=3)
        # Title on the left.
        tk.Label(f, text=title, bg=CARD, fg=MUTED,
                 font=("Segoe UI", 10)).pack(side="left")
        # Value on the right, starting as "--".
        v = tk.Label(f, text="--", bg=CARD, fg=TEXT, font=("Segoe UI", 11, "bold"))
        v.pack(side="right")
        # Return the value label so calculate() can update its text.
        return v

    def calculate(self):
        """Read the form, validate it, run the maths and show the results."""
        # Anything inside "try" that raises a ValueError jumps to "except".
        # float("abc") and int("") both raise ValueError, which is how we
        # catch empty or non-numeric input.
        try:
            # .get() reads the text from an Entry. .strip() removes spaces.
            # "or 'You'" means: if the name is empty, use "You" instead.
            name = self.name.get().strip() or "You"
            # Convert the typed text to numbers. float allows decimals.
            weight = float(self.weight.get())
            height = float(self.height.get())
            # int() for age: a whole number.
            age = int(self.age.get())
        except ValueError:
            # Show a message in the red error label and stop here.
            self.error.config(text="Please enter numbers for weight, height and age.")
            return

        # If height is bigger than 3 the user almost certainly typed
        # centimetres (175) rather than metres (1.75), so convert it.
        if height > 3:            # someone typed 175 instead of 1.75
            height = height / 100
        # Reject values outside a realistic range. "20 <= weight <= 400" is
        # Python shorthand for "weight is between 20 and 400 inclusive".
        # "not (...)" flips the result: we enter the block when a check fails.
        if not (20 <= weight <= 400 and 0.5 <= height <= 2.6 and 1 <= age <= 120):
            self.error.config(text="Please check the values: weight 20–400 kg, "
                                   "height 0.5–2.6 m, age 1–120.")
            return
        # Input is fine: clear any old error message.
        self.error.config(text="")

        # Run the maths. The three returned values are unpacked into
        # three separate variables in one line.
        bmi, bmr, water = compute(weight, height, age, self.sex.get())
        # Work out which category and colour to use.
        cat = bmi_category(bmi)
        color = CATEGORY_COLORS[cat]

        # Update the results card. .config() changes a widget's options
        # after it has been created. .title() capitalises each word.
        self.heading.config(text=f"Report for {name.title()}", fg=TEXT)
        # f"{bmi:.1f}" formats the number with exactly one decimal place.
        self.bmi_val.config(text=f"{bmi:.1f}", fg=color)
        # Badge shows the category in capitals on a coloured background.
        self.badge.config(text=cat.upper(), bg=color, fg="#0b0d14")
        # Recolour the gauge's filled part to match the category.
        ttk.Style(self).configure("Gauge.Horizontal.TProgressbar",
                                  background=color, lightcolor=color, darkcolor=color)
        # Fill the gauge. min(bmi, 40) caps it so very high BMIs don't overflow.
        self.gauge["value"] = min(bmi, 40)
        # :.0f rounds to a whole number, :.1f keeps one decimal.
        self.bmr_lbl.config(text=f"{bmr:.0f} kcal/day")
        self.water_lbl.config(text=f"{water:.1f} L/day")


# This block only runs when the file is executed directly (python health_gui.py),
# not when it is imported by another script. That lets tests import compute()
# and bmi_category() without a window popping up.
if __name__ == "__main__":
    # Create the window and start tkinter's event loop, which waits for
    # clicks and key presses until the window is closed.
    HealthApp().mainloop()
