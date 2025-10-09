from .base import BaseProvider
from .local_rules import LocalRulesProvider

try:
    from .huggingface_provider import HuggingFaceProvider, HuggingFaceChatProvider
    __all__ = [
        "BaseProvider",
        "LocalRulesProvider",
        "HuggingFaceProvider",
        "HuggingFaceChatProvider",
    ]
except ImportError:
    # HuggingFace providers not available (missing torch/transformers)
    __all__ = [
        "BaseProvider",
        "LocalRulesProvider",
    ]


