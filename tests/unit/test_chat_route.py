"""Unit tests for chat route logic."""

import asyncio
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

import backend.routes.chat as chat_module
from backend.models.schemas import ChatRequest, RetrievalMethodEnum, LanguageEnum
from backend.retrieval.hybrid_fusion import FusedResult


def test_normalise_methods_supports_strings_and_enums():
    methods = chat_module._normalise_methods(
        ["BM25", RetrievalMethodEnum.COLBERT, "Graph", "dense"]
    )
    assert methods == ["bm25", "colbert", "graph", "dense"]


def test_normalise_methods_skips_unknown_types():
    class Oddball:  # pragma: no cover - simple helper
        pass

    methods = chat_module._normalise_methods(["bm25", Oddball()])
    assert methods == ["bm25"]


def test_chat_returns_response_with_retrieval(monkeypatch):
    captured_results_dict = {}
    dummy_chat_calls = []

    fused_results = [
        FusedResult(
            doc_id="doc1",
            chunk_id="doc1_chunk_0",
            rrf_score=0.9,
            rank=1,
            text="Relevant chunk",
            language="en",
            method_scores={"bm25": 5.0},
            method_ranks={"bm25": 1}
        )
    ]

    def fake_rrf(results_dict, k, top_k):
        captured_results_dict["value"] = results_dict
        return fused_results

    class DummyChatService:
        def generate_response(self, query, retrieved_chunks, conversation_history=None, language="en"):
            dummy_chat_calls.append(
                {
                    "query": query,
                    "chunks": retrieved_chunks,
                    "history": conversation_history or [],
                    "language": language
                }
            )
            return "mocked answer"

    def fake_search(query, top_k, language):
        return [SimpleNamespace(doc_id="doc1", text="raw chunk", language=language, chunk_id="doc1_chunk_0")]

    fake_app_state = {
        "chat_service": DummyChatService(),
        "bm25_retriever": SimpleNamespace(search=fake_search),
        "dense_retriever": None,
        "graph_retriever": None,
    }

    monkeypatch.setattr(chat_module, "get_app_state", lambda: fake_app_state)
    monkeypatch.setattr(chat_module, "reciprocal_rank_fusion", fake_rrf)

    request = ChatRequest(
        message="Explain machine learning.",
        conversation_history=[{"role": "user", "content": "Hi"}],
        top_k=2,
        language=LanguageEnum.EN,
        retrieval_methods=[RetrievalMethodEnum.BM25]
    )

    response = asyncio.run(chat_module.chat(request))

    assert response.message == "mocked answer"
    assert response.retrieved_chunks[0].doc_id == "doc1"
    assert "bm25" in captured_results_dict["value"]
    assert dummy_chat_calls[0]["query"] == request.message
    assert dummy_chat_calls[0]["language"] == "en"
    assert dummy_chat_calls[0]["chunks"][0]["doc_id"] == "doc1"


def test_chat_service_unavailable(monkeypatch):
    monkeypatch.setattr(chat_module, "get_app_state", lambda: {})

    request = ChatRequest(
        message="Hello",
        conversation_history=[],
        top_k=1,
        language=LanguageEnum.EN,
        retrieval_methods=[RetrievalMethodEnum.BM25]
    )

    with pytest.raises(HTTPException) as excinfo:
        asyncio.run(chat_module.chat(request))

    assert excinfo.value.status_code == 503


def test_chat_handles_empty_retrieval(monkeypatch):
    captured_results_dict = {}

    def fake_rrf(results_dict, k, top_k):
        captured_results_dict["value"] = results_dict
        return []

    class DummyChatService:
        def generate_response(self, query, retrieved_chunks, conversation_history=None, language="en"):
            assert retrieved_chunks == []
            return "fallback answer"

    fake_app_state = {
        "chat_service": DummyChatService(),
        "bm25_retriever": None,
        "dense_retriever": None,
        "graph_retriever": None,
    }

    monkeypatch.setattr(chat_module, "get_app_state", lambda: fake_app_state)
    monkeypatch.setattr(chat_module, "reciprocal_rank_fusion", fake_rrf)

    request = ChatRequest(
        message="Any data?",
        conversation_history=[],
        top_k=1,
        language=LanguageEnum.EN,
        retrieval_methods=[RetrievalMethodEnum.BM25]
    )

    response = asyncio.run(chat_module.chat(request))

    assert response.message == "fallback answer"
    assert response.retrieved_chunks == []
    assert captured_results_dict["value"] == {}
