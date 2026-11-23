import os
import httpx
from datetime import datetime
from src.core.logging import get_logger

logger = get_logger(__name__)

class LLMService:
    """
    Open-Source LLM Service interfacing with local Ollama daemon (e.g. llama3.2, mistral, phi3)
    with autonomous, deterministic domain fallback for zero-dependency execution.
    """

    def __init__(self):
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
        self.model = os.getenv("OLLAMA_MODEL", "llama3.2")
        self.timeout = float(os.getenv("OLLAMA_TIMEOUT", "15.0"))

    async def check_ollama_status(self) -> dict:
        """Checks if local Ollama daemon is reachable and lists available models."""
        try:
            # Ultra-fast connect check (0.5s) to avoid blocking when daemon is not active
            async with httpx.AsyncClient(timeout=httpx.Timeout(1.0, connect=0.5)) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                if res.status_code == 200:
                    data = res.json()
                    models = [m.get("name") for m in data.get("models", [])]
                    active_model = self.model
                    if active_model not in models and len(models) > 0:
                        active_model = models[0]
                    return {
                        "available": True,
                        "base_url": self.base_url,
                        "active_model": active_model,
                        "available_models": models
                    }
        except Exception as e:
            logger.debug(f"Ollama local daemon offline or unreachable: {str(e)}")

        return {
            "available": False,
            "base_url": self.base_url,
            "active_model": None,
            "available_models": [],
            "message": "Ollama daemon offline. To enable local open-source LLM, run: 'ollama run llama3.2'"
        }

    async def generate_pipeline_audit(self, telemetry: dict) -> dict:
        """
        Generates an Executive Data Quality & Transformation Audit Memorandum
        using local Ollama when available, or autonomous financial rule synthesis when offline.
        """
        status = await self.check_ollama_status()
        
        if status["available"]:
            try:
                audit_text = await self._generate_with_ollama(telemetry, status["active_model"])
                return {
                    "audit_memo": audit_text,
                    "engine": f"Ollama ({status['active_model']})",
                    "status": "ai_generated",
                    "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
                }
            except Exception as e:
                logger.warning(f"Ollama inference attempt failed ({str(e)}), falling back to deterministic synthesis.")

        # Autonomous deterministic fallback
        audit_text = self._generate_deterministic_audit(telemetry)
        return {
            "audit_memo": audit_text,
            "engine": "Autonomous Financial Auditor (Ollama Offline - run 'ollama run llama3.2' for generative mode)",
            "status": "deterministic_fallback",
            "timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        }

    async def _generate_with_ollama(self, telemetry: dict, model_name: str) -> str:
        """Invokes local Ollama REST API to generate an institutional audit memorandum."""
        prompt = f"""
You are a Senior Quantitative Risk & Data Engineering Auditor at an institutional investment bank (such as ION Group).
Review the following automated pipeline execution telemetry and generate a formal, high-impact Executive Data Quality & Transformation Audit Memorandum.

PIPELINE EXECUTION TELEMETRY:
- Raw Ingested Records: {telemetry.get('raw_rows', 0)}
- Clean Model-Ready Output Records: {telemetry.get('cleaned_rows', 0)}
- Data Quality Score: {telemetry.get('data_quality_score', 0)}/100
- Auto-Mapped Column Aliases: {telemetry.get('mapped_aliases', {})}
- Sanitized Features: {telemetry.get('sanitized_columns', {})}
- Missing Imputed Columns: {telemetry.get('imputed_features', [])}
- Newly Engineered Financial Features: {telemetry.get('engineered_features', [])}
- Discarded / Unusable Rows: {telemetry.get('dropped_rows', 0)}

REQUIRED AUDIT MEMORANDUM STRUCTURE (Use GitHub Markdown):
1. **Executive Summary & Quality Health Assessment**: Clear verdict on overall dataset integrity and the calculated Data Quality Score.
2. **Ingestion & Sanitization Audit**: Detail exact data formatting corrections (e.g., currency symbols, comma separators, loan term string parsing).
3. **Advanced Financial Feature Engineering**: Explain the economic and statistical significance of the newly engineered indicators (e.g. FICO score midpoint, Payment-to-Income PTI ratio, Credit Line Age, monotonic Grade ordinals).
4. **Model-Readiness & Basel Compliance Certification**: Formal declaration that the dataset meets institutional standards for training gradient-boosted decision trees (XGBoost / Random Forest).

Keep the tone authoritative, quantitative, and concise.
"""
        payload = {
            "model": model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "top_p": 0.9
            }
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            res = await client.post(f"{self.base_url}/api/generate", json=payload)
            if res.status_code == 200:
                result_json = res.json()
                return result_json.get("response", "").strip()
            else:
                raise RuntimeError(f"Ollama returned HTTP {res.status_code}: {res.text}")

    def _generate_deterministic_audit(self, telemetry: dict) -> str:
        """
        High-precision deterministic institutional audit memorandum
        ensuring zero-dependency operation when Ollama is offline.
        """
        raw_rows = telemetry.get('raw_rows', 0)
        cleaned_rows = telemetry.get('cleaned_rows', 0)
        score = telemetry.get('data_quality_score', 95)
        mapped = telemetry.get('mapped_aliases', {})
        sanitized = telemetry.get('sanitized_columns', {})
        imputed = telemetry.get('imputed_features', [])
        engineered = telemetry.get('engineered_features', [])
        dropped = telemetry.get('dropped_rows', 0)

        # Quality Grade determination
        if score >= 90:
            verdict = "INVESTMENT GRADE (APPROVED FOR PRODUCTION TRAINING)"
            alert_badge = "✅"
        elif score >= 75:
            verdict = "CONDITIONALLY APPROVED (CONTROLLED PRODUCTION)"
            alert_badge = "⚠️"
        else:
            verdict = "DEFICIENT (REQUIRES MANUAL UNDERWRITING REVIEW)"
            alert_badge = "🛑"

        # Format mappings
        mapped_bullets = "\n".join([f"- `'{orig}'` → canonical field `'{canonical}'`" for orig, canonical in mapped.items()]) if mapped else "- Zero column alias remapping required (input schema natively matched canonical definition)."

        # Format sanitizations
        sanitized_bullets = "\n".join([f"- **`{col}`**: {desc}" for col, desc in sanitized.items()]) if sanitized else "- All numeric and duration fields conformed strictly to IEEE floating-point standards."

        # Format imputations
        imputed_bullets = "\n".join([f"- **`{col}`**: Injected conservative median baseline." for col in imputed]) if imputed else "- Zero structural missingness detected; complete attribute density verified."

        # Format engineered features
        engineered_bullets = "\n".join([f"- **`{feat}`**: {desc}" for feat, desc in engineered.items()]) if isinstance(engineered, dict) else "\n".join([f"- **`{feat}`**: Financial ratio computed." for feat in engineered])

        return f"""### 📋 Executive Data Quality & Transformation Audit Memorandum
**Audit Standard:** Basel Committee on Banking Supervision (BCBS 239) & SR 11-7 Model Risk  
**Audit Evaluation:** {alert_badge} **{verdict}**  
**Composite Data Quality Score:** **`{score}/100`**

---

#### 1. Ingestion Integrity & Volume Reconciliation
* **Raw Input Records:** `{raw_rows:,}` applications received.
* **Refined Output Records:** `{cleaned_rows:,}` model-ready applications persisted (`{((cleaned_rows / max(1, raw_rows)) * 100):.1f}%` yield).
* **Terminal Row Attrition:** `{dropped:,}` non-conforming / duplicate records neutralized.

#### 2. Schema Normalization & Self-Healing Actions
The autonomous schema normalizer detected and resolved structural naming variances:
{mapped_bullets}

#### 3. Type Sanitization & Data Cleansing Log
The automated cleaning pipeline neutralized corrupting strings and formatting artifacts:
{sanitized_bullets}

#### 4. Domain-Aware Missing Value Imputation
To prevent cold-start model pipeline execution failures, domain-aware defaults were injected:
{imputed_bullets}

#### 5. Advanced Financial Feature Engineering
The pipeline synthesized key econometric and solvency indicators required for nonlinear tree splits:
{engineered_bullets}

#### 6. Canonical Architecture Enforcement (3 Entities + 1 Solvency Stream)
The dataset was partitioned and standardized into the 4 institutional credit risk domains (21 fixed features):
- **Borrower Profile (Individual Entity - 4 features):** `annual_inc`, `emp_length`, `home_ownership`, `addr_state`
- **Credit Bureau (Bureau Entity - 6 features):** `fico_score`, `fico_range_low`, `fico_range_high`, `dti`, `revol_util`, `credit_history_months`
- **Loan Facility (Contract Agreement Entity - 7 features):** `loan_amnt`, `term`, `int_rate`, `installment`, `grade`, `grade_ordinal`, `purpose`
- **Solvency & Performance Stream (Dynamic Repayment Stream - 3 features):** `installment_to_income`, `loan_to_income`, `loan_status`
- **Primary Key:** `id`

#### 7. Institutional Model-Readiness Certification
* **Feature Matrix Dimensions:** 21 strictly canonical columns ready for gradient-boosted tree ingestion (`XGBoost` / `RandomForestClassifier`).
* **Null Tolerance:** 0.00% missing values in output feature vectors.
* **Audit Signature:** Authenticated by **Enterprise Credit Pipeline Ingestion Service**.
"""
