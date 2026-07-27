from typing import Any

from ..errors import UnsupportedModelError


class Base:
    @classmethod
    def models(cls) -> dict[str, dict[str, Any]]:
        if "MODELS" not in cls.__dict__:
            raise NotImplementedError(f"{cls.__name__} must define MODELS")
        return cls.MODELS

    @classmethod
    def model_info(cls, model: object) -> dict[str, Any] | None:
        return cls.models().get(str(model))

    @classmethod
    def validate_model(cls, model: object) -> str:
        normalized = str(model)
        if cls.model_info(normalized) is not None:
            return normalized

        supported = ", ".join(sorted(cls.models()))
        raise UnsupportedModelError(
            f"{cls.__name__} does not support model {normalized!r}. "
            f"Supported models: {supported}"
        )

    def _configure_model(self, model: object) -> None:
        self.model = self.validate_model(model)
        self._model_info = self.model_info(self.model)

    @property
    def model_metadata(self) -> dict[str, Any]:
        return self._model_info

    @property
    def context_window(self) -> int:
        return self.model_metadata["context_window"]

    @property
    def input_token_cost_per_million(self) -> float | None:
        return self.model_metadata["cost_per_million"]["input"]

    @property
    def output_token_cost_per_million(self) -> float | None:
        return self.model_metadata["cost_per_million"]["output"]

    @property
    def usage_unit(self) -> str:
        return self.model_metadata["usage_unit"]

    @property
    def usage_level(self) -> str | None:
        return self.model_metadata.get("usage_level")

    def estimate_cost(self, *, input_tokens: int, output_tokens: int) -> float | None:
        input_cost = self.input_token_cost_per_million
        output_cost = self.output_token_cost_per_million
        if input_cost is None or output_cost is None:
            return None
        return (
            input_tokens * input_cost + output_tokens * output_cost
        ) / 1_000_000
