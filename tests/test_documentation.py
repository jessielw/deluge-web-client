from __future__ import annotations

import re
from collections.abc import Callable
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[1]


def _markdown_python_blocks(text: str) -> list[str]:
    """Extract fenced Python examples from Markdown."""
    return re.findall(r"```python\s*\n(.*?)```", text, flags=re.DOTALL)


def _rst_python_blocks(text: str) -> list[str]:
    """Extract indented Python examples from reStructuredText."""
    blocks: list[str] = []
    lines = text.splitlines()
    index = 0
    while index < len(lines):
        if lines[index].strip() != ".. code-block:: python":
            index += 1
            continue

        index += 1
        while index < len(lines) and not lines[index].strip():
            index += 1

        block: list[str] = []
        while index < len(lines):
            line = lines[index]
            if line.startswith("    "):
                block.append(line[4:])
            elif not line.strip():
                block.append("")
            else:
                break
            index += 1
        blocks.append("\n".join(block).rstrip())

    return blocks


@pytest.mark.parametrize(
    ("relative_path", "extractor"),
    [
        ("README.md", _markdown_python_blocks),
        ("docs/introduction.rst", _rst_python_blocks),
    ],
)
def test_documentation_python_examples_compile(
    relative_path: str,
    extractor: Callable[[str], list[str]],
) -> None:
    """Ensure user-facing Python examples remain syntactically valid."""
    path = ROOT / relative_path
    examples = extractor(path.read_text(encoding="utf-8"))
    assert examples
    for example in examples:
        compile(example, str(path), "exec")
