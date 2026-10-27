"""theme.py - colours, fonts and small helper widgets (Apple-style look)."""
import tkinter as tk
from tkinter import ttk

BG = "#f5f5f7"          # page background
PRIMARY = "#0071e3"     # Apple blue
DARK = "#1d1d1f"        # header bar
GREEN = "#34c759"
RED = "#ff3b30"
ORANGE = "#ff9f0a"
GRAY = "#86868b"
TEXT = "#1d1d1f"
BORDER = "#e0e0e5"
SOFT = "#e8e8ed"        # light grey button
FONT = "Segoe UI"
FONT_BOLD = "Segoe UI Semibold"


def darken(color):
    """Make a hex colour a bit darker (used for the button hover effect)."""
    r, g, b = (int(color[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02x%02x%02x" % (int(r * 0.9), int(g * 0.9), int(b * 0.9))


def apply_style(root):
    """Give all ttk widgets (tabs, tables, inputs, progress bar) a clean look."""
    s = ttk.Style(root)
    s.theme_use("clam")
    s.configure("TFrame", background=BG)

    # tabs
    s.configure("TNotebook", background=BG, borderwidth=0, bordercolor=BG,
                lightcolor=BG, darkcolor=BG)
    s.configure("TNotebook.Tab", font=(FONT_BOLD, 11), padding=(26, 10),
                background=SOFT, foreground=GRAY, borderwidth=0,
                bordercolor=BG, lightcolor=SOFT, darkcolor=SOFT)
    s.map("TNotebook.Tab", background=[("selected", BG)],
          foreground=[("selected", PRIMARY)],
          lightcolor=[("selected", BG)], darkcolor=[("selected", BG)])

    # tables
    s.configure("Treeview", font=(FONT, 10), rowheight=34, background="white",
                fieldbackground="white", foreground=TEXT, borderwidth=0)
    s.layout("Treeview", [("Treeview.treearea", {"sticky": "nswe"})])   # no dark border
    s.map("Treeview", background=[("selected", "#d6e9ff")],
          foreground=[("selected", TEXT)])
    s.configure("Treeview.Heading", font=(FONT_BOLD, 9), background="#fafafc",
                foreground=GRAY, padding=9, relief="flat", borderwidth=0,
                lightcolor="#fafafc", darkcolor="#fafafc", bordercolor=BORDER)
    s.map("Treeview.Heading", background=[("active", "#fafafc")])

    # inputs
    for name in ("TEntry", "TCombobox", "TSpinbox"):
        s.configure(name, padding=7, fieldbackground="white", background="white",
                    foreground=TEXT, arrowcolor=GRAY, bordercolor="#d2d2d7",
                    lightcolor="#d2d2d7", darkcolor="#d2d2d7")
        s.map(name, bordercolor=[("focus", PRIMARY)], lightcolor=[("focus", PRIMARY)],
              darkcolor=[("focus", PRIMARY)])
    s.map("TCombobox", fieldbackground=[("readonly", "white")],
          selectbackground=[("readonly", "white")],
          selectforeground=[("readonly", TEXT)])

    s.configure("Vertical.TScrollbar", background="#d2d2d7", troughcolor="white",
                bordercolor="white", arrowcolor=GRAY, relief="flat")
    for name, color in (("green", GREEN), ("red", RED)):
        s.configure(f"{name}.Horizontal.TProgressbar", troughcolor=SOFT,
                    background=color, thickness=12, borderwidth=0,
                    lightcolor=color, darkcolor=color, bordercolor=SOFT)


class PillButton(tk.Canvas):
    """A rounded 'pill' shaped button drawn on a Canvas."""

    def __init__(self, parent, text, command, color, fg="white", width=140, height=38):
        try:
            bg = parent.cget("bg")
        except tk.TclError:
            bg = "white"
        super().__init__(parent, width=width, height=height, bg=bg,
                         highlightthickness=0, cursor="hand2")
        self.command = command
        self.create_oval(0, 0, height, height, fill=color, outline=color, tags="shape")
        self.create_oval(width - height, 0, width, height, fill=color, outline=color, tags="shape")
        self.create_rectangle(height / 2, 0, width - height / 2, height,
                              fill=color, outline=color, tags="shape")
        self.create_text(width / 2, height / 2, text=text, fill=fg, font=(FONT_BOLD, 10))
        self.bind("<Button-1>", lambda e: self.command())
        self.bind("<Enter>", lambda e: self.itemconfig("shape", fill=darken(color), outline=darken(color)))
        self.bind("<Leave>", lambda e: self.itemconfig("shape", fill=color, outline=color))


def make_button(parent, text, color, command, width=12, fg="white"):
    """width is roughly the number of characters (converted to pixels)."""
    return PillButton(parent, text, command, color, fg, width=width * 10 + 24)


def card(parent):
    """A white box with a thin border (like an Apple card)."""
    return tk.Frame(parent, bg="white", highlightbackground=BORDER, highlightthickness=1)


def stat_card(parent, title, color):
    """A card with a thin coloured top line. Returns (card, value_label)."""
    box = card(parent)
    tk.Frame(box, bg=color, height=3).pack(fill="x")
    inner = tk.Frame(box, bg="white")
    inner.pack(fill="x", padx=18, pady=(10, 12))
    title_label = tk.Label(inner, text=title, bg="white", fg=GRAY, font=(FONT, 9))
    title_label.pack(anchor="w")
    value = tk.Label(inner, text="-", bg="white", fg=TEXT, font=(FONT_BOLD, 18))
    value.pack(anchor="w")
    box.title_label = title_label          # so the title can be changed later
    return box, value