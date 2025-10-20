# 🧪 Testing Guide

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── unit/                    # Unit tests
│   ├── test_bm25_retriever.py
│   ├── test_entity_extraction.py
│   └── test_hybrid_fusion.py
├── integration/             # Integration tests
│   └── test_retrieval_pipeline.py
└── e2e/                     # End-to-end tests
    └── test_api_endpoints.py
```

## Running Tests

### Install Dev Dependencies
```bash
pip install -r requirements-dev.txt
```

### Run All Tests
```bash
pytest
```

### Run Specific Test Types
```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# E2E tests only
pytest -m e2e
```

### Run with Coverage
```bash
pytest --cov=backend --cov-report=html
open htmlcov/index.html
```

### Run Specific Test File
```bash
pytest tests/unit/test_bm25_retriever.py
```

### Run Specific Test
```bash
pytest tests/unit/test_bm25_retriever.py::TestBM25Retriever::test_initialization
```

## Test Markers

- `@pytest.mark.unit` - Fast, isolated tests
- `@pytest.mark.integration` - Tests component interaction
- `@pytest.mark.e2e` - Tests full API endpoints
- `@pytest.mark.slow` - Long-running tests
- `@pytest.mark.requires_external` - Needs external services

## Writing Tests

### Unit Test Template
```python
import pytest

@pytest.mark.unit
class TestMyComponent:
    def test_something(self):
        # Arrange
        component = MyComponent()
        
        # Act
        result = component.do_something()
        
        # Assert
        assert result == expected
```

### Using Fixtures
```python
def test_with_fixture(test_documents):
    # test_documents from conftest.py
    assert len(test_documents) > 0
```

## Test Coverage Goals

- **Unit Tests:** >80% coverage
- **Integration Tests:** Key workflows
- **E2E Tests:** All API endpoints

## Continuous Integration

Add to `.github/workflows/tests.yml`:
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt -r requirements-dev.txt
      - run: pytest -m unit
```
