from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .errors import InputError, InputTooLargeError
from .hashing import sha256_text


@dataclass(frozen=True)
class VerifiedQuote:
    quote: str
    start_line: int
    end_line: int
    char_start: int
    char_end: int


@dataclass(frozen=True)
class Manuscript:
    path: Path
    paper_id: str
    text: str
    sha256: str
    lines: tuple[str, ...]
    line_offsets: tuple[int, ...]

    @classmethod
    def load(cls, path: Path, *, allowed_extensions: list[str], max_characters: int) -> "Manuscript":
        path = path.resolve()
        if path.suffix.lower() not in {ext.lower() for ext in allowed_extensions}:
            raise InputError(f"Only {', '.join(allowed_extensions)} inputs are supported: {path}")
        if not path.is_file():
            raise InputError(f"Manuscript not found: {path}")
        try:
            text = path.read_text(encoding="utf-8", errors="strict")
        except UnicodeError as exc:
            raise InputError(f"Manuscript must be valid UTF-8: {path}") from exc
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        if len(text) > max_characters:
            raise InputTooLargeError(
                f"input_too_large: {len(text)} characters exceeds configured limit {max_characters}"
            )
        lines = tuple(text.split("\n"))
        offsets: list[int] = []
        offset = 0
        for line in lines:
            offsets.append(offset)
            offset += len(line) + 1
        return cls(
            path=path,
            paper_id=path.stem,
            text=text,
            sha256=sha256_text(text),
            lines=lines,
            line_offsets=tuple(offsets),
        )

    def numbered_text(self) -> str:
        width = max(4, len(str(len(self.lines))))
        return "\n".join(f"{index:0{width}d} | {line}" for index, line in enumerate(self.lines, 1))

    def verify_quote(self, quote: str, start_line: int, end_line: int) -> VerifiedQuote:
        if not quote:
            raise ValueError("quote is empty")
        if start_line < 1 or end_line < start_line or end_line > len(self.lines):
            raise ValueError("line range is outside the manuscript")
        segment_start = self.line_offsets[start_line - 1]
        segment_end = (
            self.line_offsets[end_line] - 1 if end_line < len(self.lines) else len(self.text)
        )
        segment = self.text[segment_start:segment_end]
        relative = segment.find(quote)
        if relative < 0:
            raise ValueError("quote does not occur exactly within the stated line range")
        char_start = segment_start + relative
        return VerifiedQuote(
            quote=quote,
            start_line=start_line,
            end_line=end_line,
            char_start=char_start,
            char_end=char_start + len(quote),
        )
