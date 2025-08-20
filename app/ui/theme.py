import ttkbootstrap as tb

MAROON = "#7A001F"      # deep maroon
TEXT_LIGHT = "#FFFFFF"

def setup_style(app):
    style = tb.Style(theme="flatly")

    # Deep maroon hero section
    style.configure("Hero.TFrame", background=MAROON, borderwidth=0)
    style.configure("HeroTitle.TLabel",
                    foreground=TEXT_LIGHT, background=MAROON,
                    font=("Segoe UI Semibold", 32, "bold"))
    style.configure("HeroSub.TLabel",
                    foreground="#F0E6EC", background=MAROON,
                    font=("Segoe UI", 11))
    style.configure("Footer.TLabel", foreground="#666666", font=("Segoe UI", 9))

    # Inputs and labels
    style.configure("FieldLabel.TLabel", font=("Segoe UI", 11, "bold"))
    style.configure("SectionTitle.TLabel", font=("Segoe UI Semibold", 24, "bold"))

    # Bigger rounded buttons
    style.configure("Big.TButton", padding=(16, 12), font=("Segoe UI", 11, "bold"))
    # Treeview improvements
    style.configure("Treeview", font=("Segoe UI", 10))
    style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
