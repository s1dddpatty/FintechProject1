# Entity Relationship Diagram

This document illustrates the physical relationship between the core business entities in the platform.

## ER Diagram

```mermaid
erDiagram
    MARKETING_CAMPAIGNS ||--o{ LOANS : acquires
    LOANS ||--o{ PAYMENTS : receives
    LOANS ||--o{ PREDICTIONS : scored_by
    MODEL_VERSIONS ||--o{ PREDICTIONS : generates
    
    MARKETING_CAMPAIGNS {
        uuid campaign_id PK
        string channel
        float spend
    }

    LOANS {
        string id PK
        uuid campaign_id FK "Nullable"
        float annual_inc
        string home_ownership
        float loan_amnt
        float int_rate
        string grade
        string loan_status
    }

    PAYMENTS {
        int payment_id PK
        string loan_id FK
        date payment_date
        float amount_received
    }

    MODEL_VERSIONS {
        int model_id PK
        string version
        string algorithm
    }

    PREDICTIONS {
        int prediction_id PK
        string loan_id FK
        int model_id FK
        float predicted_default_prob
        timestamp inference_timestamp
    }
```

## Relationship Explanations

1.  **Marketing Campaigns -> Loans (One-to-Many)**: A single marketing campaign can acquire thousands of loan applications, but a loan application is attributed to a single primary acquisition campaign.
2.  **Loans -> Payments (One-to-Many)**: A single loan receives dozens of installment payments over its term. A payment transaction is tied to exactly one loan.
4.  **Model Versions -> Predictions (One-to-Many)**: A single deployed credit risk model will score millions of applications, generating many predictions. Each prediction links back to the specific version of the model that generated it.
5.  **Loans -> Predictions (One-to-Many)**: A loan may be scored multiple times (e.g., once at origination, and repeatedly over its lifetime as a behavioral risk score). Thus, one loan maps to many predictions.
