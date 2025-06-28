import os
import tkinter as tk
from tkinter import ttk, filedialog
from harper_calc.calculator import (
    SiteData,
    calculate_site_loads,
    format_breakdown,
    save_site_data,
    load_site_data,
)
from harper_calc.defaults import DEFAULT_EMC, RUNOFF_COEFFICIENT
from harper_calc.report import export_pdf

HELP_TEXT = (
    "Harper Nutrient Calculator\n\n"
    "Enter site area, rainfall, and verify runoff coefficient and EMCs.\n"
    "Runoff volume = area * 4046.8564224 * rainfall * runoff coefficient.\n"
    "Loads = EMC * runoff volume / 1000.\n"
    "Use File > Open/Save for scenarios and Export PDF for reports."
)


class Tooltip:
    """A simple tooltip for a widget."""
    def __init__(self, widget, text, delay=500):
        self.widget = widget
        self.text = text
        self.delay = delay
        self._id = None
        self.tipwindow = None
        widget.bind("<Enter>", self._schedule)
        widget.bind("<Leave>", self._hide)

    def _schedule(self, _event=None):
        self._hide()
        self._id = self.widget.after(self.delay, self._show)

    def _show(self):
        if self.tipwindow:
            return
        x, y, cx, cy = self.widget.bbox("insert") if isinstance(self.widget, tk.Text) else (0, 0, 0, 0)
        x = x + self.widget.winfo_rootx() + 20
        y = y + self.widget.winfo_rooty() + 20
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tw, text=self.text, background="#FFFFE0", relief="solid", borderwidth=1)
        label.pack(ipadx=4, ipady=2)

    def _hide(self, _event=None):
        if self._id:
            self.widget.after_cancel(self._id)
            self._id = None
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None


