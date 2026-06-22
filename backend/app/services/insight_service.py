"""
AI Insight Generator — produces narrative business insights from an EDA report.
"""
from typing import List

from app.services.ai_provider import ai_complete_json


def generate_dataset_insights(eda_report: dict, sample_columns: list[str]) -> List[str]:
    fallback = [
        "Review the correlation matrix to identify which features most strongly drive your target metric.",
        "Several columns have missing values — consider imputation or removal before modeling.",
        "Check flagged outliers; they may represent data-entry errors or genuinely important edge cases.",
    ]
    system = (
        "You are a senior data analyst. Given an EDA report (JSON), produce "
        "5-8 concise, specific, business-readable insight statements. "
        "Reference actual column names and numbers from the report. "
        "Return JSON: {\"insights\": [<string>, ...]}"
    )
    prompt = f"""
Columns: {sample_columns}

EDA report (truncated):
{str(eda_report)[:5000]}

Generate the insights JSON now.
"""
    result = ai_complete_json(prompt, system=system, fallback={"insights": fallback})
    return result.get("insights", fallback)
