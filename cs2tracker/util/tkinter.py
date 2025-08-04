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
