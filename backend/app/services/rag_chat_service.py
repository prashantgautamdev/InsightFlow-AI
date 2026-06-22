"""
AI Dataset Chat Assistant (RAG).

Embeds a dataset's EDA summary + sample rows into ChromaDB, then answers
follow-up questions ("which feature has highest correlation?", "suggest
the best model") using retrieval-augmented generation.

Kept dependency-light: if LangChain/Chroma/embeddings aren't available
(e.g. no API key), falls back to directly answering from the EDA JSON
via the AI provider, so the feature degrades gracefully rather than 500s.
"""
import json
import os
from typing import List

import pandas as pd

from app.core.config import settings
from app.services.ai_provider import ai_complete

CHROMA_DIR = settings.CHROMA_PERSIST_DIR
os.makedirs(CHROMA_DIR, exist_ok=True)


def _build_documents(df: pd.DataFrame, eda_report: dict) -> List[str]:
    docs = []
    docs.append("DATASET SUMMARY:\n" + json.dumps(eda_report.get("summary", {}), indent=2))
    docs.append("MISSING VALUES:\n" + json.dumps(eda_report.get("missing_values", {}), indent=2))
    docs.append("STATISTICS:\n" + json.dumps(eda_report.get("statistics", {}), indent=2))
    docs.append("CORRELATION MATRIX:\n" + json.dumps(eda_report.get("correlation", {}), indent=2))
    docs.append("OUTLIERS:\n" + json.dumps(eda_report.get("outliers", {}), indent=2))
    sample = df.head(20).to_csv(index=False)
    docs.append("SAMPLE ROWS (first 20):\n" + sample)
    return docs


def index_dataset(collection_name: str, df: pd.DataFrame, eda_report: dict) -> bool:
    """Embeds EDA + sample data into a Chroma collection. Returns True on success."""
    try:
        import chromadb
        from chromadb.utils import embedding_functions

        client = chromadb.PersistentClient(path=CHROMA_DIR)
        ef = embedding_functions.DefaultEmbeddingFunction()
        try:
            client.delete_collection(collection_name)
        except Exception:
            pass
        collection = client.create_collection(collection_name, embedding_function=ef)

        docs = _build_documents(df, eda_report)
        collection.add(
            documents=docs,
            ids=[f"doc_{i}" for i in range(len(docs))],
        )
        return True
    except Exception:
        return False


def query_dataset_rag(collection_name: str, question: str, eda_report: dict, fallback_only: bool = False) -> str:
    """Retrieves relevant context from Chroma and asks the AI provider to answer.
    Falls back to answering from the raw EDA JSON if Chroma isn't available."""
    context = ""
    if not fallback_only:
        try:
            import chromadb
            from chromadb.utils import embedding_functions

            client = chromadb.PersistentClient(path=CHROMA_DIR)
            ef = embedding_functions.DefaultEmbeddingFunction()
            collection = client.get_collection(collection_name, embedding_function=ef)
            results = collection.query(query_texts=[question], n_results=4)
            context = "\n\n---\n\n".join(results.get("documents", [[]])[0])
        except Exception:
            context = ""

    if not context:
        context = json.dumps(eda_report, indent=2)[:6000]

    system = (
        "You are an expert data scientist assistant embedded in a dataset "
        "analytics platform. Answer questions about the dataset using ONLY "
        "the provided context. Be specific, cite column names and numbers, "
        "and suggest concrete next steps (e.g. which model to try, which "
        "features to drop) when relevant."
    )
    prompt = f"Context:\n{context}\n\nQuestion: {question}\n\nAnswer:"

    try:
        return ai_complete(prompt, system=system, temperature=0.3, max_tokens=600)
    except Exception:
        return (
            "I couldn't reach the AI provider right now, but based on the dataset "
            "summary, here's a quick heuristic answer: check the 'correlation' "
            "and 'statistics' sections of your EDA report for the relevant figures."
        )
