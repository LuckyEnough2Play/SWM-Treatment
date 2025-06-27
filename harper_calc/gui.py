import tkinter as tk
from tkinter import ttk, filedialog
from .calculator import SiteData, calculate_site_loads
from .defaults import DEFAULT_EMC, RUNOFF_COEFFICIENT
from .report import export_pdf


class CalculatorApp(tk.Tk):
    """Simple GUI for the Harper nutrient loading calculator."""

    def __init__(self):
        super().__init__()
        self.title("Harper Nutrient Calculator")
        self.last_result = None
        self._build_widgets()

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
        self.last_result = result
        output = (
            f"Runoff Volume (m^3): {result['runoff_volume_m3']:.2f}\n"
            f"TN Load (kg/yr): {result['TN_kg_per_yr']:.2f}\n"
            f"TP Load (kg/yr): {result['TP_kg_per_yr']:.2f}"
        )
        self._update_results(output)

    def export(self):
        if not self.last_result:
            return
        filepath = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
        )
        if filepath:
            export_pdf(self.last_result, filepath)

    def _update_results(self, text: str):
        self.results.configure(state="normal")
        self.results.delete("1.0", tk.END)
        self.results.insert(tk.END, text)
        self.results.configure(state="disabled")


def main():
    app = CalculatorApp()
    app.mainloop()


if __name__ == "__main__":
    main()