class CalculatorApp(tk.Tk):
    """WordPad-style GUI for the Harper nutrient loading calculator."""

    def __init__(self):
        super().__init__()
        self.title("Harper Nutrient Calculator")
        self.configure(bg="#DCE6F1")
        self.last_result = None
        self._setup_style()
        self._build_menu()
        self._build_toolbar()
        self._build_widgets()

    def _setup_style(self):
        style = ttk.Style(self)
        default_font = ("Calibri", 11)
        style.configure(".", font=default_font)
        style.configure("TButton", padding=4)
        style.configure("TEntry", padding=4)
        style.configure("TLabel", padding=2)
        self.option_add("*Font", default_font)

    def _build_menu(self):
        menu = tk.Menu(self)
        file_menu = tk.Menu(menu, tearoff=0)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Export PDF", command=self.export)
        menu.add_cascade(label="File", menu=file_menu)

        help_menu = tk.Menu(menu, tearoff=0)
        help_menu.add_command(label="About", command=self.show_help)
        menu.add_cascade(label="Help", menu=help_menu)

        self.config(menu=menu)

    def _build_toolbar(self):
        toolbar = tk.Frame(self, bg="#DCE6F1")
        toolbar.pack(fill="x")
        # Load icons from harper_calc/icons/<name>.png
        self.icons = {}
        icon_names = {"open": self.open_file, "save": self.save_file, "export": self.export}
        for name, cmd in icon_names.items():
            path = os.path.join(os.path.dirname(__file__), "icons", f"{name}.png")
            try:
                img = tk.PhotoImage(file=path)
            except Exception:
                img = tk.PhotoImage(width=1, height=1)  # placeholder
            self.icons[name] = img
            btn = tk.Button(toolbar, image=img, bg="#DCE6F1", bd=0, highlightthickness=0, command=cmd)
            btn.pack(side="left", padx=2, pady=2)
            Tooltip(btn, name.capitalize())

    def _build_widgets(self):
        paned = ttk.Panedwindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill="both", expand=True)

        # Left pane: form
        left = ttk.Frame(paned, padding=10, style="TFrame")
        paned.add(left, weight=1)

        # Right pane: "page"
        right_container = tk.Frame(paned, bg="#FFFFFF", bd=1, relief="solid")
        paned.add(right_container, weight=3)
        right = ttk.Frame(right_container, padding=10)
        right.pack(fill="both", expand=True)

        # Form controls
        labels = [
            ("Land Use:", 0),
            ("Area (acres):", 1),
            ("Rainfall (m):", 2),
            ("Runoff Coefficient:", 3),
            ("EMC TN (mg/L):", 4),
            ("EMC TP (mg/L):", 5),
        ]
        for text, row in labels:
            ttk.Label(left, text=text).grid(row=row, column=0, sticky="w", pady=2)
        self.landuse_var = tk.StringVar(value="residential")
        landuse_menu = ttk.OptionMenu(left, self.landuse_var, "residential", *DEFAULT_EMC.keys())
        landuse_menu.grid(row=0, column=1, sticky="ew", pady=2)
        self.area_var = tk.StringVar()
        ttk.Entry(left, textvariable=self.area_var).grid(row=1, column=1, sticky="ew", pady=2)
        self.rainfall_var = tk.StringVar(value="1.0")
        ttk.Entry(left, textvariable=self.rainfall_var).grid(row=2, column=1, sticky="ew", pady=2)
        self.runoff_var = tk.StringVar()
        ttk.Entry(left, textvariable=self.runoff_var).grid(row=3, column=1, sticky="ew", pady=2)
        self.emc_tn_var = tk.StringVar()
        ttk.Entry(left, textvariable=self.emc_tn_var).grid(row=4, column=1, sticky="ew", pady=2)
        self.emc_tp_var = tk.StringVar()
        ttk.Entry(left, textvariable=self.emc_tp_var).grid(row=5, column=1, sticky="ew", pady=2)

        # Buttons
        calc_btn = ttk.Button(left, text="Calculate", command=self.calculate)
        calc_btn.grid(row=6, column=0, columnspan=2, pady=(10, 0), sticky="ew")
        export_btn = ttk.Button(left, text="Export PDF", command=self.export)
        export_btn.grid(row=7, column=0, columnspan=2, pady=(5, 0), sticky="ew")
        left.columnconfigure(1, weight=1)

        # Results text widget
        self.results = tk.Text(right, wrap="word", state="disabled", bg="#FFFFFF")
        self.results.pack(fill="both", expand=True)

    def calculate(self):
        try:
            landuse = self.landuse_var.get()
            area = float(self.area_var.get())
            rainfall = float(self.rainfall_var.get())
            runoff = float(self.runoff_var.get()) if self.runoff_var.get() else RUNOFF_COEFFICIENT[landuse]
            emc_tn = float(self.emc_tn_var.get()) if self.emc_tn_var.get() else DEFAULT_EMC[landuse]["TN"]
            emc_tp = float(self.emc_tp_var.get()) if self.emc_tp_var.get() else DEFAULT_EMC[landuse]["TP"]
        except ValueError:
            self._update_results("Invalid numeric input.")
            return

        data = SiteData(
            area_acres=area,
            annual_rainfall_m=rainfall,
            runoff_coefficient=runoff,
            emc_mg_per_L_TN=emc_tn,
            emc_mg_per_L_TP=emc_tp,
        )

        result = calculate_site_loads(data)
        self.last_result = (result, data)
        output = (
            f"Runoff Volume (m^3): {result['runoff_volume_m3']:.2f}\n"
            f"TN Load (kg/yr): {result['TN_kg_per_yr']:.2f}\n"
            f"TP Load (kg/yr): {result['TP_kg_per_yr']:.2f}\n\n"
            f"{format_breakdown(data, result)}"
        )
        self._update_results(output)

    def export(self):
        if not self.last_result:
            return
        result, data = self.last_result
        filepath = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
        )
        if filepath:
            export_pdf(result, filepath, data=data)

    def save_file(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
        )
        if filepath:
            data = self._gather_site_data()
            save_site_data(data, filepath)

    def open_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if not filepath:
            return
        data = load_site_data(filepath)
        self._set_site_data(data)

    def _gather_site_data(self) -> SiteData:
        return SiteData(
            area_acres=float(self.area_var.get()),
            annual_rainfall_m=float(self.rainfall_var.get()),
            runoff_coefficient=float(self.runoff_var.get()) if self.runoff_var.get() else RUNOFF_COEFFICIENT[self.landuse_var.get()],
            emc_mg_per_L_TN=float(self.emc_tn_var.get()) if self.emc_tn_var.get() else DEFAULT_EMC[self.landuse_var.get()]["TN"],
            emc_mg_per_L_TP=float(self.emc_tp_var.get()) if self.emc_tp_var.get() else DEFAULT_EMC[self.landuse_var.get()]["TP"],
        )

    def _set_site_data(self, data: SiteData) -> None:
        self.area_var.set(str(data.area_acres))
        self.rainfall_var.set(str(data.annual_rainfall_m))
        self.runoff_var.set(str(data.runoff_coefficient))
        self.emc_tn_var.set(str(data.emc_mg_per_L_TN))
        self.emc_tp_var.set(str(data.emc_mg_per_L_TP))

    def _update_results(self, text: str):
        self.results.configure(state="normal")
        self.results.delete("1.0", tk.END)
        self.results.insert(tk.END, text)
        self.results.configure(state="disabled")

    def show_help(self):
        win = tk.Toplevel(self)
        win.title("About")
        text = tk.Text(win, width=60, height=15, wrap="word")
        text.insert("1.0", HELP_TEXT)
        text.configure(state="disabled")
        text.pack(fill="both", expand=True, padx=10, pady=10)


def main():
    app = CalculatorApp()
    app.mainloop()


if __name__ == "__main__":
    main()
