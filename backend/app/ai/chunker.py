"""Split a file into overlapping, line-aligned chunks so answers can cite exact line ranges."""
from dataclasses import dataclass

MAX_CHARS = 1200
OVERLAP_LINES = 3


@dataclass(frozen=True)
class TextChunk:
    text: str
    start_line: int
    end_line: int


def chunk_text(text: str, max_chars: int = MAX_CHARS, overlap_lines: int = OVERLAP_LINES) -> list[TextChunk]:
    segments: list[tuple[int, str]] = []
    for number, line in enumerate(text.splitlines(), start=1):
        for i in range(0, max(len(line), 1), max_chars):
            segments.append((number, line[i : i + max_chars]))

    chunks: list[TextChunk] = []
    start = 0
    while start < len(segments):
        end, size = start, 0
        while end < len(segments) and (end == start or size + len(segments[end][1]) + 1 <= max_chars):
            size += len(segments[end][1]) + 1
            end += 1
        block = segments[start:end]
        body = "\n".join(s for _, s in block)
        if body.strip():
            chunks.append(TextChunk(body, block[0][0], block[-1][0]))
        if end >= len(segments):
            break
        start = max(end - overlap_lines, start + 1)
    return chunks
