"""Device detection utilities for Torch-based components."""

from functools import lru_cache
import logging
import os

logger = logging.getLogger(__name__)


def _safe_getattr(obj, name, default=None):
    """Return attribute if present; swallow AttributeError."""
    try:
        return getattr(obj, name)
    except AttributeError:
        return default


@lru_cache(maxsize=1)
def detect_torch_device() -> str:
    """
    Detect the best available torch device.

    Preference order:
        1. macOS Metal (mps)
        2. CUDA GPU
        3. CPU

    Returns:
        Device string understood by torch / sentence-transformers.
    """
    try:
        import torch  # type: ignore
    except ImportError:
        logger.debug("torch not installed; defaulting to cpu")
        return "cpu"

    # macOS Metal Performance Shaders
    mps_backend = _safe_getattr(torch.backends, "mps")
    if mps_backend:
        try:
            if mps_backend.is_available():
                logger.info("Detected Apple Metal backend (mps)")
                return "mps"
        except Exception as exc:  # pragma: no cover - backend-specific
            logger.debug("MPS detection failed: %s", exc)

    # CUDA
    try:
        if torch.cuda.is_available():
            logger.info("Detected CUDA GPU backend")
            return "cuda"
    except Exception as exc:  # pragma: no cover - backend-specific
        logger.debug("CUDA detection failed: %s", exc)

    return "cpu"


def resolve_device(env_override: str | None = None) -> str:
    """
    Resolve device considering environment overrides.

    Args:
        env_override: Explicit device string; takes precedence.

    Environment variables checked (in order):
        - DENSE_DEVICE
        - TORCH_DEVICE

    Returns:
        Device string for downstream components.
    """
    if env_override:
        return env_override

    for env_var in ("DENSE_DEVICE", "TORCH_DEVICE"):
        value = os.getenv(env_var)
        if value:
            logger.info("Using device override from %s=%s", env_var, value)
            return value

    return detect_torch_device()
