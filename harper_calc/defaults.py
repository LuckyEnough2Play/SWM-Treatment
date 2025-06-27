"""Default EMC and runoff coefficients derived from Harper 2007 report."""

# Example default EMC values (mg/L) for Total Nitrogen (TN) and Total Phosphorus (TP)
# Values are illustrative and should be verified against the actual report.
DEFAULT_EMC = {
    "residential": {"TN": 1.8, "TP": 0.3},
    "commercial": {"TN": 2.5, "TP": 0.4},
    "agricultural": {"TN": 3.2, "TP": 0.6},
}

# Example runoff coefficients for land uses (unitless)
RUNOFF_COEFFICIENT = {
    "residential": 0.5,
    "commercial": 0.8,
    "agricultural": 0.3,
}
