import sv_ttk


def centered(window, geometry):
    """Convert a regular WidthxHeight geometry into one that is centered."""
    w, h = geometry.split("x")
    w, h = int(w), int(h)

    ws = window.winfo_screenwidth()
    hs = window.winfo_screenheight()
    x = (ws / 2) - (w / 2)
    y = (hs / 2) - (h / 2)

    x, y = int(x), int(y)

    return f"{w}x{h}+{x}+{y}"


def size_info(geometry):
    """Extract the window width and height from a geometry string."""
    width, height = geometry.split("x")
    width, height = int(width), int(height)

    return width, height


def fix_sv_ttk(style):
    """
    Fixes the themed text entry widget in sv_ttk.

    Source: https://github.com/Jesse205/TtkText?tab=readme-ov-file
    """
    if sv_ttk.get_theme() == "light":
        style.configure("ThemedText.TEntry", fieldbackground="#fdfdfd", textpadding=5)
        style.map(
            "ThemedText.TEntry",
            fieldbackground=[
                ("hover", "!focus", "#f9f9f9"),
            ],
            foreground=[
                ("pressed", style.lookup("TEntry", "foreground")),
            ],
        )
    else:
        style.configure("ThemedText.TEntry", fieldbackground="#292929", textpadding=5)
        style.map(
            "ThemedText.TEntry",
            fieldbackground=[
                ("hover", "!focus", "#2f2f2f"),
                ("focus", "#1c1c1c"),
            ],
            foreground=[
                ("pressed", style.lookup("TEntry", "foreground")),
            ],
        )
