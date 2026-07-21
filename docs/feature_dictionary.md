# Comprehensive Data Dictionary

This dictionary defines the LendingClub dataset features expected by the analytics platform.

| Field Name | Business Meaning | Datatype | Nullable | Example | Validation Rules | Why it Matters |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `id` | Unique identifier for the loan application | String | No | "1077501" | Must be unique, regex `^[0-9]+$` | Primary key for joining loan to payments/predictions. |
| `member_id` | Unique identifier for the customer | String | No | "1296599" | Must be unique per customer | Groups multiple loans under one borrower for CLV. |
| `loan_amnt` | The requested loan amount | Float | No | 5000.0 | Min: 500, Max: 40000 | Baseline for credit exposure and risk scaling. |
| `funded_amnt` | The amount committed to the loan | Float | No | 5000.0 | `<=` `loan_amnt` | Determines actual principal disbursed. |
| `term` | The number of payments on the loan (Months) | String/Int | No | "36 months" | Must be 36 or 60 | Dictates the repayment schedule and duration of risk. |
| `int_rate` | Interest Rate on the loan | Float | No | 10.65 | Min: 5.0, Max: 35.0 | Determines revenue and monthly installment size. |
| `installment` | The monthly payment owed by the borrower | Float | No | 162.87 | Min: 10.0, Max: 1500.0 | Used to calculate Debt-to-Income (DTI) and affordability. |
| `grade` | LendingClub assigned loan grade | String | No | "B" | In ["A", "B", "C", "D", "E", "F", "G"] | Primary categorical indicator of risk. |
| `sub_grade` | LendingClub assigned loan subgrade | String | No | "B2" | e.g., A1 to G5 | Finer granularity for pricing and risk models. |
| `emp_title` | Job title supplied by the Borrower | String | Yes | "Software Engineer" | None (Free text) | Indicates stability and sector-specific risk. |
| `emp_length` | Employment length in years | String/Int | Yes | "10+ years" | Must map to integer 0-10 | Proxy for income stability. |
| `home_ownership` | Home ownership status provided by borrower | String | No | "RENT" | In ["RENT", "OWN", "MORTGAGE", "ANY", "NONE"] | Identifies asset-backed stability and fixed expenses. |
| `annual_inc` | Self-reported annual income | Float | No | 24000.0 | `>= 0` | Crucial denominator for DTI. |
| `verification_status` | Indicates if income was verified | String | No | "Verified" | ["Verified", "Source Verified", "Not Verified"] | Determines the trustworthiness of the income field. |
| `issue_d` | The month which the loan was funded | Date/String | No | "Dec-2011" | Valid Date format | Used for cohort analysis and vintage curves. |
| `loan_status` | Current status of the loan | String | No | "Fully Paid" | ["Fully Paid", "Charged Off", "Current", ...] | The primary target variable for machine learning. |
| `pymnt_plan` | Indicates if a payment plan has been put in place | Boolean | No | "n" | ["y", "n"] | Identifies restructured loans. |
| `purpose` | A category provided by the borrower | String | No | "credit_card" | e.g., "debt_consolidation", "car" | Behavioral indicator of why funds are needed. |
| `title` | The loan title provided by the borrower | String | Yes | "Computer" | None (Free text) | Unstructured text useful for NLP features. |
| `zip_code` | The first 3 numbers of the zip code | String | No | "860xx" | Regex `^[0-9]{3}xx$` | Geospatial risk indicator. |
| `addr_state` | The state provided by the borrower | String | No | "AZ" | 2-letter US State code | Used for macroeconomic geospatial features. |
| `dti` | Debt-to-Income ratio | Float | No | 27.65 | Min: 0.0, Max: 100.0 | Core regulatory and credit risk metric. |
| `delinq_2yrs` | 30+ days past-due incidences in past 2 years | Int | No | 0 | `>= 0` | Strong predictor of future default. |
| `earliest_cr_line` | The month the earliest credit line was opened | Date/String | No | "Jan-1985" | Valid Date format | Indicates the length of credit history. |
| `fico_range_low` | Lower boundary range of FICO pull | Int | No | 735 | Min: 300, Max: 850 | External bureau score (lower bound). |
| `fico_range_high` | Upper boundary range of FICO pull | Int | No | 739 | Min: 300, Max: 850, `>= fico_range_low` | External bureau score (upper bound). |
| `inq_last_6mths` | Number of inquiries in past 6 months | Int | No | 1 | `>= 0` | Indicates credit-seeking behavior. |
| `open_acc` | Number of open credit lines | Int | No | 3 | `>= 0` | Indicates available credit capacity. |
| `pub_rec` | Number of derogatory public records | Int | No | 0 | `>= 0` | Indicates bankruptcies or severe defaults. |
| `revol_bal` | Total credit revolving balance | Float | No | 13648.0 | `>= 0` | Measures absolute current debt. |
| `revol_util` | Revolving line utilization rate | Float | Yes | 83.7 | Min: 0.0 | High utilization implies financial stress. |
| `total_acc` | Total number of credit lines currently in file | Int | No | 9 | `>= open_acc` | Overall credit experience. |
| `initial_list_status` | Initial listing status of the loan | String | No | "f" | ["w", "f"] | Fractional vs Whole funding indicator. |
| `out_prncp` | Remaining outstanding principal | Float | No | 0.0 | `>= 0`, `<= funded_amnt` | Determines current portfolio exposure. |
| `total_pymnt` | Total payments received to date | Float | No | 5863.15 | `>= 0` | Used to calculate current ROI. |
| `total_rec_prncp` | Principal received to date | Float | No | 5000.0 | `>= 0`, `<= funded_amnt` | Used to track principal paydown. |
| `total_rec_int` | Interest received to date | Float | No | 863.15 | `>= 0` | Primary driver of revenue. |
| `total_rec_late_fee` | Late fees received to date | Float | No | 0.0 | `>= 0` | Associated with delinquent accounts. |
| `recoveries` | Post charge-off gross recovery | Float | No | 0.0 | `>= 0` | Reduces total loss severity (LGD). |
| `collection_recovery_fee` | Post charge-off collection fee | Float | No | 0.0 | `>= 0` | Cost of recovery. |
| `last_pymnt_d` | Last month a payment was received | Date/String | Yes | "Jan-2015" | Valid Date format | Indicates recency of payments. |
| `last_pymnt_amnt` | Last total payment amount received | Float | No | 171.62 | `>= 0` | Helps identify full payoffs vs installments. |
| `last_credit_pull_d` | The most recent month LC pulled credit | Date/String | Yes | "Sep-2016" | Valid Date format | Recency of bureau data. |
| `last_fico_range_high` | Current FICO score upper bound | Int | Yes | 744 | Min: 300, Max: 850 | Determines risk migration post-origination. |
| `last_fico_range_low` | Current FICO score lower bound | Int | Yes | 740 | Min: 300, Max: 850 | Determines risk migration post-origination. |
| `application_type` | Indicates joint or individual application | String | No | "Individual" | ["Individual", "Joint App"] | Dictates if joint variables are populated. |
| `annual_inc_joint` | Combined annual income for joint app | Float | Yes | 100000.0 | `>= 0` | Replaces `annual_inc` for joint models. |
| `dti_joint` | Combined DTI for joint app | Float | Yes | 20.5 | Min: 0.0, Max: 100.0 | Replaces `dti` for joint models. |
| `acc_now_delinq` | The number of accounts currently delinquent | Int | No | 0 | `>= 0` | Severe immediate risk indicator. |
| `tot_cur_bal` | Total current balance of all accounts | Float | Yes | 150000.0 | `>= 0` | Measure of overall indebtedness. |
