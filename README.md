VEDA Technology — Task 24: Data Quality Audit

Objective

Audit the Sample Superstore dataset for:

Missing values

Duplicate rows

Invalid ranges

Date and categorical consistency

Business-rule exceptions

Dataset

Use the standard 21-column Sample Superstore dataset with 9,994 transaction rows.

Expected columns:
Row ID, Order ID, Order Date, Ship Date, Ship Mode, Customer ID, Customer Name, Segment, Country, City, State, Postal Code, Region, Product ID, Category, Sub-Category, Product Name, Sales, Quantity, Discount, Profit

Deliverables

data_quality_audit.py — reusable Pandas audit script

issue_log.csv — validation checklist and issue log

cleaned_sample.csv — cleaned sample records

Task24_Data_Quality_Audit_Report.pdf — final audit report

Reference audit result

The reference audit for the canonical 9,994-row Sample Superstore data reports no exact duplicate rows and no missing values; negative Profit values are retained because they represent legitimate loss-making transactions rather than corrupt data.

How to run

Download/save the raw file as Sample - Superstore.csv.

Install Pandas:
pip install pandas

Run:
python data_quality_audit.py "Sample - Superstore.csv"

The script generates:

issue_log_generated.csv

cleaned_sample_generated.csv

audit_summary.txt

GitHub

Suggested repository name:
veda-task-24-data-quality-audit

Suggested description:
Task 24: Data Quality Audit using Python and Pandas to detect missing values, duplicates, range errors and consistency issues in Sample Superstore data.

Repository structure

veda-task-24-data-quality-audit/
├── data_quality_audit.py
├── issue_log.csv
├── cleaned_sample.csv
├── Task24_Data_Quality_Audit_Report.pdf
└── README.md

Interview answers

What makes a quality rule useful?

A good quality rule is specific, measurable, repeatable and tied to the business meaning of a field. For example, Discount must remain between 0 and 1, and Ship Date should not be earlier than Order Date.

How do you prioritize issues?

I prioritize by business impact, number of affected records, data criticality and downstream risk. Missing customer IDs or invalid sales values are usually more urgent than formatting issues.
