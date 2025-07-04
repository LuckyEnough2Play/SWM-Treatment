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
        self.current_text = ""
        self.dragging_handle = None
        self._setup_style()
        self._build_menu()
        self._build_toolbar()
        self._build_widgets()
        self._update_defaults()
        self.calculate()

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
        toolbar.grid(row=0, column=0, sticky="ew")
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
        # Use grid layout for fixed left pane and expanding right pane
        container = tk.Frame(self)
        container.grid(row=1, column=0, sticky="nsew")
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)

        # Left pane with notebook
        left = ttk.Frame(container, padding=10, style="TFrame")
        left.grid(row=0, column=0, sticky="ns")
        notebook = ttk.Notebook(left)
        notebook.grid(row=0, column=0, sticky="nsew")
        inputs = ttk.Frame(notebook)
        layout_tab = ttk.Frame(notebook)
        notebook.add(inputs, text="Inputs")
        notebook.add(layout_tab, text="Layout")

        # Right pane: "page" (expanding)
        right_container = tk.Frame(container, bg="#FFFFFF", bd=1, relief="solid")
        right_container.grid(row=0, column=1, sticky="nsew")
        container.columnconfigure(1, weight=1)
        right = ttk.Frame(right_container, padding=10)
        right.grid(row=0, column=0, sticky="nsew")

        # Form controls
        labels = [
            ("Project Name:", 0),
            ("Land Use:", 1),
            ("Area (acres):", 2),
            ("Rainfall (in):", 3),
            ("Runoff Coefficient:", 4),
            ("EMC TN (mg/L):", 5),
            ("EMC TP (mg/L):", 6),
        ]
        for text, row in labels:
            ttk.Label(inputs, text=text).grid(row=row, column=0, sticky="w", pady=2)
        self.project_name_var = tk.StringVar()
        project_entry = ttk.Entry(inputs, textvariable=self.project_name_var)
        project_entry.grid(row=0, column=1, sticky="ew", pady=2)
        Tooltip(project_entry, "Project name for report header")
        self.landuse_var = tk.StringVar(value="residential")
        landuse_menu = ttk.OptionMenu(inputs, self.landuse_var, "residential", *DEFAULT_EMC.keys())
        landuse_menu.grid(row=1, column=1, sticky="ew", pady=2)
        Tooltip(landuse_menu, "Land use category affecting defaults")
        self.landuse_var.trace_add("write", self._update_defaults)
        self.area_var = tk.StringVar(value="1.0")
        area_entry = ttk.Entry(inputs, textvariable=self.area_var)
        area_entry.grid(row=2, column=1, sticky="ew", pady=2)
        Tooltip(area_entry, "Drainage area in acres")
        self.rainfall_var = tk.StringVar(value="50")
        rain_entry = ttk.Entry(inputs, textvariable=self.rainfall_var)
        rain_entry.grid(row=3, column=1, sticky="ew", pady=2)
        Tooltip(rain_entry, "Annual rainfall depth in inches")
        self.runoff_var = tk.StringVar()
        runoff_entry = ttk.Entry(inputs, textvariable=self.runoff_var)
        runoff_entry.grid(row=4, column=1, sticky="ew", pady=2)
        ttk.Button(inputs, text="Weighted...", command=self._open_weighted_dialog).grid(row=4, column=2, padx=2)
        Tooltip(runoff_entry, "Runoff coefficient")
        self.emc_tn_var = tk.StringVar()
        tn_entry = ttk.Entry(inputs, textvariable=self.emc_tn_var, state="readonly")
        tn_entry.grid(row=5, column=1, sticky="ew", pady=2)
        Tooltip(tn_entry, "Total Nitrogen EMC (mg/L)")
        self.emc_tp_var = tk.StringVar()
        tp_entry = ttk.Entry(inputs, textvariable=self.emc_tp_var, state="readonly")
        tp_entry.grid(row=6, column=1, sticky="ew", pady=2)
        Tooltip(tp_entry, "Total Phosphorus EMC (mg/L)")

        margin_frame = ttk.LabelFrame(layout_tab, text="Margins (in)")
        margin_frame.grid(row=0, column=0, pady=(10, 0), sticky="ew")
        self.left_margin_var = tk.DoubleVar(value=0.5)
        self.right_margin_var = tk.DoubleVar(value=0.5)
        self.top_margin_var = tk.DoubleVar(value=1.0)
        self.bottom_margin_var = tk.DoubleVar(value=1.0)
        ttk.Label(margin_frame, text="Left").grid(row=0, column=0, sticky="w")
        ttk.Entry(margin_frame, textvariable=self.left_margin_var, width=5).grid(row=0, column=1, padx=2)
        ttk.Label(margin_frame, text="Right").grid(row=0, column=2, sticky="w")
        ttk.Entry(margin_frame, textvariable=self.right_margin_var, width=5).grid(row=0, column=3, padx=2)
        ttk.Label(margin_frame, text="Top").grid(row=1, column=0, sticky="w")
        ttk.Entry(margin_frame, textvariable=self.top_margin_var, width=5).grid(row=1, column=1, padx=2)
        ttk.Label(margin_frame, text="Bottom").grid(row=1, column=2, sticky="w")
        ttk.Entry(margin_frame, textvariable=self.bottom_margin_var, width=5).grid(row=1, column=3, padx=2)
        for var in (self.left_margin_var, self.right_margin_var, self.top_margin_var, self.bottom_margin_var):
            var.trace_add("write", lambda *_: self._update_preview())

        # trigger calculations on input change
        vars_to_trace = [self.landuse_var, self.area_var, self.rainfall_var, self.project_name_var]
        for var in vars_to_trace:
            var.trace_add("write", lambda *_, v=var: self.calculate())

        # Layout tab additional info
        layout_tab.columnconfigure(1, weight=1)
        left.columnconfigure(0, weight=1)

        # Print preview canvas and rulers
        self.scale = 40  # pixels per inch
        page_w = int(8.5 * self.scale)
        page_h = int(11 * self.scale)

        self.top_ruler = tk.Canvas(right, height=25, width=page_w, bg="#f0f0f0")
        self.top_ruler.grid(row=0, column=0, sticky="ew")
        self.right_ruler = tk.Canvas(right, width=20, height=page_h, bg="#f0f0f0")
        self.right_ruler.grid(row=1, column=1, sticky="ns")

        self.page_canvas = tk.Canvas(right, width=page_w, height=page_h, bg="white", highlightthickness=1, highlightbackground="black")
        self.page_canvas.grid(row=1, column=0)
        right.rowconfigure(1, weight=1)
        right.columnconfigure(0, weight=1)
        self._update_preview()

    def _update_defaults(self, *_):
        landuse = self.landuse_var.get()
        self.runoff_var.set(str(RUNOFF_COEFFICIENT[landuse]))
        self.emc_tn_var.set(str(DEFAULT_EMC[landuse]["TN"]))
        self.emc_tp_var.set(str(DEFAULT_EMC[landuse]["TP"]))

    def calculate(self):
        try:
            landuse = self.landuse_var.get()
            area = float(self.area_var.get())
            rainfall = float(self.rainfall_var.get()) * 0.0254
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
            f"TN Load (kg/yr): {result['TN_kg_per_yr']:.2f} ({result['TN_lb_per_yr']:.2f} lb/yr)\n"
            f"TP Load (kg/yr): {result['TP_kg_per_yr']:.2f} ({result['TP_lb_per_yr']:.2f} lb/yr)\n\n"
            f"{format_breakdown(data, result)}"
        )
        self._update_results(output)

    def _open_weighted_dialog(self):
        win = tk.Toplevel(self)
        win.title("Weighted Runoff Coefficient")
        ttk.Label(win, text="% Pavement").grid(row=0, column=0, sticky="e")
        ttk.Label(win, text="% Grass").grid(row=1, column=0, sticky="e")
        ttk.Label(win, text="% Roof").grid(row=2, column=0, sticky="e")
        pav_var = tk.StringVar(value="0")
        grass_var = tk.StringVar(value="0")
        roof_var = tk.StringVar(value="0")
        ttk.Entry(win, textvariable=pav_var, width=5).grid(row=0, column=1)
        ttk.Entry(win, textvariable=grass_var, width=5).grid(row=1, column=1)
        ttk.Entry(win, textvariable=roof_var, width=5).grid(row=2, column=1)

        def apply_weighted():
            try:
                pav = float(pav_var.get()) / 100.0
                grass = float(grass_var.get()) / 100.0
                roof = float(roof_var.get()) / 100.0
            except ValueError:
                win.destroy()
                return
            coeff = pav * 0.9 + grass * 0.2 + roof * 0.95
            self.runoff_var.set(f"{coeff:.2f}")
            win.destroy()

        ttk.Button(win, text="Apply", command=apply_weighted).grid(row=3, column=0, columnspan=2, pady=4)

    def export(self):
        if not self.last_result:
            return
        result, data = self.last_result
        filepath = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
        )
        if filepath:
            export_pdf(
                result,
                filepath,
                data=data,
                project_name=self.project_name_var.get() or None,
                left_margin=self.left_margin_var.get(),
                right_margin=self.right_margin_var.get(),
                top_margin=self.top_margin_var.get(),
                bottom_margin=self.bottom_margin_var.get(),
            )

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
            annual_rainfall_m=float(self.rainfall_var.get()) * 0.0254,
            runoff_coefficient=float(self.runoff_var.get()) if self.runoff_var.get() else RUNOFF_COEFFICIENT[self.landuse_var.get()],
            emc_mg_per_L_TN=float(self.emc_tn_var.get()) if self.emc_tn_var.get() else DEFAULT_EMC[self.landuse_var.get()]["TN"],
            emc_mg_per_L_TP=float(self.emc_tp_var.get()) if self.emc_tp_var.get() else DEFAULT_EMC[self.landuse_var.get()]["TP"],
        )

    def _set_site_data(self, data: SiteData) -> None:
        self.area_var.set(str(data.area_acres))
        self.rainfall_var.set(str(data.annual_rainfall_m / 0.0254))
        self.runoff_var.set(str(data.runoff_coefficient))
        self.emc_tn_var.set(str(data.emc_mg_per_L_TN))
        self.emc_tp_var.set(str(data.emc_mg_per_L_TP))
        self._update_defaults()

    def _update_results(self, text: str):
        self.current_text = text
        self._update_preview()

    def _update_preview(self):
        if not hasattr(self, "page_canvas"):
            return
        self.page_canvas.delete("all")
        page_w = int(8.5 * self.scale)
        page_h = int(11 * self.scale)
        l = self.left_margin_var.get() * self.scale
        r = self.right_margin_var.get() * self.scale
        t = self.top_margin_var.get() * self.scale
        b = self.bottom_margin_var.get() * self.scale
        self.page_canvas.create_rectangle(0, 0, page_w, page_h, fill="white", outline="black")
        self.page_canvas.create_rectangle(l, t, page_w - r, page_h - b, dash=(4, 2))
        self.page_canvas.create_text(
            l,
            t,
            text=self.current_text,
            anchor="nw",
            font=("Helvetica", 10),
            width=page_w - l - r,
        )
        self._draw_rulers()

    def show_help(self):
        win = tk.Toplevel(self)
        win.title("About")
        text = tk.Text(win, width=60, height=15, wrap="word")
        text.insert("1.0", HELP_TEXT)
        text.configure(state="disabled")
        text.pack(fill="both", expand=True, padx=10, pady=10)

    def _draw_rulers(self):
        page_w = int(8.5 * self.scale)
        page_h = int(11 * self.scale)
        self.top_ruler.delete("all")
        self.right_ruler.delete("all")
        for i in range(int(8.5) + 1):
            x = i * self.scale
            self.top_ruler.create_line(x, 12, x, 25)
            self.top_ruler.create_text(x, 0, text=str(i), anchor="n", font=("Helvetica", 7))
            if i < int(8.5):
                self.top_ruler.create_line(x + self.scale / 2, 17, x + self.scale / 2, 25)
        for i in range(int(11) + 1):
            y = i * self.scale
            self.right_ruler.create_line(0, y, 10, y)
            self.right_ruler.create_text(12, y, text=str(i), anchor="w", font=("Helvetica", 7))
            if i < int(11):
                self.right_ruler.create_line(0, y + self.scale / 2, 5, y + self.scale / 2)

        # handles
        l = self.left_margin_var.get() * self.scale
        r = page_w - self.right_margin_var.get() * self.scale
        t = self.top_margin_var.get() * self.scale
        b = page_h - self.bottom_margin_var.get() * self.scale
        self.left_handle = self.top_ruler.create_rectangle(l - 4, 0, l + 4, 10, fill="blue", tags="left_handle")
        self.right_handle = self.top_ruler.create_rectangle(r - 4, 0, r + 4, 10, fill="blue", tags="right_handle")
        self.top_handle = self.right_ruler.create_rectangle(0, t - 4, 10, t + 4, fill="blue", tags="top_handle")
        self.bottom_handle = self.right_ruler.create_rectangle(0, b - 4, 10, b + 4, fill="blue", tags="bottom_handle")

        for tag in ("left_handle", "right_handle"):
            self.top_ruler.tag_bind(tag, "<ButtonPress-1>", lambda e, t=tag: self._start_handle(t))
        for tag in ("top_handle", "bottom_handle"):
            self.right_ruler.tag_bind(tag, "<ButtonPress-1>", lambda e, t=tag: self._start_handle(t))
        self.top_ruler.bind("<B1-Motion>", self._drag_motion)
        self.right_ruler.bind("<B1-Motion>", self._drag_motion)
        self.top_ruler.bind("<ButtonRelease-1>", self._end_drag)
        self.right_ruler.bind("<ButtonRelease-1>", self._end_drag)

    def _handle_drag(self, pos, which):
        value = pos / self.scale
        if which == 'left':
            self.left_margin_var.set(max(0, min(value, 3)))
        elif which == 'right':
            page_w = 8.5
            self.right_margin_var.set(max(0, min(page_w - value, 3)))
        elif which == 'top':
            self.top_margin_var.set(max(0, min(value, 3)))
        elif which == 'bottom':
            page_h = 11
            self.bottom_margin_var.set(max(0, min(page_h - value, 3)))

    def _start_handle(self, tag):
        self.dragging_handle = tag
        handle = getattr(self, tag)
        canvas = self.top_ruler if "left" in tag or "right" in tag else self.right_ruler
        canvas.itemconfig(handle, fill="red")

    def _drag_motion(self, event):
        tag = getattr(self, "dragging_handle", None)
        if not tag:
            return
        pos = event.x if "left" in tag or "right" in tag else event.y
        which = tag.split("_")[0]
        self._handle_drag(pos, which)

    def _end_drag(self, _event):
        tag = getattr(self, "dragging_handle", None)
        if not tag:
            return
        handle = getattr(self, tag)
        canvas = self.top_ruler if "left" in tag or "right" in tag else self.right_ruler
        canvas.itemconfig(handle, fill="blue")
        self.dragging_handle = None


def main():
    app = CalculatorApp()
    app.mainloop()


if __name__ == "__main__":
    main()
