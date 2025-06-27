"""Command-line interface for the Harper nutrient loading calculator."""
import argparse
from .calculator import SiteData, calculate_site_loads
from .defaults import DEFAULT_EMC, RUNOFF_COEFFICIENT


def main(argv=None):
    parser = argparse.ArgumentParser(description="Harper Nutrient Loading Calculator")
    parser.add_argument("--landuse", choices=DEFAULT_EMC.keys(), default="residential", help="Land use type")
    parser.add_argument("--area", type=float, required=True, help="Site area in acres")
    parser.add_argument("--rainfall", type=float, default=1.0, help="Annual rainfall in meters")
    parser.add_argument("--emc_tn", type=float, help="Override TN EMC in mg/L")
    parser.add_argument("--emc_tp", type=float, help="Override TP EMC in mg/L")
    parser.add_argument("--runoff_coeff", type=float, help="Override runoff coefficient")

    args = parser.parse_args(argv)

    landuse = args.landuse
    emc_tn = args.emc_tn if args.emc_tn is not None else DEFAULT_EMC[landuse]["TN"]
    emc_tp = args.emc_tp if args.emc_tp is not None else DEFAULT_EMC[landuse]["TP"]
    runoff_coeff = args.runoff_coeff if args.runoff_coeff is not None else RUNOFF_COEFFICIENT[landuse]

    site_data = SiteData(
        area_acres=args.area,
        annual_rainfall_m=args.rainfall,
        runoff_coefficient=runoff_coeff,
        emc_mg_per_L_TN=emc_tn,
        emc_mg_per_L_TP=emc_tp,
    )

    result = calculate_site_loads(site_data)

    print(f"Annual Runoff Volume (m^3): {result['runoff_volume_m3']:.2f}")
    print(f"Annual TN Load (kg/yr): {result['TN_kg_per_yr']:.2f}")
    print(f"Annual TP Load (kg/yr): {result['TP_kg_per_yr']:.2f}")


if __name__ == "__main__":
    main()
