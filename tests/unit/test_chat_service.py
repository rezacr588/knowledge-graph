"""Unit tests for ChatService behaviour."""

import sys
import types

import pytest

# Provide a stub generative AI module if the real dependency is absent.
if "google.generativeai" not in sys.modules:
    google_pkg = sys.modules.setdefault("google", types.ModuleType("google"))
    fake_genai = types.ModuleType("google.generativeai")
    fake_genai.configure = lambda *_args, **_kwargs: None
    fake_genai.GenerativeModel = lambda *_args, **_kwargs: None
    google_pkg.generativeai = fake_genai
    sys.modules["google.generativeai"] = fake_genai

import backend.services.chat_service as chat_service_module
from backend.services.chat_service import ChatService


class DummyResponse:
    def __init__(self, text: str):
        self.text = text


class DummyModel:
    def __init__(self, name: str, responses):
        self.name = name
        self._responses = responses

    def generate_content(self, prompt: str, stream: bool = False):
        self._responses.append(prompt)
        return DummyResponse("Generated answer.")


class ErrorModel:
    def __init__(self, *_):
        pass

    def generate_content(self, *_args, **_kwargs):
        raise RuntimeError("generation failed")


@pytest.fixture
def patched_chat_service(monkeypatch):
    """Create ChatService with dummy Gemini backend."""
    prompts = []

    def fake_configure(api_key: str):
        assert api_key == "fake-key"

    monkeypatch.setattr(chat_service_module.genai, "configure", fake_configure)
    monkeypatch.setattr(
        chat_service_module.genai,
        "GenerativeModel",
        lambda name: DummyModel(name, prompts),
    )

    service = ChatService(gemini_api_key="fake-key", model_name="fake-model")
    return service, prompts


def test_generate_response_includes_context_and_history(patched_chat_service):
    service, prompts = patched_chat_service

    retrieved_chunks = [
        {"text": f"Chunk {i}", "rrf_score": 1.0 / (i + 1)}
        for i in range(7)
    ]
    conversation_history = [
        {"role": "user", "content": "Hello"},
        {"role": "assistant", "content": "Hi!"},
        {"role": "user", "content": "Tell me about ML."},
    ]

    result = service.generate_response(
        query="What is machine learning?",
        retrieved_chunks=retrieved_chunks,
        conversation_history=conversation_history,
        language="en"
    )

    assert result == "Generated answer."
    assert len(prompts) == 1
    prompt = prompts[0]

    assert prompt.count("[Context") == 5  # limited to top 5
    assert "Chunk 0" in prompt and "Chunk 5" not in prompt
    assert "USER: Hello" in prompt
    assert "ASSISTANT: Hi!" in prompt
    assert "Current Question: What is machine learning?" in prompt


def test_generate_response_handles_generation_errors(monkeypatch):
    """Service should fall back to user-friendly message on errors."""
    monkeypatch.setattr(chat_service_module.genai, "configure", lambda *_, **__: None)
    monkeypatch.setattr(chat_service_module.genai, "GenerativeModel", ErrorModel)

    service = ChatService(gemini_api_key="fake-key", model_name="fake-model")

    result = service.generate_response(
        query="Why?",
        retrieved_chunks=[],
        conversation_history=None,
        language="en"
    )

    assert "I apologize" in result
