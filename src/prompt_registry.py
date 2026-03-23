from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from string import Formatter


class PromptRenderError(ValueError):
    """Raised when a prompt cannot be rendered safely."""


@dataclass(frozen=True, slots=True)
class PromptDefinition:
    name: str
    path: Path
    content: str


class PromptRegistry:
    def __init__(self, prompts_dir: Path) -> None:
        self.prompts_dir = prompts_dir
        self._definitions = self._load_definitions()

    def _load_definitions(self) -> dict[str, PromptDefinition]:
        if not self.prompts_dir.exists():
            raise FileNotFoundError(
                f"Prompt directory does not exist: {self.prompts_dir}"
            )

        definitions: dict[str, PromptDefinition] = {}
        for path in sorted(self.prompts_dir.glob("*.md")):
            definitions[path.stem] = PromptDefinition(
                name=path.stem,
                path=path,
                content=path.read_text(encoding="utf-8").strip(),
            )
        return definitions

    def list_prompts(self) -> list[PromptDefinition]:
        return list(self._definitions.values())

    def get_prompt(self, name: str) -> PromptDefinition:
        try:
            return self._definitions[name]
        except KeyError as exc:
            raise KeyError(f"Unknown prompt: {name}") from exc

    def render(self, name: str, variables: dict[str, object]) -> str:
        prompt = self.get_prompt(name)
        required_variables = {
            field_name
            for _, field_name, _, _ in Formatter().parse(prompt.content)
            if field_name
        }
        missing_variables = sorted(required_variables - variables.keys())
        if missing_variables:
            missing = ", ".join(missing_variables)
            raise PromptRenderError(f"Missing prompt variables: {missing}")

        try:
            return prompt.content.format(**variables)
        except KeyError as exc:
            raise PromptRenderError(str(exc)) from exc
