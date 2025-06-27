import tkinter as tk
from tkinter import ttk, filedialog
from .calculator import (
    SiteData,
    calculate_site_loads,
    format_breakdown,
    save_site_data,
    load_site_data,
)
from .defaults import DEFAULT_EMC, RUNOFF_COEFFICIENT
from .report import export_pdf

HELP_TEXT = (
    "Harper Nutrient Calculator\n\n"
    "Enter site area, rainfall, and verify runoff coefficient and EMCs.\n"
    "Runoff volume = area * 4046.8564224 * rainfall * runoff coefficient.\n"
    "Loads = EMC * runoff volume / 1000.\n"
    "Use File > Open/Save for scenarios and Export PDF for reports."
)


class CalculatorApp(tk.Tk):
    """Simple GUI for the Harper nutrient loading calculator."""

    def __init__(self):
        super().__init__()
        self.title("Harper Nutrient Calculator")
        self.last_result = None
        self._build_widgets()
        self._build_menu()

    def _build_widgets(self):
        frame = ttk.Frame(self, padding="10")
        frame.grid(row=0, column=0, sticky="nsew")

        ttk.Label(frame, text="Land Use:").grid(row=0, column=0, sticky="w")
        self.landuse_var = tk.StringVar(value="residential")
        landuse_menu = ttk.OptionMenu(frame, self.landuse_var, "residential", *DEFAULT_EMC.keys())
        landuse_menu.grid(row=0, column=1, sticky="ew")

        ttk.Label(frame, text="Area (acres):").grid(row=1, column=0, sticky="w")
        self.area_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.area_var).grid(row=1, column=1, sticky="ew")

        ttk.Label(frame, text="Rainfall (m):").grid(row=2, column=0, sticky="w")
        self.rainfall_var = tk.StringVar(value="1.0")
        ttk.Entry(frame, textvariable=self.rainfall_var).grid(row=2, column=1, sticky="ew")

        ttk.Label(frame, text="Runoff Coefficient:").grid(row=3, column=0, sticky="w")
        self.runoff_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.runoff_var).grid(row=3, column=1, sticky="ew")

        ttk.Label(frame, text="EMC TN (mg/L):").grid(row=4, column=0, sticky="w")
        self.emc_tn_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.emc_tn_var).grid(row=4, column=1, sticky="ew")

        ttk.Label(frame, text="EMC TP (mg/L):").grid(row=5, column=0, sticky="w")
        self.emc_tp_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.emc_tp_var).grid(row=5, column=1, sticky="ew")

        calc_btn = ttk.Button(frame, text="Calculate", command=self.calculate)
        calc_btn.grid(row=6, column=0, columnspan=2, pady=(5, 0))

        export_btn = ttk.Button(frame, text="Export PDF", command=self.export)
        export_btn.grid(row=7, column=0, columnspan=2, pady=(5, 0))

        self.results = tk.Text(frame, width=40, height=5, state="disabled")
        self.results.grid(row=8, column=0, columnspan=2, pady=(5, 0))

        frame.columnconfigure(1, weight=1)

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
        # Keep current land use selection; just populate numeric fields
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