"""
Natural Language -> Pandas query translation.

Uses the AI provider to translate a plain-English question into a single
pandas expression operating on a dataframe named `df`, executes it in a
restricted namespace, and returns both the generated code and the result.
"""
from typing import Any, Dict

import pandas as pd

from app.services.ai_provider import ai_complete_json

ALLOWED_BUILTINS = {"len": len, "round": round, "sum": sum, "min": min, "max": max, "sorted": sorted}


def generate_pandas_code(question: str, columns: list[str], dtypes: Dict[str, str]) -> str:
    system = (
        "You translate natural language questions into a SINGLE pandas "
        "expression that operates on a dataframe variable named `df`. "
        "Only use columns that exist. Return ONLY JSON: {\"code\": \"<expr>\"}. "
        "The expression must be a single line that evaluates to a result "
        "(no print, no assignment, no imports, no multi-statement code)."
    )
    prompt = f"""
DataFrame columns and dtypes: {dtypes}

Question: "{question}"

Examples:
Q: "Show top 10 customers by sales"
A: {{"code": "df.sort_values('sales', ascending=False).head(10)"}}

Q: "Find average age"
A: {{"code": "df['age'].mean()"}}

Now produce the JSON for the question above.
"""
    fallback = {"code": "df.head(10)"}
    result = ai_complete_json(prompt, system=system, fallback=fallback)
    return result.get("code", fallback["code"])


def execute_pandas_code(df: pd.DataFrame, code: str) -> Any:
    """Executes the generated single-expression code in a restricted namespace."""
    safe_globals = {"__builtins__": ALLOWED_BUILTINS, "pd": pd}
    safe_locals = {"df": df}
    try:
        result = eval(code, safe_globals, safe_locals)  # noqa: S307 - restricted namespace
    except Exception as exc:
        return {"error": f"Could not execute generated query: {exc}"}

    if isinstance(result, pd.DataFrame):
        return result.head(100).to_dict(orient="records")
    if isinstance(result, pd.Series):
        return result.head(100).to_dict()
    if hasattr(result, "item"):
        return result.item()
    return result


def explain_result(question: str, code: str, result_preview: Any) -> str:
    system = "You are a data analyst. Explain a query result in 1-3 plain-English sentences."
    prompt = f"""
Question: "{question}"
Pandas code executed: {code}
Result (truncated): {str(result_preview)[:1500]}

Explain the result clearly and concisely for a business user.
"""
    from app.services.ai_provider import ai_complete
    try:
        return ai_complete(prompt, system=system, temperature=0.3, max_tokens=300)
    except Exception:
        return "Here is the result of your query (AI explanation unavailable)."
