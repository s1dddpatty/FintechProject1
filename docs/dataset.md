# Data Quality Specification & Assumptions

## 1. Data Quality Specification
Before any data is allowed into the analytics layer (the `processed` state), it must pass strict Data Quality (DQ) checks. The ETL pipeline will enforce this contract.

### Required Columns
* Primary Keys: `id` and `member_id` must never be null.
* Target Variables: `loan_status` must never be null.
* Core Financials: `loan_amnt`, `funded_amnt`, `term`, `int_rate`, `installment`, `grade`, `issue_d` are strictly required.

### Missing Value Policy
* **Categorical Features**: Nulls in fields like `emp_title` or `emp_length` will be mapped to a constant `"Missing"` or `"Unknown"`.
* **Numeric Features**: Nulls in financial histories (e.g., `revol_util`, `tot_cur_bal`) will be imputed (e.g., using median or zero, depending on the feature's business logic), and accompanied by a binary missingness indicator column (e.g., `revol_util_is_missing = 1`).
* **Joint Applications**: Joint features (`annual_inc_joint`) are expected to be null if `application_type == 'Individual'`.

### Duplicate Policy
* `id` must be strictly unique across the entire dataset. Duplicates will trigger a pipeline exception.
* `member_id` can appear multiple times (repeat borrowers), but `(member_id, issue_d)` should be carefully monitored for parallel applications.

### Numeric Validation
* **Allowed Ranges**:
  * Percentages (`int_rate`, `dti`, `revol_util`) cannot be negative.
  * FICO scores (`fico_range_low`, `fico_range_high`) must be within [300, 850].
  * Principal (`out_prncp`, `total_rec_prncp`) cannot exceed `funded_amnt`.
* **Zero Rules**: `annual_inc` can be 0, but if `loan_amnt > 0`, DTI calculations must handle division-by-zero gracefully (e.g., cap DTI at 999).

### Categorical Validation
* Values must adhere strictly to predefined sets. For example, `grade` must be in `[A, B, C, D, E, F, G]`. Unknown categories will trigger a quarantine response in the pipeline.

### Date Validation
* Formats must be standardized to `YYYY-MM-DD` or robustly parsed from `Mon-YYYY`.
* **Temporal Logic**: `issue_d` must be >= `earliest_cr_line`. `last_pymnt_d` must be >= `issue_d`.

### Business & Cross-Column Validation
* `funded_amnt` must be $\le$ `loan_amnt`.
* `fico_range_high` must be $\ge$ `fico_range_low`.
* `open_acc` must be $\le$ `total_acc`.
* Total recovered principal (`total_rec_prncp`) + outstanding principal (`out_prncp`) + charge-offs should approximate `funded_amnt`.

---

## 2. Dataset Assumptions

### Dataset Facts
* The data originates from LendingClub, a peer-to-peer lending platform.
* Data is point-in-time for origination features, but cumulative for performance features (e.g., `total_pymnt` reflects the lifetime of the loan).
* Target leakage is a massive risk. Features like `recoveries`, `out_prncp`, and `last_fico_range_high` are *post-origination* variables. They cannot be used to train an origination credit risk model.

### Future Synthetic Data Strategy
Because LendingClub only provides credit bureau and loan performance data, we will synthetically generate Marketing and Web Tracking datasets to build out the full Customer Lifecycle Analytics platform.
* **Leads & Campaigns**: We will synthesize `marketing_campaigns.csv` containing Campaign IDs, channels, and CPCs, and map them to `member_id`.
* **Web Behavior**: We will synthesize page views and application drop-off events to demonstrate funnel analytics.
