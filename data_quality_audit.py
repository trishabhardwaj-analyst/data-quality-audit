"""
VEDA Technology - Task 24: Data Quality Audit
Dataset: Sample Superstore (standard 21-column version)
Run:
    python data_quality_audit.py "Sample - Superstore.csv"
Outputs:
    issue_log_generated.csv
    cleaned_sample_generated.csv
    audit_summary.txt
"""
import sys
from pathlib import Path
import pandas as pd

EXPECTED_COLUMNS = [
    "Row ID","Order ID","Order Date","Ship Date","Ship Mode","Customer ID",
    "Customer Name","Segment","Country","City","State","Postal Code","Region",
    "Product ID","Category","Sub-Category","Product Name","Sales","Quantity",
    "Discount","Profit"
]
EXPECTED_REGIONS = {"Central","East","South","West"}

def load_data(path):
    path = str(path)

    if path.lower().endswith((".xls", ".xlsx")):
        df = pd.read_excel(path, sheet_name=0)
    else:
        for enc in ("utf-8", "utf-8-sig", "latin1"):
            try:
                df = pd.read_csv(path, encoding=enc)
                break
            except UnicodeDecodeError:
                continue
        else:
            raise ValueError("Could not decode the CSV.")

    # Standardize column names used by different versions
    column_mapping = {
        "Country/Region": "Country",
        "State/Province": "State",
    }

    df = df.rename(columns=column_mapping)

    return df

def audit(df):
    issues = []

    # Schema
    missing_cols = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    issues.append(("DQ-000","Schema","Dataset","Missing expected columns",
                   len(missing_cols), "PASS" if not missing_cols else "FAIL",
                   "None" if not missing_cols else ", ".join(missing_cols)))

    # Missing values
    nulls = df[EXPECTED_COLUMNS].isna().sum()
    null_total = int(nulls.sum())
    issues.append(("DQ-001","Missing values","All columns",
                   "Count of blank/null cells", null_total,
                   "PASS" if null_total == 0 else "REVIEW",
                   "No action" if null_total == 0 else "Investigate field-specific blanks"))

    # Exact duplicates
    dup = int(df.duplicated().sum())
    issues.append(("DQ-002","Duplicates","Full row",
                   "Exact duplicate rows", dup,
                   "PASS" if dup == 0 else "REVIEW",
                   "No action" if dup == 0 else "Drop exact duplicates after validation"))

    # Dates
    order = pd.to_datetime(df["Order Date"], errors="coerce")
    ship = pd.to_datetime(df["Ship Date"], errors="coerce")
    bad_date_parse = int(order.isna().sum() + ship.isna().sum())
    bad_ship_order = int((ship < order).fillna(False).sum())
    date_issues = bad_date_parse + bad_ship_order
    issues.append(("DQ-003","Date validity","Order Date / Ship Date",
                   "Invalid dates or Ship Date earlier than Order Date", date_issues,
                   "PASS" if date_issues == 0 else "REVIEW",
                   "Keep valid dates; investigate invalid rows"))

    # Numeric coercion and ranges
    for col in ["Sales","Quantity","Discount","Profit"]:
        numeric = pd.to_numeric(df[col], errors="coerce")
        bad_type = int(numeric.isna().sum() - df[col].isna().sum())
        if col == "Sales":
            bad_range = int((numeric <= 0).sum())
            rule = "Sales should be > 0"
        elif col == "Quantity":
            bad_range = int((numeric <= 0).sum() + (numeric % 1 != 0).sum())
            rule = "Quantity should be a positive integer"
        elif col == "Discount":
            bad_range = int(((numeric < 0) | (numeric > 1)).sum())
            rule = "Discount should be between 0 and 1"
        else:
            bad_range = 0
            rule = "Profit may be negative; negative values are valid business outcomes"
        count = bad_type + bad_range
        issues.append((f"DQ-{len(issues)+1:03d}","Range / type",col,
                       rule, count,
                       "PASS" if count == 0 else "REVIEW",
                       "No action" if count == 0 else "Investigate and correct"))

    # Category-subcategory consistency
    mapping = df[["Category","Sub-Category"]].dropna().drop_duplicates()
    conflicts = mapping.groupby("Sub-Category")["Category"].nunique()
    conflict_count = int((conflicts > 1).sum())
    issues.append(("DQ-007","Consistency","Category / Sub-Category",
                   "Sub-category maps to more than one category", conflict_count,
                   "PASS" if conflict_count == 0 else "REVIEW",
                   "No action" if conflict_count == 0 else "Standardize category mapping"))

    # Region values
    invalid_regions = int((~df["Region"].isin(EXPECTED_REGIONS)).sum())
    issues.append(("DQ-008","Consistency","Region",
                   "Unexpected region values", invalid_regions,
                   "PASS" if invalid_regions == 0 else "REVIEW",
                   "No action" if invalid_regions == 0 else "Standardize region labels"))

    # Negative profit: report, do not clean
    neg_profit = int((pd.to_numeric(df["Profit"], errors="coerce") < 0).sum())
    issues.append(("DQ-009","Business rule","Profit",
                   "Negative-profit rows are valid loss transactions and should be flagged, not deleted",
                   neg_profit,"INFO","Retain rows; analyze pricing/discount/product mix"))

    return pd.DataFrame(issues, columns=["Issue ID","Check Type","Field(s)","Validation / Finding","Count","Status","Action"])

def main():
    if len(sys.argv) < 2:
        print("Usage: python data_quality_audit.py <Sample - Superstore.csv>")
        sys.exit(1)
    source = Path(sys.argv[1])
    df = load_data(source)
    report = audit(df)
    report.to_csv("issue_log_generated.csv", index=False, encoding="utf-8-sig")

    cleaned = df.copy()
    cleaned["Order Date"] = pd.to_datetime(cleaned["Order Date"], errors="coerce")
    cleaned["Ship Date"] = pd.to_datetime(cleaned["Ship Date"], errors="coerce")
    cleaned = cleaned.drop_duplicates()
    cleaned.to_csv("cleaned_sample_generated.csv", index=False, encoding="utf-8-sig")

    summary = [
        f"Rows: {len(df)}",
        f"Columns: {len(df.columns)}",
        f"Exact duplicate rows: {df.duplicated().sum()}",
        f"Total missing cells: {df[EXPECTED_COLUMNS].isna().sum().sum()}",
        f"Negative-profit rows (valid business values): {(pd.to_numeric(df['Profit'], errors='coerce') < 0).sum()}",
        "",
        "See issue_log_generated.csv for all checks."
    ]
    Path("audit_summary.txt").write_text("\n".join(summary), encoding="utf-8")
    print("\n".join(summary))

if __name__ == "__main__":
    main()
