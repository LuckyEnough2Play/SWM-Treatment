"""Command-line interface for the Harper nutrient loading calculator."""
import argparse
from harper_calc.calculator import (
    SiteData,
    calculate_site_loads,
    load_site_data,
    save_site_data,
    aggregate_site_loads,
    load_subareas,
    compare_scenarios,
    apply_treatment,
    TREATMENT_EFFICIENCY,
)
from harper_calc.defaults import DEFAULT_EMC, RUNOFF_COEFFICIENT


def main(argv=None):
    parser = argparse.ArgumentParser(description="Harper Nutrient Loading Calculator")
    parser.add_argument("--landuse", choices=DEFAULT_EMC.keys(), default="residential", help="Land use type")
    parser.add_argument("--area", type=float, help="Site area in acres")
    parser.add_argument(
        "--rainfall",
        type=float,
        default=50.0,
        help="Annual rainfall in inches",
    )
    parser.add_argument("--emc_tn", type=float, help="Override TN EMC in mg/L")
    parser.add_argument("--emc_tp", type=float, help="Override TP EMC in mg/L")
    parser.add_argument("--runoff_coeff", type=float, help="Override runoff coefficient")
    parser.add_argument("--load", type=str, help="Load site data from JSON file")
    parser.add_argument("--save", type=str, help="Save site data to JSON file")
    parser.add_argument("--subareas", type=str, help="JSON file with list of subareas")
    parser.add_argument("--pre", type=str, help="JSON file for pre-development subareas")
    parser.add_argument("--post", type=str, help="JSON file for post-development subareas")
    parser.add_argument("--treatment", choices=list(TREATMENT_EFFICIENCY.keys()), help="Apply treatment type to results")

    args = parser.parse_args(argv)

    if args.pre and args.post:
        pre = load_subareas(args.pre)
        post = load_subareas(args.post)
        comp = compare_scenarios(pre, post)
        post_result = comp["post"]
        if args.treatment:
            post_result = apply_treatment(post_result, args.treatment)
        print(
            f"Pre-development TN Load (kg/yr): {comp['pre']['TN_kg_per_yr']:.2f}"
        )
        print(
            f"Post-development TN Load (kg/yr): {post_result['TN_kg_per_yr']:.2f}"
        )
        tn_ok = post_result["TN_kg_per_yr"] <= comp["pre"]["TN_kg_per_yr"]
        tp_ok = post_result["TP_kg_per_yr"] <= comp["pre"]["TP_kg_per_yr"]
        if tn_ok and tp_ok:
            print("No net increase achieved.")
        else:
            print("No net increase NOT achieved.")
        return

    if args.subareas:
        subareas = load_subareas(args.subareas)
        result = aggregate_site_loads(subareas)
        if args.treatment:
            result = apply_treatment(result, args.treatment)
        print(f"Annual Runoff Volume (m^3): {result['runoff_volume_m3']:.2f}")
        print(
            f"Annual TN Load (kg/yr): {result['TN_kg_per_yr']:.2f} ({result['TN_lb_per_yr']:.2f} lb/yr)"
        )
        print(
            f"Annual TP Load (kg/yr): {result['TP_kg_per_yr']:.2f} ({result['TP_lb_per_yr']:.2f} lb/yr)"
        )
        return

    loaded = load_site_data(args.load) if args.load else None

    landuse = args.landuse
    emc_tn = args.emc_tn if args.emc_tn is not None else (
        loaded.emc_mg_per_L_TN if loaded else DEFAULT_EMC[landuse]["TN"]
    )
    emc_tp = args.emc_tp if args.emc_tp is not None else (
        loaded.emc_mg_per_L_TP if loaded else DEFAULT_EMC[landuse]["TP"]
    )
    runoff_coeff = args.runoff_coeff if args.runoff_coeff is not None else (
        loaded.runoff_coefficient if loaded else RUNOFF_COEFFICIENT[landuse]
    )

    area = args.area if args.area is not None else (loaded.area_acres if loaded else None)
    rainfall = (
        args.rainfall * 0.0254
        if args.rainfall is not None
        else (loaded.annual_rainfall_m if loaded else None)
    )
    if area is None:
        parser.error("--area is required if not loaded from file")

    site_data = SiteData(
        area_acres=area,
        annual_rainfall_m=rainfall,
        runoff_coefficient=runoff_coeff,
        emc_mg_per_L_TN=emc_tn,
        emc_mg_per_L_TP=emc_tp,
    )

    result = calculate_site_loads(site_data)
    if args.treatment:
        treated = apply_treatment(result, args.treatment)
    else:
        treated = None

    print(f"Annual Runoff Volume (m^3): {result['runoff_volume_m3']:.2f}")
    print(f"Annual TN Load (kg/yr): {result['TN_kg_per_yr']:.2f} ({result['TN_lb_per_yr']:.2f} lb/yr)")
    print(f"Annual TP Load (kg/yr): {result['TP_kg_per_yr']:.2f} ({result['TP_lb_per_yr']:.2f} lb/yr)")
    if treated:
        print(
            f"Treated TN Load (kg/yr): {treated['TN_kg_per_yr']:.2f} ({treated['TN_lb_per_yr']:.2f} lb/yr)"
        )
        print(
            f"Treated TP Load (kg/yr): {treated['TP_kg_per_yr']:.2f} ({treated['TP_lb_per_yr']:.2f} lb/yr)"
        )

    if args.save:
        save_site_data(site_data, args.save)


if __name__ == "__main__":
    main()
