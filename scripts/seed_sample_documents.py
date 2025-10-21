"""
Seed the backend with sample English and Arabic documents.

Usage:
    python scripts/seed_sample_documents.py --host http://localhost:8000
"""

from __future__ import annotations

import argparse
import pathlib
import sys
from typing import Iterable, Tuple

import requests


ENGLISH_DOCS = [
    (
        "introduction_machine_learning.txt",
        "Machine learning enables systems to learn patterns from data without being explicitly programmed."
    ),
    (
        "neural_networks_overview.txt",
        "Neural networks consist of layers of interconnected nodes that transform inputs into outputs by learning weights."
    ),
    (
        "semantic_embeddings.txt",
        "Text embeddings project words and sentences into vector spaces so that semantic similarity becomes measurable."
    ),
]

ARABIC_DOCS = [
    (
        "arabic_data_analytics.txt",
        "تحليل البيانات يساعد المؤسسات على فهم الاتجاهات واتخاذ قرارات مبنية على الأدلة."
    ),
    (
        "arabic_neural_networks.txt",
        "الشبكات العصبية الاصطناعية تتكون من طبقات من العصبونات لمعالجة البيانات والتعلم من الأمثلة."
    ),
    (
        "arabic_semantic_embeddings.txt",
        "التمثيلات الدلالية تُمكن من تحويل الكلمات إلى متجهات لفهم المعاني والعلاقات بينها."
    ),
]


def ingest_documents(
    host: str,
    documents: Iterable[Tuple[str, str]],
    language: str
) -> None:
    for filename, content in documents:
        response = requests.post(
            f"{host}/api/ingest",
            data={"language": language},
            files={"file": (filename, content.encode("utf-8"), "text/plain")},
            timeout=60,
        )
        response.raise_for_status()
        doc_id = response.json().get("document_id")
        print(f"Ingested {filename} (language={language}, id={doc_id})")


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed sample multilingual documents")
    parser.add_argument(
        "--host",
        default="http://localhost:8000",
        help="Backend host URL (default: http://localhost:8000)",
    )
    args = parser.parse_args()

    print("Seeding English documents...")
    ingest_documents(args.host, ENGLISH_DOCS, language="en")

    print("Seeding Arabic documents...")
    ingest_documents(args.host, ARABIC_DOCS, language="ar")

    print("All documents ingested successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
