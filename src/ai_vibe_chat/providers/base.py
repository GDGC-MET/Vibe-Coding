class BaseProvider:
    name = "base"

    def generate(self, prompt: str) -> str:  # pragma: no cover - intentionally incomplete
        raise NotImplementedError("Providers must implement generate()")


